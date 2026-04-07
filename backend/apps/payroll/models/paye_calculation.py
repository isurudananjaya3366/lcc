"""PAYECalculation model for tracking PAYE income tax records."""

from decimal import ROUND_HALF_UP, Decimal

from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class PAYECalculation(UUIDMixin, TimestampMixin, models.Model):
    """Records PAYE tax calculation details for each employee payroll."""

    employee_payroll = models.ForeignKey(
        "payroll.EmployeePayroll",
        on_delete=models.CASCADE,
        related_name="paye_calculations",
    )
    gross_income = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Monthly gross income.",
    )
    taxable_income = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Annual taxable income after exemptions.",
    )
    epf_deduction = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Employee EPF contribution (tax-deductible).",
    )
    exemptions = models.JSONField(
        blank=True, null=True,
        help_text="Breakdown of tax exemptions applied.",
    )
    tax_slabs_applied = models.JSONField(
        blank=True, null=True,
        help_text="Tax slab breakdown showing income and tax per slab.",
    )
    monthly_tax = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
    )
    ytd_gross = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Year-to-date gross income.",
    )
    ytd_tax = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Year-to-date tax paid.",
    )
    annual_projected_tax = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0.00"),
        help_text="Projected annual tax based on current month.",
    )
    calculation_date = models.DateField()
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "payroll_paye_calculation"
        ordering = ["-calculation_date"]
        verbose_name = "PAYE Calculation"
        verbose_name_plural = "PAYE Calculations"

    def __str__(self):
        employee = self.employee_payroll.employee
        return f"PAYE - {employee} - LKR {self.monthly_tax}"

    def calculate_taxable_income(self):
        """Calculate taxable income from gross after exemptions."""
        total_exemptions = Decimal("0.00")
        if self.exemptions:
            total_exemptions = Decimal(str(
                self.exemptions.get("total_exemptions", 0)
            ))
        annual_gross = self.gross_income * Decimal("12")
        self.taxable_income = max(
            annual_gross - total_exemptions, Decimal("0.00")
        )
        return self.taxable_income

    def apply_tax_slabs(self):
        """Apply progressive tax slabs and store breakdown."""
        from apps.payroll.models.paye_slab import PAYETaxSlab

        slabs = PAYETaxSlab.get_slabs_for_year(
            self.calculation_date.year
        )
        slab_details = []
        remaining = self.taxable_income
        total_tax = Decimal("0.00")

        for slab in slabs:
            if remaining <= 0:
                break
            if slab.to_amount is not None:
                slab_range = slab.to_amount - slab.from_amount
                income_in_slab = min(remaining, slab_range)
            else:
                income_in_slab = remaining

            tax = (
                income_in_slab * slab.rate / Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total_tax += tax
            remaining -= income_in_slab

            slab_details.append({
                "from": str(slab.from_amount),
                "to": str(slab.to_amount) if slab.to_amount else None,
                "rate": str(slab.rate),
                "income_in_slab": str(income_in_slab),
                "tax": str(tax),
            })

        self.tax_slabs_applied = {
            "slabs": slab_details,
            "total_taxable_income": str(self.taxable_income),
            "total_annual_tax": str(total_tax),
        }
        self.annual_projected_tax = total_tax
        return total_tax

    def calculate_monthly_tax(self):
        """Calculate monthly tax from annual projected tax."""
        if self.annual_projected_tax > 0:
            self.monthly_tax = (
                self.annual_projected_tax / Decimal("12")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            self.monthly_tax = Decimal("0.00")
        return self.monthly_tax
