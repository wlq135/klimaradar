"""Boulanger France spider using Playwright.

WARNING: As of 2026-07, Boulanger.com is protected by DataDome and serves a
challenge page to headless browsers. This spider uses the anti-detection init
script and proxy support from ``PlaywrightSpider``, plus robust selectors and a
short wait. Without a working proxy it will usually return 0 listings.
"""

from urllib.parse import urljoin

from playwright.async_api import Page

from app.spiders.base import ListingSnapshot
from app.spiders.playwright_base import PlaywrightSpider


class BoulangerFrSpider(PlaywrightSpider):
    """Scrape Boulanger.fr mobile AC category page."""

    @property
    def name(self) -> str:
        return "Boulanger France"

    @property
    def search_url_template(self) -> str:
        # Boulanger search URL; their category listing URL is more stable.
        return "https://www.boulanger.com/resultats?recherche={query}"

    default_query: str = "climatiseur portable"

    async def _extract_listings(
        self, page: Page, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        # Wait a moment for React/SSR hydration and delayed product renders.
        await page.wait_for_timeout(2000)

        # If we landed on a challenge/blocked page, there will be no products.
        product_cards = await page.query_selector_all(
            ".product-list .product-item, "
            "[data-testid='product-list'] > div, "
            ".c-product-list__item, "
            ".product-grid article, "
            ".product-card, "
            "[class*='productList'] > [class*='product']"
        )

        snapshots: list[ListingSnapshot] = []
        for card in product_cards:
            title_el = await card.query_selector(
                ".product-title, "
                "[data-testid='product-title'], "
                "h3.product-name, "
                ".c-product-card__title, "
                "a[class*='title'], "
                "h2, h3"
            )
            title = await title_el.inner_text() if title_el else None
            if not title:
                continue

            link_el = await card.query_selector(
                ".product-link, "
                "a[href*='/ref/'], "
                "a[href*='/produit/'], "
                "a"
            )
            href = await link_el.get_attribute("href") if link_el else None
            url = urljoin("https://www.boulanger.com", href) if href else ""

            price_el = await card.query_selector(
                ".price-current, "
                ".price--current, "
                "[data-testid='price'], "
                ".c-price__value, "
                ".price, "
                "span[class*='price']"
            )
            price_text = await price_el.inner_text() if price_el else None
            price = self._parse_price_text(price_text)

            img_el = await card.query_selector(
                ".product-image img, "
                "[data-testid='product-image'], "
                ".c-product-card__image, "
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

        Boulanger cards sometimes keep a price on sold-out items. We therefore
        require explicit signals and never assume price == in stock.
        """
        text = await card.inner_text()
        lower = text.lower()
        unavailable_markers = [
            "indisponible",
            "rupture de stock",
            "en rupture",
            "épuisé",
            "non disponible",
            "victime de son succès",
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
