"""
End-to-end transaction flow tests: complete sale lifecycle, held cart workflow,
void scenarios, session totals aggregation, and multi-transaction sessions.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.pos.constants import (
    CART_STATUS_ACTIVE,
    CART_STATUS_COMPLETED,
    CART_STATUS_HELD,
    CART_STATUS_VOIDED,
    DISCOUNT_TYPE_PERCENT,
    SESSION_STATUS_CLOSED,
    SESSION_STATUS_OPEN,
)

pytestmark = pytest.mark.django_db


# ── Complete Transaction Flow ────────────────────────────────────────


class TestCompleteTransactionFlow:
    """Test the full lifecycle: session → cart → items → discount → payment → complete."""

    def test_end_to_end_cash_sale(
        self, session, product, product2, cashier
    ):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService

        # 1. Create cart
        cart = CartService.get_or_create_cart(session)
        assert cart.status == CART_STATUS_ACTIVE

        # 2. Add items
        CartService.add_to_cart(cart, product, quantity=2)
        CartService.add_to_cart(cart, product2, quantity=1)
        cart.refresh_from_db()
        assert cart.items.count() == 2

        # 3. Apply cart discount
        CartService.apply_cart_discount(
            cart, DISCOUNT_TYPE_PERCENT, Decimal("5")
        )
        cart.refresh_from_db()
        assert cart.cart_discount_amount > Decimal("0.00")

        # 4. Process payment
        svc = PaymentService(cart=cart, user=cashier)
        svc.process_cash_payment(amount_tendered=cart.grand_total + Decimal("100"))
        assert svc.can_complete_cart()

        # 5. Complete
        result = svc.complete_transaction()
        cart.refresh_from_db()
        assert cart.status == CART_STATUS_COMPLETED
        assert cart.completed_at is not None
        assert "receipt_data" in result

    def test_end_to_end_card_sale(self, session, product, cashier):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService

        cart = CartService.get_or_create_cart(session)
        CartService.add_to_cart(cart, product, quantity=1)
        cart.refresh_from_db()

        svc = PaymentService(cart=cart, user=cashier)
        svc.process_card_payment(
            cart.grand_total, authorization_code="AUTH001"
        )
        result = svc.complete_transaction()
        cart.refresh_from_db()
        assert cart.status == CART_STATUS_COMPLETED

    def test_end_to_end_split_payment(
        self, session, product, product2, cashier
    ):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService

        cart = CartService.get_or_create_cart(session)
        CartService.add_to_cart(cart, product, quantity=2)
        CartService.add_to_cart(cart, product2, quantity=1)
        cart.refresh_from_db()

        total = cart.grand_total
        half = (total / 2).quantize(Decimal("0.01"))
        remainder = total - half

        svc = PaymentService(cart=cart, user=cashier)
        svc.split_payment([
            {"method": "cash", "amount": half, "amount_tendered": half},
            {"method": "card", "amount": remainder},
        ])
        assert svc.can_complete_cart()
        svc.complete_transaction()
        cart.refresh_from_db()
        assert cart.status == CART_STATUS_COMPLETED


# ── Session Totals Updates ───────────────────────────────────────────


class TestSessionTotalsUpdate:
    def test_session_totals_after_single_transaction(
        self, session, product, cashier
    ):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService

        cart = CartService.get_or_create_cart(session)
        CartService.add_to_cart(cart, product, quantity=2)
        cart.refresh_from_db()
        expected_total = cart.grand_total

        svc = PaymentService(cart=cart, user=cashier)
        svc.process_cash_payment(expected_total)
        svc.complete_transaction()

        session.refresh_from_db()
        assert session.transaction_count == 1
        assert session.total_sales == expected_total

    def test_session_totals_after_multiple_transactions(
        self, terminal, cashier, product, product2
    ):
        from apps.pos.cart.models import POSCart
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService
        from apps.pos.terminal.models import POSSession

        # Open fresh session
        num = POSSession.generate_session_number(terminal)
        sess = POSSession(
            terminal=terminal,
            user=cashier,
            session_number=num,
            opening_cash_amount=Decimal("5000.00"),
        )
        sess.open_session()

        running_total = Decimal("0.00")
        for p, qty in [(product, 1), (product2, 2)]:
            cart = CartService.get_or_create_cart(sess)
            CartService.add_to_cart(cart, p, quantity=qty)
            cart.refresh_from_db()
            running_total += cart.grand_total

            svc = PaymentService(cart=cart, user=cashier)
            svc.process_cash_payment(cart.grand_total)
            svc.complete_transaction()

        sess.refresh_from_db()
        assert sess.transaction_count == 2
        assert sess.total_sales == running_total


# ── Held Cart Workflow ───────────────────────────────────────────────


class TestHeldCartWorkflow:
    def test_hold_and_recall_cart(self, session, product, cashier):
        from apps.pos.cart.services.cart_service import CartService

        cart = CartService.get_or_create_cart(session)
        CartService.add_to_cart(cart, product, quantity=1)

        # Hold
        CartService.hold_cart(cart)
        cart.refresh_from_db()
        assert cart.status == CART_STATUS_HELD

        # Recall
        CartService.resume_cart(cart)
        cart.refresh_from_db()
        assert cart.status == CART_STATUS_ACTIVE
        assert cart.items.count() == 1  # items preserved

    def test_held_cart_items_preserved(self, session, product, product2, cashier):
        from apps.pos.cart.services.cart_service import CartService

        cart = CartService.get_or_create_cart(session)
        CartService.add_to_cart(cart, product, quantity=3)
        CartService.add_to_cart(cart, product2, quantity=2)
        cart.refresh_from_db()
        original_total = cart.grand_total

        CartService.hold_cart(cart)
        CartService.resume_cart(cart)
        cart.refresh_from_db()

        assert cart.items.count() == 2
        assert cart.grand_total == original_total

    def test_complete_after_recall(self, session, product, cashier):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService

        cart = CartService.get_or_create_cart(session)
        CartService.add_to_cart(cart, product, quantity=1)

        CartService.hold_cart(cart)
        CartService.resume_cart(cart)
        cart.refresh_from_db()

        svc = PaymentService(cart=cart, user=cashier)
        svc.process_cash_payment(cart.grand_total)
        svc.complete_transaction()
        cart.refresh_from_db()
        assert cart.status == CART_STATUS_COMPLETED


# ── Void Transaction Flow ────────────────────────────────────────────


class TestVoidTransactionFlow:
    def test_void_cart_with_partial_payment(self, cart_with_items, cashier):
        from apps.pos.payment.services.payment_service import PaymentService

        svc = PaymentService(cart=cart_with_items, user=cashier)
        svc.process_card_payment(Decimal("50.00"))
        svc.void_transaction(reason="Customer changed mind")

        cart_with_items.refresh_from_db()
        assert cart_with_items.status == CART_STATUS_VOIDED

    def test_void_no_items_modified_after_void(self, cart_with_items, cashier):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService

        svc = PaymentService(cart=cart_with_items, user=cashier)
        svc.void_transaction()

        cart_with_items.refresh_from_db()
        assert cart_with_items.is_modifiable is False


# ── Session Close with Transactions ──────────────────────────────────


class TestSessionCloseWithTransactions:
    def test_close_session_with_cash_reconciliation(
        self, terminal, cashier, product
    ):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService
        from apps.pos.terminal.models import POSSession

        # Open session
        num = POSSession.generate_session_number(terminal)
        sess = POSSession(
            terminal=terminal,
            user=cashier,
            session_number=num,
            opening_cash_amount=Decimal("10000.00"),
        )
        sess.open_session()

        # Process one sale
        cart = CartService.get_or_create_cart(sess)
        CartService.add_to_cart(cart, product, quantity=2)
        cart.refresh_from_db()

        svc = PaymentService(cart=cart, user=cashier)
        svc.process_cash_payment(cart.grand_total)
        svc.complete_transaction()
        sess.refresh_from_db()

        # Close session
        expected_cash = (
            Decimal("10000.00") + sess.total_sales - sess.total_refunds
        )
        sess.close_session(actual_cash_amount=expected_cash)
        assert sess.status == SESSION_STATUS_CLOSED
        assert sess.cash_variance == Decimal("0.00")

    def test_close_session_with_variance(self, terminal, cashier, product):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService
        from apps.pos.terminal.models import POSSession

        num = POSSession.generate_session_number(terminal)
        sess = POSSession(
            terminal=terminal,
            user=cashier,
            session_number=num,
            opening_cash_amount=Decimal("5000.00"),
        )
        sess.open_session()

        cart = CartService.get_or_create_cart(sess)
        CartService.add_to_cart(cart, product, quantity=1)
        cart.refresh_from_db()

        svc = PaymentService(cart=cart, user=cashier)
        svc.process_cash_payment(cart.grand_total)
        svc.complete_transaction()
        sess.refresh_from_db()

        # Cash short by 100
        expected = (
            Decimal("5000.00") + sess.total_sales - sess.total_refunds
        )
        sess.close_session(actual_cash_amount=expected - Decimal("100.00"))
        assert sess.cash_variance == Decimal("-100.00")


# ── Cart Reference Uniqueness ────────────────────────────────────────


class TestCartReferenceUniqueness:
    def test_multiple_carts_unique_references(self, session, product, cashier):
        from apps.pos.cart.services.cart_service import CartService
        from apps.pos.payment.services.payment_service import PaymentService

        references = set()
        for _ in range(3):
            cart = CartService.get_or_create_cart(session)
            CartService.add_to_cart(cart, product, quantity=1)
            cart.refresh_from_db()

            svc = PaymentService(cart=cart, user=cashier)
            svc.process_cash_payment(cart.grand_total)
            svc.complete_transaction()
            references.add(cart.reference_number)

        assert len(references) == 3
