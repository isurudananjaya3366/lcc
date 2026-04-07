from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin


class ExemptionType(models.TextChoices):
    PERSONAL = "PERSONAL", "Personal Relief"
    SPOUSE = "SPOUSE", "Spouse Relief"
    CHILD = "CHILD", "Child Relief"
    DISABLED_CHILD = "DISABLED_CHILD", "Disabled Child Relief"
    OTHER = "OTHER", "Other Exemption"


class TaxExemption(UUIDMixin, TimestampMixin, models.Model):
    """Tax exemption/relief configuration for PAYE calculation.

    Defines tax relief amounts that reduce taxable income before
    applying progressive tax rates. Standard Sri Lankan exemptions
    include personal relief, spouse relief, and child relief.
    """

    name = models.CharField(
        max_length=200,
        help_text="Exemption name (e.g. 'Personal Relief').",
    )
    code = models.CharField(
        max_length=50,
        help_text="Unique code for programmatic reference (e.g. 'PERSONAL').",
    )
    exemption_type = models.CharField(
        max_length=50,
        choices=ExemptionType.choices,
        default=ExemptionType.OTHER,
        help_text="Category of this exemption.",
    )
    tax_year = models.IntegerField(
        default=2024,
        help_text="Tax year for which this exemption is applicable (e.g. 2024).",
    )
    annual_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Annual exemption amount in LKR.",
    )
    monthly_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Monthly exemption amount (usually annual / 12).",
    )
    max_claims = models.IntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times this exemption can be claimed. Leave empty for unlimited.",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this exemption is currently applicable.",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Description of the exemption and its legal basis.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Tax Exemption"
        verbose_name_plural = "Tax Exemptions"

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        super().clean()
        errors = {}
        if self.annual_amount is not None and self.annual_amount <= 0:
            errors["annual_amount"] = "Annual amount must be positive."
        if self.monthly_amount is not None and self.monthly_amount <= 0:
            errors["monthly_amount"] = "Monthly amount must be positive."
        if self.max_claims is not None and self.max_claims < 1:
            errors["max_claims"] = "Max claims must be at least 1."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.monthly_amount and self.annual_amount:
            self.monthly_amount = self.annual_amount / Decimal("12")
        super().save(*args, **kwargs)

    def get_total_annual_exemption(self, claim_count=1):
        """Calculate total annual exemption for given claim count.

        Respects max_claims limit if set.
        """
        if claim_count < 1:
            return Decimal("0")
        if self.max_claims is not None:
            claim_count = min(claim_count, self.max_claims)
        return self.annual_amount * claim_count
