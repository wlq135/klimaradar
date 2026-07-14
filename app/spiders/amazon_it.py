"""Amazon Italy spider using Playwright."""

from app.spiders.amazon_base import BaseAmazonSpider


class AmazonItSpider(BaseAmazonSpider):
    """Scrape Amazon.it search results for portable/split/window ACs."""

    name = "Amazon Italy"
    domain = "https://www.amazon.it"
    search_url_template = "https://www.amazon.it/s?k={query}"
    default_query = "condizionatore portatile"
    currency = "EUR"
    _LOCALE = "it-IT"

    _INCLUDE_TITLE_WORDS = [
        "condizionatore",
        "climatizzatore",
        "aria condizionata",
        "air conditioner",
        "air conditioning",
        "monoblocco",
        "split",
        "klima",
    ]
    _EXCLUDE_TITLE_WORDS = [
        "laptop",
        "notebook",
        "pc",
        "raffreddatore pc",
        "raffreddatore",
        "ventilatore",
        "fan",
        "umidificatore",
        "deumidificatore",
        "riscaldatore",
        "stufa",
        "heater",
    ]

    _UNAVAILABLE_MARKERS = [
        "al momento non disponibile",
        "temporaneamente non disponibile",
        "non disponibile",
        "esaurito",
        "esausto",
        "currently unavailable",
        "temporarily out of stock",
        "out of stock",
        "sold out",
        "nessuna offerta",
        "nessuna offerta disponibile",
        "nessuna offerta in evidenza",
        "no offers",
        "no featured offers",
        "unavailable",
    ]
    _POSITIVE_MARKERS = [
        "in stock",
        "disponibile",
        "spedizione",
        "prime",
        "domani",
        "oggi",
        "immediato",
        "generalmente spedito entro",
        "available",
        "aggiungi al carrello",
        "acquista ora",
        "aggiungi",
        "buy now",
        "add to basket",
    ]
