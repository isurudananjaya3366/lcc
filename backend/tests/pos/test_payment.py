"""
Tests for PaymentService: cash, card, mobile, store credit payments,
split payments, transaction completion, voiding, and validation.
"""

from decimal import Decimal

import pytest

from apps.pos.constants import (
    CART_STATUS_ACTIVE,
    CART_STATUS_COMPLETED,
    PAYMENT_METHOD_CARD,
    PAYMENT_METHOD_CASH,
    PAYMENT_STATUS_COMPLETED,
    PAYMENT_STATUS_VOIDED,
)

pytestmark = pytest.mark.django_db


def _make_service(cart, user):
    """Shortcut to create PaymentService."""
    from apps.pos.payment.services.payment_service import PaymentService

    return PaymentService(cart=cart, user=user)


# ── Cash Payment ─────────────────────────────────────────────────────


class TestCashPayment:
    def test_cash_exact_amount(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        total = cart_with_items.grand_total
        payment = svc.process_cash_payment(amount_tendered=total)
        assert payment.status == PAYMENT_STATUS_COMPLETED
        assert payment.change_due == Decimal("0.00")
        assert payment.amount == total

    def test_cash_overpayment_returns_change(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        total = cart_with_items.grand_total
        payment = svc.process_cash_payment(amount_tendered=total + Decimal("500.00"))
        assert payment.change_due == Decimal("500.00")

    def test_cash_insufficient_raises(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        with pytest.raises(ValueError, match="Insufficient cash"):
            svc.process_cash_payment(amount_tendered=Decimal("1.00"))

    def test_cash_zero_amount_raises(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        with pytest.raises(ValueError, match="positive"):
            svc.process_cash_payment(amount_tendered=Decimal("0.00"))

    def test_cash_creates_payment_record(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        payment = svc.process_cash_payment(
            amount_tendered=cart_with_items.grand_total
        )
        assert payment.pk is not None
        assert payment.cart == cart_with_items
        assert payment.method == PAYMENT_METHOD_CASH
        assert payment.processed_by == cashier

    def test_cash_records_paid_at(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        payment = svc.process_cash_payment(
            amount_tendered=cart_with_items.grand_total
        )
        assert payment.paid_at is not None


# ── Card Payment ─────────────────────────────────────────────────────


class TestCardPayment:
    def test_card_payment_success(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        payment = svc.process_card_payment(
            cart_with_items.grand_total,
            authorization_code="AUTH123",
            reference_number="REF456",
        )
        assert payment.status == PAYMENT_STATUS_COMPLETED
        assert payment.method == PAYMENT_METHOD_CARD

    def test_card_stores_auth_code(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        payment = svc.process_card_payment(
            cart_with_items.grand_total,
            authorization_code="AUTH-XYZ",
        )
        assert payment.authorization_code == "AUTH-XYZ"

    def test_card_stores_reference(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        payment = svc.process_card_payment(
            cart_with_items.grand_total,
            reference_number="TXN-789",
        )
        assert payment.reference_number == "TXN-789"

    def test_card_exceeds_remaining_raises(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        with pytest.raises(ValueError, match="exceeds remaining"):
            svc.process_card_payment(Decimal("999999.00"))

    def test_card_zero_amount_raises(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        with pytest.raises(ValueError, match="positive"):
            svc.process_card_payment(Decimal("0.00"))


# ── Mobile Payment ───────────────────────────────────────────────────


class TestMobilePayment:
    def test_mobile_payment_success(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        payment = svc.process_mobile_payment(
            cart_with_items.grand_total,
            reference_number="MOB-001",
            method="mobile_frimi",
        )
        assert payment.status == PAYMENT_STATUS_COMPLETED
        assert payment.method == "mobile_frimi"

    def test_mobile_stores_reference(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        payment = svc.process_mobile_payment(
            cart_with_items.grand_total,
            reference_number="GENIE-123",
        )
        assert payment.reference_number == "GENIE-123"

    def test_mobile_exceeds_remaining_raises(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        with pytest.raises(ValueError, match="exceeds remaining"):
            svc.process_mobile_payment(Decimal("999999.00"))


# ── Store Credit ─────────────────────────────────────────────────────


class TestStoreCreditPayment:
    def test_store_credit_no_customer_raises(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        with pytest.raises(ValueError, match="no customer"):
            svc.process_store_credit(Decimal("100.00"))

    def test_store_credit_with_customer(self, session, customer, product, cashier):
        from apps.pos.cart.services.cart_service import CartService

        cart = CartService.get_or_create_cart(session, customer=customer)
        CartService.add_to_cart(cart, product, quantity=1)
        cart.refresh_from_db()

        svc = _make_service(cart, cashier)
        payment = svc.process_store_credit(cart.grand_total)
        assert payment.status == PAYMENT_STATUS_COMPLETED


# ── Split Payment ────────────────────────────────────────────────────


class TestSplitPayment:
    def test_split_cash_and_card(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        total = cart_with_items.grand_total
        half = total / 2

        payments = svc.split_payment([
            {"method": "cash", "amount": half, "amount_tendered": half},
            {"method": "card", "amount": total - half},
        ])
        assert len(payments) == 2
        assert svc.can_complete_cart()

    def test_split_creates_multiple_records(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        total = cart_with_items.grand_total
        third = (total / 3).quantize(Decimal("0.01"))
        remainder = total - third - third

        payments = svc.split_payment([
            {"method": "cash", "amount": third, "amount_tendered": third},
            {"method": "card", "amount": third},
            {"method": "mobile_frimi", "amount": remainder},
        ])
        assert len(payments) == 3


# ── Remaining Amount & Completion ────────────────────────────────────


class TestTransactionCompletion:
    def test_remaining_amount_before_payment(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        assert svc.get_remaining_amount() == cart_with_items.grand_total

    def test_remaining_after_partial_payment(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        partial = Decimal("50.00")
        svc.process_card_payment(partial)
        assert svc.get_remaining_amount() == cart_with_items.grand_total - partial

    def test_can_complete_after_full_payment(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        svc.process_cash_payment(cart_with_items.grand_total)
        assert svc.can_complete_cart()

    def test_complete_transaction_success(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        svc.process_cash_payment(cart_with_items.grand_total)
        result = svc.complete_transaction()
        cart_with_items.refresh_from_db()
        assert cart_with_items.status == CART_STATUS_COMPLETED
        assert cart_with_items.completed_at is not None
        assert "receipt_data" in result

    def test_complete_updates_session_totals(self, cart_with_items, cashier, session):
        svc = _make_service(cart_with_items, cashier)
        svc.process_cash_payment(cart_with_items.grand_total)
        svc.complete_transaction()
        session.refresh_from_db()
        assert session.transaction_count == 1
        assert session.total_sales == cart_with_items.grand_total

    def test_complete_without_payment_raises(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        with pytest.raises(ValueError, match="outstanding balance"):
            svc.complete_transaction()


# ── Void Transaction ─────────────────────────────────────────────────


class TestVoidTransaction:
    def test_void_active_cart_with_payments(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        svc.process_card_payment(Decimal("50.00"))
        voided_cart = svc.void_transaction(reason="Customer cancelled")
        assert voided_cart.status == "voided"

    def test_void_marks_payments_voided(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        svc.process_card_payment(Decimal("50.00"))
        svc.void_transaction()
        for p in cart_with_items.payments.all():
            assert p.status == PAYMENT_STATUS_VOIDED

    def test_void_records_reason(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        svc.void_transaction(reason="Test void")
        cart_with_items.refresh_from_db()
        assert "Test void" in cart_with_items.notes


# ── Service Validation ───────────────────────────────────────────────


class TestPaymentServiceValidation:
    def test_service_requires_cart(self, cashier):
        from apps.pos.payment.services.payment_service import PaymentService

        with pytest.raises(ValueError, match="Cart is required"):
            PaymentService(cart=None, user=cashier)

    def test_service_requires_active_cart(self, cart, cashier):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService

        CartService.void_cart(cart)
        with pytest.raises(ValueError, match="ACTIVE"):
            PaymentService(cart=cart, user=cashier)

    def test_service_requires_items_in_cart(self, cart, cashier):
        from apps.pos.payment.services.payment_service import PaymentService

        with pytest.raises(ValueError, match="no items"):
            PaymentService(cart=cart, user=cashier)


# ── Receipt Data ─────────────────────────────────────────────────────


class TestReceiptData:
    def test_receipt_data_structure(self, cart_with_items, cashier):
        svc = _make_service(cart_with_items, cashier)
        svc.process_cash_payment(cart_with_items.grand_total)
        result = svc.complete_transaction()
        receipt = result["receipt_data"]
        assert "terminal_name" in receipt
        assert "terminal_code" in receipt
        assert "reference_number" in receipt
        assert "items" in receipt
        assert "payments" in receipt
