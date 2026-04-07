"""
Exception logging utilities.

Provides contextual error logging helpers that enrich log entries with
request metadata (IP, user, tenant) for easier debugging and monitoring.
"""

from __future__ import annotations

import logging
from typing import Any

from django.http import HttpRequest

logger = logging.getLogger("apps.core.exceptions")


def get_client_ip(request: HttpRequest) -> str:
    """
    Extract the client IP address from a Django request.

    Checks ``X-Forwarded-For`` first (common behind reverse proxies),
    then falls back to ``REMOTE_ADDR``.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP in the chain (client IP).
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _request_context(request: HttpRequest | None) -> dict[str, Any]:
    """Build a dict of useful request metadata for log entries."""
    if request is None:
        return {}
    ctx: dict[str, Any] = {
        "ip": get_client_ip(request),
        "method": request.method,
        "path": request.get_full_path(),
    }
    # User info (if authenticated).
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        ctx["user_id"] = str(getattr(user, "pk", ""))
        ctx["user_email"] = str(getattr(user, "email", ""))

    # Tenant info (if set by tenant middleware).
    tenant = getattr(request, "tenant", None)
    if tenant is not None:
        ctx["tenant_id"] = str(getattr(tenant, "pk", ""))
        ctx["tenant_name"] = str(getattr(tenant, "name", ""))

    return ctx


def log_exception(
    exc: Exception,
    *,
    request: HttpRequest | None = None,
    extra: dict[str, Any] | None = None,
    level: int = logging.ERROR,
) -> None:
    """
    Log an exception with enriched context.

    Parameters
    ----------
    exc : Exception
        The exception to log.
    request : HttpRequest, optional
        The current request, used to pull IP / user / tenant details.
    extra : dict, optional
        Additional key-value pairs to include in the log record.
    level : int
        Logging level (default ``logging.ERROR``).
    """
    ctx = _request_context(request)
    if extra:
        ctx.update(extra)

    error_code = getattr(exc, "error_code", type(exc).__name__)
    message = getattr(exc, "message", str(exc))

    logger.log(
        level,
        "[%s] %s | context=%s",
        error_code,
        message,
        ctx,
        exc_info=level >= logging.ERROR,
    )


def log_business_rule_violation(
    rule_code: str,
    message: str,
    *,
    request: HttpRequest | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """
    Log a business-rule violation at WARNING level.

    Business-rule violations are not bugs — they represent expected
    domain constraints — so they are logged at WARNING rather than ERROR.

    Parameters
    ----------
    rule_code : str
        Machine-readable rule identifier (e.g. ``"ORDER_ALREADY_SHIPPED"``).
    message : str
        Human-readable description.
    request : HttpRequest, optional
        Current request for context enrichment.
    extra : dict, optional
        Additional data to log.
    """
    ctx = _request_context(request)
    if extra:
        ctx.update(extra)

    logger.warning(
        "[BUSINESS_RULE:%s] %s | context=%s",
        rule_code,
        message,
        ctx,
    )
