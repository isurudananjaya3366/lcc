"""
LankaCommerce Cloud – Caching Layer (SP09)

Provides tenant-scoped caching with automatic key prefixing,
cache decorators for views/methods, and invalidation utilities.

Usage::

    from apps.core.cache import TenantCache, get_tenant_cache
    from apps.core.cache import cache_response, cache_method, cache_queryset
    from apps.core.cache import CacheInvalidator
    from apps.core.cache.constants import CACHE_TTL_SHORT, CACHE_TTL_MEDIUM, CACHE_TTL_LONG
"""

from apps.core.cache.constants import (
    CACHE_TTL_LONG,
    CACHE_TTL_MEDIUM,
    CACHE_TTL_SHORT,
)
from apps.core.cache.decorators import cache_method, cache_queryset, cache_response
from apps.core.cache.invalidation import CacheInvalidator
from apps.core.cache.tenant_cache import TenantCache, get_tenant_cache
from apps.core.cache.utils import (
    cache_get_or_set,
    cache_stats,
    clear_cache,
    hash_key,
    make_cache_key,
)

__all__ = [
    "CACHE_TTL_SHORT",
    "CACHE_TTL_MEDIUM",
    "CACHE_TTL_LONG",
    "TenantCache",
    "get_tenant_cache",
    "cache_response",
    "cache_method",
    "cache_queryset",
    "CacheInvalidator",
    "make_cache_key",
    "hash_key",
    "cache_get_or_set",
    "clear_cache",
    "cache_stats",
]
