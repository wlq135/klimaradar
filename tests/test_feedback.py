"""Tests for the feedback form and API."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models import Base, Feedback
from app.routers import feedback


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
    app.include_router(feedback.router)

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_submit_feedback_creates_record(client, db_session):
    response = await client.post(
        "/api/feedback",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "message": "Great site, but I found a bug.",
            "page_url": "https://klima-radar.com/search?country=DE",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "Thank you" in data["message"]

    count = await db_session.scalar(select(Feedback.id))  # type: ignore[arg-type]
    assert count is not None


@pytest.mark.asyncio
async def test_submit_feedback_requires_message(client):
    response = await client.post(
        "/api/feedback",
        json={"email": "test@example.com", "message": "   "},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_feedback_page_renders(client):
    response = await client.get("/feedback")
    assert response.status_code == 200
    assert "Send feedback" in response.text
