"""Seed script for demo data and initial retailers."""

import asyncio

from app.config import settings
from app.database import AsyncSessionLocal, engine
from app.models import Base, Retailer
from app.services.scraper import run_scrape


async def seed_retailers(session: AsyncSession) -> None:
    """Create retailer rows if they do not exist."""
    retailers = [
        Retailer(
            name="Amazon Germany",
            country="DE",
            domain="https://www.amazon.de",
            affiliate_network="amazon_associates",
        ),
        Retailer(
            name="MediaMarkt Germany",
            country="DE",
            domain="https://www.mediamarkt.de",
            affiliate_network="awin",
        ),
        Retailer(
            name="Boulanger France",
            country="FR",
            domain="https://www.boulanger.com",
            affiliate_network="tradedoubler",
        ),
        Retailer(
            name="Darty France",
            country="FR",
            domain="https://www.darty.com",
            affiliate_network="tradedoubler",
        ),
    ]
    if settings.enable_demo:
        retailers.insert(
            0,
            Retailer(
                name="Demo Retailer",
                country="DEMO",
                domain="https://example.com",
                affiliate_network="none",
            ),
        )

    for retailer in retailers:
        existing = await session.scalar(
            select(Retailer).where(
                Retailer.name == retailer.name,
                Retailer.country == retailer.country,
            )
        )
        if not existing:
            session.add(retailer)

    await session.commit()


async def seed_demo_data(session: AsyncSession | None = None) -> None:
    """Ensure retailers exist and populate demo listings when enabled."""
    close_session = session is None
    if session is None:
        session = AsyncSessionLocal()

    try:
        await seed_retailers(session)
        if settings.enable_demo:
            # Run the demo spider to insert sample listings.
            await run_scrape(country="DEMO")
    finally:
        if close_session:
            await session.close()


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_demo_data()
    print("Demo data seeded.")


if __name__ == "__main__":
    asyncio.run(main())
