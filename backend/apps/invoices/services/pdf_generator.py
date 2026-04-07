"""
Invoice PDF generator service.
"""

import logging
from io import BytesIO

from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


class InvoicePDFGenerator:
    """Generates PDF invoices from Django templates."""

    TEMPLATE_MAP = {
        "STANDARD": "invoices/pdf/invoice.html",
        "SVAT": "invoices/pdf/invoice.html",
        "CREDIT_NOTE": "invoices/pdf/credit_note.html",
        "DEBIT_NOTE": "invoices/pdf/debit_note.html",
    }

    @classmethod
    def generate_pdf(cls, invoice_id):
        """Generate PDF for an invoice and store it on the model."""
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.select_related(
            "customer", "related_invoice",
        ).prefetch_related("line_items").get(id=invoice_id)

        html_content = cls._render_html(invoice)
        pdf_bytes = cls._html_to_pdf(html_content)

        filename = f"{invoice.invoice_number or invoice.id}.pdf"
        invoice.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
        invoice.pdf_generated_at = timezone.now()
        invoice.pdf_version += 1
        invoice.save(update_fields=["pdf_file", "pdf_generated_at", "pdf_version"])
        logger.info("PDF generated for invoice %s (version %d)", invoice.invoice_number, invoice.pdf_version)
        return pdf_bytes

    # ── Section Renderers ───────────────────────────────────────────

    @classmethod
    def render_header(cls, invoice, template=None):
        """Render the PDF header section as HTML."""
        return render_to_string("invoices/pdf/sections/header.html", {
            "invoice": invoice,
            "template": template,
        })

    @classmethod
    def render_billing(cls, invoice):
        """Render the billing/customer section as HTML."""
        return render_to_string("invoices/pdf/sections/billing.html", {
            "invoice": invoice,
        })

    @classmethod
    def render_line_items(cls, invoice):
        """Render the line items table as HTML."""
        line_items = invoice.line_items.all().order_by("position")
        return render_to_string("invoices/pdf/sections/line_items.html", {
            "invoice": invoice,
            "line_items": line_items,
        })

    @classmethod
    def render_tax_summary(cls, invoice):
        """Render the tax summary section as HTML."""
        return render_to_string("invoices/pdf/sections/tax_summary.html", {
            "invoice": invoice,
        })

    @classmethod
    def render_footer(cls, invoice, template=None):
        """Render the PDF footer section as HTML."""
        return render_to_string("invoices/pdf/sections/footer.html", {
            "invoice": invoice,
            "template": template,
        })

    # ── Internal ────────────────────────────────────────────────────

    @classmethod
    def _render_html(cls, invoice):
        """Render the full invoice HTML from a Django template."""
        template_name = cls.TEMPLATE_MAP.get(invoice.type, cls.TEMPLATE_MAP["STANDARD"])
        line_items = invoice.line_items.all().order_by("position")
        template_settings = cls._get_template_settings(invoice)

        context = {
            "invoice": invoice,
            "line_items": line_items,
            "template": template_settings,
        }
        return render_to_string(template_name, context)

    @classmethod
    def _get_template_settings(cls, invoice):
        """Try to load InvoiceTemplate for the current tenant."""
        try:
            from django.db import connection
            from apps.invoices.models.invoice_template import InvoiceTemplate
            tenant = connection.tenant
            return InvoiceTemplate.objects.filter(tenant=tenant, is_active=True).first()
        except Exception:
            logger.debug("Could not load invoice template settings", exc_info=True)
            return None

    @classmethod
    def _html_to_pdf(cls, html_content):
        """Convert HTML string to PDF bytes using WeasyPrint."""
        try:
            from weasyprint import HTML
            return HTML(string=html_content).write_pdf()
        except ImportError:
            logger.error("WeasyPrint is not installed. Cannot generate PDF.")
            raise RuntimeError(
                "WeasyPrint is required for PDF generation. "
                "Install it with: pip install weasyprint"
            )

    @classmethod
    def render_preview(cls, invoice_id):
        """Return rendered HTML for browser preview (no PDF conversion)."""
        from apps.invoices.models import Invoice

        invoice = Invoice.objects.select_related(
            "customer", "related_invoice",
        ).prefetch_related("line_items").get(id=invoice_id)
        return cls._render_html(invoice)
