"""Tests for the free/paid alert gating logic."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models import Base, PaidCustomer
from app.rate_limit import subscribe_limiter
from app.routers import alerts, billing, pages


@pytest.fixture(autouse=True)
def patch_paddle_checkout(monkeypatch):
    """Prevent the alert router from calling the real Paddle API."""

    async def fake_create_checkout(email: str) -> dict:
        return {
            "checkout_id": "checkout_test",
            "checkout_url": "https://test-checkout.lemonsqueezy.com",
        }

    monkeypatch.setattr("app.routers.alerts.create_checkout", fake_create_checkout)


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
    app.include_router(alerts.router)
    app.include_router(billing.router)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    subscribe_limiter._store.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


async def _verify_alert(session: AsyncSession, email: str) -> None:
    from app.models import AlertSubscription

    sub = await session.scalar(
        select(AlertSubscription).where(
            func.lower(AlertSubscription.email) == email.lower(),
            AlertSubscription.active.is_(True),
        )
    )
    if sub:
        sub.verified = True
        await session.commit()


async def _create_alert(client, email="test@example.com", city="Berlin", country="DE"):
    payload = {
        "email": email,
        "country": country,
        "city": city,
        "product_type": "portable",
        "in_stock_only": True,
    }
    return await client.post("/api/alerts/subscribe", json=payload)


@pytest.mark.asyncio
async def test_first_alert_is_free(client):
    response = await _create_alert(client)
    assert response.status_code == 200
    assert "check your email" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_second_alert_requires_upgrade(client):
    await _create_alert(client, city="Berlin")

    response = await _create_alert(client, city="Munich")
    assert response.status_code == 402
    detail = response.json()["detail"]
    assert "upgrade" in detail["message"].lower()
    assert detail["upgrade_url"] == "https://test-checkout.lemonsqueezy.com"
    assert detail["checkout_id"] == "checkout_test"


@pytest.mark.asyncio
async def test_duplicate_alert_returns_existing_message_not_upgrade(client, db_session):
    await _create_alert(client, city="Berlin")
    await _verify_alert(db_session, "test@example.com")

    response = await _create_alert(client, city="Berlin")
    assert response.status_code == 200
    assert "already have" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_paid_user_can_create_multiple_alerts(client, db_session):
    await _create_alert(client, city="Berlin")
    await _verify_alert(db_session, "test@example.com")

    db_session.add(PaidCustomer(email="test@example.com", is_paid=True))
    await db_session.commit()

    response = await _create_alert(client, city="Munich")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_revoked_paid_user_is_blocked_again(client, db_session):
    await _create_alert(client, city="Berlin")
    await _verify_alert(db_session, "test@example.com")

    db_session.add(PaidCustomer(email="test@example.com", is_paid=True))
    await db_session.commit()

    paid_customer = await db_session.get(PaidCustomer, 1)
    paid_customer.is_paid = False
    await db_session.commit()

    response = await _create_alert(client, city="Munich")
    assert response.status_code == 402


@pytest.mark.asyncio
async def test_different_emails_have_separate_limits(client):
    response_a = await _create_alert(client, email="a@example.com", city="Berlin")
    response_b = await _create_alert(client, email="b@example.com", city="Berlin")
    assert response_a.status_code == 200
    assert response_b.status_code == 200
