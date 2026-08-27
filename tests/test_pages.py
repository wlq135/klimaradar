"""Tests for city landing page SEO behavior."""

import os
from datetime import datetime, timedelta, timezone

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("BASE_URL", "http://testserver")

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models import AlertSubscription, Base, ClickEvent, Listing, Product, Retailer
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
    assert "s-maxage=60" in response.headers["cache-control"]
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


@pytest.mark.asyncio
async def test_health_reports_24h_affiliate_click_totals(client, db_session):
    now = datetime.now(timezone.utc)
    retailer = Retailer(name="Amazon Germany", country="DE", domain="amazon.de")
    product = Product(name="Health Check AC", product_type="portable")
    db_session.add_all([retailer, product])
    await db_session.flush()
    listing = Listing(
        product_id=product.id,
        retailer_id=retailer.id,
        sku="HEALTH",
        url="https://amazon.de/health",
        country="DE",
        stock_status="in_stock",
        last_seen_at=now,
    )
    db_session.add(listing)
    await db_session.flush()
    db_session.add_all(
        [
            ClickEvent(
                listing_id=listing.id,
                source="country_top3",
                placement="top3",
                position=1,
                clicked_at=now - timedelta(hours=2),
                user_agent="Mozilla/5.0 Chrome/126.0",
            ),
            ClickEvent(
                listing_id=listing.id,
                source="compare_top3",
                placement="top3",
                position=2,
                clicked_at=now - timedelta(hours=3),
                user_agent="Mozilla/5.0 Safari/605",
            ),
            ClickEvent(
                listing_id=listing.id,
                source="country_top3",
                placement="top3",
                position=3,
                clicked_at=now - timedelta(hours=4),
                user_agent="ExampleBot/1.0",
            ),
            ClickEvent(
                listing_id=listing.id,
                source="country_listing",
                placement="listing",
                clicked_at=now - timedelta(hours=30),
                user_agent="Mozilla/5.0 Chrome/126.0",
            ),
        ]
    )
    db_session.add(
        AlertSubscription(
            email="active@example.com",
            country="DE",
            verified=True,
            active=True,
            source="city_inline",
        )
    )
    db_session.add(
        AlertSubscription(
            email="pending@example.com",
            country="DE",
            verified=False,
            active=True,
            source="listing_card_modal",
            created_at=now - timedelta(hours=2),
        )
    )
    db_session.add(
        AlertSubscription(
            email="old-pending@example.com",
            country="DE",
            verified=False,
            active=True,
            source="city_inline",
            created_at=now - timedelta(days=8),
        )
    )
    await db_session.commit()

    response = await client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["affiliate_clicks_24h"] == 3
    assert payload["affiliate_clicks_24h_by_source"] == {
        "country_top3": 2,
        "compare_top3": 1,
    }
    assert payload["affiliate_clicks_24h_likely_human"] == 2
    assert payload["affiliate_clicks_24h_likely_human_by_source"] == {
        "country_top3": 1,
        "compare_top3": 1,
    }
    assert payload["affiliate_clicks_24h_by_placement"] == {"top3": 3}
    assert payload["affiliate_clicks_24h_likely_human_by_placement"] == {"top3": 2}
    assert payload["affiliate_clicks_24h_likely_automated"] == 1
    assert payload["active_subscriptions_by_source"] == {"city_inline": 1}
    assert payload["pending_subscriptions_7d_by_source"] == {
        "listing_card_modal": 1
    }
    assert payload["pending_subscriptions_7d"] == 1
    assert payload["subscription_confirmation_rate"] == 0.5


@pytest.mark.asyncio
async def test_country_page_promotes_cheapest_fresh_in_stock_deals(
    client, db_session, monkeypatch
):
    now = datetime.now(timezone.utc)
    amazon = Retailer(name="Amazon Germany", country="DE", domain="amazon.de")
    local_shop = Retailer(name="LocalShop", country="DE", domain="localshop.de")
    cheap = Product(name="Cheap Fresh AC", product_type="portable", btu_min=9000, btu_max=9000)
    mid = Product(name="Mid Fresh AC", product_type="portable", btu_min=12000, btu_max=12000)
    unavailable = Product(name="Unavailable AC", product_type="portable")
    stale = Product(name="Stale AC", product_type="portable")
    db_session.add_all([amazon, local_shop, cheap, mid, unavailable, stale])
    await db_session.flush()

    cheap_listing = Listing(
        product_id=cheap.id,
        retailer_id=amazon.id,
        sku="CHEAP",
        url="https://amazon.de/cheap",
        price=299,
        currency="EUR",
        country="DE",
        stock_status="in_stock",
        last_seen_at=now,
    )
    mid_listing = Listing(
        product_id=mid.id,
        retailer_id=local_shop.id,
        sku="MID",
        url="https://localshop.de/mid",
        price=349,
        currency="EUR",
        country="DE",
        stock_status="in_stock",
        last_seen_at=now,
    )
    db_session.add_all(
        [
            cheap_listing,
            mid_listing,
            Listing(
                product_id=unavailable.id,
                retailer_id=amazon.id,
                sku="OUT",
                url="https://amazon.de/out",
                price=199,
                currency="EUR",
                country="DE",
                stock_status="out_of_stock",
                last_seen_at=now,
            ),
            Listing(
                product_id=stale.id,
                retailer_id=amazon.id,
                sku="OLD",
                url="https://amazon.de/old",
                price=149,
                currency="EUR",
                country="DE",
                stock_status="in_stock",
                last_seen_at=now - timedelta(hours=49),
            ),
        ]
    )
    await db_session.commit()

    response = await client.get("/search?country=DE")

    assert response.status_code == 200
    text = response.text
    assert "Top-Angebote jetzt auf Lager" in text
    assert "Stale AC" not in text
    assert text.index("Cheap Fresh AC") < text.index("Mid Fresh AC")
    assert text.count("source=country_top3") == 2
    assert 'name="source" value="country_inline"' in text
    assert f'href="/go/{cheap_listing.id}?source=country_top3&amp;placement=top3&amp;position=1"' in text
    assert f'href="/go/{mid_listing.id}?source=country_top3&amp;placement=top3&amp;position=2"' in text
    assert f'href="/go/{cheap_listing.id}?source=country_listing&amp;placement=listing&amp;position=1"' in text

    redirect = await client.get(
        f"/go/{cheap_listing.id}?source=country_top3&placement=top3&position=1",
        headers={
            "User-Agent": "pytest",
            "Referer": "http://testserver/search?country=DE",
        },
    )
    assert redirect.status_code == 307
    events = (await db_session.execute(select(ClickEvent))).scalars().all()
    assert len(events) == 1
    assert events[0].listing_id == cheap_listing.id
    assert events[0].source == "country_top3"
    assert events[0].placement == "top3"
    assert events[0].position == 1
    assert events[0].page_ref == "/search?country=DE"

    monkeypatch.setattr(pages.settings, "admin_api_key", "test-admin-key")
    pages.admin_scrape_limiter._store.clear()
    analytics = await client.get(
        "/api/admin/click-analytics?days=7",
        headers={"X-Admin-API-Key": "test-admin-key"},
    )
    assert analytics.status_code == 200
    payload = analytics.json()
    assert payload["total_clicks"] == 1
    assert payload["by_country"] == {"DE": 1}
    assert payload["by_source"] == {"country_top3": 1}
    assert payload["by_placement"] == {"top3": 1}
    assert payload["by_stock_status"] == {"in_stock": 1}
    assert payload["by_page"] == {"/search?country=DE": 1}
    assert payload["rows"][0]["product"] == "Cheap Fresh AC"
    assert payload["rows"][0]["btu_min"] == 9000
    assert payload["rows"][0]["btu_max"] == 9000
    assert payload["rows"][0]["stock_status"] == "in_stock"
    assert payload["rows"][0]["retailer"] == "Amazon Germany"

    exact = await client.get(
        f"/api/admin/click-analytics?days=7&click_id={events[0].id}",
        headers={"X-Admin-API-Key": "test-admin-key"},
    )
    assert exact.status_code == 200
    exact_payload = exact.json()
    assert exact_payload["total_clicks"] == 1
    assert exact_payload["rows"][0]["click_id"] == events[0].id
    assert exact_payload["rows"][0]["source"] == "country_top3"


@pytest.mark.asyncio
async def test_comparison_page_promotes_12000_btu_deals(client, db_session):
    now = datetime.now(timezone.utc)
    retailer = Retailer(name="Amazon Germany", country="DE", domain="amazon.de")
    suitable = Product(
        name="Suitable 12000 AC",
        product_type="portable",
        btu_min=12000,
        btu_max=12000,
    )
    too_small = Product(
        name="Too Small AC",
        product_type="portable",
        btu_min=8000,
        btu_max=8000,
    )
    db_session.add_all([retailer, suitable, too_small])
    await db_session.flush()

    suitable_listing = Listing(
        product_id=suitable.id,
        retailer_id=retailer.id,
        sku="SUIT",
        url="https://amazon.de/suitable",
        price=399,
        currency="EUR",
        country="DE",
        stock_status="in_stock",
        last_seen_at=now,
    )
    db_session.add_all(
        [
            suitable_listing,
            Listing(
                product_id=too_small.id,
                retailer_id=retailer.id,
                sku="SMALL",
                url="https://amazon.de/small",
                price=249,
                currency="EUR",
                country="DE",
                stock_status="in_stock",
                last_seen_at=now,
            ),
        ]
    )
    await db_session.commit()

    response = await client.get(comparison_path("DE"))

    assert response.status_code == 200
    assert "Suitable 12000 AC" in response.text
    assert "Too Small AC" not in response.text
    assert f'href="/go/{suitable_listing.id}?source=compare_top3&amp;placement=top3&amp;position=1"' in response.text
    assert 'name="source" value="compare_inline"' in response.text

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
async def test_filtered_search_is_not_publicly_cached(client):
    response = await client.get("/search?country=DE&min_btu=12000")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.asyncio
async def test_city_page_with_listing_offers_inline_alert_capture(client, db_session):
    now = datetime.now(timezone.utc)
    retailer = Retailer(name="Amazon Germany", country="DE", domain="amazon.de")
    product = Product(name="Berlin Inline AC", product_type="portable")
    db_session.add_all([retailer, product])
    await db_session.flush()
    db_session.add(
        Listing(
            product_id=product.id,
            retailer_id=retailer.id,
            sku="BERLIN-INLINE",
            url="https://amazon.de/berlin-inline",
            country="DE",
            stock_status="in_stock",
            last_seen_at=now,
        )
    )
    await db_session.commit()

    response = await client.get("/de/berlin/portable-ac-in-stock")

    assert response.status_code == 200
    assert 'name="source" value="city_inline"' in response.text
    assert "Email me in-stock ACs" in response.text
    assert 'name="frequency" value="daily"' in response.text
    assert '"url": "https://amazon.de/berlin-inline"' in response.text
    assert "Track this model" in response.text
    assert f"openAlertModal({product.id})" in response.text


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
async def test_homepage_promotes_all_btu_comparisons(client):
    response = await client.get("/")

    assert response.status_code == 200
    text = response.text
    assert "Compare 12,000 BTU portable air conditioners" in text
    assert text.index("Compare 12,000 BTU portable air conditioners") < text.index("Popular searches")
    assert text.count('aria-labelledby="btu-comparison-heading"') == 1
    for country in COMPARISON_COUNTRIES:
        assert f'href="{comparison_path(country)}"' in text




@pytest.mark.asyncio
async def test_homepage_puts_email_capture_in_hero(client):
    response = await client.get("/")

    assert response.status_code == 200
    text = response.text
    assert 'id="homepage-alert-form"' in text
    assert "Email me in-stock ACs" in text
    assert text.index('id="homepage-alert-form"') < text.index("Compare 12,000 BTU")


@pytest.mark.asyncio
async def test_empty_country_search_still_offers_inline_email_capture(client):
    response = await client.get("/search?country=DE")

    assert response.status_code == 200
    text = response.text
    assert 'name="source" value="country_inline"' in text
    assert 'name="frequency" value="daily"' in text
    assert "Be first when a matching AC returns" in text


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
