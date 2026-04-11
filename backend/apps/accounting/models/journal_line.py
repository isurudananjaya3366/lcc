"""
JournalEntryLine model for the accounting application.

Defines the JournalEntryLine model which represents individual
debit/credit line items within a JournalEntry. Each line references
an Account and records either a debit or credit amount. Lines are
linked to a parent JournalEntry via foreign key.
"""

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.mixins import UUIDMixin


class JournalEntryLine(UUIDMixin, models.Model):
    """
    Individual debit/credit line item within a journal entry.

    Each line records either a debit or credit amount against a
    specific Account. A journal entry consists of two or more lines
    where total debits must equal total credits.

    Rules:
        - Each line has either debit_amount or credit_amount (not both).
        - Amounts must be non-negative.
        - At least 2 lines per journal entry.
        - Sum of debit_amount across lines == sum of credit_amount.
    """

    # ── Parent Entry FK ──────────────────────────────────────────────
    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name="Journal Entry",
        help_text="The parent journal entry this line belongs to.",
    )

    # ── Account FK ───────────────────────────────────────────────────
    account = models.ForeignKey(
        "accounting.Account",
        on_delete=models.PROTECT,
        related_name="journal_lines",
        verbose_name="Account",
        help_text="The account being debited or credited.",
    )

    # ── Debit & Credit ──────────────────────────────────────────────
    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Debit Amount",
        help_text="Debit amount in LKR (₨). Zero if this is a credit line.",
    )
    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Credit Amount",
        help_text="Credit amount in LKR (₨). Zero if this is a debit line.",
    )

    # ── Description ──────────────────────────────────────────────────
    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Line-level description or memo.",
    )

    # ── Sort Order ───────────────────────────────────────────────────
    sort_order = models.IntegerField(
        default=0,
        blank=True,
        verbose_name="Sort Order",
        help_text="Display order within the journal entry.",
    )

    class Meta:
        db_table = "accounting_journal_entry_line"
        verbose_name = "Journal Entry Line"
        verbose_name_plural = "Journal Entry Lines"
        ordering = ["journal_entry", "sort_order"]
        indexes = [
            models.Index(
                fields=["journal_entry", "sort_order"],
                name="idx_jel_entry_order",
            ),
            models.Index(
                fields=["account"],
                name="idx_jel_account",
            ),
        ]

    def __str__(self):
        if self.debit_amount > 0:
            return f"DR {self.debit_amount} — {self.account}"
        return f"CR {self.credit_amount} — {self.account}"

    @property
    def is_debit(self):
        """Return True if this is a debit line."""
        return self.debit_amount > 0

    @property
    def is_credit(self):
        """Return True if this is a credit line."""
        return self.credit_amount > 0

    @property
    def net_amount(self):
        """Return the net amount (debit - credit)."""
        return self.debit_amount - self.credit_amount
