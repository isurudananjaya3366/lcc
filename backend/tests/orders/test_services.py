"""
Order service tests (Task 91).
"""

import pytest
from decimal import Decimal

from apps.orders.constants import OrderStatus, OrderSource

pytestmark = pytest.mark.django_db


class TestOrderService:
    """Tests for OrderService."""

    def test_create_order(self, tenant_context):
        from apps.orders.services.order_service import OrderService

        order = OrderService.create_order(
            data={
                "customer_name": "Test Customer",
                "customer_email": "test@example.com",
                "source": OrderSource.MANUAL,
            },
            items_data=[
                {
                    "item_name": "Widget A",
                    "item_sku": "WA-001",
                    "quantity_ordered": 2,
                    "unit_price": 1000,
                    "tax_rate": 18,
                },
            ],
        )
        assert order.pk is not None
        assert order.order_number is not None
        assert order.status == OrderStatus.PENDING
        assert order.line_items.count() == 1

    def test_transition_status(self, create_order):
        from apps.orders.services.order_service import OrderService

        order = create_order(status=OrderStatus.PENDING)
        order = OrderService.transition_status(order, OrderStatus.CONFIRMED)
        assert order.status == OrderStatus.CONFIRMED
        assert order.confirmed_at is not None

    def test_invalid_transition(self, create_order):
        from apps.orders.services.order_service import (
            OrderService,
            InvalidStatusTransition,
        )

        order = create_order(status=OrderStatus.PENDING)
        with pytest.raises(InvalidStatusTransition):
            OrderService.transition_status(order, OrderStatus.SHIPPED)

    def test_duplicate_order(self, create_order, create_line_item):
        from apps.orders.services.order_service import OrderService

        order = create_order()
        create_line_item(order, item_name="Original Item")
        dup = OrderService.duplicate_order(order.id)

        assert dup.pk != order.pk
        assert dup.order_number != order.order_number
        assert dup.status == OrderStatus.PENDING
        assert dup.line_items.count() == 1

    def test_lock_order(self, create_order):
        from apps.orders.services.order_service import OrderService

        order = create_order(status=OrderStatus.CONFIRMED)
        order = OrderService.lock_order(order)
        assert order.is_locked is True

    def test_unlock_order(self, create_order):
        from apps.orders.services.order_service import OrderService

        order = create_order(status=OrderStatus.CONFIRMED, is_locked=True)
        order = OrderService.unlock_order(order)
        assert order.is_locked is False


class TestCalculationService:
    """Tests for calculation services."""

    def test_line_item_calculator_discount(self):
        from apps.orders.services.calculation_service import LineItemCalculator

        discount = LineItemCalculator.calculate_discount(
            unit_price=Decimal("1000.00"),
            quantity=Decimal("2"),
            discount_type="percentage",
            discount_value=Decimal("10"),
        )
        # 2 * 1000 = 2000, 10% discount = 200
        assert discount == Decimal("200.00")

    def test_line_item_calculator_tax(self):
        from apps.orders.services.calculation_service import LineItemCalculator

        tax = LineItemCalculator.calculate_tax(
            amount=Decimal("1800.00"),
            tax_rate=Decimal("18"),
            is_taxable=True,
        )
        # 18% of 1800 = 324
        assert tax == Decimal("324.00")

    def test_shipping_calculator_flat_rate(self):
        from apps.orders.services.calculation_service import ShippingCalculator

        cost = ShippingCalculator.flat_rate(Decimal("500"))
        assert cost == Decimal("500")


class TestCancellationService:
    """Tests for CancellationService."""

    def test_cancel_pending_order(self, create_order):
        from apps.orders.services.cancellation_service import CancellationService

        order = create_order(status=OrderStatus.PENDING)
        order = CancellationService.cancel_order(order, reason="Changed mind")
        assert order.status == OrderStatus.CANCELLED

    def test_cannot_cancel_shipped_order(self, create_order):
        from apps.orders.services.cancellation_service import (
            CancellationService,
            CancellationError,
        )

        order = create_order(status=OrderStatus.SHIPPED)
        with pytest.raises(CancellationError):
            CancellationService.cancel_order(order)

    def test_can_cancel_check(self, create_order):
        from apps.orders.services.cancellation_service import CancellationService

        pending = create_order(status=OrderStatus.PENDING)
        shipped = create_order(status=OrderStatus.SHIPPED)
        assert CancellationService.can_cancel(pending) is True
        assert CancellationService.can_cancel(shipped) is False

    def test_partial_line_item_cancellation(self, create_order, create_line_item):
        from apps.orders.services.cancellation_service import CancellationService
        from apps.orders.constants import OrderLineItemStatus

        order = create_order(status=OrderStatus.CONFIRMED)
        item = create_line_item(
            order,
            quantity_ordered=Decimal("5"),
            unit_price=Decimal("100"),
        )

        CancellationService.cancel_line_items(
            order,
            items_to_cancel=[{"line_item": item, "quantity": Decimal("3")}],
        )
        item.refresh_from_db()
        assert item.quantity_cancelled == Decimal("3")


class TestReturnService:
    """Tests for ReturnService."""

    def test_create_return_request(self, delivered_order):
        from apps.orders.services.return_service import ReturnService
        from apps.orders.models.order_return import ReturnReason

        line_item = delivered_order.line_items.first()
        order_return = ReturnService.create_return_request(
            order=delivered_order,
            items_data=[{"order_line_item": line_item, "quantity": 1}],
            reason=ReturnReason.DEFECTIVE,
        )
        assert order_return.pk is not None
        assert order_return.return_number.startswith("RET-")
        assert order_return.return_line_items.count() == 1

    def test_return_not_allowed_for_pending(self, create_order):
        from apps.orders.services.return_service import ReturnService, ReturnError
        from apps.orders.models.order_return import ReturnReason

        order = create_order(status=OrderStatus.PENDING)
        with pytest.raises(ReturnError):
            ReturnService.create_return_request(
                order=order,
                items_data=[],
                reason=ReturnReason.OTHER,
            )

    def test_approve_return(self, delivered_order):
        from apps.orders.services.return_service import ReturnService
        from apps.orders.models.order_return import ReturnReason, ReturnStatus

        line_item = delivered_order.line_items.first()
        order_return = ReturnService.create_return_request(
            order=delivered_order,
            items_data=[{"order_line_item": line_item, "quantity": 1}],
            reason=ReturnReason.WRONG_ITEM,
        )
        order_return = ReturnService.approve_return(order_return)
        assert order_return.status == ReturnStatus.APPROVED

    def test_reject_return(self, delivered_order):
        from apps.orders.services.return_service import ReturnService
        from apps.orders.models.order_return import ReturnReason, ReturnStatus

        line_item = delivered_order.line_items.first()
        order_return = ReturnService.create_return_request(
            order=delivered_order,
            items_data=[{"order_line_item": line_item, "quantity": 1}],
            reason=ReturnReason.CHANGED_MIND,
        )
        order_return = ReturnService.reject_return(
            order_return, rejection_reason="Outside return window"
        )
        assert order_return.status == ReturnStatus.REJECTED
