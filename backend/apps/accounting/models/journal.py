"""
JournalEntry model for the accounting application.

Defines the JournalEntry model which records individual debit
and credit entries in the double-entry bookkeeping system. Each
entry links to an account and records either a debit or credit
amount in LKR (₨). Entries are grouped by a reference number
to form balanced journal transactions.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.accounting.constants import (
    DEFAULT_ENTRY_STATUS,
    ENTRY_STATUS_CHOICES,
    ENTRY_STATUS_POSTED,
)

# Price field constants (consistent across all apps)
PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2


class JournalEntry(UUIDMixin, TimestampMixin, models.Model):
    """
    Double-entry journal entry line.

    Records an individual debit or credit entry against an account.
    Entries are grouped by reference_number to form balanced
    transactions where total debits must equal total credits.
    All monetary values are in LKR (₨).

    Double-entry rule:
        For every transaction, the sum of debit amounts must
        equal the sum of credit amounts across all entries
        sharing the same reference_number.

    Fields:
        reference_number: Groups entries into a single transaction.
        account: FK to the Account being debited or credited.
        entry_date: Date of the journal entry.
        debit: Debit amount in LKR (0 if credit entry).
        credit: Credit amount in LKR (0 if debit entry).
        description: Description of this entry line.
        status: Entry status (draft, posted, reversed).
        created_by: User who created the entry.
    """

    # ── Reference Number ────────────────────────────────────────────
    reference_number = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name="Reference Number",
        help_text=(
            "Groups entries into a single balanced transaction. "
            "All entries with the same reference must balance."
        ),
    )

    # ── Account FK ──────────────────────────────────────────────────
    account = models.ForeignKey(
        "accounting.Account",
        on_delete=models.PROTECT,
        related_name="journal_entries",
        verbose_name="Account",
        help_text="The account being debited or credited.",
    )

    # ── Entry Date ──────────────────────────────────────────────────
    entry_date = models.DateField(
        default=timezone.now,
        db_index=True,
        verbose_name="Entry Date",
        help_text="Date of the journal entry.",
    )

    # ── Debit & Credit (LKR) ───────────────────────────────────────
    debit = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Debit (LKR)",
        help_text="Debit amount in LKR (₨). Zero if this is a credit entry.",
    )
    credit = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Credit (LKR)",
        help_text="Credit amount in LKR (₨). Zero if this is a debit entry.",
    )

    # ── Description ─────────────────────────────────────────────────
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Description of this journal entry line.",
    )

    # ── Status ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=ENTRY_STATUS_CHOICES,
        default=DEFAULT_ENTRY_STATUS,
        db_index=True,
        verbose_name="Status",
        help_text="Entry status: draft, posted, or reversed.",
    )

    # ── Audit ───────────────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_entries",
        verbose_name="Created By",
        help_text="The user who created this journal entry.",
    )

    class Meta:
        db_table = "accounting_journalentry"
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        ordering = ["-entry_date", "reference_number"]
        indexes = [
            models.Index(
                fields=["reference_number", "entry_date"],
                name="idx_journal_ref_date",
            ),
            models.Index(
                fields=["account", "entry_date"],
                name="idx_journal_account_date",
            ),
            models.Index(
                fields=["-entry_date"],
                name="idx_journal_date_desc",
            ),
        ]

    def __str__(self):
        if self.debit > 0:
            return f"DR {self.debit} LKR — {self.account} ({self.reference_number})"
        return f"CR {self.credit} LKR — {self.account} ({self.reference_number})"

    @property
    def is_debit(self):
        """Return True if this is a debit entry."""
        return self.debit > 0

    @property
    def is_credit(self):
        """Return True if this is a credit entry."""
        return self.credit > 0

    @property
    def is_posted(self):
        """Return True if this entry has been posted."""
        return self.status == ENTRY_STATUS_POSTED

    @property
    def net_amount(self):
        """Return the net amount (debit - credit)."""
        return self.debit - self.credit
