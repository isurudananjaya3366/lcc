"""
RecurringEntry model for the accounting application.

Stores scheduling information for automatic journal entry generation
at defined intervals (daily, weekly, monthly, quarterly, yearly).
Links to JournalEntryTemplate for the entry structure and tracks
execution history via next_run_date and last_run_date.
"""

from django.conf import settings
from django.db import models

from apps.accounting.models.enums import RecurringFrequency
from apps.core.mixins import UUIDMixin


class RecurringEntry(UUIDMixin, models.Model):
    """
    Scheduled recurring journal entry configuration.

    Defines when and how often journal entries should be automatically
    generated from a linked template. Processed by a Celery Beat task
    that queries for due entries and creates journal entries.

    Schedule lifecycle:
        1. Created with start_date → next_run_date = start_date
        2. Celery task finds entries where next_run_date <= today
        3. Entry created from template, last_run_date updated
        4. next_run_date calculated based on frequency
        5. If next_run_date > end_date, is_active set to False
    """

    template = models.ForeignKey(
        "accounting.JournalEntryTemplate",
        on_delete=models.PROTECT,
        related_name="recurring_entries",
        verbose_name="Template",
        help_text="The template used to generate journal entries.",
    )

    frequency = models.CharField(
        max_length=20,
        choices=RecurringFrequency.choices,
        verbose_name="Frequency",
        help_text="How often the entry should be generated.",
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Description of this recurring entry's purpose.",
    )

    # ── Schedule Fields ─────────────────────────────────────────────
    start_date = models.DateField(
        verbose_name="Start Date",
        help_text="Date when recurring entry begins.",
    )

    next_run_date = models.DateField(
        db_index=True,
        verbose_name="Next Run Date",
        help_text="Next scheduled execution date.",
    )

    last_run_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Run Date",
        help_text="Date of last successful execution.",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="End Date",
        help_text="Optional end date; entry deactivates when reached.",
    )

    # ── Active Flag ─────────────────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Whether this recurring entry is active.",
    )

    auto_post = models.BooleanField(
        default=False,
        verbose_name="Auto-Post",
        help_text="Automatically post generated entries (skip draft).",
    )

    # ── Audit Fields ────────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recurring_entries_created",
        verbose_name="Created By",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
    )

    class Meta:
        db_table = "accounting_recurring_entry"
        verbose_name = "Recurring Entry"
        verbose_name_plural = "Recurring Entries"
        ordering = ["next_run_date"]
        indexes = [
            models.Index(
                fields=["is_active", "next_run_date"],
                name="idx_re_active_next_run",
            ),
        ]

    def __str__(self):
        return (
            f"{self.template.name} — {self.get_frequency_display()} "
            f"(next: {self.next_run_date})"
        )

    def save(self, *args, **kwargs):
        """Set next_run_date to start_date on initial creation."""
        if not self.pk and not self.next_run_date:
            self.next_run_date = self.start_date
        super().save(*args, **kwargs)
