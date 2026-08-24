"""Small bounded TTL cache for expensive public page data."""

import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

from app.config import settings


T = TypeVar("T")


class TTLCache(Generic[T]):
    """Bounded monotonic-time cache for a single web process."""

    def __init__(self, max_items: int = 256) -> None:
        self.max_items = max_items
        self._items: OrderedDict[str, tuple[float, T]] = OrderedDict()

    def get(self, key: str) -> T | None:
        entry = self._items.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at <= time.monotonic():
            self._items.pop(key, None)
            return None
        self._items.move_to_end(key)
        return value

    def set(self, key: str, value: T, ttl_seconds: float) -> None:
        self._items[key] = (time.monotonic() + ttl_seconds, value)
        self._items.move_to_end(key)
        while len(self._items) > self.max_items:
            self._items.popitem(last=False)

    def clear(self) -> None:
        self._items.clear()


public_page_cache: TTLCache[object] = TTLCache(max_items=256)


async def get_or_compute(
    key: str,
    ttl_seconds: float,
    producer: Callable[[], Awaitable[T]],
) -> T:
    """Return cached production data, while keeping local debug requests live."""
    if settings.debug:
        return await producer()

    cached_value = public_page_cache.get(key)
    if cached_value is not None:
        return cached_value  # type: ignore[return-value]

    value = await producer()
    public_page_cache.set(key, value, ttl_seconds)  # type: ignore[arg-type]
    return value
