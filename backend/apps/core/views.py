"""Core views module.

Contains health check endpoint for load balancer and monitoring integration.
"""

from datetime import datetime, timezone

from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for load balancers and monitoring services.

    Returns:
        200 with "healthy" status when all checks pass.
        503 with "unhealthy" status when any check fails.

    Query Parameters:
        detail (bool): If 'true', include full diagnostics.
    """
    checks = {}
    errors = []

    # ── Database check ─────────────────────────────────────────────
    try:
        connection.ensure_connection()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = "error"
        errors.append(f"Database connection failed: {e}")

    # ── Redis check ────────────────────────────────────────────────
    try:
        from django.core.cache import cache

        cache.set("health_check", "ok", timeout=5)
        if cache.get("health_check") == "ok":
            checks["redis"] = "ok"
        else:
            checks["redis"] = "error"
            errors.append("Redis read/write failed")
    except Exception as e:
        checks["redis"] = "error"
        errors.append(f"Redis connection failed: {e}")

    # ── Celery check (optional, graceful fail) ─────────────────────
    try:
        from config.celery import app as celery_app

        inspector = celery_app.control.inspect(timeout=1.0)
        ping_result = inspector.ping()
        if ping_result:
            checks["celery"] = "ok"
        else:
            checks["celery"] = "unavailable"
    except Exception:
        checks["celery"] = "unavailable"

    # ── Build response ─────────────────────────────────────────────
    is_healthy = not errors
    status_code = 200 if is_healthy else 503

    response_data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Include errors in response only if detail requested or unhealthy
    detail = request.GET.get("detail", "").lower() == "true"
    if errors or detail:
        response_data["errors"] = errors

    return JsonResponse(response_data, status=status_code)
