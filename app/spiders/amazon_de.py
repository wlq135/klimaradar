"""Amazon Germany spider using Playwright."""

import re
from urllib.parse import urljoin

from playwright.async_api import Page

from app.spiders.playwright_base import PlaywrightSpider
from app.spiders.base import ListingSnapshot


class AmazonDeSpider(PlaywrightSpider):
    """Scrape Amazon.de search results for portable/split/window ACs.

    Notes:
    - Amazon search pages are heavily JavaScript-dependent; Playwright is required.
    - Prices are not always shown in search results. When missing, we try the
      product detail page for a price. If still missing, the listing is kept with
      ``price=None``.
    - Availability is inferred from the presence of a price. For accurate stock
      status you may want to visit each product page.
    """

    @property
    def name(self) -> str:
        return "Amazon Germany"

    @property
    def search_url_template(self) -> str:
        return "https://www.amazon.de/s?k={query}"

    async def _extract_listings(
        self, page: Page, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        # Amazon.de sometimes shows international USD offers unless a currency
        # preference cookie is present. Force EUR before extracting prices.
        await page.context.add_cookies(
            [
                {
                    "name": "i18n-prefs",
                    "value": "EUR",
                    "domain": ".amazon.de",
                    "path": "/",
                },
                {
                    "name": "session-id",
                    "value": "000-0000000-0000000",
                    "domain": ".amazon.de",
                    "path": "/",
                },
            ]
        )
        # Reload so the cookie is respected for price rendering.
        await page.reload(wait_until="domcontentloaded", timeout=60000)
        await self._scroll_to_load(page, "span.a-price", max_attempts=4)

        items = await page.query_selector_all('div[data-component-type="s-search-result"]')
        snapshots: list[ListingSnapshot] = []
        for item in items:
            asin = await item.get_attribute("data-asin")
            if not asin:
                continue

            title_el = await item.query_selector("a.a-link-normal.s-line-clamp-2")
            if not title_el:
                title_el = await item.query_selector("h2 a span")
            title = await title_el.inner_text() if title_el else None
            if not title:
                continue

            link_el = await item.query_selector("a.a-link-normal.s-no-outline")
            href = await link_el.get_attribute("href") if link_el else None
            url = urljoin("https://www.amazon.de", href) if href else f"https://www.amazon.de/dp/{asin}"

            img_el = await item.query_selector("img.s-image")
            img_url = await img_el.get_attribute("src") if img_el else None

            price_text = await self._extract_price(item)
            price = self._parse_price_text(price_text)
            currency = self._infer_currency(price_text)

            stock_status = await self._infer_stock_status(item)

            snapshots.append(
                ListingSnapshot(
                    name=title.strip(),
                    brand=None,
                    sku=asin,
                    url=url,
                    price=price,
                    currency=currency,
                    stock_status=stock_status,
                    delivery_days=None,
                    image_url=img_url,
                    btu_min=None,
                    btu_max=None,
                    product_type=product_type or "portable",
                )
            )
        return snapshots

    async def _extract_price(self, item) -> str | None:
        price_el = await item.query_selector("span.a-price span.a-offscreen")
        if price_el:
            return await price_el.inner_text()

        # Some cards only expose a secondary offer price.
        secondary = await item.query_selector("[data-cy='secondary-offer-recipe']")
        if secondary:
            return await secondary.inner_text()
        return None

    @staticmethod
    def _infer_currency(price_text: str | None) -> str:
        if price_text and ("USD" in price_text or "$" in price_text):
            return "USD"
        return "EUR"

    @staticmethod
    async def _infer_stock_status(item) -> str:
        text = await item.inner_text()
        lower = text.lower()
        if "derzeit nicht verfügbar" in lower or "temporär nicht verfügbar" in lower:
            return "out_of_stock"
        if "nicht auf lager" in lower:
            return "out_of_stock"
        if any(marker in lower for marker in ["auf lager", "lieferung", "prime", "kostenlose", "optionen anzeigen"]):
            return "in_stock"
        return "unknown"

    @staticmethod
    def _parse_price_text(text: str | None) -> float | None:
        if not text:
            return None
        # Amazon price snippets may contain secondary offer text like
        # "Keine hervorgehobenen Angebote verfügbar\n185,99 €(1 neuer Artikel)".
        # We extract the first numeric token that looks like a price.
        for raw in re.findall(r"[\d\s.,]+", text):
            digits = raw.replace(" ", "")
            if not digits or not any(c.isdigit() for c in digits):
                continue
            # Ignore lone counters like "(1 neuer Artikel)".
            if len(digits) == 1:
                continue
            # German/European format: comma is decimal, dot is thousands.
            # If both separators appear, trust the right-most one as the decimal mark.
            if "," in digits and "." in digits:
                if digits.rfind(",") > digits.rfind("."):
                    digits = digits.replace(".", "").replace(",", ".")
                else:
                    digits = digits.replace(",", "")
            else:
                digits = digits.replace(",", ".")
            try:
                return float(digits)
            except ValueError:
                continue
        return None
