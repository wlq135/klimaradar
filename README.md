# KlimaRadar — European AC Stock Radar

A lightweight, FastAPI-based MVP that aggregates portable air-conditioner availability and prices across major European retailers and sends email alerts when units come back in stock.

## Why

Europe's 2025–2026 heat waves created severe shortages of portable AC units. Many apartments cannot install split units due to building regulations or landlord restrictions, so renters are stuck refreshing retailer websites. KlimaRadar aggregates stock status in one place and notifies users the moment a unit becomes available.

## MVP Scope

- Search in-stock / back-order portable ACs by country, city, BTU and price.
- Subscribe to email alerts (double opt-in).
- SEO landing pages for high-intent queries like “portable AC in stock Berlin”.
- Affiliate monetization via retailer links.

## Quick Start

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers (required for Amazon DE, MediaMarkt DE, Boulanger FR)
playwright install chromium

# 4. Copy and edit environment variables
cp .env.example .env
# Edit .env with your SendGrid key, affiliate tags, etc.

# 5. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 and try searching for portable ACs in Germany.

> **Note:** The first startup seeds a demo retailer so the UI is never empty. Live spiders run automatically via APScheduler based on `SCRAPER_INTERVAL_MINUTES`.

## Configuration

Key environment variables in `.env`:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | SQLite path or PostgreSQL DSN. |
| `BASE_URL` | Public URL used in confirmation/alert links (e.g. `https://klima-radar.com`). |
| `DEBUG` | Set to `true` only for local development. |
| `SENDGRID_API_KEY` | Email delivery. Leave empty to print emails to the console. |
| `FROM_EMAIL` | Sender address for alerts. |
| `ADMIN_API_KEY` | Protects the manual `/api/admin/scrape` endpoint in production. |
| `AMAZON_DE_AFFILIATE_TAG` | Amazon DE affiliate tag. |
| `MEDIAMARKT_DE_AFFILIATE_TAG` | MediaMarkt DE affiliate tag. |
| `BOULANGER_FR_AFFILIATE_TAG` | Boulanger FR affiliate tag. |
| `DARTY_FR_AFFILIATE_TAG` | Darty FR affiliate tag. |
| `PLAYWRIGHT_PROXY_SERVER` | Optional HTTP proxy for protected sites (e.g. Boulanger). |
| `PLAYWRIGHT_PROXY_USERNAME` | Proxy username, if required. |
| `PLAYWRIGHT_PROXY_PASSWORD` | Proxy password, if required. |
| `SCRAPER_INTERVAL_MINUTES` | How often to run the spider scheduler. |
| `REQUEST_TIMEOUT_SECONDS` | Per-request timeout for spiders. |
| `USER_AGENT` | Default user-agent used by spiders. |

## Supported Retailers

| Retailer | Country | Status | Implementation |
|----------|---------|--------|----------------|
| Demo Retailer | — | Always works | `app/spiders/demo.py` |
| Amazon Germany | DE | Works; prices in EUR once `i18n-prefs=EUR` cookie is set | `app/spiders/amazon_de.py` |
| MediaMarkt Germany | DE | Works; parses `__PRELOADED_STATE__` Apollo cache | `app/spiders/mediamarkt_de.py` |
| Boulanger France | FR | Blocked by DataDome; needs proxy/anti-detect | `app/spiders/boulanger_fr.py` |
| Darty France | FR | Blocked without residential proxy; placeholder selectors | `app/spiders/darty_fr.py` |

Retailers are registered in `app/spiders/registry.py`. Add new static sites by extending the `_GENERIC_SPIDERS` list, or add a Playwright spider for JS-heavy sites.

## Anti-Bot & Legal Notes

- The spiders use a real headless browser with a realistic user-agent and reasonable request rates.
- Amazon DE sometimes serves international USD offers to unknown sessions; the spider forces an `i18n-prefs=EUR` cookie.
- MediaMarkt DE exposes product data in `window.__PRELOADED_STATE__`, which is stable but may change shape.
- Boulanger FR is protected by DataDome. To make it work you will need a proxy/anti-detect service (e.g. ScrapingBee, Bright Data) or residential IP.
- Always respect each site's `robots.txt`, terms of service, and applicable data-protection laws (GDPR).

## Development

Run tests:

```bash
pytest tests/ -v
```

Run a single scraper pass manually:

```bash
# All configured spiders
python -m app.cli scrape

# Only Germany
python -m app.cli scrape --country=DE

# Only France
python -m app.cli scrape --country=FR
```

## Deployment

### Docker Compose (recommended for self-hosting)

```bash
# Build and start the app on http://localhost:8000
docker compose up --build -d

# View logs
docker compose logs -f

# The SQLite database is persisted at ./klimaradar.db on the host.
```

### Railway

1. Push this repo to GitHub.
2. Create a new Railway project and select "Deploy from GitHub repo".
3. Add environment variables in Railway dashboard:
   - `BASE_URL` (`https://klima-radar.com`)
   - `SENDGRID_API_KEY`, `FROM_EMAIL`
   - `ADMIN_API_KEY`
   - Affiliate tags
   - Optional `PLAYWRIGHT_PROXY_*` for Boulanger/Darty
4. Railway uses the included `railway.json` and `Dockerfile`.

### Render

1. Push this repo to GitHub.
2. In Render Dashboard → "New Web Service" → connect the repo.
3. Render will use `render.yaml` (or just set runtime to Docker and point to the Dockerfile).
4. Replace `YOUR_USERNAME` in `render.yaml` with your GitHub username.
5. Add `klima-radar.com` as a Custom Domain in Render and configure DNS as described in `LAUNCH.md` section 3.1.
6. Update environment variables in the Render dashboard if needed.

> **Note:** The first deploy downloads Playwright Chromium, so the initial build may take 3–5 minutes. The health endpoint `/api/health` confirms the service is ready.

## Roadmap

1. **Week 1–2**: MVP with real retailer spiders, email alerts, SEO pages.
2. **Phase 2**: Add France/Italy/Spain, Stripe premium alerts, SMS via Twilio.
3. **Phase 3**: Sponsored listings, installer lead-gen, rental/second-hand marketplace.

## License

MIT
