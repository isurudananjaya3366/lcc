"""
ReceiptSequence model — tracks daily receipt number sequences per tenant.

Task 33: Used by ReceiptNumberGenerator for atomic sequence management.
"""

from django.db import models

from apps.core.models import BaseModel


class ReceiptSequence(BaseModel):
    """
    Tracks daily receipt number sequences.

    Ensures unique, sequential receipt numbers with daily reset.
    Uses select_for_update() for thread-safe increment.
    """

    date = models.DateField(
        db_index=True,
        help_text="Date for this sequence",
    )
    current_sequence = models.IntegerField(
        default=0,
        help_text="Current sequence number for the date",
    )

    class Meta(BaseModel.Meta):
        db_table = "pos_receipt_sequence"
        verbose_name = "Receipt Sequence"
        verbose_name_plural = "Receipt Sequences"
        constraints = [
            models.UniqueConstraint(
                fields=["date"],
                name="unique_receipt_sequence_per_date",
            ),
        ]

    def __str__(self):
        return f"{self.date}: {self.current_sequence}"
