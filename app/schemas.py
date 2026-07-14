"""Pydantic schemas for API requests/responses."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ProductBase(BaseModel):
    name: str
    brand: str | None = None
    product_type: str = "portable"
    btu_min: int | None = None
    btu_max: int | None = None
    noise_db: int | None = None
    energy_label: str | None = None
    image_url: str | None = None
    specs_json: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class RetailerBase(BaseModel):
    name: str
    country: str = Field(..., min_length=2, max_length=2)
    domain: str
    affiliate_network: str | None = None
    logo_url: str | None = None


class RetailerCreate(RetailerBase):
    pass


class RetailerOut(RetailerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ListingBase(BaseModel):
    product_id: int
    retailer_id: int
    sku: str | None = None
    url: str
    affiliate_url: str | None = None
    price: float | None = None
    currency: str | None = "EUR"
    stock_status: str = "unknown"
    delivery_days: int | None = None
    country: str = Field(..., min_length=2, max_length=2)
    city_tag: str | None = None


class ListingCreate(ListingBase):
    pass


class ListingOut(ListingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product: ProductOut
    retailer: RetailerOut


class PriceHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int
    price: float | None
    stock_status: str
    captured_at: str


class AlertSubscriptionCreate(BaseModel):
    email: EmailStr
    country: str = Field(..., min_length=2, max_length=2)
    city: str | None = None
    product_type: str | None = "portable"
    min_btu: int | None = None
    max_price: float | None = None
    in_stock_only: bool = True
    frequency: str = "immediate"

    @field_validator("city", "product_type", mode="before")
    @classmethod
    def _blank_to_none(cls, value):
        return None if value == "" else value

    @field_validator("min_btu", "max_price", mode="before")
    @classmethod
    def _blank_numeric_to_none(cls, value):
        if value == "" or value is None:
            return None
        return value

    @field_validator("frequency", mode="before")
    @classmethod
    def _valid_frequency(cls, value):
        value = (value or "immediate").lower()
        if value not in {"immediate", "daily"}:
            raise ValueError("frequency must be 'immediate' or 'daily'")
        return value


class AlertSubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    country: str
    city: str | None
    product_type: str | None
    min_btu: int | None
    max_price: float | None
    in_stock_only: bool
    frequency: str
    verified: bool
    active: bool
    created_at: str


class SearchFilters(BaseModel):
    country: str = "DE"
    city: str | None = None
    product_type: str | None = "portable"
    min_btu: int | None = None
    max_price: float | None = None
    in_stock_only: bool = False
    q: str | None = None


class StatsOut(BaseModel):
    total_listings: int
    in_stock_listings: int
    active_subscriptions: int
    countries: list[str]


class FeedbackCreate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    message: str = Field(..., min_length=2, max_length=5000)
    page_url: str | None = None

    @field_validator("name", "email", "page_url", mode="before")
    @classmethod
    def _blank_to_none(cls, value):
        return None if value == "" else value

    @field_validator("message", mode="before")
    @classmethod
    def _strip_message(cls, value):
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Message is required")
        return value
