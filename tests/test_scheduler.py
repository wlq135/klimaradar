"""Tests for the periodic scraper scheduler."""

from datetime import datetime, timezone

from app.config import settings
from app.scheduler import create_scheduler


def test_scraper_runs_soon_after_startup():
    assert settings.scraper_interval_minutes == 10
    scheduler = create_scheduler()
    job = scheduler.get_job("ac_scrape")

    assert job is not None
    delay = (job.next_run_time - datetime.now(timezone.utc)).total_seconds()
    assert 0 < delay <= 60


def test_scheduler_can_be_disabled_to_protect_web_instance(monkeypatch):
    monkeypatch.setattr(settings, "enable_scheduler", False)
    scheduler = create_scheduler()

    assert scheduler.get_jobs() == []
