"""
Loyalty Reward model.

Defines the LoyaltyReward model for configuring tier-specific
and event-based rewards (birthday, anniversary, bonuses, etc.).
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.credit.constants import RewardType


class LoyaltyReward(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Reward configuration for a loyalty program.

    Uses a JSONField for flexible, reward-type-specific configuration.
    Each program can have one reward per reward_type.
    """

    program = models.ForeignKey(
        "credit.LoyaltyProgram",
        on_delete=models.CASCADE,
        related_name="rewards",
    )
    reward_type = models.CharField(
        max_length=20,
        choices=RewardType.choices,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    configuration = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = "credit"
        db_table = "credit_loyalty_rewards"
        unique_together = ["program", "reward_type"]

    def __str__(self):
        return f"{self.program.name} - {self.get_reward_type_display()} - {self.name}"

    @property
    def is_valid_today(self):
        """Check if reward is active and within date range."""
        if not self.is_active:
            return False
        today = timezone.now().date()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True

    # Configuration getters
    def get_points(self):
        return self.configuration.get("points", 0)

    def get_discount(self):
        return Decimal(str(self.configuration.get("discount_percentage", 0)))

    def get_valid_days(self):
        return self.configuration.get("valid_days", 7)

    def get_product_id(self):
        return self.configuration.get("product_id")

    # Configuration setters
    def set_config(self, key, value):
        self.configuration[key] = value

    def update_config(self, data):
        self.configuration.update(data)

    def get_config_display(self):
        """Human-readable configuration summary."""
        parts = []
        points = self.get_points()
        if points:
            parts.append(f"{points} points")
        discount = self.get_discount()
        if discount:
            parts.append(f"{discount}% discount")
        valid_days = self.get_valid_days()
        if parts:
            parts.append(f"(valid {valid_days} days)")
        return " + ".join(parts) if parts else "No configuration"

    def clean(self):
        """Validate configuration and dates."""
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValidationError(
                {"valid_until": "Valid until must be after valid from."}
            )
