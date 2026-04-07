"""
Tenant-scoped cache wrapper.

Ensures all cache keys include the current tenant's schema name,
providing data isolation in a multi-tenant environment.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Iterable, Sequence

from django.core.cache import caches
from django.db import connection

from apps.core.cache.constants import (
    KEY_PREFIX,
    MAX_KEY_LENGTH,
    SHARED_KEY_TEMPLATE,
    TENANT_KEY_TEMPLATE,
)

logger = logging.getLogger(__name__)


class TenantCache:
    """
    Multi-tenant cache wrapper around Django's cache framework.

    All keys are automatically prefixed with the current tenant's schema
    name so data from different tenants never collides.

    Usage::

        cache = TenantCache()          # uses 'default' backend
        cache = TenantCache('sessions') # uses 'sessions' backend

        cache.set('products:list', qs_data, timeout=3600)
        data = cache.get('products:list')
        cache.delete('products:list')
        cache.delete_pattern('products:*')
    """

    def __init__(self, cache_alias: str = "default") -> None:
        try:
            self._cache = caches[cache_alias]
        except Exception:
            logger.warning("Cache alias %r not found, falling back to 'default'.", cache_alias)
            self._cache = caches["default"]
        self._alias = cache_alias

    # ── Tenant context ────────────────────────────────────────────────

    @staticmethod
    def _get_tenant_schema() -> str:
        """Return current tenant schema or 'public'."""
        try:
            tenant = getattr(connection, "tenant", None)
            if tenant is not None:
                return tenant.schema_name
        except Exception:
            pass
        return "public"

    # ── Key building ──────────────────────────────────────────────────

    def make_key(self, key: str, *, shared: bool = False) -> str:
        """
        Generate a tenant-prefixed (or shared) cache key.

        Keys longer than *MAX_KEY_LENGTH* are automatically hashed.
        """
        if shared:
            full_key = SHARED_KEY_TEMPLATE.format(prefix=KEY_PREFIX, key=key)
        else:
            schema = self._get_tenant_schema()
            full_key = TENANT_KEY_TEMPLATE.format(
                prefix=KEY_PREFIX, schema=schema, key=key,
            )
        if len(full_key) > MAX_KEY_LENGTH:
            hashed = hashlib.md5(full_key.encode()).hexdigest()
            full_key = f"{KEY_PREFIX}:h:{hashed}"
        return full_key

    # ── Core operations ───────────────────────────────────────────────

    def get(self, key: str, default: Any = None, *, shared: bool = False) -> Any:
        """Get a value from cache with tenant-scoped key."""
        cache_key = self.make_key(key, shared=shared)
        try:
            return self._cache.get(cache_key, default)
        except Exception:
            logger.exception("Cache get error for key %s", cache_key)
            return default

    def set(
        self,
        key: str,
        value: Any,
        timeout: int | None = None,
        *,
        shared: bool = False,
    ) -> bool:
        """Set a value in cache with tenant-scoped key."""
        cache_key = self.make_key(key, shared=shared)
        try:
            self._cache.set(cache_key, value, timeout)
            return True
        except Exception:
            logger.exception("Cache set error for key %s", cache_key)
            return False

    def delete(self, key: str, *, shared: bool = False) -> bool:
        """Delete a key from cache."""
        cache_key = self.make_key(key, shared=shared)
        try:
            self._cache.delete(cache_key)
            return True
        except Exception:
            logger.exception("Cache delete error for key %s", cache_key)
            return False

    def delete_pattern(self, pattern: str, *, shared: bool = False) -> int:
        """
        Delete all keys matching *pattern* (supports ``*`` wildcard).

        Falls back to the django-redis ``delete_pattern`` method; returns 0
        if the backend does not support it.
        """
        cache_key_pattern = self.make_key(pattern, shared=shared)
        try:
            delete_fn = getattr(self._cache, "delete_pattern", None)
            if delete_fn is not None:
                return delete_fn(cache_key_pattern)
            # Fallback — backend does not support pattern delete
            logger.debug("Cache backend does not support delete_pattern.")
            return 0
        except Exception:
            logger.exception("Cache delete_pattern error for %s", cache_key_pattern)
            return 0

    # ── Bulk operations ───────────────────────────────────────────────

    def get_many(self, keys: Sequence[str], *, shared: bool = False) -> dict[str, Any]:
        """Get multiple keys at once."""
        mapping = {self.make_key(k, shared=shared): k for k in keys}
        try:
            raw = self._cache.get_many(list(mapping.keys()))
            return {mapping[ck]: v for ck, v in raw.items()}
        except Exception:
            logger.exception("Cache get_many error")
            return {}

    def set_many(
        self,
        data: dict[str, Any],
        timeout: int | None = None,
        *,
        shared: bool = False,
    ) -> bool:
        """Set multiple keys at once."""
        mapped = {self.make_key(k, shared=shared): v for k, v in data.items()}
        try:
            self._cache.set_many(mapped, timeout)
            return True
        except Exception:
            logger.exception("Cache set_many error")
            return False

    # ── Counter operations ────────────────────────────────────────────

    def incr(self, key: str, delta: int = 1, *, shared: bool = False) -> int | None:
        """Increment a counter."""
        cache_key = self.make_key(key, shared=shared)
        try:
            return self._cache.incr(cache_key, delta)
        except ValueError:
            # Key does not exist; initialize it
            self._cache.set(cache_key, delta)
            return delta
        except Exception:
            logger.exception("Cache incr error for key %s", cache_key)
            return None

    def decr(self, key: str, delta: int = 1, *, shared: bool = False) -> int | None:
        """Decrement a counter."""
        cache_key = self.make_key(key, shared=shared)
        try:
            return self._cache.decr(cache_key, delta)
        except ValueError:
            self._cache.set(cache_key, -delta)
            return -delta
        except Exception:
            logger.exception("Cache decr error for key %s", cache_key)
            return None


def get_tenant_cache(cache_alias: str = "default") -> TenantCache:
    """Factory function that returns a *TenantCache* instance."""
    return TenantCache(cache_alias)
