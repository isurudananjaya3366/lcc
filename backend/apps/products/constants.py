"""
Constants for the products app.

This module defines:
- PRODUCT_TYPES: Types of products (simple, variable, bundle, composite)
- PRODUCT_STATUS: Product lifecycle states (draft, active, archived, discontinued)
- TAX_TYPE_CHOICES: Sri Lankan tax classification
- VARIANT_ATTRIBUTE_CHOICES: Variant attribute types

These constants are used throughout the products app for:
- Model field choices
- Serializer validation
- View filtering
- Admin display
"""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


# ════════════════════════════════════════════════════════════════════════
# Product Type Choices
# ════════════════════════════════════════════════════════════════════════


class PRODUCT_TYPES(TextChoices):
    """
    Product type choices defining product behavior.

    - SIMPLE: Standard single product
    - VARIABLE: Product with variants (size, color, etc.)
    - BUNDLE: Collection of products
    - COMPOSITE: Product with bill of materials (BOM)
    """

    SIMPLE = "simple", _("Simple Product")
    VARIABLE = "variable", _("Variable Product")
    BUNDLE = "bundle", _("Bundle")
    COMPOSITE = "composite", _("Composite Product")


# ════════════════════════════════════════════════════════════════════════
# Product Status Choices
# ════════════════════════════════════════════════════════════════════════


class PRODUCT_STATUS(TextChoices):
    """
    Product status choices defining product lifecycle.

    Status workflow:
    - DRAFT: New product, not published (not visible)
    - ACTIVE: Published and available for sale
    - ARCHIVED: Hidden but can be restored
    - DISCONTINUED: Permanently unavailable

    Status determines:
    - Visibility in webstore and POS
    - Availability for purchase
    - Search and filter inclusion
    """

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    ARCHIVED = "archived", _("Archived")
    DISCONTINUED = "discontinued", _("Discontinued")


# Backward-compatible aliases for existing code
PRODUCT_STATUS_DRAFT = PRODUCT_STATUS.DRAFT
PRODUCT_STATUS_ACTIVE = PRODUCT_STATUS.ACTIVE
PRODUCT_STATUS_INACTIVE = PRODUCT_STATUS.ARCHIVED  # mapped: inactive → archived
PRODUCT_STATUS_DISCONTINUED = PRODUCT_STATUS.DISCONTINUED
PRODUCT_STATUS_CHOICES = PRODUCT_STATUS.choices


# ════════════════════════════════════════════════════════════════════════
# Bundle Type Choices
# ════════════════════════════════════════════════════════════════════════


class BUNDLE_TYPE(TextChoices):
    """
    Bundle pricing type choices.

    - FIXED: Bundle sold at a fixed price
    - DYNAMIC: Bundle price calculated from component prices
    """

    FIXED = "fixed", _("Fixed Price")
    DYNAMIC = "dynamic", _("Dynamic Price")


# ════════════════════════════════════════════════════════════════════════
# Discount Type Choices
# ════════════════════════════════════════════════════════════════════════


class DISCOUNT_TYPE(TextChoices):
    """
    Discount type choices for bundles.

    - PERCENTAGE: Discount as a percentage of total
    - FIXED: Fixed amount discount
    - NONE: No discount applied
    """

    PERCENTAGE = "percentage", _("Percentage")
    FIXED = "fixed", _("Fixed Amount")
    NONE = "none", _("No Discount")


# ════════════════════════════════════════════════════════════════════════
# Tax Type Choices (Sri Lankan VAT)
# ════════════════════════════════════════════════════════════════════════

TAX_TYPE_NONE = "none"
TAX_TYPE_STANDARD = "standard"
TAX_TYPE_REDUCED = "reduced"
TAX_TYPE_EXEMPT = "exempt"
TAX_TYPE_ZERO_RATED = "zero_rated"

TAX_TYPE_CHOICES = [
    (TAX_TYPE_NONE, _("No Tax")),
    (TAX_TYPE_STANDARD, _("Standard Rate")),
    (TAX_TYPE_REDUCED, _("Reduced Rate")),
    (TAX_TYPE_EXEMPT, _("Tax Exempt")),
    (TAX_TYPE_ZERO_RATED, _("Zero Rated")),
]

# Sri Lankan standard VAT rate
SRI_LANKA_VAT_RATE = 18  # percentage

# ════════════════════════════════════════════════════════════════════════
# Variant Attribute Type Choices
# ════════════════════════════════════════════════════════════════════════

VARIANT_ATTR_SIZE = "size"
VARIANT_ATTR_COLOR = "color"
VARIANT_ATTR_MATERIAL = "material"
VARIANT_ATTR_WEIGHT = "weight"
VARIANT_ATTR_CUSTOM = "custom"

VARIANT_ATTRIBUTE_CHOICES = [
    (VARIANT_ATTR_SIZE, _("Size")),
    (VARIANT_ATTR_COLOR, _("Color")),
    (VARIANT_ATTR_MATERIAL, _("Material")),
    (VARIANT_ATTR_WEIGHT, _("Weight")),
    (VARIANT_ATTR_CUSTOM, _("Custom")),
]
