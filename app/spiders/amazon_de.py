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

    _INCLUDE_TITLE_WORDS = [
        "klimagerät",
        "klimaanlage",
        "klima",
        "air conditioner",
        "air conditioning",
        "monoblock",
        "split",
    ]
    _EXCLUDE_TITLE_WORDS = [
        "laptop",
        "notebook",
        "pc",
        "cooling pad",
        "kühlpad",
        "kühler",
        "lüfter",
        "ventilator",
        "fan",
        "humidifier",
        "luftbefeuchter",
        "befeuchter",
        "dehumidifier",
        "luftentfeuchter",
        "entfeuchter",
        "heizlüfter",
        "heizung",
        "heater",
    ]

    @property
    def name(self) -> str:
        return "Amazon Germany"

    @property
    def search_url_template(self) -> str:
        return "https://www.amazon.de/s?k={query}"

    default_query: str = "mobiles klimagerät"

    @classmethod
    def _is_relevant_title(cls, title: str) -> bool:
        lower = title.lower()
        if any(word in lower for word in cls._EXCLUDE_TITLE_WORDS):
            return False
        return any(word in lower for word in cls._INCLUDE_TITLE_WORDS)

    async def _pre_navigate(self, context) -> None:
        # Amazon sometimes shows international USD offers unless a currency
        # preference cookie is present. Force EUR before loading the page.
        await context.add_cookies(
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

    async def _extract_listings(
        self, page: Page, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        # Give the results grid (and any WAF challenge) time to render.
        try:
            await page.wait_for_selector(
                'div[data-component-type="s-search-result"]', timeout=15000
            )
        except Exception:
            pass
        await self._scroll_to_load(page, "span.a-price", max_attempts=4)

        items = await page.query_selector_all('div[data-component-type="s-search-result"]')
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
            url = urljoin("https://www.amazon.de", href) if href else f"https://www.amazon.de/dp/{asin}"

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
    async def _infer_stock_status(item, price: float | None) -> str:
        """Infer stock status from the search-result card.

        Amazon search results are noisy, so we are conservative:
        - Explicit unavailable phrases -> out_of_stock
        - A price is present, no unavailable phrase, and a positive
          availability signal (e.g. "Lieferung", "Auf Lager", "Prime") -> in_stock
        - Everything else -> unknown (avoids false "in stock" claims)
        """
        text = await item.inner_text()
        lower = text.lower()
        unavailable_markers = [
            "derzeit nicht verfügbar",
            "temporär nicht verfügbar",
            "nicht verfügbar",
            "nicht auf lager",
            "nicht lieferbar",
            "nicht mehr verfügbar",
            "ausverkauft",
            "vergriffen",
            "currently unavailable",
            "temporarily out of stock",
            "out of stock",
            "sold out",
            "kein angebot",
            "keine angebote verfügbar",
            "keine hervorgehobenen angebote",
            "no offers",
            "no featured offers",
            "unavailable",
            "nur noch",
            "nur",
        ]
        if any(marker in lower for marker in unavailable_markers):
            return "out_of_stock"

        if price is None:
            return "unknown"

        # A price alone is not enough; require an explicit positive signal.
        positive_markers = [
            "auf lager",
            "lieferbar",
            "versandt",
            "versand",
            "lieferung",
            "prime",
            "morgen",
            "heute",
            "sofort",
            "gewöhnlich versandfertig",
            "in stock",
            "available",
            "in den warenkorb",
            "jetzt kaufen",
            "sofort kaufen",
            "kaufen",
            "add to basket",
            "buy now",
        ]
        if any(marker in lower for marker in positive_markers):
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
