from django.db import models

from apps.core.mixins import UUIDMixin


class EmployeeSalaryComponent(UUIDMixin, models.Model):
    """Employee-specific component value within a salary assignment.

    Stores the actual amount for each component in an employee's salary,
    which may differ from the template's default value if overridden.
    """

    employee_salary = models.ForeignKey(
        "payroll.EmployeeSalary",
        on_delete=models.CASCADE,
        related_name="salary_components",
        help_text="The employee salary this component belongs to.",
    )
    component = models.ForeignKey(
        "payroll.SalaryComponent",
        on_delete=models.PROTECT,
        related_name="employee_usages",
        help_text="The salary component.",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Actual amount for this component.",
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage used if component is percentage-based.",
    )
    calculated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="System-calculated amount before any override.",
    )
    is_overridden = models.BooleanField(
        default=False,
        help_text="Whether this amount was manually overridden from the template default.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Notes about this component value or override.",
    )

    class Meta:
        unique_together = ("employee_salary", "component")

    def __str__(self):
        return f"{self.component.name}: {self.amount}"
