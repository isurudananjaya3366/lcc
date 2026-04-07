"""
Bill Calculation Service.

Handles all vendor bill financial calculations including
line totals, tax aggregation, and grand totals.
"""

from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum


class BillCalculationService:
    """Centralized calculation logic for vendor bills."""

    TWO = Decimal("0.01")

    @staticmethod
    def calculate_line_total(quantity, billed_price, tax_rate=None):
        """Calculate a single line item total including tax."""
        two = Decimal("0.01")
        quantity = Decimal(str(quantity))
        billed_price = Decimal(str(billed_price))
        tax_rate = Decimal(str(tax_rate or 0))

        subtotal = (quantity * billed_price).quantize(two, rounding=ROUND_HALF_UP)
        tax = (subtotal * (tax_rate / Decimal("100"))).quantize(
            two, rounding=ROUND_HALF_UP
        )
        total = subtotal + tax
        return total, tax, subtotal

    @staticmethod
    def calculate_line_tax(subtotal, tax_rate):
        """Calculate tax amount for a line item."""
        two = Decimal("0.01")
        tax_rate = Decimal(str(tax_rate or 0))
        subtotal = Decimal(str(subtotal))
        return (subtotal * (tax_rate / Decimal("100"))).quantize(
            two, rounding=ROUND_HALF_UP
        )

    @staticmethod
    def calculate_bill_subtotal(vendor_bill):
        """Sum all line_total values minus tax for a bill."""
        result = vendor_bill.line_items.aggregate(
            total=Sum("line_total"),
            total_tax=Sum("tax_amount"),
        )
        total = result["total"] or Decimal("0.00")
        tax = result["total_tax"] or Decimal("0.00")
        return total - tax

    @staticmethod
    def calculate_bill_tax(vendor_bill):
        """Sum all tax_amount values for a bill."""
        result = vendor_bill.line_items.aggregate(
            total_tax=Sum("tax_amount")
        )
        return result["total_tax"] or Decimal("0.00")

    @classmethod
    def calculate_bill_total(cls, vendor_bill):
        """
        Calculate grand total: subtotal + tax - discount.

        Returns:
            Tuple of (subtotal, tax, total).
        """
        two = Decimal("0.01")
        subtotal = cls.calculate_bill_subtotal(vendor_bill)
        tax = cls.calculate_bill_tax(vendor_bill)
        discount = vendor_bill.discount_amount or Decimal("0.00")
        total = (subtotal + tax - discount).quantize(two, rounding=ROUND_HALF_UP)
        return subtotal, tax, total

    @classmethod
    def recalculate_bill(cls, vendor_bill):
        """Recalculate all line totals and bill totals atomically."""
        with transaction.atomic():
            for line in vendor_bill.line_items.all():
                line.calculate_line_total()
                type(line).objects.filter(pk=line.pk).update(
                    line_total=line.line_total,
                    tax_amount=line.tax_amount,
                )

            subtotal, tax, total = cls.calculate_bill_total(vendor_bill)
            type(vendor_bill).objects.filter(pk=vendor_bill.pk).update(
                subtotal=subtotal,
                tax_amount=tax,
                total=total,
            )
            vendor_bill.subtotal = subtotal
            vendor_bill.tax_amount = tax
            vendor_bill.total = total

    @staticmethod
    def calculate_amount_due(vendor_bill):
        """Calculate remaining amount due on a bill."""
        return vendor_bill.total - vendor_bill.amount_paid

    @staticmethod
    def calculate_early_payment_discount(vendor_bill, payment_date=None):
        """
        Calculate early payment discount if applicable.

        Args:
            vendor_bill: VendorBill instance.
            payment_date: Date of payment (defaults to today).

        Returns:
            Decimal discount amount (0 if not applicable).
        """
        from datetime import date as date_type

        try:
            from apps.vendor_bills.models.bill_settings import BillSettings
            settings = BillSettings.objects.first()
            if not settings or not settings.allow_early_payment_discount:
                return Decimal("0.00")

            payment_date = payment_date or date_type.today()
            discount_deadline = vendor_bill.bill_date + __import__(
                "datetime"
            ).timedelta(days=settings.early_payment_discount_days or 0)

            if payment_date <= discount_deadline:
                pct = settings.early_payment_discount_percentage or Decimal("0")
                return (vendor_bill.total * pct / Decimal("100")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
        except Exception:
            pass
        return Decimal("0.00")

    @staticmethod
    def get_tax_breakdown(vendor_bill):
        """Return tax breakdown grouped by rate."""
        from django.db.models import Count, DecimalField, F

        lines = vendor_bill.line_items.values("tax_rate").annotate(
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
