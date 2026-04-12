"""
EPF return model.

Stores EPF (Employees' Provident Fund) C-Form data including
employee contributions (8%), employer contributions (12%),
and per-employee schedules for CBSL submission.
"""

from django.db import models

from apps.core.mixins import UUIDMixin

from ..tax.enums import FilingStatus


class EPFReturn(UUIDMixin, models.Model):
    """
    EPF return (C-Form) for a specific tax period.

    Tracks 8% employee + 12% employer contributions (20% total)
    and detailed per-employee schedules for CBSL filing.
    """

    # ── Period Reference ────────────────────────────────────────────
    period = models.ForeignKey(
        "accounting.TaxPeriodRecord",
        on_delete=models.PROTECT,
        related_name="epf_returns",
    )
    reference_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text="Auto-generated reference (EPF-YYYYMM-XXXXX).",
    )

    # ── Contribution Fields ─────────────────────────────────────────
    total_employee_contribution = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Employee Contribution (8%)",
    )
    total_employer_contribution = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Employer Contribution (12%)",
    )
    total_contribution = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        db_index=True,
        verbose_name="Total Contribution (20%)",
    )
    total_employees = models.PositiveIntegerField(default=0)

    # ── Employee Schedule ───────────────────────────────────────────
    employee_schedule = models.JSONField(
        default=list,
        blank=True,
        help_text="Per-employee EPF contribution breakdown.",
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
        db_table = "accounting_epf_return"
        verbose_name = "EPF Return"
        verbose_name_plural = "EPF Returns"
        ordering = ["-period__year", "-period__period_number"]

    def __str__(self):
        return f"EPF Return {self.reference_number}"

    def save(self, *args, **kwargs):
        self.total_contribution = self.total_employee_contribution + self.total_employer_contribution
        if not self.reference_number:
            self.reference_number = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        year = self.period.year
        month = self.period.period_number
        count = EPFReturn.objects.filter(period__year=year).count() + 1
        return f"EPF-{year}{month:02d}-{count:05d}"
