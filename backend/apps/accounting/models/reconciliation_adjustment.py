"""
ReconciliationAdjustment model for bank reconciliation.

Records adjusting journal entries created during a reconciliation
session to account for bank charges, interest, errors, etc.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin


class ReconciliationAdjustment(UUIDMixin, models.Model):
    """
    An adjusting entry created during reconciliation.

    Links a reconciliation session to the journal entry that
    records the adjustment (bank charges, interest, errors, etc.).
    """

    reconciliation = models.ForeignKey(
        "accounting.Reconciliation",
        on_delete=models.CASCADE,
        related_name="adjustments",
    )

    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reconciliation_adjustments",
    )

    ADJUSTMENT_TYPES = [
        ("DEBIT", "Debit"),
        ("CREDIT", "Credit"),
    ]

    adjustment_type = models.CharField(
        max_length=10,
        choices=ADJUSTMENT_TYPES,
    )

    adjustment_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
    )

    adjustment_reason = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return (
            f"{self.get_adjustment_type_display()} adjustment "
            f"{self.adjustment_amount} — {self.adjustment_reason[:50]}"
        )
