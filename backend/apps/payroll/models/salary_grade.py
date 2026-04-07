from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class SalaryGrade(UUIDMixin, TimestampMixin, models.Model):
    """Salary grade/band defining salary ranges and linked templates.

    Grades organize employees into pay bands with minimum and maximum
    salary ranges. Each grade can link to a salary template.
    """

    name = models.CharField(
        max_length=100,
        help_text="Grade name (e.g. 'Grade 1 - Entry Level').",
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique grade code (e.g. 'G1', 'G2').",
    )
    level = models.PositiveIntegerField(
        default=1,
        help_text="Numeric level for ordering (1 = lowest, higher = senior).",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Detailed description of the grade, typical roles, and requirements.",
    )
    min_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Minimum basic salary for this grade.",
    )
    max_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum basic salary for this grade (null for unlimited).",
    )
    template = models.ForeignKey(
        "payroll.SalaryTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grades",
        help_text="Default salary template for this grade.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this grade is currently in use.",
    )

    class Meta:
        ordering = ["level"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.min_salary is not None and self.min_salary <= 0:
            raise ValidationError("Minimum salary must be positive.")
        if (
            self.max_salary is not None
            and self.min_salary is not None
            and self.max_salary < self.min_salary
        ):
            raise ValidationError(
                "Maximum salary cannot be less than minimum salary."
            )

    @property
    def midpoint(self):
        """Calculate the midpoint of the salary range."""
        if self.max_salary is not None and self.min_salary is not None:
            return (self.min_salary + self.max_salary) / Decimal("2")
        return None

    @property
    def range_width(self):
        """Calculate the salary range span."""
        if self.max_salary is not None and self.min_salary is not None:
            return self.max_salary - self.min_salary
        return None
