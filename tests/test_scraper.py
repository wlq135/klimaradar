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
async def test_affiliate_tagging():
    from app.services.affiliate import tag_url

    # No tag configured -> unchanged.
    assert tag_url("amazon.de", "https://www.amazon.de/dp/123") is not None

    # When a tag is present, the URL should contain it.
    url = tag_url("example.com", "https://example.com/product")
    assert url == "https://example.com/product"
