"""
Platform model mixins.

Reusable abstract model mixins for all public schema models in the
LankaCommerce Cloud platform. These mixins provide consistent field
patterns across the platform application.

Mixins:
    UUIDMixin:
        UUID v4 primary key replacing Django's default BigAutoField.
        Requires the PostgreSQL uuid-ossp extension to be available.
        All platform models should inherit this mixin to ensure
        globally unique, non-sequential primary keys.

    TimestampMixin:
        Automatic created_on / updated_on audit timestamps.
        All platform models should inherit this mixin for consistent
        audit trail support. Field names follow the project naming
        conventions (see docs/database/naming-conventions.md).

    StatusMixin:
        Active/inactive lifecycle flags with an optional deactivation
        timestamp. All platform models that can be enabled or disabled
        should inherit this mixin (e.g., SubscriptionPlan, FeatureFlag).
        PlatformSetting and AuditLog typically do not need this mixin.

    SoftDeleteMixin:
        Soft deletion behavior with is_deleted flag and deleted_on
        timestamp. Models inheriting this mixin are never physically
        removed from the database. Instead, they are marked as deleted
        and filtered out by default in application queries. All platform
        models that store business-critical data should use this mixin
        (e.g., SubscriptionPlan, BillingRecord, AuditLog).

Usage:
    All public schema platform models should inherit from the mixins
    appropriate to their domain. The recommended inheritance order is
    UUIDMixin first, then TimestampMixin, then StatusMixin and/or
    SoftDeleteMixin, then django.db.models.Model:

        class SubscriptionPlan(
            UUIDMixin, TimestampMixin, StatusMixin, SoftDeleteMixin, models.Model
        ):
            ...

    This ensures UUID primary key takes precedence, timestamps are
    automatically managed, and lifecycle/deletion behavior is consistent.
"""

import uuid

from django.db import models
from django.utils import timezone


class UUIDMixin(models.Model):
    """
    Abstract mixin providing a UUID v4 primary key.

    Replaces Django's default auto-incrementing BigAutoField with a
    UUID v4 field. This provides globally unique, non-sequential
    identifiers suitable for distributed systems and public APIs.

    Requirements:
        - PostgreSQL uuid-ossp extension must be available.
          This is enabled by default in most PostgreSQL installations
          and in the official Docker image used by this project.

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
    conventions documented in docs/database/naming-conventions.md.

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


class StatusMixin(models.Model):
    """
    Abstract mixin providing active/inactive lifecycle flags.

    Tracks whether a record is currently active and when it was
    deactivated. Models that can be enabled or disabled should
    inherit this mixin for consistent lifecycle management.

    Applicable models:
        - SubscriptionPlan: Plans can be retired/deactivated
        - FeatureFlag: Flags can be toggled on/off
        - BillingRecord: Records can be voided/deactivated

    Not typically needed for:
        - PlatformSetting: Settings are always active (use key presence)
        - AuditLog: Audit entries are immutable records

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

    Applicable models:
        - SubscriptionPlan: Plans should be recoverable
        - BillingRecord: Financial records must never be lost
        - AuditLog: Audit trail must be preserved

    Not typically needed for:
        - PlatformSetting: Settings are overwritten, not deleted
        - FeatureFlag: Flags are deactivated, not deleted

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
