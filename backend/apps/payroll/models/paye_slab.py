from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class PAYETaxSlab(UUIDMixin, TimestampMixin, models.Model):
    """PAYE (Pay As You Earn) tax slab for progressive tax calculation.

    Defines income ranges and corresponding tax rates for Sri Lankan
    PAYE calculation. Multiple slabs per tax year support progressive
    taxation, where higher income brackets are taxed at higher rates.
    """

    tax_year = models.PositiveIntegerField(
        help_text="Tax year (e.g. 2024) these slabs apply to.",
    )
    order = models.IntegerField(
        default=0,
        help_text="Slab sequence number (0, 1, 2, ...) for progressive calculation order.",
    )
    from_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Annual income starting from this amount (inclusive).",
    )
    to_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual income up to this amount (inclusive). Leave empty for top slab.",
    )
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Tax rate as percentage (e.g., 6.00 for 6%).",
    )
    effective_from = models.DateField(
        null=True,
        blank=True,
        help_text="Date from which these slabs become effective.",
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        help_text="Date when these slabs expire (null = currently active).",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this tax slab is currently active.",
    )

    class Meta:
        ordering = ["tax_year", "order"]
        verbose_name = "PAYE Tax Slab"
        verbose_name_plural = "PAYE Tax Slabs"

    def __str__(self):
        to_str = f"{self.to_amount}" if self.to_amount else "∞"
        return f"Slab {self.order}: {self.from_amount} - {to_str} @ {self.rate}% ({self.tax_year})"

    def clean(self):
        super().clean()
        errors = {}
        if self.from_amount is not None and self.from_amount < 0:
            errors["from_amount"] = "From amount must be non-negative."
        if self.to_amount is not None and self.from_amount is not None and self.to_amount <= self.from_amount:
            errors["to_amount"] = "To amount must be greater than from amount."
        if self.rate is not None and not (0 <= self.rate <= 100):
            errors["rate"] = "Tax rate must be between 0 and 100."
        if errors:
            raise ValidationError(errors)

    def calculate_slab_tax(self, taxable_income):
        """Calculate tax for the portion of income falling in this slab.

        Args:
            taxable_income: Total annual taxable income.

        Returns:
            Decimal: Tax amount for this slab only.
        """
        if taxable_income <= self.from_amount:
            return Decimal("0")

        if self.to_amount is None:
            income_in_slab = taxable_income - self.from_amount
        elif taxable_income <= self.to_amount:
            income_in_slab = taxable_income - self.from_amount
        else:
            income_in_slab = self.to_amount - self.from_amount

        return income_in_slab * (self.rate / Decimal("100"))

    @classmethod
    def get_slabs_for_year(cls, tax_year):
        """Get all active tax slabs for a specific year, ordered by slab order."""
        return cls.objects.filter(
            tax_year=tax_year,
            is_active=True,
        ).order_by("order")
