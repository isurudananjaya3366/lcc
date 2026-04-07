"""
Sentry Error Tracking Configuration.

Provides :func:`configure_sentry` which initialises the Sentry SDK
with project-appropriate defaults.  Called from ``production.py``
(and optionally from ``staging.py``) when ``SENTRY_DSN`` is set.

Usage in settings::

    from config.settings.sentry import configure_sentry
    configure_sentry(env)

Environment variables:
    SENTRY_DSN                 — Required.  Sentry project DSN.
    SENTRY_ENVIRONMENT         — e.g. "production", "staging". Default: "production".
    SENTRY_TRACES_SAMPLE_RATE  — 0.0–1.0.  Default: 0.1.
    SENTRY_PROFILES_SAMPLE_RATE — 0.0–1.0.  Default: 0.0 (profiling off).
    SENTRY_RELEASE             — Optional.  Release tag (e.g. git SHA).
    SENTRY_SEND_DEFAULT_PII    — Default: False.  Never enable in production
                                  unless legally cleared.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def configure_sentry(env: Any) -> bool:
    """
    Initialise the Sentry SDK if ``SENTRY_DSN`` is available.

    Parameters
    ----------
    env : environ.Env
        The django-environ ``Env`` instance used throughout settings.

    Returns
    -------
    bool
        ``True`` if Sentry was initialised, ``False`` otherwise.
    """
    dsn: str = env("SENTRY_DSN", default="")
    if not dsn:
        logger.info("SENTRY_DSN not set — Sentry error tracking is disabled.")
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
    except ImportError:
        logger.warning(
            "sentry-sdk is not installed — run `pip install sentry-sdk[django]`."
        )
        return False

    environment = env("SENTRY_ENVIRONMENT", default="production")
    traces_sample_rate = env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1)
    profiles_sample_rate = env.float("SENTRY_PROFILES_SAMPLE_RATE", default=0.0)
    release = env("SENTRY_RELEASE", default="")
    send_default_pii = env.bool("SENTRY_SEND_DEFAULT_PII", default=False)

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            DjangoIntegration(
                transaction_style="url",
                middleware_spans=True,
            ),
            CeleryIntegration(monitor_beat_tasks=True),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
            RedisIntegration(),
        ],
        environment=environment,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        send_default_pii=send_default_pii,
        # Attach the release tag if provided (typically a git SHA).
        **({"release": release} if release else {}),
        # Scrub sensitive data from breadcrumbs and events.
        before_send=_before_send,
    )

    logger.info(
        "Sentry initialised: env=%s, traces=%.2f, profiles=%.2f",
        environment,
        traces_sample_rate,
        profiles_sample_rate,
    )
    return True


def _before_send(event: dict, hint: dict) -> dict | None:
    """
    Pre-processing hook for Sentry events.

    - Strips sensitive headers (Authorization, Cookie).
    - Filters out noisy exceptions (e.g. DisallowedHost).
    """
    # Filter out noisy exceptions
    if "exc_info" in hint:
        exc_type = hint["exc_info"][0]
        ignored = (
            "DisallowedHost",
            "SuspiciousOperation",
        )
        if exc_type and exc_type.__name__ in ignored:
            return None

    # Scrub sensitive request headers
    request_data = event.get("request", {})
    headers = request_data.get("headers", {})
    for sensitive in ("Authorization", "Cookie", "X-CSRFToken"):
        if sensitive in headers:
            headers[sensitive] = "[Filtered]"

    return event
