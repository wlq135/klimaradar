"""Affiliate link tagging helpers."""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from app.config import settings


# Maps retailer domain (without www) to the query parameter name used for the
# affiliate identifier on that site.
_AFFILIATE_PARAMS = {
    "amazon.co.uk": "tag",
    "amazon.de": "tag",
    "amazon.com": "tag",
    "amazon.fr": "tag",
    "amazon.it": "tag",
    "amazon.es": "tag",
    "amazon.nl": "tag",
    "amazon.be": "tag",
    "amazon.com.be": "tag",
    "mediamarkt.de": "ref",
    "boulanger.com": "ref",
    "boulanger.fr": "ref",
    "darty.com": "ref",
    "darty.fr": "ref",
}


_AMAZON_DOMAINS = {
    "amazon.co.uk",
    "amazon.de",
    "amazon.com",
    "amazon.fr",
    "amazon.it",
    "amazon.es",
    "amazon.nl",
    "amazon.be",
    "amazon.com.be",
}


def _normalize_domain(domain: str | None) -> str:
    """Return a lower-case netloc without scheme or www prefix."""
    if not domain:
        return ""
    domain = domain.strip().lower()
    if domain.startswith(("http://", "https://")):
        domain = urlparse(domain).netloc
    return domain.removeprefix("www.")


def _affiliate_tag_for(domain: str) -> str | None:
    """Return the configured affiliate tag for a normalized retailer domain."""
    if domain in _AMAZON_DOMAINS:
        # Map each Amazon TLD to its country-specific tag setting.
        mapping = {
            "amazon.co.uk": settings.amazon_uk_affiliate_tag,
            "amazon.de": settings.amazon_de_affiliate_tag,
            "amazon.com": settings.amazon_de_affiliate_tag,
            "amazon.fr": settings.amazon_fr_affiliate_tag,
            "amazon.it": settings.amazon_it_affiliate_tag,
            "amazon.es": settings.amazon_es_affiliate_tag,
            "amazon.nl": settings.amazon_nl_affiliate_tag,
            "amazon.be": settings.amazon_be_affiliate_tag,
            "amazon.com.be": settings.amazon_be_affiliate_tag,
        }
        return mapping.get(domain) or None
    if domain == "mediamarkt.de":
        return settings.mediamarkt_de_affiliate_tag or None
    if domain in ("boulanger.com", "boulanger.fr"):
        return settings.boulanger_fr_affiliate_tag or None
    if domain in ("darty.com", "darty.fr"):
        return settings.darty_fr_affiliate_tag or None
    return None


def tag_url(retailer_domain: str, url: str | None) -> str | None:
    """Add an affiliate tracking parameter to a retailer URL if configured.

    For Amazon domains this appends the ``tag`` parameter. For MediaMarkt and
    Boulanger it appends ``ref``. The ``retailer_domain`` may be a bare domain
    (``amazon.de``) or a full URL (``https://www.amazon.de``).
    """
    if not url:
        return url

    parsed = urlparse(url)
    domain = _normalize_domain(parsed.netloc) or _normalize_domain(retailer_domain)

    param_name = _AFFILIATE_PARAMS.get(domain)
    tag_value = _affiliate_tag_for(domain)
    if not tag_value or not param_name:
        return url

    query = parse_qs(parsed.query, keep_blank_values=True)
    query[param_name] = [tag_value]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def _safe_subtag_segment(value: str | int | None, fallback: str) -> str:
    """Keep Amazon's customer-defined subtag short and URL-safe."""
    text = str(value or fallback).strip().lower()
    cleaned = "".join(char if char.isalnum() else "-" for char in text)
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:32] or fallback


def build_amazon_subtag(
    *,
    click_id: int,
    country: str,
    source: str | None,
    placement: str | None,
    position: int | None,
) -> str:
    """Build a compact subtag that can be joined back to ClickEvent.id.

    Amazon reports show customer-defined subtags, but not our database rows.
    Embedding the click ID lets an Amazon order be joined back to the exact
    on-site placement without exposing user information.
    """
    return "-".join(
        [
            "v1",
            _safe_subtag_segment(click_id, "0"),
            _safe_subtag_segment(country, "xx"),
            _safe_subtag_segment(source, "direct"),
            _safe_subtag_segment(placement, "unknown"),
            _safe_subtag_segment(position, "0"),
        ]
    )[:100]


def add_amazon_subtag(url: str | None, subtag: str) -> str | None:
    """Append an Amazon ``ascsubtag`` without replacing existing parameters."""
    if not url:
        return url

    parsed = urlparse(url)
    domain = _normalize_domain(parsed.netloc)
    if domain not in _AMAZON_DOMAINS:
        return url

    query = parse_qs(parsed.query, keep_blank_values=True)
    query["ascsubtag"] = [subtag[:100]]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))
