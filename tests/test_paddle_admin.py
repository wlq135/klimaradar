"""Tests for the Paddle checkout domains admin endpoint."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")
os.environ["ADMIN_API_KEY"] = "test-admin-key"
os.environ["PADDLE_API_KEY"] = "test-paddle-key"
os.environ["PADDLE_ENVIRONMENT"] = "sandbox"

import httpx
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import get_db
from app.models import Base
from app.rate_limit import admin_scrape_limiter
from app.routers import pages


@pytest.fixture(autouse=True)
def configure_settings():
    """Ensure admin and Paddle settings are populated for every test."""
    settings.admin_api_key = "test-admin-key"
    settings.paddle_api_key = "test-paddle-key"
    settings.paddle_environment = "sandbox"
    admin_scrape_limiter._store.clear()
    yield


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


@pytest.fixture
def fake_paddle_domains():
    return {
        "data": [
            {
                "id": "cdm_test_1",
                "domain": "klima-radar.com",
                "approval_status": "approved",
                "created_at": "2024-01-15T10:30:00Z",
            },
            {
                "id": "cdm_test_2",
                "domain": "checkout.klima-radar.com",
                "approval_status": "pending",
                "created_at": "2024-01-16T08:00:00Z",
            },
        ]
    }


@pytest.mark.asyncio
async def test_paddle_checkout_domains_returns_domains(
    client, monkeypatch, fake_paddle_domains
):
    """Mock Paddle /checkout-domains and verify the admin endpoint returns them."""
    original_get = httpx.AsyncClient.get

    async def mock_get(self, url, *args, **kwargs):
        if isinstance(url, str) and "paddle.com/checkout-domains" in url:
            class MockResponse:
                status_code = 200
                text = ""

                def json(self):
                    return fake_paddle_domains

                def raise_for_status(self):
                    pass

            return MockResponse()
        return await original_get(self, url, *args, **kwargs)

    monkeypatch.setattr("httpx.AsyncClient.get", mock_get)

    response = await client.get(
        "/api/admin/paddle/checkout-domains",
        headers={"X-Admin-API-Key": "test-admin-key"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["environment"] == "sandbox"
    assert len(data["domains"]) == 2
    assert data["domains"][0]["id"] == "cdm_test_1"
    assert data["domains"][0]["domain"] == "klima-radar.com"
    assert data["domains"][0]["approval_status"] == "approved"
    assert data["domains"][0]["created_at"] == "2024-01-15T10:30:00Z"
    assert data["domains"][1]["approval_status"] == "pending"


@pytest.mark.asyncio
async def test_paddle_checkout_domains_invalid_key_returns_403(client):
    response = await client.get(
        "/api/admin/paddle/checkout-domains",
        headers={"X-Admin-API-Key": "wrong-key"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_paddle_checkout_domains_missing_config_returns_503(client):
    settings.admin_api_key = ""
    response = await client.get("/api/admin/paddle/checkout-domains")
    assert response.status_code == 503
