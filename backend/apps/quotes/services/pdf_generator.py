"""
Quote PDF Generator Service.

Tasks 59-66: Generates PDF quotes using reportlab.
Supports configurable templates, QR codes, and styled output.
"""

import io
import logging
import uuid
from decimal import Decimal

from django.core.files.base import ContentFile
from django.utils import timezone

logger = logging.getLogger(__name__)

# Page-size constants in points (1 pt = 1/72 inch)
MM = 72 / 25.4  # conversion factor: mm → points


class QuotePDFGenerator:
    """
    Generate PDF documents for quotes.

    Usage::

        generator = QuotePDFGenerator(quote)
        pdf_bytes = generator.generate()
        generator.generate_and_save()   # save to Quote.pdf_file
    """

    def __init__(self, quote, template=None):
        self.quote = quote
        self.template = template or self._resolve_template()
        self._buffer = None
        self._canvas = None
        self._y = 0  # current Y position (top-down)
        self._page_width = 0
        self._page_height = 0
        self._margin_top = 0
        self._margin_bottom = 0
        self._margin_left = 0
        self._margin_right = 0

    # ── Public API ───────────────────────────────────────────────

    def generate(self) -> bytes:
        """Generate a PDF and return the raw bytes."""
        try:
            from reportlab.lib.pagesizes import A4, LEGAL, LETTER, landscape
            from reportlab.pdfgen import canvas as rl_canvas
        except ImportError as exc:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install it with: pip install reportlab"
            ) from exc

        self._buffer = io.BytesIO()

        page_map = {"A4": A4, "Letter": LETTER, "Legal": LEGAL}
        page_size = page_map.get(self.template.page_size, A4)

        if self.template.page_orientation == "landscape":
            page_size = landscape(page_size)

        self._page_width, self._page_height = page_size
        self._margin_top = self.template.margin_top * MM
        self._margin_bottom = self.template.margin_bottom * MM
        self._margin_left = self.template.margin_left * MM
        self._margin_right = self.template.margin_right * MM

        self._canvas = rl_canvas.Canvas(self._buffer, pagesize=page_size)
        self._canvas.setTitle(f"Quote {self.quote.quote_number}")
        self._canvas.setAuthor("POS Quote System")

        self._y = self._page_height - self._margin_top

        self._generate_header()
        self._generate_quote_info()
        self._generate_customer_section()
        self._generate_line_items()
        self._generate_totals()
        self._generate_notes_section()
        self._generate_terms_section()
        self._generate_qr_code()
        self._generate_signature_section()
        self._generate_footer()

        self._canvas.save()
        pdf_bytes = self._buffer.getvalue()
        self._buffer.close()
        return pdf_bytes

    def generate_and_save(self) -> str:
        """Generate PDF, save to model, and return the file path."""
        pdf_bytes = self.generate()

        filename = f"{self.quote.quote_number}.pdf"
        self.quote.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
        self.quote.pdf_generated_at = timezone.now()
        self.quote.pdf_file_size = len(pdf_bytes)
        self.quote.pdf_regeneration_count = (self.quote.pdf_regeneration_count or 0) + 1

        if not self.quote.public_token:
            self.quote.public_token = uuid.uuid4()

        self.quote.save(
            update_fields=[
                "pdf_file",
                "pdf_generated_at",
                "pdf_file_size",
                "pdf_regeneration_count",
                "public_token",
            ]
        )
        logger.info(
            "PDF generated for %s (%d bytes)",
            self.quote.quote_number,
            len(pdf_bytes),
        )
        return self.quote.pdf_file.name

    # ── Internal helpers ─────────────────────────────────────────

    def _resolve_template(self):
        """Return the template linked to the quote or tenant default."""
        if self.quote.template_id:
            return self.quote.template
        from apps.quotes.models.template import QuoteTemplate

        try:
            from django_tenants.utils import get_tenant_model

            tenant = getattr(self.quote, "_tenant", None)
            if not tenant:
                from django.db import connection

                tenant = connection.tenant
            return QuoteTemplate.get_default_template(tenant)
        except Exception:
            return QuoteTemplate()

    def _content_width(self):
        return self._page_width - self._margin_left - self._margin_right

    def _new_page_if_needed(self, needed_height=40):
        if self._y - needed_height < self._margin_bottom:
            self._canvas.showPage()
            self._y = self._page_height - self._margin_top

    def _draw_text(self, x, y, text, font="Helvetica", size=10, color=None):
        c = self._canvas
        if color:
            c.setFillColor(color)
        c.setFont(font, size)
        c.drawString(x, y, str(text))
        if color:
            c.setFillColor("#000000")

    def _draw_right_text(self, x, y, text, font="Helvetica", size=10, color=None):
        c = self._canvas
        if color:
            c.setFillColor(color)
        c.setFont(font, size)
        c.drawRightString(x, y, str(text))
        if color:
            c.setFillColor("#000000")

    def _hex_to_color(self, hex_str):
        """Convert a hex colour string to a reportlab Color."""
        from reportlab.lib.colors import HexColor

        try:
            return HexColor(hex_str)
        except Exception:
            return HexColor("#000000")

    def _format_currency(self, amount):
        """Format a Decimal/float as a currency string."""
        symbol = self.quote.currency_symbol
        try:
            return f"{symbol} {Decimal(str(amount)):,.2f}"
        except Exception:
            return f"{symbol} {amount}"

    # ── Section renderers ────────────────────────────────────────

    def _generate_header(self):
        """Render company header with optional logo."""
        tpl = self.template
        primary = self._hex_to_color(tpl.primary_color)
        left = self._margin_left
        right = self._page_width - self._margin_right

        # Company name
        self._draw_text(
            left, self._y, tpl.business_name or "Company Name",
            font=tpl.header_font + "-Bold" if tpl.header_font == "Helvetica" else tpl.header_font,
            size=18, color=primary,
        )
        self._y -= 20

        # Contact info
        if tpl.show_contact_info:
            contact_parts = []
            if tpl.phone_number:
                contact_parts.append(tpl.phone_number)
            if tpl.email_address:
                contact_parts.append(tpl.email_address)
            if tpl.website:
                contact_parts.append(tpl.website)
            if contact_parts:
                self._draw_text(left, self._y, " | ".join(contact_parts), size=8)
                self._y -= 12

        # Address
        if tpl.show_business_address and tpl.business_address:
            addr_parts = [tpl.business_address]
            if tpl.business_city:
                addr_parts.append(tpl.business_city)
            if tpl.business_postal_code:
                addr_parts.append(tpl.business_postal_code)
            if tpl.business_country:
                addr_parts.append(tpl.business_country)
            self._draw_text(left, self._y, ", ".join(addr_parts), size=8)
            self._y -= 12

        # Registration numbers
        reg_parts = []
        if tpl.company_registration_number:
            reg_parts.append(f"Reg: {tpl.company_registration_number}")
        if tpl.tax_registration_number:
            reg_parts.append(f"Tax: {tpl.tax_registration_number}")
        if reg_parts:
            self._draw_text(left, self._y, " | ".join(reg_parts), size=7)
            self._y -= 12

        # QUOTATION title (right-aligned)
        self._draw_right_text(
            right, self._page_height - self._margin_top,
            "QUOTATION", font="Helvetica-Bold", size=22, color=primary,
        )

        # Horizontal rule
        self._y -= 6
        self._canvas.setStrokeColor(primary)
        self._canvas.setLineWidth(1.5)
        self._canvas.line(left, self._y, right, self._y)
        self._y -= 16

    def _generate_quote_info(self):
        """Render quote number, date, validity, and status."""
        left = self._margin_left
        right = self._page_width - self._margin_right
        col_right = right - 10

        info = [
            ("Quote #:", self.quote.quote_number),
            ("Date:", self.quote.issue_date.strftime("%d %b %Y") if self.quote.issue_date else "-"),
            ("Status:", self.quote.get_status_display()),
        ]
        if self.quote.valid_until:
            info.append(("Valid Until:", self.quote.valid_until.strftime("%d %b %Y")))
        if self.quote.revision_number > 1:
            info.append(("Revision:", str(self.quote.revision_number)))

        for label, value in info:
            self._draw_right_text(col_right, self._y, value, size=9)
            self._draw_right_text(
                col_right - 80, self._y, label,
                font="Helvetica-Bold", size=9,
            )
            self._y -= 14

        self._y -= 8

    def _generate_customer_section(self):
        """Render customer details block."""
        self._new_page_if_needed(80)
        left = self._margin_left
        primary = self._hex_to_color(self.template.primary_color)

        self._draw_text(left, self._y, "Bill To:", font="Helvetica-Bold", size=11, color=primary)
        self._y -= 16

        q = self.quote
        name = q.customer_display_name
        self._draw_text(left, self._y, name, font="Helvetica-Bold", size=10)
        self._y -= 14

        if q.customer:
            if hasattr(q.customer, "company_name") and q.customer.company_name:
                self._draw_text(left, self._y, q.customer.company_name, size=9)
                self._y -= 12
            if hasattr(q.customer, "email") and q.customer.email:
                self._draw_text(left, self._y, q.customer.email, size=9)
                self._y -= 12
            if hasattr(q.customer, "phone") and q.customer.phone:
                self._draw_text(left, self._y, q.customer.phone, size=9)
                self._y -= 12
        else:
            if q.guest_company:
                self._draw_text(left, self._y, q.guest_company, size=9)
                self._y -= 12
            if q.guest_email:
                self._draw_text(left, self._y, q.guest_email, size=9)
                self._y -= 12
            if q.guest_phone:
                self._draw_text(left, self._y, q.guest_phone, size=9)
                self._y -= 12

        self._y -= 10

    def _generate_line_items(self):
        """Render line items as a table."""
        self._new_page_if_needed(60)
        left = self._margin_left
        right = self._page_width - self._margin_right
        primary = self._hex_to_color(self.template.primary_color)

        line_items = self.quote.line_items.order_by("position")

        # Table header
        cols = self._get_column_positions()
        header_y = self._y

        # Header background
        self._canvas.setFillColor(primary)
        self._canvas.rect(left, header_y - 4, right - left, 18, fill=1, stroke=0)
        self._canvas.setFillColor("#FFFFFF")
        self._canvas.setFont("Helvetica-Bold", 9)

        for col_name, col_x, col_align in cols:
            if col_align == "right":
                self._canvas.drawRightString(col_x, header_y, col_name)
            else:
                self._canvas.drawString(col_x, header_y, col_name)

        self._canvas.setFillColor("#000000")
        self._y = header_y - 20

        # Rows
        row_idx = 0
        for item in line_items:
            self._new_page_if_needed(30)
            row_height = 16

            # Alternating background
            if row_idx % 2 == 1:
                self._canvas.setFillColor("#F8FAFC")
                self._canvas.rect(
                    left, self._y - 4, right - left, row_height, fill=1, stroke=0
                )
                self._canvas.setFillColor("#000000")

            row_data = self._get_row_data(item)
            self._canvas.setFont("Helvetica", 9)
            for i, (_, col_x, col_align) in enumerate(cols):
                value = row_data[i] if i < len(row_data) else ""
                if col_align == "right":
                    self._canvas.drawRightString(col_x, self._y, str(value))
                else:
                    self._canvas.drawString(col_x, self._y, str(value))

            self._y -= row_height
            row_idx += 1

        # Bottom rule
        self._canvas.setStrokeColor(primary)
        self._canvas.setLineWidth(0.5)
        self._canvas.line(left, self._y, right, self._y)
        self._y -= 14

    def _get_column_positions(self):
        """Return list of (name, x_position, alignment) tuples for the table."""
        left = self._margin_left
        w = self._content_width()
        return [
            ("#", left, "left"),
            ("Description", left + w * 0.05, "left"),
            ("Qty", left + w * 0.50, "right"),
            ("Unit Price", left + w * 0.60, "right"),
            ("Discount", left + w * 0.73, "right"),
            ("Tax", left + w * 0.83, "right"),
            ("Total", left + w * 0.93 + w * 0.07, "right"),
        ]

    def _get_row_data(self, item):
        """Return cell values for a line item row."""
        desc = item.product_name or item.custom_description or ""
        return [
            str(item.position),
            desc[:50],
            str(item.quantity),
            self._format_currency(item.unit_price),
            self._format_currency(item.discount_amount) if item.discount_amount else "-",
            self._format_currency(item.tax_amount) if item.tax_amount else "-",
            self._format_currency(item.line_total),
        ]

    def _generate_totals(self):
        """Render totals block (subtotal, discount, tax, grand total)."""
        self._new_page_if_needed(80)
        right = self._page_width - self._margin_right
        primary = self._hex_to_color(self.template.primary_color)
        q = self.quote

        totals = [("Subtotal:", q.subtotal)]
        if q.discount_amount:
            totals.append(("Discount:", f"-{self._format_currency(q.discount_amount)}"))
        if q.tax_amount:
            totals.append(("Tax:", q.tax_amount))

        for label, value in totals:
            formatted = value if isinstance(value, str) else self._format_currency(value)
            self._draw_right_text(right, self._y, formatted, size=10)
            self._draw_right_text(right - 120, self._y, label, font="Helvetica-Bold", size=10)
            self._y -= 16

        # Grand total with highlight
        self._y -= 4
        self._canvas.setStrokeColor(primary)
        self._canvas.setLineWidth(1)
        self._canvas.line(right - 200, self._y + 14, right, self._y + 14)

        self._draw_right_text(
            right, self._y, self._format_currency(q.total),
            font="Helvetica-Bold", size=13, color=primary,
        )
        self._draw_right_text(
            right - 120, self._y, "TOTAL:",
            font="Helvetica-Bold", size=13, color=primary,
        )
        self._y -= 22

    def _generate_notes_section(self):
        """Render customer notes if present."""
        if not self.quote.notes:
            return
        if not self.template.is_section_visible("notes"):
            return

        self._new_page_if_needed(40)
        left = self._margin_left
        self._draw_text(left, self._y, "Notes:", font="Helvetica-Bold", size=10)
        self._y -= 14

        for line in self.quote.notes.split("\n"):
            self._new_page_if_needed(14)
            self._draw_text(left, self._y, line.strip(), size=9)
            self._y -= 12
        self._y -= 6

    def _generate_terms_section(self):
        """Render terms and conditions."""
        tpl = self.template
        if not tpl.show_terms:
            return

        content = self.quote.terms or tpl.terms_and_conditions
        if not content:
            return

        self._new_page_if_needed(40)
        left = self._margin_left
        self._draw_text(
            left, self._y, tpl.terms_title,
            font="Helvetica-Bold", size=10,
        )
        self._y -= 14

        for line in content.split("\n"):
            self._new_page_if_needed(14)
            self._draw_text(left, self._y, line.strip(), size=8)
            self._y -= 11
        self._y -= 6

    def _generate_qr_code(self):
        """Render a QR code linking to the public quote URL."""
        try:
            import qrcode
        except ImportError:
            return  # silently skip if qrcode not installed

        url = self.quote.get_public_url()
        if not url:
            return

        self._new_page_if_needed(80)

        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        from reportlab.lib.utils import ImageReader

        img_reader = ImageReader(img_buffer)
        qr_size = 60
        x = self._page_width - self._margin_right - qr_size
        self._canvas.drawImage(img_reader, x, self._y - qr_size, qr_size, qr_size)
        self._draw_text(
            x, self._y - qr_size - 10,
            "Scan for details", size=7,
        )
        # Don't reduce self._y; QR is drawn alongside other content

    def _generate_signature_section(self):
        """Render signature line if configured."""
        tpl = self.template
        if not tpl.show_signature_line:
            return

        self._new_page_if_needed(60)
        left = self._margin_left
        self._y -= 20

        line_width = 180
        self._canvas.setStrokeColor("#000000")
        self._canvas.setLineWidth(0.5)
        self._canvas.line(left, self._y, left + line_width, self._y)
        self._y -= 12

        self._draw_text(left, self._y, tpl.signature_label, size=8)
        self._y -= 12

        if tpl.authorized_person_name:
            self._draw_text(left, self._y, tpl.authorized_person_name, font="Helvetica-Bold", size=9)
            self._y -= 12
        if tpl.authorized_person_title:
            self._draw_text(left, self._y, tpl.authorized_person_title, size=8)
            self._y -= 12

    def _generate_footer(self):
        """Render footer text at the bottom of each page."""
        tpl = self.template
        if not tpl.show_footer:
            return

        footer_y = self._margin_bottom - 10
        left = self._margin_left
        right = self._page_width - self._margin_right
        center = (left + right) / 2

        # Thank-you message
        if tpl.default_thank_you_message:
            self._draw_text(
                center - len(tpl.default_thank_you_message) * 2,
                footer_y + 20,
                tpl.default_thank_you_message,
                size=9,
            )

        # Validity message
        if tpl.validity_message_template and self.quote.valid_until:
            msg = tpl.validity_message_template.format(
                valid_until=self.quote.valid_until.strftime("%d %b %Y"),
            )
            self._draw_text(
                center - len(msg) * 2,
                footer_y + 8,
                msg,
                size=8,
            )

        # Footer text
        if tpl.footer_text:
            self._canvas.setFont("Helvetica", 7)
            if tpl.footer_alignment == "center":
                self._canvas.drawCentredString(center, footer_y, tpl.footer_text)
            elif tpl.footer_alignment == "right":
                self._canvas.drawRightString(right, footer_y, tpl.footer_text)
            else:
                self._canvas.drawString(left, footer_y, tpl.footer_text)

        # Page number
        page_num = self._canvas.getPageNumber()
        self._canvas.setFont("Helvetica", 7)
        self._canvas.drawRightString(right, footer_y - 10, f"Page {page_num}")
