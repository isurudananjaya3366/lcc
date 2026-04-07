"""Payslip line item models for earnings, deductions, and employer contributions."""

from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class PayslipEarning(UUIDMixin, TimestampMixin, models.Model):
    """Stores an individual earning line item on a payslip.

    Each record represents one earning component (e.g. Basic Salary,
    Transport Allowance) with its current-period amount and YTD total.
    """

    payslip = models.ForeignKey(
        "payslip.Payslip",
        on_delete=models.CASCADE,
        related_name="earnings",
        help_text="Payslip this earning belongs to.",
    )
    component_code = models.CharField(
        max_length=20,
        db_index=True,
        help_text="System identifier (e.g. BASIC, TRANSPORT).",
    )
    component_name = models.CharField(
        max_length=100,
        help_text="Display name (e.g. Basic Salary).",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Earning amount for this period.",
    )
    ytd_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Year-to-date total for this component.",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Sort order on the payslip.",
    )
    is_highlighted = models.BooleanField(
        default=False,
        help_text="Whether to highlight this earning on the PDF.",
    )

    class Meta:
        app_label = "payslip"
        verbose_name = "Payslip Earning"
        verbose_name_plural = "Payslip Earnings"
        ordering = ["display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["payslip", "component_code"],
                name="unique_earning_component_per_payslip",
            ),
        ]

    def __str__(self):
        return f"{self.component_name} - {self.amount}"


class PayslipDeduction(UUIDMixin, TimestampMixin, models.Model):
    """Stores an individual deduction line item on a payslip.

    Each record represents one deduction component (e.g. EPF Employee,
    PAYE Tax) with its current-period amount and YTD total.
    """

    payslip = models.ForeignKey(
        "payslip.Payslip",
        on_delete=models.CASCADE,
        related_name="deductions",
        help_text="Payslip this deduction belongs to.",
    )
    component_code = models.CharField(
        max_length=20,
        db_index=True,
        help_text="System identifier (e.g. EPF_EMPLOYEE, PAYE).",
    )
    component_name = models.CharField(
        max_length=100,
        help_text="Display name (e.g. EPF - Employee Contribution).",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Deduction amount for this period.",
    )
    ytd_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Year-to-date total for this component.",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Sort order on the payslip.",
    )
    is_highlighted = models.BooleanField(
        default=False,
        help_text="Whether to highlight this deduction on the PDF.",
    )

    class Meta:
        app_label = "payslip"
        verbose_name = "Payslip Deduction"
        verbose_name_plural = "Payslip Deductions"
        ordering = ["display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["payslip", "component_code"],
                name="unique_deduction_component_per_payslip",
            ),
        ]

    def __str__(self):
        return f"{self.component_name} - {self.amount}"


class PayslipEmployerContribution(UUIDMixin, TimestampMixin, models.Model):
    """Stores an employer contribution line item on a payslip.

    Each record represents one employer-side contribution (e.g. EPF Employer,
    ETF) with its current-period amount and YTD total.
    """

    payslip = models.ForeignKey(
        "payslip.Payslip",
        on_delete=models.CASCADE,
        related_name="employer_contributions",
        help_text="Payslip this contribution belongs to.",
    )
    component_code = models.CharField(
        max_length=20,
        db_index=True,
        help_text="System identifier (e.g. EPF_EMPLOYER, ETF).",
    )
    component_name = models.CharField(
        max_length=100,
        help_text="Display name (e.g. EPF - Employer Contribution).",
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Contribution amount for this period.",
    )
    ytd_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Year-to-date total for this component.",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Sort order on the payslip.",
    )

    class Meta:
        app_label = "payslip"
        verbose_name = "Payslip Employer Contribution"
        verbose_name_plural = "Payslip Employer Contributions"
        ordering = ["display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["payslip", "component_code"],
                name="unique_employer_contrib_per_payslip",
            ),
        ]

    def __str__(self):
        return f"{self.component_name} - {self.amount}"
