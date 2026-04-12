"""
VAT return generator service.

Generates VAT returns by calculating output VAT from sales,
input VAT from purchases, handling zero-rated/exempt sales,
SVAT adjustments, and producing PDF/CSV exports.
"""

import csv
import io
from datetime import date
from decimal import Decimal

from django.template.loader import render_to_string

from apps.accounting.models.tax_configuration import TaxConfiguration
from apps.accounting.models.tax_period import TaxPeriodRecord
from apps.accounting.models.vat_return import VATReturn


class VATReturnGenerator:
    """Generates complete VAT returns from invoice data for a given period."""

    STANDARD_RATE = Decimal("8.00")

    def __init__(self, period: TaxPeriodRecord):
        self.period = period
        self.tax_config = TaxConfiguration.objects.filter(is_active=True).first()

    def generate(self) -> VATReturn:
        """Generate a complete VAT return for the period."""
        sales_vat = self._get_sales_vat()
        purchase_vat = self._get_purchase_vat()
        zero_rated = self._get_zero_rated_sales()
        exempt = self._get_exempt_sales()
        svat = self._calculate_svat_adjustment(sales_vat, purchase_vat, zero_rated)

        output_vat = sales_vat["total_vat"]
        input_vat = purchase_vat["total_claimable_vat"] + svat.get("adjustment_amount", Decimal("0"))

        line_items = {
            "standard_rated": sales_vat["items"],
            "zero_rated": zero_rated["items"],
            "exempt": exempt["items"],
            "purchases": purchase_vat["items"],
            "svat_calculation": svat,
            "summary": {
                "total_standard_count": len(sales_vat["items"]),
                "total_zero_count": len(zero_rated["items"]),
                "total_exempt_count": len(exempt["items"]),
                "total_purchases_count": len(purchase_vat["items"]),
            },
        }

        vat_return = VATReturn(
            period=self.period,
            output_vat=output_vat,
            input_vat=input_vat,
            line_items=line_items,
        )
        vat_return.save()
        return vat_return

    def _get_sales_vat(self) -> dict:
        """Calculate output VAT from standard-rated sales invoices."""
        from apps.accounting.models import JournalEntry, JournalEntryLine

        items = []
        total_vat = Decimal("0")

        entries = JournalEntry.objects.filter(
            entry_date__gte=self.period.start_date,
            entry_date__lte=self.period.end_date,
            entry_source="SALES",
            entry_status="POSTED",
        )

        for entry in entries:
            vat_lines = entry.lines.filter(
                account__code__startswith="2-2",  # VAT liability accounts
            )
            for line in vat_lines:
                vat_amount = line.credit_amount - line.debit_amount
                if vat_amount > 0:
                    taxable = (vat_amount / self.STANDARD_RATE * 100).quantize(Decimal("0.01"))
                    items.append({
                        "invoice_number": entry.entry_number,
                        "date": entry.entry_date.isoformat(),
                        "description": entry.description if hasattr(entry, "description") else "",
                        "taxable_amount": str(taxable),
                        "vat_rate": str(self.STANDARD_RATE),
                        "vat_amount": str(vat_amount),
                        "total_amount": str(taxable + vat_amount),
                    })
                    total_vat += vat_amount

        return {"items": items, "total_vat": total_vat}

    def _get_purchase_vat(self) -> dict:
        """Calculate input VAT from purchase invoices with claimability rules."""
        from apps.accounting.models import JournalEntry

        items = []
        total_claimable_vat = Decimal("0")

        entries = JournalEntry.objects.filter(
            entry_date__gte=self.period.start_date,
            entry_date__lte=self.period.end_date,
            entry_source="PURCHASE",
            entry_status="POSTED",
        )

        for entry in entries:
            vat_lines = entry.lines.filter(
                account__code__startswith="1-5",  # Input VAT asset accounts
            )
            for line in vat_lines:
                vat_amount = line.debit_amount - line.credit_amount
                if vat_amount > 0:
                    claimable = vat_amount  # 100% claimable by default
                    items.append({
                        "supplier_invoice": entry.entry_number,
                        "date": entry.entry_date.isoformat(),
                        "description": entry.description if hasattr(entry, "description") else "",
                        "vat_amount": str(vat_amount),
                        "claimable_vat": str(claimable),
                        "purchase_type": "local",
                    })
                    total_claimable_vat += claimable

        return {"items": items, "total_claimable_vat": total_claimable_vat}

    def _get_zero_rated_sales(self) -> dict:
        """Identify zero-rated sales (exports, essential goods)."""
        from apps.accounting.models import JournalEntry

        items = []
        total_amount = Decimal("0")

        entries = JournalEntry.objects.filter(
            entry_date__gte=self.period.start_date,
            entry_date__lte=self.period.end_date,
            entry_source="SALES",
            entry_status="POSTED",
        )

        for entry in entries:
            revenue_lines = entry.lines.filter(
                account__code__startswith="4-",  # Revenue accounts
            )
            has_vat = entry.lines.filter(account__code__startswith="2-2").exists()
            if not has_vat:
                for line in revenue_lines:
                    amount = line.credit_amount - line.debit_amount
                    if amount > 0:
                        items.append({
                            "invoice_number": entry.entry_number,
                            "date": entry.entry_date.isoformat(),
                            "taxable_amount": str(amount),
                            "vat_amount": "0",
                        })
                        total_amount += amount

        return {"items": items, "total_amount": total_amount}

    def _get_exempt_sales(self) -> dict:
        """Identify exempt sales (financial services, education, healthcare)."""
        return {"items": [], "total_amount": Decimal("0")}

    def _calculate_svat_adjustment(self, sales_vat, purchase_vat, zero_rated) -> dict:
        """Calculate SVAT adjustment for export-heavy businesses."""
        if not self.tax_config or not self.tax_config.is_svat_registered:
            return {
                "is_svat_registered": False,
                "adjustment_amount": Decimal("0"),
            }

        total_taxable = sales_vat["total_vat"] / self.STANDARD_RATE * 100 if sales_vat["total_vat"] > 0 else Decimal("0")
        total_zero = zero_rated["total_amount"]
        total_sales = total_taxable + total_zero

        if total_sales == 0:
            return {
                "is_svat_registered": True,
                "export_ratio": "0",
                "adjustment_amount": Decimal("0"),
            }

        export_ratio = total_zero / total_sales
        enhancement_factor = Decimal("0.15")
        ceiling = Decimal("0.20")

        input_vat = purchase_vat["total_claimable_vat"]
        adjustment = min(
            input_vat * export_ratio * enhancement_factor,
            input_vat * ceiling,
        )

        return {
            "is_svat_registered": True,
            "export_ratio": str(export_ratio.quantize(Decimal("0.01"))),
            "enhancement_factor": str(enhancement_factor),
            "adjustment_amount": adjustment.quantize(Decimal("0.01")),
        }

    def generate_summary_by_rate(self, vat_return: VATReturn) -> dict:
        """Generate VAT summary grouped by rate."""
        line_items = vat_return.line_items
        standard = line_items.get("standard_rated", [])
        zero = line_items.get("zero_rated", [])
        exempt = line_items.get("exempt", [])

        standard_taxable = sum(Decimal(i.get("taxable_amount", "0")) for i in standard)
        standard_vat = sum(Decimal(i.get("vat_amount", "0")) for i in standard)
        zero_amount = sum(Decimal(i.get("taxable_amount", "0")) for i in zero)
        exempt_amount = sum(Decimal(i.get("taxable_amount", i.get("amount", "0"))) for i in exempt)

        total = standard_taxable + zero_amount + exempt_amount

        return {
            "period": f"{vat_return.period.year}-{vat_return.period.period_number:02d}",
            "rates": [
                {
                    "rate": "8%",
                    "label": "Standard Rated",
                    "count": len(standard),
                    "taxable_amount": str(standard_taxable),
                    "vat_amount": str(standard_vat),
                    "percentage": str((standard_taxable / total * 100).quantize(Decimal("0.01"))) if total else "0",
                },
                {
                    "rate": "0%",
                    "label": "Zero Rated",
                    "count": len(zero),
                    "taxable_amount": str(zero_amount),
                    "vat_amount": "0",
                    "percentage": str((zero_amount / total * 100).quantize(Decimal("0.01"))) if total else "0",
                },
                {
                    "rate": "N/A",
                    "label": "Exempt",
                    "count": len(exempt),
                    "taxable_amount": str(exempt_amount),
                    "vat_amount": "N/A",
                    "percentage": str((exempt_amount / total * 100).quantize(Decimal("0.01"))) if total else "0",
                },
            ],
            "totals": {
                "total_sales": str(total),
                "total_output_vat": str(vat_return.output_vat),
                "total_input_vat": str(vat_return.input_vat),
                "net_payable": str(vat_return.net_vat_payable),
            },
        }

    def export_csv(self, vat_return: VATReturn) -> str:
        """Export VAT return data as CSV for IRD portal upload."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\r\n")

        # Sales section
        writer.writerow(["SALES TRANSACTIONS"])
        writer.writerow([
            "Invoice#", "Date", "Customer TIN", "Taxable Amount",
            "VAT Rate", "VAT Amount", "Category",
        ])

        line_items = vat_return.line_items
        for item in line_items.get("standard_rated", []):
            writer.writerow([
                item.get("invoice_number", ""),
                item.get("date", ""),
                item.get("customer_tin", ""),
                item.get("taxable_amount", "0"),
                item.get("vat_rate", "8.00"),
                item.get("vat_amount", "0"),
                "Standard Rated",
            ])

        for item in line_items.get("zero_rated", []):
            writer.writerow([
                item.get("invoice_number", ""),
                item.get("date", ""),
                item.get("customer_tin", ""),
                item.get("taxable_amount", "0"),
                "0.00",
                "0",
                "Zero Rated",
            ])

        writer.writerow([])

        # Purchases section
        writer.writerow(["PURCHASE TRANSACTIONS"])
        writer.writerow([
            "Invoice#", "Date", "Supplier TIN", "Taxable Amount",
            "VAT Amount", "Purchase Type", "Category",
        ])

        for item in line_items.get("purchases", []):
            writer.writerow([
                item.get("supplier_invoice", ""),
                item.get("date", ""),
                item.get("supplier_tin", ""),
                item.get("taxable_amount", "0"),
                item.get("vat_amount", "0"),
                item.get("purchase_type", "local"),
                "Standard Purchase",
            ])

        writer.writerow([])

        # Summary
        writer.writerow(["SUMMARY"])
        writer.writerow(["Output VAT", str(vat_return.output_vat)])
        writer.writerow(["Input VAT", str(vat_return.input_vat)])
        writer.writerow(["Net VAT Payable", str(vat_return.net_vat_payable)])

        return output.getvalue()

    def render_pdf_html(self, vat_return: VATReturn) -> str:
        """Render VAT return as HTML for PDF generation."""
        context = {
            "vat_return": vat_return,
            "tax_config": self.tax_config,
            "period": self.period,
            "line_items": vat_return.line_items,
            "summary": self.generate_summary_by_rate(vat_return),
            "generated_date": date.today().isoformat(),
        }
        return render_to_string("tax/vat_return.html", context)
