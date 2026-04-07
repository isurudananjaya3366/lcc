"""
CreditTransaction model for credit transaction tracking.

Records all credit-related activities: purchases on credit,
payments received, adjustments, interest charges, and write-offs.
"""

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.credit.constants import TransactionType


class CreditTransactionStatus(models.TextChoices):
    """Status choices for credit transactions."""

    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    REVERSED = "reversed", "Reversed"


class CreditTransaction(UUIDMixin, TimestampMixin, models.Model):
    """
    Credit transaction record.

    Maintains a complete audit trail of all credit usage and payments
    with running balance tracking.
    """

    # ── Relationships ───────────────────────────────────────────────
    credit_account = models.ForeignKey(
        "credit.CustomerCredit",
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    # ── Transaction Identification ──────────────────────────────────
    transaction_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique transaction number (CT-YYYY-NNNNN).",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        help_text="Type of credit transaction.",
    )

    # ── Amount & Balance ────────────────────────────────────────────
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount (LKR).",
    )
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Credit balance after transaction (LKR).",
    )

    # ── Reference Fields ────────────────────────────────────────────
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Type of reference document (Order, Invoice, etc.).",
    )
    reference_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of reference document.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Additional notes about transaction.",
    )

    # ── Processing ──────────────────────────────────────────────────
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_credit_transactions",
        help_text="User who processed this transaction.",
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Payment method (for payment transactions).",
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Payment reference (cheque number, transaction ID).",
    )
    status = models.CharField(
        max_length=20,
        choices=CreditTransactionStatus.choices,
        default=CreditTransactionStatus.COMPLETED,
        help_text="Transaction status.",
    )

    # ── Reversal Tracking ───────────────────────────────────────────
    is_reversed = models.BooleanField(
        default=False,
        help_text="Whether this transaction has been reversed.",
    )
    reversed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    reversed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reversed_credit_transactions",
    )
    reversal_reason = models.TextField(
        blank=True,
        default="",
    )

    # ── Interest Fields ─────────────────────────────────────────────
    interest_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    interest_days = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    interest_rate_applied = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # ── Date Fields ─────────────────────────────────────────────────
    transaction_date = models.DateTimeField(
        default=timezone.now,
        help_text="When transaction occurred.",
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Payment due date (for credit purchases).",
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        help_text="When payment was made.",
    )
    effective_date = models.DateField(
        default=date.today,
        help_text="Date when transaction takes effect.",
    )

    class Meta:
        verbose_name = "Credit Transaction"
        verbose_name_plural = "Credit Transactions"
        db_table = "credit_transaction"
        ordering = ["-transaction_date", "-created_on"]
        indexes = [
            models.Index(fields=["transaction_date"], name="credit_txn_date_idx"),
            models.Index(fields=["due_date"], name="credit_txn_due_idx"),
            models.Index(
                fields=["credit_account", "transaction_date"],
                name="credit_txn_acct_date_idx",
            ),
            models.Index(
                fields=["transaction_type"], name="credit_txn_type_idx"
            ),
        ]

    def __str__(self):
        return (
            f"{self.transaction_number} - "
            f"{self.get_transaction_type_display()} "
            f"Rs. {self.amount:,.2f}"
        )

    # ── Properties ──────────────────────────────────────────────────

    @property
    def is_credit_transaction(self):
        """Return True if this increases the outstanding balance."""
        return self.transaction_type in (
            TransactionType.CREDIT_PURCHASE,
            TransactionType.INTEREST,
        )

    @property
    def is_debit_transaction(self):
        """Return True if this decreases the outstanding balance."""
        return self.transaction_type in (
            TransactionType.PAYMENT,
            TransactionType.WRITE_OFF,
        )

    @property
    def days_overdue(self):
        """Return days overdue, 0 if not overdue, None if no due date."""
        if not self.due_date:
            return None
        delta = (date.today() - self.due_date).days
        return max(delta, 0)

    @property
    def is_overdue(self):
        """Return True if past due date."""
        if not self.due_date:
            return False
        return date.today() > self.due_date

    @property
    def days_until_due(self):
        """Return days until due date (negative if overdue)."""
        if not self.due_date:
            return None
        return (self.due_date - date.today()).days

    @property
    def can_be_reversed(self):
        """Return True if this transaction can be reversed."""
        return (
            not self.is_reversed
            and self.status == CreditTransactionStatus.COMPLETED
        )
