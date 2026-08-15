"""Tests for the scraper pipeline."""

import pytest

from app.spiders.demo import DemoSpider


@pytest.mark.asyncio
async def test_demo_spider_returns_listings():
    spider = DemoSpider(retailer_id=1)
    listings = await spider.fetch_listings("portable ac")
    assert len(listings) >= 3
    for item in listings:
        assert item.name
        assert item.url
        assert item.currency == "EUR"
        assert item.stock_status in {
            "in_stock",
            "out_of_stock",
            "back_order",
            "pre_order",
            "unknown",
        }


@pytest.mark.asyncio
async def test_generic_price_parser():
    from app.spiders.generic import GenericHtmlSpider

    assert GenericHtmlSpider._parse_price("€349,99") == 349.99
    assert GenericHtmlSpider._parse_price("1.299,00 €") == 1299.0
    assert GenericHtmlSpider._parse_price("499.99") == 499.99
    assert GenericHtmlSpider._parse_price(None) is None
    assert GenericHtmlSpider._parse_price("N/A") is None


@pytest.mark.asyncio
async def test_amazon_uk_spider_uses_gbp_currency_preference():
    class FakeContext:
        def __init__(self):
            self.cookies = []

        async def add_cookies(self, cookies):
            self.cookies.extend(cookies)

    from app.spiders.amazon_uk import AmazonUkSpider

    spider = AmazonUkSpider(retailer_id=1, country="GB", affiliate_tag=None)
    context = FakeContext()
    await spider._pre_navigate(context)

    assert spider.domain == "https://www.amazon.co.uk"
    assert spider.currency == "GBP"
    assert "10000 BTU air conditioner" in spider.default_queries
    assert "14000 BTU air conditioner" in spider.default_queries
    assert context.cookies == [
        {
            "name": "i18n-prefs",
            "value": "GBP",
            "domain": ".amazon.co.uk",
            "path": "/",
        },
        {
            "name": "session-id",
            "value": "000-0000000-0000000",
            "domain": ".amazon.co.uk",
            "path": "/",
        },
    ]


def test_registry_includes_amazon_uk():
    from app.spiders.registry import get_spiders_for_country
    from app.spiders.amazon_uk import AmazonUkSpider

    spiders = get_spiders_for_country(
        {("GB", "Amazon United Kingdom"): 123}, country_filter="GB"
    )

    assert [spider.name for spider in spiders] == ["Amazon United Kingdom"]
    assert not AmazonUkSpider._is_relevant_title(
        "Sensibo Sky 3 Pack, Smart Home Air Conditioner System"
    )
    assert not AmazonUkSpider._is_relevant_title(
        "2000 BTU Portable Air Conditioner Mini Air Cooler"
    )
    assert not AmazonUkSpider._is_relevant_title(
        "Portable Air Conditioners for Room, Swamp Cooler, Windowless Evaporative Air Cooler"
    )
    assert not AmazonUkSpider._is_relevant_title(
        "12V Air Conditioner Under-Dash AC Kit for Classic Cars"
    )
    assert not AmazonUkSpider._is_relevant_title(
        "Portable Air Conditioner with Remote Control"
    )
    assert AmazonUkSpider._is_relevant_title(
        "Portable Air Conditioner 10000 BTU with Remote Control"
    )


def test_amazon_spiders_use_high_intent_btu_queries():
    from app.spiders.amazon_de import AmazonDeSpider
    from app.spiders.amazon_es import AmazonEsSpider
    from app.spiders.amazon_fr import AmazonFrSpider
    from app.spiders.amazon_it import AmazonItSpider
    from app.spiders.amazon_nl import AmazonNlSpider

    expected = {
        AmazonDeSpider: "mobiles klimagerät 12000 BTU",
        AmazonFrSpider: "climatiseur mobile 9000 BTU",
        AmazonItSpider: "climatizzatore portatile 12000 BTU",
        AmazonEsSpider: "aire acondicionado portátil 9000 BTU",
        AmazonNlSpider: "airconditioner 9000 BTU",
    }

    for spider, query in expected.items():
        assert query in spider.default_queries


def test_amazon_es_keeps_real_portable_acs_with_fan_mode():
    from app.spiders.amazon_es import AmazonEsSpider

    assert AmazonEsSpider._is_relevant_title(
        "Aire Acondicionado Portátil 9000 BTU con Ventilador y Deshumidificador"
    )
    assert not AmazonEsSpider._is_relevant_title(
        "Aire Acondicionado Portátil 9000 BTU, Climatizador Evaporativo con Nebulización"
    )


@pytest.mark.asyncio
async def test_amazon_be_spider_uses_marketplace_domain_and_queries():
    class FakeContext:
        def __init__(self):
            self.cookies = []

        async def add_cookies(self, cookies):
            self.cookies.extend(cookies)

    from app.spiders.amazon_be import AmazonBeSpider

    spider = AmazonBeSpider(retailer_id=1, country="BE", affiliate_tag=None)
    context = FakeContext()
    await spider._pre_navigate(context)

    assert spider.domain == "https://www.amazon.com.be"
    assert spider.search_url_template == "https://www.amazon.com.be/s?k={query}"
    assert "draagbare airconditioner" in spider.default_queries
    assert "mobiele airconditioner" in spider.default_queries
    assert "portable air conditioner" in spider.default_queries
    assert spider._MIN_PRICE == 120.0
    assert context.cookies[0]["domain"] == ".amazon.com.be"


def test_amazon_de_filters_evaporative_coolers_without_exhaust_hose():
    from app.spiders.amazon_de import AmazonDeSpider

    assert not AmazonDeSpider._is_relevant_title(
        "Klimagerät ohne Abluftschlauch 30L mit Kühlakkus"
    )
    assert AmazonDeSpider._is_relevant_title(
        "OKYUK Mobile Klimaanlage 7000 BTU mit Abluftschlauch"
    )


@pytest.mark.asyncio
async def test_affiliate_tagging():
    from app.services.affiliate import tag_url

    # No tag configured -> unchanged.
    assert tag_url("amazon.de", "https://www.amazon.de/dp/123") is not None

    # When a tag is present, the URL should contain it.
    url = tag_url("example.com", "https://example.com/product")
    assert url == "https://example.com/product"
