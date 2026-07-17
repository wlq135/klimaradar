"""Lemon Squeezy billing integration helpers.

This module uses direct HTTP calls against the Lemon Squeezy API v1 so we can
keep dependencies minimal (``httpx`` is already used elsewhere). It creates
checkouts, verifies webhook signatures, and updates the local ``PaidCustomer``
record based on Lemon Squeezy events.
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
from app.models import LemonSqueezyPayment, PaidCustomer

logger = logging.getLogger(__name__)

_FREE_ALERT_LIMIT = 1

_API_BASE = "https://api.lemonsqueezy.com/v1"


def _headers() -> dict[str, str]:
    return {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {settings.lemon_squeezy_api_key}",
    }


async def create_checkout(email: str) -> dict[str, str]:
    """Create a Lemon Squeezy checkout and return the hosted checkout URL."""
    if not settings.lemon_squeezy_api_key:
        raise RuntimeError("Lemon Squeezy API key must be configured")
    if not settings.lemon_squeezy_store_id or not settings.lemon_squeezy_variant_id:
        raise RuntimeError("Lemon Squeezy store and variant IDs must be configured")

    payload = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "checkout_data": {
                    "email": email,
                    "custom": {"email": email},
                },
            },
            "relationships": {
                "store": {
                    "data": {
                        "type": "stores",
                        "id": settings.lemon_squeezy_store_id,
                    }
                },
                "variant": {
                    "data": {
                        "type": "variants",
                        "id": settings.lemon_squeezy_variant_id,
                    }
                },
            },
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{_API_BASE}/checkouts",
            headers=_headers(),
            json=payload,
            timeout=30.0,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error(
                "Lemon Squeezy /checkouts failed: status=%s body=%s",
                response.status_code,
                response.text,
            )
            raise
        data = response.json()["data"]

    return {
        "checkout_id": data["id"],
        "checkout_url": data["attributes"]["url"],
    }


def verify_signature(secret: str, body: bytes, signature_header: str) -> bool:
    """Verify the ``X-Signature`` header on a webhook request.

    The signature is computed as ``HMAC-SHA256(secret, body).hexdigest()``.
    """
    computed = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(computed, signature_header)


def _email_from_event(data: dict) -> str | None:
    """Extract the email from a Lemon Squeezy event payload.

    We prefer the email stored in ``checkout_data.custom.email`` because we put
    it there explicitly when creating the checkout. Otherwise fall back to the
    ``user_email`` attribute.
    """
    attributes = data.get("attributes") or {}
    if isinstance(attributes, dict):
        checkout_data = attributes.get("checkout_data") or {}
        if isinstance(checkout_data, dict):
            custom = checkout_data.get("custom") or {}
            if isinstance(custom, dict) and custom.get("email"):
                return custom["email"].lower()

        user_email = attributes.get("user_email")
        if isinstance(user_email, str) and user_email:
            return user_email.lower()

    return None


async def _get_or_create_paid_customer(session: AsyncSession, email: str) -> PaidCustomer:
    stmt = select(PaidCustomer).where(func.lower(PaidCustomer.email) == email.lower())
    customer = await session.scalar(stmt)
    if customer is None:
        customer = PaidCustomer(email=email.lower())
        session.add(customer)
    return customer


async def _already_processed(session: AsyncSession, event_id: str) -> bool:
    existing = await session.scalar(
        select(LemonSqueezyPayment).where(LemonSqueezyPayment.event_id == event_id)
    )
    return existing is not None


async def handle_lemon_squeezy_event(session: AsyncSession, event: dict) -> None:
    """Process a verified Lemon Squeezy webhook event.

    Idempotent: duplicate ``event_id`` values are ignored.
    """
    meta = event.get("meta") or {}
    event_id = meta.get("event_id")
    event_name = meta.get("event_name", "unknown")
    data = event.get("data") or {}

    if not event_id:
        logger.warning("Lemon Squeezy event missing event_id: %s", event_name)
        return

    if await _already_processed(session, event_id):
        logger.debug("Lemon Squeezy event %s already processed", event_id)
        return

    attributes = data.get("attributes") or {}
    order_id = data.get("id")
    checkout_id = attributes.get("checkout_id")
    email = _email_from_event(data)
    status = attributes.get("status")
    if isinstance(status, str):
        status = status.lower()

    total = attributes.get("total")
    currency = attributes.get("currency")
    amount = str(total) if total is not None else None

    payment = LemonSqueezyPayment(
        event_id=event_id,
        event_name=event_name,
        order_id=order_id,
        checkout_id=checkout_id,
        email=email,
        status=status,
        amount=amount,
        currency=currency,
        payload_json=json.dumps(event, ensure_ascii=False),
    )
    session.add(payment)

    now = datetime.now(timezone.utc)

    if event_name == "order_created" and status == "paid":
        if email:
            customer = await _get_or_create_paid_customer(session, email)
            customer.is_paid = True
            customer.paid_at = now
            customer.revoked_at = None
            payment.paid_at = now
        else:
            logger.warning("Lemon Squeezy order_created event missing email: %s", event_id)

    elif event_name == "order_refunded":
        if email:
            customer = await _get_or_create_paid_customer(session, email)
            customer.is_paid = False
            customer.revoked_at = now
            payment.refunded_at = now
        else:
            logger.warning("Lemon Squeezy order_refunded event missing email: %s", event_id)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        logger.warning("IntegrityError processing Lemon Squeezy event %s", event_id)


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
