"""
Core Middleware Package

Provides reusable middleware classes for cross-cutting concerns:

- :class:`BaseMiddleware` — Abstract base with ``process_request`` /
  ``process_response`` hooks.
- :class:`RequestLoggingMiddleware` — Structured request/response logging.
- :class:`SecurityHeadersMiddleware` — Adds security-related HTTP headers.
- :class:`RateLimitingMiddleware` — In-memory per-IP rate limiting.
- :class:`TimezoneMiddleware` — Activates the authenticated user's timezone.
- :class:`SentryContextMiddleware` — Enriches Sentry events with user,
  tenant, and request context.

Tenant-specific middleware lives in :mod:`apps.tenants.middleware`.
"""

from apps.core.middleware.base import BaseMiddleware
from apps.core.middleware.request_logging import RequestLoggingMiddleware
from apps.core.middleware.security import SecurityHeadersMiddleware
from apps.core.middleware.rate_limiting import RateLimitingMiddleware
from apps.core.middleware.timezone import TimezoneMiddleware
from apps.core.middleware.sentry import SentryContextMiddleware

__all__ = [
    "BaseMiddleware",
    "RequestLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "RateLimitingMiddleware",
    "TimezoneMiddleware",
    "SentryContextMiddleware",
]
