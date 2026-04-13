"""KPI cache service — Redis caching for dashboard KPIs."""

import hashlib
import json
import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache timeouts in seconds
CACHE_TIMEOUTS = {
    "TODAY": 300,       # 5 minutes
    "YESTERDAY": 3600,  # 1 hour
    "WEEK": 900,        # 15 minutes
    "LAST_WEEK": 3600,  # 1 hour
    "MONTH": 900,       # 15 minutes
    "LAST_MONTH": 3600, # 1 hour
    "QUARTER": 1800,    # 30 minutes
    "YEAR": 1800,       # 30 minutes
    "LAST_YEAR": 3600,  # 1 hour
    "CUSTOM": 600,      # 10 minutes
}


def _build_cache_key(calculator_name: str, period: str, filters: dict | None = None) -> str:
    """Build a consistent cache key for a KPI calculation."""
    key_parts = f"kpi:{calculator_name}:{period}"
    if filters:
        filter_hash = hashlib.md5(
            json.dumps(filters, sort_keys=True, default=str).encode()
        ).hexdigest()[:8]
        key_parts += f":{filter_hash}"
    return key_parts


def get_cached_kpi(calculator_name: str, period: str, filters: dict | None = None):
    """Retrieve cached KPI data if available."""
    key = _build_cache_key(calculator_name, period, filters)
    data = cache.get(key)
    if data is not None:
        logger.debug("Cache hit for %s", key)
    return data


def set_cached_kpi(
    calculator_name: str,
    period: str,
    data: dict | list,
    filters: dict | None = None,
) -> None:
    """Cache KPI calculation results."""
    key = _build_cache_key(calculator_name, period, filters)
    timeout = CACHE_TIMEOUTS.get(period, 600)
    cache.set(key, data, timeout)
    logger.debug("Cached %s for %d seconds", key, timeout)


def invalidate_kpi_cache(calculator_name: str | None = None) -> None:
    """Invalidate KPI cache entries.

    If calculator_name is provided, invalidates only that calculator's cache.
    Otherwise, attempts to clear all KPI cache entries.
    """
    if calculator_name:
        for period in CACHE_TIMEOUTS:
            key = _build_cache_key(calculator_name, period)
            cache.delete(key)
        logger.info("Invalidated cache for %s", calculator_name)
    else:
        # Best-effort: clear common keys
        for calc_name in ("sales", "inventory", "financial", "hr"):
            for period in CACHE_TIMEOUTS:
                key = _build_cache_key(calc_name, period)
                cache.delete(key)
        logger.info("Invalidated all KPI caches")
