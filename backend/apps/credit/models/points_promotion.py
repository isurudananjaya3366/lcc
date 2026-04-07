"""
PointsPromotion model.

Configurable promotions for bonus points campaigns:
multipliers, flat bonuses, category-specific bonuses,
spend thresholds, first-purchase, and birthday-month.
"""

from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.credit.constants import PromotionType


class PointsPromotion(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Points promotion campaign linked to a LoyaltyProgram.

    Supports multiple promotion types with flexible JSON configuration,
    optional M2M links to categories/products, and tier-gating.
    """

    program = models.ForeignKey(
        "credit.LoyaltyProgram",
        on_delete=models.CASCADE,
        related_name="promotions",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    promotion_type = models.CharField(
        max_length=20,
        choices=PromotionType.choices,
        db_index=True,
    )

    # ── Points Configuration ────────────────────────────────────────
    multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("1.00"),
        help_text="Point multiplier (e.g. 2.0 for double points).",
    )
    bonus_points = models.IntegerField(
        default=0,
        help_text="Flat bonus points to award.",
    )
    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Minimum purchase amount to qualify.",
    )
    configuration = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible JSON configuration for promotion rules.",
    )

    # ── Validity Period ─────────────────────────────────────────────
    valid_from = models.DateTimeField(help_text="Promotion start date/time.")
    valid_to = models.DateTimeField(help_text="Promotion end date/time.")
    is_active = models.BooleanField(default=True, db_index=True)

    # ── Scope ───────────────────────────────────────────────────────
    applicable_categories = models.ManyToManyField(
        "products.Category",
        blank=True,
        related_name="points_promotions",
        help_text="Categories this promotion applies to.",
    )
    applicable_products = models.ManyToManyField(
        "products.Product",
        blank=True,
        related_name="points_promotions",
        help_text="Products this promotion applies to.",
    )
    tier_required = models.ForeignKey(
        "credit.LoyaltyTier",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tier_promotions",
        help_text="Tier required to participate (null = all tiers).",
    )

    class Meta:
        db_table = "credit_points_promotions"
        verbose_name = "Points Promotion"
        verbose_name_plural = "Points Promotions"
        ordering = ["-valid_from", "name"]
        indexes = [
            models.Index(fields=["program", "is_active"]),
            models.Index(fields=["valid_from", "valid_to"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_promotion_type_display()})"

    # ── Properties ──────────────────────────────────────────────────

    @property
    def is_currently_active(self):
        """Check if promotion is active and within validity period."""
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_to

    @property
    def max_bonus_points(self):
        """Get max bonus cap from configuration, if any."""
        return self.configuration.get("max_bonus_points")

    @property
    def exclude_sale_items(self):
        """Whether sale items are excluded from this promotion."""
        return self.configuration.get("exclude_sale_items", False)
