"""Tests for the standalone scraper worker and its ingest API."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models import Base, Listing, Product, Retailer
from app.routers import pages
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

    session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(db_session, monkeypatch):
    monkeypatch.setattr(pages.settings, "admin_api_key", "test-admin-key")
    pages.admin_scrape_limiter._store.clear()
    app = FastAPI()
    app.include_router(pages.router)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


def test_spider_specs_are_registry_driven(monkeypatch):
    from app.config import settings
    from app.spiders.registry import get_spider_specs

    monkeypatch.setattr(settings, "playwright_proxy_server", "")
    specs = get_spider_specs()
    assert [(country, name) for country, name, _ in specs] == [
        ("DE", "Amazon Germany"),
        ("FR", "Amazon France"),
        ("IT", "Amazon Italy"),
        ("ES", "Amazon Spain"),
        ("NL", "Amazon Netherlands"),
        ("BE", "Amazon Belgium"),
        ("GB", "Amazon United Kingdom"),
    ]

    german_specs = get_spider_specs("DE")
    assert [(country, name) for country, name, _ in german_specs] == [
        ("DE", "Amazon Germany")
    ]


def test_web_scheduler_can_run_maintenance_without_scraping(monkeypatch):
    from app.config import settings
    from app.scheduler import create_scheduler

    monkeypatch.setattr(settings, "enable_scheduler", True)
    monkeypatch.setattr(settings, "enable_scraper", False)
    scheduler = create_scheduler()

    assert scheduler.get_job("ac_scrape") is None
    assert scheduler.get_job("daily_digest") is not None
    assert scheduler.get_job("data_cleanup") is not None
    assert scheduler.get_job("db_backup") is not None


@pytest.mark.asyncio
async def test_ingest_rejects_missing_admin_key(client):
    response = await client.post(
        "/api/admin/ingest",
        json={"country": "DE", "retailer_name": "Amazon Germany", "snapshots": []},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_ingest_rejects_unknown_retailer(client):
    response = await client.post(
        "/api/admin/ingest",
        headers={"X-Admin-API-Key": "test-admin-key"},
        json={"country": "DE", "retailer_name": "Missing", "snapshots": []},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ingest_persists_worker_snapshots(client, db_session):
    retailer = Retailer(name="Amazon Germany", country="DE", domain="amazon.de")
    db_session.add(retailer)
    await db_session.commit()

    response = await client.post(
        "/api/admin/ingest",
        headers={"X-Admin-API-Key": "test-admin-key"},
        json={
            "country": "DE",
            "retailer_name": "Amazon Germany",
            "queries": ["mobile klimagerät 12000 BTU"],
            "snapshots": [
                {
                    "name": "Midea 12000 BTU Mobile Klimagerät",
                    "brand": "Midea",
                    "sku": "B0WORKER1",
                    "url": "https://www.amazon.de/dp/B0WORKER1",
                    "price": 399.99,
                    "currency": "EUR",
                    "stock_status": "in_stock",
                    "delivery_days": 2,
                    "image_url": "https://images.amazon.com/item.jpg",
                    "btu_min": 12000,
                    "btu_max": 12000,
                    "product_type": "portable",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["listings"] == 1
    listing = await db_session.scalar(select(Listing).where(Listing.sku == "B0WORKER1"))
    assert listing is not None
    assert listing.retailer_id == retailer.id
    assert listing.price == 399.99
    product = await db_session.get(Product, listing.product_id)
    assert product.name == "Midea 12000 BTU Mobile Klimagerät"
    assert product.btu_min == 12000


@pytest.mark.asyncio
async def test_worker_posts_normalized_payload(monkeypatch):
    from app import worker
    from app.config import settings

    class FakeSpider:
        def __init__(self, retailer_id: int, country: str):
            self.retailer_id = retailer_id
            self.country = country

        async def fetch_listings_for_queries(self, queries, product_type=None):
            assert queries == ["portable air conditioner"]
            assert product_type == "portable"
            return [
                ListingSnapshot(
                    name="Worker AC",
                    brand="Midea",
                    sku="B0WORKERPAYLOAD",
                    url="https://www.amazon.de/dp/B0WORKERPAYLOAD",
                    price=299.0,
                    currency="EUR",
                    stock_status="in_stock",
                    delivery_days=1,
                    image_url=None,
                    btu_min=9000,
                    btu_max=9000,
                    product_type="portable",
                    specs_json=None,
                )
            ]

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"listings": 1, "stats": {"created": 1}}

    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.posts = []

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return None

        async def post(self, path, json):
            self.posts.append((path, json))
            return FakeResponse()

    created_clients = []

    def fake_client_factory(**kwargs):
        client = FakeClient(**kwargs)
        created_clients.append(client)
        return client

    monkeypatch.setattr(settings, "worker_api_base", "https://klima-radar.com/")
    monkeypatch.setattr(settings, "worker_api_key", "")
    monkeypatch.setattr(settings, "admin_api_key", "test-admin-key")
    monkeypatch.setattr(settings, "worker_country", "de")
    monkeypatch.setattr(worker, "get_spider_specs", lambda country: [("DE", "Amazon Germany", FakeSpider)])
    monkeypatch.setattr(worker.httpx, "AsyncClient", fake_client_factory)

    results = await worker.run_worker_once()
    fake_client = created_clients[0]

    assert results == {
        "Amazon Germany": {
            "success": True,
            "listings": 1,
            "stats": {"created": 1},
        }
    }
    path, payload = fake_client.posts[0]
    assert path == "/api/admin/ingest"
    assert fake_client.kwargs["base_url"] == "https://klima-radar.com"
    assert fake_client.kwargs["headers"] == {"X-Admin-API-Key": "test-admin-key"}
    assert payload["country"] == "DE"
    assert payload["retailer_name"] == "Amazon Germany"
    assert payload["queries"] == ["portable air conditioner"]
    assert payload["snapshots"][0]["sku"] == "B0WORKERPAYLOAD"
