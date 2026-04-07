from django.db import models

from apps.core.mixins import SoftDeleteMixin, TimestampMixin, UUIDMixin
from apps.payroll.constants import (
    CalculationType,
    ComponentCategory,
    ComponentType,
)


class SalaryComponent(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """Defines a salary component (earning, deduction, or employer contribution).

    Each component has a type, category, calculation method, and flags
    for taxability, EPF applicability, and attendance-based variability.
    Used as building blocks for salary templates and employee salary structures.
    """

    # ── Core Identification ──────────────────────────────────
    name = models.CharField(
        max_length=100,
        help_text="Component name (e.g. 'Basic Salary', 'Transport Allowance').",
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique uppercase code (e.g. 'BASIC', 'EPF_EE').",
    )
    component_type = models.CharField(
        max_length=25,
        choices=ComponentType.choices,
        help_text="Whether this is an earning, deduction, or employer contribution.",
    )
    category = models.CharField(
        max_length=20,
        choices=ComponentCategory.choices,
        help_text="Category classification for grouping and reporting.",
    )

    # ── Calculation Configuration ────────────────────────────
    calculation_type = models.CharField(
        max_length=25,
        choices=CalculationType.choices,
        default=CalculationType.FIXED,
        help_text="How the component amount is calculated.",
    )
    default_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Default fixed amount (used when calculation_type is FIXED).",
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Percentage value (used for PERCENTAGE_OF_BASIC or PERCENTAGE_OF_GROSS).",
    )
    formula = models.TextField(
        blank=True,
        default="",
        help_text="Custom formula expression (used when calculation_type is FORMULA).",
    )

    # ── Flags ────────────────────────────────────────────────
    is_taxable = models.BooleanField(
        default=True,
        help_text="Include in PAYE taxable income calculation.",
    )
    is_epf_applicable = models.BooleanField(
        default=False,
        help_text="Include in EPF base calculation (8% employee + 12% employer).",
    )
    is_fixed = models.BooleanField(
        default=True,
        help_text="Fixed monthly amount (False = attendance/variable-based).",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this component is currently available for use.",
    )

    # ── Display & Description ────────────────────────────────
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order for payslip display (lower = higher on payslip).",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Description of the component and its purpose.",
    )

    class Meta:
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["code"], name="idx_component_code"),
            models.Index(fields=["component_type"], name="idx_component_type"),
            models.Index(fields=["category"], name="idx_component_category"),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)
