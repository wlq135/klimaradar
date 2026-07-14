"""Background scheduler for periodic scraping and digest emails."""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

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
    return scheduler
