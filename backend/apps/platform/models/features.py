"""
Feature flag model for the LankaCommerce Cloud platform.

Defines the FeatureFlag model for controlling feature availability
across the platform. Feature flags allow gradual rollout, A/B testing,
and instant toggling of functionality without code deployments.

Feature flags exist in the public (shared) schema and apply globally
across all tenants. Tenant-specific overrides will be handled
separately through a TenantFeatureOverride model.

Table: platform_featureflag
Schema: public (shared)

Key naming convention:
    Feature flag keys use lowercase snake_case with a module prefix.
    Examples: webstore.live_chat, inventory.barcode_scanner,
    billing.multi_currency, reports.advanced_analytics

Rollout strategy:
    Each flag has a rollout_percentage (0-100) that determines what
    percentage of tenants receive the feature. A value of 0 means
    the feature is disabled for all tenants, while 100 means it is
    enabled for all. Values between 0 and 100 enable gradual rollout.
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

from apps.platform.models.mixins import StatusMixin, TimestampMixin, UUIDMixin

# ── Constants ────────────────────────────────────────────────

KEY_MAX_LENGTH = 100
NAME_MAX_LENGTH = 200
DESCRIPTION_MAX_LENGTH = 500
ROLLOUT_MIN = 0
ROLLOUT_MAX = 100
ROLLOUT_DEFAULT = 0


# ── Model ────────────────────────────────────────────────────


class FeatureFlag(UUIDMixin, TimestampMixin, StatusMixin, models.Model):
    """
    Feature flag for controlling feature availability.

    Feature flags provide a mechanism to toggle functionality on or
    off without modifying code. They support gradual rollout through
    percentage-based enablement and can be toggled globally or
    overridden per tenant.

    Flags use StatusMixin for is_active/deactivated_on lifecycle
    management. Flags are deactivated rather than deleted — there is
    no SoftDeleteMixin because feature flag history should be
    preserved.

    Inheritance:
        - UUIDMixin: UUID v4 primary key
        - TimestampMixin: created_on / updated_on audit fields
        - StatusMixin: is_active / deactivated_on lifecycle flags
    """

    # ── Identity Fields ──────────────────────────────────────

    key = models.CharField(
        max_length=KEY_MAX_LENGTH,
        unique=True,
        db_index=True,
        help_text=(
            "Unique identifier for the feature flag. Use lowercase "
            "snake_case with a module prefix (e.g. webstore.live_chat)."
        ),
    )

    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text="Human-readable name for the feature flag.",
    )

    description = models.TextField(
        max_length=DESCRIPTION_MAX_LENGTH,
        blank=True,
        default="",
        help_text="Description of what this feature flag controls.",
    )

    # ── Rollout Configuration ────────────────────────────────

    rollout_percentage = models.IntegerField(
        default=ROLLOUT_DEFAULT,
        validators=[
            MinValueValidator(ROLLOUT_MIN),
            MaxValueValidator(ROLLOUT_MAX),
        ],
        help_text=(
            "Percentage of tenants that receive this feature (0-100). "
            "0 = disabled for all, 100 = enabled for all. "
            "Values between allow gradual rollout."
        ),
    )

    # ── Visibility ───────────────────────────────────────────

    is_public = models.BooleanField(
        default=False,
        help_text=(
            "Whether this flag is visible to tenant administrators. "
            "Non-public flags are managed only by platform admins."
        ),
    )

    # ── Meta ─────────────────────────────────────────────────

    class Meta:
        db_table = "platform_featureflag"
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"
        ordering = ["key"]
        indexes = [
            models.Index(
                fields=["key"],
                name="idx_feature_flag_key",
            ),
            models.Index(
                fields=["is_active"],
                name="idx_feature_flag_active",
            ),
            models.Index(
                fields=["is_active", "is_public"],
                name="idx_feature_flag_active_public",
            ),
        ]

    # ── String Representation ────────────────────────────────

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"{self.key} ({status}, {self.rollout_percentage}%)"

    # ── Methods ──────────────────────────────────────────────

    def save(self, *args, **kwargs):
        """Save the feature flag, auto-generating key from name if empty."""
        if not self.key and self.name:
            self.key = slugify(self.name).replace("-", "_")
        super().save(*args, **kwargs)

    # ── Properties ───────────────────────────────────────────

    @property
    def is_fully_rolled_out(self):
        """Return True if flag is active and rolled out to 100%."""
        return self.is_active and self.rollout_percentage == ROLLOUT_MAX

    @property
    def is_disabled(self):
        """Return True if flag is inactive or rollout is 0%."""
        return not self.is_active or self.rollout_percentage == ROLLOUT_MIN

    @property
    def rollout_display(self):
        """Return a human-readable rollout status string."""
        if not self.is_active:
            return "Inactive"
        if self.rollout_percentage == ROLLOUT_MAX:
            return "Fully rolled out"
        if self.rollout_percentage == ROLLOUT_MIN:
            return "Disabled"
        return f"{self.rollout_percentage}% rollout"
