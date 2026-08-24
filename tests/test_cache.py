"""Tests for the bounded public-page cache."""

import pytest

from app.config import settings
from app.services.cache import TTLCache, get_or_compute, public_page_cache


@pytest.mark.asyncio
async def test_get_or_compute_caches_production_values(monkeypatch):
    public_page_cache.clear()
    monkeypatch.setattr(settings, "debug", False)
    calls = 0

    async def produce():
        nonlocal calls
        calls += 1
        return {"listings": [1, 2, 3]}

    first = await get_or_compute("test:key", 60, produce)
    second = await get_or_compute("test:key", 60, produce)

    assert first == second == {"listings": [1, 2, 3]}
    assert calls == 1
    public_page_cache.clear()


@pytest.mark.asyncio
async def test_get_or_compute_bypasses_debug(monkeypatch):
    public_page_cache.clear()
    monkeypatch.setattr(settings, "debug", True)
    calls = 0

    async def produce():
        nonlocal calls
        calls += 1
        return calls

    assert await get_or_compute("test:debug", 60, produce) == 1
    assert await get_or_compute("test:debug", 60, produce) == 2


def test_ttl_cache_is_bounded():
    cache = TTLCache(max_items=2)
    cache.set("one", 1, 60)
    cache.set("two", 2, 60)
    cache.set("three", 3, 60)

    assert cache.get("one") is None
    assert cache.get("two") == 2
    assert cache.get("three") == 3
