"""
Reconciliation model for bank reconciliation sessions.

Tracks the reconciliation of bank statement balances against GL
account (book) balances over a specified date range.
"""

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.accounting.models.enums import ReconciliationStatus
from apps.core.mixins import UUIDMixin


class Reconciliation(UUIDMixin, models.Model):
    """
    Bank reconciliation session.

    Compares a bank statement balance to the GL book balance and
    tracks matched items until the difference reaches zero.

    Status workflow:
        IN_PROGRESS → COMPLETED  (balanced)
        IN_PROGRESS → CANCELLED  (abandoned)
    """

    bank_account = models.ForeignKey(
        "accounting.BankAccount",
        on_delete=models.PROTECT,
        related_name="reconciliations",
    )

    bank_statement = models.ForeignKey(
        "accounting.BankStatement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reconciliation",
        help_text="Linked bank statement (optional for manual reconciliations).",
    )

    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)

    statement_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Balance per bank statement.",
    )

    book_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Balance per GL account.",
    )

    difference = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="statement_balance − book_balance.",
    )

    status = models.CharField(
        max_length=20,
        choices=ReconciliationStatus.choices,
        default=ReconciliationStatus.IN_PROGRESS,
    )

    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completed_reconciliations",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_reconciliations",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bank Reconciliation"
        verbose_name_plural = "Bank Reconciliations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "bank_account"]),
            models.Index(fields=["bank_account", "start_date", "end_date"]),
        ]

    def __str__(self):
        return (
            f"Reconciliation {self.bank_account} — "
            f"{self.start_date} to {self.end_date} ({self.get_status_display()})"
        )

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must be >= start date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ── Properties ─────────────────────────────────────────────────

    @property
    def period_days(self):
        return (self.end_date - self.start_date).days + 1

    @property
    def is_month_end(self):
        next_day = self.end_date + timedelta(days=1)
        return next_day.month != self.end_date.month

    @property
    def period_description(self):
        if self.is_month_end:
            return self.end_date.strftime("%B %Y")
        return f"{self.start_date} — {self.end_date}"

    def is_completed(self):
        """Return True if status is COMPLETED."""
        from apps.accounting.models.enums import ReconciliationStatus

        return self.status == ReconciliationStatus.COMPLETED

    def is_in_progress(self):
        """Return True if status is IN_PROGRESS."""
        from apps.accounting.models.enums import ReconciliationStatus

        return self.status == ReconciliationStatus.IN_PROGRESS
