"""Email alert generation and delivery."""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import AlertDigest, AlertLog, AlertSubscription, Listing

logger = logging.getLogger(__name__)


def _start_of_day(dt: datetime | None = None) -> datetime:
    dt = dt or datetime.now(timezone.utc)
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


async def _digest_already_queued_today(
    session: AsyncSession, subscription_id: int, listing_id: int
) -> bool:
    """Return True if a digest entry already exists for this sub/listing today."""
    existing = await session.scalar(
        select(AlertDigest).where(
            AlertDigest.subscription_id == subscription_id,
            AlertDigest.listing_id == listing_id,
            AlertDigest.created_at >= _start_of_day(),
        )
    )
    return existing is not None


async def _queue_digest_alert(
    session: AsyncSession,
    subscription: AlertSubscription,
    listing: Listing,
    event_type: str,
) -> None:
    """Add a matching listing to the subscriber's daily digest queue."""
    if await _digest_already_queued_today(session, subscription.id, listing.id):
        return
    session.add(
        AlertDigest(
            subscription_id=subscription.id,
            listing_id=listing.id,
            event_type=event_type,
        )
    )


class EmailBackend:
    """Abstract email backend."""

    async def send(self, to_email: str, subject: str, body: str) -> bool:
        raise NotImplementedError


class ConsoleEmailBackend(EmailBackend):
    """Prints emails to the console — useful for local development."""

    async def send(self, to_email: str, subject: str, body: str) -> bool:
        print("=" * 60)
        print(f"TO: {to_email}")
        print(f"SUBJECT: {subject}")
        print("-" * 60)
        print(body)
        print("=" * 60)
        return True


class SendGridEmailBackend(EmailBackend):
    """Sends email via SendGrid API."""

    def __init__(self, api_key: str, from_email: str):
        self.api_key = api_key
        self.from_email = from_email

    async def send(self, to_email: str, subject: str, body: str) -> bool:
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
        except ImportError:  # pragma: no cover
            logger.error("sendgrid package not installed")
            return False

        client = SendGridAPIClient(self.api_key)
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=body,
        )
        try:
            response = await asyncio.to_thread(client.send, message)
            return 200 <= response.status_code < 300
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to send email via SendGrid: %s", exc)
            return False


class SmtpEmailBackend(EmailBackend):
    """Sends email via any SMTP relay (Brevo, Mailgun, AWS SES, etc.)."""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        from_email: str,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.from_email = from_email

    async def send(self, to_email: str, subject: str, body: str) -> bool:
        try:
            from aiosmtplib import send
            from email.message import EmailMessage
        except ImportError:  # pragma: no cover
            logger.error("aiosmtplib package not installed")
            return False

        message = EmailMessage()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body, subtype="html")

        try:
            await send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                start_tls=True,
            )
            return True
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to send email via SMTP: %s", exc)
            return False


class BrevoApiEmailBackend(EmailBackend):
    """Sends email via the Brevo v3 transactional email API.

    This is a useful fallback when Brevo's SMTP relay is not yet activated
    on a new account.
    """

    def __init__(self, api_key: str, from_email: str):
        self.api_key = api_key
        self.from_email = from_email

    async def send(self, to_email: str, subject: str, body: str) -> bool:
        try:
            import httpx
        except ImportError:  # pragma: no cover
            logger.error("httpx package not installed")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={
                        "api-key": self.api_key,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    json={
                        "sender": {"name": "KlimaRadar", "email": self.from_email},
                        "to": [{"email": to_email}],
                        "subject": subject,
                        "htmlContent": body,
                    },
                    timeout=30,
                )
            if response.is_success:
                return True
            logger.error(
                "Brevo API returned %s: %s", response.status_code, response.text
            )
            return False
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to send email via Brevo API: %s", exc)
            return False


def get_email_backend() -> EmailBackend:
    """Return the configured email backend.

    Priority: Brevo API > SMTP > SendGrid > console fallback.
    """
    if settings.brevo_api_key:
        return BrevoApiEmailBackend(settings.brevo_api_key, settings.from_email)
    if settings.smtp_host and settings.smtp_user and settings.smtp_password:
        return SmtpEmailBackend(
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_user,
            settings.smtp_password,
            settings.from_email,
        )
    if settings.sendgrid_api_key:
        return SendGridEmailBackend(settings.sendgrid_api_key, settings.from_email)
    return ConsoleEmailBackend()


async def notify_subscribers_for_listing(
    session: AsyncSession,
    listing: Listing,
    event_type: str,
) -> int:
    """Find matching active subscriptions and send or queue an alert.

    Args:
        session: database session.
        listing: the listing that changed.
        event_type: human-readable event like "back in stock" or "price drop".

    Returns:
        Number of alerts sent or queued.
    """
    # Match by country, city (optional), product type, BTU, price.
    stmt = select(AlertSubscription).where(
        AlertSubscription.active.is_(True),
        AlertSubscription.verified.is_(True),
        AlertSubscription.country == listing.country,
    )
    subs = (await session.scalars(stmt)).all()

    sent = 0
    backend = get_email_backend()
    for sub in subs:
        if sub.city:
            listing_city = (listing.city_tag or "").lower()
            if listing_city and listing_city != sub.city.lower():
                continue
        if sub.product_type and sub.product_type != listing.product.product_type:
            continue
        if sub.min_btu and (listing.product.btu_max or 0) < sub.min_btu:
            continue
        if sub.max_price and (listing.price or float("inf")) > sub.max_price:
            continue
        if sub.in_stock_only and listing.stock_status != "in_stock":
            continue

        if sub.frequency == "daily":
            await _queue_digest_alert(session, sub, listing, event_type)
            sent += 1
            continue

        # Avoid duplicate alerts for the same listing within 24 hours.
        recent = await session.scalar(
            select(AlertLog).where(
                AlertLog.subscription_id == sub.id,
                AlertLog.listing_id == listing.id,
                AlertLog.sent_at >= _start_of_day(),
            )
        )
        if recent:
            continue

        subject = f"🌡️ KlimaRadar: {listing.product.name} is {event_type}"
        body = _render_alert_body(sub, listing, event_type)
        success = await backend.send(sub.email, subject, body)
        if success:
            log = AlertLog(
                subscription_id=sub.id,
                listing_id=listing.id,
                channel="email",
            )
            session.add(log)
            sent += 1

    await session.commit()
    return sent


def _render_alert_body(
    subscription: AlertSubscription, listing: Listing, event_type: str
) -> str:
    price_str = f"€{listing.price:.2f}" if listing.price else "Price unavailable"
    product_url = listing.affiliate_url or listing.url
    return f"""
    <html>
      <body>
        <h2>KlimaRadar Alert</h2>
        <p>Hi,</p>
        <p>A unit matching your alert is now <strong>{event_type}</strong>:</p>
        <ul>
          <li><strong>{listing.product.name}</strong></li>
          <li>Price: {price_str}</li>
          <li>Status: {listing.stock_status.replace('_', ' ').title()}</li>
          <li>Retailer: {listing.retailer.name}</li>
        </ul>
        <p>
          <a href="{product_url}" style="padding:10px 15px;background:#2563eb;color:#fff;text-decoration:none;border-radius:5px;">
            View / Buy Now
          </a>
        </p>
        <p style="font-size:12px;color:#666;">
          You received this because you subscribed to KlimaRadar alerts for {subscription.country}.
          <br>
          <a href="{settings.base_url}/api/alerts/unsubscribe?token={subscription.verification_token}">Unsubscribe</a>
        </p>
      </body>
    </html>
    """.strip()


async def send_daily_digests(session: AsyncSession) -> int:
    """Send one grouped email per daily subscriber for queued matches.

    Returns:
        Number of digest emails successfully sent.
    """
    stmt = (
        select(AlertDigest)
        .where(AlertDigest.sent_at.is_(None))
        .options(
            selectinload(AlertDigest.subscription),
            selectinload(AlertDigest.listing).selectinload(Listing.product),
            selectinload(AlertDigest.listing).selectinload(Listing.retailer),
        )
        .order_by(AlertDigest.created_at)
    )
    rows = (await session.scalars(stmt)).all()

    by_subscription: dict[int, list[AlertDigest]] = defaultdict(list)
    for row in rows:
        by_subscription[row.subscription_id].append(row)

    backend = get_email_backend()
    sent_count = 0
    now = datetime.now(timezone.utc)
    for entries in by_subscription.values():
        subscription = entries[0].subscription
        if not subscription.active or not subscription.verified:
            continue
        if subscription.frequency != "daily":
            continue

        subject = f"🌡️ KlimaRadar daily digest — {len(entries)} new match(es)"
        body = _render_digest_body(subscription, entries)
        success = await backend.send(subscription.email, subject, body)
        if success:
            for entry in entries:
                entry.sent_at = now
            subscription.digest_last_sent_at = now
            sent_count += 1

    await session.commit()
    return sent_count


def _render_digest_body(
    subscription: AlertSubscription, entries: list[AlertDigest]
) -> str:
    """Build an HTML digest from queued alert entries."""
    items_html = ""
    for entry in entries:
        listing = entry.listing
        price_str = f"€{listing.price:.2f}" if listing.price else "Price unavailable"
        product_url = listing.affiliate_url or listing.url
        items_html += f"""
        <li style="margin-bottom:12px;">
          <strong>{listing.product.name}</strong> — {entry.event_type}<br>
          Price: {price_str} · Status: {listing.stock_status.replace('_', ' ').title()} · Retailer: {listing.retailer.name}<br>
          <a href="{product_url}">View / Buy Now</a>
        </li>
        """

    return f"""
    <html>
      <body>
        <h2>KlimaRadar Daily Digest</h2>
        <p>Hi,</p>
        <p>Here are the AC matches we found for your alert in {subscription.country}:</p>
        <ul>
          {items_html}
        </ul>
        <p style="font-size:12px;color:#666;">
          You received this because you subscribed to daily KlimaRadar alerts for {subscription.country}.
          <br>
          <a href="{settings.base_url}/api/alerts/unsubscribe?token={subscription.verification_token}">Unsubscribe</a>
        </p>
      </body>
    </html>
    """.strip()
