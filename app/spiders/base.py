"""Base spider interface used by the scraper service."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ListingSnapshot:
    """A normalized, retailer-agnostic snapshot of one listing."""

    name: str
    brand: str | None
    sku: str | None
    url: str
    price: float | None
    currency: str
    stock_status: str
    delivery_days: int | None
    image_url: str | None
    btu_min: int | None
    btu_max: int | None
    product_type: str
    specs_json: str | None = None


class Spider(ABC):
    """Abstract base class for all retailer spiders."""

    def __init__(self, retailer_id: int, affiliate_tag: str | None = None):
        self.retailer_id = retailer_id
        self.affiliate_tag = affiliate_tag

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable spider name."""

    @property
    @abstractmethod
    def country(self) -> str:
        """ISO-3166-1 alpha-2 country code."""

    @abstractmethod
    async def fetch_listings(
        self, query: str, product_type: str | None = None
    ) -> list[ListingSnapshot]:
        """Fetch and normalize listings for a search query."""
