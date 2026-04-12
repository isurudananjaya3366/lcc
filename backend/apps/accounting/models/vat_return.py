"""
VAT return model.

Stores VAT return data for Sri Lankan businesses including output VAT,
input VAT, net payable amounts, and detailed line item breakdowns.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin

from ..tax.enums import FilingStatus


class VATReturn(UUIDMixin, models.Model):
    """
    VAT return for a specific tax period.

    Tracks output VAT (sales), input VAT (purchases), net payable,
    and detailed transaction breakdowns for IRD compliance.
    """

    # ── Period Reference ────────────────────────────────────────────
    period = models.ForeignKey(
        "accounting.TaxPeriodRecord",
        on_delete=models.PROTECT,
        related_name="vat_returns",
    )
    reference_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text="Auto-generated reference (VAT-YYYYMM-XXXXX).",
    )

    # ── VAT Amounts ─────────────────────────────────────────────────
    output_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Output VAT",
        help_text="Total VAT collected on sales (8% standard rate).",
    )
    input_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Input VAT",
        help_text="Total claimable VAT paid on purchases.",
    )
    net_vat_payable = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Net VAT Payable",
        help_text="Output VAT minus Input VAT. Negative = refund position.",
    )

    # ── Breakdown ───────────────────────────────────────────────────
    line_items = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed transaction breakdown by category.",
    )

    # ── Filing ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=FilingStatus.choices,
        default=FilingStatus.GENERATED,
    )
    filed_date = models.DateTimeField(null=True, blank=True)
    filed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="filed_vat_returns",
    )
    notes = models.TextField(blank=True, default="")

    # ── Timestamps ──────────────────────────────────────────────────
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_vat_return"
        verbose_name = "VAT Return"
        verbose_name_plural = "VAT Returns"
        ordering = ["-period__year", "-period__period_number"]

    def __str__(self):
        return f"VAT Return {self.reference_number}"

    def save(self, *args, **kwargs):
        self.net_vat_payable = self.output_vat - self.input_vat
        if not self.reference_number:
            self.reference_number = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        year = self.period.year
        month = self.period.period_number
        count = VATReturn.objects.filter(
            period__year=year,
        ).count() + 1
        return f"VAT-{year}{month:02d}-{count:05d}"

    @property
    def is_refund_position(self):
        return self.net_vat_payable < 0

    @property
    def is_late(self):
        from django.utils import timezone

        if self.status in (FilingStatus.FILED, FilingStatus.ACCEPTED):
            return False
        return timezone.now().date() > self.period.due_date
