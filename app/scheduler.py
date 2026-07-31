"""Background scheduler for periodic scraping and digest emails."""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import datetime, timedelta, timezone
from sqlalchemy import delete
from app.models import AlertDigest, PriceHistory

from app.config import settings
from app.database import AsyncSessionLocal
from app.services.alerter import send_daily_digests
from app.services.scraper import run_scrape

logger = logging.getLogger(__name__)


async def _scheduled_scrape():
    try:
        results = await run_scrape()
        logger.info("Scheduled scrape completed: %s", results)
    except Exception as exc:
        logger.exception("Scheduled scrape failed: %s", exc)


async def _scheduled_digest():
    try:
        async with AsyncSessionLocal() as session:
            sent = await send_daily_digests(session)
            logger.info("Daily digest sent %s email(s)", sent)
    except Exception as exc:
        logger.exception("Daily digest job failed: %s", exc)


async def _scheduled_cleanup():
    """Purge historical data to keep the database bounded.

    Keeps 90 days of price history and removes alert digests already sent
    more than 30 days ago. Without this price_history grows ~1M rows/year.
    """
    try:
        now = datetime.now(timezone.utc)
        price_cutoff = now - timedelta(days=90)
        digest_cutoff = now - timedelta(days=30)
        async with AsyncSessionLocal() as session:
            price_result = await session.execute(
                delete(PriceHistory).where(PriceHistory.captured_at < price_cutoff)
            )
            digest_result = await session.execute(
                delete(AlertDigest).where(
                    AlertDigest.sent_at.is_not(None),
                    AlertDigest.sent_at < digest_cutoff,
                )
            )
            await session.commit()
            logger.info(
                "Cleanup removed %s old price rows, %s sent digests",
                price_result.rowcount,
                digest_result.rowcount,
            )
    except Exception as exc:
        logger.exception("Scheduled cleanup failed: %s", exc)


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the APScheduler instance."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _scheduled_scrape,
        "interval",
        minutes=settings.scraper_interval_minutes,
        id="ac_scrape",
        replace_existing=True,
    )
    scheduler.add_job(
        _scheduled_digest,
        "cron",
        hour=8,
        minute=0,
        id="daily_digest",
        replace_existing=True,
    )

    scheduler.add_job(
        _scheduled_cleanup,
        "cron",
        hour=3,
        minute=30,
        id="data_cleanup",
        replace_existing=True,
    )
    return scheduler
