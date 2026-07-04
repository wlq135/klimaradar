"""Tests for affiliate link tagging and the /go redirect."""

import os

# Configure the test environment BEFORE any app modules are imported so the
# settings object is loaded with the test affiliate tags.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["AMAZON_DE_AFFILIATE_TAG"] = "klrmrd-21"
os.environ["MEDIAMARKT_DE_AFFILIATE_TAG"] = "klrmrd"
os.environ["BOULANGER_FR_AFFILIATE_TAG"] = "klrmrd"

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models import Base, ClickEvent, Listing, Product, Retailer
from app.routers import pages


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
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(db_session):
    app = FastAPI()
    app.include_router(pages.router)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


async def _create_test_listing(
    session: AsyncSession,
    retailer_name: str,
    domain: str,
    url: str,
    country: str = "DE",
) -> Listing:
    product = Product(
        name="Test Portable AC",
        brand="TestBrand",
        product_type="portable",
        btu_max=9000,
    )
    retailer = Retailer(
        name=retailer_name,
        country=country,
        domain=domain,
        affiliate_network="test",
    )
    session.add_all([product, retailer])
    await session.flush()

    listing = Listing(
        product_id=product.id,
        retailer_id=retailer.id,
        url=url,
        affiliate_url=None,
        country=country,
        stock_status="in_stock",
    )
    session.add(listing)
    await session.commit()
    return listing


@pytest.mark.asyncio
async def test_go_redirect_tags_amazon_url_and_logs_click(client, db_session):
    listing = await _create_test_listing(
        db_session,
        retailer_name="Amazon Germany",
        domain="https://www.amazon.de",
        url="https://www.amazon.de/dp/B08EXAMPLE",
    )

    response = await client.get(
        f"/go/{listing.id}", follow_redirects=False
    )

    assert response.status_code in (307, 302)
    location = response.headers["location"]
    assert "tag=klrmrd-21" in location

    click_count = await db_session.scalar(select(func.count(ClickEvent.id)))
    assert click_count == 1


@pytest.mark.asyncio
async def test_go_redirect_tags_mediamarkt_url(client, db_session):
    listing = await _create_test_listing(
        db_session,
        retailer_name="MediaMarkt Germany",
        domain="https://www.mediamarkt.de",
        url="https://www.mediamarkt.de/de/product/test-klimaanlage-123.html",
    )

    response = await client.get(
        f"/go/{listing.id}", follow_redirects=False
    )

    assert response.status_code in (307, 302)
    location = response.headers["location"]
    assert "ref=klrmrd" in location


@pytest.mark.asyncio
async def test_go_redirect_returns_404_for_missing_listing(client, db_session):
    response = await client.get("/go/999999", follow_redirects=False)
    assert response.status_code == 404
