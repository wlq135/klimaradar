"""Tests for Creem billing integration and webhooks."""

import hashlib
import hmac
import json
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")
os.environ["CREEM_API_KEY"] = "test_api_key"
os.environ["CREEM_WEBHOOK_SECRET"] = "test_webhook_secret"
os.environ["CREEM_PRODUCT_ID"] = "prod_test"

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import get_db
from app.models import Base, CreemPayment, PaidCustomer
from app.rate_limit import billing_limiter
from app.routers import billing, pages


@pytest.fixture(autouse=True)
def configure_creem_settings():
    """Ensure Creem settings are populated regardless of import order."""
    settings.creem_api_key = "test_api_key"
    settings.creem_webhook_secret = "test_webhook_secret"
    settings.creem_product_id = "prod_test"
    settings.creem_api_base = "https://test-api.creem.io/v1"
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


def _sign_creem_payload(secret: str, payload: bytes) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()


def _checkout_completed_event(email: str, event_id: str = "evt_1") -> dict:
    return {
        "id": event_id,
        "eventType": "checkout.completed",
        "created_at": 1700000000000,
        "object": {
            "id": "ord_1",
            "status": "paid",
            "amount": 300,
            "currency": "EUR",
            "checkout": {"id": "ch_1"},
            "customer": {"id": "cust_1", "email": email},
            "product": {"id": "prod_test"},
            "metadata": {"email": email},
        },
    }


def _refund_created_event(email: str, event_id: str = "evt_2") -> dict:
    return {
        "id": event_id,
        "eventType": "refund.created",
        "created_at": 1700000000001,
        "object": {
            "id": "ref_1",
            "status": "succeeded",
            "refund_amount": 300,
            "refund_currency": "EUR",
            "order": {"id": "ord_1", "status": "refunded"},
            "customer": {"id": "cust_1", "email": email},
            "metadata": {"email": email},
        },
    }


@pytest.mark.asyncio
async def test_create_creem_checkout(client, monkeypatch):
    async def fake_create_checkout(email: str) -> dict:
        return {
            "checkout_id": "ch_test",
            "checkout_url": "https://checkout.creem.io/ch_test",
        }

    monkeypatch.setattr(
        "app.routers.billing.create_creem_checkout", fake_create_checkout
    )

    response = await client.post(
        "/api/billing/creem/checkout",
        json={"email": "user@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["checkout_id"] == "ch_test"
    assert data["checkout_url"] == "https://checkout.creem.io/ch_test"


@pytest.mark.asyncio
async def test_creem_webhook_grants_access(client, db_session):
    event = _checkout_completed_event("paid@example.com")
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_creem_payload(
        os.environ["CREEM_WEBHOOK_SECRET"], payload
    )

    response = await client.post(
        "/api/billing/webhooks/creem",
        content=payload,
        headers={"creem-signature": signature},
    )
    assert response.status_code == 200

    customer = await db_session.scalar(
        select(PaidCustomer).where(PaidCustomer.email == "paid@example.com")
    )
    assert customer is not None
    assert customer.is_paid is True

    payment = await db_session.scalar(
        select(CreemPayment).where(CreemPayment.event_id == "evt_1")
    )
    assert payment is not None
    assert payment.status == "paid"


@pytest.mark.asyncio
async def test_creem_webhook_duplicate_event_ignored(client, db_session):
    event = _checkout_completed_event("dup@example.com", event_id="evt_dup")
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_creem_payload(
        os.environ["CREEM_WEBHOOK_SECRET"], payload
    )

    for _ in range(2):
        response = await client.post(
            "/api/billing/webhooks/creem",
            content=payload,
            headers={"creem-signature": signature},
        )
        assert response.status_code == 200

    count = await db_session.scalar(
        select(func.count(CreemPayment.id)).where(
            CreemPayment.event_id == "evt_dup"
        )
    )
    assert count == 1


@pytest.mark.asyncio
async def test_creem_webhook_invalid_signature_rejected(client):
    event = _checkout_completed_event("hacker@example.com")
    payload = json.dumps(event).encode("utf-8")

    response = await client.post(
        "/api/billing/webhooks/creem",
        content=payload,
        headers={"creem-signature": "invalid"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_creem_webhook_refund_revokes_access(client, db_session):
    db_session.add(PaidCustomer(email="refund@example.com", is_paid=True))
    await db_session.commit()

    event = _refund_created_event("refund@example.com")
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_creem_payload(
        os.environ["CREEM_WEBHOOK_SECRET"], payload
    )

    response = await client.post(
        "/api/billing/webhooks/creem",
        content=payload,
        headers={"creem-signature": signature},
    )
    assert response.status_code == 200

    customer = await db_session.scalar(
        select(PaidCustomer).where(PaidCustomer.email == "refund@example.com")
    )
    assert customer.is_paid is False
    assert customer.revoked_at is not None
