"""
JournalEntry header model for the accounting application.

Defines the JournalEntry model which serves as the header for
double-entry bookkeeping transactions. Each journal entry contains
one or more line items (JournalEntryLine) and captures entry-level
metadata: auto-generated entry number, transaction date, type,
status, source, and posting workflow fields.

Entry Number Format: JE-YYYY-NNNNN (e.g., JE-2026-00001)
"""

from django.conf import settings
from django.db import models

from apps.accounting.models.enums import (
    JournalEntryStatus,
    JournalEntryType,
    JournalSource,
)
from apps.core.mixins import UUIDMixin


class JournalEntry(UUIDMixin, models.Model):
    """
    Journal entry header for double-entry bookkeeping.

    Represents a complete accounting transaction consisting of one
    or more line items where total debits must equal total credits.
    Supports a full lifecycle workflow from draft through approval
    and posting, with voiding via reversal entries.

    Status Lifecycle:
        DRAFT → PENDING_APPROVAL → APPROVED → POSTED → (VOID)

    Fields:
        entry_number:  Auto-generated, format JE-YYYY-NNNNN.
        entry_date:    Transaction date (no default, explicit).
        entry_type:    MANUAL | AUTO | ADJUSTING | REVERSING.
        entry_status:  DRAFT | PENDING_APPROVAL | APPROVED | POSTED | VOID.
        entry_source:  SALES | PURCHASE | PAYROLL | INVENTORY | BANKING | MANUAL | ADJUSTMENT.
        reference:     Optional source document reference (e.g. Invoice #).
        description:   Transaction narration/memo.
        total_debit:   Cached sum of line debit amounts.
        total_credit:  Cached sum of line credit amounts.
        created_by:    User who created the entry.
        posted_by:     User who posted the entry.
        posted_at:     Timestamp when entry was posted.
        reversal_of:   Self-FK linking a reversal to its original entry.
        created_at:    Record creation timestamp.
        updated_at:    Last modification timestamp.
    """

    # ── Entry Number (auto-generated) ──────────────────────────────
    entry_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name="Entry Number",
        help_text="Auto-generated entry number (format: JE-YYYY-NNNNN).",
    )

    # ── Entry Date ──────────────────────────────────────────────────
    entry_date = models.DateField(
        db_index=True,
        verbose_name="Entry Date",
        help_text="Transaction date of the journal entry.",
    )

    # ── Entry Type ──────────────────────────────────────────────────
    entry_type = models.CharField(
        max_length=20,
        choices=JournalEntryType.choices,
        default=JournalEntryType.MANUAL,
        db_index=True,
        verbose_name="Entry Type",
        help_text="Type of journal entry (Manual, Auto, Adjusting, Reversing).",
    )

    # ── Entry Status ────────────────────────────────────────────────
    entry_status = models.CharField(
        max_length=20,
        choices=JournalEntryStatus.choices,
        default=JournalEntryStatus.DRAFT,
        db_index=True,
        verbose_name="Entry Status",
        help_text="Lifecycle status of the journal entry.",
    )

    # ── Entry Source ────────────────────────────────────────────────
    entry_source = models.CharField(
        max_length=20,
        choices=JournalSource.choices,
        default=JournalSource.MANUAL,
        db_index=True,
        verbose_name="Source",
        help_text="Origin/source system of the journal entry.",
    )

    # ── Reference ───────────────────────────────────────────────────
    reference = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Reference",
        help_text="Source document reference (e.g. Invoice #, PO #).",
    )

    # ── Description ─────────────────────────────────────────────────
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Transaction narration or memo.",
    )

    # ── Cached Totals ───────────────────────────────────────────────
    total_debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="Total Debit",
        help_text="Total debit amount (cached from lines).",
    )
    total_credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        editable=False,
        verbose_name="Total Credit",
        help_text="Total credit amount (cached from lines).",
    )

    # ── Created By ──────────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="journal_entries_created",
        null=True,
        blank=True,
        verbose_name="Created By",
        help_text="User who created this journal entry.",
    )

    # ── Posted By / Posted At ───────────────────────────────────────
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="journal_entries_posted",
        null=True,
        blank=True,
        verbose_name="Posted By",
        help_text="User who posted this journal entry.",
    )
    posted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Posted At",
        help_text="Timestamp when this entry was posted.",
    )

    # ── Reversal FK ─────────────────────────────────────────────────
    reversal_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="reversed_by",
        null=True,
        blank=True,
        verbose_name="Reversal Of",
        help_text="Links this reversal entry to the original entry.",
    )

    # ── Timestamps ──────────────────────────────────────────────────
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Timestamp when this record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="Timestamp when this record was last updated.",
    )

    class Meta:
        db_table = "accounting_journal_entry"
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        ordering = ["-entry_date", "-entry_number"]
        indexes = [
            models.Index(
                fields=["entry_date", "entry_number"],
                name="idx_je_date_number",
            ),
            models.Index(
                fields=["entry_status", "entry_date"],
                name="idx_je_status_date",
            ),
            models.Index(
                fields=["entry_type"],
                name="idx_je_type",
            ),
            models.Index(
                fields=["entry_source"],
                name="idx_je_source",
            ),
            models.Index(
                fields=["reference"],
                name="idx_je_reference",
            ),
        ]

    def __str__(self):
        return f"{self.entry_number} — {self.entry_date} ({self.get_entry_status_display()})"

    def save(self, *args, **kwargs):
        """Auto-generate entry_number on first save."""
        if not self.entry_number:
            self.entry_number = self._generate_entry_number()
        super().save(*args, **kwargs)

    def _generate_entry_number(self):
        """
        Generate the next sequential entry number for the year.

        Format: JE-YYYY-NNNNN
        Sequence resets each year and is tenant-isolated (via
        django-tenants schema isolation).
        """
        year = self.entry_date.year
        prefix = f"JE-{year}-"

        last_entry = (
            JournalEntry.objects.filter(entry_number__startswith=prefix)
            .order_by("-entry_number")
            .values_list("entry_number", flat=True)
            .first()
        )

        if last_entry:
            last_seq = int(last_entry.split("-")[2])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f"{prefix}{new_seq:05d}"

    @property
    def is_balanced(self):
        """Return True if total_debit equals total_credit."""
        return self.total_debit == self.total_credit

    @property
    def is_draft(self):
        """Return True if entry is in draft status."""
        return self.entry_status == JournalEntryStatus.DRAFT

    @property
    def is_posted(self):
        """Return True if entry has been posted."""
        return self.entry_status == JournalEntryStatus.POSTED

    @property
    def is_void(self):
        """Return True if entry has been voided."""
        return self.entry_status == JournalEntryStatus.VOID

    @property
    def is_editable(self):
        """Return True if entry can be edited (draft only)."""
        return self.entry_status == JournalEntryStatus.DRAFT
