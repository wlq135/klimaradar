"""Tests for Lemon Squeezy billing integration and webhooks."""

import hashlib
import hmac
import json
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")
os.environ["LEMON_SQUEEZY_API_KEY"] = "test_api_key"
os.environ["LEMON_SQUEEZY_WEBHOOK_SECRET"] = "test_webhook_secret"
os.environ["LEMON_SQUEEZY_STORE_ID"] = "store_test"
os.environ["LEMON_SQUEEZY_VARIANT_ID"] = "variant_test"

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import get_db
from app.models import Base, LemonSqueezyPayment, PaidCustomer
from app.rate_limit import billing_limiter
from app.routers import billing, pages


@pytest.fixture(autouse=True)
def configure_lemon_squeezy_settings():
    """Ensure Lemon Squeezy settings are populated regardless of import order."""
    settings.lemon_squeezy_api_key = "test_api_key"
    settings.lemon_squeezy_webhook_secret = "test_webhook_secret"
    settings.lemon_squeezy_store_id = "store_test"
    settings.lemon_squeezy_variant_id = "variant_test"
    billing_limiter._store.clear()
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
    app.include_router(billing.router)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


def _sign_lemon_squeezy_payload(secret: str, payload: bytes) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()


def _order_created_event(email: str, event_id: str = "evt_1") -> dict:
    return {
        "meta": {
            "event_id": event_id,
            "event_name": "order_created",
        },
        "data": {
            "id": "order_1",
            "type": "orders",
            "attributes": {
                "status": "paid",
                "user_email": email,
                "checkout_id": "checkout_1",
                "checkout_data": {
                    "custom": {"email": email},
                },
                "total": "3.00",
                "currency": "EUR",
            },
        },
    }


def _order_refunded_event(email: str, event_id: str = "evt_2") -> dict:
    return {
        "meta": {
            "event_id": event_id,
            "event_name": "order_refunded",
        },
        "data": {
            "id": "order_1",
            "type": "orders",
            "attributes": {
                "status": "refunded",
                "user_email": email,
                "checkout_id": "checkout_1",
                "checkout_data": {
                    "custom": {"email": email},
                },
                "total": "3.00",
                "currency": "EUR",
            },
        },
    }


@pytest.mark.asyncio
async def test_create_lemon_squeezy_checkout(client, monkeypatch):
    async def fake_create_checkout(email: str) -> dict:
        return {
            "checkout_id": "checkout_test",
            "checkout_url": "https://test-checkout.lemonsqueezy.com",
        }

    monkeypatch.setattr(
        "app.routers.billing.create_lemon_squeezy_checkout", fake_create_checkout
    )

    response = await client.post(
        "/api/billing/lemon-squeezy/checkout",
        json={"email": "user@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["checkout_id"] == "checkout_test"
    assert data["checkout_url"] == "https://test-checkout.lemonsqueezy.com"


@pytest.mark.asyncio
async def test_lemon_squeezy_webhook_grants_access(client, db_session):
    event = _order_created_event("paid@example.com")
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_lemon_squeezy_payload(
        os.environ["LEMON_SQUEEZY_WEBHOOK_SECRET"], payload
    )

    response = await client.post(
        "/api/billing/webhooks/lemon-squeezy",
        content=payload,
        headers={"X-Signature": signature},
    )
    assert response.status_code == 200

    customer = await db_session.scalar(
        select(PaidCustomer).where(PaidCustomer.email == "paid@example.com")
    )
    assert customer is not None
    assert customer.is_paid is True

    payment = await db_session.scalar(
        select(LemonSqueezyPayment).where(LemonSqueezyPayment.event_id == "evt_1")
    )
    assert payment is not None
    assert payment.status == "paid"


@pytest.mark.asyncio
async def test_lemon_squeezy_webhook_duplicate_event_ignored(client, db_session):
    event = _order_created_event("dup@example.com", event_id="evt_dup")
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_lemon_squeezy_payload(
        os.environ["LEMON_SQUEEZY_WEBHOOK_SECRET"], payload
    )

    for _ in range(2):
        response = await client.post(
            "/api/billing/webhooks/lemon-squeezy",
            content=payload,
            headers={"X-Signature": signature},
        )
        assert response.status_code == 200

    count = await db_session.scalar(
        select(func.count(LemonSqueezyPayment.id)).where(
            LemonSqueezyPayment.event_id == "evt_dup"
        )
    )
    assert count == 1


@pytest.mark.asyncio
async def test_lemon_squeezy_webhook_invalid_signature_rejected(client):
    event = _order_created_event("hacker@example.com")
    payload = json.dumps(event).encode("utf-8")

    response = await client.post(
        "/api/billing/webhooks/lemon-squeezy",
        content=payload,
        headers={"X-Signature": "invalid"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_lemon_squeezy_webhook_refund_revokes_access(client, db_session):
    db_session.add(PaidCustomer(email="refund@example.com", is_paid=True))
    await db_session.commit()

    event = _order_refunded_event("refund@example.com")
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_lemon_squeezy_payload(
        os.environ["LEMON_SQUEEZY_WEBHOOK_SECRET"], payload
    )

    response = await client.post(
        "/api/billing/webhooks/lemon-squeezy",
        content=payload,
        headers={"X-Signature": signature},
    )
    assert response.status_code == 200

    customer = await db_session.scalar(
        select(PaidCustomer).where(PaidCustomer.email == "refund@example.com")
    )
    assert customer.is_paid is False
    assert customer.revoked_at is not None
