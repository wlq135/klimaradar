"""Standalone scraper worker for deployments where the web process is small.

The worker owns Playwright/Chromium and sends normalized snapshots to the web
service. The web service persists them to its existing SQLite disk and handles
alerts, avoiding a cross-service SQLite mount (which Render does not support).
"""

import asyncio
import gc
import json
import logging
import os
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

import httpx

from app.config import settings
logger = logging.getLogger(__name__)

_SPIDER_TARGETS: list[tuple[str, str]] = [
    ("DE", "Amazon Germany"),
    ("FR", "Amazon France"),
    ("IT", "Amazon Italy"),
    ("ES", "Amazon Spain"),
    ("NL", "Amazon Netherlands"),
    ("BE", "Amazon Belgium"),
    ("GB", "Amazon United Kingdom"),
]


def get_spider_specs(country_filter: str | None = None):
    """Load spider classes lazily so the supervisor can stay lightweight."""
    from app.spiders.registry import get_spider_specs as load_spider_specs

    return load_spider_specs(country_filter)


def _get_spider_targets(country_filter: str | None = None) -> list[tuple[str, str]]:
    """Return retailer targets without importing Playwright in the supervisor."""
    targets = list(_SPIDER_TARGETS)
    if settings.playwright_proxy_server:
        targets.extend([
            ("DE", "MediaMarkt Germany"),
            ("FR", "Boulanger France"),
            ("FR", "Darty France"),
        ])
    if country_filter:
        targets = [target for target in targets if target[0] == country_filter]
    return targets


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


async def run_worker_once_in_children() -> dict[str, dict]:
    """Run each retailer in a fresh child process.

    Chromium frequently does not return all renderer memory to the container
    after ``browser.close()``. Running all seven marketplaces sequentially in
    one process repeatedly pushed the 512 MB Render Starter worker over its
    limit. A small supervisor parent never launches Chromium;
    each child scrapes one marketplace and exits, returning that memory to the
    operating system before the next marketplace starts.
    """
    targets = _get_spider_targets(settings.worker_country.upper() or None)
    results: dict[str, dict] = {}

    for country, retailer_name in targets:
        with tempfile.TemporaryDirectory(prefix="klimaradar-worker-") as state_dir:
            result_path = Path(state_dir) / "result.json"
            command = [
                sys.executable,
                "-m",
                "app.worker",
                "--child",
                "--country",
                country,
                "--result-file",
                str(result_path),
            ]
            logger.info("Starting isolated worker child for %s", retailer_name)
            process = await asyncio.create_subprocess_exec(*command)
            return_code = await process.wait()

            child_result: dict[str, dict] = {}
            if result_path.exists():
                try:
                    child_result = json.loads(result_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    logger.exception("Could not read result from worker child")

            if return_code != 0:
                logger.error(
                    "Isolated worker child for %s exited with code %s",
                    retailer_name,
                    return_code,
                )
                child_result.pop(retailer_name, None)
                child_result[retailer_name] = {
                    "success": False,
                    "error": f"worker child exited with code {return_code}",
                    "listings": 0,
                    "stats": {},
                }

            results.update(child_result)
            logger.info(
                "Isolated worker child finished %s: %s",
                retailer_name,
                results.get(retailer_name, {}),
            )

    return results


async def run_worker_forever() -> None:
    """Run scraping cycles forever at the configured interval."""
    completed_cycles = 0
    while True:
        try:
            if settings.worker_isolated_spiders:
                results = await run_worker_once_in_children()
            else:
                results = await run_worker_once()
            logger.info("Worker cycle completed: %s", results)
        except Exception:
            logger.exception("Worker cycle failed")

        if settings.worker_isolated_spiders:
            # Chromium only exists in short-lived child processes. Sleeping in
            # the lightweight parent avoids pointless supervisor restarts.
            await asyncio.sleep(max(1, settings.scraper_interval_minutes) * 60)
            continue

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


def _write_child_result(path: str, results: dict[str, dict]) -> None:
    """Persist child results without putting secrets or logs in the file."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results), encoding="utf-8")


def _run_cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="KlimaRadar standalone scraper worker")
    parser.add_argument("--child", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--country", default=settings.worker_country)
    parser.add_argument("--result-file", default="", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.child:
        settings.worker_country = args.country
        child_results = asyncio.run(run_worker_once())
        if args.result_file:
            _write_child_result(args.result_file, child_results)
        return

    asyncio.run(run_worker_forever())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    _run_cli()
