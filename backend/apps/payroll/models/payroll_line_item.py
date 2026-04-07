"""PayrollLineItem model for detailed salary component breakdowns."""

from decimal import Decimal

from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.payroll.constants import LineType


class PayrollLineItem(UUIDMixin, TimestampMixin, models.Model):
    """Stores a single salary component line for an employee payroll record.

    Each line item represents an earning, deduction, or employer contribution,
    tracking the base amount, calculated amount, adjustments, and final amount.
    Provides detailed payslip breakdown and audit trail.
    """

    # ── Relationships ────────────────────────────────────────
    employee_payroll = models.ForeignKey(
        "payroll.EmployeePayroll",
        on_delete=models.CASCADE,
        related_name="line_items",
        help_text="The employee payroll record this line item belongs to.",
    )
    component = models.ForeignKey(
        "payroll.SalaryComponent",
        on_delete=models.PROTECT,
        related_name="payroll_line_items",
        help_text="The salary component this line item represents.",
    )

    # ── Line Type ────────────────────────────────────────────
    line_type = models.CharField(
        max_length=30,
        choices=LineType.choices,
        help_text="Whether this is an earning, deduction, contribution, or adjustment.",
    )

    # ── Amount Fields ────────────────────────────────────────
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Original component amount from salary structure.",
    )
    calculated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Amount after attendance-based calculations.",
    )
    adjustment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Pro-rata or other adjustments (can be negative).",
    )
    final_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Final amount after all adjustments (appears on payslip).",
    )

    # ── Display & Audit ──────────────────────────────────────
    description = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Display name for payslip (defaults to component name).",
    )
    calculation_notes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Calculation details for auditing.",
    )

    class Meta:
        ordering = ["line_type", "component"]
        verbose_name = "Payroll Line Item"
        verbose_name_plural = "Payroll Line Items"

    def __str__(self):
        return f"{self.description or self.component} - {self.final_amount}"
