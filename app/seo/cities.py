"""City metadata and localized SEO copy for KlimaRadar city landing pages."""

from __future__ import annotations

COUNTRY_LANGUAGES = {
    "DE": "de-DE",
    "FR": "fr-FR",
    "IT": "it-IT",
    "ES": "es-ES",
    "NL": "nl-NL",
    "BE": "nl-BE",
}

COUNTRY_NAMES = {
    "DE": {"de": "Deutschland", "fr": "Allemagne", "en": "Germany"},
    "FR": {"de": "Frankreich", "fr": "France", "en": "France"},
    "IT": {"de": "Italien", "fr": "Italie", "en": "Italy", "it": "Italia"},
    "ES": {"de": "Spanien", "fr": "Espagne", "en": "Spain", "es": "España"},
    "NL": {"de": "Niederlande", "fr": "Pays-Bas", "en": "Netherlands", "nl": "Nederland"},
    "BE": {"de": "Belgien", "fr": "Belgique", "en": "Belgium", "nl": "België"},
}

# fmt: off
CITY_METADATA: list[dict] = [
    # Germany
    {"country": "DE", "slug": "berlin", "display_name": "Berlin", "region": "Berlin"},
    {"country": "DE", "slug": "hamburg", "display_name": "Hamburg", "region": "Hamburg"},
    {"country": "DE", "slug": "muenchen", "display_name": "München", "region": "Bayern"},
    {"country": "DE", "slug": "koeln", "display_name": "Köln", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "frankfurt", "display_name": "Frankfurt am Main", "region": "Hessen"},
    {"country": "DE", "slug": "stuttgart", "display_name": "Stuttgart", "region": "Baden-Württemberg"},
    {"country": "DE", "slug": "duesseldorf", "display_name": "Düsseldorf", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "leipzig", "display_name": "Leipzig", "region": "Sachsen"},
    {"country": "DE", "slug": "dortmund", "display_name": "Dortmund", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "essen", "display_name": "Essen", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "bremen", "display_name": "Bremen", "region": "Bremen"},
    {"country": "DE", "slug": "dresden", "display_name": "Dresden", "region": "Sachsen"},
    {"country": "DE", "slug": "hannover", "display_name": "Hannover", "region": "Niedersachsen"},
    {"country": "DE", "slug": "nuernberg", "display_name": "Nürnberg", "region": "Bayern"},
    {"country": "DE", "slug": "duisburg", "display_name": "Duisburg", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "bochum", "display_name": "Bochum", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "wuppertal", "display_name": "Wuppertal", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "bielefeld", "display_name": "Bielefeld", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "bonn", "display_name": "Bonn", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "muenster", "display_name": "Münster", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "karlsruhe", "display_name": "Karlsruhe", "region": "Baden-Württemberg"},
    {"country": "DE", "slug": "mannheim", "display_name": "Mannheim", "region": "Baden-Württemberg"},
    {"country": "DE", "slug": "augsburg", "display_name": "Augsburg", "region": "Bayern"},
    {"country": "DE", "slug": "wiesbaden", "display_name": "Wiesbaden", "region": "Hessen"},
    {"country": "DE", "slug": "gelsenkirchen", "display_name": "Gelsenkirchen", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "moenchengladbach", "display_name": "Mönchengladbach", "region": "Nordrhein-Westfalen"},
    {"country": "DE", "slug": "braunschweig", "display_name": "Braunschweig", "region": "Niedersachsen"},
    {"country": "DE", "slug": "kiel", "display_name": "Kiel", "region": "Schleswig-Holstein"},
    {"country": "DE", "slug": "chemnitz", "display_name": "Chemnitz", "region": "Sachsen"},
    {"country": "DE", "slug": "aachen", "display_name": "Aachen", "region": "Nordrhein-Westfalen"},

    # France
    {"country": "FR", "slug": "paris", "display_name": "Paris", "region": "Île-de-France"},
    {"country": "FR", "slug": "lyon", "display_name": "Lyon", "region": "Auvergne-Rhône-Alpes"},
    {"country": "FR", "slug": "marseille", "display_name": "Marseille", "region": "Provence-Alpes-Côte d'Azur"},
    {"country": "FR", "slug": "toulouse", "display_name": "Toulouse", "region": "Occitanie"},
    {"country": "FR", "slug": "nice", "display_name": "Nice", "region": "Provence-Alpes-Côte d'Azur"},
    {"country": "FR", "slug": "nantes", "display_name": "Nantes", "region": "Pays de la Loire"},
    {"country": "FR", "slug": "strasbourg", "display_name": "Strasbourg", "region": "Grand Est"},
    {"country": "FR", "slug": "montpellier", "display_name": "Montpellier", "region": "Occitanie"},
    {"country": "FR", "slug": "bordeaux", "display_name": "Bordeaux", "region": "Nouvelle-Aquitaine"},
    {"country": "FR", "slug": "lille", "display_name": "Lille", "region": "Hauts-de-France"},
    {"country": "FR", "slug": "rennes", "display_name": "Rennes", "region": "Bretagne"},
    {"country": "FR", "slug": "reims", "display_name": "Reims", "region": "Grand Est"},
    {"country": "FR", "slug": "saint-etienne", "display_name": "Saint-Étienne", "region": "Auvergne-Rhône-Alpes"},
    {"country": "FR", "slug": "le-havre", "display_name": "Le Havre", "region": "Normandie"},
    {"country": "FR", "slug": "toulon", "display_name": "Toulon", "region": "Provence-Alpes-Côte d'Azur"},
    {"country": "FR", "slug": "grenoble", "display_name": "Grenoble", "region": "Auvergne-Rhône-Alpes"},
    {"country": "FR", "slug": "dijon", "display_name": "Dijon", "region": "Bourgogne-Franche-Comté"},
    {"country": "FR", "slug": "angers", "display_name": "Angers", "region": "Pays de la Loire"},
    {"country": "FR", "slug": "nimes", "display_name": "Nîmes", "region": "Occitanie"},
    {"country": "FR", "slug": "villeurbanne", "display_name": "Villeurbanne", "region": "Auvergne-Rhône-Alpes"},
    {"country": "FR", "slug": "saint-denis", "display_name": "Saint-Denis", "region": "Île-de-France"},
    {"country": "FR", "slug": "le-mans", "display_name": "Le Mans", "region": "Pays de la Loire"},
    {"country": "FR", "slug": "clermont-ferrand", "display_name": "Clermont-Ferrand", "region": "Auvergne-Rhône-Alpes"},
    {"country": "FR", "slug": "aix-en-provence", "display_name": "Aix-en-Provence", "region": "Provence-Alpes-Côte d'Azur"},
    {"country": "FR", "slug": "brest", "display_name": "Brest", "region": "Bretagne"},
    {"country": "FR", "slug": "limoges", "display_name": "Limoges", "region": "Nouvelle-Aquitaine"},
    {"country": "FR", "slug": "tours", "display_name": "Tours", "region": "Centre-Val de Loire"},
    {"country": "FR", "slug": "amiens", "display_name": "Amiens", "region": "Hauts-de-France"},
    {"country": "FR", "slug": "perpignan", "display_name": "Perpignan", "region": "Occitanie"},
    {"country": "FR", "slug": "metz", "display_name": "Metz", "region": "Grand Est"},

    # Italy
    {"country": "IT", "slug": "roma", "display_name": "Roma", "region": "Lazio"},
    {"country": "IT", "slug": "milano", "display_name": "Milano", "region": "Lombardia"},
    {"country": "IT", "slug": "napoli", "display_name": "Napoli", "region": "Campania"},
    {"country": "IT", "slug": "torino", "display_name": "Torino", "region": "Piemonte"},
    {"country": "IT", "slug": "palermo", "display_name": "Palermo", "region": "Sicilia"},
    {"country": "IT", "slug": "genova", "display_name": "Genova", "region": "Liguria"},
    {"country": "IT", "slug": "bologna", "display_name": "Bologna", "region": "Emilia-Romagna"},
    {"country": "IT", "slug": "firenze", "display_name": "Firenze", "region": "Toscana"},
    {"country": "IT", "slug": "bari", "display_name": "Bari", "region": "Puglia"},
    {"country": "IT", "slug": "catania", "display_name": "Catania", "region": "Sicilia"},
    {"country": "IT", "slug": "venezia", "display_name": "Venezia", "region": "Veneto"},
    {"country": "IT", "slug": "verona", "display_name": "Verona", "region": "Veneto"},
    {"country": "IT", "slug": "messina", "display_name": "Messina", "region": "Sicilia"},
    {"country": "IT", "slug": "padova", "display_name": "Padova", "region": "Veneto"},
    {"country": "IT", "slug": "trieste", "display_name": "Trieste", "region": "Friuli-Venezia Giulia"},
    {"country": "IT", "slug": "brescia", "display_name": "Brescia", "region": "Lombardia"},
    {"country": "IT", "slug": "prato", "display_name": "Prato", "region": "Toscana"},
    {"country": "IT", "slug": "taranto", "display_name": "Taranto", "region": "Puglia"},
    {"country": "IT", "slug": "modena", "display_name": "Modena", "region": "Emilia-Romagna"},
    {"country": "IT", "slug": "reggio-calabria", "display_name": "Reggio Calabria", "region": "Calabria"},

    # Spain
    {"country": "ES", "slug": "madrid", "display_name": "Madrid", "region": "Comunidad de Madrid"},
    {"country": "ES", "slug": "barcelona", "display_name": "Barcelona", "region": "Cataluña"},
    {"country": "ES", "slug": "valencia", "display_name": "Valencia", "region": "Comunidad Valenciana"},
    {"country": "ES", "slug": "sevilla", "display_name": "Sevilla", "region": "Andalucía"},
    {"country": "ES", "slug": "zaragoza", "display_name": "Zaragoza", "region": "Aragón"},
    {"country": "ES", "slug": "malaga", "display_name": "Málaga", "region": "Andalucía"},
    {"country": "ES", "slug": "murcia", "display_name": "Murcia", "region": "Región de Murcia"},
    {"country": "ES", "slug": "palma", "display_name": "Palma", "region": "Islas Baleares"},
    {"country": "ES", "slug": "las-palmas", "display_name": "Las Palmas", "region": "Canarias"},
    {"country": "ES", "slug": "bilbao", "display_name": "Bilbao", "region": "País Vasco"},
    {"country": "ES", "slug": "alicante", "display_name": "Alicante", "region": "Comunidad Valenciana"},
    {"country": "ES", "slug": "cordoba", "display_name": "Córdoba", "region": "Andalucía"},
    {"country": "ES", "slug": "valladolid", "display_name": "Valladolid", "region": "Castilla y León"},
    {"country": "ES", "slug": "vigo", "display_name": "Vigo", "region": "Galicia"},
    {"country": "ES", "slug": "gijon", "display_name": "Gijón", "region": "Asturias"},
    {"country": "ES", "slug": "hospitalet-de-llobregat", "display_name": "Hospitalet de Llobregat", "region": "Cataluña"},
    {"country": "ES", "slug": "la-coruna", "display_name": "La Coruña", "region": "Galicia"},
    {"country": "ES", "slug": "granada", "display_name": "Granada", "region": "Andalucía"},
    {"country": "ES", "slug": "vitoria-gasteiz", "display_name": "Vitoria-Gasteiz", "region": "País Vasco"},
    {"country": "ES", "slug": "elche", "display_name": "Elche", "region": "Comunidad Valenciana"},

    # Netherlands
    {"country": "NL", "slug": "amsterdam", "display_name": "Amsterdam", "region": "Noord-Holland"},
    {"country": "NL", "slug": "rotterdam", "display_name": "Rotterdam", "region": "Zuid-Holland"},
    {"country": "NL", "slug": "den-haag", "display_name": "Den Haag", "region": "Zuid-Holland"},
    {"country": "NL", "slug": "utrecht", "display_name": "Utrecht", "region": "Utrecht"},
    {"country": "NL", "slug": "eindhoven", "display_name": "Eindhoven", "region": "Noord-Brabant"},
    {"country": "NL", "slug": "tilburg", "display_name": "Tilburg", "region": "Noord-Brabant"},
    {"country": "NL", "slug": "groningen", "display_name": "Groningen", "region": "Groningen"},
    {"country": "NL", "slug": "almere", "display_name": "Almere", "region": "Flevoland"},
    {"country": "NL", "slug": "breda", "display_name": "Breda", "region": "Noord-Brabant"},
    {"country": "NL", "slug": "nijmegen", "display_name": "Nijmegen", "region": "Gelderland"},
    {"country": "NL", "slug": "enschede", "display_name": "Enschede", "region": "Overijssel"},
    {"country": "NL", "slug": "haarlem", "display_name": "Haarlem", "region": "Noord-Holland"},
    {"country": "NL", "slug": "arnhem", "display_name": "Arnhem", "region": "Gelderland"},
    {"country": "NL", "slug": "amersfoort", "display_name": "Amersfoort", "region": "Utrecht"},
    {"country": "NL", "slug": "zaanstad", "display_name": "Zaanstad", "region": "Noord-Holland"},
    {"country": "NL", "slug": "apeldoorn", "display_name": "Apeldoorn", "region": "Gelderland"},
    {"country": "NL", "slug": "s-hertogenbosch", "display_name": "'s-Hertogenbosch", "region": "Noord-Brabant"},
    {"country": "NL", "slug": "hoofddorp", "display_name": "Hoofddorp", "region": "Noord-Holland"},
    {"country": "NL", "slug": "maastricht", "display_name": "Maastricht", "region": "Limburg"},
    {"country": "NL", "slug": "leiden", "display_name": "Leiden", "region": "Zuid-Holland"},

    # Belgium
    {"country": "BE", "slug": "brussels", "display_name": "Brussels", "region": "Brussels-Capital"},
    {"country": "BE", "slug": "antwerp", "display_name": "Antwerp", "region": "Antwerp"},
    {"country": "BE", "slug": "ghent", "display_name": "Ghent", "region": "East Flanders"},
    {"country": "BE", "slug": "charleroi", "display_name": "Charleroi", "region": "Hainaut"},
    {"country": "BE", "slug": "liege", "display_name": "Liège", "region": "Liège"},
    {"country": "BE", "slug": "bruges", "display_name": "Bruges", "region": "West Flanders"},
    {"country": "BE", "slug": "namur", "display_name": "Namur", "region": "Namur"},
    {"country": "BE", "slug": "leuven", "display_name": "Leuven", "region": "Flemish Brabant"},
    {"country": "BE", "slug": "mons", "display_name": "Mons", "region": "Hainaut"},
    {"country": "BE", "slug": "alost", "display_name": "Alost", "region": "East Flanders"},
    {"country": "BE", "slug": "mechelen", "display_name": "Mechelen", "region": "Antwerp"},
    {"country": "BE", "slug": "la-louviere", "display_name": "La Louvière", "region": "Hainaut"},
    {"country": "BE", "slug": "kortrijk", "display_name": "Kortrijk", "region": "West Flanders"},
    {"country": "BE", "slug": "hasselt", "display_name": "Hasselt", "region": "Limburg"},
    {"country": "BE", "slug": "ostend", "display_name": "Ostend", "region": "West Flanders"},
    {"country": "BE", "slug": "sint-niklaas", "display_name": "Sint-Niklaas", "region": "East Flanders"},
    {"country": "BE", "slug": "genk", "display_name": "Genk", "region": "Limburg"},
    {"country": "BE", "slug": "seraing", "display_name": "Seraing", "region": "Liège"},
    {"country": "BE", "slug": "roeselare", "display_name": "Roeselare", "region": "West Flanders"},
    {"country": "BE", "slug": "mouscron", "display_name": "Mouscron", "region": "Hainaut"},
]
# fmt: on

SEO_COPY = {
    "de": {
        "title": "Mobile Klimaanlage auf Lager in {city} — KlimaRadar",
        "description": (
            "Finde mobile Klimaanlagen auf Lager in {city} und Umgebung. "
            "KlimaRadar vergleicht landesweite Verfügbarkeit, Preise und Lieferzeiten für ganz {country}."
        ),
        "h1": "Mobile Klimaanlage auf Lager in {city}",
        "intro": (
            "Wir verfolgen mobile Klimaanlagen, die online für die Lieferung nach {city} verfügbar sind. "
            "Vergleiche aktuelle Preise, Verfügbarkeit und Lieferoptionen von Händlern in ganz {country}."
        ),
        "popular_cities": "Beliebte Städte in {country}",
        "country_breadcrumb": "{country}",
    },
    "fr": {
        "title": "Climatiseur mobile en stock à {city} — KlimaRadar",
        "description": (
            "Trouvez des climatiseurs mobiles en stock à {city} et aux alentours. "
            "KlimaRadar compare la disponibilité, les prix et les délais de livraison pour toute la {country}."
        ),
        "h1": "Climatiseur mobile en stock à {city}",
        "intro": (
            "Nous suivons les climatiseurs mobiles disponibles en ligne pour livraison à {city}. "
            "Comparez les prix actuels, la disponibilité et les options de livraison des retailers en {country}."
        ),
        "popular_cities": "Villes populaires en {country}",
        "country_breadcrumb": "{country}",
    },
    "it": {
        "title": "Condizionatore portatile in stock a {city} — KlimaRadar",
        "description": (
            "Trova condizionatori portatili in stock a {city} e dintorni. "
            "KlimaRadar confronta disponibilità, prezzi e tempi di consegna in tutta la {country}."
        ),
        "h1": "Condizionatore portatile in stock a {city}",
        "intro": (
            "Monitoriamo i condizionatori portatili disponibili online per la consegna a {city}. "
            "Confronta prezzi attuali, disponibilità e opzioni di consegna dei retailer in {country}."
        ),
        "popular_cities": "Città popolari in {country}",
        "country_breadcrumb": "{country}",
    },
    "es": {
        "title": "Aire acondicionado portátil en stock en {city} — KlimaRadar",
        "description": (
            "Encuentra aires acondicionados portátiles en stock en {city} y alrededores. "
            "KlimaRadar compara disponibilidad, precios y plazos de entrega en toda {country}."
        ),
        "h1": "Aire acondicionado portátil en stock en {city}",
        "intro": (
            "Seguimos los aires acondicionados portátiles disponibles online para entrega en {city}. "
            "Compara precios actuales, disponibilidad y opciones de entrega de retailers en {country}."
        ),
        "popular_cities": "Ciudades populares en {country}",
        "country_breadcrumb": "{country}",
    },
    "nl": {
        "title": "Draagbare airconditioner op voorraad in {city} — KlimaRadar",
        "description": (
            "Vind draagbare airconditioners op voorraad in {city} en omgeving. "
            "KlimaRadar vergelijkt beschikbaarheid, prijzen en levertijden door heel {country}."
        ),
        "h1": "Draagbare airconditioner op voorraad in {city}",
        "intro": (
            "Wij volgen draagbare airconditioners die online beschikbaar zijn voor bezorging in {city}. "
            "Vergelijk actuele prijzen, beschikbaarheid en bezorgopties van retailers in {country}."
        ),
        "popular_cities": "Populaire steden in {country}",
        "country_breadcrumb": "{country}",
    },
    "be": {
        "title": "Draagbare airconditioner op voorraad in {city} — KlimaRadar",
        "description": (
            "Vind draagbare airconditioners op voorraad in {city} en omgeving. "
            "KlimaRadar vergelijkt beschikbaarheid, prijzen en levertijden door heel {country}."
        ),
        "h1": "Draagbare airconditioner op voorraad in {city}",
        "intro": (
            "Wij volgen draagbare airconditioners die online beschikbaar zijn voor bezorging in {city}. "
            "Vergelijk actuele prijzen, beschikbaarheid en bezorgopties van retailers in {country}."
        ),
        "popular_cities": "Populaire steden in {country}",
        "country_breadcrumb": "{country}",
    },
    "en": {
        "title": "Portable AC in stock in {city} — KlimaRadar",
        "description": (
            "Find portable air conditioners in stock in {city} and nearby. "
            "KlimaRadar compares availability, prices and delivery times across {country}."
        ),
        "h1": "Portable AC in stock in {city}",
        "intro": (
            "We track portable air conditioners available online for delivery to {city}. "
            "Compare current prices, availability and delivery options from retailers across {country}."
        ),
        "popular_cities": "Popular cities in {country}",
        "country_breadcrumb": "{country}",
    },
}


def _lang(country: str) -> str:
    return COUNTRY_LANGUAGES.get(country, "en")[:2]


def get_city_info(country: str, slug: str) -> dict | None:
    """Return city metadata for a normalized country code and city slug."""
    country_key = country.upper()
    slug_key = slug.lower()
    for city in CITY_METADATA:
        if city["country"] == country_key and city["slug"] == slug_key:
            return city
    return None


def list_cities_for_country(
    country: str, *, limit: int = 10, exclude_slug: str | None = None
) -> list[dict]:
    """Return up to ``limit`` cities for a country, optionally excluding one slug."""
    country_key = country.upper()
    excluded = exclude_slug.lower() if exclude_slug else None
    return [
        city
        for city in CITY_METADATA
        if city["country"] == country_key and city["slug"] != excluded
    ][:limit]


def get_seo_copy(country: str, city_info: dict) -> dict[str, str]:
    """Render localized SEO copy for a city landing page."""
    lang = _lang(country)
    templates = SEO_COPY.get(lang, SEO_COPY["en"])
    country_name = COUNTRY_NAMES.get(country.upper(), {}).get(lang, country.upper())
    city = city_info["display_name"]
    return {
        key: template.format(city=city, country=country_name)
        for key, template in templates.items()
    }


def get_sitemap_cities() -> list[tuple[str, str]]:
    """Return (country_lower, city_slug) tuples for every supported city."""
    return sorted((city["country"].lower(), city["slug"]) for city in CITY_METADATA)


def build_hreflang_alternates(
    html_lang: str, canonical_url: str, base_url: str
) -> list[tuple[str, str]]:
    """Return self-referencing hreflang + x-default for a page.

    ``canonical_url`` and ``base_url`` should be absolute and have no trailing slash.
    """
    base = base_url.rstrip("/")
    return [
        (html_lang, canonical_url),
        ("x-default", f"{base}/"),
    ]


def build_breadcrumb_jsonld(
    base_url: str, country: str, city_info: dict, seo_copy: dict
) -> dict:
    """Build a BreadcrumbList JSON-LD object for a city landing page."""
    base = base_url.rstrip("/")
    lang = _lang(country)
    country_name = COUNTRY_NAMES.get(country.upper(), {}).get(lang, country.upper())
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": f"{base}/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": country_name,
                "item": f"{base}/search?country={country.upper()}",
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": seo_copy["h1"],
                "item": f"{base}/{country.lower()}/{city_info['slug']}/portable-ac-in-stock",
            },
        ],
    }


def build_website_organization_jsonld(base_url: str) -> dict:
    """Build WebSite + Organization JSON-LD for the homepage."""
    base = base_url.rstrip("/")
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "name": "KlimaRadar",
                "url": f"{base}/",
                "description": (
                    "Find portable air conditioners in stock across Europe. "
                    "KlimaRadar tracks real-time AC availability, prices and delivery times across multiple European countries."
                ),
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": {
                        "@type": "EntryPoint",
                        "urlTemplate": f"{base}/search?country=DE&q={{search_term_string}}",
                    },
                    "query-input": "required name=search_term_string",
                },
            },
            {
                "@type": "Organization",
                "name": "KlimaRadar",
                "url": f"{base}/",
                "logo": f"{base}/static/img/favicon.svg",
            },
        ],
    }
