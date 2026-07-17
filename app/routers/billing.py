"""Billing and Paddle webhook endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.cloudflare import get_client_ip
from app.config import settings
from app.database import get_db
from app.rate_limit import billing_limiter
from app.services.lemon_squeezy import (
    create_checkout as create_lemon_squeezy_checkout,
    handle_lemon_squeezy_event,
    verify_signature as verify_lemon_squeezy_signature,
)
from app.services.paddle import (
    create_checkout,
    handle_paddle_event,
    verify_paddle_signature,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/billing")


def _client_ip(request: Request) -> str:
    return get_client_ip(request)


class CheckoutRequest(BaseModel):
    email: EmailStr


class CheckoutResponse(BaseModel):
    checkout_url: str
    transaction_id: str


class LemonSqueezyCheckoutResponse(BaseModel):
    checkout_url: str
    checkout_id: str


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    payload: CheckoutRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    await billing_limiter.check(_client_ip(request))
    try:
        result = await create_checkout(payload.email)
    except Exception as exc:
        logger.exception("Failed to create Paddle checkout")
        raise HTTPException(
            status_code=500,
            detail="Unable to start checkout. Please try again later.",
        ) from exc
    return CheckoutResponse(**result)


@router.post("/webhooks/paddle")
async def paddle_webhook(request: Request, session: AsyncSession = Depends(get_db)):
    """Handle Paddle webhook events.

    Always returns 200 for valid requests so Paddle does not retry. Invalid
    signatures return 400.
    """
    body = await request.body()
    signature_header = request.headers.get("Paddle-Signature", "")

    if not settings.paddle_webhook_secret:
        logger.warning("Paddle webhook secret not configured; rejecting webhook")
        raise HTTPException(status_code=400, detail="Webhook not configured")

    if not verify_paddle_signature(
        settings.paddle_webhook_secret, body, signature_header
    ):
        logger.warning("Invalid Paddle webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        event = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    try:
        await handle_paddle_event(session, event)
    except Exception:
        logger.exception("Failed to process Paddle event")
        # Still return 200 so Paddle does not retry.

    return {"status": "ok"}


@router.post("/lemon-squeezy/checkout", response_model=LemonSqueezyCheckoutResponse)
async def lemon_squeezy_checkout(
    payload: CheckoutRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Create a Lemon Squeezy checkout for unlimited alerts."""
    await billing_limiter.check(_client_ip(request))
    try:
        result = await create_lemon_squeezy_checkout(payload.email)
    except Exception as exc:
        logger.exception("Failed to create Lemon Squeezy checkout")
        raise HTTPException(
            status_code=500,
            detail="Unable to start checkout. Please try again later.",
        ) from exc
    return LemonSqueezyCheckoutResponse(**result)


@router.post("/webhooks/lemon-squeezy")
async def lemon_squeezy_webhook(
    request: Request, session: AsyncSession = Depends(get_db)
):
    """Handle Lemon Squeezy webhook events.

    Always returns 200 for valid requests so Lemon Squeezy does not retry.
    Invalid signatures or unconfigured secrets return 400.
    """
    body = await request.body()
    signature_header = request.headers.get("X-Signature", "")

    if not settings.lemon_squeezy_webhook_secret:
        logger.warning("Lemon Squeezy webhook secret not configured; rejecting webhook")
        raise HTTPException(status_code=400, detail="Webhook not configured")

    if not verify_lemon_squeezy_signature(
        settings.lemon_squeezy_webhook_secret, body, signature_header
    ):
        logger.warning("Invalid Lemon Squeezy webhook signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        event = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    try:
        await handle_lemon_squeezy_event(session, event)
    except Exception:
        logger.exception("Failed to process Lemon Squeezy event")
        # Still return 200 so Lemon Squeezy does not retry.

    return {"status": "ok"}
