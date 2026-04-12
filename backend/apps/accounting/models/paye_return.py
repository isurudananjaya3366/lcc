"""
PAYE return model.

Stores PAYE (Pay As You Earn) return data including employee counts,
total remuneration, PAYE deductions, and per-employee breakdowns.
"""

from django.db import models

from apps.core.mixins import UUIDMixin

from ..tax.enums import FilingStatus


class PAYEReturn(UUIDMixin, models.Model):
    """
    PAYE return for a specific tax period.

    Tracks employee count, total remuneration, PAYE deducted,
    and detailed per-employee schedules for IRD T-10 form.
    """

    # ── Period Reference ────────────────────────────────────────────
    period = models.ForeignKey(
        "accounting.TaxPeriodRecord",
        on_delete=models.PROTECT,
        related_name="paye_returns",
    )
    reference_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text="Auto-generated reference (PAYE-YYYYMM-XXXXX).",
    )

    # ── Summary Fields ──────────────────────────────────────────────
    total_employees = models.PositiveIntegerField(
        default=0,
        verbose_name="Total Employees",
        help_text="Count of employees paid during the period.",
    )
    total_remuneration = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total Remuneration",
        help_text="Sum of all gross salaries (basic + allowances + bonuses).",
    )
    total_paye_deducted = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total PAYE Deducted",
        help_text="Sum of PAYE tax deducted from all employees.",
    )

    # ── Employee Details ────────────────────────────────────────────
    employee_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-employee breakdown: NIC, salary, taxable income, PAYE, YTD.",
    )

    # ── Filing ──────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=FilingStatus.choices,
        default=FilingStatus.GENERATED,
    )
    filed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    # ── Timestamps ──────────────────────────────────────────────────
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounting_paye_return"
        verbose_name = "PAYE Return"
        verbose_name_plural = "PAYE Returns"
        ordering = ["-period__year", "-period__period_number"]

    def __str__(self):
        return f"PAYE Return {self.reference_number}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        year = self.period.year
        month = self.period.period_number
        count = PAYEReturn.objects.filter(
            period__year=year,
        ).count() + 1
        return f"PAYE-{year}{month:02d}-{count:05d}"
