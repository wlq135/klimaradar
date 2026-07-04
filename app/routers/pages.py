"""Public HTML pages and affiliate redirect."""

from datetime import datetime, timezone
import hashlib

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models import ClickEvent, Listing, Product, Retailer
from app.rate_limit import admin_scrape_limiter
from app.schemas import SearchFilters, StatsOut
from app.services.affiliate import tag_url
from app.services.scraper import run_scrape
from app.templating import templates


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


_SITEMAP_CITIES = [
    ("de", "berlin"),
    ("de", "hamburg"),
    ("de", "munich"),
    ("de", "cologne"),
    ("de", "frankfurt"),
    ("de", "stuttgart"),
    ("fr", "paris"),
    ("fr", "lyon"),
    ("fr", "marseille"),
]

_DEFAULT_DESCRIPTION = (
    "Find portable air conditioners in stock across Europe. "
    "KlimaRadar tracks real-time AC availability, prices and delivery times in Germany, France and beyond."
)

router = APIRouter()


def _template_context(**extra) -> dict:
    return extra


def _hash_ip(ip: str | None) -> str | None:
    if not ip:
        return None
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()[:32]


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, session: AsyncSession = Depends(get_db)):
    stats = await _get_stats(session)
    return templates.TemplateResponse(
        request,
        "index.html",
        _template_context(
            title="KlimaRadar — Find portable ACs in stock across Europe",
            description=_DEFAULT_DESCRIPTION,
            stats=stats,
        ),
    )


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    base = settings.base_url.rstrip("/")
    return PlainTextResponse(
        f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml",
        media_type="text/plain",
    )


@router.get("/sitemap.xml")
async def sitemap_xml():
    base = settings.base_url.rstrip("/")
    today = datetime.now(timezone.utc).date().isoformat()

    urls = [
        (f"{base}/", "1.0"),
        (f"{base}/search?country=DE", "0.8"),
        (f"{base}/search?country=FR", "0.8"),
        (f"{base}/privacy", "0.5"),
        (f"{base}/about", "0.5"),
    ]
    for country, city in _SITEMAP_CITIES:
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


@router.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse(
        request,
        "privacy.html",
        _template_context(
            title="Privacy Policy — KlimaRadar",
            description="Read KlimaRadar's privacy policy, cookie usage, email practices, affiliate disclosure and your GDPR rights.",
        ),
    )


@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        request,
        "about.html",
        _template_context(
            title="About KlimaRadar",
            description="Learn what KlimaRadar does: real-time portable AC stock and price tracking across Europe.",
        ),
    )


@router.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse(
        request,
        "terms.html",
        _template_context(
            title="Terms of Service — KlimaRadar",
            description="Read KlimaRadar's terms of service and affiliate disclosure.",
        ),
    )


@router.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    country: str = "DE",
    city: str | None = None,
    product_type: str | None = "portable",
    min_btu: int | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    q: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    filters = SearchFilters(
        country=country,
        city=city,
        product_type=product_type,
        min_btu=min_btu,
        max_price=max_price,
        in_stock_only=in_stock_only,
        q=q,
    )
    listings = await _fetch_filtered_listings(session, filters)
    title = f"Portable AC in stock{f' in {city}' if city else ''}, {country}"
    description = (
        f"Browse portable air conditioners in stock{f' in {city}' if city else ''} in {country}. "
        "Compare prices, stock status and delivery times on KlimaRadar."
    )
    return templates.TemplateResponse(
        request,
        "search.html",
        _template_context(
            title=title,
            description=description,
            listings=listings,
            filters=filters.model_dump(),
            total=len(listings),
        ),
    )


@router.get("/{country}/{city}/portable-ac-in-stock", response_class=HTMLResponse)
async def city_seo_page(
    request: Request,
    country: str,
    city: str,
    session: AsyncSession = Depends(get_db),
):
    filters = SearchFilters(country=country.upper(), city=city.title())
    listings = await _fetch_filtered_listings(session, filters)
    title = f"Portable AC in stock in {city.title()}, {country.upper()} — KlimaRadar"
    description = (
        f"Find portable air conditioners in stock in {city.title()}, {country.upper()}. "
        "Compare live availability, prices and delivery options on KlimaRadar."
    )
    return templates.TemplateResponse(
        request,
        "search.html",
        _template_context(
            title=title,
            description=description,
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
        ip_hash=_hash_ip(request.client.host if request.client else None),
    )
    session.add(click)
    await session.commit()

    target = listing.affiliate_url or tag_url(listing.retailer.domain, listing.url)
    if not target:
        raise HTTPException(status_code=500, detail="No redirect target for listing")
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
    """Manual trigger for the scraper. Protected by ADMIN_API_KEY in production."""
    await admin_scrape_limiter.check(_client_ip(request))
    if settings.admin_api_key and x_admin_api_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid or missing admin API key")
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
