"""Email alert generation and delivery."""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import AlertLog, AlertSubscription, Listing

logger = logging.getLogger(__name__)


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


def get_email_backend() -> EmailBackend:
    """Return the configured email backend.

    Priority: SMTP > SendGrid > console fallback.
    """
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
    """Find matching active subscriptions and send them an alert.

    Args:
        session: database session.
        listing: the listing that changed.
        event_type: human-readable event like "back in stock" or "price drop".

    Returns:
        Number of alerts sent.
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
        if sub.city and sub.city != listing.city_tag:
            continue
        if sub.product_type and sub.product_type != listing.product.product_type:
            continue
        if sub.min_btu and (listing.product.btu_min or 0) < sub.min_btu:
            continue
        if sub.max_price and (listing.price or float("inf")) > sub.max_price:
            continue
        if sub.in_stock_only and listing.stock_status != "in_stock":
            continue

        # Avoid duplicate alerts for the same listing within 24 hours.
        recent = await session.scalar(
            select(AlertLog).where(
                AlertLog.subscription_id == sub.id,
                AlertLog.listing_id == listing.id,
                AlertLog.sent_at >= datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
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
