"""Darty France spider using Playwright.

Darty (part of Fnac Darty) is a major French electronics retailer and serves as
a backup source for French AC listings alongside Boulanger. Like many large
French e-commerce sites, it is JavaScript-heavy and may block headless browsers
without a residential proxy.

This spider reuses the anti-detection init script and optional proxy support
from ``PlaywrightSpider``. Without a working proxy it may return 0 listings.
"""

from urllib.parse import urljoin

from playwright.async_api import Page

from app.spiders.base import ListingSnapshot
from app.spiders.playwright_base import PlaywrightSpider


class DartyFrSpider(PlaywrightSpider):
    """Scrape Darty.fr search results for air conditioners."""

    @property
    def name(self) -> str:
        return "Darty France"

    @property
    def search_url_template(self) -> str:
        return "https://www.darty.com/nav/recherche?p={query}"

    default_query: str = "climatiseur portable"

    async def _extract_listings(
        self, page: Page, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        # Wait briefly for the product grid to render.
        await page.wait_for_timeout(2500)

        # Try the modern product grid first, then older/fallback layouts.
        product_cards = await page.query_selector_all(
            ".product-list__item, "
            ".product-grid__item, "
            ".prd-list .prd, "
            "[data-testid='product-list-item'], "
            ".darty_product, "
            ".product-tile"
        )

        snapshots: list[ListingSnapshot] = []
        for card in product_cards:
            title_el = await card.query_selector(
                ".product-name, "
                ".product-title, "
                ".darty_prd_name, "
                "a[href*='/produit/'] span, "
                "h3, h2"
            )
            title = await title_el.inner_text() if title_el else None
            if not title:
                continue

            link_el = await card.query_selector(
                "a[href*='/produit/'], "
                "a[href*='/nav/achat/'], "
                ".product-link, "
                "a"
            )
            href = await link_el.get_attribute("href") if link_el else None
            url = urljoin("https://www.darty.com", href) if href else ""

            price_el = await card.query_selector(
                ".product-price, "
                ".price-current, "
                ".darty_prix, "
                ".darty_price, "
                "span[class*='price']"
            )
            price_text = await price_el.inner_text() if price_el else None
            price = self._parse_price_text(price_text)

            img_el = await card.query_selector(
                ".product-image img, "
                ".product-img img, "
                ".darty_prd_img img, "
                "img"
            )
            img_url = await img_el.get_attribute("src") if img_el else None

            stock_status = await self._infer_stock_status(card, price)

            snapshots.append(
                ListingSnapshot(
                    name=title.strip(),
                    brand=None,
                    sku=None,
                    url=url,
                    price=price,
                    currency="EUR",
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
    def _parse_price_text(text: str | None) -> float | None:
        if not text:
            return None
        digits = "".join(c for c in text if c.isdigit() or c in ",.")
        if not digits:
            return None
        digits = digits.replace(",", ".")
        parts = digits.split(".")
        if len(parts) > 2:
            digits = "".join(parts[:-1]) + "." + parts[-1]
        try:
            return float(digits)
        except ValueError:
            return None

    @staticmethod
    async def _infer_stock_status(card, price: float | None) -> str:
        """Infer stock status from the product card text.

        Darty cards may display a price even when the item is unavailable, so we
        require explicit availability signals rather than assuming price == stock.
        """
        text = await card.inner_text()
        lower = text.lower()
        unavailable_markers = [
            "indisponible",
            "rupture de stock",
            "en rupture",
            "épuisé",
            "non disponible",
            "produit épuisé",
        ]
        if any(marker in lower for marker in unavailable_markers):
            return "out_of_stock"

        if price is None:
            return "unknown"

        positive_markers = [
            "en stock",
            "disponible",
            "livraison",
            "retrait",
            "expédié",
        ]
        if any(marker in lower for marker in positive_markers):
            return "in_stock"
        return "unknown"
