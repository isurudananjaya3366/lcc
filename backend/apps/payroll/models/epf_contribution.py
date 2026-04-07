"""EPF Contribution model for tracking individual employee EPF records."""

from decimal import ROUND_HALF_UP, Decimal

from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class EPFContribution(UUIDMixin, TimestampMixin, models.Model):
    """Records EPF contribution details for each employee payroll."""

    employee_payroll = models.ForeignKey(
        "payroll.EmployeePayroll",
        on_delete=models.CASCADE,
        related_name="epf_contributions",
    )
    epf_number = models.CharField(max_length=20, blank=True, default="")
    epf_base = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Total EPF-applicable earnings used as the calculation base.",
    )
    base_calculation_details = models.JSONField(
        blank=True, null=True,
        help_text="Breakdown of components that make up the EPF base.",
    )
    employee_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Employee EPF contribution (default 8%).",
    )
    employer_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Employer EPF contribution (default 12%).",
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Total EPF contribution (employee + employer).",
    )
    employee_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("8.00"),
    )
    employer_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("12.00"),
    )
    calculation_date = models.DateField()
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "payroll_epf_contribution"
        ordering = ["-calculation_date"]
        verbose_name = "EPF Contribution"
        verbose_name_plural = "EPF Contributions"

    def __str__(self):
        employee = self.employee_payroll.employee
        return f"EPF - {employee} - LKR {self.total_amount}"

    def calculate_employee_contribution(self):
        """Recalculate employee EPF from base and rate."""
        self.employee_amount = (
            self.epf_base * self.employee_rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return self.employee_amount

    def calculate_employer_contribution(self):
        """Recalculate employer EPF from base and rate."""
        self.employer_amount = (
            self.epf_base * self.employer_rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return self.employer_amount

    def calculate_total(self):
        """Recalculate total from employee + employer amounts."""
        self.total_amount = self.employee_amount + self.employer_amount
        return self.total_amount
