"""Standalone scraper worker for deployments where the web process is small.

The worker owns Playwright/Chromium and sends normalized snapshots to the web
service. The web service persists them to its existing SQLite disk and handles
alerts, avoiding a cross-service SQLite mount (which Render does not support).
"""

import asyncio
import gc
import logging
import os
import sys
from dataclasses import asdict

import httpx

from app.config import settings
from app.spiders.registry import get_spider_specs

logger = logging.getLogger(__name__)


def _restart_worker_process() -> None:
    """Replace this process with a fresh worker using the same environment."""
    executable = sys.executable or "python"
    args = [executable, "-m", "app.worker"]
    logger.warning("Restarting worker process to release Chromium memory")
    os.execv(executable, args)


async def run_worker_once() -> dict[str, dict]:
    """Run one scraping cycle and upload one batch per retailer."""
    api_base = settings.worker_api_base.rstrip("/")
    api_key = settings.worker_api_key or settings.admin_api_key
    if not api_base or not api_key:
        raise RuntimeError(
            "WORKER_API_BASE and WORKER_API_KEY (or ADMIN_API_KEY) are required"
        )

    country = settings.worker_country.upper() or None
    specs = get_spider_specs(country)
    results: dict[str, dict] = {}

    async with httpx.AsyncClient(
        base_url=api_base,
        headers={"X-Admin-API-Key": api_key},
        timeout=httpx.Timeout(120, connect=30),
    ) as client:
        for spider_country, retailer_name, spider_cls in specs:
            spider = spider_cls(retailer_id=0, country=spider_country)
            try:
                queries = list(getattr(spider, "default_queries", None) or [])
                if not queries:
                    queries = [getattr(spider, "default_query", "portable air conditioner")]

                snapshots = await spider.fetch_listings_for_queries(
                    queries,
                    product_type="portable",
                )
                response = await client.post(
                    "/api/admin/ingest",
                    json={
                        "country": spider_country,
                        "retailer_name": retailer_name,
                        "queries": queries,
                        "snapshots": [asdict(snapshot) for snapshot in snapshots],
                    },
                )
                response.raise_for_status()
                body = response.json()
                results[retailer_name] = {
                    "success": True,
                    "listings": body.get("listings", len(snapshots)),
                    "stats": body.get("stats", {}),
                }
                logger.info(
                    "Worker uploaded %s listings for %s: %s",
                    len(snapshots),
                    retailer_name,
                    body.get("stats", {}),
                )
            except Exception as exc:
                logger.exception("Worker spider %s failed: %s", retailer_name, exc)
                results[retailer_name] = {
                    "success": False,
                    "error": str(exc),
                    "listings": 0,
                    "stats": {},
                }
            finally:
                gc.collect()
                await asyncio.sleep(1)

    return results


async def run_worker_forever() -> None:
    """Run scraping cycles forever at the configured interval."""
    completed_cycles = 0
    while True:
        try:
            results = await run_worker_once()
            logger.info("Worker cycle completed: %s", results)
        except Exception:
            logger.exception("Worker cycle failed")
        completed_cycles += 1
        await asyncio.sleep(max(1, settings.scraper_interval_minutes) * 60)

        restart_after = settings.worker_restart_cycles
        if restart_after > 0 and completed_cycles >= restart_after:
            logger.info(
                "Completed %s worker cycles; recycling process",
                completed_cycles,
            )
            _restart_worker_process()
            # os.execv normally never returns. Keeping this explicit return
            # also makes the function safe for tests and non-POSIX hosts.
            return


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(run_worker_forever())
