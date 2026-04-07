"""
CustomerMerge model for tracking merge operations.

Records every customer merge with a full audit trail including
counts of transferred records and a snapshot of the duplicate's
data before the merge.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin


class CustomerMerge(UUIDMixin, models.Model):
    """
    Audit record of a customer merge operation.
    """

    # ── Participants ────────────────────────────────────────────────
    primary_customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="merges_as_primary",
        verbose_name="Primary Customer (kept)",
    )
    duplicate_customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="merges_as_duplicate",
        verbose_name="Duplicate Customer (merged)",
    )
    merged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="customer_merges",
        verbose_name="Merged By",
    )
    merged_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Merged At",
    )
    merge_reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Merge Reason",
    )
    duplicate_score = models.IntegerField(
        default=0,
        verbose_name="Duplicate Score",
        help_text="Confidence score (0-100) from duplicate detection.",
    )

    # ── Transfer Counts ─────────────────────────────────────────────
    orders_transferred = models.IntegerField(default=0)
    invoices_transferred = models.IntegerField(default=0)
    payments_transferred = models.IntegerField(default=0)
    addresses_transferred = models.IntegerField(default=0)
    phones_transferred = models.IntegerField(default=0)
    total_purchases_added = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
    )

    # ── Snapshot ────────────────────────────────────────────────────
    duplicate_customer_snapshot = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Duplicate Snapshot",
        help_text="Full data snapshot of the duplicate before merge.",
    )

    class Meta:
        db_table = "customers_customer_merge"
        verbose_name = "Customer Merge"
        verbose_name_plural = "Customer Merges"
        ordering = ["-merged_at"]
        indexes = [
            models.Index(
                fields=["primary_customer"],
                name="idx_merge_primary",
            ),
            models.Index(
                fields=["duplicate_customer"],
                name="idx_merge_duplicate",
            ),
            models.Index(
                fields=["-merged_at"],
                name="idx_merge_date",
            ),
        ]

    def __str__(self):
        return (
            f"Merge: {self.duplicate_customer} → {self.primary_customer} "
            f"({self.merged_at:%Y-%m-%d})"
        )
