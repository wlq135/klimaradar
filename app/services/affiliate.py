"""Affiliate link tagging helpers."""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from app.config import settings


# Maps retailer domain (without www) to the query parameter name used for the
# affiliate identifier on that site.
_AFFILIATE_PARAMS = {
    "amazon.de": "tag",
    "amazon.com": "tag",
    "mediamarkt.de": "ref",
    "boulanger.com": "ref",
    "boulanger.fr": "ref",
    "darty.com": "ref",
    "darty.fr": "ref",
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
    if domain in ("amazon.de", "amazon.com"):
        return settings.amazon_de_affiliate_tag or None
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
