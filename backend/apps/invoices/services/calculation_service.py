"""
Invoice calculation service.

Handles all financial calculations for invoices: line item totals,
VAT/SVAT tax calculations, header discounts, and tax breakdowns.
"""

import logging
from collections import defaultdict
from decimal import Decimal

from django.db import transaction

from apps.invoices.constants import (
    DiscountType,
    SRI_LANKA_SVAT_RATE,
    SRI_LANKA_VAT_RATE,
    TaxScheme,
)

logger = logging.getLogger(__name__)


class InvoiceCalculationService:
    """
    Service for calculating invoice and line item totals.
    Handles discounts, taxes, and Sri Lanka VAT/SVAT calculations.
    """

    # ── Line Item Calculations ──────────────────────────────────────

    @classmethod
    def calculate_line_item(cls, line_item):
        """Calculate a single line item's discount, tax, and total."""
        line_subtotal = line_item.quantity * line_item.unit_price

        # Discount
        if line_item.discount_type == DiscountType.PERCENTAGE and line_item.discount_value:
            line_item.discount_amount = (
                line_subtotal * line_item.discount_value / Decimal("100")
            ).quantize(Decimal("0.01"))
        elif line_item.discount_type == DiscountType.FIXED and line_item.discount_value:
            line_item.discount_amount = min(line_item.discount_value, line_subtotal)
        else:
            line_item.discount_amount = Decimal("0.00")

        taxable_amount = line_subtotal - line_item.discount_amount

        # Tax
        if line_item.is_taxable and line_item.tax_rate > 0:
            line_item.tax_amount = (
                taxable_amount * line_item.tax_rate / Decimal("100")
            ).quantize(Decimal("0.01"))
        else:
            line_item.tax_amount = Decimal("0.00")

        line_item.line_total = taxable_amount + line_item.tax_amount
        return line_item

    @classmethod
    @transaction.atomic
    def calculate_all_line_items(cls, invoice):
        """Calculate all line items for an invoice."""
        for line_item in invoice.line_items.all():
            cls.calculate_line_item(line_item)
            line_item.save(update_fields=["discount_amount", "tax_amount", "line_total"])

    # ── Tax Calculations ────────────────────────────────────────────

    @classmethod
    def calculate_vat(cls, taxable_amount, rate=None):
        """Calculate standard VAT amount."""
        if rate is None:
            rate = Decimal(str(SRI_LANKA_VAT_RATE))
        return (taxable_amount * rate / Decimal("100")).quantize(Decimal("0.01"))

    @classmethod
    def calculate_svat(cls, taxable_amount, rate=None):
        """Calculate simplified VAT amount."""
        if rate is None:
            rate = Decimal(str(SRI_LANKA_SVAT_RATE))
        return (taxable_amount * rate / Decimal("100")).quantize(Decimal("0.01"))

    @classmethod
    def apply_vat_to_line_item(cls, line_item, vat_rate=None):
        """Apply standard VAT rate to a single line item."""
        if vat_rate is None:
            vat_rate = Decimal(str(SRI_LANKA_VAT_RATE))
        line_item.is_taxable = True
        line_item.tax_rate = vat_rate
        line_item.tax_code = "STANDARD_RATE"
        line_item.tax_description = f"VAT {vat_rate}%"
        cls.calculate_line_item(line_item)
        line_item.save()
        return line_item

    @classmethod
    @transaction.atomic
    def apply_vat_to_invoice(cls, invoice, vat_rate=None):
        """Apply standard VAT rate to all taxable line items on an invoice."""
        if vat_rate is None:
            vat_rate = Decimal(str(SRI_LANKA_VAT_RATE))
        for item in invoice.line_items.filter(is_taxable=True):
            item.tax_rate = vat_rate
            item.tax_code = "STANDARD_RATE"
            item.tax_description = f"VAT {vat_rate}%"
            cls.calculate_line_item(item)
            item.save()
        cls.calculate_invoice_totals(invoice)
        invoice.save()
        return invoice

    @classmethod
    def apply_svat_to_line_item(cls, line_item, svat_rate=None):
        """Apply SVAT rate to a single line item."""
        if svat_rate is None:
            svat_rate = Decimal(str(SRI_LANKA_SVAT_RATE))
        line_item.is_taxable = True
        line_item.tax_rate = svat_rate
        line_item.tax_code = "SVAT_RATE"
        line_item.tax_description = f"Simplified VAT {svat_rate}%"
        cls.calculate_line_item(line_item)
        line_item.save()
        return line_item

    @classmethod
    @transaction.atomic
    def apply_svat_to_invoice(cls, invoice, svat_rate=None):
        """Apply SVAT rate to all taxable line items on an invoice."""
        if svat_rate is None:
            svat_rate = Decimal(str(SRI_LANKA_SVAT_RATE))
        for item in invoice.line_items.filter(is_taxable=True):
            item.tax_rate = svat_rate
            item.tax_code = "SVAT_RATE"
            item.tax_description = f"Simplified VAT {svat_rate}%"
            cls.calculate_line_item(item)
            item.save()
        cls.calculate_invoice_totals(invoice)
        invoice.save()
        return invoice

    # ── Tax Breakdown ───────────────────────────────────────────────

    @classmethod
    def generate_tax_breakdown(cls, invoice):
        """
        Generate a tax breakdown grouped by rate.
        Returns list of dicts: [{rate, taxable_amount, tax_amount}]
        """
        breakdown = defaultdict(lambda: {"taxable_amount": Decimal("0.00"), "tax_amount": Decimal("0.00")})

        for item in invoice.line_items.all():
            if item.is_taxable and item.tax_rate > 0:
                key = str(item.tax_rate)
                line_subtotal = item.quantity * item.unit_price - item.discount_amount
                breakdown[key]["taxable_amount"] += line_subtotal
                breakdown[key]["tax_amount"] += item.tax_amount

        result = []
        for rate, amounts in sorted(breakdown.items()):
            result.append({
                "rate": rate,
                "taxable_amount": str(amounts["taxable_amount"].quantize(Decimal("0.01"))),
                "tax_amount": str(amounts["tax_amount"].quantize(Decimal("0.01"))),
            })
        return result

    # ── Header Discount ─────────────────────────────────────────────

    @classmethod
    def apply_header_discount(cls, invoice, subtotal_after_line_discounts):
        """Apply invoice-level header discount."""
        if invoice.discount_type == DiscountType.PERCENTAGE and invoice.discount_value:
            invoice.discount_amount = (
                subtotal_after_line_discounts * invoice.discount_value / Decimal("100")
            ).quantize(Decimal("0.01"))
        elif invoice.discount_type == DiscountType.FIXED and invoice.discount_value:
            invoice.discount_amount = min(
                invoice.discount_value, subtotal_after_line_discounts
            )
        else:
            invoice.discount_amount = Decimal("0.00")

    # ── Invoice Totals ──────────────────────────────────────────────

    @classmethod
    def calculate_invoice_totals(cls, invoice):
        """Calculate invoice-level totals from line items."""
        line_items = list(invoice.line_items.all())

        # Subtotal = sum of (qty × unit_price) for all lines
        invoice.subtotal = sum(
            (item.quantity * item.unit_price for item in line_items),
            Decimal("0.00"),
        )

        # Line-level discounts total
        line_discounts = sum(
            (item.discount_amount for item in line_items), Decimal("0.00")
        )
        subtotal_after_line_discounts = invoice.subtotal - line_discounts

        # Header discount
        cls.apply_header_discount(invoice, subtotal_after_line_discounts)

        # Total tax from line items
        invoice.tax_amount = sum(
            (item.tax_amount for item in line_items), Decimal("0.00")
        )

        # Tax breakdown
        invoice.tax_breakdown = cls.generate_tax_breakdown(invoice)

        # Grand total
        invoice.total = (
            subtotal_after_line_discounts - invoice.discount_amount + invoice.tax_amount
        )

        # Balance
        invoice.balance_due = invoice.total - invoice.amount_paid

        # Base currency
        invoice.calculate_base_currency_total()

        return invoice

    # ── Full Recalculation ──────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def recalculate_invoice(cls, invoice_id):
        """Fully recalculate an invoice including all line items and totals."""
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.get(id=invoice_id)
        cls.calculate_all_line_items(invoice)
        cls.calculate_invoice_totals(invoice)
        invoice.save(update_fields=[
            "subtotal", "discount_amount", "tax_amount", "total",
            "balance_due", "tax_breakdown", "base_currency_total",
        ])
        logger.info("Invoice %s recalculated", invoice.invoice_number or invoice.id)
        return invoice
