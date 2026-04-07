"""
Products models package.

Exports all models from the products application for convenient
importing. Models can be imported directly from apps.products.models:

    from apps.products.models import (
        Brand, BundleItem, Category, Product, ProductBundle,
        ProductImage, ProductVariant, TaxClass, UnitOfMeasure,
    )
"""

# Supporting models
from apps.products.models.brand import Brand
from apps.products.models.tax_class import TaxClass
from apps.products.models.unit_of_measure import UnitOfMeasure

# Core models
from apps.products.models.category import Category
from apps.products.models.image import ProductImage
from apps.products.models.product import Product
from apps.products.models.product_variant import (
    ProductOptionConfig,
    ProductVariant,
    ProductVariantOption,
)
from apps.products.models.variant_image import VariantImage

# Bundle models
from apps.products.models.bundle import BundleItem, ProductBundle

# BOM models
from apps.products.models.bom import BillOfMaterials, BOMItem, BOMManager, BOMQuerySet

# Variant option models
from apps.products.models.variant_option import (
    VariantOptionType,
    VariantOptionValue,
)

# Managers
from apps.products.models.managers import (
    BundleManager,
    BundleQuerySet,
    CategoryManager,
    CategoryQuerySet,
    ProductManager,
    ProductQuerySet,
)
from apps.products.models.variant_managers import (
    VariantManager,
    VariantQuerySet,
)

__all__ = [
    "BillOfMaterials",
    "BOMItem",
    "BOMManager",
    "BOMQuerySet",
    "Brand",
    "BundleItem",
    "BundleManager",
    "BundleQuerySet",
    "Category",
    "CategoryManager",
    "CategoryQuerySet",
    "Product",
    "ProductBundle",
    "ProductImage",
    "ProductManager",
    "ProductOptionConfig",
    "ProductQuerySet",
    "ProductVariant",
    "ProductVariantOption",
    "TaxClass",
    "UnitOfMeasure",
    "VariantManager",
    "VariantOptionType",
    "VariantOptionValue",
    "VariantQuerySet",
]
