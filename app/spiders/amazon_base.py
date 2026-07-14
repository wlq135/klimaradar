"""Configurable base spider for Amazon EU marketplaces."""

import re
from urllib.parse import urljoin

from playwright.async_api import Page

from app.spiders.base import ListingSnapshot
from app.spiders.playwright_base import PlaywrightSpider


class BaseAmazonSpider(PlaywrightSpider):
    """Scrape an Amazon marketplace search results for portable/split/window ACs.

    Subclasses configure the domain, locale, query and language-specific
    keywords. The extraction logic is shared across Amazon EU sites.
    """

    domain: str = ""
    search_url_template: str = ""
    default_query: str = "portable air conditioner"
    currency: str = "EUR"
    _LOCALE: str = "en-US"

    _INCLUDE_TITLE_WORDS: list[str] = [
        "air conditioner",
        "air conditioning",
        "ac",
        "klima",
        "climatiseur",
        "clim",
        "condizionatore",
        "aire acondicionado",
        "airco",
        "monoblock",
        "monobloc",
        "split",
    ]
    _EXCLUDE_TITLE_WORDS: list[str] = [
        "laptop",
        "notebook",
        "pc",
        "cooling pad",
        "refroidisseur pc",
        "refroidisseur",
        "ventilateur",
        "ventilo",
        "ventilator",
        "fan",
        "humidifier",
        "humidificateur",
        "déshumidificateur",
        "deshumidificateur",
        "dehumidifier",
        "luftentfeuchter",
        "entfeuchter",
        "radiateur",
        "chauffage",
        "heater",
        "heizlüfter",
        "heizung",
    ]

    _UNAVAILABLE_MARKERS: list[str] = [
        "currently unavailable",
        "temporarily out of stock",
        "out of stock",
        "sold out",
        "no offers",
        "no featured offers",
        "unavailable",
    ]
    _POSITIVE_MARKERS: list[str] = [
        "in stock",
        "available",
        "add to basket",
        "buy now",
        "prime",
    ]

    @classmethod
    def _is_relevant_title(cls, title: str) -> bool:
        lower = title.lower()
        if any(word in lower for word in cls._EXCLUDE_TITLE_WORDS):
            return False
        return any(word in lower for word in cls._INCLUDE_TITLE_WORDS)

    async def _pre_navigate(self, context) -> None:
        # Force EUR currency preference before loading the page.
        parsed = __import__("urllib.parse").urlparse(self.domain)
        cookie_domain = f".{parsed.netloc.replace('www.', '')}"
        await context.add_cookies(
            [
                {
                    "name": "i18n-prefs",
                    "value": "EUR",
                    "domain": cookie_domain,
                    "path": "/",
                },
                {
                    "name": "session-id",
                    "value": "000-0000000-0000000",
                    "domain": cookie_domain,
                    "path": "/",
                },
            ]
        )

    async def _extract_listings(
        self, page: Page, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        try:
            await page.wait_for_selector(
                'div[data-component-type="s-search-result"]', timeout=15000
            )
        except Exception:
            pass
        await self._scroll_to_load(page, "span.a-price", max_attempts=4)

        items = await page.query_selector_all(
            'div[data-component-type="s-search-result"]'
        )
        snapshots: list[ListingSnapshot] = []
        for item in items:
            asin = await item.get_attribute("data-asin")
            if not asin:
                continue

            title_el = await item.query_selector("a.a-link-normal.s-line-clamp-2")
            if not title_el:
                title_el = await item.query_selector("a.a-link-normal h2 span")
            if not title_el:
                title_el = await item.query_selector("h2 span")
            title = await title_el.inner_text() if title_el else None
            if not title:
                continue

            if not self._is_relevant_title(title):
                continue

            link_el = await item.query_selector("a.a-link-normal.s-no-outline")
            href = await link_el.get_attribute("href") if link_el else None
            url = (
                urljoin(self.domain, href)
                if href
                else f"{self.domain}/dp/{asin}"
            )

            img_el = await item.query_selector("img.s-image")
            img_url = await img_el.get_attribute("src") if img_el else None

            price_text = await self._extract_price(item)
            price = self._parse_price_text(price_text)
            currency = self._infer_currency(price_text)

            stock_status = await self._infer_stock_status(item, price)

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

        secondary = await item.query_selector("[data-cy='secondary-offer-recipe']")
        if secondary:
            return await secondary.inner_text()
        return None

    def _infer_currency(self, price_text: str | None) -> str:
        if price_text and ("USD" in price_text or "$" in price_text):
            return "USD"
        return self.currency

    @classmethod
    async def _infer_stock_status(cls, item, price: float | None) -> str:
        text = await item.inner_text()
        lower = text.lower()
        if any(marker in lower for marker in cls._UNAVAILABLE_MARKERS):
            return "out_of_stock"

        if price is None:
            return "unknown"

        if any(marker in lower for marker in cls._POSITIVE_MARKERS):
            return "in_stock"
        return "unknown"

    @staticmethod
    def _parse_price_text(text: str | None) -> float | None:
        if not text:
            return None
        for raw in re.findall(r"[\d\s.,]+", text):
            digits = raw.replace(" ", "")
            if not digits or not any(c.isdigit() for c in digits):
                continue
            if len(digits) == 1:
                continue
            # European format: comma decimal, dot thousands.
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
