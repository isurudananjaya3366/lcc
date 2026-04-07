"""
Cache decorators for views, methods, and querysets.

All decorators use *TenantCache* so cache keys are automatically
scoped to the current tenant.
"""

from __future__ import annotations

import functools
import hashlib
import logging
from typing import Any, Callable

from apps.core.cache.constants import CACHE_TTL_MEDIUM
from apps.core.cache.tenant_cache import TenantCache

logger = logging.getLogger(__name__)


def cache_response(
    cache_key: str | Callable | None = None,
    timeout: int = CACHE_TTL_MEDIUM,
    cache_alias: str = "default",
    vary_on_tenant: bool = True,
    vary_on_user: bool = False,
):
    """
    Decorator for DRF/Django views that caches the response.

    Usage::

        @cache_response(timeout=300)
        def list(self, request):
            ...

        @cache_response(cache_key='products:featured', timeout=CACHE_TTL_LONG)
        def featured(self, request):
            ...
    """

    def decorator(view_func: Callable) -> Callable:
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            # Determine request — handle both function views and class-based
            request = None
            if args:
                # Class-based view: self, request, ...
                for arg in args:
                    if hasattr(arg, "method") and hasattr(arg, "path"):
                        request = arg
                        break

            # Build the cache key
            _key = _resolve_cache_key(cache_key, view_func, request, kwargs)
            if vary_on_user and request and hasattr(request, "user"):
                user_id = getattr(request.user, "pk", "anon") or "anon"
                _key = f"{_key}:u:{user_id}"

            tc = TenantCache(cache_alias)
            # When vary_on_tenant is False, use shared key space
            shared = not vary_on_tenant

            cached = tc.get(_key, shared=shared)
            if cached is not None:
                return cached

            response = view_func(*args, **kwargs)

            # Only cache successful responses
            status = getattr(response, "status_code", 200)
            if 200 <= status < 300:
                # For DRF responses, cache .data; otherwise cache response
                cache_value = getattr(response, "data", response)
                tc.set(_key, cache_value, timeout=timeout, shared=shared)

            return response

        wrapper.cache_key_prefix = cache_key
        return wrapper

    return decorator


def cache_method(
    cache_key: str | None = None,
    timeout: int = CACHE_TTL_MEDIUM,
    cache_alias: str = "default",
):
    """
    Decorator for caching the return value of an arbitrary method.

    Usage::

        class ProductService:
            @cache_method(timeout=3600)
            def get_popular_products(self, limit=10):
                ...
    """

    def decorator(method: Callable) -> Callable:
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            _key = cache_key or f"method:{method.__qualname__}"
            if kwargs:
                kw_hash = hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()[:8]
                _key = f"{_key}:{kw_hash}"

            tc = TenantCache(cache_alias)
            cached = tc.get(_key)
            if cached is not None:
                return cached

            result = method(*args, **kwargs)
            tc.set(_key, result, timeout=timeout)
            return result

        wrapper.cache_key_prefix = cache_key
        return wrapper

    return decorator


def cache_queryset(
    cache_key: str | None = None,
    timeout: int = CACHE_TTL_MEDIUM,
    cache_alias: str = "default",
):
    """
    Decorator that caches a queryset result (evaluated to list).

    Usage::

        @cache_queryset(cache_key='products:active', timeout=3600)
        def get_active_products():
            return Product.objects.filter(is_active=True)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _key = cache_key or f"qs:{func.__qualname__}"

            tc = TenantCache(cache_alias)
            cached = tc.get(_key)
            if cached is not None:
                return cached

            result = func(*args, **kwargs)
            # Evaluate queryset to list for serialisability
            if hasattr(result, "__iter__") and hasattr(result, "query"):
                result = list(result)

            tc.set(_key, result, timeout=timeout)
            return result

        wrapper.cache_key_prefix = cache_key
        return wrapper

    return decorator


# ── Helpers ───────────────────────────────────────────────────────────

def _resolve_cache_key(
    cache_key: str | Callable | None,
    view_func: Callable,
    request: Any,
    kwargs: dict,
) -> str:
    """Resolve the final cache key string."""
    if callable(cache_key):
        return cache_key(request)
    if cache_key:
        return cache_key
    # Auto-generate from view name + path
    name = getattr(view_func, "__qualname__", view_func.__name__)
    path = getattr(request, "path", "") if request else ""
    query = getattr(request, "META", {}).get("QUERY_STRING", "") if request else ""
    raw = f"view:{name}:{path}"
    if query:
        raw = f"{raw}?{query}"
    return raw
