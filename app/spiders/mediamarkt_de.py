"""MediaMarkt Germany spider using Playwright + Apollo state JSON."""

import json
import re
from datetime import datetime, timezone
from urllib.parse import urljoin

from playwright.async_api import Page

from app.spiders.base import ListingSnapshot
from app.spiders.playwright_base import PlaywrightSpider


class MediaMarktDeSpider(PlaywrightSpider):
    """Scrape MediaMarkt.de search results.

    MediaMarkt renders product data into ``window.__PRELOADED_STATE__`` as an
    Apollo normalized cache. We extract that JSON and map the relevant entities.
    """

    @property
    def name(self) -> str:
        return "MediaMarkt Germany"

    @property
    def search_url_template(self) -> str:
        return "https://www.mediamarkt.de/de/search.html?query={query}"

    default_query: str = "mobiles klimagerät"

    async def _extract_listings(
        self, page: Page, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        await page.wait_for_timeout(3000)
        html = await page.content()
        state = self._extract_preloaded_state(html)

        product_keys = [k for k in state.keys() if k.startswith("GraphqlProduct:")]
        snapshots: list[ListingSnapshot] = []
        for key in product_keys:
            product = state[key]
            pid = product["id"]
            price_feature = state.get(f"CofrPriceFeature:Media:de:{pid}")
            status_feature = state.get(f"CofrOnlineStatusFeature:Media:de:{pid}")
            media_feature = state.get(f"CofrMediaAssetsFeature:Media:de:{pid}")
            delivery_feature = state.get(f"CofrDeliveryFeature:Media:de:{pid}")

            price = None
            if price_feature and price_feature.get("price"):
                price = price_feature["price"].get("amount")

            stock_status = "unknown"
            if status_feature:
                if status_feature.get("isAvailableAndBuyable"):
                    stock_status = "in_stock"
                else:
                    stock_status = "out_of_stock"

            image_url = None
            if media_feature and media_feature.get("productMainImage"):
                image_url = media_feature["productMainImage"].get("link")

            delivery_days = self._delivery_days(delivery_feature)
            relative_url = product.get("url") or (
                media_feature.get("urlRelative") if media_feature else None
            )
            url = (
                urljoin("https://www.mediamarkt.de", relative_url)
                if relative_url
                else f"https://www.mediamarkt.de/de/product/{pid}.html"
            )

            snapshots.append(
                ListingSnapshot(
                    name=product.get("title", "").strip(),
                    brand=product.get("manufacturer"),
                    sku=pid,
                    url=url,
                    price=price,
                    currency="EUR",
                    stock_status=stock_status,
                    delivery_days=delivery_days,
                    image_url=image_url,
                    btu_min=None,
                    btu_max=None,
                    product_type=product_type or "portable",
                )
            )
        return snapshots

    @staticmethod
    def _extract_preloaded_state(html: str) -> dict:
        match = re.search(
            r"window\.__PRELOADED_STATE__\s*=\s*({.*?});?\s*</script>",
            html,
            re.DOTALL,
        )
        if not match:
            raise ValueError("__PRELOADED_STATE__ not found on MediaMarkt page")
        # The JSON may contain literal ``undefined`` and ``NaN`` values.
        raw = match.group(1).replace("undefined", "null").replace("NaN", "null")
        # Trim a trailing semicolon if present.
        raw = raw.rstrip(";").rstrip()
        data = json.loads(raw)
        return data.get("apolloState", {})

    @staticmethod
    def _delivery_days(delivery_feature: dict | None) -> int | None:
        if not delivery_feature:
            return None
        delivery = delivery_feature.get("delivery") or {}
        fulfillment = delivery.get("fulfillmentTime") or {}
        earliest = fulfillment.get("earliest")
        if not earliest:
            return None
        try:
            earliest_dt = datetime.fromisoformat(earliest.replace("Z", "+00:00"))
            delta = earliest_dt - datetime.now(timezone.utc)
            return max(0, delta.days)
        except ValueError:
            return None
