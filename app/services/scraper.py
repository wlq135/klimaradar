"""High-level scraper orchestration."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Retailer
from app.services.stock_monitor import upsert_listings
from app.spiders.registry import get_spiders_for_country

logger = logging.getLogger(__name__)


async def _build_retailer_map(session: AsyncSession) -> dict[tuple[str, str], int]:
    result = await session.scalars(select(Retailer))
    return {(r.country, r.name): r.id for r in result}


async def run_scrape(country: str | None = None) -> dict[str, dict]:
    """Run all registered spiders and persist their listings.

    Args:
        country: optional ISO country code to limit the scrape.

    Returns:
        A mapping of spider name -> run result with ``success``, ``listings``,
        and ``stats`` keys.
    """
    async with AsyncSessionLocal() as session:
        retailer_map = await _build_retailer_map(session)
        spiders = get_spiders_for_country(retailer_map, country_filter=country)
        if not spiders:
            logger.warning("No spiders configured for country=%s", country)
            return {}

        results: dict[str, dict] = {}
        for spider in spiders:
            try:
                snapshots = await spider.fetch_listings(
                    query="portable air conditioner",
                    product_type="portable",
                )
                stats = await upsert_listings(
                    session, spider.retailer_id, spider.country, snapshots
                )
                results[spider.name] = {
                    "success": True,
                    "listings": len(snapshots),
                    "stats": stats,
                }
                logger.info(
                    "Spider %s fetched %d listings. Stats: %s",
                    spider.name,
                    len(snapshots),
                    stats,
                )
            except Exception as exc:
                logger.exception("Spider %s failed: %s", spider.name, exc)
                results[spider.name] = {
                    "success": False,
                    "error": str(exc),
                    "listings": 0,
                    "stats": {},
                }
        return results
