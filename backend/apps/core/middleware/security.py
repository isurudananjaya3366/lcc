"""
Security Headers Middleware.

Adds recommended security HTTP headers to every response.  These
headers complement Django's built-in ``SecurityMiddleware`` and add
extra protections commonly required by penetration tests and security
audits.

Enable by adding to ``MIDDLEWARE``::

    MIDDLEWARE = [
        ...
        "apps.core.middleware.SecurityHeadersMiddleware",
        ...
    ]

Override defaults in settings::

    SECURITY_EXTRA_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "X-XSS-Protection": "1; mode=block",
        "Cross-Origin-Opener-Policy": "same-origin",
    }
"""

from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from apps.core.middleware.base import BaseMiddleware

# Sensible defaults — override via settings.SECURITY_EXTRA_HEADERS
_DEFAULT_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "X-XSS-Protection": "1; mode=block",
    "Cross-Origin-Opener-Policy": "same-origin",
}


class SecurityHeadersMiddleware(BaseMiddleware):
    """
    Inject security-related HTTP headers into every response.

    Headers are merged from ``_DEFAULT_HEADERS`` and the optional
    ``settings.SECURITY_EXTRA_HEADERS`` dict.  Setting a header value
    to ``None`` or an empty string in settings removes that header from
    the defaults.
    """

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        headers = self._get_headers()
        for name, value in headers.items():
            if value:
                response[name] = value
        return response

    @staticmethod
    def _get_headers() -> dict[str, str]:
        custom = getattr(settings, "SECURITY_EXTRA_HEADERS", {})
        merged = {**_DEFAULT_HEADERS, **custom}
        # Drop entries explicitly set to None / empty
        return {k: v for k, v in merged.items() if v}
