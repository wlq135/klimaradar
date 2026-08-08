"""Background scheduler for periodic scraping and digest emails."""

import asyncio
import logging
import os
import shutil
import glob
import re
from urllib.parse import urlparse

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


def _get_db_path() -> str:
    """Extract the filesystem path of the SQLite database from the URL."""
    url = settings.database_url
    # sqlite+aiosqlite:///path/to/db or sqlite+aiosqlite:////absolute/path
    match = re.sub(r"^sqlite\+aiosqlite://", "", url)
    return match


async def _scheduled_backup():
    """Create a timestamped copy of the SQLite database.

    Keeps the 7 most recent backups; older ones are deleted automatically.
    Runs every 6 hours so at most a few hours of data is lost on failure.
    """
    try:
        db_path = _get_db_path()
        if not os.path.exists(db_path):
            logger.warning("Backup skipped: DB file %s not found", db_path)
            return

        backup_dir = os.path.join(os.path.dirname(db_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"klimaradar_{timestamp}.db")
        shutil.copy2(db_path, backup_path)
        logger.info("Database backed up to %s", backup_path)

        # Keep only the 7 most recent backups
        backups = sorted(
            glob.glob(os.path.join(backup_dir, "klimaradar_*.db")),
            key=os.path.getmtime,
        )
        for old in backups[:-7]:
            os.remove(old)
            logger.info("Removed old backup %s", old)
    except Exception as exc:
        logger.exception("Scheduled backup failed: %s", exc)


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
    scheduler.add_job(
        _scheduled_backup,
        "interval",
        hours=6,
        id="db_backup",
        replace_existing=True,
    )
    return scheduler
