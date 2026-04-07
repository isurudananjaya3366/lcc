"""
Core models module.

Provides the base model hierarchy for all tenant-schema business models
in the LankaCommerce Cloud platform.

Base Models Hierarchy:
    TimeStampedModel (created_on, updated_on)
        └── SoftDeleteModel (is_deleted, deleted_on)
            └── AuditModel (created_by, updated_by)

    UUIDModel (UUID v4 primary key + timestamps)

    TenantScopedModel (automatic tenant filtering)

    BaseModel (UUID PK + timestamps + soft delete + status)
        - The recommended base class for most business models.

All models compose from the abstract mixins defined in apps.core.mixins
(UUIDMixin, TimestampMixin, AuditMixin, StatusMixin, SoftDeleteMixin).
"""

from django.conf import settings
from django.db import models

from apps.core.managers import AliveManager, SoftDeleteManager
from apps.core.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    StatusMixin,
    TimestampMixin,
    UUIDMixin,
)


class TimeStampedModel(TimestampMixin, models.Model):
    """
    Abstract model providing created_on / updated_on timestamps.

    Inherits:
        TimestampMixin: created_on, updated_on fields.

    Usage:
        class Article(TimeStampedModel):
            title = models.CharField(max_length=255)
    """

    class Meta:
        abstract = True
        ordering = ["-created_on"]


class SoftDeleteModel(SoftDeleteMixin, TimestampMixin, models.Model):
    """
    Abstract model with soft-delete support and timestamps.

    Provides is_deleted / deleted_on fields. The default manager
    (``objects``) filters out soft-deleted records. Use
    ``all_with_deleted`` to include them.

    Inherits:
        SoftDeleteMixin: is_deleted, deleted_on fields.
        TimestampMixin: created_on, updated_on fields.

    Methods:
        soft_delete(): Mark as deleted.
        restore(): Restore a soft-deleted record.
        hard_delete(): Permanently remove from database.
    """

    objects = SoftDeleteManager()
    all_with_deleted = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-created_on"]

    def soft_delete(self):
        """Mark this record as soft-deleted."""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_on = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_on"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_on = None
        self.save(update_fields=["is_deleted", "deleted_on"])

    def hard_delete(self):
        """Permanently delete this record from the database."""
        super().delete()

    def delete(self, using=None, keep_parents=False):
        """Override delete to use soft-delete by default."""
        self.soft_delete()


class AuditModel(AuditMixin, SoftDeleteMixin, models.Model):
    """
    Abstract model with full audit trail and soft-delete support.

    Provides created_by / updated_by fields (from AuditMixin which
    extends TimestampMixin), plus soft deletion (is_deleted, deleted_on).

    Inherits:
        AuditMixin: created_on, updated_on, created_by, updated_by.
        SoftDeleteMixin: is_deleted, deleted_on.

    Methods:
        soft_delete(), restore(), hard_delete() from SoftDeleteModel pattern.
    """

    objects = SoftDeleteManager()
    all_with_deleted = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-created_on"]

    def soft_delete(self):
        """Mark this record as soft-deleted."""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_on = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_on"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_on = None
        self.save(update_fields=["is_deleted", "deleted_on"])

    def hard_delete(self):
        """Permanently delete this record from the database."""
        super().delete()

    def delete(self, using=None, keep_parents=False):
        """Override delete to use soft-delete by default."""
        self.soft_delete()


class UUIDModel(UUIDMixin, TimestampMixin, models.Model):
    """
    Abstract model with UUID v4 primary key and timestamps.

    Inherits:
        UUIDMixin: UUID v4 ``id`` field as primary key.
        TimestampMixin: created_on, updated_on fields.

    Usage:
        class Token(UUIDModel):
            value = models.CharField(max_length=255)
    """

    class Meta:
        abstract = True
        ordering = ["-created_on"]


class TenantScopedModel(
    UUIDMixin, TimestampMixin, StatusMixin, SoftDeleteMixin, models.Model
):
    """
    Abstract model for tenant-scoped business data.

    Combines UUID primary key, timestamps, active status, and soft-delete.
    Tenant scoping is enforced at the database level via django-tenants
    schema isolation (each tenant has its own PostgreSQL schema), so no
    explicit ``tenant`` ForeignKey is needed here.

    The default manager (``objects``) returns only active, non-deleted
    records. Use ``all_with_deleted`` for unfiltered access.

    Inherits:
        UUIDMixin: UUID v4 primary key.
        TimestampMixin: created_on, updated_on.
        StatusMixin: is_active, deactivated_on.
        SoftDeleteMixin: is_deleted, deleted_on.
    """

    objects = AliveManager()
    all_with_deleted = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-created_on"]

    def soft_delete(self):
        """Mark this record as soft-deleted."""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_on = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_on"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_on = None
        self.save(update_fields=["is_deleted", "deleted_on"])

    def hard_delete(self):
        """Permanently delete this record from the database."""
        super().delete()

    def delete(self, using=None, keep_parents=False):
        """Override delete to use soft-delete by default."""
        self.soft_delete()


class BaseModel(
    UUIDMixin, AuditMixin, StatusMixin, SoftDeleteMixin, models.Model
):
    """
    Recommended base class for most tenant business models.

    Combines all core features:
        - UUID v4 primary key (UUIDMixin)
        - Timestamps: created_on, updated_on (via AuditMixin → TimestampMixin)
        - Audit: created_by, updated_by (AuditMixin)
        - Status: is_active, deactivated_on (StatusMixin)
        - Soft delete: is_deleted, deleted_on (SoftDeleteMixin)

    Default manager (``objects``) returns only active + non-deleted records.
    Use ``all_with_deleted`` for unfiltered access.

    Usage:
        class Product(BaseModel):
            name = models.CharField(max_length=255)
            price = models.DecimalField(max_digits=10, decimal_places=2)

            class Meta(BaseModel.Meta):
                db_table = "products"
    """

    objects = AliveManager()
    all_with_deleted = models.Manager()

    class Meta:
        abstract = True
        ordering = ["-created_on"]

    def soft_delete(self):
        """Mark this record as soft-deleted."""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_on = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_on"])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_on = None
        self.save(update_fields=["is_deleted", "deleted_on"])

    def hard_delete(self):
        """Permanently delete this record from the database."""
        super().delete()

    def delete(self, using=None, keep_parents=False):
        """Override delete to use soft-delete by default."""
        self.soft_delete()

    def __str__(self):
        """Return string representation using pk."""
        return f"{self.__class__.__name__}(pk={self.pk})"
