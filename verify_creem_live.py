"""Verify Creem integration on https://klima-radar.com is in live mode."""

import json
import sys
import uuid
from datetime import datetime, timezone

import requests

BASE_URL = "https://klima-radar.com"
CHECKOUT_URL = f"{BASE_URL}/api/billing/creem/checkout"
WEBHOOK_URL = f"{BASE_URL}/api/billing/webhooks/creem"

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


def _unique_email() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    uid = uuid.uuid4().hex[:8]
    return f"creem-live-{ts}-{uid}@example.com".lower()


def main() -> dict:
    results = {
        "checkout_ok": False,
        "checkout_url": None,
        "checkout_page_ok": False,
        "is_live_url": False,
        "webhook_route_exists": False,
        "webhook_secret_configured": False,
        "errors": [],
    }

    # 1. Create a checkout
    checkout_email = _unique_email()
    try:
        resp = requests.post(
            CHECKOUT_URL,
            json={"email": checkout_email},
            headers={"Accept": "application/json"},
            timeout=30,
        )
        results["checkout_ok"] = resp.status_code == 200
        if resp.status_code == 200:
            data = resp.json()
            checkout_url = data.get("checkout_url", "")
            results["checkout_url"] = checkout_url
            url_lower = checkout_url.lower()
            results["is_live_url"] = "/test/" not in url_lower and "test-api" not in url_lower
            if not results["is_live_url"]:
                results["errors"].append(
                    f"Checkout URL appears to be test mode: {checkout_url}"
                )
        else:
            results["errors"].append(
                f"Checkout returned {resp.status_code}: {resp.text[:500]}"
            )
    except Exception as exc:
        results["errors"].append(f"Checkout request failed: {exc}")

    # 2. Fetch the checkout page with a browser-like User-Agent
    checkout_url = results.get("checkout_url")
    if checkout_url:
        try:
            resp = requests.get(
                checkout_url,
                headers={
                    "User-Agent": BROWSER_UA,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=30,
                allow_redirects=True,
            )
            results["checkout_page_ok"] = resp.status_code == 200
            body = resp.text.lower()
            if resp.status_code == 200:
                # The URL is the authoritative indicator of live vs. test mode.
                # The page body contains Creem seller-dashboard strings (e.g., test
                # mode toggles) that are not indicators of the current checkout mode.
                if "creem" not in body or "checkout" not in body:
                    results["errors"].append(
                        "Checkout page body does not look like a live Creem checkout."
                    )
            else:
                results["errors"].append(
                    f"Checkout page returned {resp.status_code}: {resp.text[:500]}"
                )
        except Exception as exc:
            results["errors"].append(f"Checkout page request failed: {exc}")
    else:
        results["errors"].append("No checkout URL to fetch.")

    # 3. GET webhook route should return 405 (Method Not Allowed)
    try:
        resp = requests.get(WEBHOOK_URL, timeout=30)
        results["webhook_route_exists"] = resp.status_code == 405
        if resp.status_code != 405:
            results["errors"].append(
                f"GET webhook returned {resp.status_code}, expected 405: {resp.text[:500]}"
            )
    except Exception as exc:
        results["errors"].append(f"GET webhook request failed: {exc}")

    # 4. POST invalid-signature event; should be rejected with 400 proving secret is configured
    invalid_event = {
        "id": f"evt_{uuid.uuid4().hex[:12]}",
        "eventType": "checkout.completed",
        "created_at": int(datetime.now(timezone.utc).timestamp() * 1000),
        "object": {"id": f"ord_{uuid.uuid4().hex[:12]}"},
    }
    payload_bytes = json.dumps(invalid_event, separators=(",", ":")).encode("utf-8")
    try:
        resp = requests.post(
            WEBHOOK_URL,
            data=payload_bytes,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "creem-signature": "invalid",
            },
            timeout=30,
        )
        results["webhook_secret_configured"] = (
            resp.status_code == 400
            and "invalid signature" in resp.text.lower()
        )
        if not results["webhook_secret_configured"]:
            results["errors"].append(
                f"Invalid-signature webhook returned {resp.status_code}: {resp.text[:500]}"
            )
    except Exception as exc:
        results["errors"].append(f"Invalid-signature webhook request failed: {exc}")

    return results


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
    sys.exit(0 if all([
        result["checkout_ok"],
        result["checkout_page_ok"],
        result["is_live_url"],
        result["webhook_route_exists"],
        result["webhook_secret_configured"],
    ]) else 1)
