"""Tests for Paddle billing integration and webhooks."""

import hashlib
import hmac
import json
import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")
os.environ["PADDLE_API_KEY"] = "test_api_key"
os.environ["PADDLE_WEBHOOK_SECRET"] = "test_webhook_secret"
os.environ["PADDLE_PRICE_ID"] = "pri_test"

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import func, select
from app.config import settings
from app.database import get_db
from app.models import Base, PaidCustomer, PaddleCustomer, PaddlePayment
from app.rate_limit import billing_limiter
from app.routers import billing, pages


@pytest.fixture(autouse=True)
def configure_paddle_settings():
    """Ensure Paddle settings are populated regardless of import order."""
    settings.paddle_api_key = "test_api_key"
    settings.paddle_webhook_secret = "test_webhook_secret"
    settings.paddle_price_id = "pri_test"
    settings.paddle_environment = "sandbox"
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


def _sign_paddle_payload(secret: str, payload: bytes, timestamp: str = "1234567890") -> str:
    signed = f"{timestamp}:{payload.decode('utf-8')}"
    signature = hmac.new(
        secret.encode("utf-8"),
        signed.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"ts={timestamp},h1={signature}"


def _paid_event(email: str, event_id: str = "evt_1") -> dict:
    return {
        "event_id": event_id,
        "event_type": "transaction.paid",
        "data": {
            "id": "txn_1",
            "customer_id": "ctm_1",
            "status": "paid",
            "custom_data": {"email": email},
            "details": {
                "totals": {
                    "total": "3.00",
                    "currency_code": "EUR",
                }
            },
        },
    }


def _refund_event(email: str, event_id: str = "evt_2") -> dict:
    return {
        "event_id": event_id,
        "event_type": "transaction.updated",
        "data": {
            "id": "txn_1",
            "customer_id": "ctm_1",
            "status": "refunded",
            "custom_data": {"email": email},
        },
    }


@pytest.mark.asyncio
async def test_create_checkout(client, monkeypatch):
    async def fake_create_checkout(email: str) -> dict:
        return {
            "transaction_id": "txn_test",
            "checkout_url": "https://test-checkout.paddle.com",
        }

    monkeypatch.setattr(
        "app.routers.billing.create_checkout", fake_create_checkout
    )

    response = await client.post(
        "/api/billing/checkout",
        json={"email": "user@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == "txn_test"
    assert data["checkout_url"] == "https://test-checkout.paddle.com"
    assert data["checkout_url"] == "https://test-checkout.paddle.com"


@pytest.mark.asyncio
async def test_paddle_webhook_grants_access(client, db_session):
    event = _paid_event("paid@example.com")
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_paddle_payload(
        os.environ["PADDLE_WEBHOOK_SECRET"], payload
    )

    response = await client.post(
        "/api/billing/webhooks/paddle",
        content=payload,
        headers={"Paddle-Signature": signature},
    )
    assert response.status_code == 200

    customer = await db_session.scalar(
        select(PaidCustomer).where(PaidCustomer.email == "paid@example.com")
    )
    assert customer is not None
    assert customer.is_paid is True

    paddle_customer = await db_session.scalar(
        select(PaddleCustomer).where(PaddleCustomer.email == "paid@example.com")
    )
    assert paddle_customer is not None
    assert paddle_customer.paddle_customer_id == "ctm_1"


@pytest.mark.asyncio
async def test_paddle_webhook_duplicate_event_ignored(client, db_session):
    event = _paid_event("dup@example.com", event_id="evt_dup")
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_paddle_payload(
        os.environ["PADDLE_WEBHOOK_SECRET"], payload
    )

    for _ in range(2):
        response = await client.post(
            "/api/billing/webhooks/paddle",
            content=payload,
            headers={"Paddle-Signature": signature},
        )
        assert response.status_code == 200

    count = await db_session.scalar(
        select(func.count(PaddlePayment.id)).where(PaddlePayment.event_id == "evt_dup")
    )
    assert count == 1


@pytest.mark.asyncio
async def test_paddle_webhook_invalid_signature_rejected(client):
    event = _paid_event("hacker@example.com")
    payload = json.dumps(event).encode("utf-8")

    response = await client.post(
        "/api/billing/webhooks/paddle",
        content=payload,
        headers={"Paddle-Signature": "ts=1,h1=invalid"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_paddle_webhook_refund_revokes_access(client, db_session):
    db_session.add(PaidCustomer(email="refund@example.com", is_paid=True))
    await db_session.commit()

    event = _refund_event("refund@example.com")
    payload = json.dumps(event).encode("utf-8")
    signature = _sign_paddle_payload(
        os.environ["PADDLE_WEBHOOK_SECRET"], payload
    )

    response = await client.post(
        "/api/billing/webhooks/paddle",
        content=payload,
        headers={"Paddle-Signature": signature},
    )
    assert response.status_code == 200

    customer = await db_session.scalar(
        select(PaidCustomer).where(PaidCustomer.email == "refund@example.com")
    )
    assert customer.is_paid is False
    assert customer.revoked_at is not None


# Need func import for duplicate-event test; imported here to avoid shadowing earlier imports.
from sqlalchemy import func, select
