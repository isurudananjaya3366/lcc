"""
StatementLine model for the accounting application.

Stores individual transaction lines from imported bank statements
with amount, description, reference, and reconciliation tracking.
"""

from django.db import models

from apps.accounting.models.enums import MatchStatus
from apps.core.mixins import UUIDMixin


class StatementLine(UUIDMixin, models.Model):
    """
    Individual transaction line within a bank statement.

    Each line represents a single bank transaction with debit/credit
    amounts, description, reference, and running balance. Lines can
    be matched to journal entries during reconciliation.
    """

    statement = models.ForeignKey(
        "accounting.BankStatement",
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Statement",
        help_text="Parent bank statement.",
    )

    line_number = models.PositiveIntegerField(
        verbose_name="Line Number",
        help_text="Sequential line number within the statement.",
    )

    transaction_date = models.DateField(
        db_index=True,
        verbose_name="Transaction Date",
        help_text="Date the transaction occurred.",
    )

    value_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Value Date",
        help_text="Date the transaction takes effect for interest calculation.",
    )

    posting_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Posting Date",
        help_text="Date the bank processed the transaction.",
    )

    description = models.TextField(
        verbose_name="Description",
        help_text="Transaction description or narration from the bank.",
    )

    description_clean = models.TextField(
        blank=True,
        null=True,
        verbose_name="Cleaned Description",
        help_text="Normalized description for matching.",
    )

    memo = models.TextField(
        blank=True,
        null=True,
        verbose_name="Memo",
        help_text="User annotations during reconciliation.",
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Reference",
        help_text="Bank reference number, cheque number, or transfer reference.",
    )

    reference_type = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Reference Type",
        help_text="Categorisation of reference (e.g., CHEQUE, TRANSFER, CARD).",
    )

    external_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="External Reference",
        help_text="External system reference identifier.",
    )

    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Debit",
        help_text="Debit (withdrawal) amount.",
    )

    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Credit",
        help_text="Credit (deposit) amount.",
    )

    running_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Running Balance",
        help_text="Account balance after this transaction.",
    )

    match_status = models.CharField(
        max_length=20,
        choices=MatchStatus.choices,
        default=MatchStatus.UNMATCHED,
        db_index=True,
        verbose_name="Match Status",
        help_text="Current reconciliation matching status.",
    )

    matched_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matched_statement_lines",
        verbose_name="Matched Entry",
        help_text="Journal entry matched to this statement line.",
    )

    is_reconciled = models.BooleanField(
        default=False,
        verbose_name="Reconciled",
        help_text="Whether this line has been reconciled.",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = "accounting_statement_line"
        verbose_name = "Statement Line"
        verbose_name_plural = "Statement Lines"
        ordering = ["statement", "line_number"]
        unique_together = [("statement", "line_number")]
        indexes = [
            models.Index(
                fields=["transaction_date", "match_status"],
                name="idx_stmt_line_date_match",
            ),
        ]

    def __str__(self):
        amount = self.debit_amount or self.credit_amount
        direction = "DR" if self.debit_amount else "CR"
        return f"Line {self.line_number}: {amount} {direction} - {self.description[:50]}"

    @property
    def net_amount(self):
        """Net amount (positive for credits, negative for debits)."""
        return self.credit_amount - self.debit_amount

    @property
    def amount(self):
        """Signed amount: negative for debits, positive for credits."""
        return self.credit_amount - self.debit_amount

    @property
    def absolute_amount(self):
        """Always-positive amount value."""
        return self.debit_amount if self.debit_amount else self.credit_amount

    @property
    def transaction_type(self):
        """Return 'DEBIT' or 'CREDIT'."""
        return "DEBIT" if self.debit_amount else "CREDIT"

    @property
    def is_debit(self):
        return bool(self.debit_amount)

    @property
    def is_credit(self):
        return bool(self.credit_amount)

    def clean_description(self):
        """Normalise description for matching and store in description_clean."""
        import re

        text = (self.description or "").strip()
        text = re.sub(r"\s+", " ", text)
        text = text.upper()
        self.description_clean = text

    def parse_reference(self):
        """Extract reference from description if not explicitly provided."""
        import re

        if self.reference:
            return
        desc = self.description or ""
        patterns = [
            r"\bREF[:\s]*([A-Z0-9-]+)",
            r"\bCHQ[:\s]*(\d+)",
            r"\bTRF[:\s]*([A-Z0-9]+)",
        ]
        for pat in patterns:
            m = re.search(pat, desc, re.IGNORECASE)
            if m:
                self.reference = m.group(1)
                return
