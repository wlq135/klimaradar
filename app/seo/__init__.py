"""SEO helpers for KlimaRadar."""

from app.seo.cities import (
    CITY_METADATA,
    COUNTRY_LANGUAGES,
    COUNTRY_NAMES,
    SEO_COPY,
    build_breadcrumb_jsonld,
    build_hreflang_alternates,
    build_website_organization_jsonld,
    get_city_info,
    get_seo_copy,
    get_sitemap_cities,
    list_cities_for_country,
)

__all__ = [
    "CITY_METADATA",
    "COUNTRY_LANGUAGES",
    "COUNTRY_NAMES",
    "SEO_COPY",
    "build_breadcrumb_jsonld",
    "build_hreflang_alternates",
    "build_website_organization_jsonld",
    "get_city_info",
    "get_seo_copy",
    "get_sitemap_cities",
    "list_cities_for_country",
]
