from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class EmployeeSalary(UUIDMixin, TimestampMixin, models.Model):
    """Assigns a salary structure to an employee with effective dates.

    Tracks basic salary, gross salary, linked template, and validity period.
    Only one salary record per employee should have is_current=True.
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="salaries",
        help_text="The employee this salary is assigned to.",
    )
    template = models.ForeignKey(
        "payroll.SalaryTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_salaries",
        help_text="Salary template used (optional).",
    )
    salary_grade = models.ForeignKey(
        "payroll.SalaryGrade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_salaries",
        help_text="Salary grade/band for this assignment.",
    )
    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Monthly basic salary amount.",
    )
    gross_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Calculated gross salary (basic + all earnings).",
    )
    effective_from = models.DateField(
        db_index=True,
        help_text="Date from which this salary is effective.",
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date until which this salary is effective (null = ongoing).",
    )
    is_current = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this is the employee's current active salary.",
    )
    revision_number = models.IntegerField(
        default=1,
        help_text="Revision number for tracking salary versions.",
    )
    revision_reason = models.TextField(
        blank=True,
        default="",
        help_text="Reason for this salary revision.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_salaries",
        help_text="User who created this salary record.",
    )

    class Meta:
        ordering = ["-effective_from"]
        verbose_name_plural = "Employee salaries"

    def __str__(self):
        return f"{self.employee} - {self.basic_salary} (from {self.effective_from})"
