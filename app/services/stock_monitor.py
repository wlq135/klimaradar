"""Detect stock and price changes from newly scraped snapshots."""

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Listing, PriceHistory, Product, Retailer
from app.services.affiliate import tag_url
from app.services.alerter import notify_subscribers_for_listing
from app.spiders.base import ListingSnapshot


async def upsert_listings(
    session: AsyncSession,
    retailer_id: int,
    country: str,
    snapshots: list[ListingSnapshot],
) -> dict[str, int]:
    """Persist spider snapshots to the database and detect changes.

    Returns:
        A counter dict with keys: created, updated, back_in_stock, price_dropped.
    """
    stats = {"created": 0, "updated": 0, "back_in_stock": 0, "price_dropped": 0}

    retailer = await session.get(Retailer, retailer_id)
    if not retailer:
        raise ValueError(f"Retailer {retailer_id} not found")

    for snap in snapshots:
        product = await _get_or_create_product(session, snap)
        listing, is_new = await _get_or_create_listing(
            session, retailer_id, product.id, snap, country
        )

        previous_status = listing.stock_status
        previous_price = listing.price

        listing.name = snap.name  # denormalize for quick display
        listing.price = snap.price
        listing.currency = snap.currency
        listing.stock_status = snap.stock_status
        listing.delivery_days = snap.delivery_days
        listing.last_seen_at = datetime.now(timezone.utc)
        listing.country = country
        listing.city_tag = None  # city tags are derived from landing pages, not listings
        listing.url = snap.url
        listing.affiliate_url = tag_url(retailer.domain, snap.url)

        # Keep relationships loaded so downstream services can read them without extra queries.
        listing.product = product
        listing.retailer = retailer

        session.add(listing)
        await session.flush()

        # Record a price-history snapshot for every scrape.
        history = PriceHistory(
            listing_id=listing.id,
            price=listing.price,
            stock_status=listing.stock_status,
        )
        session.add(history)

        # Detect meaningful events.
        if previous_status != "in_stock" and listing.stock_status == "in_stock":
            stats["back_in_stock"] += 1
            await notify_subscribers_for_listing(session, listing, "back in stock")
        elif (
            previous_price is not None
            and listing.price is not None
            and listing.price < previous_price
        ):
            stats["price_dropped"] += 1
            await notify_subscribers_for_listing(session, listing, "on sale")

        if is_new:
            stats["created"] += 1
        else:
            stats["updated"] += 1

    await session.commit()
    return stats


async def _get_or_create_product(
    session: AsyncSession, snap: ListingSnapshot
) -> Product:
    # Try to match by name + brand + product type to avoid duplicates.
    stmt = select(Product).where(
        Product.name == snap.name,
        Product.brand == snap.brand,
        Product.product_type == snap.product_type,
    )
    product = await session.scalar(stmt)
    if product:
        return product

    product = Product(
        name=snap.name,
        brand=snap.brand,
        product_type=snap.product_type,
        btu_min=snap.btu_min,
        btu_max=snap.btu_max,
        image_url=snap.image_url,
        specs_json=snap.specs_json or json.dumps({}),
    )
    session.add(product)
    await session.flush()
    return product


async def _get_or_create_listing(
    session: AsyncSession,
    retailer_id: int,
    product_id: int,
    snap: ListingSnapshot,
    country: str,
) -> tuple[Listing, bool]:
    # Match by retailer + SKU when available (Amazon ASIN, MediaMarkt product id).
    # URLs change between scrapes due to session/query params, so SKU is more stable.
    if snap.sku:
        stmt = select(Listing).where(
            Listing.retailer_id == retailer_id,
            Listing.sku == snap.sku,
        )
    else:
        stmt = select(Listing).where(
            Listing.retailer_id == retailer_id,
            Listing.product_id == product_id,
            Listing.url == snap.url,
        )
    listing = await session.scalar(stmt)
    if listing:
        return listing, False

    listing = Listing(
        retailer_id=retailer_id,
        product_id=product_id,
        sku=snap.sku,
        url=snap.url,
        affiliate_url=tag_url("", snap.url),
        price=snap.price,
        currency=snap.currency,
        stock_status=snap.stock_status,
        delivery_days=snap.delivery_days,
        country=country,
    )
    session.add(listing)
    await session.flush()
    return listing, True
