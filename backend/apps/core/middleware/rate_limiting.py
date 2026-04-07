"""
Rate Limiting Middleware.

Provides a lightweight, in-memory per-IP rate limiter for general use.
For production environments, a Redis-backed solution (e.g. django-ratelimit,
DRF throttling) is recommended — this middleware serves as a safety net.

Enable by adding to ``MIDDLEWARE``::

    MIDDLEWARE = [
        ...
        "apps.core.middleware.RateLimitingMiddleware",
        ...
    ]

Configure via settings::

    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100      # Max requests per window
    RATE_LIMIT_WINDOW_SECONDS = 60 # Rolling window in seconds
    RATE_LIMIT_SKIP_PATHS = ["/health/", "/readyz/"]
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from threading import Lock
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse

from apps.core.middleware.base import BaseMiddleware

logger = logging.getLogger("apps.core.middleware.rate_limiting")

# Defaults
_DEFAULT_MAX_REQUESTS = 100
_DEFAULT_WINDOW_SECONDS = 60
_DEFAULT_SKIP_PATHS = ("/health/", "/readyz/")


class _TokenBucket:
    """Simple per-key token bucket stored in memory."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window: float) -> bool:
        now = time.monotonic()
        with self._lock:
            timestamps = self._buckets[key]
            # Purge expired entries
            cutoff = now - window
            self._buckets[key] = [t for t in timestamps if t > cutoff]
            if len(self._buckets[key]) >= max_requests:
                return False
            self._buckets[key].append(now)
            return True

    def remaining(self, key: str, max_requests: int, window: float) -> int:
        now = time.monotonic()
        with self._lock:
            cutoff = now - window
            active = [t for t in self._buckets.get(key, []) if t > cutoff]
            return max(0, max_requests - len(active))


# Module-level singleton so state persists across requests.
_bucket = _TokenBucket()


class RateLimitingMiddleware(BaseMiddleware):
    """
    In-memory per-IP rate limiter.

    Returns HTTP 429 with a JSON body when the limit is exceeded.
    Adds ``X-RateLimit-Remaining`` header to every allowed response.
    """

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        if not self._is_enabled():
            return None
        if self._should_skip(request.path):
            return None

        ip = self._get_client_ip(request)
        max_requests = getattr(
            settings, "RATE_LIMIT_REQUESTS", _DEFAULT_MAX_REQUESTS
        )
        window = getattr(
            settings, "RATE_LIMIT_WINDOW_SECONDS", _DEFAULT_WINDOW_SECONDS
        )

        if not _bucket.is_allowed(ip, max_requests, window):
            logger.warning("Rate limit exceeded for IP %s on %s", ip, request.path)
            return JsonResponse(
                {
                    "success": False,
                    "error": {
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                    },
                },
                status=429,
                headers={"Retry-After": str(window)},
            )

        # Stash remaining count for process_response
        request._lcc_rate_remaining = _bucket.remaining(  # type: ignore[attr-defined]
            ip, max_requests, window
        )
        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        remaining = getattr(request, "_lcc_rate_remaining", None)
        if remaining is not None:
            response["X-RateLimit-Remaining"] = str(remaining)
        return response

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_enabled() -> bool:
        return getattr(settings, "RATE_LIMIT_ENABLED", True)

    @staticmethod
    def _should_skip(path: str) -> bool:
        skip_paths = getattr(settings, "RATE_LIMIT_SKIP_PATHS", _DEFAULT_SKIP_PATHS)
        return any(path.startswith(p) for p in skip_paths)

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
