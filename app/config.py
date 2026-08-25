"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All env-backed settings with sensible MVP defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "KlimaRadar"
    base_url: str = "http://localhost:8000"
    debug: bool = False

    database_url: str = "sqlite+aiosqlite:///./klimaradar.db"

    sendgrid_api_key: str = ""
    from_email: str = "alerts@klima-radar.com"

    # Brevo API key (v3 /smtp/email) — useful when SMTP is not yet activated.
    # If set, it takes precedence over the SMTP backend.
    brevo_api_key: str = ""

    # SMTP email backend (e.g. Brevo, Mailgun, AWS SES). If SMTP_HOST is set,
    # it takes precedence over SendGrid.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # Admin API key used to protect manual endpoints like /api/admin/scrape.
    # Must be set in production; endpoints will reject requests when empty.
    admin_api_key: str = ""

    # Demo data/spider. Keep disabled on the public site to avoid fake listings.
    enable_demo: bool = False

    # Run low-memory maintenance jobs inside the web process. Keep this enabled
    # even when Chromium scraping is moved to the standalone worker.
    enable_scheduler: bool = True

    # Run Chromium scraping inside the web process. Keep this disabled on the
    # 512 MB Render Starter web service; the standalone worker posts snapshots
    # to /api/admin/ingest instead.
    enable_scraper: bool = True

    # Standalone scraper worker. The worker runs Playwright and sends normalized
    # snapshots to the web service's admin ingest endpoint over HTTPS.
    worker_api_base: str = ""
    worker_api_key: str = ""
    worker_country: str = ""
    # Chromium/Playwright memory can fragment over long-running worker
    # processes. Replace the process periodically without losing the container.
    worker_restart_cycles: int = 3

    amazon_de_affiliate_tag: str = ""
    amazon_uk_affiliate_tag: str = ""
    amazon_fr_affiliate_tag: str = ""
    amazon_it_affiliate_tag: str = ""
    amazon_es_affiliate_tag: str = ""
    amazon_nl_affiliate_tag: str = ""
    amazon_be_affiliate_tag: str = ""
    mediamarkt_de_affiliate_tag: str = ""
    boulanger_fr_affiliate_tag: str = ""
    darty_fr_affiliate_tag: str = ""

    # Analytics (optional). Set PLAUSIBLE_DOMAIN to enable Plausible Analytics.
    # Example: PLAUSIBLE_DOMAIN=klima-radar.com
    plausible_domain: str = ""

    # Plausible script URL. Use the exact snippet URL from your Plausible site
    # settings (it may include extensions such as outbound-links). Defaults to the
    # standard script if left empty.
    plausible_script_url: str = "https://plausible.io/js/script.js"

    # Cloudflare Web Analytics beacon token (free, privacy-friendly, no cookies).
    # Find it in dash.cloudflare.com -> Analytics & Logs -> Web Analytics.
    cf_web_analytics_token: str = ""

    # Google Search Console verification (optional). Paste the content of the
    # meta tag here to inject <meta name="google-site-verification" content="...">.
    google_site_verification: str = ""

    # IndexNow key used by participating search engines (Bing, Yandex, and
    # others). The public key file is served at /indexnow-{key}.txt.
    indexnow_key: str = "0ca6aab482edb0f186ec58eaf9bed7a0"

    # Playwright proxy (optional). Set PLAYWRIGHT_PROXY_SERVER to route traffic
    # through an HTTP proxy. Credentials are only required when the proxy needs
    # authentication (e.g. Bright Data, ScrapingBee residential proxies).
    # PLAYWRIGHT_PROXY_RETAILERS is a comma-separated list of spider names; when
    # set, only those retailers will use the proxy (e.g. "Boulanger France,Darty
    # France"). Leave empty to apply the proxy to all Playwright spiders.
    playwright_proxy_server: str = ""
    playwright_proxy_username: str = ""
    playwright_proxy_password: str = ""
    playwright_proxy_retailers: str = ""

    # Paddle billing integration.
    # Paddle handles EU VAT as the merchant of record.
    paddle_environment: str = "sandbox"  # "sandbox" or "production"
    paddle_api_key: str = ""
    paddle_webhook_secret: str = ""
    paddle_price_id: str = ""  # e.g. pri_...

    # Lemon Squeezy billing integration (legacy; kept for existing webhooks).
    lemon_squeezy_api_key: str = ""
    lemon_squeezy_webhook_secret: str = ""
    lemon_squeezy_store_id: str = ""
    lemon_squeezy_variant_id: str = ""

    # Creem billing integration (new default checkout).
    creem_api_key: str = ""
    creem_webhook_secret: str = ""
    creem_product_id: str = ""
    creem_api_base: str = "https://api.creem.io/v1"

    scraper_interval_minutes: int = 10
    request_timeout_seconds: int = 30
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )


settings = Settings()
