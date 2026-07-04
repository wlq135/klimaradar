"""Background scheduler for periodic scraping."""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.services.scraper import run_scrape

logger = logging.getLogger(__name__)


async def _scheduled_scrape():
    try:
        results = await run_scrape()
        logger.info("Scheduled scrape completed: %s", results)
    except Exception as exc:
        logger.exception("Scheduled scrape failed: %s", exc)


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
    return scheduler
