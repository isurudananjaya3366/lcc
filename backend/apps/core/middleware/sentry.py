"""
Sentry Context Middleware.

Enriches every Sentry event with user context, tenant tags, and
request metadata so errors are easy to triage in the Sentry dashboard.

- **Task 71** — User context via ``sentry_sdk.set_user()``.
- **Task 72** — Tags via ``sentry_sdk.set_tag()`` (tenant, request-id).
- Extras via ``sentry_sdk.set_context()`` (request metadata).

The middleware degrades gracefully when ``sentry-sdk`` is not installed
(e.g. in local development or test environments).

Enable by adding to ``MIDDLEWARE``::

    MIDDLEWARE = [
        ...
        "apps.core.middleware.sentry.SentryContextMiddleware",
        ...
    ]
"""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from apps.core.middleware.base import BaseMiddleware

# Conditional import — sentry_sdk may not be installed in dev / test.
try:
    import sentry_sdk

    _HAS_SENTRY = True
except ImportError:  # pragma: no cover
    sentry_sdk = None  # type: ignore[assignment]
    _HAS_SENTRY = False

logger = logging.getLogger("apps.core.middleware.sentry")


class SentryContextMiddleware(BaseMiddleware):
    """
    Inject user, tenant, and request context into the current Sentry scope.

    All context is set **before** the view executes so that any exception
    captured during the request already carries the enriched information.

    Context added
    ~~~~~~~~~~~~~

    User (``set_user``):
        * ``id`` — PlatformUser UUID primary key.
        * ``email`` — PlatformUser email address.
        * ``ip_address`` — Client IP from the request.

    Tags (``set_tag``):
        * ``tenant_id`` — resolved tenant PK (if available).
        * ``tenant_domain`` — resolved tenant domain (if available).
        * ``request_id`` — value of the ``X-Request-ID`` header, when
          present (typically injected by a reverse proxy or
          :class:`~apps.core.middleware.request_logging.RequestLoggingMiddleware`).

    Extra context (``set_context("request_meta")``):
        * ``method`` — HTTP method (GET, POST, …).
        * ``path`` — Request path.
        * ``content_type`` — ``Content-Type`` header value.
        * ``user_agent`` — ``User-Agent`` header value.
    """

    # ------------------------------------------------------------------
    # Hooks
    # ------------------------------------------------------------------

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        """Set Sentry context before the view runs."""
        if not _HAS_SENTRY:
            return None

        if not self._is_sentry_enabled():
            return None

        self._set_user_context(request)
        self._set_tags(request)
        self._set_request_context(request)
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_sentry_enabled() -> bool:
        """Return ``True`` when the Sentry SDK has been initialised."""
        try:
            client = sentry_sdk.get_client()
            return client.is_active()
        except Exception:  # noqa: BLE001
            return False

    @staticmethod
    def _set_user_context(request: HttpRequest) -> None:
        """Populate ``sentry_sdk.set_user()`` from the authenticated user."""
        user = getattr(request, "user", None)
        if user is None or not getattr(user, "is_authenticated", False):
            # Anonymous requests — only attach the IP.
            sentry_sdk.set_user(
                {"ip_address": SentryContextMiddleware._get_client_ip(request)}
            )
            return

        user_data: dict[str, Any] = {
            "id": str(user.pk),
            "email": getattr(user, "email", ""),
            "ip_address": SentryContextMiddleware._get_client_ip(request),
        }

        # PlatformUser is email-based and may not have a ``username``
        # field.  Only include it when the attribute actually exists.
        username = getattr(user, "username", None)
        if username:
            user_data["username"] = username

        sentry_sdk.set_user(user_data)

    @staticmethod
    def _set_tags(request: HttpRequest) -> None:
        """Add searchable tags for tenant and request identifiers."""
        # ── Tenant tags ──────────────────────────────────────
        tenant = getattr(request, "tenant", None)
        if tenant is not None:
            sentry_sdk.set_tag("tenant_id", str(getattr(tenant, "pk", "")))
            # Prefer schema_name, fall back to domain_url.
            domain = (
                getattr(tenant, "schema_name", "")
                or getattr(tenant, "domain_url", "")
            )
            if domain:
                sentry_sdk.set_tag("tenant_domain", domain)

        # ── Request ID (typically set by nginx / load balancer) ──
        request_id = (
            request.META.get("HTTP_X_REQUEST_ID")
            or getattr(request, "id", None)
            or ""
        )
        if request_id:
            sentry_sdk.set_tag("request_id", str(request_id))

    @staticmethod
    def _set_request_context(request: HttpRequest) -> None:
        """Attach non-PII request metadata as structured context."""
        sentry_sdk.set_context(
            "request_meta",
            {
                "method": request.method,
                "path": request.path,
                "content_type": request.content_type,
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            },
        )

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        """
        Best-effort client IP extraction.

        Checks ``X-Forwarded-For`` first (set by proxies), then falls
        back to ``REMOTE_ADDR``.
        """
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            # X-Forwarded-For may contain a chain; the leftmost is the
            # original client.
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
