"""Tests for retailer stock-status inference heuristics."""

from unittest.mock import AsyncMock

import pytest

from app.spiders.amazon_de import AmazonDeSpider
from app.spiders.boulanger_fr import BoulangerFrSpider
from app.spiders.darty_fr import DartyFrSpider


def _card(text: str):
    """Return a fake Playwright element whose inner_text() returns ``text``."""
    item = AsyncMock()
    item.inner_text = AsyncMock(return_value=text)
    return item


@pytest.mark.asyncio
async def test_amazon_unavailable_phrases_are_out_of_stock():
    cases = [
        "Derzeit nicht verfügbar",
        "Keine hervorgehobenen Angebote verfügbar",
        "Keine Angebote verfügbar",
        "Currently unavailable",
        "Temporarily out of stock",
    ]
    for text in cases:
        assert (
            await AmazonDeSpider._infer_stock_status(_card(text), 199.99)
            == "out_of_stock"
        )


@pytest.mark.asyncio
async def test_amazon_price_without_positive_signal_is_unknown():
    # A raw price snippet alone must not be treated as in stock.
    assert (
        await AmazonDeSpider._infer_stock_status(
            _card("Midea AC\n185,99 €\n(1 neuer Artikel)"), 185.99
        )
        == "unknown"
    )


@pytest.mark.asyncio
async def test_amazon_positive_availability_signals_are_in_stock():
    cases = [
        "Midea AC\n199 €\nPrime\nLieferung morgen",
        "Midea AC\nAuf Lager\n199 €",
        "Midea AC\nSofort lieferbar\n199 €",
    ]
    for text in cases:
        assert (
            await AmazonDeSpider._infer_stock_status(_card(text), 199.0)
            == "in_stock"
        )


@pytest.mark.asyncio
async def test_amazon_no_price_is_unknown():
    assert (
        await AmazonDeSpider._infer_stock_status(
            _card("Midea AC\nLieferung morgen"), None
        )
        == "unknown"
    )


@pytest.mark.asyncio
async def test_boulanger_unavailable_markers_are_out_of_stock():
    assert (
        await BoulangerFrSpider._infer_stock_status(
            _card("Climatiseur\n299 €\nIndisponible"), 299.0
        )
        == "out_of_stock"
    )


@pytest.mark.asyncio
async def test_boulanger_price_without_positive_signal_is_unknown():
    assert (
        await BoulangerFrSpider._infer_stock_status(
            _card("Climatiseur\n299 €"), 299.0
        )
        == "unknown"
    )


@pytest.mark.asyncio
async def test_boulanger_positive_signal_is_in_stock():
    assert (
        await BoulangerFrSpider._infer_stock_status(
            _card("Climatiseur\n299 €\nEn stock"), 299.0
        )
        == "in_stock"
    )


@pytest.mark.asyncio
async def test_darty_unavailable_markers_are_out_of_stock():
    assert (
        await DartyFrSpider._infer_stock_status(
            _card("Climatiseur\n349 €\nRupture de stock"), 349.0
        )
        == "out_of_stock"
    )


@pytest.mark.asyncio
async def test_darty_price_without_positive_signal_is_unknown():
    assert (
        await DartyFrSpider._infer_stock_status(
            _card("Climatiseur\n349 €"), 349.0
        )
        == "unknown"
    )


@pytest.mark.asyncio
async def test_darty_positive_signal_is_in_stock():
    assert (
        await DartyFrSpider._infer_stock_status(
            _card("Climatiseur\n349 €\nDisponible"), 349.0
        )
        == "in_stock"
    )
