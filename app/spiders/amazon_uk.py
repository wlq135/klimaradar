"""Amazon United Kingdom spider using Playwright."""

from app.spiders.amazon_base import BaseAmazonSpider


class AmazonUkSpider(BaseAmazonSpider):
    """Scrape Amazon.co.uk search results for portable/split/window ACs."""

    name = "Amazon United Kingdom"
    domain = "https://www.amazon.co.uk"
    search_url_template = "https://www.amazon.co.uk/s?k={query}"
    default_query = "portable air conditioner"
    default_queries = [
        "portable air conditioner",
        "mobile air conditioner",
        "10000 BTU air conditioner",
        "14000 BTU air conditioner",
    ]
    currency = "GBP"
    _LOCALE = "en-GB"

    _INCLUDE_TITLE_WORDS = [
        "air conditioner",
        "air conditioning",
        "air cooler",
        "monoblock",
        "monobloc",
        "split",
    ]
    _EXCLUDE_TITLE_WORDS = [
        "laptop",
        "notebook",
        "pc",
        "cooling pad",
        "cooler pad",
        "fan",
        "humidifier",
        "dehumidifier",
        "radiator",
        "heater",
    ]

    _UNAVAILABLE_MARKERS = [
        "currently unavailable",
        "temporarily out of stock",
        "out of stock",
        "sold out",
        "no offers",
        "no featured offers",
        "unavailable",
        "only 1 left in stock",
        "only 2 left in stock",
        "order soon",
    ]
    _POSITIVE_MARKERS = [
        "in stock",
        "available",
        "dispatched from",
        "dispatch",
        "delivery",
        "tomorrow",
        "today",
        "usually dispatched",
        "prime",
        "add to basket",
        "buy now",
    ]
