"""
BankStatement model for the accounting application.

Stores imported bank statement headers with date range, balances,
file reference, and import status tracking.
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.accounting.models.enums import ImportStatus, StatementFormat
from apps.core.mixins import UUIDMixin


class BankStatement(UUIDMixin, models.Model):
    """
    Imported bank statement header.

    Represents a single bank statement file import with metadata
    about the statement period, balances, and import processing status.
    """

    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Statement Name",
        help_text="Descriptive identifier (e.g., 'December 2025 Statement').",
    )

    bank_account = models.ForeignKey(
        "accounting.BankAccount",
        on_delete=models.PROTECT,
        related_name="statements",
        verbose_name="Bank Account",
        help_text="Bank account this statement belongs to.",
    )

    statement_format = models.CharField(
        max_length=10,
        choices=StatementFormat.choices,
        default=StatementFormat.CSV,
        verbose_name="Format",
        help_text="File format of the imported statement.",
    )

    start_date = models.DateField(
        db_index=True,
        verbose_name="Start Date",
        help_text="First transaction date in the statement.",
    )

    end_date = models.DateField(
        db_index=True,
        verbose_name="End Date",
        help_text="Last transaction date in the statement.",
    )

    opening_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Opening Balance",
        help_text="Statement opening balance.",
    )

    closing_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Closing Balance",
        help_text="Statement closing balance.",
    )

    file = models.FileField(
        upload_to="statements/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Statement File",
        help_text="Uploaded statement file.",
    )

    import_status = models.CharField(
        max_length=20,
        choices=ImportStatus.choices,
        default=ImportStatus.PENDING,
        db_index=True,
        verbose_name="Import Status",
        help_text="Current import processing status.",
    )

    import_error = models.TextField(
        blank=True,
        null=True,
        verbose_name="Import Error",
        help_text="Error message if import failed.",
    )

    import_line_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Imported Lines",
        help_text="Number of transaction lines imported.",
    )

    imported_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Imported At",
        help_text="Timestamp when import was completed.",
    )

    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="statements_imported",
        verbose_name="Imported By",
    )

    is_reconciled = models.BooleanField(
        default=False,
        verbose_name="Reconciled",
        help_text="Whether this statement has been fully reconciled.",
    )

    reconciled_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Reconciled At",
        help_text="Timestamp when reconciliation was completed.",
    )

    reconciled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reconciled_statements",
        verbose_name="Reconciled By",
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Additional notes about this statement.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="statements_created",
        verbose_name="Created By",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = "accounting_bank_statement"
        verbose_name = "Bank Statement"
        verbose_name_plural = "Bank Statements"
        ordering = ["-end_date", "-start_date"]
        indexes = [
            models.Index(
                fields=["bank_account", "start_date", "end_date"],
                name="idx_stmt_bank_period",
            ),
        ]

    def __str__(self):
        return (
            f"{self.bank_account.account_name} "
            f"({self.start_date} to {self.end_date})"
        )

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": "End date must be on or after start date."}
            )

    @property
    def balance_movement(self):
        """Net balance change during the statement period."""
        return self.closing_balance - self.opening_balance

    def get_period_days(self):
        """Number of days covered by this statement (inclusive)."""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def get_period_display(self):
        """Human-readable period string."""
        if self.start_date and self.end_date:
            if self.start_date.month == self.end_date.month:
                return (
                    f"{self.start_date.strftime('%B')} "
                    f"{self.start_date.day}-{self.end_date.day}, "
                    f"{self.end_date.year}"
                )
            return f"{self.start_date.strftime('%b %d')} - {self.end_date.strftime('%b %d, %Y')}"
        return ""

    @property
    def is_period_complete(self):
        """True if end_date is in the past."""
        if self.end_date:
            return self.end_date < timezone.now().date()
        return False

    def overlaps_with(self, other):
        """Check if this statement's period overlaps with another."""
        if not all([self.start_date, self.end_date, other.start_date, other.end_date]):
            return False
        return self.start_date <= other.end_date and other.start_date <= self.end_date

    def get_expected_closing_balance(self):
        """Calculate expected closing balance from lines."""
        from django.db.models import Sum

        agg = self.lines.aggregate(
            total_debits=Sum("debit_amount"),
            total_credits=Sum("credit_amount"),
        )
        debits = agg["total_debits"] or Decimal("0")
        credits = agg["total_credits"] or Decimal("0")
        return self.opening_balance + credits - debits

    def get_balance_discrepancy(self):
        """Difference between actual and expected closing balance."""
        return self.closing_balance - self.get_expected_closing_balance()

    @property
    def is_balanced(self):
        """True if discrepancy is within 0.01."""
        return abs(self.get_balance_discrepancy()) <= Decimal("0.01")

    def get_balance_summary(self):
        """Summary dict of all balance information."""
        expected = self.get_expected_closing_balance()
        return {
            "opening": self.opening_balance,
            "closing": self.closing_balance,
            "change": self.balance_movement,
            "expected": expected,
            "discrepancy": self.closing_balance - expected,
        }

    def get_unreconciled_count(self):
        """Count of statement lines not yet reconciled."""
        from apps.accounting.models.enums import MatchStatus

        return self.lines.filter(match_status=MatchStatus.UNMATCHED).count()

    def get_reconciliation_percentage(self):
        """Percentage of lines that have been matched (0-100)."""
        total = self.lines.count()
        if total == 0:
            return 0.0
        matched = total - self.get_unreconciled_count()
        return (matched / total) * 100
