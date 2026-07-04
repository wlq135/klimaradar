"""SQLAlchemy ORM models for KlimaRadar."""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class StockStatus(str, enum.Enum):
    """Possible availability states for a listing."""

    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    BACK_ORDER = "back_order"
    PRE_ORDER = "pre_order"
    UNKNOWN = "unknown"


class ProductType(str, enum.Enum):
    """Broad categories of cooling devices."""

    PORTABLE = "portable"
    WINDOW = "window"
    SPLIT = "split"
    EVAPORATIVE = "evaporative"


class Product(Base):
    """A canonical product (e.g. Midea 9000 BTU portable AC)."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    product_type: Mapped[str] = mapped_column(
        String(20), default=ProductType.PORTABLE.value, nullable=False
    )
    btu_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    btu_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    noise_db: Mapped[int | None] = mapped_column(Integer, nullable=True)
    energy_label: Mapped[str | None] = mapped_column(String(10), nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    specs_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    listings: Mapped[list["Listing"]] = relationship(
        "Listing", back_populates="product", lazy="selectin"
    )


class Retailer(Base):
    """A retailer or marketplace that sells AC units."""

    __tablename__ = "retailers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    affiliate_network: Mapped[str | None] = mapped_column(String(50), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    listings: Mapped[list["Listing"]] = relationship(
        "Listing", back_populates="retailer", lazy="selectin"
    )


class Listing(Base):
    """A specific retailer offering for a product."""

    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    retailer_id: Mapped[int] = mapped_column(
        ForeignKey("retailers.id"), nullable=False, index=True
    )
    sku: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    affiliate_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    stock_status: Mapped[str] = mapped_column(
        String(20), default=StockStatus.UNKNOWN.value, nullable=False
    )
    delivery_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    city_tag: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    product: Mapped["Product"] = relationship("Product", back_populates="listings")
    retailer: Mapped["Retailer"] = relationship("Retailer", back_populates="listings")
    price_history: Mapped[list["PriceHistory"]] = relationship(
        "PriceHistory", back_populates="listing", lazy="selectin"
    )


class PriceHistory(Base):
    """Snapshot of a listing's price and stock status over time."""

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id"), nullable=False, index=True
    )
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    stock_status: Mapped[str] = mapped_column(
        String(20), default=StockStatus.UNKNOWN.value, nullable=False
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    listing: Mapped["Listing"] = relationship("Listing", back_populates="price_history")


class AlertSubscription(Base):
    """User request to be notified when matching listings change."""

    __tablename__ = "alert_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    city: Mapped[str | None] = mapped_column(String(50), nullable=True)
    product_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    min_btu: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    in_stock_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    alert_logs: Mapped[list["AlertLog"]] = relationship(
        "AlertLog", back_populates="subscription", lazy="selectin"
    )


class AlertLog(Base):
    """Record of an alert that was sent to a subscriber."""

    __tablename__ = "alert_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("alert_subscriptions.id"), nullable=False, index=True
    )
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id"), nullable=False, index=True
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(String(20), default="email", nullable=False)
    clicked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    subscription: Mapped["AlertSubscription"] = relationship(
        "AlertSubscription", back_populates="alert_logs"
    )


class ClickEvent(Base):
    """Outbound affiliate link click for analytics."""

    __tablename__ = "click_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id"), nullable=False, index=True
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
