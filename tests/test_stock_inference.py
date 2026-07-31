"""Tests for retailer stock-status inference heuristics."""

from unittest.mock import AsyncMock

import pytest

from app.spiders.amazon_base import BaseAmazonSpider
from app.spiders.amazon_de import AmazonDeSpider
from app.spiders.amazon_fr import AmazonFrSpider
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


@pytest.mark.asyncio
async def test_amazon_fr_unavailable_phrases_are_out_of_stock():
    cases = [
        "Actuellement indisponible",
        "Aucune offre mise en avant",
        "Aucune offre disponible",
        "En rupture de stock",
    ]
    for text in cases:
        assert (
            await AmazonFrSpider._infer_stock_status(_card(text), 199.99)
            == "out_of_stock"
        )


@pytest.mark.asyncio
async def test_amazon_fr_positive_availability_signals_are_in_stock():
    cases = [
        "Climatiseur\n199 €\nPrime\nLivraison demain",
        "Climatiseur\nEn stock\n199 €",
        "Climatiseur\nDisponible\n199 €",
    ]
    for text in cases:
        assert (
            await AmazonFrSpider._infer_stock_status(_card(text), 199.0)
            == "in_stock"
        )


# --- Accessory filtering -----------------------------------------------------
# These tests guard data quality: AC accessories (window seals, deflectors,
# gaskets) must be excluded, while real ACs that merely mention an accessory
# in their description (e.g. "mit Fensterabdichtung") must be kept.
from app.spiders.amazon_de import AmazonDeSpider
from app.spiders.amazon_fr import AmazonFrSpider
from app.spiders.amazon_it import AmazonItSpider
from app.spiders.amazon_es import AmazonEsSpider


@pytest.mark.asyncio
async def test_accessory_titles_are_excluded_across_locales():
    """Window seals, deflectors and gaskets must never be listed as ACs."""
    cases = [
        (AmazonDeSpider, "Mobile Klimaanlage Fensterabdichtung 300cm Ohne Bohren, Fensterabdeckung, Hot Air Stop"),
        (AmazonItSpider, "Deflettore Condizionatore Regolabile, Deflettore Aria per Condizionatore a Parete"),
        (AmazonItSpider, "300 CM Guarnizione Finestra Condizionatore Portatile Anti-Zanzare"),
        (AmazonEsSpider, "Kit ventana aire acondicionado portatil, Junta de ventana"),
        (AmazonFrSpider, "HOOMEE Joint de Portes Coulissantes pour Climatiseur Mobile et Seche-Linge"),
        (AmazonItSpider, "400CM Universale Guarnizione Finestra Condizionatore"),
    ]
    for spider, title in cases:
        assert spider._is_relevant_title(title) is False, (spider.__name__, title)


@pytest.mark.asyncio
async def test_real_ac_titles_are_kept_even_when_mentioning_accessory():
    """A genuine AC that bundles a window seal must NOT be filtered out."""
    cases = [
        (AmazonDeSpider, "Mobiles Klimagerat 7000 BTU, 4-in-1 Mobile Klimaanlage mit Abluftschlauch & 4m Fensterabdichtung"),
        (AmazonItSpider, "Condizionatore Portatile 7000 BTU con Tubo di Scarico"),
        (AmazonFrSpider, "Climatiseur Mobile 9000 BTU - Climatiseur Portable 4 en 1"),
        (AmazonEsSpider, "Aire Acondicionado Portatil 12000 BTU"),
    ]
    for spider, title in cases:
        assert spider._is_relevant_title(title) is True, (spider.__name__, title)


def test_price_floor_is_reasonable():
    """The safety-net price floor must stay above typical accessory prices."""
    assert BaseAmazonSpider._MIN_PRICE >= 40.0
    for spider in (AmazonDeSpider, AmazonFrSpider, AmazonItSpider, AmazonEsSpider):
        assert spider._MIN_PRICE >= 40.0, spider.__name__

