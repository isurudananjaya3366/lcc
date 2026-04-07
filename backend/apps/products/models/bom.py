"""
Bill of Materials (BOM) models for LankaCommerce Cloud.

Provides two models:
- BillOfMaterials: Manufacturing recipe with versioning for composite products
- BOMItem: Individual raw material component in a BOM

Composite products are manufactured from raw materials using a Bill of
Materials (BOM). Each BOM defines a recipe with materials, quantities,
wastage allowances, and yield quantities.

Examples:
    Custom Birthday Cake = Flour (500g) + Sugar (200g) + Eggs (4 pcs) + Butter (100g)
    Wooden Table = Timber (10 boards) + Screws (24 pcs) + Varnish (0.5 liters)
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


__all__ = [
    "BillOfMaterials",
    "BOMItem",
]


class BOMQuerySet(models.QuerySet):
    """Custom QuerySet for BillOfMaterials."""

    def active(self):
        """Return only active BOMs."""
        return self.filter(is_active=True, is_deleted=False)

    def for_product(self, product):
        """Return BOMs for a specific product."""
        return self.filter(product=product)

    def active_for_product(self, product):
        """Return the active BOM for a specific product."""
        return self.active().filter(product=product)

    def with_items(self):
        """Prefetch BOM items with related products."""
        return self.prefetch_related(
            "items",
            "items__raw_material",
            "items__substitute",
            "items__unit",
        ).select_related("product")


class BOMManager(models.Manager):
    """Custom manager for BillOfMaterials."""

    def get_queryset(self):
        return BOMQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def for_product(self, product):
        return self.get_queryset().for_product(product)

    def active_for_product(self, product):
        return self.get_queryset().active_for_product(product)

    def with_items(self):
        return self.get_queryset().with_items()


class BillOfMaterials(BaseModel):
    """
    Bill of Materials for a composite/manufactured product.

    Defines a manufacturing recipe with versioning support. Each BOM
    contains BOMItems representing the raw materials and their quantities
    needed to produce the composite product.

    A product can have multiple BOM versions, but only one should be
    active at a time for production use.
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="boms",
        verbose_name=_("Product"),
        help_text=_("The composite product this BOM belongs to"),
        db_index=True,
    )

    version = models.CharField(
        max_length=20,
        default="1.0",
        verbose_name=_("Version"),
        help_text=_("BOM version identifier (e.g., 1.0, 2.1, v3)"),
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Active"),
        help_text=_("Whether this BOM version is currently in use"),
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes"),
        help_text=_("Manufacturing instructions and notes"),
    )

    yield_quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_("Yield Quantity"),
        help_text=_("Number of units produced per batch"),
    )

    objects = BOMManager()
    all_with_deleted = models.Manager()

    class Meta(BaseModel.Meta):
        db_table = "products_bom"
        verbose_name = _("Bill of Materials")
        verbose_name_plural = _("Bills of Materials")
        ordering = ["-created_on"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "version"],
                name="unique_product_bom_version",
            ),
        ]

    def __str__(self):
        name = self.product.name if hasattr(self, "product") and self.product_id else "?"
        return f"{name} BOM v{self.version}"

    def __repr__(self):
        name = self.product.name if hasattr(self, "product") and self.product_id else "?"
        status = "active" if self.is_active else "inactive"
        return f"<BOM: {name} v{self.version} [{status}]>"


class BOMItem(BaseModel):
    """
    Individual raw material component in a Bill of Materials.

    Represents a single ingredient/material needed to manufacture
    a composite product, including quantity, unit of measure,
    wastage allowance, and optional substitute material.
    """

    bom = models.ForeignKey(
        "products.BillOfMaterials",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("BOM"),
        help_text=_("The Bill of Materials this item belongs to"),
        db_index=True,
    )

    raw_material = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="bom_usages",
        verbose_name=_("Raw Material"),
        help_text=_("The raw material product used in manufacturing"),
        db_index=True,
    )

    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        verbose_name=_("Quantity"),
        help_text=_("Required quantity of this material per batch"),
    )

    unit = models.ForeignKey(
        "products.UnitOfMeasure",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bom_items",
        verbose_name=_("Unit of Measure"),
        help_text=_("Unit of measure for this material"),
    )

    wastage_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Wastage %"),
        help_text=_("Percentage of material lost during manufacturing (0-100)"),
    )

    is_critical = models.BooleanField(
        default=False,
        verbose_name=_("Critical Component"),
        help_text=_("Whether this is an essential component with no substitutes"),
    )

    substitute = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="substituted_for",
        verbose_name=_("Substitute Material"),
        help_text=_("Alternative material when primary is unavailable"),
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sort Order"),
        help_text=_("Display order within the BOM"),
    )

    class Meta(BaseModel.Meta):
        db_table = "products_bom_item"
        verbose_name = _("BOM Item")
        verbose_name_plural = _("BOM Items")
        ordering = ["sort_order", "raw_material__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["bom", "raw_material"],
                name="unique_bom_raw_material",
            ),
        ]

    def __str__(self):
        name = self.raw_material.name if hasattr(self, "raw_material") and self.raw_material_id else "?"
        unit_str = f" {self.unit.symbol}" if self.unit_id else ""
        return f"{name} ({self.quantity}{unit_str})"

    def __repr__(self):
        raw_name = self.raw_material.name if hasattr(self, "raw_material") and self.raw_material_id else "?"
        bom_name = self.bom.product.name if hasattr(self, "bom") and self.bom_id else "?"
        return f"<BOMItem: {raw_name} for {bom_name}>"

    def get_effective_quantity(self):
        """
        Calculate actual material needed including wastage.

        Returns:
            Decimal: quantity * (1 + wastage_percent / 100)
        """
        from decimal import Decimal

        wastage_multiplier = Decimal("1") + (self.wastage_percent / Decimal("100"))
        return self.quantity * wastage_multiplier
