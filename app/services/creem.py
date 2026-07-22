"""Creem billing integration helpers.

This module uses direct HTTP calls against the Creem API v1 so we can keep
dependencies minimal (``httpx`` is already used elsewhere). It creates checkouts,
verifies webhook signatures, and updates the local ``PaidCustomer`` record based
on Creem events.
"""

import hashlib
import hmac
import json
import logging
import secrets
import uuid
from datetime import datetime, timezone

import httpx
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import CreemCheckoutSession, CreemPayment, PaidCustomer

logger = logging.getLogger(__name__)

_FREE_ALERT_LIMIT = 1


def _api_base() -> str:
    return settings.creem_api_base.rstrip("/")


def _headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "x-api-key": settings.creem_api_key,
    }


def _success_url() -> str:
    return f"{settings.base_url.rstrip('/')}/pricing?success=1"


def _amount_to_str(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return str(value)
    return str(value) if value else None


async def create_checkout(email: str) -> dict[str, str]:
    """Create a Creem checkout and return the hosted checkout URL."""
    if not settings.creem_api_key:
        raise RuntimeError("Creem API key must be configured")
    if not settings.creem_product_id:
        raise RuntimeError("Creem product ID must be configured")

    request_id = f"req_{uuid.uuid4().hex[:16]}"
    payload = {
        "product_id": settings.creem_product_id,
        "success_url": _success_url(),
        "request_id": request_id,
        "metadata": {"email": email.lower()},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{_api_base()}/checkouts",
            headers=_headers(),
            json=payload,
            timeout=30.0,
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error(
                "Creem /checkouts failed: status=%s body=%s",
                response.status_code,
                response.text,
            )
            raise
        data = response.json()

    checkout_id = data.get("id")
    checkout_url = data.get("checkout_url")
    if not checkout_id or not checkout_url:
        raise RuntimeError(f"Unexpected Creem checkout response: {data}")

    return {
        "checkout_id": checkout_id,
        "checkout_url": checkout_url,
        "request_id": request_id,
    }


def verify_signature(secret: str, body: bytes, signature_header: str) -> bool:
    """Verify the ``creem-signature`` header on a webhook request.

    The signature is computed as ``HMAC-SHA256(secret, body).hexdigest()``.
    The secret is stripped of surrounding whitespace to tolerate copy-paste
    errors in environment variables.
    """
    cleaned_secret = secret.strip()
    computed = hmac.new(
        cleaned_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    match = hmac.compare_digest(computed, signature_header)
    if not match:
        logger.warning(
            "Creem signature mismatch: computed=%s... received=%s... body_len=%s",
            computed[:8],
            signature_header[:8] if signature_header else "",
            len(body),
        )
    return match


def _email_from_event(event: dict, obj: dict) -> str | None:
    """Extract the customer email from a Creem event.

    Some events nest the email under ``object.customer`` or
    ``object.metadata.email``; others put it at the top-level
    ``metadata.email``. We check all common locations.
    """
    for source in (obj, event):
        customer = source.get("customer") or {}
        if isinstance(customer, dict):
            email = customer.get("email")
            if isinstance(email, str) and email:
                return email.lower()
        metadata = source.get("metadata") or {}
        if isinstance(metadata, dict):
            email = metadata.get("email")
            if isinstance(email, str) and email:
                return email.lower()
    return None


def _order_id_from_event(obj: dict) -> str | None:
    """Extract the order id from a Creem event object."""
    if isinstance(obj.get("id"), str):
        return obj["id"]
    order = obj.get("order") or {}
    if isinstance(order, dict):
        return order.get("id")
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
        select(CreemPayment).where(CreemPayment.event_id == event_id)
    )
    return existing is not None


async def handle_creem_event(session: AsyncSession, event: dict) -> None:
    """Process a verified Creem webhook event.

    Idempotent: duplicate ``event_id`` values are ignored.
    """
    event_id = event.get("id")
    event_type = event.get("eventType") or event.get("event_type", "unknown")
    obj = event.get("object") or {}

    if not event_id:
        logger.warning("Creem event missing id: %s", event_type)
        return

    if await _already_processed(session, event_id):
        logger.debug("Creem event %s already processed", event_id)
        return

    checkout_id = None
    checkout = obj.get("checkout") or {}
    if isinstance(checkout, dict):
        checkout_id = checkout.get("id")
    if not checkout_id and isinstance(obj.get("checkout_id"), str):
        checkout_id = obj["checkout_id"]

    order_id = _order_id_from_event(obj)
    customer_id = None
    customer = obj.get("customer") or {}
    if isinstance(customer, dict):
        customer_id = customer.get("id")
    email = _email_from_event(event, obj)
    product_id = None
    product = obj.get("product") or {}
    if isinstance(product, dict):
        product_id = product.get("id")

    status = obj.get("status")
    if isinstance(status, str):
        status = status.lower()

    amount = _amount_to_str(obj.get("amount"))
    currency = obj.get("currency")

    logger.info(
        "Processing Creem event: id=%s type=%s order_id=%s email=%s product_id=%s status=%s",
        event_id,
        event_type,
        order_id,
        email,
        product_id,
        status,
    )

    payment = CreemPayment(
        event_id=event_id,
        event_type=event_type,
        checkout_id=checkout_id,
        order_id=order_id,
        customer_id=customer_id,
        email=email,
        product_id=product_id,
        status=status,
        amount=amount,
        currency=currency,
        payload_json=json.dumps(event, ensure_ascii=False),
    )
    session.add(payment)

    now = datetime.now(timezone.utc)

    if event_type == "checkout.completed":
        if email:
            customer = await _get_or_create_paid_customer(session, email)
            customer.is_paid = True
            customer.paid_at = now
            customer.revoked_at = None
            payment.paid_at = now
            logger.info("Granted paid access to %s from Creem event %s", email, event_id)
        else:
            logger.warning("Creem checkout.completed event missing email: %s", event_id)

    elif event_type == "refund.created":
        refund_email = email
        if not refund_email:
            refund_customer = obj.get("customer") or {}
            if isinstance(refund_customer, dict):
                refund_email = refund_customer.get("email")
        if refund_email:
            customer = await _get_or_create_paid_customer(session, refund_email)
            customer.is_paid = False
            customer.revoked_at = now
            payment.refunded_at = now
        else:
            logger.warning("Creem refund.created event missing email: %s", event_id)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        logger.warning("IntegrityError processing Creem event %s", event_id)


async def record_checkout_session(
    session: AsyncSession, request_id: str, email: str, checkout_id: str
) -> CreemCheckoutSession:
    """Persist the request_id -> email mapping for post-redirect lookups."""
    checkout_session = CreemCheckoutSession(
        request_id=request_id,
        email=email.lower(),
        checkout_id=checkout_id,
    )
    session.add(checkout_session)
    await session.commit()
    return checkout_session


async def get_session_status(
    session: AsyncSession, request_id: str
) -> dict[str, object] | None:
    """Return the email and paid status for a Creem checkout request_id."""
    stmt = select(CreemCheckoutSession).where(
        CreemCheckoutSession.request_id == request_id
    )
    checkout_session = await session.scalar(stmt)
    if checkout_session is None:
        return None
    paid = await has_paid_access(session, checkout_session.email)
    return {
        "email": checkout_session.email,
        "paid": paid,
        "checkout_id": checkout_session.checkout_id,
    }


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
