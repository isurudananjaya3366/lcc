"""
PO PDF Generator service.

Generates PDF documents for purchase orders using reportlab or
a simple text-based fallback.
"""

import io
from datetime import datetime


class POPDFGenerator:
    """Generates PDF documents for purchase orders."""

    @classmethod
    def generate_pdf(cls, po, template=None):
        """
        Generate a PDF for the given purchase order.

        Args:
            po: PurchaseOrder instance.
            template: Optional POTemplate instance for styling.

        Returns:
            bytes: PDF content.
        """
        try:
            from reportlab.lib.pagesizes import A4
            return cls._generate_reportlab_pdf(po, template)
        except ImportError:
            return cls._generate_text_pdf(po, template)

    @classmethod
    def _generate_reportlab_pdf(cls, po, template=None):
        """Generate PDF using reportlab with full sections."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Table,
            TableStyle,
            Paragraph,
            Spacer,
            HRFlowable,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_RIGHT, TA_CENTER

        buffer = io.BytesIO()

        # Page size from template
        pagesize = A4
        if template and template.page_size == "Letter":
            pagesize = letter

        doc = SimpleDocTemplate(buffer, pagesize=pagesize)
        styles = getSampleStyleSheet()

        # Custom styles from template
        primary_color = colors.HexColor(template.primary_color) if template else colors.black
        secondary_color = colors.HexColor(template.secondary_color) if template else colors.grey
        header_size = template.font_size_header if template else 16
        body_size = template.font_size_body if template else 10

        styles.add(ParagraphStyle(
            "CompanyName", parent=styles["Title"],
            fontSize=header_size, textColor=primary_color,
        ))
        styles.add(ParagraphStyle(
            "RightAlign", parent=styles["Normal"],
            alignment=TA_RIGHT, fontSize=body_size,
        ))
        styles.add(ParagraphStyle(
            "CenterAlign", parent=styles["Normal"],
            alignment=TA_CENTER, fontSize=body_size,
        ))

        elements = []

        # ── HEADER SECTION ────────────────────────────────────────
        elements.extend(cls._render_header(po, template, styles, primary_color))
        elements.append(HRFlowable(width="100%", color=primary_color, thickness=1))
        elements.append(Spacer(1, 5 * mm))

        # ── VENDOR & SHIP TO SECTIONS ─────────────────────────────
        elements.extend(cls._render_vendor_and_shipping(po, template, styles))
        elements.append(Spacer(1, 5 * mm))

        # ── LINE ITEMS TABLE ─────────────────────────────────────
        elements.extend(cls._render_line_items_table(po, template, styles, primary_color))
        elements.append(Spacer(1, 5 * mm))

        # ── TOTALS SECTION ────────────────────────────────────────
        elements.extend(cls._render_totals_section(po, template, styles))
        elements.append(Spacer(1, 5 * mm))

        # ── TERMS & SIGNATURES ────────────────────────────────────
        elements.extend(cls._render_terms_section(po, template, styles))
        elements.append(Spacer(1, 10 * mm))
        elements.extend(cls._render_signature_section(styles))

        # ── FOOTER ────────────────────────────────────────────────
        if template and template.footer_text:
            elements.append(Spacer(1, 5 * mm))
            elements.append(HRFlowable(width="100%", color=secondary_color, thickness=0.5))
            elements.append(Paragraph(template.footer_text, styles["CenterAlign"]))

        doc.build(elements)
        return buffer.getvalue()

    @classmethod
    def _render_header(cls, po, template, styles, primary_color):
        """Render the PDF header - company info, PO number, date."""
        from reportlab.platypus import Paragraph, Table, TableStyle
        from reportlab.lib import colors

        elements = []
        company = template.company_name if template else "Company"
        elements.append(Paragraph(f"<b>{company}</b>", styles["CompanyName"]))

        if template:
            address_parts = []
            if template.company_address:
                address_parts.append(template.company_address)
            if template.company_phone:
                address_parts.append(f"Phone: {template.company_phone}")
            if template.company_email:
                address_parts.append(f"Email: {template.company_email}")
            if template.company_website:
                address_parts.append(template.company_website)
            if template.tax_id:
                address_parts.append(f"Tax ID: {template.tax_id}")
            if address_parts:
                elements.append(Paragraph(
                    "<br/>".join(address_parts), styles["Normal"]
                ))

        # PO details
        elements.append(Paragraph(
            f"<b>Purchase Order: {po.po_number}</b>", styles["Heading2"]
        ))

        details = [
            f"Date: {po.order_date}",
            f"Status: {po.get_status_display()}",
        ]
        if po.expected_delivery_date:
            details.append(f"Expected Delivery: {po.expected_delivery_date}")
        if po.vendor_reference:
            details.append(f"Vendor Ref: {po.vendor_reference}")

        elements.append(Paragraph(" | ".join(details), styles["Normal"]))

        if template and template.header_text:
            elements.append(Paragraph(template.header_text, styles["Normal"]))

        return elements

    @classmethod
    def _render_vendor_and_shipping(cls, po, template, styles):
        """Render vendor info and Ship To sections side by side."""
        from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
        from reportlab.lib import colors
        from reportlab.lib.units import mm

        elements = []

        # VENDOR TO section
        vendor = po.vendor
        vendor_lines = [f"<b>VENDOR</b>"]
        vendor_lines.append(str(vendor.company_name))
        if hasattr(vendor, "address") and vendor.address:
            vendor_lines.append(str(vendor.address))
        if hasattr(vendor, "phone") and vendor.phone:
            vendor_lines.append(f"Phone: {vendor.phone}")
        if hasattr(vendor, "email") and vendor.email:
            vendor_lines.append(f"Email: {vendor.email}")
        if hasattr(vendor, "contact_person") and vendor.contact_person:
            vendor_lines.append(f"Contact: {vendor.contact_person}")
        vendor_text = "<br/>".join(vendor_lines)

        # SHIP TO section
        ship_lines = [f"<b>SHIP TO</b>"]
        if po.ship_to_address:
            ship_lines.append(po.ship_to_address)
        if po.shipping_method:
            ship_lines.append(f"Method: {po.shipping_method}")
        if hasattr(po, "receiving_warehouse") and po.receiving_warehouse:
            ship_lines.append(f"Warehouse: {po.receiving_warehouse}")
        ship_text = "<br/>".join(ship_lines)

        # Two-column table
        data = [[
            Paragraph(vendor_text, styles["Normal"]),
            Paragraph(ship_text, styles["Normal"]),
        ]]
        table = Table(data, colWidths=["50%", "50%"])
        table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(table)
        return elements

    @classmethod
    def _render_line_items_table(cls, po, template, styles, primary_color):
        """Render line items as a table with template settings."""
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle

        elements = []

        # Build headers based on template settings
        headers = []
        show_line_numbers = template.show_line_numbers if template else True
        show_item_codes = template.show_item_codes if template else True

        if show_line_numbers:
            headers.append("#")
        headers.append("Product")
        if show_item_codes:
            headers.append("SKU")
        headers.extend(["Qty", "Unit Price", "Tax", "Total"])

        data = [headers]
        for idx, line in enumerate(po.line_items.all()):
            row = []
            if show_line_numbers:
                row.append(str(line.line_number))
            row.append(line.product_name)
            if show_item_codes:
                row.append(line.vendor_sku or "")
            row.extend([
                str(line.quantity_ordered),
                f"{line.unit_price:.2f}",
                f"{line.tax_amount:.2f}",
                f"{line.line_total:.2f}",
            ])
            data.append(row)

        if len(data) > 1:
            table = Table(data, repeatRows=1)
            style_commands = [
                ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (-3, 1), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
            # Alternating row colors
            for i in range(1, len(data)):
                if i % 2 == 0:
                    style_commands.append(
                        ("BACKGROUND", (0, i), (-1, i), colors.Color(0.95, 0.95, 0.95))
                    )
            table.setStyle(TableStyle(style_commands))
            elements.append(table)
        return elements

    @classmethod
    def _render_totals_section(cls, po, template, styles):
        """Render the totals section on the right side."""
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors

        elements = []
        show_tax_breakdown = template.show_tax_breakdown if template else True

        totals_data = [
            ["Subtotal:", f"{po.currency} {po.subtotal:.2f}"],
        ]
        if po.discount_amount:
            totals_data.append(["Discount:", f"-{po.currency} {po.discount_amount:.2f}"])
        if show_tax_breakdown:
            totals_data.append(["Tax:", f"{po.currency} {po.tax_amount:.2f}"])
        if po.shipping_cost:
            totals_data.append(["Shipping:", f"{po.currency} {po.shipping_cost:.2f}"])
        totals_data.append(["TOTAL:", f"{po.currency} {po.total:.2f}"])

        # Right-aligned totals table
        totals_table = Table(totals_data, colWidths=[100, 120], hAlign="RIGHT")
        totals_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("FONT", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(totals_table)
        return elements

    @classmethod
    def _render_terms_section(cls, po, template, styles):
        """Render payment terms and notes."""
        from reportlab.platypus import Paragraph

        elements = []
        elements.append(Paragraph("<b>Terms & Conditions</b>", styles["Heading3"]))

        if po.payment_terms:
            elements.append(
                Paragraph(f"<b>Payment Terms:</b> {po.payment_terms}", styles["Normal"])
            )
        if po.notes:
            elements.append(
                Paragraph(f"<b>Notes:</b> {po.notes}", styles["Normal"])
            )
        if po.delivery_instructions:
            elements.append(
                Paragraph(
                    f"<b>Delivery Instructions:</b> {po.delivery_instructions}",
                    styles["Normal"],
                )
            )
        return elements

    @classmethod
    def _render_signature_section(cls, styles):
        """Render signature lines for Prepared By, Approved By, Vendor Ack."""
        from reportlab.platypus import Table, TableStyle, Spacer
        from reportlab.lib.units import mm

        elements = []
        sig_data = [
            ["_" * 30, "_" * 30, "_" * 30],
            ["Prepared By", "Approved By", "Vendor Acknowledgment"],
            ["Date: ____________", "Date: ____________", "Date: ____________"],
        ]
        sig_table = Table(sig_data, colWidths=["33%", "33%", "34%"])
        sig_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(sig_table)
        return elements

    @classmethod
    def _generate_text_pdf(cls, po, template=None):
        """
        Fallback text-based PDF generation when reportlab is not available.
        Returns UTF-8 encoded text content.
        """
        lines = []
        company = template.company_name if template else "Company"
        lines.append(f"{'=' * 70}")
        lines.append(f"  {company}")
        if template:
            if template.company_address:
                lines.append(f"  {template.company_address}")
            if template.company_phone:
                lines.append(f"  Phone: {template.company_phone}")
        lines.append(f"{'=' * 70}")
        lines.append("")
        lines.append(f"  PURCHASE ORDER: {po.po_number}")
        lines.append(f"  Date: {po.order_date}")
        lines.append(f"  Status: {po.get_status_display()}")
        if po.expected_delivery_date:
            lines.append(f"  Expected Delivery: {po.expected_delivery_date}")
        lines.append(f"{'-' * 70}")
        lines.append("")

        # Vendor & Ship To
        lines.append(f"  VENDOR: {po.vendor.company_name}")
        if po.vendor_reference:
            lines.append(f"  Vendor Ref: {po.vendor_reference}")
        lines.append("")
        if po.ship_to_address:
            lines.append(f"  SHIP TO: {po.ship_to_address}")
        if po.shipping_method:
            lines.append(f"  Shipping Method: {po.shipping_method}")
        lines.append(f"{'-' * 70}")
        lines.append("")

        lines.append("  LINE ITEMS:")
        lines.append(f"  {'#':<4} {'Product':<30} {'Qty':<6} {'Price':<12} {'Total':<12}")
        lines.append(f"  {'-' * 66}")
        for line in po.line_items.all():
            lines.append(
                f"  {line.line_number:<4} {line.product_name:<30} "
                f"{line.quantity_ordered:<6} {line.unit_price:<12} {line.line_total:<12}"
            )
        lines.append(f"{'-' * 70}")
        lines.append("")
        lines.append(f"  {'Subtotal:':>50} {po.currency} {po.subtotal}")
        lines.append(f"  {'Tax:':>50} {po.currency} {po.tax_amount}")
        if po.shipping_cost:
            lines.append(f"  {'Shipping:':>50} {po.currency} {po.shipping_cost}")
        lines.append(f"  {'TOTAL:':>50} {po.currency} {po.total}")
        lines.append("")

        if po.payment_terms:
            lines.append(f"  Payment Terms: {po.payment_terms}")
        if po.notes:
            lines.append(f"  Notes: {po.notes}")
        lines.append("")
        lines.append(f"  {'_' * 20}        {'_' * 20}        {'_' * 20}")
        lines.append(f"  {'Prepared By':^20}        {'Approved By':^20}        {'Vendor Ack':^20}")
        lines.append(f"{'=' * 70}")

        return "\n".join(lines).encode("utf-8")
