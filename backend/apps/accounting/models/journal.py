"""
Legacy journal entry line model for the accounting application.

This module contains the legacy JournalEntry model which records
individual debit and credit entries. This model will be superseded
by the JournalEntryLine model in SP09 Group B. Kept for backward
compatibility with existing code and migrations.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounting.constants import (
    DEFAULT_ENTRY_STATUS,
    ENTRY_STATUS_CHOICES,
    ENTRY_STATUS_POSTED,
)
from apps.core.mixins import TimestampMixin, UUIDMixin

# Price field constants (consistent across all apps)
PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2


class LegacyJournalEntry(UUIDMixin, TimestampMixin, models.Model):
    """
    Legacy double-entry journal entry line.

    Records an individual debit or credit entry against an account.
    Entries are grouped by reference_number to form balanced
    transactions where total debits must equal total credits.
    All monetary values are in LKR (₨).

    NOTE: This model predates the SP09 Journal Entry system.
    It will be superseded by JournalEntryLine once SP09 Group B
    is implemented. The db_table is preserved for migration
    compatibility.
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
