"""
PO Calculation Service.

Handles all purchase order financial calculations including
line totals, tax aggregation, and grand totals.
"""

from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum


class POCalculationService:
    """Centralized calculation logic for purchase orders."""

    TWO = Decimal("0.01")

    @staticmethod
    def calculate_line_total(unit_price, quantity, discount_pct=None,
                             discount_amt=None, tax_rate=None):
        """Calculate a single line item total."""
        two = Decimal("0.01")
        unit_price = Decimal(str(unit_price))
        quantity = int(quantity)
        discount_pct = Decimal(str(discount_pct or 0))
        discount_amt = Decimal(str(discount_amt or 0))
        tax_rate = Decimal(str(tax_rate or 0))

        base = unit_price * quantity

        if discount_pct > 0:
            discount = base * (discount_pct / Decimal("100"))
        else:
            discount = discount_amt * quantity

        subtotal = base - discount
        tax = (subtotal * (tax_rate / Decimal("100"))).quantize(
            two, rounding=ROUND_HALF_UP
        )
        total = (subtotal + tax).quantize(two, rounding=ROUND_HALF_UP)
        return total, tax

    @staticmethod
    def calculate_line_tax(subtotal, tax_rate):
        """Calculate tax amount for a line item."""
        two = Decimal("0.01")
        tax_rate = Decimal(str(tax_rate or 0))
        subtotal = Decimal(str(subtotal))
        tax = (subtotal * (tax_rate / Decimal("100"))).quantize(
            two, rounding=ROUND_HALF_UP
        )
        return tax

    @staticmethod
    def calculate_po_subtotal(purchase_order):
        """Sum all line_total values for a PO."""
        result = purchase_order.line_items.aggregate(
            subtotal=Sum("line_total")
        )
        return result["subtotal"] or Decimal("0.00")

    @staticmethod
    def calculate_po_tax(purchase_order):
        """Sum all tax_amount values for a PO."""
        result = purchase_order.line_items.aggregate(
            total_tax=Sum("tax_amount")
        )
        return result["total_tax"] or Decimal("0.00")

    @staticmethod
    def get_tax_breakdown(purchase_order):
        """Return tax breakdown grouped by rate."""
        from django.db.models import Count, F, DecimalField
        lines = purchase_order.line_items.values("tax_rate").annotate(
            total_tax=Sum("tax_amount"),
            taxable_amount=Sum(
                F("line_total") - F("tax_amount"),
                output_field=DecimalField(),
            ),
            line_count=Count("id"),
        )
        return {
            str(entry["tax_rate"]): {
                "rate": entry["tax_rate"],
                "taxable_amount": entry["taxable_amount"],
                "tax_amount": entry["total_tax"],
                "line_count": entry["line_count"],
            }
            for entry in lines
        }

    @classmethod
    def calculate_po_total(cls, purchase_order):
        """Calculate grand total: subtotal - discount + tax + shipping."""
        two = Decimal("0.01")
        subtotal = cls.calculate_po_subtotal(purchase_order)
        tax = cls.calculate_po_tax(purchase_order)

        # Order-level discount
        if purchase_order.discount_percentage > 0:
            discount = (
                subtotal * (purchase_order.discount_percentage / Decimal("100"))
            ).quantize(two, rounding=ROUND_HALF_UP)
        else:
            discount = purchase_order.discount_amount

        total = (subtotal - discount + tax + purchase_order.shipping_cost).quantize(
            two, rounding=ROUND_HALF_UP
        )
        return subtotal, tax, discount, total

    @classmethod
    def recalculate_po(cls, purchase_order):
        """Recalculate all line totals and PO totals atomically."""
        with transaction.atomic():
            # Recalculate each line
            for line in purchase_order.line_items.all():
                line.calculate_total()
                # Save without triggering signal loop
                type(line).objects.filter(pk=line.pk).update(
                    tax_amount=line.tax_amount,
                    line_total=line.line_total,
                )

            subtotal, tax, discount, total = cls.calculate_po_total(purchase_order)
            purchase_order.subtotal = subtotal
            purchase_order.tax_amount = tax
            purchase_order.total = total
            purchase_order.save(
                update_fields=["subtotal", "tax_amount", "total", "updated_on"]
            )

    @staticmethod
    def lookup_vendor_price(vendor_id, product_id):
        """Look up price and info from vendor product catalog."""
        import logging
        from datetime import date, timedelta
        from apps.vendors.models import VendorProduct

        logger = logging.getLogger(__name__)

        try:
            vp = VendorProduct.objects.get(
                vendor_id=vendor_id, product_id=product_id
            )
            expected_delivery = (
                date.today() + timedelta(days=vp.lead_time_days)
                if vp.lead_time_days
                else None
            )
            return {
                "unit_price": vp.unit_cost,
                "vendor_sku": vp.vendor_sku,
                "lead_time_days": vp.lead_time_days,
                "expected_delivery_date": expected_delivery,
                "minimum_order_quantity": vp.min_order_qty,
                "is_preferred": vp.is_preferred,
            }
        except VendorProduct.DoesNotExist:
            logger.warning(
                "No VendorProduct found for vendor %s, product %s.",
                vendor_id,
                product_id,
            )
            return None
