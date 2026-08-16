"""Tests for city landing page SEO behavior."""

import os
from datetime import datetime, timedelta, timezone

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models import Base, Listing, Product, Retailer
from app.routers import pages
from app.seo import (
    build_breadcrumb_jsonld,
    build_hreflang_alternates,
    get_city_info,
    get_seo_copy,
    get_sitemap_cities,
    guide_path,
    comparison_path,
    COMPARISON_COUNTRIES,
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


@pytest.mark.asyncio
async def test_search_hides_listings_not_seen_for_48_hours(client, db_session):
    now = datetime.now(timezone.utc)
    retailer = Retailer(name="Amazon Germany", country="DE", domain="amazon.de")
    product = Product(name="Midea 12,000 BTU Portable Air Conditioner", product_type="portable")
    db_session.add_all([retailer, product])
    await db_session.flush()
    fresh = Listing(
        product_id=product.id,
        retailer_id=retailer.id,
        sku="FRESH",
        url="https://amazon.de/fresh",
        country="DE",
        stock_status="in_stock",
        last_seen_at=now,
    )
    stale = Listing(
        product_id=product.id,
        retailer_id=retailer.id,
        sku="STALE",
        url="https://amazon.de/stale",
        country="DE",
        stock_status="in_stock",
        last_seen_at=now - timedelta(hours=49),
    )
    db_session.add_all([fresh, stale])
    await db_session.commit()

    response = await client.get("/search?country=DE")

    assert response.status_code == 200
    assert "FRESH" not in response.text
    assert "12,000 BTU Portable Air Conditioner" in response.text
    assert response.text.count('href="/go/') == 1


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
    assert len([c for c, _ in cities if c == "de"]) == 8
    assert len([c for c, _ in cities if c == "fr"]) == 7
    assert ("be", "kortrijk") not in cities


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "expected_title", "expected_h1"),
    [
        ("/search?country=IT", "Portable Air Conditioners in Italy: Prices and Stock | KlimaRadar", "Portable air conditioners in Italy: live prices and stock"),
        ("/search?country=ES", "Portable Air Conditioners in Spain: Prices and Stock | KlimaRadar", "Portable air conditioners in Spain: live prices and stock"),
        ("/search?country=BE", "Portable Air Conditioners in Belgium: Prices and Stock | KlimaRadar", "Portable air conditioners in Belgium: live prices and stock"),
        ("/search?country=GB", "Portable AC in stock in United Kingdom — KlimaRadar", "Portable AC in stock in United Kingdom"),
    ],
)
async def test_high_intent_country_search_pages_match_search_demand(client, path, expected_title, expected_h1):
    response = await client.get(path)
    assert response.status_code == 200
    assert f"<title>{expected_title}</title>" in response.text
    assert f"<h1 class=\"text-2xl md:text-3xl font-bold mb-2\">{expected_h1}</h1>" in response.text


@pytest.mark.asyncio
async def test_city_page_renders_localized_german(client):
    response = await client.get("/de/berlin/portable-ac-in-stock")
    assert response.status_code == 200
    text = response.text
    assert '<html lang="de-DE"' in text
    assert "Mobile Klimaanlage auf Lager in Berlin" in text
    assert 'href="/guides/de/portable-air-conditioner"' in text
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
async def test_secondary_city_redirects_to_country_page(client):
    response = await client.get("/de/dortmund/portable-ac-in-stock")

    assert response.status_code == 301
    assert response.headers["location"] == "/search?country=DE"


@pytest.mark.asyncio
async def test_sitemap_contains_city_urls(client):
    response = await client.get("/sitemap.xml")
    assert response.status_code == 200
    text = response.text
    assert "/de/berlin/portable-ac-in-stock" in text
    assert "/fr/paris/portable-ac-in-stock" in text
    assert text.count("portable-ac-in-stock") == 44
    assert "/be/kortrijk/portable-ac-in-stock" not in text


@pytest.mark.asyncio
async def test_indexnow_key_file(client):
    from app.config import settings

    response = await client.get(f"/indexnow-{settings.indexnow_key}.txt")

    assert response.status_code == 200
    assert response.text == settings.indexnow_key
    invalid = await client.get("/indexnow-invalid-key.txt")
    assert invalid.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("country", "html_lang", "country_name"),
    [
        ("DE", "de-DE", "Deutschland"),
        ("FR", "fr-FR", "France"),
        ("IT", "it-IT", "Italia"),
        ("ES", "es-ES", "España"),
        ("NL", "nl-NL", "Nederland"),
        ("BE", "nl-BE", "België"),
        ("GB", "en-GB", "United Kingdom"),
    ],
)
async def test_country_buying_guides_render(client, country, html_lang, country_name):
    response = await client.get(guide_path(country))

    assert response.status_code == 200
    text = response.text
    assert f'<html lang="{html_lang}"' in text
    assert country_name in text
    assert f'href="/search?country={country}"' in text
    assert '"@type": "Article"' in text
    assert '"@type": "FAQPage"' in text
    assert "12,000 BTU" in text or "12.000 BTU" in text or "12 000 BTU" in text


@pytest.mark.asyncio
async def test_btu_comparison_page_renders_live_listing_and_seo(client, db_session):
    now = datetime.now(timezone.utc)
    retailer = Retailer(name="Amazon Germany", country="DE", domain="amazon.de")
    product = Product(
        name="Midea 12000 BTU Portable Air Conditioner",
        product_type="portable",
        btu_min=12000,
        btu_max=12000,
    )
    db_session.add_all([retailer, product])
    await db_session.flush()
    db_session.add(
        Listing(
            product_id=product.id,
            retailer_id=retailer.id,
            sku="BTU12",
            url="https://amazon.de/btu12",
            country="DE",
            stock_status="in_stock",
            last_seen_at=now,
        )
    )
    await db_session.commit()

    response = await client.get(comparison_path("DE"))

    assert response.status_code == 200
    text = response.text
    assert '<html lang="de-DE"' in text
    assert "Mobile Klimaanlagen mit 12.000 BTU auf Lager in Deutschland" in text
    from app.config import settings
    expected_canonical = f'{settings.base_url.rstrip("/")}{comparison_path("DE")}'
    assert f'rel="canonical" href="{expected_canonical}"' in text
    assert 'value="12000"' in text
    assert "Midea 12000 BTU Portable Air Conditioner" in text
    assert 'href="/go/' in text
    assert "Für welche Räume 12.000 BTU ausreichen" in text
    assert "Häufige Fragen zu 12.000-BTU-Klimageräten" in text
    assert '"@type": "Article"' in text
    assert '"@type": "BreadcrumbList"' in text
    assert '"@type": "FAQPage"' in text


@pytest.mark.asyncio
async def test_unknown_btu_comparison_returns_404(client):
    response = await client.get("/compare/us/12000-btu-portable-air-conditioner")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_guide_and_sitemap_link_btu_comparisons(client):
    search = await client.get("/search?country=IT")
    guide = await client.get(guide_path("FR"))
    sitemap = await client.get("/sitemap.xml")

    assert search.status_code == 200
    assert guide.status_code == 200
    assert sitemap.status_code == 200
    assert 'href="/compare/it/12000-btu-portable-air-conditioner"' in search.text
    assert 'href="/compare/fr/12000-btu-portable-air-conditioner"' in guide.text
    assert search.text.index('href="/compare/it/12000-btu-portable-air-conditioner"') < search.text.index('href="/guides/it/portable-air-conditioner"')
    for country in COMPARISON_COUNTRIES:
        assert comparison_path(country) in sitemap.text


@pytest.mark.asyncio
async def test_country_search_links_to_guide_and_renders_faq(client):
    response = await client.get("/search?country=IT")

    assert response.status_code == 200
    text = response.text
    assert 'href="/guides/it/portable-air-conditioner"' in text
    assert "Guida: climatizzatori portatili in Italia" in text
    assert "Domande frequenti sui climatizzatori portatili" in text
    assert '"@type": "FAQPage"' in text


@pytest.mark.asyncio
async def test_homepage_and_sitemap_expose_all_guides(client):
    home = await client.get("/")
    sitemap = await client.get("/sitemap.xml")

    assert home.status_code == 200
    assert sitemap.status_code == 200
    for country in ("DE", "FR", "IT", "ES", "NL", "BE", "GB"):
        path = guide_path(country)
        assert f'href="{path}"' in home.text
        assert f"<loc>" in sitemap.text and path in sitemap.text


def test_uk_prices_use_pound_symbol():
    from app.templating import format_price

    assert format_price(445.99, "GBP") == "£445.99"


@pytest.mark.asyncio
async def test_homepage_has_structured_data(client):
    response = await client.get("/")
    assert response.status_code == 200
    text = response.text
    assert '"@type": "WebSite"' in text
    assert '"@type": "Organization"' in text
    assert '<html lang="en"' in text
    assert "Mobile Klimaanlage in Berlin" in text
    assert "Climatiseur mobile à Paris" in text
    assert "Portable AC in London" in text
    assert "United Kingdom" in text
    assert "Portable AC in Birmingham" in text
    assert "Portable AC in Sheffield" not in text


def test_freshness_labels_recent_and_stale():
    """The _freshness helper classifies listings by age for the UI."""
    from datetime import datetime, timedelta, timezone
    from app.routers.pages import _freshness

    now = datetime.now(timezone.utc)
    label_none, stale_none = _freshness(None)
    assert stale_none is True

    label_now, stale_now = _freshness(now)
    assert "just now" in label_now and stale_now is False

    label_5h, stale_5h = _freshness(now - timedelta(hours=5))
    assert "5h" in label_5h and stale_5h is False

    label_1d, stale_1d = _freshness(now - timedelta(days=1))
    assert "1d" in label_1d and stale_1d is False

    label_5d, stale_5d = _freshness(now - timedelta(days=5))
    assert "Checked" in label_5d and stale_5d is True

    # Naive datetimes are treated as UTC without crashing.
    label_naive, _ = _freshness(datetime.now(timezone.utc).replace(tzinfo=None))
    assert isinstance(label_naive, str)
