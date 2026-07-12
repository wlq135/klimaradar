"""City metadata and localized SEO copy for KlimaRadar city landing pages."""

from __future__ import annotations

COUNTRY_LANGUAGES = {
    "DE": "de-DE",
    "FR": "fr-FR",
}

COUNTRY_NAMES = {
    "DE": {"de": "Deutschland", "fr": "Allemagne", "en": "Germany"},
    "FR": {"de": "Frankreich", "fr": "France", "en": "France"},
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
    templates = SEO_COPY.get(lang, SEO_COPY["de"])
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
                    "KlimaRadar tracks real-time AC availability, prices and delivery times in Germany and France."
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
