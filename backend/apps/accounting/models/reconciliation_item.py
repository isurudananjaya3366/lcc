"""
ReconciliationItem model for bank reconciliation.

Each item represents a matched pair: one bank statement line linked
to one journal entry within a reconciliation session.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.accounting.models.enums import MatchType
from apps.core.mixins import UUIDMixin


class ReconciliationItem(UUIDMixin, models.Model):
    """
    A matched pair within a reconciliation session.

    Links a statement line to a journal entry, recording how and
    when the match was made.
    """

    reconciliation = models.ForeignKey(
        "accounting.Reconciliation",
        on_delete=models.CASCADE,
        related_name="items",
    )

    statement_line = models.ForeignKey(
        "accounting.StatementLine",
        on_delete=models.PROTECT,
        related_name="reconciliation_items",
    )

    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.PROTECT,
        related_name="reconciliation_items",
    )

    match_type = models.CharField(
        max_length=20,
        choices=MatchType.choices,
    )

    matched_at = models.DateTimeField(auto_now_add=True)
    matched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="User who created manual match (null for AUTO).",
    )

    notes = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Reconciliation Item"
        verbose_name_plural = "Reconciliation Items"
        ordering = ["matched_at"]
        indexes = [
            models.Index(fields=["reconciliation", "statement_line"]),
            models.Index(fields=["match_type"]),
        ]

    def __str__(self):
        return (
            f"Match: Line {self.statement_line_id} → "
            f"JE {self.journal_entry_id} ({self.get_match_type_display()})"
        )

    def clean(self):
        super().clean()
        if self.match_type == MatchType.MANUAL and not self.matched_by_id:
            raise ValidationError(
                {"matched_by": "Manual matches must specify matched_by."}
            )
