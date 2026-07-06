"""Amazon France spider using Playwright."""

from urllib.parse import urljoin

from playwright.async_api import Page

from app.spiders.amazon_de import AmazonDeSpider
from app.spiders.base import ListingSnapshot


class AmazonFrSpider(AmazonDeSpider):
    """Scrape Amazon.fr search results for portable/split/window ACs.

    Reuses the extraction logic from the German spider with French-language
    availability heuristics.
    """

    @property
    def name(self) -> str:
        return "Amazon France"

    @property
    def search_url_template(self) -> str:
        return "https://www.amazon.fr/s?k={query}"

    default_query: str = "climatiseur portable"

    async def _pre_navigate(self, context) -> None:
        # Force EUR currency preference on the French domain before loading the page.
        await context.add_cookies(
            [
                {
                    "name": "i18n-prefs",
                    "value": "EUR",
                    "domain": ".amazon.fr",
                    "path": "/",
                },
                {
                    "name": "session-id",
                    "value": "000-0000000-0000000",
                    "domain": ".amazon.fr",
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

            link_el = await item.query_selector("a.a-link-normal.s-no-outline")
            href = await link_el.get_attribute("href") if link_el else None
            url = urljoin("https://www.amazon.fr", href) if href else f"https://www.amazon.fr/dp/{asin}"

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

    @staticmethod
    async def _infer_stock_status(item, price: float | None) -> str:
        """Infer stock status from the French search-result card.

        Conservative, same philosophy as the German spider:
        - Explicit unavailable phrases -> out_of_stock
        - Price present + positive signal -> in_stock
        - Everything else -> unknown
        """
        text = await item.inner_text()
        lower = text.lower()
        unavailable_markers = [
            "actuellement indisponible",
            "temporairement indisponible",
            "indisponible",
            "en rupture de stock",
            "rupture de stock",
            "épuisé",
            "non disponible",
            "plus disponible",
            "currently unavailable",
            "temporarily out of stock",
            "out of stock",
            "sold out",
            "aucune offre",
            "aucune offre disponible",
            "aucune offre mise en avant",
            "no offers",
            "no featured offers",
            "unavailable",
        ]
        if any(marker in lower for marker in unavailable_markers):
            return "out_of_stock"

        if price is None:
            return "unknown"

        positive_markers = [
            "en stock",
            "disponible",
            "livraison",
            "expédié",
            "prime",
            "demain",
            "aujourd'hui",
            "immédiat",
            "généralement expédié sous",
            "in stock",
            "available",
        ]
        if any(marker in lower for marker in positive_markers):
            return "in_stock"
        return "unknown"
