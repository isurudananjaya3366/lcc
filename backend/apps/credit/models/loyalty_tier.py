"""
Loyalty Tier model.

Defines the LoyaltyTier model for tier-based loyalty programs with
threshold qualifications, benefit configurations, and display settings.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin


class LoyaltyTier(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Loyalty program tier (e.g. Bronze, Silver, Gold, Platinum).

    Tiers provide escalating benefits including points multipliers,
    discounts, and premium features. Customers qualify via lifetime
    points OR lifetime spend thresholds (OR logic).
    """

    program = models.ForeignKey(
        "credit.LoyaltyProgram",
        on_delete=models.CASCADE,
        related_name="tiers",
    )
    name = models.CharField(max_length=100)
    level = models.PositiveIntegerField(
        default=0,
        help_text="Numeric level for ordering (higher = better tier).",
    )

    # Threshold fields (Task 52)
    min_points_required = models.PositiveIntegerField(
        default=0,
        help_text="Minimum lifetime points to qualify for this tier.",
    )
    min_spend_required = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Minimum lifetime spend (Rs.) to qualify for this tier.",
    )

    # Benefit fields (Task 53)
    points_multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1,
        help_text="Points earning multiplier for this tier.",
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Tier discount percentage on purchases.",
    )
    free_shipping = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    early_access = models.BooleanField(default=False)

    # Display fields (Task 54)
    description = models.TextField(blank=True, null=True)
    badge_image = models.ImageField(
        upload_to="loyalty/tier_badges/",
        blank=True,
        null=True,
    )
    color = models.CharField(max_length=7, default="#808080")
    icon = models.CharField(max_length=10, blank=True, null=True)

    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the entry-level tier.",
    )

    class Meta:
        app_label = "credit"
        db_table = "credit_loyalty_tier"
        ordering = ["level"]
        indexes = [
            models.Index(fields=["program", "level"], name="idx_tier_program_level"),
        ]

    def __str__(self):
        return f"{self.name} (Level {self.level})"
