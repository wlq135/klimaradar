"""Tests for marketplace title attribute extraction."""

from app.services.product_attributes import extract_btu, extract_brand


def test_extract_brands_uses_canonical_spacing_and_case():
    assert extract_brand("Midea Duo 12,000 BTU Portable Air Conditioner") == "Midea"
    assert extract_brand("black+decker 9000 BTU air conditioner") == "Black+Decker"
    assert extract_brand("De'longhi PAC EX100 Silent") == "De'Longhi"
    assert extract_brand("AEG AXP26U338CW mobile Klimaanlage") == "AEG"


def test_extract_brand_does_not_guess_unknown_names():
    assert extract_brand("Portable Air Conditioner 9000 BTU") is None


def test_extract_btu_supports_marketplace_number_formats():
    assert extract_btu("Midea 12,000 BTU portable AC") == (12000, 12000)
    assert extract_btu("Klimagerät 9.000 BTU/h") == (9000, 9000)
    assert extract_btu("9000BTU Air Conditioner") == (9000, 9000)
    assert extract_btu("12k BTU portable AC") == (12000, 12000)
    assert extract_btu("7,000/11,000 BTU portable AC") == (7000, 11000)


def test_extract_btu_ignores_unlikely_values():
    assert extract_btu("40 BTU toy cooler") == (None, None)
