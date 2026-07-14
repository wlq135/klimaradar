"""Amazon Spain spider using Playwright."""

from app.spiders.amazon_base import BaseAmazonSpider


class AmazonEsSpider(BaseAmazonSpider):
    """Scrape Amazon.es search results for portable/split/window ACs."""

    name = "Amazon Spain"
    domain = "https://www.amazon.es"
    search_url_template = "https://www.amazon.es/s?k={query}"
    default_query = "aire acondicionado portátil"
    currency = "EUR"
    _LOCALE = "es-ES"

    _INCLUDE_TITLE_WORDS = [
        "aire acondicionado",
        "acondicionador",
        "climatizador",
        "air conditioner",
        "air conditioning",
        "monobloque",
        "split",
        "klima",
    ]
    _EXCLUDE_TITLE_WORDS = [
        "laptop",
        "portátil",
        "ordenador",
        "pc",
        "refrigerador",
        "ventilador",
        "fan",
        "humidificador",
        "deshumidificador",
        "radiador",
        "calefactor",
        "heater",
    ]

    _UNAVAILABLE_MARKERS = [
        "actualmente no disponible",
        "temporalmente no disponible",
        "no disponible",
        "agotado",
        "currently unavailable",
        "temporarily out of stock",
        "out of stock",
        "sold out",
        "no hay ofertas",
        "ninguna oferta disponible",
        "ninguna oferta destacada",
        "no offers",
        "no featured offers",
        "unavailable",
    ]
    _POSITIVE_MARKERS = [
        "en stock",
        "disponible",
        "envío",
        "prime",
        "mañana",
        "hoy",
        "inmediato",
        "generalmente se envía en",
        "in stock",
        "available",
        "añadir a la cesta",
        "comprar ahora",
        "añadir",
        "buy now",
        "add to basket",
    ]
