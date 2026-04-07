"""
Feature flag helper functions.

Provides a simplified API for checking feature flag state throughout
the application. This module wraps the lower-level resolution and
caching utilities from utils/features.py with a cleaner interface.

Primary entry point:
    from apps.platform.utils.flags import is_enabled
    if is_enabled("webstore.live_chat", tenant):
        # Feature is enabled for this tenant
        ...

View decorator:
    from apps.platform.utils.flags import require_feature
    @require_feature("webstore.live_chat")
    def my_view(request):
        ...

Flag lookup:
    from apps.platform.utils.flags import get_flag
    flag = get_flag("webstore.live_chat")
    if flag and flag.is_fully_rolled_out:
        ...

This module re-exports the core resolution functions from
utils/features.py for convenience, so callers can import everything
from a single location:

    from apps.platform.utils.flags import (
        is_enabled,
        get_flag,
        require_feature,
        get_tenant_flags,
        invalidate_feature_cache,
        invalidate_all_feature_caches,
    )
"""

import functools
import logging

from django.http import HttpResponseNotFound

from apps.platform.utils.features import (
    get_tenant_flags,
    invalidate_all_feature_caches,
    invalidate_feature_cache,
    is_flag_enabled,
)

logger = logging.getLogger(__name__)

# ── Re-exports ───────────────────────────────────────────────
# Expose core resolution functions for single-module imports.

__all__ = [
    "is_enabled",
    "get_flag",
    "require_feature",
    "get_tenant_flags",
    "invalidate_feature_cache",
    "invalidate_all_feature_caches",
]


# ── Helper Functions ─────────────────────────────────────────


def is_enabled(flag_key, tenant=None):
    """
    Check whether a feature flag is enabled.

    This is the primary entry point for feature flag checks
    throughout the application. When a tenant is provided, the
    check includes tenant-specific overrides and caching. When
    no tenant is given, only the global flag state is checked.

    Resolution order (with tenant):
        1. Tenant override (authoritative if present)
        2. Global flag state (is_active + rollout_percentage)
        3. Default: disabled

    Resolution (without tenant):
        1. Global flag state (is_active + rollout_percentage > 0)
        2. Default: disabled

    Args:
        flag_key: The feature flag key (e.g. "webstore.live_chat").
        tenant: Optional Tenant model instance. If None, checks
            only the global flag active state.

    Returns:
        bool: True if the feature is enabled.
    """
    if tenant is not None:
        return is_flag_enabled(flag_key, tenant)

    # No tenant — check global flag state only
    from apps.platform.models.features import FeatureFlag

    try:
        flag = FeatureFlag.objects.get(key=flag_key)
        return flag.is_active and flag.rollout_percentage > 0
    except FeatureFlag.DoesNotExist:
        return False


def get_flag(flag_key):
    """
    Retrieve a FeatureFlag instance by its key.

    Returns the FeatureFlag object for inspection or direct
    manipulation. Returns None if the flag does not exist.

    Args:
        flag_key: The feature flag key string
            (e.g. "webstore.live_chat").

    Returns:
        FeatureFlag or None: The flag instance, or None if not found.
    """
    from apps.platform.models.features import FeatureFlag

    try:
        return FeatureFlag.objects.get(key=flag_key)
    except FeatureFlag.DoesNotExist:
        return None


def require_feature(flag_key):
    """
    View decorator that gates access behind a feature flag.

    If the feature flag is not enabled for the current tenant,
    returns a 404 response. The tenant is resolved from the
    request object (set by tenant middleware or feature flag
    middleware).

    Args:
        flag_key: The feature flag key to check.

    Returns:
        Decorator function that wraps the view.

    Usage:
        @require_feature("webstore.live_chat")
        def live_chat_view(request):
            ...
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            tenant = getattr(request, "tenant", None)
            if not is_enabled(flag_key, tenant):
                logger.info(
                    "Feature '%s' not enabled for tenant '%s', "
                    "returning 404.",
                    flag_key,
                    getattr(tenant, "name", "unknown"),
                )
                return HttpResponseNotFound()
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
