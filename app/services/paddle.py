"""Paddle Billing integration helpers.

This module uses direct HTTP calls against the Paddle Billing API v2 so we can
keep dependencies minimal (``httpx`` is already used elsewhere). It creates
checkout transactions, verifies webhook signatures, and updates the local
``PaidCustomer`` record based on Paddle events.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import PaddleCustomer, PaddlePayment, PaidCustomer

logger = logging.getLogger(__name__)

_FREE_ALERT_LIMIT = 1


def _api_base() -> str:
    return (
        "https://sandbox-api.paddle.com"
        if settings.paddle_environment == "sandbox"
        else "https://api.paddle.com"
    )


def _headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.paddle_api_key}",
    }


async def create_checkout(email: str) -> dict[str, str]:
    """Create a Paddle transaction and return the hosted checkout URL."""
    if not settings.paddle_api_key or not settings.paddle_price_id:
        raise RuntimeError("Paddle API key and price ID must be configured")

    payload = {
        "items": [
            {
                "price": {"id": settings.paddle_price_id},
                "quantity": 1,
            }
        ],
        "customer": {"email": email},
        "custom_data": {"email": email},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{_api_base()}/transactions",
            headers=_headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()["data"]

    return {
        "transaction_id": data["id"],
        "checkout_url": data["checkout"]["url"],
    }


def verify_paddle_signature(secret: str, body: bytes, signature_header: str) -> bool:
    """Verify the ``Paddle-Signature`` header on a webhook request.

    The header format is ``ts=<timestamp>,h1=<hex_signature>``. The signature is
    computed as ``HMAC-SHA256(secret, f"{ts}:{body}")``.
    """
    parts = {}
    for part in signature_header.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            parts[key.strip()] = value.strip()

    timestamp = parts.get("ts")
    expected = parts.get("h1")
    if not timestamp or not expected:
        return False

    signed_payload = f"{timestamp}:{body.decode('utf-8')}"
    computed = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, expected)


def _email_from_event(data: dict) -> str | None:
    """Extract the email from Paddle event data.

    We prefer the email stored in ``custom_data`` because we put it there
    explicitly when creating the checkout. Otherwise fall back to the customer
    object.
    """
    custom_data = data.get("custom_data") or {}
    if isinstance(custom_data, dict) and custom_data.get("email"):
        return custom_data["email"].lower()

    customer = data.get("customer") or {}
    if isinstance(customer, dict) and customer.get("email"):
        return customer["email"].lower()

    return None


def _transaction_status(data: dict) -> str | None:
    status = data.get("status")
    return status.lower() if isinstance(status, str) else status


def _payment_amount(data: dict) -> tuple[str | None, str | None]:
    details = data.get("details") or {}
    totals = details.get("totals") or {}
    return totals.get("total"), totals.get("currency_code")


async def _get_or_create_paid_customer(session: AsyncSession, email: str) -> PaidCustomer:
    stmt = select(PaidCustomer).where(func.lower(PaidCustomer.email) == email.lower())
    customer = await session.scalar(stmt)
    if customer is None:
        customer = PaidCustomer(email=email.lower())
        session.add(customer)
    return customer


async def _record_paddle_customer(
    session: AsyncSession, email: str, paddle_customer_id: str
) -> None:
    stmt = select(PaddleCustomer).where(func.lower(PaddleCustomer.email) == email.lower())
    existing = await session.scalar(stmt)
    if existing is None:
        session.add(
            PaddleCustomer(
                email=email.lower(),
                paddle_customer_id=paddle_customer_id,
            )
        )
    elif existing.paddle_customer_id != paddle_customer_id:
        existing.paddle_customer_id = paddle_customer_id


async def _already_processed(session: AsyncSession, event_id: str) -> bool:
    existing = await session.scalar(
        select(PaddlePayment).where(PaddlePayment.event_id == event_id)
    )
    return existing is not None


async def handle_paddle_event(session: AsyncSession, event: dict) -> None:
    """Process a verified Paddle webhook event.

    Idempotent: duplicate ``event_id`` values are ignored.
    """
    event_id = event.get("event_id")
    event_type = event.get("event_type", "unknown")
    data = event.get("data") or {}

    if not event_id:
        logger.warning("Paddle event missing event_id: %s", event_type)
        return

    if await _already_processed(session, event_id):
        logger.debug("Paddle event %s already processed", event_id)
        return

    email = _email_from_event(data)
    paddle_customer_id = data.get("customer_id")
    transaction_id = data.get("id")
    status = _transaction_status(data)
    amount, currency = _payment_amount(data)

    # Store the raw event for debugging/auditing.
    payment = PaddlePayment(
        paddle_transaction_id=transaction_id or "unknown",
        paddle_customer_id=paddle_customer_id,
        email=email,
        status=status,
        amount=str(amount) if amount is not None else None,
        currency=currency,
        event_id=event_id,
        event_type=event_type,
        payload_json=json.dumps(event, ensure_ascii=False),
    )
    session.add(payment)

    if email and paddle_customer_id:
        await _record_paddle_customer(session, email, paddle_customer_id)

    now = datetime.now(timezone.utc)

    if event_type in ("transaction.paid", "transaction.completed"):
        if email:
            customer = await _get_or_create_paid_customer(session, email)
            customer.is_paid = True
            customer.paid_at = now
            customer.revoked_at = None
            payment.paid_at = now
        else:
            logger.warning("Paddle %s event missing email: %s", event_type, event_id)

    elif event_type == "transaction.updated" and status == "refunded":
        if email:
            customer = await _get_or_create_paid_customer(session, email)
            customer.is_paid = False
            customer.revoked_at = now
            payment.refunded_at = now
        else:
            logger.warning("Paddle refund event missing email: %s", event_id)

    elif event_type == "payment.refunded":
        if email:
            customer = await _get_or_create_paid_customer(session, email)
            customer.is_paid = False
            customer.revoked_at = now
            payment.refunded_at = now
        else:
            logger.warning("Paddle refund event missing email: %s", event_id)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        logger.warning("IntegrityError processing Paddle event %s", event_id)


async def has_paid_access(session: AsyncSession, email: str) -> bool:
    """Return True if the given email has an active paid subscription."""
    stmt = select(PaidCustomer).where(func.lower(PaidCustomer.email) == email.lower())
    customer = await session.scalar(stmt)
    return bool(customer and customer.is_paid)


async def active_alert_count(session: AsyncSession, email: str) -> int:
    """Count active alerts for the given email address."""
    from app.models import AlertSubscription

    stmt = (
        select(func.count(AlertSubscription.id))
        .where(func.lower(AlertSubscription.email) == email.lower())
        .where(AlertSubscription.active.is_(True))
    )
    return (await session.scalar(stmt)) or 0


async def can_create_alert(session: AsyncSession, email: str) -> dict[str, bool]:
    """Return whether the user can create another alert and whether they are paid."""
    paid = await has_paid_access(session, email)
    if paid:
        return {"allowed": True, "paid": True}
    count = await active_alert_count(session, email)
    return {"allowed": count < _FREE_ALERT_LIMIT, "paid": False}
