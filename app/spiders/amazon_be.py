"""Amazon Belgium spider using Playwright."""

from app.spiders.amazon_base import BaseAmazonSpider


class AmazonBeSpider(BaseAmazonSpider):
    """Scrape Amazon.be search results for portable/split/window ACs."""

    name = "Amazon Belgium"
    domain = "https://www.amazon.be"
    search_url_template = "https://www.amazon.be/s?k={query}"
    default_query = "draagbare airconditioner"
    currency = "EUR"
    _LOCALE = "nl-BE"

    _INCLUDE_TITLE_WORDS = [
        "airconditioner",
        "airco",
        "air conditioner",
        "air conditioning",
        "klima",
        "monoblock",
        "split",
    ]
    _EXCLUDE_TITLE_WORDS = [
        "laptop",
        "notebook",
        "pc",
        "koelpad",
        "koeler",
        "ventilator",
        "fan",
        "bevochtiger",
        "luchtbevochtiger",
        "ontvochtiger",
        "luchtontvochtiger",
        "kachel",
        "verwarming",
        "heater",
    ]

    _UNAVAILABLE_MARKERS = [
        "momenteel niet beschikbaar",
        "tijdelijk niet op voorraad",
        "niet op voorraad",
        "niet beschikbaar",
        "uitverkocht",
        "currently unavailable",
        "temporarily out of stock",
        "out of stock",
        "sold out",
        "geen aanbiedingen",
        "geen aanbiedingen beschikbaar",
        "geen aanbiedingen in de kijker",
        "no offers",
        "no featured offers",
        "unavailable",
    ]
    _POSITIVE_MARKERS = [
        "op voorraad",
        "beschikbaar",
        "verzending",
        "prime",
        "morgen",
        "vandaag",
        "direct",
        "gewoonlijk verzonden binnen",
        "in stock",
        "available",
        "in winkelwagen",
        "nu kopen",
        "kopen",
        "buy now",
        "add to basket",
    ]
