"""
Task 79: Receipt Builder Tests.

Tests for ReceiptBuilder service including header, items, totals,
payments, footer, QR code, and template application.
"""

import pytest
from decimal import Decimal

from apps.pos.receipts.services.builder import ReceiptBuilder
from apps.pos.receipts.services.exceptions import (
    CartValidationError,
    ReceiptBuildError,
)

pytestmark = pytest.mark.django_db


# ── Builder Initialization ────────────────────────────────────


class TestReceiptBuilderInit:
    """Test ReceiptBuilder initialisation."""

    def test_builder_init_with_cart_and_template(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        assert builder.cart == completed_cart
        assert builder.template == receipt_template

    def test_builder_init_without_template(self, completed_cart):
        builder = ReceiptBuilder(cart=completed_cart, template=None)
        assert builder.template is None


# ── Cart Validation ───────────────────────────────────────────


class TestCartValidation:
    """Test that builder validates cart status."""

    def test_validate_completed_cart_passes(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        # Should not raise
        builder.validate_cart()

    def test_validate_active_cart_raises(self, cart, receipt_template):
        """Active (non-completed) cart should be rejected."""
        builder = ReceiptBuilder(cart=cart, template=receipt_template)
        with pytest.raises(CartValidationError):
            builder.validate_cart()


# ── Full Build ────────────────────────────────────────────────


class TestReceiptBuild:
    """Test the complete build() output."""

    def test_build_returns_dict(self, completed_cart, receipt_template):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()
        assert isinstance(result, dict)

    def test_build_contains_required_sections(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()

        assert "header" in result
        assert "transaction" in result
        assert "items" in result
        assert "totals" in result
        assert "payments" in result
        assert "footer" in result

    def test_build_header_has_business_name(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()
        header = result["header"]
        assert "business_name" in header
        assert header["business_name"] == "Test Store"

    def test_build_items_match_cart(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()
        items = result["items"]
        # The cart has 2 products (COKE-330 × 2, PEPSI-500 × 1)
        assert len(items) >= 2

    def test_build_items_have_required_fields(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()
        items = result["items"]
        for item in items:
            assert "name" in item
            assert "quantity" in item
            assert "line_total" in item

    def test_build_totals_has_grand_total(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()
        totals = result["totals"]
        assert "grand_total" in totals

    def test_build_payments_not_empty(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()
        payments = result["payments"]
        assert len(payments) >= 1

    def test_build_payment_has_method(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()
        for payment in result["payments"]:
            assert "method" in payment
            assert "amount" in payment

    def test_build_footer_has_lines(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()
        footer = result["footer"]
        assert "footer_lines" in footer

    def test_build_transaction_has_receipt_info(
        self, completed_cart, receipt_template
    ):
        builder = ReceiptBuilder(
            cart=completed_cart, template=receipt_template
        )
        result = builder.build()
        txn = result["transaction"]
        assert "date" in txn
        assert "time" in txn


# ── Receipt Number Generation ─────────────────────────────────


class TestReceiptNumberGenerator:
    """Test receipt number format and uniqueness."""

    def test_generate_returns_string(self, tenant_context):
        from apps.pos.receipts.services import ReceiptNumberGenerator

        gen = ReceiptNumberGenerator()
        number = gen.generate()
        assert isinstance(number, str)

    def test_generate_follows_format(self, tenant_context):
        from apps.pos.receipts.services import ReceiptNumberGenerator

        gen = ReceiptNumberGenerator()
        number = gen.generate()
        # Format: REC-YYYYMMDD-NNNNN
        assert number.startswith("REC-")
        parts = number.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 8  # date part
        assert len(parts[2]) == 5  # sequence part

    def test_generate_unique_numbers(self, tenant_context):
        from apps.pos.receipts.services import ReceiptNumberGenerator

        gen = ReceiptNumberGenerator()
        numbers = {gen.generate() for _ in range(5)}
        assert len(numbers) == 5  # all unique


# ── Receipt Model ─────────────────────────────────────────────


class TestReceiptModel:
    """Test Receipt model methods."""

    def test_receipt_str(self, receipt):
        assert receipt.receipt_number in str(receipt)
        assert "SALE" in str(receipt)

    def test_mark_as_printed(self, receipt):
        assert receipt.printed_at is None
        receipt.mark_as_printed()
        receipt.refresh_from_db()
        assert receipt.printed_at is not None
        assert receipt.was_printed is True

    def test_mark_as_emailed(self, receipt):
        assert receipt.emailed_at is None
        receipt.mark_as_emailed()
        receipt.refresh_from_db()
        assert receipt.emailed_at is not None
        assert receipt.was_emailed is True

    def test_is_sale(self, receipt):
        assert receipt.is_sale() is True
        assert receipt.is_refund() is False
        assert receipt.is_void() is False

    def test_watermark_sale_is_none(self, receipt):
        assert receipt.get_watermark_text() is None

    def test_receipt_data_accessors(self, receipt):
        assert isinstance(receipt.get_header_data(), dict)
        assert isinstance(receipt.get_items_data(), list)
        assert isinstance(receipt.get_totals_data(), dict)
        assert isinstance(receipt.get_payments_data(), list)


# ── Duplicate Receipt ─────────────────────────────────────────


class TestDuplicateReceipt:
    """Test duplicate receipt generation."""

    def test_generate_duplicate(self, receipt):
        duplicate = receipt.generate_duplicate(
            requested_by=receipt.generated_by
        )
        assert duplicate.pk is not None
        assert duplicate.receipt_type == "DUPLICATE"
        assert duplicate.original_receipt == receipt

    def test_duplicate_increments_reprint_count(self, receipt):
        assert receipt.reprint_count == 0
        receipt.generate_duplicate()
        receipt.refresh_from_db()
        assert receipt.reprint_count == 1

    def test_duplicate_preserves_data(self, receipt):
        duplicate = receipt.generate_duplicate()
        assert duplicate.receipt_data.get("is_duplicate") is True
        assert (
            duplicate.receipt_data.get("original_receipt_number")
            == receipt.receipt_number
        )

    def test_cannot_duplicate_a_duplicate(self, receipt):
        from django.core.exceptions import ValidationError

        duplicate = receipt.generate_duplicate()
        with pytest.raises(ValidationError):
            duplicate.generate_duplicate()

    def test_cannot_duplicate_voided(self, receipt):
        from django.core.exceptions import ValidationError

        receipt.receipt_type = "VOID"
        receipt.save(update_fields=["receipt_type"])
        with pytest.raises(ValidationError):
            receipt.generate_duplicate()


# ── Template Model ────────────────────────────────────────────


class TestReceiptTemplateModel:
    """Test ReceiptTemplate model features."""

    def test_template_str(self, receipt_template):
        assert "Standard Receipt" in str(receipt_template)

    def test_get_default_template(self, receipt_template):
        default = ReceiptTemplate.objects.get_default()
        assert default is not None
        assert default.is_default is True

    def test_clone_template(self, receipt_template):
        clone = receipt_template.clone_template("Cloned Template")
        assert clone.pk is not None
        assert clone.name == "Cloned Template"
        assert clone.is_default is False
        assert clone.paper_size == receipt_template.paper_size

    def test_get_effective_value(self, receipt_template):
        val = receipt_template.get_effective_value("paper_size")
        assert val == "80mm"

    def test_template_inheritance(self, receipt_template, tenant_context):
        child = ReceiptTemplate.objects.create(
            name="Child Template",
            parent_template=receipt_template,
            inherits_from_parent=True,
            paper_size="58mm",
        )
        # Paper size is overridden
        assert child.get_effective_value("paper_size") == "58mm"
        # Business name inherited from parent
        assert (
            child.get_effective_value("business_name_override")
            == "Test Store"
        )


from apps.pos.receipts.models import ReceiptTemplate
