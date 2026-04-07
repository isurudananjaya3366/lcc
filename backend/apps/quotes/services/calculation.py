"""
Quote calculation service for computing line totals, subtotals,
discounts, tax, and grand total.

Tasks 30-34, 36: Full calculation pipeline.
"""

from decimal import Decimal

from django.db import transaction
from django.db.models import F, Sum


class QuoteCalculationService:
    """Handles all financial calculations for a quote."""

    def __init__(self, quote):
        self.quote = quote

    def get_line_items(self):
        """Get all line items for this quote, ordered by position."""
        return self.quote.line_items.select_related("product", "variant").order_by(
            "position"
        )

    def _ensure_decimal(self, value):
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
            for line_item in line_items:
                line_item.recalculate()
                line_item.save(
                    update_fields=[
                        "discount_amount",
                        "tax_amount",
                        "line_total",
                        "updated_at",
                    ]
                )
                count += 1
        return count

    def calculate_subtotal(self):
        """Sum all line_total fields into quote.subtotal."""
        result = self.get_line_items().aggregate(subtotal=Sum("line_total"))
        subtotal = result["subtotal"] or Decimal("0.00")
        self.quote.subtotal = subtotal
        return subtotal

    def get_lines_breakdown(self):
        """Return itemized breakdown of all line items."""
        return [
            {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "discount_amount": item.discount_amount,
                "tax_amount": item.tax_amount,
                "line_total": item.line_total,
            }
            for item in self.get_line_items()
        ]

    # ── Tax Calculator (Task 32) ─────────────────────────────────

    def calculate_tax(self):
        """Calculate total tax from all line items."""
        result = self.get_line_items().aggregate(total_tax=Sum("tax_amount"))
        tax_amount = result["total_tax"] or Decimal("0.00")
        self.quote.tax_amount = tax_amount
        return tax_amount

    def get_tax_breakdown(self):
        """Group tax amounts by tax rate."""
        breakdown = {}
        for item in self.get_line_items():
            rate = str(item.tax_rate)
            if rate not in breakdown:
                breakdown[rate] = Decimal("0.00")
            breakdown[rate] += item.tax_amount
        return breakdown

    def get_taxable_amount(self):
        """Calculate total amount subject to tax."""
        taxable_items = self.get_line_items().filter(is_taxable=True)
        result = taxable_items.aggregate(
            taxable=Sum(F("quantity") * F("unit_price") - F("discount_amount"))
        )
        return result["taxable"] or Decimal("0.00")

    # ── Header Discount (Task 33) ────────────────────────────────

    def apply_header_discount(self):
        """Apply quote-level discount to the subtotal."""
        subtotal = self._ensure_decimal(self.quote.subtotal)

        if not self.quote.discount_type:
            self.quote.discount_amount = Decimal("0.00")
            return Decimal("0.00")

        if self.quote.discount_type == "PERCENTAGE":
            discount_value = self._ensure_decimal(self.quote.discount_value)
            if discount_value > 100:
                raise ValueError("Percentage discount cannot exceed 100%.")
            amount = subtotal * (discount_value / Decimal("100"))
        elif self.quote.discount_type == "FIXED":
            amount = self._ensure_decimal(self.quote.discount_value)
            if amount > subtotal:
                raise ValueError("Fixed discount cannot exceed subtotal.")
        else:
            amount = Decimal("0.00")

        self.quote.discount_amount = amount.quantize(Decimal("0.01"))
        return self.quote.discount_amount

    def validate_header_discount(self):
        """Validate the header discount configuration."""
        if not self.quote.discount_type:
            return True
        subtotal = self._ensure_decimal(self.quote.subtotal)
        discount_value = self._ensure_decimal(self.quote.discount_value)
        if self.quote.discount_type == "PERCENTAGE" and discount_value > 100:
            raise ValueError("Percentage discount cannot exceed 100%.")
        if self.quote.discount_type == "FIXED" and discount_value > subtotal:
            raise ValueError("Fixed discount cannot exceed subtotal.")
        return True

    def get_discounted_subtotal(self):
        """Return subtotal after header discount."""
        return self._ensure_decimal(self.quote.subtotal) - self._ensure_decimal(
            self.quote.discount_amount
        )

    def get_discount_percentage_actual(self):
        """Return the actual discount as a percentage of subtotal."""
        subtotal = self._ensure_decimal(self.quote.subtotal)
        if subtotal == 0:
            return Decimal("0.00")
        return (
            self._ensure_decimal(self.quote.discount_amount) / subtotal
        ) * Decimal("100")

    # ── Grand Total (Task 34) ────────────────────────────────────

    def calculate_grand_total(self):
        """Calculate the final grand total."""
        subtotal = self._ensure_decimal(self.quote.subtotal)
        discount = self._ensure_decimal(self.quote.discount_amount)
        tax = self._ensure_decimal(self.quote.tax_amount)

        grand_total = subtotal - discount + tax

        if grand_total < 0:
            raise ValueError("Grand total cannot be negative.")

        self.quote.total = grand_total
        return grand_total

    def get_total_breakdown(self):
        """Return full financial breakdown of the quote."""
        subtotal = self._ensure_decimal(self.quote.subtotal)
        discount = self._ensure_decimal(self.quote.discount_amount)
        tax = self._ensure_decimal(self.quote.tax_amount)
        total = self._ensure_decimal(self.quote.total)

        return {
            "subtotal": subtotal,
            "discount_type": self.quote.discount_type,
            "discount_value": self._ensure_decimal(self.quote.discount_value),
            "discount_amount": discount,
            "after_discount": subtotal - discount,
            "tax_amount": tax,
            "grand_total": total,
            "currency": self.quote.currency or "LKR",
            "formatted_total": self.format_currency(total),
        }

    def get_calculation_summary(self):
        """Return summary dict for display."""
        return {
            "line_items_count": self.get_line_items().count(),
            "subtotal": self._ensure_decimal(self.quote.subtotal),
            "header_discount_amount": self._ensure_decimal(
                self.quote.discount_amount
            ),
            "taxable_amount": self.get_taxable_amount(),
            "tax_amount": self._ensure_decimal(self.quote.tax_amount),
            "grand_total": self._ensure_decimal(self.quote.total),
        }

    @staticmethod
    def format_currency(amount):
        """Format amount as Sri Lankan Rupees."""
        return f"₨ {amount:,.2f}"

    # ── Price Snapshotting (Task 36) ─────────────────────────────

    def snapshot_all_prices(self):
        """Re-snapshot prices from products for all product-based items."""
        line_items = self.get_line_items().filter(product__isnull=False)
        for item in line_items:
            item.snapshot_from_product(item.product, item.variant)
            item.save(
                update_fields=[
                    "unit_price",
                    "original_price",
                    "cost_price",
                    "tax_rate",
                    "is_taxable",
                    "price_snapshot_at",
                    "updated_at",
                ]
            )

    # ── Orchestrator (Task 34) ───────────────────────────────────

    def calculate_all(self, save=True):
        """Run the full calculation pipeline."""
        with transaction.atomic():
            self.calculate_line_totals()
            self.calculate_subtotal()
            self.apply_header_discount()
            self.calculate_tax()
            self.calculate_grand_total()

            if save:
                self.quote.save(
                    update_fields=[
                        "subtotal",
                        "discount_amount",
                        "tax_amount",
                        "total",
                    ]
                )

        return self.quote
