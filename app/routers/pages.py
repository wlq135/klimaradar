"""Public HTML pages and affiliate redirect."""

import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.cloudflare import get_client_ip
from app.config import settings
from app.database import get_db
from app.models import ClickEvent, Listing, Product, Retailer
from app.rate_limit import admin_scrape_limiter
from app.schemas import SearchFilters, StatsOut
from app.seo import (
    CITY_METADATA,
    COUNTRY_NAMES,
    COUNTRY_LANGUAGES,
    build_breadcrumb_jsonld,
    build_faq_jsonld,
    build_hreflang_alternates,
    build_website_organization_jsonld,
    get_faq_content,
    get_city_info,
    get_seo_copy,
    get_sitemap_cities,
    list_cities_for_country,
    build_article_jsonld,
    get_country_guide,
    list_country_guides,
)
from app.services.affiliate import tag_url
from app.services.paddle import list_checkout_domains
from app.services.scraper import run_scrape
from app.templating import templates


def _client_ip(request: Request) -> str:
    return get_client_ip(request)


_DEFAULT_DESCRIPTION = (
    "Find portable air conditioners in stock across Europe. "
    "KlimaRadar tracks up-to-the-minute AC availability, prices and delivery times in Germany, France and beyond."
)

router = APIRouter()


_CITY_LINK_COPY = {
    "DE": ("Mobile Klimaanlage in {city}", "Aktuelle Geräte und Preise für {city} ansehen."),
    "FR": ("Climatiseur mobile à {city}", "Voir les appareils disponibles et les prix à {city}."),
    "IT": ("Climatizzatore portatile a {city}", "Vedi disponibilità e prezzi a {city}."),
    "ES": ("Aire acondicionado portátil en {city}", "Consulta disponibilidad y precios en {city}."),
    "NL": ("Draagbare airconditioner in {city}", "Bekijk beschikbaarheid en prijzen in {city}."),
    "BE": ("Draagbare airconditioner in {city}", "Bekijk beschikbaarheid en prijzen in {city}."),
    "GB": ("Portable AC in {city}", "See in-stock units and prices in {city}."),
}




_COUNTRY_SEARCH_COPY = {
    "DE": {
        "title": "Mobile Klimaanlage auf Lager in {place} — KlimaRadar",
        "h1": "Mobile Klimaanlage auf Lager in {place}",
        "intro": "Vergleiche aktuelle Preise, Verfügbarkeit und Lieferzeiten mobiler Klimaanlagen in {place}.",
    },
    "FR": {
        "title": "Climatiseur mobile en stock à {place} — KlimaRadar",
        "h1": "Climatiseur mobile en stock à {place}",
        "intro": "Comparez les prix, la disponibilité et les délais de livraison des climatiseurs mobiles à {place}.",
    },
    "IT": {
        "title": "Climatizzatore portatile disponibile a {place} — KlimaRadar",
        "h1": "Climatizzatore portatile disponibile a {place}",
        "intro": "Confronta prezzi, disponibilità e tempi di consegna dei climatizzatori portatili a {place}.",
    },
    "ES": {
        "title": "Aire acondicionado portátil en stock en {place} — KlimaRadar",
        "h1": "Aire acondicionado portátil en stock en {place}",
        "intro": "Compara precios, disponibilidad y tiempos de entrega de aire acondicionado portátil en {place}.",
    },
    "NL": {
        "title": "Draagbare airconditioner op voorraad in {place} — KlimaRadar",
        "h1": "Draagbare airconditioner op voorraad in {place}",
        "intro": "Vergelijk prijzen, beschikbaarheid en levertijden van draagbare airconditioners in {place}.",
    },
    "BE": {
        "title": "Draagbare airconditioner op voorraad in {place} — KlimaRadar",
        "h1": "Draagbare airconditioner op voorraad in {place}",
        "intro": "Vergelijk prijzen, beschikbaarheid en levertijden van draagbare airconditioners in {place}.",
    },
    "GB": {
        "title": "Portable AC in stock in {place} — KlimaRadar",
        "h1": "Portable AC in stock in {place}",
        "intro": "Compare live portable air conditioner prices, availability and delivery times in {place}.",
    },
}
_LISTING_UI_COPY = {
    "de": {
        "result_found": "Ergebnisse gefunden",
        "create_alert": "+ Benachrichtigung erstellen",
        "create_alert_long": "Benachrichtigung erstellen",
        "trust_intro": "Wir vergleichen Preise bei Amazon, MediaMarkt, Boulanger, Darty und mehr.",
        "affiliate_note": "Affiliate-Links können uns eine Provision einbringen.",
        "stock_labels": {
            "in_stock": "Auf Lager",
            "low_stock": "Geringer Bestand",
            "out_of_stock": "Nicht auf Lager",
            "back_order": "Vorbestellung",
            "pre_order": "Vorbestellung",
            "unknown": "Unbekannt",
        },
        "unconfirmed": "unbestätigt",
        "delivery": "Lieferung in",
        "delivery_days": "Tagen",
        "delivery_day": "Tag",
        "unknown_brand": "Unbekannte Marke",
        "high_demand": "⚡ Gefragt — Bestand ändert sich stündlich",
        "buy_prefix": "Kaufen bei",
        "no_matches_title": "Zurzeit keine passenden Geräte auf Lager.",
        "no_matches_body": "Erstelle eine Benachrichtigung und wir informieren dich, sobald ein Gerät verfügbar ist.",
        "previous": "Zurück",
        "next": "Weiter",
        "page": "Seite",
        "of": "von",
    },
    "fr": {
        "result_found": "résultats trouvés",
        "create_alert": "+ Créer une alerte",
        "create_alert_long": "Créer une alerte",
        "trust_intro": "Nous comparons les prix d'Amazon, MediaMarkt, Boulanger, Darty et d'autres.",
        "affiliate_note": "Les liens affiliés peuvent nous rapporter une commission.",
        "stock_labels": {
            "in_stock": "En stock",
            "low_stock": "Stock limité",
            "out_of_stock": "Rupture de stock",
            "back_order": "Précommande",
            "pre_order": "Précommande",
            "unknown": "Inconnu",
        },
        "unconfirmed": "non confirmé",
        "delivery": "Livraison en",
        "delivery_days": "jours",
        "delivery_day": "jour",
        "unknown_brand": "Marque inconnue",
        "high_demand": "⚡ Forte demande — le stock change toutes les heures",
        "buy_prefix": "Acheter chez",
        "no_matches_title": "Aucun appareil correspondant en stock pour le moment.",
        "no_matches_body": "Créez une alerte et nous vous informerons dès qu'un appareil sera disponible.",
        "previous": "Précédent",
        "next": "Suivant",
        "page": "Page",
        "of": "sur",
    },
    "it": {
        "result_found": "risultati trovati",
        "create_alert": "+ Crea un avviso",
        "create_alert_long": "Crea un avviso",
        "trust_intro": "Confrontiamo i prezzi di Amazon, MediaMarkt, Boulanger, Darty e altri.",
        "affiliate_note": "I link affiliati possono farci guadagnare una commissione.",
        "stock_labels": {
            "in_stock": "Disponibile",
            "low_stock": "Scorte limitate",
            "out_of_stock": "Non disponibile",
            "back_order": "Ordine differito",
            "pre_order": "Preordine",
            "unknown": "Sconosciuto",
        },
        "unconfirmed": "non confermato",
        "delivery": "Consegna in",
        "delivery_days": "giorni",
        "delivery_day": "giorno",
        "unknown_brand": "Marca sconosciuta",
        "high_demand": "⚡ Alta richiesta — la disponibilità cambia ogni ora",
        "buy_prefix": "Acquista su",
        "no_matches_title": "Nessun dispositivo corrispondente disponibile al momento.",
        "no_matches_body": "Crea un avviso e ti informeremo non appena un dispositivo sarà disponibile.",
        "previous": "Precedente",
        "next": "Successiva",
        "page": "Pagina",
        "of": "di",
    },
    "es": {
        "result_found": "resultados encontrados",
        "create_alert": "+ Crear alerta",
        "create_alert_long": "Crear alerta",
        "trust_intro": "Comparamos precios de Amazon, MediaMarkt, Boulanger, Darty y más.",
        "affiliate_note": "Los enlaces de afiliados pueden generarnos una comisión.",
        "stock_labels": {
            "in_stock": "En stock",
            "low_stock": "Poco stock",
            "out_of_stock": "Agotado",
            "back_order": "Pedido anticipado",
            "pre_order": "Reserva",
            "unknown": "Desconocido",
        },
        "unconfirmed": "sin confirmar",
        "delivery": "Entrega en",
        "delivery_days": "días",
        "delivery_day": "día",
        "unknown_brand": "Marca desconocida",
        "high_demand": "⚡ Alta demanda — el stock cambia cada hora",
        "buy_prefix": "Comprar en",
        "no_matches_title": "No hay dispositivos coincidentes en stock ahora mismo.",
        "no_matches_body": "Crea una alerta y te avisaremos en cuanto haya uno disponible.",
        "previous": "Anterior",
        "next": "Siguiente",
        "page": "Página",
        "of": "de",
    },
    "nl": {
        "result_found": "resultaten gevonden",
        "create_alert": "+ Alert aanmaken",
        "create_alert_long": "Alert aanmaken",
        "trust_intro": "We vergelijken prijzen van Amazon, MediaMarkt, Boulanger, Darty en meer.",
        "affiliate_note": "Affiliatelinks kunnen ons een commissie opleveren.",
        "stock_labels": {
            "in_stock": "Op voorraad",
            "low_stock": "Beperkte voorraad",
            "out_of_stock": "Uitverkocht",
            "back_order": "Voorbestelling",
            "pre_order": "Voorbestelling",
            "unknown": "Onbekend",
        },
        "unconfirmed": "onbevestigd",
        "delivery": "Levering in",
        "delivery_days": "dagen",
        "delivery_day": "dag",
        "unknown_brand": "Onbekend merk",
        "high_demand": "⚡ Veel gevraagd — voorraad verandert per uur",
        "buy_prefix": "Koop bij",
        "no_matches_title": "Momenteel geen passende apparaten op voorraad.",
        "no_matches_body": "Maak een alert aan en we mailen zodra er één beschikbaar is.",
        "previous": "Vorige",
        "next": "Volgende",
        "page": "Pagina",
        "of": "van",
    },
    "en": {
        "result_found": "results found",
        "create_alert": "+ Create alert",
        "create_alert_long": "Create an alert",
        "trust_intro": "We compare prices across Amazon, MediaMarkt, Boulanger, Darty and more.",
        "affiliate_note": "Affiliate links may earn us a commission.",
        "stock_labels": {
            "in_stock": "In Stock",
            "low_stock": "Low Stock",
            "out_of_stock": "Out of Stock",
            "back_order": "Back Order",
            "pre_order": "Pre-Order",
            "unknown": "Unknown",
        },
        "unconfirmed": "unconfirmed",
        "delivery": "Delivery in",
        "delivery_days": "days",
        "delivery_day": "day",
        "unknown_brand": "Unknown brand",
        "high_demand": "⚡ In high demand — stock changes hourly",
        "buy_prefix": "Buy at",
        "no_matches_title": "No matching units in stock right now.",
        "no_matches_body": "Create an alert and we'll email you as soon as one becomes available.",
        "previous": "Previous",
        "next": "Next",
        "page": "Page",
        "of": "of",
    },
}


def _listing_ui(country: str) -> dict:
    language = COUNTRY_LANGUAGES.get(country.upper(), "en")[:2]
    return _LISTING_UI_COPY.get(language, _LISTING_UI_COPY["en"])



_FRESHNESS_COPY = {
    "de": ("Verfügbarkeit unbekannt", "Gerade überprüft", "Vor {hours} Std. überprüft", "Vor 1 Tag überprüft", "Vor {days} Tagen überprüft", "Zuletzt geprüft vor {days} Tagen"),
    "fr": ("Disponibilité inconnue", "Vérifié à l'instant", "Vérifié il y a {hours} h", "Vérifié il y a 1 jour", "Vérifié il y a {days} jours", "Dernière vérification il y a {days} jours"),
    "it": ("Disponibilità sconosciuta", "Verificato ora", "Verificato {hours} ore fa", "Verificato 1 giorno fa", "Verificato {days} giorni fa", "Ultimo controllo {days} giorni fa"),
    "es": ("Disponibilidad desconocida", "Verificado ahora mismo", "Verificado hace {hours} h", "Verificado hace 1 día", "Verificado hace {days} días", "Última comprobación hace {days} días"),
    "nl": ("Beschikbaarheid onbekend", "Zojuist gecontroleerd", "{hours} uur geleden gecontroleerd", "1 dag geleden gecontroleerd", "{days} dagen geleden gecontroleerd", "Laatst gecontroleerd {days} dagen geleden"),
    "en": ("Availability unknown", "Verified just now", "Verified {hours}h ago", "Verified 1d ago", "Verified {days}d ago", "Checked {days}d ago"),
}


def _freshness(seen_at, country: str = "EN") -> tuple[str, bool]:
    """Return a localized (label, is_stale) pair relative to now."""
    lang = COUNTRY_LANGUAGES.get(country.upper(), "en")[:2]
    unknown, now, hours, one_day, days, stale = _FRESHNESS_COPY.get(lang, _FRESHNESS_COPY["en"])
    if not seen_at:
        return unknown, True
    if seen_at.tzinfo is None:
        seen_at = seen_at.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - seen_at
    elapsed_hours = delta.total_seconds() / 3600
    if elapsed_hours < 1:
        return now, False
    if elapsed_hours < 24:
        return hours.format(hours=int(elapsed_hours)), False
    elapsed_days = int(elapsed_hours // 24)
    if elapsed_days == 1:
        return one_day, False
    if elapsed_days <= 2:
        return days.format(days=elapsed_days), False
    return stale.format(days=elapsed_days), True


def _template_context(request: Request, **extra) -> dict:
    base = settings.base_url.rstrip("/")
    extra.setdefault("canonical_url", base + request.url.path)
    extra.setdefault("settings", settings)
    return extra


def _hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()[:32]


def _retailer_hostname(retailer: Retailer) -> str:
    """Return the normalized hostname for a retailer domain."""
    hostname = urlparse(retailer.domain).netloc or retailer.domain
    return hostname.lower().removeprefix("www.")


def _is_safe_redirect_target(target: str, retailer: Retailer) -> bool:
    """Ensure the redirect target stays within the retailer's domain."""
    try:
        parsed = urlparse(target)
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    target_host = (parsed.netloc or "").lower().removeprefix("www.")
    retailer_host = _retailer_hostname(retailer)
    if not retailer_host:
        return False
    return target_host == retailer_host or target_host.endswith("." + retailer_host)


def _empty_to_none(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


def _int_or_none(value: str | None) -> int | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _float_or_none(value: str | None) -> float | None:
    value = _empty_to_none(value)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _bool_from_param(value: str | None) -> bool:
    if value is None:
        return False
    return value.lower() in ("true", "1", "on", "yes")


@router.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def index(request: Request, session: AsyncSession = Depends(get_db)):
    stats = await _get_stats(session)
    base = settings.base_url.rstrip("/")
    canonical_url = f"{base}/"
    html_lang = "en"
    hreflang_alternates = build_hreflang_alternates(html_lang, canonical_url, base)
    structured_data = build_website_organization_jsonld(base)

    country_order = ["DE", "FR", "IT", "ES", "NL", "BE", "GB"]
    popular_searches = []
    for code in country_order:
        cities = [c for c in CITY_METADATA if c["country"] == code]
        if not cities:
            continue
        guide = get_country_guide(code)
        popular_searches.append(
            {
                "code": code,
                "name": COUNTRY_NAMES.get(code, {}).get("en", code),
                "guide_path": guide["path"],
                "guide_title": guide["card_title"],
                "guide_intro": guide["card_body"],
                "cities": [
                    {
                        **city,
                        "search_title": _CITY_LINK_COPY[code][0].format(city=city["display_name"]),
                        "search_intro": _CITY_LINK_COPY[code][1].format(city=city["display_name"]),
                    }
                    for city in cities
                ],
            }
        )

    return templates.TemplateResponse(
        request,
        "index.html",
        _template_context(
            request,
            title="KlimaRadar — Find portable ACs in stock across Europe",
            description=_DEFAULT_DESCRIPTION,
            html_lang=html_lang,
            hreflang_alternates=hreflang_alternates,
            structured_data=json.dumps(structured_data, ensure_ascii=False),
            stats=stats,
            popular_searches=popular_searches,
            canonical_url=canonical_url,
        ),
    )


@router.api_route("/pricing", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def pricing(request: Request):
    return templates.TemplateResponse(
        request,
        "pricing.html",
        _template_context(
            request,
            title="Pricing — KlimaRadar",
            description="Get unlimited AC stock alerts for a one-time €3 payment. Free tier includes 1 alert.",
        ),
    )


@router.api_route("/robots.txt", methods=["GET", "HEAD"], response_class=PlainTextResponse)
async def robots_txt():
    base = settings.base_url.rstrip("/")
    return PlainTextResponse(
        f"User-agent: *\nDisallow: /api/\nDisallow: /go/\nAllow: /\nSitemap: {base}/sitemap.xml",
        media_type="text/plain",
    )


@router.api_route(
    "/indexnow-{key}.txt",
    methods=["GET", "HEAD"],
    response_class=PlainTextResponse,
)
async def indexnow_key_file(key: str):
    """Serve the key file required to submit URLs through IndexNow."""
    if not settings.indexnow_key or key != settings.indexnow_key:
        raise HTTPException(status_code=404, detail="Not found")
    return PlainTextResponse(settings.indexnow_key, media_type="text/plain")


@router.api_route("/sitemap.xml", methods=["GET", "HEAD"])
async def sitemap_xml():
    base = settings.base_url.rstrip("/")
    today = datetime.now(timezone.utc).date().isoformat()

    urls = [
        (f"{base}/", "1.0"),
        (f"{base}/search?country=DE", "0.8"),
        (f"{base}/search?country=FR", "0.8"),
        (f"{base}/search?country=IT", "0.8"),
        (f"{base}/search?country=ES", "0.8"),
        (f"{base}/search?country=NL", "0.8"),
        (f"{base}/search?country=BE", "0.8"),
        (f"{base}/search?country=GB", "0.8"),
        (f"{base}/pricing", "0.8"),
        (f"{base}/privacy", "0.5"),
        (f"{base}/terms", "0.5"),
        (f"{base}/refunds", "0.5"),
        (f"{base}/about", "0.5"),
    ]
    for country, city in get_sitemap_cities():
        urls.append((f"{base}/{country}/{city}/portable-ac-in-stock", "0.7"))
    for guide in list_country_guides():
        urls.append((f"{base}{guide['path']}", "0.8"))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, priority in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{today}</lastmod>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    return Response(content="\n".join(lines), media_type="application/xml")


@router.api_route("/privacy", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse(
        request,
        "privacy.html",
        _template_context(
            request,
            title="Privacy Policy — KlimaRadar",
            description="Read KlimaRadar's privacy policy, cookie usage, email practices, affiliate disclosure and your GDPR rights.",
        ),
    )


@router.api_route("/about", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        request,
        "about.html",
        _template_context(
            request,
            title="About KlimaRadar",
            description="Learn what KlimaRadar does: up-to-the-minute portable AC stock and price tracking across Europe.",
        ),
    )


@router.api_route("/terms", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse(
        request,
        "terms.html",
        _template_context(
            request,
            title="Terms of Service — KlimaRadar",
            description="Read KlimaRadar's terms of service and affiliate disclosure.",
        ),
    )


@router.api_route("/refunds", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def refunds(request: Request):
    return templates.TemplateResponse(
        request,
        "refunds.html",
        _template_context(
            request,
            title="Refund Policy — KlimaRadar",
            description="Read KlimaRadar's refund policy for the lifetime upgrade.",
        ),
    )


@router.api_route("/search", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def search(
    request: Request,
    country: str = "DE",
    city_raw: str | None = Query(None, alias="city"),
    product_type_raw: str | None = Query(None, alias="product_type"),
    min_btu_raw: str | None = Query(None, alias="min_btu"),
    max_price_raw: str | None = Query(None, alias="max_price"),
    in_stock_only_raw: str | None = Query(None, alias="in_stock_only"),
    q_raw: str | None = Query(None, alias="q"),
    page_raw: str | None = Query(None, alias="page"),
    session: AsyncSession = Depends(get_db),
):
    _PAGE_SIZE = 24
    city = _empty_to_none(city_raw)
    product_type = _empty_to_none(product_type_raw) or "portable"
    q = _empty_to_none(q_raw)
    filters = SearchFilters(
        country=country,
        city=city,
        product_type=product_type,
        min_btu=_int_or_none(min_btu_raw),
        max_price=_float_or_none(max_price_raw),
        in_stock_only=_bool_from_param(in_stock_only_raw),
        q=q,
    )
    page = max(1, int(page_raw) if page_raw and page_raw.isdigit() else 1)
    offset = (page - 1) * _PAGE_SIZE
    listings, total = await _fetch_filtered_listings(
        session, filters, limit=_PAGE_SIZE, offset=offset
    )
    total_pages = (total + _PAGE_SIZE - 1) // _PAGE_SIZE if total else 0

    country_upper = country.upper()
    base = settings.base_url.rstrip("/")

    # Filtered search pages (any param beyond a bare country) must not be
    # indexed: they create thousands of near-duplicate URLs that waste crawl
    # budget. Canonical points to the clean country-level page instead.
    has_filter_params = bool(
        q
        or city
        or _int_or_none(min_btu_raw)
        or _float_or_none(max_price_raw)
        or _bool_from_param(in_stock_only_raw)
        or product_type != "portable"
    )
    if has_filter_params:
        canonical_url = f"{base}/search?country={country}"
        noindex = True
    else:
        query_suffix = f"?{request.url.query}" if request.url.query else ""
        canonical_url = f"{base}{request.url.path}{query_suffix}"
        noindex = False
    html_lang = COUNTRY_LANGUAGES.get(country_upper, "en")
    hreflang_alternates = build_hreflang_alternates(html_lang, canonical_url, base)

    language = COUNTRY_LANGUAGES.get(country_upper, "en")[:2]
    country_name = COUNTRY_NAMES.get(country_upper, {}).get(
        language, COUNTRY_NAMES.get(country_upper, {}).get("en", country_upper)
    )
    search_copy = _COUNTRY_SEARCH_COPY.get(
        country_upper,
        {
            "title": "Portable AC in stock in {place} — KlimaRadar",
            "h1": "Portable AC in stock in {place}",
            "intro": "Compare live portable air conditioner prices, availability and delivery times in {place}.",
        },
    )
    place = city or country_name
    title = search_copy["title"].format(place=place)
    description = search_copy["intro"].format(place=place)
    search_h1 = search_copy["h1"].format(place=place)
    search_other_cities = list_cities_for_country(country_upper, limit=50)
    search_cities_title = "Other cities in " + COUNTRY_NAMES.get(country_upper, {}).get("en", country_upper)
    listing_ui = _listing_ui(country_upper)
    country_guide = get_country_guide(country_upper)
    if country_guide:
        search_cities_title = country_guide["cities_title"]
    faq_content = country_guide["faqs"] if country_guide else None
    faq_jsonld = build_faq_jsonld(faq_content) if country_guide else None
    return templates.TemplateResponse(
        request,
        "search.html",
        _template_context(
            request,
            title=title,
            description=description,
            html_lang=html_lang,
            hreflang_alternates=hreflang_alternates,
            canonical_url=canonical_url,
            h1=search_h1,
            page_intro=description,
            listings=listings,
            filters=filters.model_dump(),
            total=total,
            noindex=noindex,
            current_page=page,
            total_pages=total_pages,
            has_prev=page > 1,
            has_next=page < total_pages,
            other_cities=search_other_cities,
            popular_cities_title=search_cities_title,
            listing_ui=listing_ui,
            country_guide=country_guide,
            faq_title=country_guide["faq_title"] if country_guide else None,
            faq_content=faq_content,
            faq_jsonld=json.dumps(faq_jsonld, ensure_ascii=False) if faq_jsonld else None,
        ),
    )


@router.api_route(
    "/guides/{country}/portable-air-conditioner",
    methods=["GET", "HEAD"],
    response_class=HTMLResponse,
)
async def country_buying_guide(request: Request, country: str):
    guide = get_country_guide(country)
    if guide is None:
        raise HTTPException(status_code=404, detail="Guide not found")

    base = settings.base_url.rstrip("/")
    canonical_url = f"{base}{guide['path']}"
    hreflang_alternates = build_hreflang_alternates(
        guide["html_lang"], canonical_url, base
    )
    article_jsonld = build_article_jsonld(base, guide)
    faq_jsonld = build_faq_jsonld(guide["faqs"])
    top_cities = list_cities_for_country(guide["country"], limit=9)
    other_guides = list_country_guides(exclude=guide["country"])
    listing_ui = _listing_ui(guide["country"])

    return templates.TemplateResponse(
        request,
        "guide.html",
        _template_context(
            request,
            title=guide["title"],
            description=guide["description"],
            html_lang=guide["html_lang"],
            hreflang_alternates=hreflang_alternates,
            canonical_url=canonical_url,
            guide=guide,
            top_cities=top_cities,
            other_guides=other_guides,
            listing_ui=listing_ui,
            article_jsonld=json.dumps(article_jsonld, ensure_ascii=False),
            faq_jsonld=json.dumps(faq_jsonld, ensure_ascii=False),
        ),
    )


@router.api_route(
    "/{country}/{city}/portable-ac-in-stock",
    methods=["GET", "HEAD"],
    response_class=HTMLResponse,
)
async def city_seo_page(
    request: Request,
    country: str,
    city: str,
    session: AsyncSession = Depends(get_db),
):
    country_code = country.upper()
    city_info = get_city_info(country_code, city)
    if city_info is None:
        raise HTTPException(status_code=404, detail="City not found")

    filters = SearchFilters(
        country=country_code,
        city=city_info["display_name"],
        product_type="portable",
    )
    listings, _ = await _fetch_filtered_listings(session, filters)
    seo_copy = get_seo_copy(country_code, city_info)

    base = settings.base_url.rstrip("/")
    canonical_url = f"{base}/{country_code.lower()}/{city_info['slug']}/portable-ac-in-stock"
    html_lang = COUNTRY_LANGUAGES.get(country_code, "en")
    hreflang_alternates = build_hreflang_alternates(html_lang, canonical_url, base)
    breadcrumb_jsonld = build_breadcrumb_jsonld(base, country_code, city_info, seo_copy)
    faq_content = get_faq_content(country_code, city_info)
    faq_jsonld = build_faq_jsonld(faq_content)
    other_cities = list_cities_for_country(country_code, limit=50, exclude_slug=city_info["slug"])
    listing_ui = _listing_ui(country_code)
    country_guide = get_country_guide(country_code)

    return templates.TemplateResponse(
        request,
        "search.html",
        _template_context(
            request,
            title=seo_copy["title"],
            description=seo_copy["description"],
            html_lang=html_lang,
            hreflang_alternates=hreflang_alternates,
            canonical_url=canonical_url,
            h1=seo_copy["h1"],
            page_intro=seo_copy["intro"],
            popular_cities_title=seo_copy["popular_cities"],
            other_cities=other_cities,
            listing_ui=listing_ui,
            country_guide=country_guide,
            breadcrumb_jsonld=json.dumps(breadcrumb_jsonld, ensure_ascii=False),
            faq_jsonld=json.dumps(faq_jsonld, ensure_ascii=False),
            faq_content=faq_content,
            listings=listings,
            filters=filters.model_dump(),
            total=len(listings),
            seo_mode=True,
        ),
    )


@router.get("/go/{listing_id}")
async def affiliate_redirect(
    request: Request,
    listing_id: int,
    session: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Listing)
        .options(selectinload(Listing.retailer))
        .where(Listing.id == listing_id)
    )
    result = await session.execute(stmt)
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    click = ClickEvent(
        listing_id=listing.id,
        source=request.query_params.get("source"),
        user_agent=request.headers.get("user-agent"),
        ip_hash=_hash_ip(_client_ip(request)),
    )
    session.add(click)
    await session.commit()

    target = tag_url(listing.retailer.domain, listing.affiliate_url or listing.url)
    if not target or not _is_safe_redirect_target(target, listing.retailer):
        target = tag_url(listing.retailer.domain, listing.url)
    if not target or not _is_safe_redirect_target(target, listing.retailer):
        logger = logging.getLogger(__name__)
        logger.error(
            "Unsafe redirect target for listing %s (retailer %s): %s",
            listing.id,
            listing.retailer.domain,
            target,
        )
        raise HTTPException(status_code=400, detail="Invalid redirect target")

    return RedirectResponse(url=target)


@router.get("/api/health")
async def health(session: AsyncSession = Depends(get_db)):
    email_backend_name = "unknown"
    email_error = None
    try:
        from app.services.alerter import get_email_backend, _last_brevo_error, _last_email_error
        email_backend_name = get_email_backend().__class__.__name__
        if _last_email_error:
            email_error = _last_email_error
        elif _last_brevo_error:
            email_error = _last_brevo_error
    except Exception:
        pass

    try:
        listing_count = await session.scalar(select(func.count(Listing.id)))
        retailer_count = await session.scalar(select(func.count(Retailer.id)))
        return {
            "status": "ok",
            "listings": listing_count,
            "retailers": retailer_count,
            "email_backend": email_backend_name,
            "email_error": email_error,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")


@router.post("/api/admin/scrape")
async def trigger_scrape(
    request: Request,
    country: str | None = None,
    x_admin_api_key: str | None = Header(None, alias="X-Admin-API-Key"),
):
    """Manual trigger for the scraper. Requires a non-empty ADMIN_API_KEY."""
    await admin_scrape_limiter.check(_client_ip(request))
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=503, detail="Admin endpoint is not configured"
        )
    if not x_admin_api_key or not secrets.compare_digest(
        x_admin_api_key, settings.admin_api_key
    ):
        raise HTTPException(status_code=403, detail="Invalid admin API key")
    results = await run_scrape(country=country)
    return {"results": results}


@router.get("/api/admin/paddle/checkout-domains")
async def paddle_checkout_domains(
    request: Request,
    x_admin_api_key: str | None = Header(None, alias="X-Admin-API-Key"),
):
    """Check Paddle checkout domain approval status. Requires admin API key."""
    await admin_scrape_limiter.check(_client_ip(request))
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=503, detail="Admin endpoint is not configured"
        )
    if not x_admin_api_key or not secrets.compare_digest(
        x_admin_api_key, settings.admin_api_key
    ):
        raise HTTPException(status_code=403, detail="Invalid admin API key")
    try:
        domains = await list_checkout_domains()
    except RuntimeError as exc:
        logger.warning("Failed to fetch Paddle checkout domains: %s", exc)
        raise HTTPException(
            status_code=502, detail="Unable to fetch domain status from Paddle"
        ) from exc
    return {"environment": settings.paddle_environment, "domains": domains}


async def _get_stats(session: AsyncSession) -> StatsOut:
    total = await session.scalar(select(func.count(Listing.id)))
    # Count only listings verified in the last 48h so the
    # headline "In stock now" number reflects real availability, not stale
    # data that may already be gone from the retailer.
    fresh_cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    in_stock = await session.scalar(
        select(func.count(Listing.id)).where(
            Listing.stock_status == "in_stock",
            Listing.last_seen_at >= fresh_cutoff,
        )
    )
    countries = (
        await session.scalars(select(Listing.country).distinct())
    ).all()
    from app.models import AlertSubscription

    active_subs = await session.scalar(
        select(func.count(AlertSubscription.id)).where(
            AlertSubscription.active.is_(True), AlertSubscription.verified.is_(True)
        )
    )
    return StatsOut(
        total_listings=total or 0,
        in_stock_listings=in_stock or 0,
        active_subscriptions=active_subs or 0,
        countries=[c for c in countries if c],
    )


async def _fetch_filtered_listings(
    session: AsyncSession,
    filters: SearchFilters,
    *,
    limit: int | None = None,
    offset: int = 0,
) -> tuple[list[dict], int]:
    stmt = (
        select(Listing, Product, Retailer)
        .join(Product, Listing.product_id == Product.id)
        .join(Retailer, Listing.retailer_id == Retailer.id)
        .where(Listing.country == filters.country)
        .order_by(
            # In-stock first. Amazon follows because it has the strongest
            # purchase-trust signal and directly supports the Associates goal;
            # then freshest data and cheapest price.
            (Listing.stock_status == "in_stock").desc(),
            Retailer.domain.ilike("amazon.%").desc(),
            Listing.last_seen_at.desc().nullslast(),
            Listing.price.asc().nullslast(),
        )
    )

    if filters.product_type:
        stmt = stmt.where(Product.product_type == filters.product_type)
    if filters.min_btu:
        stmt = stmt.where(
            (Product.btu_max >= filters.min_btu) | (Product.btu_max.is_(None))
        )
    if filters.max_price:
        stmt = stmt.where(
            (Listing.price <= filters.max_price) | (Listing.price.is_(None))
        )
    if filters.in_stock_only:
        stmt = stmt.where(Listing.stock_status == "in_stock")
    if filters.q:
        like = f"%{filters.q}%"
        stmt = stmt.where(Product.name.ilike(like))

    # Count total matching rows (before pagination).
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = (await session.execute(count_stmt)).scalar() or 0

    if limit is not None:
        stmt = stmt.limit(limit).offset(offset)

    result = await session.execute(stmt)
    rows = []
    for listing, product, retailer in result.unique().all():
        rows.append(
            {
                "id": listing.id,
                "name": product.name,
                "brand": product.brand,
                "price": listing.price,
                "currency": listing.currency,
                "stock_status": listing.stock_status,
                "delivery_days": listing.delivery_days,
                "image_url": product.image_url,
                "retailer": retailer.name,
                "country": listing.country,
                "btu_min": product.btu_min,
                "btu_max": product.btu_max,
                "affiliate_url": f"/go/{listing.id}",
                "freshness_label": _freshness(listing.last_seen_at, listing.country)[0],
                "stale": _freshness(listing.last_seen_at, listing.country)[1],
            }
        )
    return rows, total_count
