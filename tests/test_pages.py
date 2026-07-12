"""Tests for city landing page SEO behavior."""

import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models import Base
from app.routers import pages
from app.seo import (
    build_breadcrumb_jsonld,
    build_hreflang_alternates,
    get_city_info,
    get_seo_copy,
    get_sitemap_cities,
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


def test_get_city_info_known_city():
    info = get_city_info("DE", "muenchen")
    assert info is not None
    assert info["display_name"] == "München"
    assert info["country"] == "DE"


def test_get_city_info_unknown_city():
    assert get_city_info("DE", "notacity") is None


def test_get_seo_copy_german():
    info = get_city_info("DE", "berlin")
    copy = get_seo_copy("DE", info)
    assert "Berlin" in copy["title"]
    assert "Deutschland" in copy["description"]
    assert copy["h1"].startswith("Mobile Klimaanlage")


def test_get_seo_copy_french():
    info = get_city_info("FR", "paris")
    copy = get_seo_copy("FR", info)
    assert "Paris" in copy["title"]
    assert "France" in copy["description"]
    assert copy["h1"].startswith("Climatiseur mobile")


def test_build_breadcrumb_jsonld():
    info = get_city_info("DE", "berlin")
    copy = get_seo_copy("DE", info)
    data = build_breadcrumb_jsonld("https://klima-radar.com", "DE", info, copy)
    assert data["@type"] == "BreadcrumbList"
    items = data["itemListElement"]
    assert len(items) == 3
    assert items[-1]["name"] == copy["h1"]


def test_build_hreflang_alternates():
    alts = build_hreflang_alternates(
        "de-DE", "https://klima-radar.com/de/berlin/portable-ac-in-stock", "https://klima-radar.com"
    )
    assert ("de-DE", "https://klima-radar.com/de/berlin/portable-ac-in-stock") in alts
    assert ("x-default", "https://klima-radar.com/") in alts


def test_get_sitemap_cities_covers_both_countries():
    cities = get_sitemap_cities()
    assert ("de", "berlin") in cities
    assert ("fr", "paris") in cities
    assert len([c for c, _ in cities if c == "de"]) > 10
    assert len([c for c, _ in cities if c == "fr"]) > 10


@pytest.mark.asyncio
async def test_city_page_renders_localized_german(client):
    response = await client.get("/de/berlin/portable-ac-in-stock")
    assert response.status_code == 200
    text = response.text
    assert '<html lang="de-DE"' in text
    assert "Mobile Klimaanlage auf Lager in Berlin" in text
    assert 'hreflang="de-DE"' in text
    assert 'hreflang="x-default"' in text
    assert '"@type": "BreadcrumbList"' in text


@pytest.mark.asyncio
async def test_city_page_renders_localized_french(client):
    response = await client.get("/fr/paris/portable-ac-in-stock")
    assert response.status_code == 200
    text = response.text
    assert '<html lang="fr-FR"' in text
    assert "Climatiseur mobile en stock à Paris" in text


@pytest.mark.asyncio
async def test_unknown_city_returns_404(client):
    response = await client.get("/de/notacity/portable-ac-in-stock")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_sitemap_contains_city_urls(client):
    response = await client.get("/sitemap.xml")
    assert response.status_code == 200
    text = response.text
    assert "/de/berlin/portable-ac-in-stock" in text
    assert "/fr/paris/portable-ac-in-stock" in text
    assert text.count("portable-ac-in-stock") > 50


@pytest.mark.asyncio
async def test_homepage_has_structured_data(client):
    response = await client.get("/")
    assert response.status_code == 200
    text = response.text
    assert '"@type": "WebSite"' in text
    assert '"@type": "Organization"' in text
    assert '<html lang="en"' in text
