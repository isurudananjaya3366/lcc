"""
Timezone Middleware.

Activates the authenticated user's preferred timezone for the duration
of the request.  Falls back to ``settings.TIME_ZONE`` when no user
preference is available.

Enable by adding to ``MIDDLEWARE`` (after authentication)::

    MIDDLEWARE = [
        ...
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "apps.core.middleware.TimezoneMiddleware",
        ...
    ]

The user's timezone is resolved in order:

1. ``request.user.timezone`` attribute (if the User model stores it).
2. ``request.session["django_timezone"]`` (if the frontend sets it).
3. ``settings.TIME_ZONE`` (project default, usually ``"Asia/Colombo"``).
"""

from __future__ import annotations

import logging
import zoneinfo

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from apps.core.middleware.base import BaseMiddleware

logger = logging.getLogger("apps.core.middleware.timezone")


class TimezoneMiddleware(BaseMiddleware):
    """
    Activate the user's timezone for each request.

    After the response is generated Django's timezone is deactivated
    to avoid leaking one request's timezone into the next (important
    in async / threading scenarios).
    """

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        tz_name = self._resolve_timezone(request)
        try:
            tz = zoneinfo.ZoneInfo(tz_name)
            timezone.activate(tz)
        except (KeyError, zoneinfo.ZoneInfoNotFoundError):
            logger.warning("Invalid timezone '%s', falling back to UTC.", tz_name)
            timezone.deactivate()
        return None

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        timezone.deactivate()
        return response

    # ------------------------------------------------------------------
    # Resolution chain
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_timezone(request: HttpRequest) -> str:
        # 1. User model attribute
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            user_tz = getattr(user, "timezone", None)
            if user_tz:
                return str(user_tz)

        # 2. Session value (set by frontend JS)
        session = getattr(request, "session", None)
        if session:
            session_tz = session.get("django_timezone")
            if session_tz:
                return str(session_tz)

        # 3. Project default
        return getattr(settings, "TIME_ZONE", "UTC")
