"""CLI helpers for ad-hoc operations."""

import argparse
import asyncio

from app.services.scraper import run_scrape


async def scrape_command(country: str | None = None) -> None:
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
