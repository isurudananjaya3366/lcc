"""
Customer Loyalty model.

Defines the CustomerLoyalty model that tracks a customer's loyalty account,
points balance, lifetime statistics, and tier assignment.
"""

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.credit.constants import CreditStatus


class CustomerLoyalty(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Customer's loyalty account linked to a loyalty program.

    Tracks points balance, lifetime earned/redeemed, tier assignment,
    and enrollment details.
    """

    customer = models.OneToOneField(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="loyalty_account",
    )
    program = models.ForeignKey(
        "credit.LoyaltyProgram",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loyalty_accounts",
    )

    # Enrollment
    enrolled_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=CreditStatus.choices,
        default=CreditStatus.ACTIVE,
    )

    # Points balance
    points_balance = models.IntegerField(default=0)
    lifetime_points_earned = models.IntegerField(default=0)
    total_points_redeemed = models.IntegerField(default=0)
    last_activity_date = models.DateTimeField(auto_now=True)

    # Tier tracking
    current_tier = models.ForeignKey(
        "credit.LoyaltyTier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tier_members",
    )
    tier_evaluated_at = models.DateTimeField(null=True, blank=True)
    tier_expiry_date = models.DateField(null=True, blank=True)
    tier_upgraded_at = models.DateTimeField(null=True, blank=True)

    # Reward tracking (Group D)
    last_birthday_reward_date = models.DateField(null=True, blank=True)
    last_anniversary_reward_year = models.IntegerField(null=True, blank=True)
    anniversary_rewards_count = models.IntegerField(default=0)

    class Meta:
        app_label = "credit"
        db_table = "credit_customer_loyalty"
        verbose_name_plural = "Customer loyalty accounts"
        indexes = [
            models.Index(fields=["status"], name="idx_loyalty_status"),
            models.Index(fields=["points_balance"], name="idx_loyalty_points"),
        ]

    def __str__(self):
        return f"Loyalty: {self.customer} ({self.points_balance} pts)"

    @property
    def tier_multiplier(self):
        """Return current tier's points multiplier, defaulting to 1."""
        if self.current_tier:
            return self.current_tier.points_multiplier
        return 1

    @property
    def lifetime_points_expired(self):
        """Calculate total expired points from transactions."""
        from apps.credit.constants import PointsTransactionType

        expired = self.points_transactions.filter(
            transaction_type=PointsTransactionType.EXPIRE,
        ).aggregate(total=models.Sum("points"))["total"]
        return abs(expired or 0)
