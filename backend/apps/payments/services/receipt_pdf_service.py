"""Receipt PDF generation service using ReportLab."""

import io
import logging

from django.core.files.base import ContentFile
from django.utils import timezone

from apps.payments.utils.pdf_utils import (
    CONTENT_WIDTH,
    DARK_COLOR,
    LIGHT_COLOR,
    MARGIN_BOTTOM,
    MARGIN_LEFT,
    MARGIN_TOP,
    PAGE_HEIGHT,
    PAGE_WIDTH,
    PRIMARY_COLOR,
    format_currency,
    get_company_setting,
)

logger = logging.getLogger(__name__)


class ReceiptPDFService:
    """Service for generating payment receipt PDFs using ReportLab."""

    @staticmethod
    def generate_receipt_pdf(receipt):
        """
        Generate a PDF for the given receipt and save it to the receipt's pdf_file field.

        Args:
            receipt: PaymentReceipt instance.

        Returns:
            PaymentReceipt instance with pdf_file set.
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.pdfgen import canvas
        except ImportError:
            logger.warning("ReportLab not installed. Skipping PDF generation.")
            return receipt

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setTitle(f"Payment Receipt - {receipt.receipt_number}")

        y = PAGE_HEIGHT - MARGIN_TOP

        y = ReceiptPDFService._build_header(c, receipt, y)
        y = ReceiptPDFService._build_customer_info(c, receipt, y)
        y = ReceiptPDFService._build_payment_details(c, receipt, y)
        if receipt.invoice:
            y = ReceiptPDFService._build_invoice_reference(c, receipt, y)
        ReceiptPDFService._build_footer(c, receipt, y)

        c.save()
        buffer.seek(0)

        filename = f"{receipt.receipt_number}.pdf"
        receipt.pdf_file.save(filename, ContentFile(buffer.read()), save=False)
        receipt.pdf_generated_at = timezone.now()
        receipt.save(update_fields=["pdf_file", "pdf_generated_at", "updated_on"])

        return receipt

    @staticmethod
    def _build_header(c, receipt, y):
        """Render the header section with company name and receipt info."""
        # Company name
        c.setFont("Helvetica-Bold", 18)
        c.setFillColorRGB(*PRIMARY_COLOR)
        company_name = get_company_setting("COMPANY_NAME")
        c.drawString(MARGIN_LEFT, y, company_name)
        y -= 18

        # Company address
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(*DARK_COLOR)
        company_address = get_company_setting("COMPANY_ADDRESS")
        c.drawString(MARGIN_LEFT, y, company_address)
        y -= 12

        company_contact = get_company_setting("COMPANY_CONTACT")
        c.drawString(MARGIN_LEFT, y, company_contact)
        y -= 25

        # Receipt title
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(*PRIMARY_COLOR)
        c.drawString(MARGIN_LEFT, y, "PAYMENT RECEIPT")
        y -= 20

        # Receipt number and date
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(*DARK_COLOR)
        c.drawString(MARGIN_LEFT, y, f"Receipt #: {receipt.receipt_number}")
        date_str = receipt.receipt_date.strftime("%d %B %Y") if receipt.receipt_date else ""
        c.drawRightString(PAGE_WIDTH - MARGIN_LEFT, y, f"Date: {date_str}")
        y -= 15

        # Separator line
        c.setStrokeColorRGB(*PRIMARY_COLOR)
        c.setLineWidth(1)
        c.line(MARGIN_LEFT, y, PAGE_WIDTH - MARGIN_LEFT, y)
        y -= 20

        return y

    @staticmethod
    def _build_customer_info(c, receipt, y):
        """Render customer information section."""
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(*DARK_COLOR)
        c.drawString(MARGIN_LEFT, y, "BILL TO:")
        y -= 16

        c.setFont("Helvetica", 10)
        customer = receipt.customer
        if customer:
            name = getattr(customer, "company_name", "") or str(customer)
            c.drawString(MARGIN_LEFT, y, name)
            y -= 14

            address = getattr(customer, "address", "")
            if address:
                c.drawString(MARGIN_LEFT, y, str(address))
                y -= 14

            phone = getattr(customer, "phone", "")
            if phone:
                c.drawString(MARGIN_LEFT, y, f"Phone: {phone}")
                y -= 14

            email = getattr(customer, "email", "")
            if email:
                c.drawString(MARGIN_LEFT, y, f"Email: {email}")
                y -= 14

        y -= 10
        return y

    @staticmethod
    def _build_payment_details(c, receipt, y):
        """Render payment details section."""
        # Section background
        c.setFillColorRGB(*LIGHT_COLOR)
        c.rect(MARGIN_LEFT, y - 80, CONTENT_WIDTH, 90, fill=True, stroke=False)

        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(*DARK_COLOR)
        c.drawString(MARGIN_LEFT + 10, y, "PAYMENT DETAILS")
        y -= 18

        c.setFont("Helvetica", 10)
        details = [
            ("Amount", format_currency(receipt.receipt_amount, receipt.currency)),
            ("Payment Method", receipt.get_display_method()),
            ("Payment Date", receipt.receipt_date.strftime("%d %B %Y") if receipt.receipt_date else "N/A"),
        ]

        if receipt.reference_number:
            details.append(("Reference", receipt.reference_number))

        if receipt.exchange_rate:
            details.append(("Exchange Rate", str(receipt.exchange_rate)))

        for label, value in details:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(MARGIN_LEFT + 10, y, f"{label}:")
            c.setFont("Helvetica", 10)
            c.drawString(MARGIN_LEFT + 150, y, value)
            y -= 16

        y -= 15
        return y

    @staticmethod
    def _build_invoice_reference(c, receipt, y):
        """Render invoice reference if applicable."""
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(*DARK_COLOR)
        c.drawString(MARGIN_LEFT, y, "INVOICE REFERENCE")
        y -= 18

        c.setFont("Helvetica", 10)
        invoice = receipt.invoice
        if invoice:
            invoice_number = getattr(invoice, "invoice_number", str(invoice))
            c.drawString(MARGIN_LEFT + 10, y, f"Invoice #: {invoice_number}")
            y -= 16

            total = getattr(invoice, "total", None)
            if total is not None:
                c.drawString(MARGIN_LEFT + 10, y, f"Invoice Total: {format_currency(total, receipt.currency)}")
                y -= 16

            balance = getattr(invoice, "balance_due", None)
            if balance is not None:
                c.drawString(MARGIN_LEFT + 10, y, f"Balance Due: {format_currency(balance, receipt.currency)}")
                y -= 16

        y -= 15
        return y

    @staticmethod
    def _build_footer(c, receipt, y):
        """Render footer with thank-you message and company details."""
        # Thank you message
        footer_y = MARGIN_BOTTOM + 80
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(*PRIMARY_COLOR)
        thank_you = get_company_setting("RECEIPT_THANK_YOU_MESSAGE")
        c.drawCentredString(PAGE_WIDTH / 2, footer_y, thank_you)
        footer_y -= 18

        # Registration info
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(*DARK_COLOR)
        reg = get_company_setting("COMPANY_REGISTRATION")
        if reg:
            c.drawCentredString(PAGE_WIDTH / 2, footer_y, f"Registration: {reg}")
            footer_y -= 12

        vat = get_company_setting("COMPANY_VAT_NUMBER")
        if vat:
            c.drawCentredString(PAGE_WIDTH / 2, footer_y, f"VAT: {vat}")
            footer_y -= 12

        # Footer message
        footer_msg = get_company_setting("RECEIPT_FOOTER_MESSAGE")
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(PAGE_WIDTH / 2, footer_y, footer_msg)
