"""Demo spider returning sample listings for local development and UI testing."""

from app.spiders.base import ListingSnapshot, Spider


class DemoSpider(Spider):
    """Returns synthetic listings so the platform works without real scraping."""

    def __init__(self, retailer_id: int):
        super().__init__(retailer_id, affiliate_tag=None)

    @property
    def name(self) -> str:
        return "Demo Retailer"

    @property
    def country(self) -> str:
        return "DEMO"

    async def fetch_listings(
        self, query: str, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        # Ignore the query and return a curated set of portable ACs.
        return [
            ListingSnapshot(
                name="Midea Mobile Air Conditioner 9000 BTU",
                brand="Midea",
                sku="DEMO-001",
                url="https://example.com/midea-9000",
                price=349.99,
                currency="EUR",
                stock_status="in_stock",
                delivery_days=2,
                image_url="https://via.placeholder.com/300x300?text=Midea+9000BTU",
                btu_min=9000,
                btu_max=9000,
                product_type=product_type or "portable",
            ),
            ListingSnapshot(
                name="De'Longhi Pinguino 12000 BTU WiFi",
                brand="De'Longhi",
                sku="DEMO-002",
                url="https://example.com/delonghi-12000",
                price=549.0,
                currency="EUR",
                stock_status="out_of_stock",
                delivery_days=None,
                image_url="https://via.placeholder.com/300x300?text=DeLonghi+12000BTU",
                btu_min=12000,
                btu_max=12000,
                product_type=product_type or "portable",
            ),
            ListingSnapshot(
                name="TCL 7000 BTU Portable AC for Small Rooms",
                brand="TCL",
                sku="DEMO-003",
                url="https://example.com/tcl-7000",
                price=279.0,
                currency="EUR",
                stock_status="back_order",
                delivery_days=7,
                image_url="https://via.placeholder.com/300x300?text=TCL+7000BTU",
                btu_min=7000,
                btu_max=7000,
                product_type=product_type or "portable",
            ),
            ListingSnapshot(
                name="Honeywell MN12CES 12000 BTU Portable Air Conditioner",
                brand="Honeywell",
                sku="DEMO-004",
                url="https://example.com/honeywell-12000",
                price=499.99,
                currency="EUR",
                stock_status="in_stock",
                delivery_days=1,
                image_url="https://via.placeholder.com/300x300?text=Honeywell+12000BTU",
                btu_min=12000,
                btu_max=12000,
                product_type=product_type or "portable",
            ),
        ]
