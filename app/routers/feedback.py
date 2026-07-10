"""User feedback API and page."""

import hashlib
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.cloudflare import get_client_ip
from app.config import settings
from app.database import get_db
from app.models import Feedback
from app.rate_limit import feedback_limiter
from app.schemas import FeedbackCreate
from app.services.alerter import get_email_backend
from app.templating import templates

logger = logging.getLogger(__name__)
router = APIRouter()


def _client_ip(request: Request) -> str:
    return get_client_ip(request)


def _hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()[:32]


async def _send_feedback_notification(feedback: Feedback) -> bool:
    """Email the site owner when new feedback is submitted."""
    backend = get_email_backend()
    subject = f"📝 New KlimaRadar feedback from {feedback.name or 'anonymous'}"
    body = f"""
    <html>
      <body>
        <h2>New feedback on KlimaRadar</h2>
        <ul>
          <li><strong>Name:</strong> {feedback.name or 'Not provided'}</li>
          <li><strong>Email:</strong> {feedback.email or 'Not provided'}</li>
          <li><strong>Page:</strong> {feedback.page_url or 'Not provided'}</li>
        </ul>
        <p><strong>Message:</strong></p>
        <p>{feedback.message.replace(chr(10), '<br>')}</p>
      </body>
    </html>
    """.strip()
    try:
        return await backend.send(settings.from_email, subject, body)
    except Exception:
        logger.exception("Failed to send feedback notification email")
        return False


@router.get("/feedback", response_class=HTMLResponse)
async def feedback_page(
    request: Request,
    page: str | None = None,
):
    return templates.TemplateResponse(
        request,
        "feedback.html",
        {
            "title": "Feedback — KlimaRadar",
            "description": "Help us improve KlimaRadar by reporting bugs, suggesting features, or sharing your experience.",
            "page_url": page or str(request.headers.get("referer", "")),
            "settings": settings,
        },
    )


@router.post("/api/feedback")
async def submit_feedback(
    payload: FeedbackCreate,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    await feedback_limiter.check(_client_ip(request))

    feedback = Feedback(
        name=payload.name,
        email=payload.email,
        message=payload.message,
        page_url=payload.page_url,
        user_agent=request.headers.get("user-agent"),
        ip_hash=_hash_ip(_client_ip(request)),
    )
    session.add(feedback)
    await session.commit()

    # Notify admin asynchronously; failure should not break the user experience.
    await _send_feedback_notification(feedback)

    return {"message": "Thank you for your feedback!"}
