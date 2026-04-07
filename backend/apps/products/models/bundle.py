"""
Bundle product models for LankaCommerce Cloud.

Provides two models:
- ProductBundle: Bundle container linking to a Product of type BUNDLE
- BundleItem: Individual component items within a bundle

Bundle products are collections of existing products sold together,
with either fixed or dynamic pricing strategies.

Examples:
    Gift Hamper = Chocolate + Wine + Card
    Office Starter Kit = Laptop + Mouse + Keyboard + Bag
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.products.constants import BUNDLE_TYPE, DISCOUNT_TYPE
from apps.products.models.managers import BundleManager


__all__ = [
    "ProductBundle",
    "BundleItem",
]


class ProductBundle(BaseModel):
    """
    Bundle configuration for a product of type BUNDLE.

    Links to a base Product model and defines the pricing strategy
    (fixed or dynamic) plus optional discounts. Each ProductBundle
    contains BundleItems representing the component products.

    Pricing Strategies:
    - FIXED: Bundle sold at a specified fixed_price
    - DYNAMIC: Price calculated as sum of component prices minus discount

    Discount Types:
    - PERCENTAGE: Discount as a percentage of component total
    - FIXED: Flat discount amount
    - NONE: No discount applied
    """

    product = models.OneToOneField(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="bundle",
        verbose_name=_("Product"),
        help_text=_("The base product this bundle configuration belongs to"),
        db_index=True,
    )

    bundle_type = models.CharField(
        max_length=20,
        choices=BUNDLE_TYPE.choices,
        default=BUNDLE_TYPE.DYNAMIC,
        verbose_name=_("Bundle Type"),
        help_text=_("Pricing strategy: fixed price or dynamic from components"),
        db_index=True,
    )

    fixed_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)],
        verbose_name=_("Fixed Price"),
        help_text=_("Fixed bundle price (used when bundle_type is 'fixed')"),
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE.choices,
        default=DISCOUNT_TYPE.NONE,
        verbose_name=_("Discount Type"),
        help_text=_("Type of discount applied to dynamic pricing"),
        db_index=True,
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        verbose_name=_("Discount Value"),
        help_text=_("Discount amount (percentage or fixed based on discount_type)"),
    )

    objects = BundleManager()
    all_with_deleted = models.Manager()

    class Meta(BaseModel.Meta):
        db_table = "products_bundle"
        verbose_name = _("Product Bundle")
        verbose_name_plural = _("Product Bundles")
        ordering = ["-created_on"]

    def __str__(self):
        return f"Bundle: {self.product.name}" if hasattr(self, "product") and self.product_id else f"Bundle(pk={self.pk})"

    def __repr__(self):
        return (
            f"<ProductBundle(pk={self.pk}, "
            f"bundle_type='{self.bundle_type}', "
            f"is_active={self.is_active})>"
        )


class BundleItem(BaseModel):
    """
    Individual component item within a product bundle.

    Represents a product (and optionally a specific variant) that is
    part of a bundle, along with its quantity and display order.

    Items can be marked as optional, allowing customizable bundles
    where customers can choose to include or exclude certain items.
    """

    bundle = models.ForeignKey(
        "products.ProductBundle",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Bundle"),
        help_text=_("The bundle this item belongs to"),
        db_index=True,
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="bundle_items",
        verbose_name=_("Product"),
        help_text=_("The component product in this bundle"),
        db_index=True,
    )

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bundle_items",
        verbose_name=_("Variant"),
        help_text=_("Specific variant of the product (optional)"),
        db_index=True,
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_("Quantity"),
        help_text=_("Number of this product included in the bundle"),
    )

    is_optional = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Optional"),
        help_text=_("Whether this item is optional in the bundle"),
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name=_("Sort Order"),
        help_text=_("Display order within the bundle"),
    )

    class Meta(BaseModel.Meta):
        db_table = "products_bundle_item"
        verbose_name = _("Bundle Item")
        verbose_name_plural = _("Bundle Items")
        ordering = ["sort_order", "product__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["bundle", "product", "variant"],
                name="unique_bundle_product_variant",
            ),
        ]
        indexes = [
            models.Index(
                fields=["bundle", "is_optional"],
                name="idx_bundleitem_bundle_optional",
            ),
        ]

    def __str__(self):
        name = self.product.name if hasattr(self, "product") and self.product_id else "?"
        variant_str = f" ({self.variant})" if self.variant_id else ""
        return f"{name}{variant_str} x{self.quantity}"

    def __repr__(self):
        return (
            f"<BundleItem(pk={self.pk}, "
            f"bundle_id={self.bundle_id}, "
            f"product_id={self.product_id}, "
            f"qty={self.quantity})>"
        )
