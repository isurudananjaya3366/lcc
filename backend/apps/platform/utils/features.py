"""
Feature flag resolution and caching utilities.

Provides functions for resolving feature flag state per tenant,
including tenant-specific override handling and caching.

Resolution order (precedence rules):
    1. Tenant override: If a TenantFeatureOverride exists for the
       tenant+flag pair, its is_enabled value is authoritative.
    2. Global flag: If no override exists, the global FeatureFlag
       state is used (is_active AND rollout_percentage determines
       eligibility).
    3. Default: If the flag does not exist at all, the feature is
       considered disabled.

Override interaction with rollout percentage:
    - When a tenant has an override with is_enabled=True, the feature
      is enabled regardless of the global rollout_percentage (even 0%).
    - When a tenant has an override with is_enabled=False, the feature
      is disabled regardless of the global rollout_percentage (even 100%).
    - When no override exists, the rollout_percentage determines
      eligibility based on tenant position in the rollout.

Caching strategy:
    - Feature flags are cached per tenant to avoid repeated DB queries.
    - Cache key format: feature_flags:{tenant_id} — stores a dict of
      all resolved flag states for that tenant.
    - Cache TTL: 1 hour (3600 seconds), matching platform settings cache.
    - Cache is invalidated when:
        - A FeatureFlag is saved or deleted
        - A TenantFeatureOverride is saved or deleted
    - Invalidation scope:
        - Flag changes invalidate ALL tenant caches (global impact)
        - Override changes invalidate only the affected tenant's cache

Usage:
    from apps.platform.utils.features import is_flag_enabled
    if is_flag_enabled("webstore.live_chat", tenant):
        # Feature is enabled for this tenant
        ...

    from apps.platform.utils.features import get_tenant_flags
    flags = get_tenant_flags(tenant)
    # flags = {"webstore.live_chat": True, "billing.multi_currency": False, ...}

    from apps.platform.utils.features import invalidate_feature_cache
    invalidate_feature_cache(tenant_id=tenant.id)
"""

from django.core.cache import cache

# ── Cache Configuration ──────────────────────────────────────

FEATURE_CACHE_KEY_PREFIX = "feature_flags"
FEATURE_CACHE_TTL = 3600  # 1 hour, matching platform settings cache


def _build_cache_key(tenant_id):
    """
    Build a cache key for a tenant's resolved feature flags.

    Args:
        tenant_id: The tenant's primary key (UUID or int).

    Returns:
        str: Cache key in the format "feature_flags:{tenant_id}".
    """
    return f"{FEATURE_CACHE_KEY_PREFIX}:{tenant_id}"


def get_tenant_flags(tenant):
    """
    Return a dict of all resolved feature flag states for a tenant.

    Resolution applies override precedence: tenant override values
    supersede global flag states. Results are cached per tenant.

    Args:
        tenant: A Tenant model instance.

    Returns:
        dict: Mapping of flag key (str) to enabled state (bool).
            Example: {"webstore.live_chat": True, "billing.multi_currency": False}
    """
    cache_key = _build_cache_key(tenant.pk)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Lazy imports to avoid circular dependencies
    from apps.platform.models.features import FeatureFlag
    from apps.platform.models.overrides import TenantFeatureOverride

    # Fetch all active global flags
    flags = FeatureFlag.objects.filter(is_active=True).values_list(
        "key", "rollout_percentage"
    )

    # Build base flag state from global flags
    resolved = {}
    for key, rollout in flags:
        resolved[key] = rollout > 0

    # Fetch tenant-specific overrides and apply them
    overrides = TenantFeatureOverride.objects.filter(
        tenant=tenant,
    ).select_related("feature_flag").values_list(
        "feature_flag__key", "is_enabled"
    )

    for key, is_enabled in overrides:
        resolved[key] = is_enabled

    cache.set(cache_key, resolved, FEATURE_CACHE_TTL)
    return resolved


def is_flag_enabled(flag_key, tenant):
    """
    Check whether a specific feature flag is enabled for a tenant.

    Uses the cached resolved flag states for the tenant. If the
    flag key does not exist in the resolved states, the feature
    is considered disabled.

    Args:
        flag_key: The feature flag key string (e.g. "webstore.live_chat").
        tenant: A Tenant model instance.

    Returns:
        bool: True if the feature is enabled for this tenant.
    """
    flags = get_tenant_flags(tenant)
    return flags.get(flag_key, False)


def invalidate_feature_cache(tenant_id=None):
    """
    Invalidate feature flag cache for a specific tenant or all tenants.

    Call this when a FeatureFlag or TenantFeatureOverride is modified.

    For global flag changes (FeatureFlag save/delete), pass tenant_id=None
    to invalidate all tenant caches. For override changes, pass the
    specific tenant_id to invalidate only that tenant's cache.

    Args:
        tenant_id: The tenant's primary key to invalidate, or None
            to invalidate all tenant caches.
    """
    if tenant_id is not None:
        # Invalidate single tenant cache
        cache_key = _build_cache_key(tenant_id)
        cache.delete(cache_key)
    else:
        # Invalidate all tenant feature caches
        # Since we cannot enumerate cache keys, we use a version-based
        # approach: delete known keys by fetching all tenant IDs
        from apps.tenants.models import Tenant

        tenant_ids = Tenant.objects.values_list("id", flat=True)
        keys = [_build_cache_key(tid) for tid in tenant_ids]
        if keys:
            cache.delete_many(keys)


def invalidate_all_feature_caches():
    """
    Invalidate all tenant feature flag caches.

    Convenience wrapper for invalidate_feature_cache(tenant_id=None).
    Use this when a global FeatureFlag is modified.
    """
    invalidate_feature_cache(tenant_id=None)
