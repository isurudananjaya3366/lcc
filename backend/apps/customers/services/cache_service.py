"""
Customer cache service.

Uses the project's TenantCache wrapper to cache frequently accessed
customer data with automatic tenant-scoped key isolation.
"""

from __future__ import annotations

import logging
from typing import Any

from apps.core.cache.constants import CACHE_TTL_SHORT
from apps.core.cache.tenant_cache import TenantCache

logger = logging.getLogger(__name__)

# Default TTL for customer cache entries (15 minutes)
CUSTOMER_CACHE_TTL = 900

# Cache key patterns
_KEY_BY_ID = "customer:id:{customer_id}"
_KEY_BY_CODE = "customer:code:{code}"
_KEY_BY_PHONE = "customer:phone:{phone}"


class CustomerCacheService:
    """
    Redis-backed cache for customer lookups.

    All keys are automatically tenant-scoped via ``TenantCache``.
    """

    def __init__(self) -> None:
        self._cache = TenantCache()

    # ── Cache by customer ID ────────────────────────────────────────

    def cache_customer(
        self,
        customer_id: str,
        customer_data: dict[str, Any],
        ttl: int = CUSTOMER_CACHE_TTL,
    ) -> None:
        """Store customer data in cache keyed by ID."""
        key = _KEY_BY_ID.format(customer_id=customer_id)
        self._cache.set(key, customer_data, timeout=ttl)

    def get_cached_customer(self, customer_id: str) -> dict[str, Any] | None:
        """Retrieve cached customer data by ID."""
        key = _KEY_BY_ID.format(customer_id=customer_id)
        return self._cache.get(key)

    def invalidate_customer_cache(self, customer_id: str) -> None:
        """Remove a customer from cache by ID."""
        key = _KEY_BY_ID.format(customer_id=customer_id)
        self._cache.delete(key)

    # ── Cache by customer code ──────────────────────────────────────

    def cache_customer_by_code(
        self,
        code: str,
        customer_data: dict[str, Any],
        ttl: int = CUSTOMER_CACHE_TTL,
    ) -> None:
        """Store customer data keyed by customer code."""
        key = _KEY_BY_CODE.format(code=code)
        self._cache.set(key, customer_data, timeout=ttl)

    def get_cached_customer_by_code(self, code: str) -> dict[str, Any] | None:
        """Retrieve cached customer data by code."""
        key = _KEY_BY_CODE.format(code=code)
        return self._cache.get(key)

    # ── Cache by phone ──────────────────────────────────────────────

    def cache_customer_by_phone(
        self,
        phone: str,
        customer_data: dict[str, Any],
        ttl: int = CUSTOMER_CACHE_TTL,
    ) -> None:
        """Store customer data keyed by phone number."""
        key = _KEY_BY_PHONE.format(phone=phone)
        self._cache.set(key, customer_data, timeout=ttl)

    def get_cached_customer_by_phone(self, phone: str) -> dict[str, Any] | None:
        """Retrieve cached customer data by phone."""
        key = _KEY_BY_PHONE.format(phone=phone)
        return self._cache.get(key)

    # ── Bulk invalidation ───────────────────────────────────────────

    def invalidate_all(self, customer_id: str, code: str = "", phone: str = "") -> None:
        """
        Invalidate all cache entries for a customer.

        Call this after any update to ensure stale data is not served.
        """
        self.invalidate_customer_cache(customer_id)
        if code:
            key = _KEY_BY_CODE.format(code=code)
            self._cache.delete(key)
        if phone:
            key = _KEY_BY_PHONE.format(phone=phone)
            self._cache.delete(key)
