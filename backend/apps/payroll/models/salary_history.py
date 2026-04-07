from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.payroll.constants import SalaryChangeReason


class SalaryHistory(UUIDMixin, TimestampMixin, models.Model):
    """Tracks salary changes over time for audit and reporting.

    Records the previous and new salary details whenever an employee's
    salary is revised, along with the reason and effective date.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="salary_history",
        help_text="The employee whose salary changed.",
    )
    salary = models.ForeignKey(
        "payroll.EmployeeSalary",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="history_records",
        help_text="The salary record this history entry relates to.",
    )
    previous_basic = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Previous basic salary amount.",
    )
    new_basic = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="New basic salary amount.",
    )
    previous_gross = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Previous gross salary amount.",
    )
    new_gross = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="New gross salary amount.",
    )
    effective_date = models.DateField(
        help_text="Date from which the new salary is effective.",
    )
    change_reason = models.CharField(
        max_length=20,
        choices=SalaryChangeReason.choices,
        default=SalaryChangeReason.OTHER,
        help_text="Reason for the salary change.",
    )
    remarks = models.TextField(
        blank=True,
        default="",
        help_text="Additional notes about the salary change.",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="salary_changes",
        help_text="User who made this salary change.",
    )

    class Meta:
        ordering = ["-effective_date"]
        verbose_name_plural = "Salary histories"

    def __str__(self):
        return f"{self.employee} - {self.previous_basic} → {self.new_basic}"
