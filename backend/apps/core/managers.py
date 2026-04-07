"""
Core model managers and querysets for tenant-schema models.

Provides reusable Manager and QuerySet classes that leverage the
core mixins (StatusMixin, SoftDeleteMixin) to offer convenient
filtering helpers across all tenant apps.

Managers:
    ActiveManager:
        Default-filters to ``is_active=True``.
        Use on models that include ``StatusMixin``.

    SoftDeleteManager:
        Default-filters to ``is_deleted=False``.
        Use on models that include ``SoftDeleteMixin``.

    AliveManager:
        Default-filters to ``is_active=True`` AND ``is_deleted=False``.
        Use on models that include *both* StatusMixin and SoftDeleteMixin.

QuerySets:
    ActiveQuerySet:
        Adds ``.active()`` and ``.inactive()`` helpers.

    SoftDeleteQuerySet:
        Adds ``.alive()`` and ``.dead()`` helpers.

    AliveQuerySet:
        Combines both helpers — ``.active()``, ``.inactive()``,
        ``.alive()``, ``.dead()``.

Usage::

    from apps.core.managers import ActiveManager, SoftDeleteManager

    class MyModel(StatusMixin, models.Model):
        objects = ActiveManager()          # default qs filters is_active=True
        all_objects = models.Manager()     # unfiltered fallback

    class AnotherModel(SoftDeleteMixin, models.Model):
        objects = SoftDeleteManager()      # default qs filters is_deleted=False
        all_objects = models.Manager()     # unfiltered fallback
"""

from django.db import models


# ---------------------------------------------------------------------------
# QuerySets
# ---------------------------------------------------------------------------
class ActiveQuerySet(models.QuerySet):
    """QuerySet helpers for models with ``StatusMixin``."""

    def active(self):
        """Return only active records (``is_active=True``)."""
        return self.filter(is_active=True)

    def inactive(self):
        """Return only inactive records (``is_active=False``)."""
        return self.filter(is_active=False)


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet helpers for models with ``SoftDeleteMixin``."""

    def alive(self):
        """Return non-deleted records (``is_deleted=False``)."""
        return self.filter(is_deleted=False)

    def dead(self):
        """Return soft-deleted records (``is_deleted=True``)."""
        return self.filter(is_deleted=True)


class AliveQuerySet(models.QuerySet):
    """
    Combined QuerySet for models with both ``StatusMixin``
    and ``SoftDeleteMixin``.
    """

    def active(self):
        """Return only active records (``is_active=True``)."""
        return self.filter(is_active=True)

    def inactive(self):
        """Return only inactive records (``is_active=False``)."""
        return self.filter(is_active=False)

    def alive(self):
        """Return non-deleted records (``is_deleted=False``)."""
        return self.filter(is_deleted=False)

    def dead(self):
        """Return soft-deleted records (``is_deleted=True``)."""
        return self.filter(is_deleted=True)

    def active_alive(self):
        """
        Return records that are both active and not soft-deleted.

        This is the most common filter for user-facing queries.
        """
        return self.filter(is_active=True, is_deleted=False)


# ---------------------------------------------------------------------------
# Managers
# ---------------------------------------------------------------------------
class ActiveManager(models.Manager):
    """
    Manager that returns only active records by default.

    The default queryset filters ``is_active=True``.
    Attach ``all_objects = models.Manager()`` alongside this manager
    if you need unfiltered access.
    """

    def get_queryset(self):
        return ActiveQuerySet(self.model, using=self._db).active()


class SoftDeleteManager(models.Manager):
    """
    Manager that excludes soft-deleted records by default.

    The default queryset filters ``is_deleted=False``.
    Attach ``all_objects = models.Manager()`` alongside this manager
    if you need unfiltered access (including deleted records).
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class AliveManager(models.Manager):
    """
    Manager that returns only *active AND non-deleted* records.

    Combines ``is_active=True`` and ``is_deleted=False``.
    Ideal for models that use both ``StatusMixin`` and ``SoftDeleteMixin``.
    """

    def get_queryset(self):
        return AliveQuerySet(self.model, using=self._db).active_alive()
