"""Tests for retailer seeding."""

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import Base, Retailer
from app.seed import seed_retailers


@pytest.mark.asyncio
async def test_seed_updates_existing_amazon_belgium_domain(monkeypatch):
    monkeypatch.setattr("app.seed.settings.enable_demo", False)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with session_factory() as session:
        session.add(
            Retailer(
                name="Amazon Belgium",
                country="BE",
                domain="https://www.amazon.be",
                affiliate_network="amazon_associates",
            )
        )
        await session.commit()
        await seed_retailers(session)
        retailer = await session.get(Retailer, 1)

    assert retailer.domain == "https://www.amazon.com.be"
    await engine.dispose()
