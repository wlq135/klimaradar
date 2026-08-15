"""City metadata and localized SEO copy for KlimaRadar city landing pages."""

from __future__ import annotations

COUNTRY_LANGUAGES = {
    "DE": "de-DE",
    "FR": "fr-FR",
    "IT": "it-IT",
    "ES": "es-ES",
    "NL": "nl-NL",
    "BE": "nl-BE",
    "GB": "en-GB",
}

COUNTRY_NAMES = {
    "DE": {"de": "Deutschland", "fr": "Allemagne", "en": "Germany"},
    "FR": {"de": "Frankreich", "fr": "France", "en": "France"},
    "IT": {"de": "Italien", "fr": "Italie", "en": "Italy", "it": "Italia"},
    "ES": {"de": "Spanien", "fr": "Espagne", "en": "Spain", "es": "España"},
    "NL": {"de": "Niederlande", "fr": "Pays-Bas", "en": "Netherlands", "nl": "Nederland"},
    "BE": {"de": "Belgien", "fr": "Belgique", "en": "Belgium", "nl": "België"},
    "GB": {"en": "United Kingdom", "de": "Vereinigtes Königreich", "fr": "Royaume-Uni"},
}

# Keep only the strongest city pages indexable. The remaining city URLs are
# still recognized, but they redirect to the country page to consolidate
# crawl budget and avoid large groups of near-duplicate thin pages.
SEO_CITY_LIMITS = {
    "DE": 8,
    "FR": 7,
    "IT": 6,
    "ES": 6,
    "NL": 6,
    "BE": 5,
    "GB": 6,
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

    # United Kingdom
    {"country": "GB", "slug": "london", "display_name": "London", "region": "Greater London"},
    {"country": "GB", "slug": "birmingham", "display_name": "Birmingham", "region": "West Midlands"},
    {"country": "GB", "slug": "manchester", "display_name": "Manchester", "region": "Greater Manchester"},
    {"country": "GB", "slug": "leeds", "display_name": "Leeds", "region": "West Yorkshire"},
    {"country": "GB", "slug": "glasgow", "display_name": "Glasgow", "region": "Scotland"},
    {"country": "GB", "slug": "liverpool", "display_name": "Liverpool", "region": "Merseyside"},
    {"country": "GB", "slug": "newcastle", "display_name": "Newcastle upon Tyne", "region": "Tyne and Wear"},
    {"country": "GB", "slug": "sheffield", "display_name": "Sheffield", "region": "South Yorkshire"},
    {"country": "GB", "slug": "bristol", "display_name": "Bristol", "region": "South West"},
    {"country": "GB", "slug": "nottingham", "display_name": "Nottingham", "region": "East Midlands"},
    {"country": "GB", "slug": "leicester", "display_name": "Leicester", "region": "East Midlands"},
    {"country": "GB", "slug": "coventry", "display_name": "Coventry", "region": "West Midlands"},
    {"country": "GB", "slug": "cardiff", "display_name": "Cardiff", "region": "Wales"},
    {"country": "GB", "slug": "belfast", "display_name": "Belfast", "region": "Northern Ireland"},
    {"country": "GB", "slug": "edinburgh", "display_name": "Edinburgh", "region": "Scotland"},
    {"country": "GB", "slug": "brighton", "display_name": "Brighton", "region": "East Sussex"},
    {"country": "GB", "slug": "southampton", "display_name": "Southampton", "region": "Hampshire"},
    {"country": "GB", "slug": "portsmouth", "display_name": "Portsmouth", "region": "Hampshire"},
    {"country": "GB", "slug": "plymouth", "display_name": "Plymouth", "region": "Devon"},
    {"country": "GB", "slug": "aberdeen", "display_name": "Aberdeen", "region": "Scotland"},
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
    """Return up to ``limit`` primary cities for a country.

    Primary cities are the first cities listed for each country in
    ``CITY_METADATA``. Keeping this set deliberately small prevents the public
    archive from generating dozens of near-duplicate pages with little unique
    content.
    """
    country_key = country.upper()
    excluded = exclude_slug.lower() if exclude_slug else None
    selected: list[dict] = []
    for city in CITY_METADATA:
        if city["country"] != country_key or city["slug"] == excluded:
            continue
        if len(selected) >= SEO_CITY_LIMITS.get(country_key, 10):
            break
        selected.append(city)
    return selected[:limit]


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
    """Return (country_lower, city_slug) tuples for indexable primary cities."""
    countries = sorted({city["country"] for city in CITY_METADATA})
    return sorted(
        (city["country"].lower(), city["slug"])
        for country in countries
        for city in list_cities_for_country(country, limit=SEO_CITY_LIMITS[country])
    )


def is_primary_city(country: str, slug: str) -> bool:
    """Return whether a city URL should remain indexable."""
    country_key = country.upper()
    slug_key = slug.lower()
    return any(
        city["slug"] == slug_key
        for city in list_cities_for_country(
            country_key, limit=SEO_CITY_LIMITS.get(country_key, 10)
        )
    )


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
                    "KlimaRadar tracks up-to-the-minute AC availability, prices and delivery times across multiple European countries."
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


# Localized FAQ Q&A for city landing pages.
FAQ_CONTENT: dict[str, list[dict[str, str]]] = {
    "de": [
        {"q": "Wann sind wieder mobile Klimaanlagen auf Lager?", "a": "Die Verfügbarkeit ändert sich ständig. KlimaRadar überwacht die Lagerbestände der wichtigsten Händler in {country} in Echtzeit. Aktivieren Sie einen Alarm, um sofort benachrichtigt zu werden."},
        {"q": "Wie viel Leistung (BTU) benötige ich für meinen Raum?", "a": "Als Faustregel: Für 25 m² etwa 7.000 BTU (2,0 kW), für 35 m² ca. 9.000 BTU und für 50 m² mindestens 12.000 BTU."},
        {"q": "Was kostet eine mobile Klimaanlage?", "a": "Mobile Klimaanlagen kosten in {country} typischerweise zwischen 250 € und 700 €. Vergleichen Sie die aktuellen Preise auf dieser Seite."},
        {"q": "Kann ich nach {city} liefern lassen?", "a": "Ja, alle hier gelisteten Händler liefern in ganz {country} inklusive {city}. Lieferzeit meist 1–5 Werktage."},
    ],
    "fr": [
        {"q": "Quand les climatiseurs mobiles seront-ils de nouveau en stock ?", "a": "La disponibilité change constamment. KlimaRadar surveille les stocks des principaux revendeurs en {country} en temps réel. Activez une alerte pour être prévenu."},
        {"q": "Quelle puissance (BTU) pour quelle surface ?", "a": "Comptez environ 7 000 BTU (2,0 kW) pour 25 m², 9 000 BTU pour 35 m² et au moins 12 000 BTU pour 50 m²."},
        {"q": "Combien coûte un climatiseur mobile ?", "a": "Les climatiseurs mobiles coûtent généralement entre 250 € et 700 € en {country}. Comparez les prix actuels sur cette page."},
        {"q": "Peut-on se faire livrer à {city} ?", "a": "Oui, tous les revendeurs listés livrent partout en {country} y compris à {city}. Délai généralement de 1 à 5 jours ouvrés."},
    ],
    "it": [
        {"q": "Quando saranno di nuovo disponibili i condizionatori portatili?", "a": "La disponibilità cambia continuamente. KlimaRadar monitora le scorte in {country} in tempo reale. Attiva un avviso per essere notificato."},
        {"q": "Quanti BTU servono per la mia stanza?", "a": "Circa 7.000 BTU (2,0 kW) per 25 m², 9.000 BTU per 35 m² e almeno 12.000 BTU per 50 m²."},
        {"q": "Quanto costa un condizionatore portatile?", "a": "I condizionatori portatili costano in {country} tipicamente tra 250 € e 700 €. Confronta i prezzi attuali su questa pagina."},
        {"q": "È possibile la consegna a {city}?", "a": "Sì, tutti i rivenditori consegnano in tutta la {country} inclusa {city}. Tempi di consegna 1–5 giorni lavorativi."},
    ],
    "es": [
        {"q": "¿Cuándo habrá aires acondicionados portátiles en stock?", "a": "La disponibilidad cambia constantemente. KlimaRadar monitoriza las existencias en {country} en tiempo real. Activa una alerta para recibir una notificación."},
        {"q": "¿Qué potencia (BTU) necesito para mi habitación?", "a": "Unos 7.000 BTU (2,0 kW) para 25 m², 9.000 BTU para 35 m² y al menos 12.000 BTU para 50 m²."},
        {"q": "¿Cuánto cuesta un aire acondicionado portátil?", "a": "Los aires acondicionados portátiles cuestan en {country} típicamente entre 250 € y 700 €. Compara los precios actuales en esta página."},
        {"q": "¿Se puede entregar en {city}?", "a": "Sí, todos los minoristas entregan en toda {country} incluida {city}. Plazo de entrega 1 a 5 días hábiles."},
    ],
    "nl": [
        {"q": "Wanneer zijn draagbare airconditioners weer op voorraad?", "a": "De beschikbaarheid verandert voortdurend. KlimaRadar houdt de voorraden in {country} realtime bij. Activeer een melding om direct een seintje te krijgen."},
        {"q": "Hoeveel BTU heb ik nodig voor mijn kamer?", "a": "Ongeveer 7.000 BTU (2,0 kW) voor 25 m², 9.000 BTU voor 35 m² en minstens 12.000 BTU voor 50 m²."},
        {"q": "Wat kost een draagbare airconditioner?", "a": "Draagbare airconditioners kosten in {country} doorgaans tussen 250 € en 700 €. Vergelijk de actuele prijzen op deze pagina."},
        {"q": "Kan er geleverd worden in {city}?", "a": "Ja, alle retailers leveren in heel {country} inclusief {city}. Levertijd meestal 1–5 werkdagen."},
    ],
    "en": [
        {"q": "When will portable air conditioners be back in stock?", "a": "Availability changes constantly. KlimaRadar tracks stock levels at major retailers in {country} in real time. Set up an alert to get notified the moment a unit becomes available."},
        {"q": "How many BTU do I need for my room?", "a": "As a rule of thumb: roughly 7,000 BTU (2.0 kW) for 25 m², 9,000 BTU for 35 m², and at least 12,000 BTU for 50 m²."},
        {"q": "How much does a portable air conditioner cost?", "a": "Portable air conditioners typically cost between 200 and 600 in {country} currency, depending on power and brand. Compare current prices on this page."},
        {"q": "Can I get delivery to {city}?", "a": "Yes, all retailers listed here deliver across {country} including {city}. Delivery time is usually 1–5 working days."},
    ],
}


def get_faq_content(country: str, city_info: dict) -> list[dict[str, str]]:
    """Return localized FAQ Q&A pairs for a city landing page."""
    lang = _lang(country)
    faqs = FAQ_CONTENT.get(lang, FAQ_CONTENT["en"])
    country_name = COUNTRY_NAMES.get(country.upper(), {}).get(lang, country.upper())
    city = city_info["display_name"]
    return [
        {"question": f["q"].format(city=city, country=country_name),
         "answer": f["a"].format(city=city, country=country_name)}
        for f in faqs
    ]


def build_faq_jsonld(faq_content: list[dict[str, str]]) -> dict:
    """Build a FAQPage JSON-LD object from FAQ content."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["answer"],
                },
            }
            for item in faq_content
        ],
    }
