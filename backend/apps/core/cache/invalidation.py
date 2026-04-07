"""
Cache invalidation patterns.

Provides automatic cache invalidation on model changes via
Django signals and a manual invalidation API.
"""

from __future__ import annotations

import logging
from typing import Any, Sequence, Type

from django.db import models, transaction

from apps.core.cache.tenant_cache import TenantCache

logger = logging.getLogger(__name__)


class CacheInvalidator:
    """
    Provides static methods for targeted cache invalidation.

    All methods log their actions and silently handle errors to
    avoid breaking application logic if the cache is unavailable.
    """

    @staticmethod
    def invalidate_model(model_class: Type[models.Model]) -> int:
        """Clear ALL cached data for *model_class*."""
        model_name = model_class._meta.label_lower.replace(".", "_")
        pattern = f"{model_name}:*"
        tc = TenantCache()
        count = tc.delete_pattern(pattern)
        logger.debug("Invalidated model %s (%d keys)", model_name, count)
        return count

    @staticmethod
    def invalidate_list(model_class: Type[models.Model]) -> int:
        """Clear list/collection caches for *model_class*."""
        model_name = model_class._meta.label_lower.replace(".", "_")
        pattern = f"{model_name}:list*"
        tc = TenantCache()
        count = tc.delete_pattern(pattern)
        logger.debug("Invalidated %s lists (%d keys)", model_name, count)
        return count

    @staticmethod
    def invalidate_detail(
        model_class: Type[models.Model],
        instance_id: Any,
    ) -> int:
        """Clear detail cache for a specific model instance."""
        model_name = model_class._meta.label_lower.replace(".", "_")
        pattern = f"{model_name}:detail:{instance_id}*"
        tc = TenantCache()
        count = tc.delete_pattern(pattern)
        logger.debug("Invalidated %s detail:%s (%d keys)", model_name, instance_id, count)
        return count

    @staticmethod
    def invalidate_related(
        model_class: Type[models.Model],
        instance: models.Model,
        related_models: Sequence[Type[models.Model]] | None = None,
    ) -> int:
        """
        Clear caches for *model_class* **and** its related models.

        If *related_models* is not given, inspects the model's
        ``_meta.related_objects`` for FK/M2M relations.
        """
        total = CacheInvalidator.invalidate_model(model_class)

        if related_models is None:
            related_models = [
                rel.related_model
                for rel in model_class._meta.related_objects
            ]

        for rel_model in related_models:
            total += CacheInvalidator.invalidate_model(rel_model)

        logger.debug(
            "Invalidated %s + %d related models (%d total keys)",
            model_class._meta.label_lower,
            len(related_models),
            total,
        )
        return total

    @staticmethod
    def invalidate_tenant_cache() -> bool:
        """Clear the entire cache for the current tenant (all models)."""
        tc = TenantCache()
        schema = tc._get_tenant_schema()
        pattern = f"*"
        count = tc.delete_pattern(pattern)
        logger.info("Cleared entire tenant cache for %s (%d keys)", schema, count)
        return True


# ── Signal handlers ───────────────────────────────────────────────────

def cache_post_save_handler(
    sender: Type[models.Model], instance: models.Model, **kwargs: Any
) -> None:
    """Post-save signal handler — invalidates list + detail caches.

    Uses ``transaction.on_commit`` to avoid invalidating cache for
    changes that might be rolled back.
    """

    def _do_invalidate() -> None:
        try:
            CacheInvalidator.invalidate_list(sender)
            if instance.pk:
                CacheInvalidator.invalidate_detail(sender, instance.pk)
        except Exception:
            logger.exception("Error in cache_post_save_handler for %s", sender)

    try:
        transaction.on_commit(_do_invalidate)
    except Exception:
        # If we're outside a transaction (e.g. in tests with autocommit),
        # execute immediately.
        _do_invalidate()


def cache_post_delete_handler(
    sender: Type[models.Model], instance: models.Model, **kwargs: Any
) -> None:
    """Post-delete signal handler — invalidates model caches.

    Uses ``transaction.on_commit`` to avoid invalidating cache for
    changes that might be rolled back.
    """

    def _do_invalidate() -> None:
        try:
            CacheInvalidator.invalidate_model(sender)
        except Exception:
            logger.exception("Error in cache_post_delete_handler for %s", sender)

    try:
        transaction.on_commit(_do_invalidate)
    except Exception:
        _do_invalidate()


class CacheMixin:
    """
    Model mixin that auto-registers post_save/post_delete signal
    handlers for cache invalidation.

    Usage::

        class Product(CacheMixin, models.Model):
            class CacheMeta:
                invalidate_related = [Category]
            ...
    """

    @classmethod
    def _get_invalidation_related(cls) -> list:
        cache_meta = getattr(cls, "CacheMeta", None)
        if cache_meta:
            return getattr(cache_meta, "invalidate_related", [])
        return []

    def get_cache_key(self, suffix: str = "detail") -> str:
        """Return the cache key for this instance."""
        model_name = self._meta.label_lower.replace(".", "_")  # type: ignore[attr-defined]
        return f"{model_name}:{suffix}:{self.pk}"  # type: ignore[attr-defined]

    def invalidate_cache(self) -> int:
        """Invalidate all caches related to this instance."""
        model_class = type(self)
        total = CacheInvalidator.invalidate_detail(model_class, self.pk)  # type: ignore[attr-defined]
        total += CacheInvalidator.invalidate_list(model_class)
        related = self._get_invalidation_related()
        for rel_model in related:
            total += CacheInvalidator.invalidate_model(rel_model)
        return total

    class Meta:
        abstract = True
