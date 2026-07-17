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

    amazon_de_affiliate_tag: str = ""
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

    # Google Search Console verification (optional). Paste the content of the
    # meta tag here to inject <meta name="google-site-verification" content="...">.
    google_site_verification: str = ""

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

    # Lemon Squeezy billing integration (new default checkout).
    lemon_squeezy_api_key: str = ""
    lemon_squeezy_webhook_secret: str = ""
    lemon_squeezy_store_id: str = ""
    lemon_squeezy_variant_id: str = ""

    scraper_interval_minutes: int = 60
    request_timeout_seconds: int = 30
    user_agent: str = (
        "Mozilla/5.0 (compatible; KlimaRadar/1.0; +https://klima-radar.com)"
    )


settings = Settings()
