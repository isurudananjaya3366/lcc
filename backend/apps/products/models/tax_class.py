"""
TaxClass model for LankaCommerce Cloud.

Manages tax rates for products in accordance with Sri Lankan tax regulations.
Tax classes allow flexible tax rate configuration per tenant.

Sri Lankan Tax Context:
- VAT (Value Added Tax): Standard rate is 15% (as of 2024)
- Some products are exempt (0%)
- Rates are configurable per tenant
- Each product references a tax class

Examples:
- Standard VAT (15%)
- Zero-rated (0%)
- Essential Goods (0% or reduced rate)
"""

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class TaxClass(BaseModel):
    """
    Represents a tax rate configuration for products.

    Tax classes allow flexible configuration of tax rates per tenant.
    Each product references a tax class which determines the tax rate
    applied during pricing and invoice generation.

    Examples:
        - Standard VAT (15%)
        - Zero-rated (0%)
        - Essential Goods (8%)
        - Exempt (0%)

    Relationships:
        - Products: Many products can use the same tax class

    Tenant Isolation: Each tenant has separate tax classes via
    django-tenants schema isolation.
    """

    # ── Core Fields ─────────────────────────────────────────────────
    name = models.CharField(
        max_length=50,
        verbose_name=_("Tax Class Name"),
        help_text=_("Name of the tax class (e.g., Standard VAT, Zero-rated)."),
    )
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
        verbose_name=_("Tax Rate (%)"),
        help_text=_("Tax rate as percentage (e.g., 15.00 for 15% VAT)."),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
        help_text=_("Optional description for this tax class."),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default Tax Class"),
        help_text=_(
            "Mark as default tax class for new products. "
            "Only one tax class should be default per tenant."
        ),
    )

    class Meta:
        db_table = "products_tax_class"
        verbose_name = _("Tax Class")
        verbose_name_plural = _("Tax Classes")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_default"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.rate}%)"

    def save(self, *args, **kwargs):
        """Ensure only one default tax class exists per tenant."""
        if self.is_default:
            # Unset is_default on all other TaxClass instances
            TaxClass.objects.filter(is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )
        super().save(*args, **kwargs)
