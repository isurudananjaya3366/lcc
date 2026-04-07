"""
Tenant feature flag override model for the LankaCommerce Cloud platform.

Defines the TenantFeatureOverride model for tenant-specific feature flag
overrides. While FeatureFlag defines global feature availability and rollout
percentages, individual tenants may need to opt in early (for beta testing)
or opt out (due to plan restrictions, regulatory requirements, etc.).

A TenantFeatureOverride record supersedes the global FeatureFlag settings
for the specified tenant. The precedence rules for feature flag resolution
are as follows — when determining whether a feature is enabled for a
given tenant, the resolution order is:

    1. Check for a TenantFeatureOverride for the tenant+flag pair
    2. If an override exists, use its is_enabled value
    3. If no override exists, fall back to the global FeatureFlag state

Each tenant may have at most one override per feature flag, enforced
by a unique_together constraint on (tenant, feature_flag).

Table: platform_tenantfeatureoverride
Schema: public (shared)

Override types:
    - Force-enable: is_enabled=True — tenant gets the feature regardless
      of global rollout percentage or flag active state
    - Force-disable: is_enabled=False — tenant is excluded from the feature
      even if the global flag is active and fully rolled out

Common use cases:
    - Beta testing: Enable a feature for specific tenants before global rollout
    - Plan restrictions: Disable premium features for free-tier tenants
    - Regulatory compliance: Disable features that conflict with local regulations
    - Custom agreements: Enable features for enterprise tenants with special contracts
"""

from django.db import models

from apps.platform.models.features import FeatureFlag
from apps.platform.models.mixins import TimestampMixin, UUIDMixin


# ── Constants ────────────────────────────────────────────────

REASON_MAX_LENGTH = 500


# ── Model ────────────────────────────────────────────────────


class TenantFeatureOverride(UUIDMixin, TimestampMixin, models.Model):
    """
    Tenant-specific feature flag override.

    Allows individual tenants to have a different feature flag state
    than the global default. An override explicitly enables or disables
    a feature for one tenant, superseding the global FeatureFlag
    rollout configuration.

    Overrides use UUIDMixin and TimestampMixin only — no StatusMixin
    or SoftDeleteMixin. An override is either present (active) or
    deleted. There is no concept of a "deactivated override."

    Precedence rules:
        Tenant override > Global flag rollout_percentage > Default (disabled)

    Inheritance:
        - UUIDMixin: UUID v4 primary key
        - TimestampMixin: created_on / updated_on audit fields
    """

    # ── Relationships ────────────────────────────────────────

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="feature_overrides",
        help_text="The tenant this override applies to.",
    )

    feature_flag = models.ForeignKey(
        FeatureFlag,
        on_delete=models.CASCADE,
        related_name="tenant_overrides",
        help_text="The feature flag being overridden for this tenant.",
    )

    # ── Override Value ───────────────────────────────────────

    is_enabled = models.BooleanField(
        help_text=(
            "Whether the feature is enabled for this tenant. "
            "True = force-enable, False = force-disable. "
            "This value supersedes the global flag state."
        ),
    )

    # ── Context ──────────────────────────────────────────────

    reason = models.TextField(
        max_length=REASON_MAX_LENGTH,
        blank=True,
        default="",
        help_text=(
            "Optional explanation for why this override was created. "
            "Useful for auditing and understanding override decisions."
        ),
    )

    # ── Meta ─────────────────────────────────────────────────

    class Meta:
        db_table = "platform_tenantfeatureoverride"
        verbose_name = "Tenant Feature Override"
        verbose_name_plural = "Tenant Feature Overrides"
        ordering = ["tenant", "feature_flag"]
        unique_together = [("tenant", "feature_flag")]
        indexes = [
            models.Index(
                fields=["tenant", "feature_flag"],
                name="idx_override_tenant_flag",
            ),
            models.Index(
                fields=["feature_flag"],
                name="idx_override_flag",
            ),
            models.Index(
                fields=["tenant"],
                name="idx_override_tenant",
            ),
        ]

    # ── String Representation ────────────────────────────────

    def __str__(self):
        status = "enabled" if self.is_enabled else "disabled"
        return (
            f"{self.feature_flag.key} → {self.tenant.name} "
            f"({status})"
        )

    # ── Properties ───────────────────────────────────────────

    @property
    def override_type(self):
        """Return a human-readable override type string."""
        return "force-enable" if self.is_enabled else "force-disable"
