"""
Cache utility functions.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Callable

from django.core.cache import caches

from apps.core.cache.constants import CACHE_TTL_MEDIUM, KEY_PREFIX, MAX_KEY_LENGTH
from apps.core.cache.tenant_cache import TenantCache

logger = logging.getLogger(__name__)


def make_cache_key(*parts: str, shared: bool = False) -> str:
    """
    Build a cache key from parts and scope to the current tenant.

    Usage::

        key = make_cache_key("products", "list")
        # => lcc:tenant:acme:products:list
    """
    key = ":".join(parts)
    tc = TenantCache()
    return tc.make_key(key, shared=shared)


def hash_key(key: str) -> str:
    """
    Return an MD5 hex digest of *key*.

    Useful when key length exceeds MAX_KEY_LENGTH.
    """
    return hashlib.md5(key.encode()).hexdigest()


def cache_get_or_set(
    key: str,
    callback: Callable[[], Any],
    timeout: int = CACHE_TTL_MEDIUM,
    cache_alias: str = "default",
    *,
    shared: bool = False,
) -> Any:
    """
    Return the cached value for *key*, or call *callback* to compute
    and cache the result.

    Usage::

        data = cache_get_or_set(
            'dashboard:stats',
            lambda: expensive_computation(),
            timeout=CACHE_TTL_SHORT,
        )
    """
    tc = TenantCache(cache_alias)
    cached = tc.get(key, shared=shared)
    if cached is not None:
        return cached
    value = callback()
    tc.set(key, value, timeout=timeout, shared=shared)
    return value


def clear_cache(
    cache_alias: str = "default",
    pattern: str | None = None,
) -> bool:
    """
    Clear entire cache or keys matching *pattern*.

    Returns True on success.
    """
    try:
        if pattern:
            tc = TenantCache(cache_alias)
            tc.delete_pattern(pattern)
        else:
            caches[cache_alias].clear()
        return True
    except Exception:
        logger.exception("Error clearing cache (alias=%s, pattern=%s)", cache_alias, pattern)
        return False


def cache_stats(cache_alias: str = "default") -> dict[str, Any]:
    """
    Return basic cache statistics.

    Only works with django-redis backend; returns empty dict otherwise.
    """
    try:
        cache = caches[cache_alias]
        client = getattr(cache, "client", None)
        if client is None:
            return {}
        get_client = getattr(client, "get_client", None)
        if get_client is None:
            return {}
        redis_client = get_client()
        info = redis_client.info(section="memory")
        keys_count = redis_client.dbsize()
        return {
            "used_memory": info.get("used_memory_human", "N/A"),
            "total_keys": keys_count,
            "max_memory": info.get("maxmemory_human", "N/A"),
            "hit_rate": info.get("keyspace_hits", 0),
            "miss_rate": info.get("keyspace_misses", 0),
        }
    except Exception:
        logger.debug("Could not retrieve cache stats for alias %s", cache_alias)
        return {}
