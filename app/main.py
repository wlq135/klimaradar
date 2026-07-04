"""FastAPI application factory and lifecycle hooks."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import engine
from app.models import Base, Retailer
from app.routers import alerts, pages
from app.templating import templates
from app.cloudflare import is_cloudflare_request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables, seed demo data and start the scraper scheduler."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed retailers if the database is empty. Demo listings are only generated
    # when ENABLE_DEMO is true.
    from app.database import AsyncSessionLocal
    from app.seed import seed_demo_data

    async with AsyncSessionLocal() as session:
        retailer_count = await session.scalar(select(func.count(Retailer.id)))
        if not retailer_count:
            logger.info("Seeding retailers...")
            await seed_demo_data(session)
            await session.commit()

    # Start periodic scraping.
    from app.scheduler import create_scheduler

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scraper scheduler started (every %s minutes)", settings.scraper_interval_minutes)

    yield

    scheduler.shutdown()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# Only trust X-Forwarded-Proto when the request comes through Cloudflare
# (identified by the presence of CF-Connecting-IP). This avoids allowing any
# client to spoof the request scheme.
@app.middleware("http")
async def cloudflare_scheme(request, call_next):
    if (
        is_cloudflare_request(request)
        and request.headers.get("x-forwarded-proto") == "https"
    ):
        request.scope["scheme"] = "https"
    return await call_next(request)


@app.middleware("http")
async def security_headers(request, call_next):
    """Add baseline security headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


def _wants_html(request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept or "*/*" in accept


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    if _wants_html(request):
        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "title": f"Error {exc.status_code}",
                "status_code": exc.status_code,
                "detail": exc.detail,
            },
            status_code=exc.status_code,
        )
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    if _wants_html(request):
        return templates.TemplateResponse(
            request,
            "error.html",
            {"title": "Bad request", "status_code": 400, "detail": "Invalid request."},
            status_code=400,
        )
    return JSONResponse({"detail": "Invalid request"}, status_code=400)


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.exception("Unhandled error processing request")
    if _wants_html(request):
        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "title": "Server error",
                "status_code": 500,
                "detail": "Something went wrong. Please try again later.",
            },
            status_code=500,
        )
    return JSONResponse({"detail": "Internal server error"}, status_code=500)


app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(pages.router)
app.include_router(alerts.router)
