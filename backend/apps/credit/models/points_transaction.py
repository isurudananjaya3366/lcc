"""
Points Transaction model.

Defines the PointsTransaction model for tracking all point movements —
earning, redemption, expiry, bonuses, and manual adjustments.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.credit.constants import PointsTransactionType


class PointsTransaction(UUIDMixin, TimestampMixin, models.Model):
    """
    Immutable record of a points transaction.

    Every change to a customer's points balance creates a new transaction,
    providing a complete audit trail. Points values are positive for
    earn/bonus and negative for redeem/expire.
    """

    customer_loyalty = models.ForeignKey(
        "credit.CustomerLoyalty",
        on_delete=models.CASCADE,
        related_name="points_transactions",
    )

    # Transaction details
    transaction_type = models.CharField(
        max_length=20,
        choices=PointsTransactionType.choices,
    )
    points = models.IntegerField(
        help_text="Positive for earn/bonus, negative for redeem/expire.",
    )
    balance_after = models.IntegerField(
        help_text="Points balance snapshot after this transaction.",
    )
    description = models.TextField(null=True, blank=True)

    # Reference to originating entity (Order, Promotion, etc.)
    reference_type = models.CharField(max_length=100, null=True, blank=True)
    reference_id = models.UUIDField(null=True, blank=True)

    # Expiry tracking (for EARN transactions)
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when earned points expire.",
    )
    is_expired = models.BooleanField(default=False)

    # Adjustment tracking
    adjusted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="points_adjustments",
    )
    adjustment_reason = models.CharField(max_length=500, null=True, blank=True)

    # Transaction date
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "credit"
        db_table = "credit_points_transaction"
        ordering = ["-transaction_date"]
        indexes = [
            models.Index(
                fields=["customer_loyalty", "-transaction_date"],
                name="idx_pts_txn_loyalty_date",
            ),
            models.Index(fields=["reference_id"], name="idx_pts_txn_reference"),
            models.Index(
                fields=["transaction_type", "is_expired"],
                name="idx_pts_txn_type_expired",
            ),
            models.Index(fields=["expiry_date"], name="idx_pts_txn_expiry"),
        ]

    def __str__(self):
        sign = "+" if self.points >= 0 else ""
        return (
            f"{self.get_transaction_type_display()}: {sign}{self.points} pts "
            f"({self.customer_loyalty.customer})"
        )
