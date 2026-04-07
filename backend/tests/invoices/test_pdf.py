"""Invoice PDF generation tests."""

import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock

from apps.invoices.constants import InvoiceStatus, InvoiceType
from apps.invoices.models import Invoice, InvoiceLineItem
from apps.invoices.services.pdf_generator import InvoicePDFGenerator

pytestmark = pytest.mark.django_db


@pytest.fixture
def issued_invoice(tenant_context, invoice_data, user):
    """Create an issued invoice with a line item for PDF testing."""
    from apps.invoices.services.invoice_service import InvoiceService

    data = {
        "type": InvoiceType.STANDARD,
        "customer_name": "PDF Test Customer",
        "customer_email": "pdf@example.com",
        "business_name": "PDF Test Business",
        "currency": "LKR",
    }
    line_items = [
        {
            "description": "Widget A",
            "quantity": Decimal("5"),
            "unit_price": Decimal("200.00"),
            "tax_rate": Decimal("12.00"),
            "is_taxable": True,
        },
        {
            "description": "Widget B",
            "quantity": Decimal("2"),
            "unit_price": Decimal("500.00"),
            "tax_rate": Decimal("12.00"),
            "is_taxable": True,
        },
    ]
    invoice = InvoiceService.create_invoice(data, line_items_data=line_items, user=user)
    InvoiceService.issue_invoice(invoice.id, user=user)
    invoice.refresh_from_db()
    return invoice


class TestPDFHTMLRendering:
    """Test HTML rendering for PDF templates."""

    def test_render_preview_returns_html(self, issued_invoice):
        html = InvoicePDFGenerator.render_preview(issued_invoice.id)
        assert isinstance(html, str)
        assert len(html) > 0

    def test_render_preview_contains_invoice_number(self, issued_invoice):
        html = InvoicePDFGenerator.render_preview(issued_invoice.id)
        assert issued_invoice.invoice_number in html

    def test_render_preview_contains_customer(self, issued_invoice):
        html = InvoicePDFGenerator.render_preview(issued_invoice.id)
        assert "PDF Test Customer" in html

    def test_render_preview_contains_business(self, issued_invoice):
        html = InvoicePDFGenerator.render_preview(issued_invoice.id)
        assert "PDF Test Business" in html

    def test_render_preview_contains_line_items(self, issued_invoice):
        html = InvoicePDFGenerator.render_preview(issued_invoice.id)
        assert "Widget A" in html
        assert "Widget B" in html


class TestPDFSectionRenderers:
    """Test individual section rendering methods."""

    def test_render_header(self, issued_invoice):
        html = InvoicePDFGenerator.render_header(issued_invoice)
        assert isinstance(html, str)
        assert issued_invoice.invoice_number in html

    def test_render_billing(self, issued_invoice):
        html = InvoicePDFGenerator.render_billing(issued_invoice)
        assert isinstance(html, str)
        assert "PDF Test Customer" in html

    def test_render_line_items(self, issued_invoice):
        html = InvoicePDFGenerator.render_line_items(issued_invoice)
        assert isinstance(html, str)
        assert "Widget A" in html

    def test_render_tax_summary(self, issued_invoice):
        html = InvoicePDFGenerator.render_tax_summary(issued_invoice)
        assert isinstance(html, str)

    def test_render_footer(self, issued_invoice):
        html = InvoicePDFGenerator.render_footer(issued_invoice)
        assert isinstance(html, str)


class TestPDFGeneration:
    """Test actual PDF generation with WeasyPrint mocked."""

    @patch("apps.invoices.services.pdf_generator.InvoicePDFGenerator._html_to_pdf")
    def test_generate_pdf_stores_file(self, mock_to_pdf, issued_invoice):
        mock_to_pdf.return_value = b"%PDF-1.4 fake pdf content"
        pdf_bytes = InvoicePDFGenerator.generate_pdf(issued_invoice.id)

        assert pdf_bytes == b"%PDF-1.4 fake pdf content"
        issued_invoice.refresh_from_db()
        assert issued_invoice.pdf_file
        assert issued_invoice.pdf_generated_at is not None

    @patch("apps.invoices.services.pdf_generator.InvoicePDFGenerator._html_to_pdf")
    def test_generate_pdf_increments_version(self, mock_to_pdf, issued_invoice):
        mock_to_pdf.return_value = b"%PDF-1.4 fake"
        old_version = issued_invoice.pdf_version

        InvoicePDFGenerator.generate_pdf(issued_invoice.id)
        issued_invoice.refresh_from_db()
        assert issued_invoice.pdf_version == old_version + 1

    @patch("apps.invoices.services.pdf_generator.InvoicePDFGenerator._html_to_pdf")
    def test_generate_pdf_filename(self, mock_to_pdf, issued_invoice):
        mock_to_pdf.return_value = b"%PDF-1.4 fake"
        InvoicePDFGenerator.generate_pdf(issued_invoice.id)
        issued_invoice.refresh_from_db()
        assert issued_invoice.invoice_number in issued_invoice.pdf_file.name


class TestPDFTemplateSelection:
    """Test correct template selection by invoice type."""

    def test_standard_template(self):
        assert InvoicePDFGenerator.TEMPLATE_MAP["STANDARD"] == "invoices/pdf/invoice.html"

    def test_svat_template(self):
        assert InvoicePDFGenerator.TEMPLATE_MAP["SVAT"] == "invoices/pdf/invoice.html"

    def test_credit_note_template(self):
        assert InvoicePDFGenerator.TEMPLATE_MAP["CREDIT_NOTE"] == "invoices/pdf/credit_note.html"

    def test_debit_note_template(self):
        assert InvoicePDFGenerator.TEMPLATE_MAP["DEBIT_NOTE"] == "invoices/pdf/debit_note.html"
