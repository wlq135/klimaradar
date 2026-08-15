"""Tests for the periodic scraper scheduler."""

from datetime import datetime, timezone

from app.scheduler import create_scheduler


def test_scraper_runs_soon_after_startup():
    scheduler = create_scheduler()
    job = scheduler.get_job("ac_scrape")

    assert job is not None
    delay = (job.next_run_time - datetime.now(timezone.utc)).total_seconds()
    assert 0 < delay <= 60
