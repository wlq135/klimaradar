"""Registry of retailer spiders.

Each entry maps a retailer name/country to a concrete spider implementation.
"""

from app.config import settings
from app.spiders.amazon_de import AmazonDeSpider
from app.spiders.amazon_fr import AmazonFrSpider
from app.spiders.boulanger_fr import BoulangerFrSpider
from app.spiders.base import Spider
from app.spiders.darty_fr import DartyFrSpider
from app.spiders.demo import DemoSpider
from app.spiders.generic import GenericHtmlSpider
from app.spiders.mediamarkt_de import MediaMarktDeSpider

# GenericHtmlSpider configs for retailers that serve static HTML.
_GENERIC_SPIDERS: list[dict] = [
    {
        "name": "Generic Static Retailer (example)",
        "country": "DE",
        "base_url": "https://example-shop.de",
        "search_url_template": "https://example-shop.de/search",
        "query_param": "q",
        "currency": "EUR",
        "affiliate_url_template": "{url}?ref={tag}",
        "listing_selector": ".product-card",
        "fields": {
            "name": ".product-title",
            "url": "a",
            "price": ".product-price",
            "image": "img",
            "stock": ".availability",
        },
        "in_stock_words": ["auf lager", "lieferbar", "verfügbar"],
        "out_of_stock_words": ["nicht lieferbar", "ausverkauft"],
    },
]


def _affiliate_tag_for(country: str, retailer_name: str) -> str | None:
    if retailer_name == "Amazon Germany":
        return settings.amazon_de_affiliate_tag
    if retailer_name == "Amazon France":
        return settings.amazon_fr_affiliate_tag
    if retailer_name == "MediaMarkt Germany":
        return settings.mediamarkt_de_affiliate_tag
    if retailer_name == "Boulanger France":
        return settings.boulanger_fr_affiliate_tag
    if retailer_name == "Darty France":
        return settings.darty_fr_affiliate_tag
    return None


def get_spiders_for_country(
    retailer_id_map: dict[tuple[str, str], int],
    country_filter: str | None = None,
) -> list[Spider]:
    """Instantiate spider objects for the requested countries.

    Args:
        retailer_id_map: mapping of (country, retailer_name) -> retailer db id.
        country_filter: if provided, only return spiders for that country.
    """
    spiders: list[Spider] = []

    # Demo spider is only enabled in debug/demo mode to avoid fake public listings.
    if settings.enable_demo:
        demo_id = retailer_id_map.get(("DEMO", "Demo Retailer"))
        if demo_id:
            spiders.append(DemoSpider(retailer_id=demo_id))

    # Playwright-based spiders for known retailers.
    playwright_spiders: list[tuple[str, str, type[Spider]]] = [
        ("DE", "Amazon Germany", AmazonDeSpider),
        ("DE", "MediaMarkt Germany", MediaMarktDeSpider),
        ("FR", "Amazon France", AmazonFrSpider),
        ("FR", "Boulanger France", BoulangerFrSpider),
        ("FR", "Darty France", DartyFrSpider),
    ]
    for country, retailer_name, spider_cls in playwright_spiders:
        if country_filter and country != country_filter:
            continue
        retailer_id = retailer_id_map.get((country, retailer_name))
        if not retailer_id:
            continue
        tag = _affiliate_tag_for(country, retailer_name)
        spiders.append(spider_cls(retailer_id=retailer_id, country=country, affiliate_tag=tag))

    # Static/generic spiders for simple HTML sites.
    for config in _GENERIC_SPIDERS:
        country = config["country"]
        if country_filter and country != country_filter:
            continue
        key = (country, config["name"])
        retailer_id = retailer_id_map.get(key)
        if not retailer_id:
            continue
        tag = _affiliate_tag_for(country, config["name"])
        spiders.append(GenericHtmlSpider(retailer_id, config, tag))

    return spiders
