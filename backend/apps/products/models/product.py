"""
Product model for LankaCommerce Cloud.

The Product model is the core of the inventory and catalog system.
It supports multiple product types and integrates with all aspects
of the ERP system.

Product Types:
- SIMPLE: Single product without variations
- VARIABLE: Parent product with variants (size, color, etc.)
- BUNDLE: Collection of products sold together
- COMPOSITE: Product with bill of materials (BOM)

Key Features:
- Multi-tenant isolation
- SKU and barcode management
- Category and brand classification
- Tax class integration
- Visibility controls (webstore, POS)
- SEO optimization fields
- Physical dimensions and weight

Relationships:
- Category: FK to Category (hierarchical, MPTT)
- Brand: FK to Brand (optional)
- TaxClass: FK to TaxClass (optional)
- UnitOfMeasure: FK to UnitOfMeasure (optional)
- Variants: One-to-many (in SubPhase-04)
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.products.constants import PRODUCT_STATUS, PRODUCT_TYPES
from apps.products.models.managers import ProductManager


# ════════════════════════════════════════════════════════════════════════
# Pricing Constants
# ════════════════════════════════════════════════════════════════════════

# LKR currency: max 10 digits, 2 decimal places
PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2


class Product(BaseModel):
    """
    Core product model for LankaCommerce Cloud.

    Represents all types of products in the catalog including simple products,
    variable products (with variants), bundles, and composite products.

    Product Types:
    - SIMPLE: Standard single product (e.g., Book, Pen)
    - VARIABLE: Has variants with different attributes (e.g., T-Shirt with sizes)
    - BUNDLE: Collection of products (e.g., Gift Set)
    - COMPOSITE: Built from components/BOM (e.g., Custom Cake)

    Product Status:
    - DRAFT: Not visible, being configured
    - ACTIVE: Published and available
    - ARCHIVED: Temporarily hidden
    - DISCONTINUED: Permanently unavailable

    Tenant Isolation: All products are tenant-specific

    Relationships:
    - category: FK to Category (required, PROTECT)
    - brand: FK to Brand (optional, SET_NULL)
    - tax_class: FK to TaxClass (optional, SET_NULL)
    - unit_of_measure: FK to UnitOfMeasure (optional, SET_NULL)

    Inherited from BaseModel:
    - id: UUID v4 primary key
    - created_on, updated_on: Timestamps
    - created_by, updated_by: Audit fields
    - is_active, deactivated_on: Status
    - is_deleted, deleted_on: Soft delete
    """

    # ============================================
    # IDENTITY FIELDS
    # ============================================

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name=_("Product Name"),
        help_text=_("Full product name as displayed to customers"),
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        unique=True,
        verbose_name=_("URL Slug"),
        help_text=_(
            "SEO-friendly URL identifier (auto-generated from name if left blank). "
            "Example: apple-iphone-15-pro"
        ),
    )
    sku = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name=_("SKU"),
        help_text=_(
            "Stock Keeping Unit — unique product identifier "
            "(auto-generated if left blank). Example: PRD-A1B2C"
        ),
    )
    barcode = models.CharField(
        max_length=50,
        blank=True,
        default="",
        db_index=True,
        verbose_name=_("Barcode"),
        help_text=_(
            "Product barcode for scanning (EAN-13, UPC-A, or Code-128). "
            "Leave blank if product has no barcode."
        ),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
        help_text=_(
            "Full product description with features and specifications. "
            "Supports HTML formatting for rich content display."
        ),
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name=_("Short Description"),
        help_text=_(
            "Brief product summary for listings and search results "
            "(max 500 characters). Plain text only, no HTML."
        ),
    )

    # ============================================
    # CLASSIFICATION FIELDS
    # ============================================

    category = models.ForeignKey(
        "products.Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Category"),
        help_text=_("Product category for organization and filtering"),
    )
    brand = models.ForeignKey(
        "products.Brand",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Brand"),
        help_text=_("Product brand or manufacturer (optional)"),
    )
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES.choices,
        default=PRODUCT_TYPES.SIMPLE,
        verbose_name=_("Product Type"),
        help_text=_(
            "Type determines product behavior: "
            "Simple (single item), Variable (with variants), "
            "Bundle (collection), Composite (BOM)"
        ),
    )
    status = models.CharField(
        max_length=20,
        choices=PRODUCT_STATUS.choices,
        default=PRODUCT_STATUS.DRAFT,
        db_index=True,
        verbose_name=_("Status"),
        help_text=_(
            "Product status: Draft (not visible), Active (published), "
            "Archived (hidden), Discontinued (unavailable)"
        ),
    )

    # ============================================
    # VISIBILITY FIELDS
    # ============================================

    is_webstore_visible = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Webstore Visible"),
        help_text=_(
            "Show product in webstore. Product must also be Active. "
            "Use this to hide products from webstore while keeping in POS."
        ),
    )
    is_pos_visible = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("POS Visible"),
        help_text=_(
            "Show product in POS system. Product must also be Active. "
            "Use this to hide online-only products from POS."
        ),
    )
    featured = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Featured Product"),
        help_text=_("Mark as featured for display on homepage and promotions"),
    )

    # ============================================
    # MANAGER
    # ============================================

    objects = ProductManager()

    # ============================================
    # TAX & MEASUREMENT
    # ============================================

    tax_class = models.ForeignKey(
        "products.TaxClass",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Tax Class"),
        help_text=_(
            "Tax rate applied to this product (e.g., Standard VAT 15%). "
            "Used for price calculations and tax reporting."
        ),
    )
    unit_of_measure = models.ForeignKey(
        "products.UnitOfMeasure",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Unit of Measure"),
        help_text=_(
            "How product quantity is measured (e.g., Piece, Kilogram, Liter). "
            "Used in inventory tracking and display."
        ),
    )

    # ============================================
    # PRICING FIELDS (LKR)
    # ============================================

    cost_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Cost Price (₨)"),
        help_text=_("Purchase cost from supplier in LKR."),
    )
    selling_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Selling Price (₨)"),
        help_text=_("Standard selling price in LKR."),
    )
    mrp = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("MRP (₨)"),
        help_text=_("Maximum Retail Price in LKR. Common in Sri Lankan retail."),
    )
    wholesale_price = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Wholesale Price (₨)"),
        help_text=_("Bulk/wholesale purchase price in LKR."),
    )

    # ============================================
    # PHYSICAL ATTRIBUTES
    # ============================================

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Weight (kg)"),
        help_text=_("Product weight in kilograms (e.g., 1.500 for 1.5kg)"),
    )
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Length (cm)"),
        help_text=_("Product length in centimeters"),
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Width (cm)"),
        help_text=_("Product width in centimeters"),
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Height (cm)"),
        help_text=_("Product height in centimeters"),
    )

    # ============================================
    # SEO FIELDS
    # ============================================

    seo_title = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("SEO Title"),
        help_text=_(
            "Page title for search engines (50-60 chars optimal). "
            "Defaults to product name if blank."
        ),
    )
    seo_description = models.CharField(
        max_length=300,
        blank=True,
        default="",
        verbose_name=_("SEO Description"),
        help_text=_(
            "Meta description for search engines (150-160 chars optimal). "
            "Defaults to short description if blank."
        ),
    )

    # ============================================
    # META & METHODS
    # ============================================

    class Meta(BaseModel.Meta):
        db_table = "products_product"
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["-created_on", "name"]
        indexes = [
            models.Index(
                fields=["status", "created_on"],
                name="product_status_created",
            ),
            models.Index(
                fields=["category", "status"],
                name="product_category_status",
            ),
            models.Index(
                fields=["sku"],
                name="product_sku",
            ),
            models.Index(
                fields=["barcode"],
                name="product_barcode_idx",
            ),
            models.Index(
                fields=["product_type"],
                name="product_type_idx",
            ),
            models.Index(
                fields=["status", "is_webstore_visible"],
                name="product_published_idx",
            ),
            models.Index(
                fields=["featured"],
                name="product_featured_idx",
            ),
        ]

    def __str__(self):
        """Return product name with SKU if available."""
        if self.sku:
            return f"{self.name} ({self.sku})"
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name and SKU from UUID if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            short_id = str(self.id).replace("-", "")[:5].upper()
            self.sku = f"PRD-{short_id}"
        super().save(*args, **kwargs)

    @property
    def profit_margin(self):
        """
        Calculate profit margin percentage.

        Returns the profit margin as a percentage based on cost_price
        and selling_price. Returns 0 if cost_price is zero or not set.
        """
        if self.selling_price and self.cost_price and self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0
