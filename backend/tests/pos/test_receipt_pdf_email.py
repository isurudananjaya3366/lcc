"""
Task 81: PDF Generator & Email Service Tests.

Tests for PDFGeneratorService, ReceiptEmailService,
ReceiptVerificationService, and ReceiptSMSService.
"""

import pytest
from unittest.mock import MagicMock, patch

from apps.pos.receipts.services.pdf_generator import PDFGeneratorService
from apps.pos.receipts.services.email_service import ReceiptEmailService
from apps.pos.receipts.services.verification import ReceiptVerificationService
from apps.pos.receipts.services.sms_service import ReceiptSMSService

pytestmark = pytest.mark.django_db


# ── PDF Generator ─────────────────────────────────────────────


class TestPDFGeneratorService:
    """Test PDF generation from receipt data."""

    def test_init_with_receipt(self, receipt):
        service = PDFGeneratorService(receipt=receipt)
        assert service.receipt == receipt

    def test_generate_html(self, receipt):
        service = PDFGeneratorService(receipt=receipt)
        html = service.generate_html()
        assert isinstance(html, str)
        assert len(html) > 0

    def test_generate_html_contains_receipt_number(self, receipt):
        service = PDFGeneratorService(receipt=receipt)
        html = service.generate_html()
        assert receipt.receipt_number in html

    def test_generate_html_contains_business_name(self, receipt):
        service = PDFGeneratorService(receipt=receipt)
        html = service.generate_html()
        header = receipt.receipt_data.get("header", {})
        business_name = header.get("business_name", "")
        if business_name:
            assert business_name in html

    def test_generate_pdf_returns_bytes(self, receipt):
        """PDF generation returns bytes (HTML fallback if WeasyPrint unavailable)."""
        service = PDFGeneratorService(receipt=receipt)
        result = service.generate_pdf()
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_build_context(self, receipt):
        service = PDFGeneratorService(receipt=receipt)
        ctx = service._build_context()
        assert isinstance(ctx, dict)
        assert "header" in ctx or "receipt_data" in ctx or "totals" in ctx

    def test_get_metadata(self, receipt):
        service = PDFGeneratorService(receipt=receipt)
        meta = service.get_metadata()
        assert isinstance(meta, dict)
        assert "title" in meta

    def test_get_cache_key(self, receipt):
        key = PDFGeneratorService.get_cache_key(
            receipt_id=str(receipt.pk)
        )
        assert isinstance(key, str)
        assert len(key) > 0


# ── Email Service ─────────────────────────────────────────────


class TestReceiptEmailService:
    """Test receipt email delivery."""

    def test_init_with_receipt(self, receipt):
        service = ReceiptEmailService(receipt=receipt)
        assert service.receipt == receipt

    def test_build_email_context(self, receipt):
        service = ReceiptEmailService(receipt=receipt)
        ctx = service._build_email_context()
        assert isinstance(ctx, dict)

    @patch("apps.pos.receipts.services.email_service.EmailMultiAlternatives")
    def test_send_email_calls_send(self, mock_email_cls, receipt):
        """Email service constructs and sends email."""
        mock_email = MagicMock()
        mock_email_cls.return_value = mock_email

        service = ReceiptEmailService(receipt=receipt)
        service.send_email(recipient_email="customer@test.com")

        mock_email.send.assert_called_once()

    @patch("apps.pos.receipts.services.email_service.EmailMultiAlternatives")
    def test_send_email_with_custom_message(
        self, mock_email_cls, receipt
    ):
        mock_email = MagicMock()
        mock_email_cls.return_value = mock_email

        service = ReceiptEmailService(receipt=receipt)
        service.send_email(
            recipient_email="customer@test.com",
            custom_message="Thank you for your purchase!",
        )
        mock_email.send.assert_called_once()

    @patch("apps.pos.receipts.services.email_service.EmailMultiAlternatives")
    def test_send_email_with_cc(self, mock_email_cls, receipt):
        mock_email = MagicMock()
        mock_email_cls.return_value = mock_email

        service = ReceiptEmailService(receipt=receipt)
        service.send_email(
            recipient_email="customer@test.com",
            cc_emails=["manager@test.com"],
        )
        mock_email.send.assert_called_once()


# ── Verification Service ──────────────────────────────────────


class TestReceiptVerificationService:
    """Test receipt hash generation and verification."""

    def test_generate_hash_returns_string(self, receipt):
        hash_val = ReceiptVerificationService.generate_hash(receipt)
        assert isinstance(hash_val, str)
        assert len(hash_val) > 0

    def test_generate_hash_consistent(self, receipt):
        """Same receipt produces same hash."""
        h1 = ReceiptVerificationService.generate_hash(receipt)
        h2 = ReceiptVerificationService.generate_hash(receipt)
        assert h1 == h2

    def test_generate_token_returns_16_chars(self, receipt):
        token = ReceiptVerificationService.generate_token(receipt)
        assert isinstance(token, str)
        assert len(token) == 16

    def test_verify_with_valid_token(self, receipt):
        token = ReceiptVerificationService.generate_token(receipt)
        assert ReceiptVerificationService.verify(receipt, token) is True

    def test_verify_with_invalid_token(self, receipt):
        assert (
            ReceiptVerificationService.verify(receipt, "invalidtoken1234")
            is False
        )

    def test_generate_verification_url(self, receipt):
        url = ReceiptVerificationService.generate_verification_url(
            receipt, base_url="https://store.example.com"
        )
        assert isinstance(url, str)
        assert "https://store.example.com" in url
        assert str(receipt.id) in url
        assert "token=" in url


# ── SMS Service ───────────────────────────────────────────────


class TestReceiptSMSService:
    """Test SMS service stub."""

    def test_init_with_receipt(self, receipt):
        service = ReceiptSMSService(receipt_data=receipt.receipt_data)
        assert service.data == receipt.receipt_data

    def test_send_sms_returns_bool(self, receipt):
        """SMS send returns bool (stub behaviour)."""
        service = ReceiptSMSService(receipt_data=receipt.receipt_data)
        result = service.send_sms(
            phone_number="+94771234567",
            short_url="https://store.example.com/r/abc",
        )
        assert isinstance(result, bool)
