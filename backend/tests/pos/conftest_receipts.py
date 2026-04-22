"""
Receipt module test fixtures.

Provides conftest-level fixtures for receipt builder, thermal printer,
PDF generator, and email service tests.
"""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from apps.pos.receipts.models import Receipt, ReceiptTemplate


@pytest.fixture
def receipt_template(tenant_context):
    """Default receipt template with standard settings."""
    return ReceiptTemplate.objects.create(
        name="Standard Receipt",
        paper_size="80mm",
        is_default=True,
        description="Standard 80mm thermal receipt",
        show_logo=True,
        show_business_name=True,
        business_name_override="Test Store",
        header_line_1="123 Test Street",
        header_line_2="Colombo 07, Sri Lanka",
        header_line_3="Tel: +94 11 234 5678",
        show_sku=True,
        show_discount_per_item=True,
        show_subtotal=True,
        show_tax_breakdown=True,
        show_total_discount=True,
        show_payment_method=True,
        show_amount_tendered=True,
        show_change_given=True,
        footer_line_1="Thank you for your purchase!",
        footer_line_2="Visit again soon.",
        show_qr_code=True,
        qr_content_type="TRANSACTION_ID",
    )


@pytest.fixture
def receipt_template_58mm(tenant_context):
    """58mm narrow receipt template."""
    return ReceiptTemplate.objects.create(
        name="Narrow Receipt",
        paper_size="58mm",
        is_default=False,
        description="Compact 58mm thermal receipt",
        show_logo=False,
        show_business_name=True,
        business_name_override="Test Store",
        show_sku=False,
        show_qr_code=False,
    )


@pytest.fixture
def completed_cart(session, product, product2):
    """A completed cart with items and payment for receipt generation."""
    from apps.pos.cart.services import CartService
    from apps.pos.payment.services import PaymentService

    cart = CartService.get_or_create_cart(session)
    CartService.add_to_cart(cart, product, quantity=2)
    CartService.add_to_cart(cart, product2, quantity=1)

    svc = PaymentService(cart=cart, user=session.user)
    svc.process_cash_payment(amount_tendered=cart.grand_total + Decimal("100.00"))
    svc.complete_transaction()

    cart.refresh_from_db()
    return cart


@pytest.fixture
def receipt(completed_cart, receipt_template):
    """A generated receipt record."""
    from apps.pos.receipts.services import ReceiptBuilder, ReceiptNumberGenerator

    builder = ReceiptBuilder(cart=completed_cart, template=receipt_template)
    receipt_data = builder.build()

    # Use the same number the builder generated internally (avoids a duplicate generate)
    receipt_number = builder._receipt_number or ReceiptNumberGenerator().generate()

    return Receipt.objects.create(
        receipt_number=receipt_number,
        cart=completed_cart,
        receipt_type="SALE",
        template=receipt_template,
        generated_at=completed_cart.completed_at,
        receipt_data=receipt_data,
        generated_by=completed_cart.session.user,
    )


@pytest.fixture
def sample_receipt_data():
    """Pre-built receipt data dict for unit tests that don't need DB."""
    return {
        "header": {
            "business_name": "Test Store",
            "header_lines": [
                "123 Test Street",
                "Colombo 07, Sri Lanka",
                "Tel: +94 11 234 5678",
            ],
            "duplicate_marker": False,
        },
        "transaction": {
            "receipt_number": "REC-20240101-00001",
            "date": "2024-01-01",
            "time": "14:30:00",
            "operator": "Test Cashier",
            "terminal": "T001",
        },
        "items": [
            {
                "name": "Coca Cola 330ml",
                "sku": "COKE-330",
                "quantity": "2.000",
                "quantity_display": "2",
                "unit_price": "Rs. 150.00",
                "line_total": "Rs. 300.00",
                "line_total_display": "Rs. 300.00",
            },
            {
                "name": "Pepsi 500ml",
                "sku": "PEPSI-500",
                "quantity": "1.000",
                "quantity_display": "1",
                "unit_price": "Rs. 200.00",
                "line_total": "Rs. 200.00",
                "line_total_display": "Rs. 200.00",
            },
        ],
        "totals": {
            "subtotal": "Rs. 500.00",
            "subtotal_display": "Rs. 500.00",
            "discount_total": "Rs. 0.00",
            "discount_display": "Rs. 0.00",
            "tax_total": "Rs. 0.00",
            "grand_total": "Rs. 500.00",
            "grand_total_display": "Rs. 500.00",
            "item_count": 3,
        },
        "payments": [
            {
                "method": "Cash",
                "amount": "Rs. 500.00",
                "tendered": "Rs. 600.00",
                "change": "Rs. 100.00",
            },
        ],
        "footer": {
            "footer_lines": [
                "Thank you for your purchase!",
                "Visit again soon.",
            ],
            "return_policy": "Items may be returned within 7 days.",
        },
        "qr_code": {
            "content": "REC-20240101-00001",
            "label": "Scan to verify",
        },
    }
