"""Amazon Germany spider using Playwright."""

from app.spiders.amazon_base import BaseAmazonSpider


class AmazonDeSpider(BaseAmazonSpider):
    """Scrape Amazon.de search results for portable/split/window ACs."""

    name = "Amazon Germany"
    domain = "https://www.amazon.de"
    search_url_template = "https://www.amazon.de/s?k={query}"
    default_query = "mobiles klimagerät"
    currency = "EUR"
    _LOCALE = "de-DE"

    _INCLUDE_TITLE_WORDS = [
        "klimagerät",
        "klimaanlage",
        "klima",
        "air conditioner",
        "air conditioning",
        "monoblock",
        "split",
    ]
    _EXCLUDE_TITLE_WORDS = [
        "laptop",
        "notebook",
        "pc",
        "cooling pad",
        "kühlpad",
        "kühler",
        "lüfter",
        "ventilator",
        "fan",
        "humidifier",
        "luftbefeuchter",
        "befeuchter",
        "dehumidifier",
        "luftentfeuchter",
        "entfeuchter",
        "heizlüfter",
        "heizung",
        "heater",
    ]

    _UNAVAILABLE_MARKERS = [
        "derzeit nicht verfügbar",
        "temporär nicht verfügbar",
        "nicht verfügbar",
        "nicht auf lager",
        "nicht lieferbar",
        "nicht mehr verfügbar",
        "ausverkauft",
        "vergriffen",
        "currently unavailable",
        "temporarily out of stock",
        "out of stock",
        "sold out",
        "kein angebot",
        "keine angebote verfügbar",
        "keine hervorgehobenen angebote",
        "no offers",
        "no featured offers",
        "unavailable",
        "nur noch",
        "nur",
    ]
    _POSITIVE_MARKERS = [
        "auf lager",
        "lieferbar",
        "versandt",
        "versand",
        "lieferung",
        "prime",
        "morgen",
        "heute",
        "sofort",
        "gewöhnlich versandfertig",
        "in stock",
        "available",
        "in den warenkorb",
        "jetzt kaufen",
        "sofort kaufen",
        "kaufen",
        "add to basket",
        "buy now",
    ]
