"""Simple in-memory rate limiting for MVP.

NOTE: This stores counters in process memory. If you run multiple workers,
use a shared store (Redis) instead.
"""

import asyncio
import time
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request


class RateLimiter:
    """Sliding-window rate limiter keyed by a string extracted from the request."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> None:
        now = time.monotonic()
        async with self._lock:
            timestamps = self._store[key]
            # Drop old entries outside the window.
            cutoff = now - self.window_seconds
            self._store[key] = [ts for ts in timestamps if ts > cutoff]
            if len(self._store[key]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please slow down and try again later.",
                )
            self._store[key].append(now)

    def dependency(self, key_func: Callable[[Request], str]):
        async def _limit(request: Request) -> None:
            key = key_func(request)
            await self.check(key)

        return _limit


# 5 subscription attempts per minute per IP.
subscribe_limiter = RateLimiter(max_requests=5, window_seconds=60)

# 10 admin scrape calls per minute per IP.
admin_scrape_limiter = RateLimiter(max_requests=10, window_seconds=60)

# 3 feedback submissions per minute per IP.
feedback_limiter = RateLimiter(max_requests=3, window_seconds=60)
