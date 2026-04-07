"""
LankaCommerce Cloud - Tenant Signals.

Provides automatic creation of related records when tenants are
created. Ensures every new tenant has a TenantSettings record
with sensible defaults.

Signals:
    create_tenant_settings — post_save on Tenant model.
        Creates a TenantSettings record when a new Tenant is saved
        for the first time (created=True). Uses get_or_create to
        prevent duplicates if called multiple times.

    invalidate_domain_cache_on_save — post_save on Domain model.
        Evicts the SubdomainResolver's Redis cache entry for the changed
        domain, ensuring stale tenant lookups are not served from cache
        after a Domain record is created, updated, or deleted (Task 25).

    invalidate_domain_cache_on_delete — post_delete on Domain model.
        Same as above, triggered when a Domain record is deleted.

    invalidate_custom_domain_cache_on_save — post_save on Domain model.
        Evicts the CustomDomainResolver cache for the changed domain
        (Task 29). Complements subdomain cache invalidation.

    invalidate_custom_domain_cache_on_delete — post_delete on Domain model.
        Same as above, triggered when a Domain record is deleted.
"""

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="tenants.Tenant")
def create_tenant_settings(sender, instance, created, **kwargs):
    """
    Auto-create TenantSettings when a new Tenant is created.

    This signal fires on every Tenant.save(), but only creates
    a TenantSettings record when the tenant is first created
    (created=True). Uses get_or_create as a safety measure
    against duplicate signal firing.

    Args:
        sender: The Tenant model class.
        instance: The Tenant instance that was saved.
        created: True if this is a new record, False if update.
        **kwargs: Additional signal arguments.
    """
    if created:
        from apps.tenants.models import TenantSettings

        _, settings_created = TenantSettings.objects.get_or_create(
            tenant=instance,
        )
        if settings_created:
            logger.info(
                "Created TenantSettings for tenant '%s' (schema: %s)",
                instance.name,
                instance.schema_name,
            )


# ── Task 25: Cache invalidation on Domain change ──────────────────────


@receiver(post_save, sender="tenants.Domain")
def invalidate_domain_cache_on_save(sender, instance, **kwargs):
    """
    Invalidate SubdomainResolver cache when a Domain record is saved.

    Fires on every Domain.save() (both create and update). Evicts the
    cached subdomain → Tenant mapping so that the next request triggers
    a fresh database lookup.

    This prevents stale cache entries after:
        - A new Domain is added for a tenant.
        - A Domain's hostname is changed.
        - A Domain is deactivated or reassigned.

    Args:
        sender: The Domain model class.
        instance: The Domain instance that was saved.
        **kwargs: Additional signal arguments (includes 'created').
    """
    try:
        from apps.tenants.middleware.subdomain_resolver import invalidate_subdomain_cache

        invalidate_subdomain_cache(instance.domain)
        logger.info(
            "Domain cache invalidated on save for domain='%s'",
            instance.domain,
        )
    except Exception as exc:
        # Never block the save operation due to cache errors
        logger.warning(
            "Failed to invalidate domain cache for '%s' on save: %s",
            instance.domain,
            exc,
        )


@receiver(post_delete, sender="tenants.Domain")
def invalidate_domain_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate SubdomainResolver cache when a Domain record is deleted.

    Ensures the cache entry is removed so requests to the deleted domain
    return 404 instead of a cached stale Tenant.

    Args:
        sender: The Domain model class.
        instance: The Domain instance that was deleted.
        **kwargs: Additional signal arguments.
    """
    try:
        from apps.tenants.middleware.subdomain_resolver import invalidate_subdomain_cache

        invalidate_subdomain_cache(instance.domain)
        logger.info(
            "Domain cache invalidated on delete for domain='%s'",
            instance.domain,
        )
    except Exception as exc:
        logger.warning(
            "Failed to invalidate domain cache for '%s' on delete: %s",
            instance.domain,
            exc,
        )


# ── Task 29: Custom domain cache invalidation on Domain change ────────


@receiver(post_save, sender="tenants.Domain")
def invalidate_custom_domain_cache_on_save(sender, instance, **kwargs):
    """
    Invalidate CustomDomainResolver cache when a Domain record is saved.

    Complements invalidate_domain_cache_on_save for the custom domain
    cache (keyed by full domain string instead of subdomain).

    Args:
        sender: The Domain model class.
        instance: The Domain instance that was saved.
        **kwargs: Additional signal arguments.
    """
    try:
        from apps.tenants.middleware.domain_resolver import invalidate_custom_domain_cache

        invalidate_custom_domain_cache(instance.domain)
        logger.info(
            "Custom domain cache invalidated on save for domain='%s'",
            instance.domain,
        )
    except Exception as exc:
        logger.warning(
            "Failed to invalidate custom domain cache for '%s' on save: %s",
            instance.domain,
            exc,
        )


@receiver(post_delete, sender="tenants.Domain")
def invalidate_custom_domain_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate CustomDomainResolver cache when a Domain record is deleted.

    Args:
        sender: The Domain model class.
        instance: The Domain instance that was deleted.
        **kwargs: Additional signal arguments.
    """
    try:
        from apps.tenants.middleware.domain_resolver import invalidate_custom_domain_cache

        invalidate_custom_domain_cache(instance.domain)
        logger.info(
            "Custom domain cache invalidated on delete for domain='%s'",
            instance.domain,
        )
    except Exception as exc:
        logger.warning(
            "Failed to invalidate custom domain cache for '%s' on delete: %s",
            instance.domain,
            exc,
        )
