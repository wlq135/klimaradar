"""Tests for snapshot validation in upsert_listings."""

import os
from datetime import datetime, timezone

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Listing, Product, Retailer
from app.services.stock_monitor import upsert_listings
from app.spiders.base import ListingSnapshot


@pytest.fixture
async def db_session():
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        future=True,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        retailer = Retailer(name="TestShop", country="DE", domain="testshop.de")
        session.add(retailer)
        await session.commit()
        session.retailer_id = retailer.id
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


def _snap(name="Valid AC", url="https://t.de/p", price=299.0, stock_status="in_stock", sku="SKU1"):
    return ListingSnapshot(
        name=name, brand=None, sku=sku, url=url,
        price=price, currency="EUR", stock_status=stock_status,
        delivery_days=None, image_url=None, btu_min=None, btu_max=None,
        product_type="portable",
    )


@pytest.mark.asyncio
async def test_valid_snapshot_is_persisted(db_session):
    stats = await upsert_listings(db_session, db_session.retailer_id, "DE", [_snap()])
    assert stats["created"] == 1
    listings = (await db_session.scalars(select(Listing))).all()
    assert len(listings) == 1
    assert listings[0].price == 299.0


@pytest.mark.asyncio
async def test_empty_name_is_rejected(db_session):
    stats = await upsert_listings(db_session, db_session.retailer_id, "DE", [_snap(name="", url="https://t.de/p")])
    assert stats["created"] == 0
    listings = (await db_session.scalars(select(Listing))).all()
    assert len(listings) == 0


@pytest.mark.asyncio
async def test_empty_url_is_rejected(db_session):
    stats = await upsert_listings(db_session, db_session.retailer_id, "DE", [_snap(url="")])
    assert stats["created"] == 0
    listings = (await db_session.scalars(select(Listing))).all()
    assert len(listings) == 0


@pytest.mark.asyncio
async def test_invalid_stock_status_is_rejected(db_session):
    stats = await upsert_listings(
        db_session, db_session.retailer_id, "DE",
        [_snap(stock_status="bogus_status")],
    )
    assert stats["created"] == 0
    listings = (await db_session.scalars(select(Listing))).all()
    assert len(listings) == 0


@pytest.mark.asyncio
async def test_mixed_batch_keeps_only_valid(db_session):
    snaps = [_snap(name=""), _snap(), _snap(stock_status="weird"), _snap(name="Second AC", url="https://t.de/p2", sku=None)]
    stats = await upsert_listings(db_session, db_session.retailer_id, "DE", snaps)
    assert stats["created"] == 2
    listings = (await db_session.scalars(select(Listing))).all()
    assert len(listings) == 2


@pytest.mark.asyncio
async def test_attributes_are_parsed_and_backfilled_without_duplicate_products(db_session):
    name = "Midea 12,000 BTU Portable Air Conditioner"
    legacy = Product(name=name, brand=None, product_type="portable")
    db_session.add(legacy)
    await db_session.flush()

    snapshot = _snap(
        name=name,
        url="https://t.de/p/asin",
        sku="ASIN1",
    )

    stats = await upsert_listings(db_session, db_session.retailer_id, "DE", [snapshot])

    products = (await db_session.scalars(select(Product))).all()
    listings = (await db_session.scalars(select(Listing))).all()
    assert stats["created"] == 1
    assert len(products) == 1
    assert len(listings) == 1
    assert products[0].brand == "Midea"
    assert products[0].btu_min == 12000
    assert products[0].btu_max == 12000
    assert listings[0].product_id == products[0].id


@pytest.mark.asyncio
async def test_successful_scrape_retires_missing_retailer_rows(db_session):
    now = datetime.now(timezone.utc)
    current = Product(name="Current Midea 12000 BTU AC", product_type="portable")
    removed = Product(name="Removed Evaporative Cooler", product_type="portable")
    db_session.add_all([current, removed])
    await db_session.flush()
    db_session.add_all(
        [
            Listing(
                product_id=current.id,
                retailer_id=db_session.retailer_id,
                sku="CURRENT",
                url="https://t.de/current",
                country="DE",
                stock_status="in_stock",
                last_seen_at=now,
            ),
            Listing(
                product_id=removed.id,
                retailer_id=db_session.retailer_id,
                sku="REMOVED",
                url="https://t.de/removed",
                country="DE",
                stock_status="in_stock",
                last_seen_at=now,
            ),
        ]
    )
    await db_session.commit()

    snapshot = _snap(
        name="Current Midea 12000 BTU AC",
        url="https://t.de/current",
        sku="CURRENT",
    )
    stats = await upsert_listings(db_session, db_session.retailer_id, "DE", [snapshot])

    rows = {listing.sku: listing for listing in (await db_session.scalars(select(Listing)))}
    assert stats["retired"] == 1
    now_naive = now.replace(tzinfo=None)
    assert rows["CURRENT"].last_seen_at.replace(tzinfo=None) > now_naive
    assert rows["REMOVED"].last_seen_at.replace(tzinfo=None) < now_naive
