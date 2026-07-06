"""Base Playwright spider with common launch, scroll and extraction helpers."""

from abc import abstractmethod

from playwright.async_api import BrowserContext, Page, async_playwright

from app.config import settings
from app.spiders.base import ListingSnapshot, Spider


# JavaScript injected into every page before any navigation. It removes the most
# common headless fingerprints and makes Playwright look like a regular Chromium
# user. This is a baseline mitigation; sites protected by advanced bot management
# (DataDome, Cloudflare Turnstile) may still require a residential proxy or a
# managed browser service.
_STEALTH_INIT_SCRIPT = """
(() => {
  // Hide the navigator.webdriver flag.
  Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

  // Pretend plugins are installed (Chrome usually has at least a couple).
  Object.defineProperty(navigator, 'plugins', {
    get: () => [
      { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
      { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format plugin' },
      { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
    ]
  });

  // Plausible languages list for a French or German user agent.
  Object.defineProperty(navigator, 'languages', { get: () => ['fr-FR', 'fr', 'en-US', 'en'] });

  // Chrome exposes window.chrome on real browsers.
  window.chrome = window.chrome || { runtime: {} };

  // Remove Playwright-specific permissions if present.
  const originalQuery = window.navigator.permissions.query;
  window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications'
      ? Promise.resolve({ state: Notification.permission })
      : originalQuery(parameters)
  );

  // Mask the runtime error stack traces that some bot detectors look for.
  const oldToString = Function.prototype.toString;
  Function.prototype.toString = function(...args) {
    if (this === window.navigator.permissions.query) {
      return 'function query() { [native code] }';
    }
    if (this === Function.prototype.toString) {
      return 'function toString() { [native code] }';
    }
    return oldToString.call(this, ...args);
  };
})();
"""


class PlaywrightSpider(Spider):
    """Spider that drives a headless Chromium browser via Playwright.

    Subclasses implement ``_extract_listings`` to parse a loaded page.
    """

    def __init__(self, retailer_id: int, country: str, affiliate_tag: str | None = None):
        super().__init__(retailer_id, affiliate_tag)
        self._country = country

    @property
    def country(self) -> str:
        return self._country

    @property
    @abstractmethod
    def search_url_template(self) -> str:
        """URL template that must contain a ``{query}`` placeholder."""

    def _build_search_url(self, query: str) -> str:
        return self.search_url_template.format(query=query.replace(" ", "+"))

    @abstractmethod
    async def _extract_listings(
        self, page: Page, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        """Parse the rendered page and return normalized snapshots."""

    def _proxy_config(self) -> dict | None:
        """Return Playwright proxy options when PLAYWRIGHT_PROXY_SERVER is set."""
        if not settings.playwright_proxy_server:
            return None
        proxy: dict = {"server": settings.playwright_proxy_server}
        if settings.playwright_proxy_username:
            proxy["username"] = settings.playwright_proxy_username
        if settings.playwright_proxy_password:
            proxy["password"] = settings.playwright_proxy_password
        return proxy

    async def _prepare_context(self, browser) -> BrowserContext:
        """Create a browser context with anti-detection and optional proxy."""
        context_kwargs: dict = {
            "user_agent": settings.user_agent,
            "viewport": {"width": 1280, "height": 800},
            "locale": "de-DE" if self.country == "DE" else "fr-FR",
        }
        proxy = self._proxy_config()
        if proxy:
            context_kwargs["proxy"] = proxy

        context = await browser.new_context(**context_kwargs)
        await context.add_init_script(_STEALTH_INIT_SCRIPT)
        return context

    async def _pre_navigate(self, context: BrowserContext) -> None:
        """Optional hook to set cookies / session state before loading the page."""
        return None

    async def fetch_listings(
        self, query: str, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            context = await self._prepare_context(browser)
            page = await context.new_page()
            try:
                await self._pre_navigate(context)
                url = self._build_search_url(query)
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                listings = await self._extract_listings(page, product_type)
                return listings
            finally:
                await browser.close()

    @staticmethod
    async def _scroll_to_load(page: Page, selector: str, max_attempts: int = 3) -> None:
        """Scroll down repeatedly until ``selector`` appears on the page."""
        for _ in range(max_attempts):
            try:
                await page.wait_for_selector(selector, timeout=5000)
                return
            except Exception:
                await page.evaluate("window.scrollBy(0, 800)")
                await page.wait_for_timeout(1500)
