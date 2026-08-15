"""Detect stock and price changes from newly scraped snapshots."""

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import Listing, PriceHistory, Product, Retailer
from app.services.affiliate import tag_url
from app.services.alerter import notify_subscribers_for_listing
from app.services.product_attributes import enrich_snapshot
from app.spiders.base import ListingSnapshot

logger = logging.getLogger(__name__)


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
    alert_events: list[tuple[str, int]] = []

    retailer = await session.get(Retailer, retailer_id)
    if not retailer:
        raise ValueError(f"Retailer {retailer_id} not found")

    for snap in snapshots:
        # Last line of defense: reject garbage snapshots (empty name or url,
        # or invalid stock status) so a malformed scrape never pollutes the DB
        # and reaches users. This catches e.g. a challenge page that parsed
        # partially instead of failing outright.
        if not snap.name or not snap.name.strip() or not snap.url:
            logger.warning("Skipping invalid snapshot: name=%r url=%r", snap.name, snap.url)
            continue
        if snap.stock_status not in {
            "in_stock", "out_of_stock", "back_order", "pre_order", "low_stock", "unknown"
        }:
            logger.warning("Skipping snapshot with invalid stock_status=%r", snap.stock_status)
            continue
        enrich_snapshot(snap)
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

        # Detect meaningful events but do not send emails yet; we want to commit
        # the listing changes before holding the DB lock during SMTP sends.
        if previous_status != "in_stock" and listing.stock_status == "in_stock":
            stats["back_in_stock"] += 1
            alert_events.append(("back in stock", listing.id))
        elif (
            previous_price is not None
            and listing.price is not None
            and listing.price < previous_price
        ):
            stats["price_dropped"] += 1
            alert_events.append(("on sale", listing.id))

        if is_new:
            stats["created"] += 1
        else:
            stats["updated"] += 1

    await session.commit()

    # Send alert emails outside the main transaction so a slow SMTP relay
    # does not hold the SQLite lock and block web requests.
    for event_type, listing_id in alert_events:
        try:
            async with AsyncSessionLocal() as alert_session:
                listing_obj = await alert_session.scalar(
                    select(Listing)
                    .where(Listing.id == listing_id)
                    .options(
                        selectinload(Listing.product),
                        selectinload(Listing.retailer),
                    )
                )
                if listing_obj:
                    await notify_subscribers_for_listing(
                        alert_session, listing_obj, event_type
                    )
        except Exception:
            logger.exception(
                "Failed to send %s alerts for listing %s", event_type, listing_id
            )

    return stats


async def _get_or_create_product(
    session: AsyncSession, snap: ListingSnapshot
) -> Product:
    # Match by name + product type. Older Amazon products may have null brand
    # and BTU fields, so an exact-name match is also used to backfill them
    # instead of creating duplicate canonical products.
    stmt = select(Product).where(
        Product.name == snap.name,
        Product.product_type == snap.product_type,
    )
    product = await session.scalar(stmt)
    if product:
        if snap.brand:
            product.brand = snap.brand
        if snap.btu_min is not None:
            product.btu_min = snap.btu_min
        if snap.btu_max is not None:
            product.btu_max = snap.btu_max
        if snap.image_url:
            product.image_url = snap.image_url
        session.add(product)
        await session.flush()
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
