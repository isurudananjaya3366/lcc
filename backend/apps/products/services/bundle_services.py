"""
Bundle stock and pricing services for LankaCommerce Cloud.

Provides two service classes:
- BundleStockService: Calculates bundle availability from component stock
- BundlePricingService: Handles fixed/dynamic pricing and discounts
"""

import math
from decimal import Decimal

from django.db import transaction
from django.utils.translation import gettext_lazy as _


class BundleStockService:
    """
    Service for calculating bundle stock availability.

    Bundle stock is determined by the minimum number of complete bundles
    that can be assembled from available component stock. Only required
    (non-optional) items are considered for stock calculations.

    Formula:
        Available bundles = MIN(floor(item_stock / item_qty) for each required item)
    """

    def __init__(self, bundle):
        """
        Initialize with a ProductBundle instance.

        Args:
            bundle: ProductBundle instance with related items.
        """
        self.bundle = bundle

    def _get_required_items(self):
        """Return required (non-optional) bundle items."""
        return self.bundle.items.filter(
            is_optional=False,
        ).select_related("product", "variant")

    def get_available_stock(self):
        """
        Calculate available bundle stock from component availability.

        Returns:
            int: Number of complete bundles that can be assembled.
                 Returns 0 if no required items or any component has 0 stock.
        """
        required_items = self._get_required_items()
        if not required_items.exists():
            return 0

        min_bundles = None
        for item in required_items:
            # Get component stock - use variant stock if variant specified
            if item.variant_id and hasattr(item.variant, "stock_quantity"):
                component_stock = item.variant.stock_quantity
            elif hasattr(item.product, "stock_quantity"):
                component_stock = item.product.stock_quantity
            else:
                component_stock = 0

            if item.quantity <= 0:
                continue

            possible_bundles = math.floor(component_stock / item.quantity)

            if min_bundles is None:
                min_bundles = possible_bundles
            else:
                min_bundles = min(min_bundles, possible_bundles)

        return min_bundles if min_bundles is not None else 0

    def check_availability(self, quantity=1):
        """
        Check if a given quantity of bundles can be fulfilled.

        Args:
            quantity: Number of bundles requested (default: 1).

        Returns:
            bool: True if enough stock exists for the requested quantity.
        """
        if quantity <= 0:
            return False
        return self.get_available_stock() >= quantity

    def get_limiting_item(self):
        """
        Identify the bottleneck component limiting bundle availability.

        Returns:
            dict or None: Dictionary with 'item', 'stock', and 'possible_bundles'
                         for the limiting component, or None if no required items.
        """
        required_items = self._get_required_items()
        if not required_items.exists():
            return None

        limiting = None
        for item in required_items:
            if item.variant_id and hasattr(item.variant, "stock_quantity"):
                component_stock = item.variant.stock_quantity
            elif hasattr(item.product, "stock_quantity"):
                component_stock = item.product.stock_quantity
            else:
                component_stock = 0

            possible = math.floor(component_stock / item.quantity) if item.quantity > 0 else 0
            entry = {
                "item": item,
                "stock": component_stock,
                "possible_bundles": possible,
            }

            if limiting is None or possible < limiting["possible_bundles"]:
                limiting = entry

        return limiting

    @transaction.atomic
    def reserve_stock(self, quantity=1):
        """
        Reserve component stock for a number of bundles.

        Atomically reserves stock for all required components. If any
        component has insufficient stock, the entire reservation is
        rolled back.

        Args:
            quantity: Number of bundles to reserve (default: 1).

        Returns:
            bool: True if reservation was successful.

        Raises:
            ValueError: If insufficient stock for any component.
        """
        if quantity <= 0:
            raise ValueError(_("Quantity must be a positive integer."))

        if not self.check_availability(quantity):
            raise ValueError(
                _("Insufficient stock to reserve %(qty)d bundle(s).")
                % {"qty": quantity}
            )

        required_items = self._get_required_items().select_for_update()
        for item in required_items:
            needed = item.quantity * quantity
            if item.variant_id and hasattr(item.variant, "stock_quantity"):
                item.variant.stock_quantity -= needed
                item.variant.save(update_fields=["stock_quantity"])
            elif hasattr(item.product, "stock_quantity"):
                item.product.stock_quantity -= needed
                item.product.save(update_fields=["stock_quantity"])

        return True


class BundlePricingService:
    """
    Service for calculating bundle prices and discounts.

    Supports two pricing strategies:
    - Fixed: Bundle sold at a predetermined fixed price
    - Dynamic: Price calculated from sum of component prices minus discount
    """

    def __init__(self, bundle):
        """
        Initialize with a ProductBundle instance.

        Args:
            bundle: ProductBundle instance with related items.
        """
        self.bundle = bundle

    def calculate_fixed_price(self):
        """
        Get the fixed bundle price.

        Returns:
            Decimal: The fixed price, or Decimal('0.00') if not set.
        """
        if self.bundle.fixed_price is not None:
            return Decimal(str(self.bundle.fixed_price))
        return Decimal("0.00")

    def calculate_dynamic_price(self):
        """
        Calculate dynamic price from component prices.

        Sum of (component_selling_price × quantity) for all items,
        then apply any configured discount.

        Returns:
            Decimal: The calculated bundle price after discount.
        """
        total = Decimal("0.00")
        items = self.bundle.items.select_related("product", "variant").all()

        for item in items:
            # Use variant price if available, else product selling price
            if item.variant_id and hasattr(item.variant, "selling_price") and item.variant.selling_price:
                price = Decimal(str(item.variant.selling_price))
            elif hasattr(item.product, "selling_price") and item.product.selling_price:
                price = Decimal(str(item.product.selling_price))
            else:
                price = Decimal("0.00")

            total += price * item.quantity

        return self.apply_discount(total)

    def apply_discount(self, total):
        """
        Apply the bundle's discount to a total price.

        Args:
            total: Decimal total to apply discount to.

        Returns:
            Decimal: The discounted price (never below 0).
        """
        from apps.products.constants import DISCOUNT_TYPE

        discount_value = Decimal(str(self.bundle.discount_value or 0))

        if self.bundle.discount_type == DISCOUNT_TYPE.PERCENTAGE:
            discount_amount = (total * discount_value / Decimal("100")).quantize(
                Decimal("0.01")
            )
        elif self.bundle.discount_type == DISCOUNT_TYPE.FIXED:
            discount_amount = discount_value
        else:
            discount_amount = Decimal("0.00")

        result = total - discount_amount
        return max(result, Decimal("0.00"))

    def get_bundle_price(self):
        """
        Get the effective bundle price based on bundle type.

        Returns:
            Decimal: The bundle price (fixed or dynamic).
        """
        from apps.products.constants import BUNDLE_TYPE

        if self.bundle.bundle_type == BUNDLE_TYPE.FIXED:
            return self.calculate_fixed_price()
        return self.calculate_dynamic_price()

    def get_individual_total(self):
        """
        Calculate total if items were purchased individually (no discount).

        Returns:
            Decimal: Sum of (component_price × quantity) without discount.
        """
        total = Decimal("0.00")
        items = self.bundle.items.select_related("product", "variant").all()

        for item in items:
            if item.variant_id and hasattr(item.variant, "selling_price") and item.variant.selling_price:
                price = Decimal(str(item.variant.selling_price))
            elif hasattr(item.product, "selling_price") and item.product.selling_price:
                price = Decimal(str(item.product.selling_price))
            else:
                price = Decimal("0.00")

            total += price * item.quantity

        return total

    def get_savings(self):
        """
        Calculate how much the customer saves by buying the bundle.

        Returns:
            Decimal: Savings amount (individual_total - bundle_price).
                     Never below 0.
        """
        individual = self.get_individual_total()
        bundle_price = self.get_bundle_price()
        savings = individual - bundle_price
        return max(savings, Decimal("0.00"))
