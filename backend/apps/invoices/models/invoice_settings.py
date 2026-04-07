"""
Invoice settings model — per-tenant invoice configuration.
"""

from datetime import timedelta
from decimal import Decimal

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class InvoiceSettings(UUIDMixin, TimestampMixin, models.Model):
    """Per-tenant invoice configuration."""

    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="invoice_settings",
    )

    # ── Numbering ───────────────────────────────────────────────────
    invoice_number_prefix = models.CharField(max_length=10, default="INV")
    credit_note_prefix = models.CharField(max_length=10, default="CN")
    debit_note_prefix = models.CharField(max_length=10, default="DN")
    sequence_start = models.IntegerField(default=1)
    reset_sequence_yearly = models.BooleanField(default=True)

    # ── Defaults ────────────────────────────────────────────────────
    default_due_days = models.IntegerField(default=30)
    default_payment_terms = models.CharField(max_length=100, default="Net 30")
    default_vat_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("12.00"),
    )
    default_tax_inclusive = models.BooleanField(default=False)

    # ── Display ─────────────────────────────────────────────────────
    show_business_registration = models.BooleanField(default=True)
    show_vat_registration = models.BooleanField(default=True)
    show_logo = models.BooleanField(default=True)
    show_bank_details = models.BooleanField(default=True)

    # ── Behavior ────────────────────────────────────────────────────
    auto_send_on_issue = models.BooleanField(default=False)
    auto_issue_from_order = models.BooleanField(default=False)
    require_approval = models.BooleanField(default=False)
    allow_editing_issued = models.BooleanField(default=False)

    # ── Late Fees ───────────────────────────────────────────────────
    apply_late_fees = models.BooleanField(default=False)
    late_fee_type = models.CharField(
        max_length=20,
        choices=[("PERCENTAGE", "Percentage"), ("FIXED", "Fixed Amount")],
        default="PERCENTAGE",
    )
    late_fee_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        help_text="Percentage rate (e.g., 2.00 for 2%)",
    )
    late_fee_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        help_text="Fixed amount in LKR",
    )
    late_fee_grace_days = models.IntegerField(default=7)

    # ── Reminders ───────────────────────────────────────────────────
    send_payment_reminders = models.BooleanField(default=True)
    reminder_days_before_due = models.JSONField(default=list, blank=True)
    reminder_days_after_due = models.JSONField(default=list, blank=True)

    # ── Default Text ────────────────────────────────────────────────
    default_terms_and_conditions = models.TextField(blank=True, default="")
    default_payment_instructions = models.TextField(blank=True, default="")
    default_footer_text = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Invoice Settings"
        verbose_name_plural = "Invoice Settings"

    def __str__(self):
        return f"Invoice Settings (tenant {self.tenant_id})"

    def get_due_date(self, issue_date=None):
        """Calculate due date from issue date."""
        from django.utils import timezone
        if issue_date is None:
            issue_date = timezone.now().date()
        return issue_date + timedelta(days=self.default_due_days)

    def get_payment_terms_text(self):
        """Return formatted payment terms."""
        return self.default_payment_terms or f"Net {self.default_due_days}"
