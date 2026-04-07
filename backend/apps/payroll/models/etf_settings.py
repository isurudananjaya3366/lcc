from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class ETFSettings(UUIDMixin, TimestampMixin, models.Model):
    """ETF (Employees' Trust Fund) rate configuration.

    Stores the employer-only contribution rate as per
    Sri Lankan ETF Act (No. 46 of 1980). Standard rate: 3%.
    Only the employer contributes to ETF (no employee contribution).
    Typically only one active record per tenant.
    """

    employer_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("3.00"),
        verbose_name="Employer Rate (%)",
        help_text="Employer ETF contribution rate as percentage (e.g., 3.00 for 3%).",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether these ETF settings are currently active.",
    )
    effective_from = models.DateField(
        null=True,
        blank=True,
        help_text="Date from which this rate is effective.",
    )

    class Meta:
        ordering = ["-effective_from"]
        verbose_name = "ETF Settings"
        verbose_name_plural = "ETF Settings"

    def __str__(self):
        return f"ETF: Employer {self.employer_rate}%"

    def clean(self):
        super().clean()
        if self.employer_rate is not None and not (0 <= self.employer_rate <= 100):
            raise ValidationError(
                {"employer_rate": "Employer rate must be between 0 and 100."}
            )

    def calculate_employer_contribution(self, etf_base_amount):
        """Calculate the employer ETF contribution.

        Args:
            etf_base_amount: Employee's ETF-applicable earnings.

        Returns:
            Decimal: Employer contribution amount.
        """
        return etf_base_amount * (self.employer_rate / Decimal("100"))
