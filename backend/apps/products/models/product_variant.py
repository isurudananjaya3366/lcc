"""
Product variant models for variable products.

Provides three models:
- ProductVariant: Specific variant of a variable product (e.g., T-Shirt Medium/Red)
- ProductVariantOption: Through model linking variants to option values
- ProductOptionConfig: Defines which option types apply to a product
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.products.constants import PRODUCT_TYPES
from apps.products.models.variant_managers import VariantManager


class ProductVariant(BaseModel):
    """
    Represents a specific variant of a variable product.

    Each variant is a unique combination of option values (e.g., Size: M +
    Color: Red). Variants have their own SKU, optional barcode, and can
    override the parent product's weight and dimensions for accurate
    shipping calculations.

    Examples:
        - Classic T-Shirt — Medium / Red  (SKU: TSHIRT-M-RED)
        - Dell XPS 15 — 16 GB / 512 GB SSD  (SKU: XPS15-16-512)
        - Basmati Rice — 5 kg  (SKU: RICE-BAS-5KG)
    """

    # ── Parent Relationship ─────────────────────────────────────────

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name=_("Product"),
        help_text=_("The parent product this variant belongs to"),
    )

    # ── Identification ──────────────────────────────────────────────

    sku = models.CharField(
        max_length=100,
        verbose_name=_("SKU"),
        help_text=_("Unique Stock Keeping Unit for this variant"),
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Barcode"),
        help_text=_("Barcode for this variant (EAN-13, UPC, etc.)"),
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Variant Name"),
        help_text=_(
            "Display name for this variant "
            "(auto-generated from options if blank)"
        ),
    )

    # ── Option Values (ManyToMany through ProductVariantOption) ─────

    option_values = models.ManyToManyField(
        "products.VariantOptionValue",
        through="products.ProductVariantOption",
        related_name="product_variants",
        blank=True,
        verbose_name=_("Option Values"),
        help_text=_("Option values that define this variant"),
    )

    # ── Weight & Dimension Overrides ────────────────────────────────

    weight_override = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name=_("Weight Override"),
        help_text=_(
            "Override product weight for this variant (kg). "
            "Leave empty to use product weight"
        ),
    )
    length_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Length Override"),
        help_text=_(
            "Override product length for this variant (cm)"
        ),
    )
    width_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Width Override"),
        help_text=_(
            "Override product width for this variant (cm)"
        ),
    )
    height_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Height Override"),
        help_text=_(
            "Override product height for this variant (cm)"
        ),
    )

    # ── Display ─────────────────────────────────────────────────────

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sort Order"),
        help_text=_(
            "Order in which this variant appears "
            "(lower numbers first)"
        ),
    )

    # ── Manager ─────────────────────────────────────────────────────

    objects = VariantManager()

    class Meta(BaseModel.Meta):
        db_table = "products_productvariant"
        verbose_name = _("Product Variant")
        verbose_name_plural = _("Product Variants")
        ordering = ["product", "sort_order", "name"]
        indexes = [
            models.Index(
                fields=["product", "is_active"],
                name="prodvar_product_active_idx",
            ),
            models.Index(
                fields=["sku"],
                name="prodvar_sku_idx",
            ),
            models.Index(
                fields=["product", "sort_order"],
                name="prodvar_product_sort_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["sku"],
                name="unique_productvariant_sku",
            ),
        ]

    def __str__(self):
        """Return 'ProductName - VariantName' or fallback to SKU."""
        if self.name:
            return f"{self.product.name} - {self.name}"
        return f"{self.product.name} ({self.sku})"

    def clean(self):
        """Validate that the parent product is of type VARIABLE."""
        super().clean()
        if (
            hasattr(self, "product")
            and self.product_id
            and self.product.product_type != PRODUCT_TYPES.VARIABLE
        ):
            raise ValidationError(
                {
                    "product": _(
                        "Variants can only be created for "
                        "products with type 'Variable'."
                    )
                }
            )

    def save(self, *args, **kwargs):
        """Auto-generate name from option values if blank."""
        # Name generation happens after M2M save, so only generate
        # if not explicitly set and the instance already has a PK
        # (M2M through table requires PK to exist)
        super().save(*args, **kwargs)

    def generate_name_from_options(self):
        """
        Generate and save name from option values.

        Called after option_values M2M is populated. Joins option
        value labels ordered by option_type.display_order with ' / '.
        """
        option_vals = (
            self.option_values.select_related("option_type")
            .order_by("option_type__display_order", "display_order")
        )
        labels = [ov.label or ov.value for ov in option_vals]
        if labels:
            self.name = " / ".join(labels)
            self.save(update_fields=["name"])

    # ── Property Methods ────────────────────────────────────────────

    @property
    def get_full_name(self):
        """Full display name including the parent product name."""
        if self.name:
            return f"{self.product.name} - {self.name}"
        return f"{self.product.name} ({self.sku})"

    def get_weight(self):
        """Return weight_override if set, else product weight."""
        if self.weight_override is not None:
            return self.weight_override
        return self.product.weight

    def get_dimensions(self):
        """
        Return variant dimensions, using overrides if set.

        Returns:
            dict: Keys 'length', 'width', 'height' using override
            values when available, falling back to parent product.
        """
        return {
            "length": (
                self.length_override
                if self.length_override is not None
                else self.product.length
            ),
            "width": (
                self.width_override
                if self.width_override is not None
                else self.product.width
            ),
            "height": (
                self.height_override
                if self.height_override is not None
                else self.product.height
            ),
        }

    def get_option_display(self):
        """
        Return a dictionary of option types to their values.

        Returns:
            dict: e.g., {'Size': 'Medium', 'Color': 'Red'}
        """
        result = {}
        options = (
            self.variant_options.select_related(
                "option_value", "option_value__option_type"
            )
            .order_by("display_order")
        )
        for vo in options:
            type_name = vo.option_value.option_type.name
            result[type_name] = vo.option_value.label or vo.option_value.value
        return result


class ProductVariantOption(models.Model):
    """
    Through model linking ProductVariant to VariantOptionValue.

    Maintains the display ordering of options within a variant and
    ensures each option value appears only once per variant.
    """

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="variant_options",
        verbose_name=_("Variant"),
    )
    option_value = models.ForeignKey(
        "products.VariantOptionValue",
        on_delete=models.PROTECT,
        related_name="variant_options",
        verbose_name=_("Option Value"),
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("Controls option display order within the variant"),
    )

    class Meta:
        db_table = "products_productvariantoption"
        verbose_name = _("Variant Option")
        verbose_name_plural = _("Variant Options")
        ordering = ["display_order"]
        unique_together = [["variant", "option_value"]]

    def __str__(self):
        return f"{self.variant} - {self.option_value}"


class ProductOptionConfig(BaseModel):
    """
    Links a product to applicable option types for variant generation.

    Defines which option types (e.g., Size, Color) apply to a
    specific product. Controls the order in which option selectors
    appear in the UI and guides the variant generation process.

    Examples:
        - Classic T-Shirt → Size (order: 0), Color (order: 10)
        - Dell XPS 15 → RAM (order: 0), Storage (order: 10)
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="option_configs",
        verbose_name=_("Product"),
        help_text=_("Product this option configuration applies to"),
    )
    option_type = models.ForeignKey(
        "products.VariantOptionType",
        on_delete=models.CASCADE,
        related_name="product_configs",
        verbose_name=_("Option Type"),
        help_text=_("Option type applicable to this product"),
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_(
            "Order in which this option type appears in the UI "
            "(lower numbers first)"
        ),
    )

    class Meta(BaseModel.Meta):
        db_table = "products_productoptionconfig"
        verbose_name = _("Product Option Configuration")
        verbose_name_plural = _("Product Option Configurations")
        ordering = ["product", "display_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "option_type"],
                name="unique_product_option_config",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.option_type.name}"

    def clean(self):
        """Validate that the product is of type VARIABLE."""
        super().clean()
        if (
            hasattr(self, "product")
            and self.product_id
            and self.product.product_type != PRODUCT_TYPES.VARIABLE
        ):
            raise ValidationError(
                {
                    "product": _(
                        "Option configurations can only be added to "
                        "products with type 'Variable'."
                    )
                }
            )
