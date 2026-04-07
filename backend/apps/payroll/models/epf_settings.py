from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class EPFSettings(UUIDMixin, TimestampMixin, models.Model):
    """EPF (Employees' Provident Fund) rate configuration.

    Stores the employee and employer contribution rates as per
    Sri Lankan EPF Act (No. 15 of 1958), with an optional
    contribution ceiling. Standard rates: Employee 8%, Employer 12%.
    Typically only one active record per tenant.
    """

    employee_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("8.00"),
        help_text="Employee EPF contribution rate as percentage (e.g., 8.00 for 8%).",
    )
    employer_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("12.00"),
        help_text="Employer EPF contribution rate as percentage (e.g., 12.00 for 12%).",
    )
    max_contribution_ceiling = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Maximum Contribution Ceiling",
        help_text="Maximum monthly earnings amount for EPF calculation. Leave empty for no ceiling.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether these EPF settings are currently active.",
    )
    effective_from = models.DateField(
        null=True,
        blank=True,
        help_text="Date from which these rates are effective.",
    )

    class Meta:
        ordering = ["-effective_from"]
        verbose_name = "EPF Settings"
        verbose_name_plural = "EPF Settings"

    def __str__(self):
        return f"EPF: Employee {self.employee_rate}% / Employer {self.employer_rate}%"

    def clean(self):
        super().clean()
        errors = {}
        if self.employee_rate is not None and not (0 <= self.employee_rate <= 100):
            errors["employee_rate"] = "Employee rate must be between 0 and 100."
        if self.employer_rate is not None and not (0 <= self.employer_rate <= 100):
            errors["employer_rate"] = "Employer rate must be between 0 and 100."
        if self.max_contribution_ceiling is not None and self.max_contribution_ceiling <= 0:
            errors["max_contribution_ceiling"] = "Ceiling must be greater than zero."
        if errors:
            raise ValidationError(errors)

    def get_epf_applicable_amount(self, gross_amount):
        """Return the EPF-applicable amount considering the ceiling.

        If a ceiling is set and gross_amount exceeds it, returns the ceiling.
        Otherwise returns the gross_amount unchanged.
        """
        if self.max_contribution_ceiling is not None and gross_amount > self.max_contribution_ceiling:
            return self.max_contribution_ceiling
        return gross_amount
