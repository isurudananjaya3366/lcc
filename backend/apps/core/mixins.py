"""
Core model mixins for tenant-schema models.

Reusable abstract model mixins for all tenant-schema models in the
LankaCommerce Cloud platform. These mixins provide consistent field
patterns across tenant business applications (products, inventory,
customers, orders, etc.).

These mixins mirror the platform mixins (apps.platform.models.mixins)
but are intended for use in TENANT_APPS. They reside in apps.core
(a SHARED_APP) so they are importable from any tenant app without
introducing cross-app dependencies.

Mixins:
    UUIDMixin:
        UUID v4 primary key replacing Django's default BigAutoField.
        All tenant models that require globally unique, non-sequential
        identifiers should inherit this mixin. Aligns with the platform
        UUID pattern for consistency across public and tenant schemas.

    TimestampMixin:
        Automatic created_on / updated_on audit timestamps.
        All tenant models should inherit this mixin for consistent
        audit trail support. Field names follow the project naming
        conventions (created_on / updated_on, NOT created_at / updated_at).

    AuditMixin:
        Extended audit tracking combining timestamps with user tracking.
        Includes created_by and updated_by fields to record which user
        performed the action. Tenant models that need full audit trails
        should inherit this mixin instead of TimestampMixin.

    StatusMixin:
        Active/inactive lifecycle flags with an optional deactivation
        timestamp. Tenant models that can be enabled or disabled should
        inherit this mixin for consistent lifecycle management.

    SoftDeleteMixin:
        Soft deletion behavior with is_deleted flag and deleted_on
        timestamp. Models inheriting this mixin are never physically
        removed from the database. Instead, they are marked as deleted
        and filtered out by default in application queries.

Usage:
    Tenant-schema models should inherit from the mixins appropriate
    to their domain. The recommended inheritance order is UUIDMixin
    first, then TimestampMixin or AuditMixin, then StatusMixin and/or
    SoftDeleteMixin, then django.db.models.Model:

        from apps.core.mixins import UUIDMixin, TimestampMixin

        class Product(UUIDMixin, TimestampMixin, models.Model):
            name = models.CharField(max_length=255)
            ...

            class Meta:
                app_label = "products"
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class UUIDMixin(models.Model):
    """
    Abstract mixin providing a UUID v4 primary key.

    Replaces Django's default auto-incrementing BigAutoField with a
    UUID v4 field. This provides globally unique, non-sequential
    identifiers suitable for distributed systems and public APIs.

    Aligns with the platform UUID pattern (apps.platform.models.mixins)
    to ensure consistency across public and tenant schemas.

    Fields:
        id (UUIDField): Primary key, auto-generated UUID v4 value.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
        help_text="Unique identifier (UUID v4).",
    )

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """
    Abstract mixin providing created/updated audit timestamps.

    Automatically tracks when a record was first created and when
    it was last modified. Field names follow the project naming
    conventions: created_on / updated_on (NOT created_at / updated_at).

    Fields:
        created_on (DateTimeField): Set once on initial creation.
            Uses django.utils.timezone.now as the default value.
            Not editable after creation.

        updated_on (DateTimeField): Updated on every save.
            Uses auto_now to automatically refresh the timestamp
            whenever the model instance is saved.
    """

    created_on = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Created on",
        help_text="Timestamp when this record was created.",
    )
    updated_on = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated on",
        help_text="Timestamp when this record was last updated.",
    )

    class Meta:
        abstract = True


class AuditMixin(TimestampMixin):
    """
    Abstract mixin providing full audit tracking.

    Extends TimestampMixin with user tracking fields to record which
    user created and last modified a record. This provides a complete
    audit trail for tenant business data.

    Inherits:
        TimestampMixin: created_on, updated_on timestamps.

    Additional Fields:
        created_by (ForeignKey): The user who created the record.
            References AUTH_USER_MODEL. Nullable to allow system-
            generated records (e.g., migrations, signals).

        updated_by (ForeignKey): The user who last modified the record.
            References AUTH_USER_MODEL. Nullable to allow system
            updates.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name="Created by",
        help_text="User who created this record.",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name="Updated by",
        help_text="User who last updated this record.",
    )

    class Meta:
        abstract = True


class StatusMixin(models.Model):
    """
    Abstract mixin providing active/inactive lifecycle flags.

    Tracks whether a record is currently active and when it was
    deactivated. Tenant models that can be enabled or disabled
    should inherit this mixin for consistent lifecycle management.

    Fields:
        is_active (BooleanField): Whether the record is currently
            active. Defaults to True on creation.

        deactivated_on (DateTimeField): When the record was
            deactivated. Null when active. Should be set when
            is_active is changed to False.
    """

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Whether this record is currently active.",
    )
    deactivated_on = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deactivated on",
        help_text="Timestamp when this record was deactivated.",
    )

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    Abstract mixin providing soft deletion behavior.

    Instead of physically removing records from the database, this
    mixin marks them as deleted with a timestamp. Application queries
    should filter out soft-deleted records by default using
    .filter(is_deleted=False) or a custom manager.

    Fields:
        is_deleted (BooleanField): Whether the record has been
            soft-deleted. Defaults to False.

        deleted_on (DateTimeField): When the record was soft-deleted.
            Null when not deleted. Set automatically when is_deleted
            is changed to True.
    """

    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Deleted",
        help_text="Whether this record has been soft-deleted.",
    )
    deleted_on = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deleted on",
        help_text="Timestamp when this record was soft-deleted.",
    )

    class Meta:
        abstract = True
