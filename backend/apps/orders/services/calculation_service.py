"""
Order calculation service for computing line totals, subtotals,
discounts, tax, shipping, and grand total.

Tasks 30-33: Full calculation pipeline following the quotes pattern.
"""

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum


class LineItemCalculator:
    """
    Calculates individual line item totals (Task 31).

    Handles discount application, tax calculation, and line total
    with proper Decimal precision.
    """

    @staticmethod
    def calculate(line_item):
        """
        Recalculate a single line item's financial fields.

        Applies discount → tax → line_total in sequence.
        Mutates line_item in-place; does NOT save.
        """
        line_item.recalculate()

    @staticmethod
    def calculate_discount(unit_price, quantity, discount_type, discount_value):
        """Pure calculation: return discount amount."""
        from apps.orders.constants import DiscountType

        subtotal = quantity * unit_price
        if discount_type == DiscountType.PERCENTAGE and discount_value:
            return (subtotal * discount_value / Decimal("100")).quantize(
                Decimal("0.01")
            )
        elif discount_type == DiscountType.FIXED and discount_value:
            return min(discount_value, subtotal)
        return Decimal("0")

    @staticmethod
    def calculate_tax(amount, tax_rate, is_taxable=True):
        """Pure calculation: return tax amount for a given amount."""
        if not is_taxable or not tax_rate:
            return Decimal("0")
        return (amount * tax_rate / Decimal("100")).quantize(Decimal("0.01"))


class TaxCalculator:
    """
    Tax calculation strategies for orders (Task 32).

    Supports per-line-item tax and order-level tax.
    Includes Sri Lanka-specific rates.
    """

    # Sri Lanka standard rates
    STANDARD_RATE = Decimal("18")
    REDUCED_RATE = Decimal("8")
    ZERO_RATE = Decimal("0")

    RATE_MAP = {
        "STANDARD": STANDARD_RATE,
        "REDUCED": REDUCED_RATE,
        "ZERO": ZERO_RATE,
        "EXEMPT": ZERO_RATE,
    }

    @classmethod
    def get_rate(cls, tax_code):
        """Look up tax rate by code."""
        return cls.RATE_MAP.get(tax_code, cls.STANDARD_RATE)

    @classmethod
    def calculate_line_item_tax(cls, line_items):
        """
        Per-line-item tax strategy: sum each item's tax_amount.
        Returns total tax.
        """
        total_tax = Decimal("0")
        for item in line_items:
            if item.is_taxable and item.tax_rate:
                after_discount = (item.quantity_ordered * item.unit_price) - item.discount_amount
                item.tax_amount = (
                    after_discount * item.tax_rate / Decimal("100")
                ).quantize(Decimal("0.01"))
            else:
                item.tax_amount = Decimal("0")
            total_tax += item.tax_amount
        return total_tax

    @classmethod
    def calculate_order_level_tax(cls, taxable_amount, tax_rate):
        """
        Order-level tax strategy: apply a single rate to the taxable amount.
        """
        if not tax_rate or taxable_amount <= 0:
            return Decimal("0")
        return (taxable_amount * tax_rate / Decimal("100")).quantize(
            Decimal("0.01")
        )

    @classmethod
    def get_tax_breakdown(cls, line_items):
        """Group tax amounts by tax_rate."""
        breakdown = {}
        for item in line_items:
            rate_key = str(item.tax_rate)
            if rate_key not in breakdown:
                breakdown[rate_key] = Decimal("0")
            breakdown[rate_key] += item.tax_amount
        return breakdown


class ShippingCalculator:
    """
    Shipping cost calculator (Task 33).

    Supports multiple calculation methods: flat rate, weight-based,
    value-based, and destination-based (Sri Lanka zones).
    """

    # Sri Lanka zone-based rates
    ZONE_RATES = {
        "colombo": Decimal("200"),
        "western": Decimal("350"),
        "southern": Decimal("500"),
        "central": Decimal("500"),
        "northern": Decimal("700"),
        "eastern": Decimal("700"),
        "north_western": Decimal("550"),
        "north_central": Decimal("600"),
        "uva": Decimal("600"),
        "sabaragamuwa": Decimal("500"),
    }

    @classmethod
    def flat_rate(cls, rate):
        """Fixed shipping cost."""
        return Decimal(str(rate))

    @classmethod
    def weight_based(cls, total_weight, rate_per_kg, minimum=None):
        """Shipping by total weight."""
        cost = Decimal(str(total_weight)) * Decimal(str(rate_per_kg))
        if minimum:
            cost = max(cost, Decimal(str(minimum)))
        return cost.quantize(Decimal("0.01"))

    @classmethod
    def value_based(cls, order_value, thresholds=None):
        """
        Shipping by order value with tiered thresholds.

        thresholds: list of (min_value, shipping_cost) sorted ascending.
        Default: free shipping above 5000 LKR.
        """
        if thresholds is None:
            thresholds = [
                (Decimal("0"), Decimal("350")),
                (Decimal("2500"), Decimal("200")),
                (Decimal("5000"), Decimal("0")),
            ]
        shipping = thresholds[0][1]
        for min_val, cost in thresholds:
            if order_value >= min_val:
                shipping = cost
        return shipping

    @classmethod
    def by_zone(cls, zone):
        """Sri Lanka zone-based shipping."""
        zone_key = zone.lower().replace(" ", "_")
        return cls.ZONE_RATES.get(zone_key, Decimal("500"))

    @classmethod
    def free_shipping_eligible(cls, order_value, threshold=Decimal("5000")):
        """Check if the order qualifies for free shipping."""
        return order_value >= threshold


class OrderCalculationService:
    """
    Orchestrates all financial calculations for an order (Task 30).

    Follows the same pattern as QuoteCalculationService.
    """

    def __init__(self, order):
        self.order = order

    def get_line_items(self):
        """Get all line items for this order, ordered by position."""
        return self.order.line_items.select_related(
            "product", "variant"
        ).order_by("position")

    @staticmethod
    def _ensure_decimal(value):
        """Convert value to Decimal; None becomes Decimal('0.00')."""
        if value is None:
            return Decimal("0.00")
        return Decimal(str(value))

    # ── Line Totals (Task 31) ────────────────────────────────────

    def calculate_line_totals(self):
        """Recalculate all line item totals. Returns count of items."""
        line_items = self.get_line_items()
        if not line_items.exists():
            return 0

        count = 0
        with transaction.atomic():
            for item in line_items:
                LineItemCalculator.calculate(item)
                item.save(
                    update_fields=[
                        "discount_amount",
                        "tax_amount",
                        "line_total",
                        "updated_on",
                    ]
                )
                count += 1
        return count

    def calculate_subtotal(self):
        """Sum all line_total fields into order.subtotal."""
        result = self.get_line_items().aggregate(subtotal=Sum("line_total"))
        subtotal = result["subtotal"] or Decimal("0.00")
        self.order.subtotal = subtotal
        return subtotal

    # ── Tax Calculator (Task 32) ─────────────────────────────────

    def calculate_tax(self):
        """Calculate total tax from all line items."""
        result = self.get_line_items().aggregate(total_tax=Sum("tax_amount"))
        tax_amount = result["total_tax"] or Decimal("0.00")
        self.order.tax_amount = tax_amount
        return tax_amount

    def get_tax_breakdown(self):
        """Group tax amounts by tax rate."""
        return TaxCalculator.get_tax_breakdown(self.get_line_items())

    def get_taxable_amount(self):
        """Calculate total amount subject to tax."""
        from django.db.models import F

        taxable_items = self.get_line_items().filter(is_taxable=True)
        result = taxable_items.aggregate(
            taxable=Sum(
                F("quantity_ordered") * F("unit_price") - F("discount_amount")
            )
        )
        return result["taxable"] or Decimal("0.00")

    # ── Header Discount ──────────────────────────────────────────

    def apply_header_discount(self):
        """Apply order-level discount to the subtotal."""
        subtotal = self._ensure_decimal(self.order.subtotal)

        if not self.order.discount_type:
            self.order.discount_amount = Decimal("0.00")
            return Decimal("0.00")

        from apps.orders.constants import DiscountType

        if self.order.discount_type == DiscountType.PERCENTAGE:
            discount_value = self._ensure_decimal(self.order.discount_value)
            if discount_value > 100:
                raise ValueError("Percentage discount cannot exceed 100%.")
            amount = subtotal * (discount_value / Decimal("100"))
        elif self.order.discount_type == DiscountType.FIXED:
            amount = self._ensure_decimal(self.order.discount_value)
            if amount > subtotal:
                raise ValueError("Fixed discount cannot exceed subtotal.")
        else:
            amount = Decimal("0.00")

        self.order.discount_amount = amount.quantize(Decimal("0.01"))
        return self.order.discount_amount

    # ── Grand Total ──────────────────────────────────────────────

    def calculate_grand_total(self):
        """Calculate the final grand total."""
        subtotal = self._ensure_decimal(self.order.subtotal)
        discount = self._ensure_decimal(self.order.discount_amount)
        tax = self._ensure_decimal(self.order.tax_amount)
        shipping = self._ensure_decimal(self.order.shipping_amount)

        grand_total = subtotal - discount + tax + shipping

        if grand_total < 0:
            raise ValueError("Grand total cannot be negative.")

        self.order.total_amount = grand_total
        self.order.balance_due = grand_total - self._ensure_decimal(
            self.order.amount_paid
        )

        # Multi-currency conversion
        if self.order.exchange_rate and self.order.exchange_rate > 0:
            self.order.base_total = grand_total * self.order.exchange_rate

        return grand_total

    # ── Full Pipeline ────────────────────────────────────────────

    def calculate_all(self, save=False):
        """
        Run the full calculation pipeline.

        1. Recalculate all line item totals
        2. Sum subtotal
        3. Apply header discount
        4. Sum tax
        5. Calculate grand total + balance
        """
        with transaction.atomic():
            self.calculate_line_totals()
            self.calculate_subtotal()
            self.apply_header_discount()
            self.calculate_tax()
            self.calculate_grand_total()

            if save:
                self.order.save(
                    update_fields=[
                        "subtotal",
                        "discount_amount",
                        "tax_amount",
                        "total_amount",
                        "balance_due",
                        "base_total",
                        "updated_on",
                    ]
                )

    # ── Reporting ────────────────────────────────────────────────

    def get_lines_breakdown(self):
        """Return itemized breakdown of all line items."""
        return [
            {
                "item_name": item.item_name or str(item.product or "Item"),
                "item_sku": item.item_sku,
                "quantity": item.quantity_ordered,
                "unit_price": item.unit_price,
                "discount_amount": item.discount_amount,
                "tax_amount": item.tax_amount,
                "line_total": item.line_total,
            }
            for item in self.get_line_items()
        ]

    def get_total_breakdown(self):
        """Return full financial breakdown of the order."""
        return {
            "subtotal": self._ensure_decimal(self.order.subtotal),
            "discount_type": self.order.discount_type,
            "discount_value": self._ensure_decimal(self.order.discount_value),
            "discount_amount": self._ensure_decimal(self.order.discount_amount),
            "tax_amount": self._ensure_decimal(self.order.tax_amount),
            "shipping_amount": self._ensure_decimal(self.order.shipping_amount),
            "grand_total": self._ensure_decimal(self.order.total_amount),
            "amount_paid": self._ensure_decimal(self.order.amount_paid),
            "balance_due": self._ensure_decimal(self.order.balance_due),
            "currency": self.order.currency or "LKR",
            "formatted_total": self.format_currency(
                self._ensure_decimal(self.order.total_amount)
            ),
        }

    def get_calculation_summary(self):
        """Return summary dict for display."""
        return {
            "line_items_count": self.get_line_items().count(),
            "subtotal": self._ensure_decimal(self.order.subtotal),
            "header_discount_amount": self._ensure_decimal(
                self.order.discount_amount
            ),
            "taxable_amount": self.get_taxable_amount(),
            "tax_amount": self._ensure_decimal(self.order.tax_amount),
            "shipping_amount": self._ensure_decimal(self.order.shipping_amount),
            "grand_total": self._ensure_decimal(self.order.total_amount),
        }

    @staticmethod
    def format_currency(amount):
        """Format amount as Sri Lankan Rupees."""
        return f"₨ {amount:,.2f}"
