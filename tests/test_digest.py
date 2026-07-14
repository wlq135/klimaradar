"""Tests for daily digest alert behaviour."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import (
    AlertDigest,
    AlertLog,
    AlertSubscription,
    Base,
    Listing,
    Product,
    Retailer,
)
from app.services.alerter import (
    ConsoleEmailBackend,
    notify_subscribers_for_listing,
    send_daily_digests,
)


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
def sent_emails(monkeypatch):
    """Capture emails sent by the console backend used in tests."""
    emails = []

    async def fake_send(self, to_email: str, subject: str, body: str) -> bool:
        emails.append({"to": to_email, "subject": subject, "body": body})
        return True

    monkeypatch.setattr(ConsoleEmailBackend, "send", fake_send)
    return emails


async def _seed_listing(session: AsyncSession):
    """Create a product, retailer and listing tied to Germany/Berlin."""
    retailer = Retailer(name="TestShop", country="DE", domain="testshop.de")
    product = Product(
        name="Test AC",
        product_type="portable",
        btu_min=9000,
        btu_max=12000,
    )
    listing = Listing(
        product=product,
        retailer=retailer,
        url="https://testshop.de/ac",
        price=299.99,
        currency="EUR",
        stock_status="in_stock",
        country="DE",
        city_tag="berlin",
    )
    session.add_all([retailer, product, listing])
    await session.commit()
    return listing


@pytest.mark.asyncio
async def test_immediate_subscriber_receives_email(db_session, sent_emails):
    listing = await _seed_listing(db_session)
    subscription = AlertSubscription(
        email="test@example.com",
        country="DE",
        city="berlin",
        frequency="immediate",
        verified=True,
        active=True,
    )
    db_session.add(subscription)
    await db_session.commit()

    count = await notify_subscribers_for_listing(db_session, listing, "back in stock")

    assert count == 1
    assert len(sent_emails) == 1
    assert "back in stock" in sent_emails[0]["subject"].lower()
    logs = (await db_session.scalars(select(AlertLog))).all()
    assert len(logs) == 1


@pytest.mark.asyncio
async def test_daily_subscriber_gets_queued_not_emailed(db_session, sent_emails):
    listing = await _seed_listing(db_session)
    subscription = AlertSubscription(
        email="test@example.com",
        country="DE",
        city="berlin",
        frequency="daily",
        verified=True,
        active=True,
    )
    db_session.add(subscription)
    await db_session.commit()

    count = await notify_subscribers_for_listing(db_session, listing, "back in stock")

    assert count == 1
    assert len(sent_emails) == 0
    queued = (await db_session.scalars(select(AlertDigest))).all()
    assert len(queued) == 1
    assert queued[0].sent_at is None


@pytest.mark.asyncio
async def test_daily_digest_batches_multiple_matches(db_session, sent_emails):
    listing1 = await _seed_listing(db_session)
    listing2 = Listing(
        product=listing1.product,
        retailer=listing1.retailer,
        url="https://testshop.de/ac-2",
        price=349.99,
        currency="EUR",
        stock_status="in_stock",
        country="DE",
        city_tag="berlin",
    )
    db_session.add(listing2)
    subscription = AlertSubscription(
        email="test@example.com",
        country="DE",
        city="berlin",
        frequency="daily",
        verified=True,
        active=True,
    )
    db_session.add(subscription)
    await db_session.commit()

    await notify_subscribers_for_listing(db_session, listing1, "back in stock")
    await notify_subscribers_for_listing(db_session, listing2, "back in stock")
    assert len(sent_emails) == 0

    sent_count = await send_daily_digests(db_session)

    assert sent_count == 1
    assert len(sent_emails) == 1
    assert "daily digest" in sent_emails[0]["subject"].lower()
    assert "Test AC" in sent_emails[0]["body"]
    queued = (await db_session.scalars(select(AlertDigest))).all()
    assert all(entry.sent_at is not None for entry in queued)


@pytest.mark.asyncio
async def test_daily_digest_skips_inactive_and_unverified_subscribers(db_session, sent_emails):
    listing = await _seed_listing(db_session)

    inactive = AlertSubscription(
        email="inactive@example.com",
        country="DE",
        city="berlin",
        frequency="daily",
        verified=True,
        active=False,
    )
    unverified = AlertSubscription(
        email="unverified@example.com",
        country="DE",
        city="berlin",
        frequency="daily",
        verified=False,
        active=True,
    )
    db_session.add_all([inactive, unverified])
    await db_session.commit()

    await notify_subscribers_for_listing(db_session, listing, "back in stock")
    sent_count = await send_daily_digests(db_session)

    assert sent_count == 0
    assert len(sent_emails) == 0


@pytest.mark.asyncio
async def test_daily_digest_does_not_duplicate_same_listing_same_day(db_session, sent_emails):
    listing = await _seed_listing(db_session)
    subscription = AlertSubscription(
        email="test@example.com",
        country="DE",
        city="berlin",
        frequency="daily",
        verified=True,
        active=True,
    )
    db_session.add(subscription)
    await db_session.commit()

    await notify_subscribers_for_listing(db_session, listing, "back in stock")
    await notify_subscribers_for_listing(db_session, listing, "price drop")

    queued = (await db_session.scalars(select(AlertDigest))).all()
    assert len(queued) == 1

    sent_count = await send_daily_digests(db_session)
    assert sent_count == 1
    assert len(sent_emails) == 1
