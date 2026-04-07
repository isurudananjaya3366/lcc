"""
Platform settings helper utilities.

Provides convenience functions for accessing platform settings
throughout the application. All functions use the cached singleton
approach via PlatformSetting.load(), ensuring minimal database
queries and consistent one-hour cache TTL.

Usage:
    from apps.platform.utils.settings import get_platform_settings
    settings = get_platform_settings()
    print(settings.platform_name)

    from apps.platform.utils.settings import get_setting
    name = get_setting("platform_name")

Cache behavior:
    - Settings are cached for 1 hour (SETTINGS_CACHE_TTL = 3600s)
    - Cache is invalidated automatically on every PlatformSetting.save()
    - Manual invalidation: invalidate_settings_cache()
"""

from django.core.cache import cache


def get_platform_settings():
    """
    Return the cached singleton PlatformSetting instance.

    This is the primary entry point for reading platform settings.
    Uses PlatformSetting.load() which checks the cache first,
    then falls back to the database.

    Returns:
        PlatformSetting: The singleton settings instance.
    """
    from apps.platform.models.settings import PlatformSetting

    return PlatformSetting.load()


def get_setting(field_name, default=None):
    """
    Return a single setting value by field name.

    Convenience wrapper that loads the cached settings and returns
    the value of the specified field. Returns the default value
    if the field does not exist.

    Args:
        field_name: Name of the PlatformSetting field to retrieve.
        default: Value to return if the field does not exist.

    Returns:
        The field value, or default if not found.
    """
    settings = get_platform_settings()
    return getattr(settings, field_name, default)


def invalidate_settings_cache():
    """
    Manually invalidate the platform settings cache.

    Typically not needed since PlatformSetting.save() automatically
    invalidates the cache. Use this when settings need to be
    refreshed outside of normal save operations (e.g., after a
    direct database update or fixture load).
    """
    from apps.platform.models.settings import SETTINGS_CACHE_KEY

    cache.delete(SETTINGS_CACHE_KEY)


def is_maintenance_mode():
    """
    Check whether the platform is in maintenance mode.

    Returns:
        bool: True if maintenance mode is enabled.
    """
    return get_setting("maintenance_mode", False)


def is_feature_enabled(feature_name):
    """
    Check whether a platform-level feature toggle is enabled.

    Supported feature names:
        - webstore (enable_webstore)
        - api_access (enable_api_access)
        - multi_currency (enable_multi_currency)

    Args:
        feature_name: Short feature name without the 'enable_' prefix.

    Returns:
        bool: True if the feature is enabled.
    """
    field_name = f"enable_{feature_name}"
    return get_setting(field_name, False)
