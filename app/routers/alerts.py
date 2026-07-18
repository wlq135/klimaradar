"""Alert subscription API."""

import logging
import secrets
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cloudflare import get_client_ip
from app.config import settings
from app.database import get_db
from app.models import AlertSubscription
from app.rate_limit import subscribe_limiter
from app.schemas import AlertSubscriptionCreate
from app.services.alerter import get_email_backend
from app.services.creem import can_create_alert, create_checkout
from app.templating import templates

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts")


def _client_ip(request: Request) -> str:
    return get_client_ip(request)


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


async def _send_confirmation_email(to_email: str, token: str) -> bool:
    """Send a double opt-in confirmation email."""
    backend = get_email_backend()
    confirm_url = f"{settings.base_url}/api/alerts/confirm?token={token}"
    subject = "Confirm your KlimaRadar AC alert"
    body = f"""
    <html>
      <body>
        <h2>Almost done — confirm your alert</h2>
        <p>Click the button below to start receiving AC stock alerts:</p>
        <p>
          <a href="{confirm_url}"
             style="padding:10px 15px;background:#16a34a;color:#fff;text-decoration:none;border-radius:5px;">
            Confirm my alert
          </a>
        </p>
        <p style="font-size:12px;color:#666;">If you didn't request this, ignore it.</p>
      </body>
    </html>
    """.strip()
    try:
        return await backend.send(to_email, subject, body)
    except Exception:
        logger.exception("Failed to send confirmation email to %s", to_email)
        return False


@router.post("/subscribe")
async def subscribe(
    payload: AlertSubscriptionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    await subscribe_limiter.check(_client_ip(request))
    # Prevent duplicate active subscriptions for the same email + filters.
    stmt = select(AlertSubscription).where(
        AlertSubscription.email == payload.email,
        AlertSubscription.country == payload.country,
        AlertSubscription.city == payload.city,
        AlertSubscription.product_type == payload.product_type,
        AlertSubscription.min_btu == payload.min_btu,
        AlertSubscription.max_price == payload.max_price,
        AlertSubscription.in_stock_only == payload.in_stock_only,
        AlertSubscription.active.is_(True),
    )
    existing = await session.scalar(stmt)
    if existing:
        if not existing.verified:
            # Resend the confirmation email so the user can activate the alert.
            existing.verification_token = _generate_token()
            await session.commit()
            success = await _send_confirmation_email(
                existing.email, existing.verification_token
            )
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Unable to send confirmation email. Please try again later.",
                )
            return {
                "message": "Confirmation email resent. Please check your inbox and click the link to activate."
            }
        return {
            "message": "You already have an active alert for this country."
        }

    # Enforce the free-tier alert limit.
    access = await can_create_alert(session, payload.email)
    if not access["allowed"]:
        try:
            checkout = await create_checkout(payload.email)
        except Exception as exc:
            logger.exception("Failed to create Lemon Squeezy checkout for upgrade")
            raise HTTPException(
                status_code=500,
                detail="Unable to start checkout. Please try again later.",
            ) from exc
        raise HTTPException(
            status_code=402,
            detail={
                "message": "You have used your free alert. Upgrade to unlimited alerts for €3 (lifetime).",
                "upgrade_url": checkout["checkout_url"],
                "checkout_id": checkout["checkout_id"],
            },
        )

    token = _generate_token()
    sub = AlertSubscription(
        email=payload.email,
        country=payload.country,
        city=payload.city,
        product_type=payload.product_type,
        min_btu=payload.min_btu,
        max_price=payload.max_price,
        in_stock_only=payload.in_stock_only,
        frequency=payload.frequency,
        verification_token=token,
    )
    session.add(sub)
    await session.commit()

    success = await _send_confirmation_email(payload.email, token)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Unable to send confirmation email. Please try again later.",
        )

    return {
        "message": "Please check your email to confirm the alert.",
        "token": token if settings.debug else None,
    }


@router.get("/confirm", response_class=HTMLResponse)
async def confirm(
    request: Request,
    token: str,
    session: AsyncSession = Depends(get_db),
):
    stmt = select(AlertSubscription).where(
        AlertSubscription.verification_token == token
    )
    sub = await session.scalar(stmt)
    if not sub:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    sub.verified = True
    sub.active = True
    await session.commit()

    return templates.TemplateResponse(
        request,
        "alert_confirm.html",
        {
            "title": "Alert confirmed",
            "success": True,
            "message": "You're subscribed! We'll email you when matching ACs are in stock.",
            "token": token,
        },
    )


@router.get("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe(
    request: Request,
    token: str,
    session: AsyncSession = Depends(get_db),
):
    stmt = select(AlertSubscription).where(
        AlertSubscription.verification_token == token
    )
    sub = await session.scalar(stmt)
    if not sub:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    sub.active = False
    await session.commit()

    return templates.TemplateResponse(
        request,
        "alert_confirm.html",
        {
            "title": "Unsubscribed",
            "success": True,
            "message": "You have been unsubscribed and will no longer receive alerts.",
        },
    )


@router.post("/test/{token}")
async def test_alert(
    token: str,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Send a test alert email to the subscription identified by its token."""
    await subscribe_limiter.check(_client_ip(request))
    stmt = select(AlertSubscription).where(
        AlertSubscription.verification_token == token,
        AlertSubscription.active.is_(True),
        AlertSubscription.verified.is_(True),
    )
    sub = await session.scalar(stmt)
    if not sub:
        raise HTTPException(
            status_code=404, detail="Active verified subscription not found"
        )

    backend = get_email_backend()
    subject = "🌡️ KlimaRadar: test alert"
    body = f"""
    <html>
      <body>
        <h2>This is a test alert from KlimaRadar</h2>
        <p>If you received this email, your alert subscription is working correctly.</p>
        <p style="font-size:12px;color:#666;">
          You subscribed to alerts for {sub.country}.
          <br>
          <a href="{settings.base_url}/api/alerts/unsubscribe?token={sub.verification_token}">Unsubscribe</a>
        </p>
      </body>
    </html>
    """.strip()
    success = await backend.send(sub.email, subject, body)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send test alert")
    return {"message": f"Test alert sent to {sub.email}"}


