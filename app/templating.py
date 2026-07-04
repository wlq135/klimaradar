"""Jinja2 template environment setup."""

from pathlib import Path

from fastapi.templating import Jinja2Templates

TEMPLATE_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def format_price(value: float | None, currency: str = "EUR") -> str:
    if value is None:
        return "N/A"
    return f"€{value:,.2f}" if currency == "EUR" else f"{value:,.2f} {currency}"


def stock_label(status: str) -> str:
    labels = {
        "in_stock": "In Stock",
        "low_stock": "Low Stock",
        "out_of_stock": "Out of Stock",
        "back_order": "Back Order",
        "pre_order": "Pre-Order",
        "unknown": "Unknown",
    }
    return labels.get(status, status.replace("_", " ").title())


templates.env.filters["price"] = format_price
templates.env.filters["stock_label"] = stock_label
