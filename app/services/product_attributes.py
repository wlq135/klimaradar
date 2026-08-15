"""Extract normalized product attributes from retailer titles.

Marketplace titles are inconsistent and many spider implementations cannot get
structured brand/specification data. These helpers provide a conservative
fallback so product cards do not lose trust with “Unknown brand · ? BTU”.
"""

from __future__ import annotations

import re

from app.spiders.base import ListingSnapshot


_BRANDS = [
    "AEG",
    "Airforce",
    "Argoclima",
    "Arlec",
    "Black+Decker",
    "Blaupunkt",
    "Comfee",
    "De'Longhi",
    "Duracraft",
    "Electrolux",
    "Eurom",
    "Frigidaire",
    "Honeywell",
    "Igenix",
    "Klarstein",
    "Kesser",
    "LG",
    "Midea",
    "Milectric",
    "Olimpia Splendid",
    "OneConcept",
    "Philips",
    "Pifco",
    "Prem-I-Air",
    "Princess",
    "Pro Breeze",
    "Remko",
    "Russell Hobbs",
    "Samsung",
    "Severin",
    "Sharp",
    "Suntec",
    "TCL",
    "Trotec",
    "Tristar",
    "Whirlpool",
    "Whynter",
    "Zibazi",
]

# Ordered longest-first so multi-word brands win over their individual words.
_BRAND_PATTERNS = [
    (brand, re.compile(rf"(?<![A-Za-z0-9]){re.escape(brand)}(?![A-Za-z0-9])", re.I))
    for brand in sorted(_BRANDS, key=len, reverse=True)
]

_BTU_VALUE = r"(?:[1-9]\d?(?:[.,]\d{3})+|[1-9]\d{2,}|[5-9]|[1-4][0-9])"
_BTU_PATTERN = re.compile(
    rf"(?<![A-Za-z0-9])((?:{_BTU_VALUE}\s*[/–-]\s*)*{_BTU_VALUE})\s*(?:btu|british thermal units?)(?![A-Za-z])",
    re.I,
)
_BTU_K_PATTERN = re.compile(
    rf"(?<![A-Za-z0-9])([5-9]|[1-4][0-9])\s*k\s*(?:btu|british thermal units?)(?![A-Za-z])",
    re.I,
)


def _parse_number(value: str) -> int | None:
    normalized = value.replace(".", "").replace(",", "")
    if not normalized.isdigit():
        return None
    parsed = int(normalized)
    # Real residential portable ACs are normally 5k–16k BTU. The guard avoids
    # treating an unrelated number followed by BTU as a cooling rating.
    if 5_000 <= parsed <= 16_000:
        return parsed
    return None


def extract_brand(title: str | None) -> str | None:
    """Return a recognized canonical brand from a marketplace title."""
    if not title:
        return None
    for canonical, pattern in _BRAND_PATTERNS:
        if pattern.search(title):
            return canonical
    return None


def extract_btu(title: str | None) -> tuple[int | None, int | None]:
    """Return the minimum and maximum BTU rating found in a title."""
    if not title:
        return None, None

    values: list[int] = []
    for match in _BTU_PATTERN.finditer(title):
        for raw_value in re.findall(_BTU_VALUE, match.group(1)):
            value = _parse_number(raw_value)
            if value is not None:
                values.append(value)
    for match in _BTU_K_PATTERN.finditer(title):
        kilos = int(match.group(1))
        if 5 <= kilos <= 16:
            values.append(kilos * 1_000)

    if not values:
        return None, None
    return min(values), max(values)


def enrich_snapshot(snapshot: ListingSnapshot) -> ListingSnapshot:
    """Fill missing brand/BTU fields from the listing title."""
    if snapshot.brand is None:
        snapshot.brand = extract_brand(snapshot.name)
    if snapshot.btu_min is None or snapshot.btu_max is None:
        btu_min, btu_max = extract_btu(snapshot.name)
        snapshot.btu_min = snapshot.btu_min if snapshot.btu_min is not None else btu_min
        snapshot.btu_max = snapshot.btu_max if snapshot.btu_max is not None else btu_max
    return snapshot
