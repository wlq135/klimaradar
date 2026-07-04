"""Spiders package — retailer-specific inventory fetchers."""

from app.spiders.base import ListingSnapshot, Spider
from app.spiders.registry import get_spiders_for_country

__all__ = ["ListingSnapshot", "Spider", "get_spiders_for_country"]
