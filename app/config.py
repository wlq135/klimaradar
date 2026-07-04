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

    # SMTP email backend (e.g. Brevo, Mailgun, AWS SES). If SMTP_HOST is set,
    # it takes precedence over SendGrid.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # Admin API key used to protect manual endpoints like /api/admin/scrape.
    # Leave empty to allow unauthenticated access (not recommended in production).
    admin_api_key: str = ""

    amazon_de_affiliate_tag: str = ""
    mediamarkt_de_affiliate_tag: str = ""
    boulanger_fr_affiliate_tag: str = ""
    darty_fr_affiliate_tag: str = ""

    # Playwright proxy (optional). Set PLAYWRIGHT_PROXY_SERVER to route traffic
    # through an HTTP proxy. Credentials are only required when the proxy needs
    # authentication (e.g. Bright Data, ScrapingBee residential proxies).
    playwright_proxy_server: str = ""
    playwright_proxy_username: str = ""
    playwright_proxy_password: str = ""

    scraper_interval_minutes: int = 10
    request_timeout_seconds: int = 30
    user_agent: str = (
        "Mozilla/5.0 (compatible; KlimaRadar/1.0; +https://klima-radar.com)"
    )


settings = Settings()
