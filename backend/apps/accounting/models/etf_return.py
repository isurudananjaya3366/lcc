"""
ETF return model.

Stores ETF (Employees' Trust Fund) return data including
3% employer-only contributions and per-employee schedules.
"""

from django.db import models

from apps.core.mixins import UUIDMixin

from ..tax.enums import FilingStatus


class ETFReturn(UUIDMixin, models.Model):
    """
    ETF return for a specific tax period.

    Tracks 3% employer-only contribution and per-employee schedules
    for ETF Board filing.
    """

    # ── Period Reference ────────────────────────────────────────────
    period = models.ForeignKey(
        "accounting.TaxPeriodRecord",
        on_delete=models.PROTECT,
        related_name="etf_returns",
    )
    reference_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text="Auto-generated reference (ETF-YYYYMM-XXXXX).",
    )

    # ── Contribution Fields ─────────────────────────────────────────
    total_contribution = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total ETF Contribution (3%)",
    )
    total_gross_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Total Gross Salary Base",
    )
    total_employees = models.PositiveIntegerField(default=0)

    # ── Employee Schedule ───────────────────────────────────────────
    employee_schedule = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-employee ETF contribution breakdown.",
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
        db_table = "accounting_etf_return"
        verbose_name = "ETF Return"
        verbose_name_plural = "ETF Returns"
        ordering = ["-period__year", "-period__period_number"]

    def __str__(self):
        return f"ETF Return {self.reference_number}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        year = self.period.year
        month = self.period.period_number
        count = ETFReturn.objects.filter(period__year=year).count() + 1
        return f"ETF-{year}{month:02d}-{count:05d}"
