"""
Request Logging Middleware.

Logs every HTTP request and response with timing, status, path, user,
and tenant information for observability and debugging.

Enable by adding to ``MIDDLEWARE``::

    MIDDLEWARE = [
        "apps.tenants.middleware.LCCTenantMiddleware",
        ...
        "apps.core.middleware.RequestLoggingMiddleware",
        ...
    ]

Control verbosity via settings::

    REQUEST_LOGGING_ENABLED = True          # Toggle on/off
    REQUEST_LOGGING_SKIP_PATHS = [          # Paths to exclude
        "/health/",
        "/readyz/",
        "/static/",
        "/media/",
    ]
    REQUEST_LOGGING_SLOW_THRESHOLD_MS = 500  # Log slow requests at WARNING
"""

from __future__ import annotations

import logging
import time
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from apps.core.middleware.base import BaseMiddleware

logger = logging.getLogger("apps.core.middleware.request_logging")

# Defaults (overridable via Django settings)
_DEFAULT_SKIP_PATHS = ("/health/", "/readyz/", "/static/", "/media/", "/favicon.ico")
_DEFAULT_SLOW_THRESHOLD_MS = 500


class RequestLoggingMiddleware(BaseMiddleware):
    """
    Log HTTP requests with timing information.

    Attaches ``request._lcc_start_time`` in ``process_request`` and
    computes the duration in ``process_response``.
    """

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        if not self._is_enabled():
            return None
        if self._should_skip(request.path):
            return None

        request._lcc_start_time = time.monotonic()  # type: ignore[attr-defined]
        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        if not self._is_enabled():
            return response
        if self._should_skip(request.path):
            return response

        start = getattr(request, "_lcc_start_time", None)
        duration_ms = (
            round((time.monotonic() - start) * 1000, 2) if start else None
        )

        log_data = self._build_log_data(request, response, duration_ms)

        slow_threshold = getattr(
            settings, "REQUEST_LOGGING_SLOW_THRESHOLD_MS", _DEFAULT_SLOW_THRESHOLD_MS
        )

        if duration_ms and duration_ms >= slow_threshold:
            logger.warning("Slow request: %s", log_data)
        elif response.status_code >= 500:
            logger.error("Server error: %s", log_data)
        elif response.status_code >= 400:
            logger.warning("Client error: %s", log_data)
        else:
            logger.info("Request: %s", log_data)

        return response

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_enabled() -> bool:
        return getattr(settings, "REQUEST_LOGGING_ENABLED", True)

    @staticmethod
    def _should_skip(path: str) -> bool:
        skip_paths = getattr(settings, "REQUEST_LOGGING_SKIP_PATHS", _DEFAULT_SKIP_PATHS)
        return any(path.startswith(p) for p in skip_paths)

    @staticmethod
    def _build_log_data(
        request: HttpRequest,
        response: HttpResponse,
        duration_ms: float | None,
    ) -> dict[str, Any]:
        user = getattr(request, "user", None)
        tenant = getattr(request, "tenant", None)

        data: dict[str, Any] = {
            "method": request.method,
            "path": request.get_full_path(),
            "status": response.status_code,
            "duration_ms": duration_ms,
        }
        if user and getattr(user, "is_authenticated", False):
            data["user_id"] = str(getattr(user, "pk", ""))
        if tenant:
            data["tenant"] = str(getattr(tenant, "schema_name", ""))
        return data
