"""Cloudflare-aware client-IP and scheme helpers."""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """Return the real client IP when behind Cloudflare.

    Cloudflare adds ``CF-Connecting-IP``. If that header is missing we fall back
    to the first entry of ``X-Forwarded-For`` and finally to the transport-level
    client host.
    """
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


def is_cloudflare_request(request: Request) -> bool:
    """Return True if the request appears to come through Cloudflare."""
    return bool(request.headers.get("cf-connecting-ip"))
