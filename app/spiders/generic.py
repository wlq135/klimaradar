"""Generic CSS-selector spider for simple HTML retailer pages."""

from urllib.parse import urlencode, urljoin

import httpx
from bs4 import BeautifulSoup

from app.config import settings
from app.spiders.base import ListingSnapshot, Spider


class GenericHtmlSpider(Spider):
    """A configurable spider that extracts listings from static HTML.

    Retailers are described by a ``SpiderConfig`` dict. This is enough for
    simple search-result pages. JavaScript-heavy sites (Amazon, many modern
    retailers) will need a Playwright-based spider instead.
    """

    def __init__(
        self,
        retailer_id: int,
        config: dict,
        affiliate_tag: str | None = None,
    ):
        super().__init__(retailer_id, affiliate_tag)
        self.config = config

    @property
    def name(self) -> str:
        return self.config["name"]

    @property
    def country(self) -> str:
        return self.config["country"]

    def _build_search_url(self, query: str) -> str:
        template = self.config["search_url_template"]
        params = {self.config.get("query_param", "q"): query}
        if "?" in template:
            return template + "&" + urlencode(params)
        return template + "?" + urlencode(params)

    @staticmethod
    def _extract_text(soup: BeautifulSoup, selector: str | None) -> str | None:
        if not selector:
            return None
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else None

    @staticmethod
    def _extract_attr(
        soup: BeautifulSoup, selector: str | None, attr: str
    ) -> str | None:
        if not selector:
            return None
        element = soup.select_one(selector)
        return element.get(attr) if element else None

    @staticmethod
    def _parse_price(text: str | None) -> float | None:
        if not text:
            return None
        digits = "".join(c for c in text if c.isdigit() or c in ",.")
        if not digits:
            return None
        # Normalize European decimal comma.
        digits = digits.replace(",", ".")
        # If there are multiple dots keep the last as decimal separator.
        parts = digits.split(".")
        if len(parts) > 2:
            digits = "".join(parts[:-1]) + "." + parts[-1]
        try:
            return float(digits)
        except ValueError:
            return None

    @staticmethod
    def _parse_stock(text: str | None, config: dict) -> str:
        if not text:
            return "unknown"
        lowered = text.lower()
        if any(word in lowered for word in config.get("in_stock_words", ["in stock", "available", "auf lager"])):
            return "in_stock"
        if any(word in lowered for word in config.get("out_of_stock_words", ["out of stock", "unavailable", "nicht verfügbar"])):
            return "out_of_stock"
        if any(word in lowered for word in config.get("back_order_words", ["back order", "back-order", "vorbestellung"])):
            return "back_order"
        return "unknown"

    def _tag_url(self, url: str) -> str:
        if not self.affiliate_tag or not url:
            return url
        template = self.config.get("affiliate_url_template")
        if not template:
            sep = "&" if "?" in url else "?"
            return f"{url}{sep}tag={self.affiliate_tag}"
        return template.format(url=url, tag=self.affiliate_tag)

    async def fetch_listings(
        self, query: str, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        url = self._build_search_url(query)
        headers = {"User-Agent": settings.user_agent}
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            follow_redirects=True,
        ) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select(self.config["listing_selector"])
        results: list[ListingSnapshot] = []
        for item in items:
            name = self._extract_text(item, self.config["fields"].get("name"))
            if not name:
                continue
            raw_url = self._extract_attr(item, self.config["fields"].get("url"), "href")
            absolute_url = urljoin(self.config["base_url"], raw_url) if raw_url else ""
            price_text = self._extract_text(item, self.config["fields"].get("price"))
            price = self._parse_price(price_text)
            stock_text = self._extract_text(item, self.config["fields"].get("stock"))
            results.append(
                ListingSnapshot(
                    name=name,
                    brand=self._extract_text(item, self.config["fields"].get("brand")),
                    sku=self._extract_text(item, self.config["fields"].get("sku")),
                    url=absolute_url,
                    price=price,
                    currency=self.config.get("currency", "EUR"),
                    stock_status=self._parse_stock(stock_text, self.config),
                    delivery_days=None,
                    image_url=self._extract_attr(
                        item, self.config["fields"].get("image"), "src"
                    ),
                    btu_min=None,
                    btu_max=None,
                    product_type=product_type or "portable",
                )
            )
        return results
