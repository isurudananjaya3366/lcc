"""
Products services package.

Exports the variant generation service for convenient importing::

    from apps.products.services import VariantGenerator
"""

from apps.products.services.bundle_services import (
    BundlePricingService,
    BundleStockService,
)
from apps.products.services.manufacturing_services import (
    CostCalculationService,
    ManufacturingStockService,
)
from apps.products.services.variant_generator import VariantGenerator

__all__ = [
    "BundlePricingService",
    "BundleStockService",
    "CostCalculationService",
    "ManufacturingStockService",
    "VariantGenerator",
]
