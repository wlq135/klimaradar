"""CLI helpers for ad-hoc operations."""

import argparse
import asyncio

from app.services.scraper import run_scrape


async def scrape_command(country: str | None = None) -> None:
    # The CLI runs outside the FastAPI lifespan, so it must initialize the
    # schema itself: create_all builds any missing tables, and run_migrations
    # backfills columns added after launch (e.g. alert subscription frequency).
    from app.database import engine, run_migrations
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await run_migrations()

    # Ensure retailers are seeded so every registered spider has a retailer row
    # to write to. The CLI must not depend on a prior server startup.
    from app.database import AsyncSessionLocal
    from app.seed import seed_demo_data

    async with AsyncSessionLocal() as session:
        await seed_demo_data(session)

    results = await run_scrape(country=country)
    for name, result in results.items():
        print(f"{name}: {result}")


def main() -> None:
    parser = argparse.ArgumentParser(description="KlimaRadar CLI")
    subparsers = parser.add_subparsers(dest="command")

    scrape_parser = subparsers.add_parser("scrape", help="Run spiders manually")
    scrape_parser.add_argument(
        "--country", type=str, default=None, help="Limit scrape to one country"
    )

    args = parser.parse_args()
    if args.command == "scrape":
        asyncio.run(scrape_command(country=args.country))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
