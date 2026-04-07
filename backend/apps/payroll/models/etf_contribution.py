"""ETF Contribution model for tracking employer ETF records."""

from decimal import ROUND_HALF_UP, Decimal

from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class ETFContribution(UUIDMixin, TimestampMixin, models.Model):
    """Records ETF contribution details for each employee payroll.

    ETF is an employer-only contribution (default 3%) in Sri Lanka.
    """

    employee_payroll = models.ForeignKey(
        "payroll.EmployeePayroll",
        on_delete=models.CASCADE,
        related_name="etf_contributions",
    )
    etf_base = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="ETF-applicable earnings base (same as EPF base).",
    )
    base_calculation_details = models.JSONField(
        blank=True, null=True,
        help_text="Breakdown of components that make up the ETF base.",
    )
    employer_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Employer ETF contribution (default 3%).",
    )
    etf_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("3.00"),
    )
    calculation_date = models.DateField()
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "payroll_etf_contribution"
        ordering = ["-calculation_date"]
        verbose_name = "ETF Contribution"
        verbose_name_plural = "ETF Contributions"

    def __str__(self):
        employee = self.employee_payroll.employee
        return f"ETF - {employee} - LKR {self.employer_amount}"

    def calculate_contribution(self):
        """Calculate employer ETF contribution from base and rate."""
        self.employer_amount = (
            self.etf_base * self.etf_rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return self.employer_amount

    def validate_etf_base(self):
        """Validate that ETF base is non-negative."""
        return self.etf_base >= Decimal("0.00")
