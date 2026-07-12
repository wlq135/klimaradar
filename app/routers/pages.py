"""Public HTML pages and affiliate redirect."""

import hashlib
import json
import logging
from datetime import datetime, timezone
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
    COUNTRY_LANGUAGES,
    build_breadcrumb_jsonld,
    build_hreflang_alternates,
    build_website_organization_jsonld,
    get_city_info,
    get_seo_copy,
    get_sitemap_cities,
    list_cities_for_country,
)
from app.services.affiliate import tag_url
from app.services.scraper import run_scrape
from app.templating import templates


def _client_ip(request: Request) -> str:
    return get_client_ip(request)


_DEFAULT_DESCRIPTION = (
    "Find portable air conditioners in stock across Europe. "
    "KlimaRadar tracks real-time AC availability, prices and delivery times in Germany, France and beyond."
)

router = APIRouter()


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
        f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml",
        media_type="text/plain",
    )


@router.api_route("/sitemap.xml", methods=["GET", "HEAD"])
async def sitemap_xml():
    base = settings.base_url.rstrip("/")
    today = datetime.now(timezone.utc).date().isoformat()

    urls = [
        (f"{base}/", "1.0"),
        (f"{base}/search?country=DE", "0.8"),
        (f"{base}/search?country=FR", "0.8"),
        (f"{base}/pricing", "0.8"),
        (f"{base}/privacy", "0.5"),
        (f"{base}/about", "0.5"),
    ]
    for country, city in get_sitemap_cities():
        urls.append((f"{base}/{country}/{city}/portable-ac-in-stock", "0.7"))

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
            description="Learn what KlimaRadar does: real-time portable AC stock and price tracking across Europe.",
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
    session: AsyncSession = Depends(get_db),
):
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
    listings = await _fetch_filtered_listings(session, filters)

    country_upper = country.upper()
    base = settings.base_url.rstrip("/")
    query_suffix = f"?{request.url.query}" if request.url.query else ""
    canonical_url = f"{base}{request.url.path}{query_suffix}"
    html_lang = COUNTRY_LANGUAGES.get(country_upper, "en")
    hreflang_alternates = build_hreflang_alternates(html_lang, canonical_url, base)

    if country_upper == "DE":
        title = f"Mobile Klimaanlage auf Lager{f' in {city}' if city else ''} — {country_upper}"
        description = (
            f"Finde mobile Klimaanlagen auf Lager{f' in {city}' if city else ''} in Deutschland. "
            "Vergleiche Preise, Verfügbarkeit und Lieferzeiten auf KlimaRadar."
        )
    elif country_upper == "FR":
        title = f"Climatiseur mobile en stock{f' à {city}' if city else ''} — {country_upper}"
        description = (
            f"Trouvez des climatiseurs mobiles en stock{f' à {city}' if city else ''} en France. "
            "Comparez les prix, la disponibilité et les délais de livraison sur KlimaRadar."
        )
    else:
        title = f"Portable AC in stock{f' in {city}' if city else ''}, {country_upper}"
        description = (
            f"Browse portable air conditioners in stock{f' in {city}' if city else ''} in {country_upper}. "
            "Compare prices, stock status and delivery times on KlimaRadar."
        )

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
            listings=listings,
            filters=filters.model_dump(),
            total=len(listings),
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
    listings = await _fetch_filtered_listings(session, filters)
    seo_copy = get_seo_copy(country_code, city_info)

    base = settings.base_url.rstrip("/")
    canonical_url = f"{base}/{country_code.lower()}/{city_info['slug']}/portable-ac-in-stock"
    html_lang = COUNTRY_LANGUAGES.get(country_code, "en")
    hreflang_alternates = build_hreflang_alternates(html_lang, canonical_url, base)
    breadcrumb_jsonld = build_breadcrumb_jsonld(base, country_code, city_info, seo_copy)
    other_cities = list_cities_for_country(country_code, limit=10, exclude_slug=city_info["slug"])

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
            breadcrumb_jsonld=json.dumps(breadcrumb_jsonld, ensure_ascii=False),
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

    target = listing.affiliate_url or tag_url(listing.retailer.domain, listing.url)
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
    try:
        listing_count = await session.scalar(select(func.count(Listing.id)))
        retailer_count = await session.scalar(select(func.count(Retailer.id)))
        return {
            "status": "ok",
            "listings": listing_count,
            "retailers": retailer_count,
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
    if x_admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin API key")
    results = await run_scrape(country=country)
    return {"results": results}


async def _get_stats(session: AsyncSession) -> StatsOut:
    total = await session.scalar(select(func.count(Listing.id)))
    in_stock = await session.scalar(
        select(func.count(Listing.id)).where(Listing.stock_status == "in_stock")
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
    session: AsyncSession, filters: SearchFilters
) -> list[dict]:
    stmt = (
        select(Listing, Product, Retailer)
        .join(Product, Listing.product_id == Product.id)
        .join(Retailer, Listing.retailer_id == Retailer.id)
        .where(Listing.country == filters.country)
        .order_by(
            (Listing.stock_status == "in_stock").desc(),
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
            }
        )
    return rows
