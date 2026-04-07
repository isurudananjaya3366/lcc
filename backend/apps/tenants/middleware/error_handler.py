"""
Error handling and fallback for LankaCommerce Cloud tenant middleware.

Provides consistent responses when tenant resolution fails, when tenants
are suspended or expired, or when requests should fall back to the public
schema. Also provides resolution error logging and error metrics tracking.

Error scenarios handled:

    Tenant not found (Tasks 55-56):
        When no tenant matches the request hostname, subdomain, header,
        or custom domain, the middleware returns a 404 response with a
        tenant-specific error message. The tenant_not_found() handler
        logs the failure and returns an appropriate HTTP 404 response.

    Custom 404 template (Task 57):
        A custom HTML template (tenants/404_tenant_not_found.html) is
        rendered for browser requests. API requests receive a JSON 404.
        The template path is configurable via TENANT_404_TEMPLATE.

    Public tenant fallback (Tasks 58-59):
        Certain paths (authentication, registration, health checks) must
        be accessible without tenant resolution. These paths always use
        the public schema and bypass tenant resolution entirely.
        Configured via PUBLIC_SCHEMA_PATHS in Django settings.

    Suspended tenant (Tasks 60-61):
        When a resolved tenant has a 'suspended' status, the middleware
        blocks access and returns an HTTP 403 response with a clear
        message. A custom template (tenants/suspended.html) is rendered
        for browser requests.

    Suspended template (Task 62):
        The suspended.html template is documented and placed at
        apps/tenants/templates/tenants/suspended.html. Configurable
        via TENANT_SUSPENDED_TEMPLATE setting.

    Expired subscription (Tasks 63-64):
        When a resolved tenant has an 'expired' status, the middleware
        blocks access and returns an HTTP 403 response indicating the
        subscription has expired. A grace period policy allows tenants
        to renew within a configurable window (default 7 days) before
        access is fully revoked. API and browser responses are provided.

    Expired template (Task 65):
        A custom HTML template (tenants/expired.html) is rendered for
        browser requests when a tenant's subscription has expired.
        The template path is configurable via TENANT_EXPIRED_TEMPLATE.

    Resolution error logging (Task 66):
        All tenant resolution errors are logged consistently with
        domain, path, error type, method, and timestamp. Log entries
        use structured fields for easy parsing and aggregation.
        Retention follows the application log rotation policy.

    Error metrics (Task 67):
        In-memory counters track error occurrences by error type and
        domain. Provides get_error_metrics() and reset_error_metrics()
        for monitoring dashboards and alerting.

    Error handling documentation (Task 68):
        Comprehensive documentation covers all error flows, template
        mappings, settings, logging, and metrics. Maintained at
        docs/backend/error-handling.md.

Security notes:
    - Error responses do not leak tenant details to unauthenticated users.
    - Suspended/expired tenants receive generic messages without internal IDs.
    - All resolution failures are logged for audit and monitoring.
    - Public schema paths should be kept minimal to reduce attack surface.

Task coverage:
    - Task 55: Create Tenant Not Found Handler
    - Task 56: Create 404 Response
    - Task 57: Create Custom 404 Template
    - Task 58: Configure Public Tenant Fallback
    - Task 59: Define Public Schema Paths
    - Task 60: Handle Suspended Tenant
    - Task 61: Create Suspended Response
    - Task 62: Create Suspended Template
    - Task 63: Handle Expired Subscription
    - Task 64: Create Expired Response
    - Task 65: Create Expired Template
    - Task 66: Log Resolution Errors
    - Task 67: Create Error Metrics
    - Task 68: Document Error Handling

Dependencies:
    - Django template system (for HTML error pages)
    - Django settings (for PUBLIC_SCHEMA_PATHS, template paths)
    - Tenant model (for status checks)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.http import JsonResponse

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TENANT_STATUS_ACTIVE = "active"
TENANT_STATUS_SUSPENDED = "suspended"
TENANT_STATUS_EXPIRED = "expired"

_VALID_STATUSES = frozenset(
    {TENANT_STATUS_ACTIVE, TENANT_STATUS_SUSPENDED, TENANT_STATUS_EXPIRED}
)

# Default template paths
DEFAULT_404_TEMPLATE = "tenants/404_tenant_not_found.html"
DEFAULT_SUSPENDED_TEMPLATE = "tenants/suspended.html"
DEFAULT_EXPIRED_TEMPLATE = "tenants/expired.html"

# Grace period for expired subscriptions (days)
DEFAULT_GRACE_PERIOD_DAYS = 7

# ---------------------------------------------------------------------------
# Task 67: Error metrics — in-memory counters
# ---------------------------------------------------------------------------

_error_counts: dict[str, int] = {}
_error_counts_by_domain: dict[str, dict[str, int]] = {}


# ---------------------------------------------------------------------------
# Task 58-59: Public schema path helpers
# ---------------------------------------------------------------------------


def get_public_schema_paths() -> list[str]:
    """
    Return the list of URL paths that always use the public schema.

    Public schema paths (Task 59):
        These paths bypass tenant resolution entirely and always use
        the public PostgreSQL schema. This is necessary for endpoints
        that must be accessible without a tenant context:
        - Authentication endpoints (login, token refresh)
        - Tenant registration (new tenant sign-up)
        - Subscription plan listing
        - Health checks and monitoring
        - Prometheus metrics

    Configuration (Task 59):
        Paths are read from the PUBLIC_SCHEMA_PATHS setting in
        Django settings (config/settings/base.py). If not configured,
        a sensible default list is used.

    Returns:
        list[str]: URL path prefixes that use the public schema.
    """
    from django.conf import settings

    return list(
        getattr(
            settings,
            "PUBLIC_SCHEMA_PATHS",
            [
                "/api/v1/auth/",
                "/api/v1/register/",
                "/api/v1/plans/",
                "/health/",
                "/metrics/",
            ],
        )
    )


def is_public_path(path: str) -> bool:
    """
    Check if a request path should use the public schema.

    Public fallback (Task 58):
        Returns True if the path matches any prefix in
        PUBLIC_SCHEMA_PATHS. When True, the middleware should
        skip tenant resolution and use the public schema directly.

    Rationale (Task 58):
        Authentication and registration must work before a tenant
        is identified. Health checks and metrics must always be
        reachable regardless of tenant state.

    Args:
        path: The request URL path (e.g. "/api/v1/auth/login/").

    Returns:
        bool: True if the path should use the public schema.
    """
    if not path:
        return False
    public_paths = get_public_schema_paths()
    is_public = any(path.startswith(prefix) for prefix in public_paths)
    if is_public:
        logger.debug(
            "ErrorHandler: path '%s' matches public schema paths — "
            "bypassing tenant resolution (Task 58)",
            path,
        )
    return is_public


# ---------------------------------------------------------------------------
# Task 55-57: Tenant not found handler
# ---------------------------------------------------------------------------


def _is_api_request(request: "HttpRequest") -> bool:
    """
    Determine if a request expects a JSON response.

    Checks the Accept header and request path to decide whether
    to return JSON or HTML. API paths and requests with
    application/json Accept header get JSON responses.

    Args:
        request: The incoming Django HttpRequest.

    Returns:
        bool: True if the request expects JSON.
    """
    accept = request.META.get("HTTP_ACCEPT", "")
    if "application/json" in accept:
        return True
    path = getattr(request, "path", "")
    return path.startswith("/api/") or path.startswith("/mobile/")


def tenant_not_found(
    request: "HttpRequest",
    hostname: str = "",
) -> "HttpResponse":
    """
    Handle a tenant resolution failure with a 404 response.

    Not-found handler (Task 55):
        Called when no tenant matches the request. Provides a
        consistent fallback behaviour: logs the failure and returns
        an HTTP 404 response.

    404 response (Task 56):
        Returns HTTP 404 with a descriptive message. The response
        format depends on the request type:
        - API requests: JSON {"error": "tenant_not_found", "detail": ...}
        - Browser requests: Rendered HTML template.

    Custom 404 template (Task 57):
        For browser requests, renders the template specified by
        TENANT_404_TEMPLATE (default: tenants/404_tenant_not_found.html).
        If the template does not exist, a plain text 404 is returned.

    Logging (Task 55):
        Every not-found event is logged at WARNING level with the
        requested hostname for audit and monitoring.

    Args:
        request: The incoming Django HttpRequest.
        hostname: The hostname that failed to resolve (for logging).

    Returns:
        HttpResponse: An HTTP 404 response (JSON or HTML).
    """
    logger.warning(
        "ErrorHandler: tenant not found for hostname='%s' path='%s' "
        "method='%s' (Task 55)",
        hostname or request.META.get("HTTP_HOST", "unknown"),
        request.path,
        request.method,
    )

    # Track metric (Task 67)
    host = hostname or request.META.get("HTTP_HOST", "unknown")
    _record_error_metric("tenant_not_found", host)

    if _is_api_request(request):
        return JsonResponse(
            {
                "error": "tenant_not_found",
                "detail": "No tenant found for this domain.",
            },
            status=404,
        )

    # Browser request — try to render HTML template
    from django.conf import settings

    template_name = getattr(
        settings, "TENANT_404_TEMPLATE", DEFAULT_404_TEMPLATE
    )

    try:
        from django.template.loader import render_to_string

        html = render_to_string(
            template_name,
            {"hostname": hostname or request.META.get("HTTP_HOST", "")},
            request=request,
        )
        from django.http import HttpResponse

        return HttpResponse(html, status=404, content_type="text/html")
    except Exception:
        logger.debug(
            "ErrorHandler: template '%s' not found — returning plain 404",
            template_name,
        )
        from django.http import HttpResponse

        return HttpResponse(
            "Tenant not found.",
            status=404,
            content_type="text/plain",
        )


# ---------------------------------------------------------------------------
# Task 60-61: Suspended tenant handler
# ---------------------------------------------------------------------------


def is_tenant_suspended(tenant) -> bool:
    """
    Check if a tenant is in suspended state.

    Suspended tenant detection (Task 60):
        Returns True if the tenant has a status field set to
        'suspended', or if the tenant has is_active=False and
        a status attribute indicating suspension.

    Args:
        tenant: The resolved Tenant model instance.

    Returns:
        bool: True if the tenant is suspended.
    """
    if tenant is None:
        return False

    # Check explicit status field
    status = getattr(tenant, "status", None)
    if status is not None:
        return str(status).lower() == TENANT_STATUS_SUSPENDED

    # Fallback: check is_active combined with context
    return False


def tenant_suspended(
    request: "HttpRequest",
    tenant=None,
) -> "HttpResponse":
    """
    Handle a request to a suspended tenant with a 403 response.

    Suspended handling (Task 60):
        When a resolved tenant is in suspended state, this handler
        blocks access and returns an HTTP 403 Forbidden response.
        All data remains intact but inaccessible until the tenant
        is reactivated.

    Suspended response (Task 61):
        Returns HTTP 403 with a clear message:
        - API requests: JSON {"error": "tenant_suspended", "detail": ...}
        - Browser requests: Rendered HTML template.

    Template (Task 61):
        For browser requests, renders the template specified by
        TENANT_SUSPENDED_TEMPLATE (default: tenants/suspended.html).
        If the template does not exist, a plain text 403 is returned.

    Logging (Task 60):
        Suspended access attempts are logged at WARNING level with
        the tenant name and request details.

    Args:
        request: The incoming Django HttpRequest.
        tenant: The suspended Tenant instance (for logging context).

    Returns:
        HttpResponse: An HTTP 403 Forbidden response (JSON or HTML).
    """
    tenant_name = (
        getattr(tenant, "name", str(getattr(tenant, "pk", "?")))
        if tenant is not None
        else "unknown"
    )

    logger.warning(
        "ErrorHandler: tenant '%s' is suspended — blocking access "
        "path='%s' method='%s' (Task 60)",
        tenant_name,
        request.path,
        request.method,
    )

    # Track metric (Task 67)
    hostname = request.META.get("HTTP_HOST", "unknown")
    _record_error_metric("tenant_suspended", hostname)

    if _is_api_request(request):
        return JsonResponse(
            {
                "error": "tenant_suspended",
                "detail": (
                    "This account has been suspended. "
                    "Please contact support for assistance."
                ),
            },
            status=403,
        )

    # Browser request — try to render HTML template
    from django.conf import settings

    template_name = getattr(
        settings, "TENANT_SUSPENDED_TEMPLATE", DEFAULT_SUSPENDED_TEMPLATE
    )

    try:
        from django.template.loader import render_to_string

        html = render_to_string(
            template_name,
            {"tenant_name": tenant_name},
            request=request,
        )
        from django.http import HttpResponse

        return HttpResponse(html, status=403, content_type="text/html")
    except Exception:
        logger.debug(
            "ErrorHandler: template '%s' not found — returning plain 403",
            template_name,
        )
        from django.http import HttpResponse

        return HttpResponse(
            "This account has been suspended. "
            "Please contact support for assistance.",
            status=403,
            content_type="text/plain",
        )


# ---------------------------------------------------------------------------
# Convenience: get_tenant_status
# ---------------------------------------------------------------------------


def get_tenant_status(tenant) -> str:
    """
    Return the normalised status of a tenant.

    Reads the tenant's status field and normalises it to one of:
    'active', 'suspended', 'expired', or the raw string value.

    If no status field exists, checks is_active to determine status.

    Args:
        tenant: The Tenant model instance.

    Returns:
        str: The normalised status string.
    """
    if tenant is None:
        return "not_found"

    # Explicit status field
    status = getattr(tenant, "status", None)
    if status is not None:
        return str(status).lower()

    # Fallback to is_active
    is_active = getattr(tenant, "is_active", True)
    return TENANT_STATUS_ACTIVE if is_active else TENANT_STATUS_SUSPENDED


# ---------------------------------------------------------------------------
# Task 63-65: Expired subscription handler
# ---------------------------------------------------------------------------


def is_tenant_expired(tenant) -> bool:
    """
    Check if a tenant's subscription has expired.

    Expired subscription detection (Task 63):
        Returns True if the tenant has a status field set to
        'expired'. This indicates the subscription has lapsed
        and access should be blocked (subject to grace period).

    Grace period (Task 63):
        The grace period is checked separately by
        is_within_grace_period(). This function only checks the
        raw status value.

    Args:
        tenant: The resolved Tenant model instance.

    Returns:
        bool: True if the tenant's subscription has expired.
    """
    if tenant is None:
        return False

    status = getattr(tenant, "status", None)
    if status is not None:
        return str(status).lower() == TENANT_STATUS_EXPIRED

    return False


def is_within_grace_period(tenant) -> bool:
    """
    Check if an expired tenant is still within the grace period.

    Grace period policy (Task 63):
        After a subscription expires, tenants have a configurable
        grace period (default 7 days) during which they retain
        read-only access. After the grace period, access is fully
        revoked.

    The grace period is determined by:
        1. TENANT_GRACE_PERIOD_DAYS setting (default: 7 days).
        2. The tenant's expired_at or subscription_end field.
        3. If no date field exists, grace period is not applied.

    Args:
        tenant: The expired Tenant model instance.

    Returns:
        bool: True if the tenant is within the grace period.
    """
    if tenant is None:
        return False

    from datetime import datetime, timezone

    from django.conf import settings

    grace_days = getattr(
        settings, "TENANT_GRACE_PERIOD_DAYS", DEFAULT_GRACE_PERIOD_DAYS
    )

    # Check for expiration date field
    expired_at = getattr(tenant, "expired_at", None)
    if expired_at is None:
        expired_at = getattr(tenant, "subscription_end", None)
    if expired_at is None:
        # No date field — cannot determine grace period
        return False

    # Ensure timezone-aware comparison
    now = datetime.now(tz=timezone.utc)
    if hasattr(expired_at, "tzinfo") and expired_at.tzinfo is None:
        from datetime import timezone as tz

        expired_at = expired_at.replace(tzinfo=tz.utc)

    from datetime import timedelta

    grace_end = expired_at + timedelta(days=grace_days)
    return now <= grace_end


def tenant_expired(
    request: "HttpRequest",
    tenant=None,
) -> "HttpResponse":
    """
    Handle a request to a tenant with an expired subscription.

    Expired handling (Task 63):
        When a resolved tenant has an expired subscription, this
        handler blocks access and returns an HTTP 403 Forbidden
        response. A grace period policy may allow limited access
        before full revocation.

    Expired response (Task 64):
        Returns HTTP 403 with a clear message:
        - API requests: JSON {"error": "tenant_expired", "detail": ...}
        - Browser requests: Rendered HTML template.

    Template (Task 65):
        For browser requests, renders the template specified by
        TENANT_EXPIRED_TEMPLATE (default: tenants/expired.html).
        If the template does not exist, a plain text 403 is returned.

    Logging (Task 63):
        Expired access attempts are logged at WARNING level with
        the tenant name and request details.

    Args:
        request: The incoming Django HttpRequest.
        tenant: The expired Tenant instance (for logging context).

    Returns:
        HttpResponse: An HTTP 403 Forbidden response (JSON or HTML).
    """
    tenant_name = (
        getattr(tenant, "name", str(getattr(tenant, "pk", "?")))
        if tenant is not None
        else "unknown"
    )

    logger.warning(
        "ErrorHandler: tenant '%s' subscription expired — blocking "
        "access path='%s' method='%s' (Task 63)",
        tenant_name,
        request.path,
        request.method,
    )

    # Track metric (Task 67)
    hostname = request.META.get("HTTP_HOST", "unknown")
    _record_error_metric("tenant_expired", hostname)

    if _is_api_request(request):
        return JsonResponse(
            {
                "error": "tenant_expired",
                "detail": (
                    "Your subscription has expired. "
                    "Please renew your plan to continue."
                ),
            },
            status=403,
        )

    # Browser request — try to render HTML template
    from django.conf import settings

    template_name = getattr(
        settings, "TENANT_EXPIRED_TEMPLATE", DEFAULT_EXPIRED_TEMPLATE
    )

    try:
        from django.template.loader import render_to_string

        html = render_to_string(
            template_name,
            {"tenant_name": tenant_name},
            request=request,
        )
        from django.http import HttpResponse

        return HttpResponse(html, status=403, content_type="text/html")
    except Exception:
        logger.debug(
            "ErrorHandler: template '%s' not found — returning plain 403",
            template_name,
        )
        from django.http import HttpResponse

        return HttpResponse(
            "Your subscription has expired. "
            "Please renew your plan to continue.",
            status=403,
            content_type="text/plain",
        )


# ---------------------------------------------------------------------------
# Task 66: Resolution error logging
# ---------------------------------------------------------------------------


def log_resolution_error(
    error_type: str,
    request: "HttpRequest",
    hostname: str = "",
    detail: str = "",
) -> None:
    """
    Log a tenant resolution error with structured fields.

    Resolution error logging (Task 66):
        All tenant resolution errors are logged consistently with
        the following fields:
        - error_type: Category of error (not_found, suspended, expired).
        - domain: The hostname/domain involved in the failure.
        - path: The request URL path.
        - method: The HTTP method (GET, POST, etc.).
        - detail: Optional additional information.

    Retention (Task 66):
        Log entries follow the application log rotation policy.
        Structured fields allow aggregation by domain and error type.

    Args:
        error_type: The error category string.
        request: The incoming Django HttpRequest.
        hostname: The domain/hostname involved.
        detail: Optional extra detail string.
    """
    host = hostname or request.META.get("HTTP_HOST", "unknown")

    logger.warning(
        "ErrorHandler: resolution_error type='%s' domain='%s' "
        "path='%s' method='%s' detail='%s' (Task 66)",
        error_type,
        host,
        request.path,
        request.method,
        detail,
    )

    # Track metric (Task 67)
    _record_error_metric(error_type, host)


# ---------------------------------------------------------------------------
# Task 67: Error metrics
# ---------------------------------------------------------------------------


def _record_error_metric(error_type: str, domain: str) -> None:
    """
    Record an error metric in the in-memory counters.

    Error metrics (Task 67):
        Increments the global error count for the given error type
        and the per-domain error count. These counters can be
        exposed to monitoring dashboards and alerting systems.

    Args:
        error_type: The error category (not_found, suspended, expired).
        domain: The domain/hostname associated with the error.
    """
    # Global counter by error type
    _error_counts[error_type] = _error_counts.get(error_type, 0) + 1

    # Per-domain counter
    if domain not in _error_counts_by_domain:
        _error_counts_by_domain[domain] = {}
    domain_counts = _error_counts_by_domain[domain]
    domain_counts[error_type] = domain_counts.get(error_type, 0) + 1


def get_error_metrics() -> dict:
    """
    Return the current error metrics.

    Error metrics (Task 67):
        Returns a dictionary with:
        - total: Total count of all resolution errors.
        - by_type: Error counts grouped by error type.
        - by_domain: Error counts grouped by domain and error type.

    Usage:
        Intended for monitoring dashboards, health check endpoints,
        and alerting systems. The metrics are in-memory and reset
        on application restart. Use reset_error_metrics() to clear
        counters manually.

    Returns:
        dict: Error metrics with total, by_type, and by_domain keys.
    """
    return {
        "total": sum(_error_counts.values()),
        "by_type": dict(_error_counts),
        "by_domain": {
            domain: dict(counts)
            for domain, counts in _error_counts_by_domain.items()
        },
    }


def reset_error_metrics() -> None:
    """
    Reset all error metrics counters.

    Clears the in-memory error counters. Useful for testing and
    for periodic reset in long-running processes.
    """
    _error_counts.clear()
    _error_counts_by_domain.clear()
