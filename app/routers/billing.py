"""Billing and Paddle webhook endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.cloudflare import get_client_ip
from app.config import settings
from app.database import get_db
from app.rate_limit import billing_limiter
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
