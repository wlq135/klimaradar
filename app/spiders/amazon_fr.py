"""Amazon France spider using Playwright."""

from app.spiders.amazon_base import BaseAmazonSpider


class AmazonFrSpider(BaseAmazonSpider):
    """Scrape Amazon.fr search results for portable/split/window ACs."""

    name = "Amazon France"
    domain = "https://www.amazon.fr"
    search_url_template = "https://www.amazon.fr/s?k={query}"
    default_query = "climatiseur portable"
    currency = "EUR"
    _LOCALE = "fr-FR"

    _INCLUDE_TITLE_WORDS = [
        "climatiseur",
        "clim",
        "air conditionné",
        "air conditioner",
        "air conditioning",
        "monobloc",
        "split",
        "klima",
    ]
    _EXCLUDE_TITLE_WORDS = [
        "laptop",
        "ordinateur portable",
        "pc",
        "refroidisseur pc",
        "refroidisseur",
        "ventilateur",
        "ventilo",
        "fan",
        "humidificateur",
        "déshumidificateur",
        "deshumidificateur",
        "radiateur",
        "chauffage",
        "heater",
    ]

    _UNAVAILABLE_MARKERS = [
        "actuellement indisponible",
        "temporairement indisponible",
        "indisponible",
        "en rupture de stock",
        "rupture de stock",
        "épuisé",
        "epuise",
        "non disponible",
        "plus disponible",
        "currently unavailable",
        "temporarily out of stock",
        "out of stock",
        "sold out",
        "aucune offre",
        "aucune offre disponible",
        "aucune offre mise en avant",
        "no offers",
        "no featured offers",
        "unavailable",
        "il ne reste plus",
    ]
    _POSITIVE_MARKERS = [
        "en stock",
        "disponible",
        "livraison",
        "expédié",
        "prime",
        "demain",
        "aujourd'hui",
        "immédiat",
        "généralement expédié sous",
        "generalement expedie sous",
        "in stock",
        "available",
        "ajouter au panier",
        "acheter maintenant",
        "ajouter",
        "buy now",
        "add to basket",
    ]
