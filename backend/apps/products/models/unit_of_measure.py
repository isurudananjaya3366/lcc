"""
UnitOfMeasure model for LankaCommerce Cloud.

Defines measurement units for products used in inventory tracking,
sales transactions, and pricing.

Common units in Sri Lankan commerce:
- Count: Piece (pcs), Dozen (dz)
- Weight: Kilogram (kg), Gram (g)
- Volume: Liter (l), Milliliter (ml)
- Length: Meter (m), Centimeter (cm)
- Packaging: Box, Carton, Pack

Each product references a unit of measure which determines:
- How quantity is displayed
- How stock is tracked
- Unit conversions (if applicable)
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class UnitOfMeasure(BaseModel):
    """
    Represents a unit of measurement for products.

    Units define how product quantities are measured and displayed.
    Each product has one unit of measure which determines inventory
    tracking and display format.

    Examples:
        - Piece (pcs): Countable items
        - Kilogram (kg): Weight measurement
        - Liter (l): Volume measurement
        - Meter (m): Length measurement

    Relationships:
        - Products: Many products can use the same unit

    Tenant Isolation: Each tenant has separate units via
    django-tenants schema isolation.
    """

    # ── Core Fields ─────────────────────────────────────────────────
    name = models.CharField(
        max_length=50,
        verbose_name=_("Unit Name"),
        help_text=_("Full name of the unit (e.g., Kilogram, Piece, Liter)."),
    )
    symbol = models.CharField(
        max_length=10,
        verbose_name=_("Symbol"),
        help_text=_("Unit abbreviation or symbol (e.g., kg, pcs, l)."),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
        help_text=_("Detailed description of when to use this unit."),
    )

    # ── Conversion Fields ───────────────────────────────────────────
    conversion_factor = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True,
        verbose_name=_("Conversion Factor"),
        help_text=_(
            "Conversion factor to base unit (e.g., 1 g = 0.001 kg). "
            "Leave blank if not applicable."
        ),
    )
    is_base_unit = models.BooleanField(
        default=False,
        verbose_name=_("Base Unit"),
        help_text=_("Mark as base unit for conversions in this category."),
    )

    class Meta:
        db_table = "products_unit_of_measure"
        verbose_name = _("Unit of Measure")
        verbose_name_plural = _("Units of Measure")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["symbol"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_base_unit"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    def clean(self):
        """Validate model data."""
        super().clean()
        # If marked as base unit, conversion_factor should be 1.0
        if self.is_base_unit and self.conversion_factor is not None:
            from decimal import Decimal

            if self.conversion_factor != Decimal("1.0"):
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    {
                        "conversion_factor": _(
                            "Base units must have a conversion factor of 1.0."
                        )
                    }
                )
