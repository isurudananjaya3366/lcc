"""
Order model tests (Task 91).
"""

import pytest
from decimal import Decimal

from apps.orders.constants import (
    ALLOWED_TRANSITIONS,
    CANCELLABLE_STATES,
    EDITABLE_STATES,
    OrderStatus,
    OrderSource,
    PaymentStatus,
    OrderLineItemStatus,
    TaxStrategy,
)

pytestmark = pytest.mark.django_db


class TestOrderModel:
    """Tests for the Order model."""

    def test_create_order(self, create_order):
        order = create_order()
        assert order.pk is not None
        assert order.order_number.startswith("ORD-")
        assert order.status == OrderStatus.PENDING

    def test_order_str(self, create_order):
        order = create_order(order_number="ORD-2025-00001")
        assert "ORD-2025-00001" in str(order)

    def test_order_is_draft(self, create_order):
        order = create_order(is_draft=True)
        assert order.is_draft is True

    def test_order_is_editable_pending(self, create_order):
        order = create_order(status=OrderStatus.PENDING)
        assert order.is_editable is True

    def test_order_is_editable_shipped(self, create_order):
        order = create_order(status=OrderStatus.SHIPPED)
        assert order.is_editable is False

    def test_order_is_editable_locked(self, create_order):
        order = create_order(status=OrderStatus.PENDING, is_locked=True)
        assert order.is_editable is False

    def test_order_default_currency(self, create_order):
        order = create_order()
        assert order.currency == "LKR"


class TestOrderConstants:
    """Tests for order constants and transitions."""

    def test_allowed_transitions(self):
        assert OrderStatus.CONFIRMED in ALLOWED_TRANSITIONS[OrderStatus.PENDING]
        assert OrderStatus.CANCELLED in ALLOWED_TRANSITIONS[OrderStatus.PENDING]

    def test_terminal_states_no_transitions(self):
        assert ALLOWED_TRANSITIONS[OrderStatus.CANCELLED] == []
        assert ALLOWED_TRANSITIONS[OrderStatus.RETURNED] == []

    def test_editable_states(self):
        assert OrderStatus.PENDING in EDITABLE_STATES
        assert OrderStatus.CONFIRMED in EDITABLE_STATES
        assert OrderStatus.SHIPPED not in EDITABLE_STATES

    def test_cancellable_states(self):
        assert OrderStatus.PENDING in CANCELLABLE_STATES
        assert OrderStatus.PROCESSING in CANCELLABLE_STATES
        assert OrderStatus.SHIPPED not in CANCELLABLE_STATES


class TestOrderLineItemModel:
    """Tests for the OrderLineItem model."""

    def test_create_line_item(self, create_order, create_line_item):
        order = create_order()
        item = create_line_item(order)
        assert item.pk is not None
        assert item.order == order

    def test_line_item_recalculate(self, create_order, create_line_item):
        order = create_order()
        item = create_line_item(
            order,
            quantity_ordered=Decimal("2"),
            unit_price=Decimal("1000.00"),
            tax_rate=Decimal("18.00"),
        )
        # 2 * 1000 = 2000 subtotal + 18% tax = 2360
        assert item.line_total == Decimal("2360.00")
        assert item.tax_amount == Decimal("360.00")

    def test_line_item_default_status(self, create_order, create_line_item):
        order = create_order()
        item = create_line_item(order)
        assert item.status == OrderLineItemStatus.PENDING

    def test_line_item_auto_position(self, create_order, create_line_item):
        order = create_order()
        item1 = create_line_item(order, position=0, item_name="First")
        item2 = create_line_item(order, position=0, item_name="Second")
        assert item1.position > 0 or item2.position > item1.position


class TestOrderHistoryModel:
    """Tests for the OrderHistory model."""

    def test_create_history_entry(self, create_order):
        from apps.orders.models import OrderHistory

        order = create_order()
        entry = OrderHistory.objects.create(
            order=order,
            event_type="status_changed",
            description="Status changed to confirmed",
        )
        assert entry.pk is not None
        assert entry.order == order

    def test_history_str(self, create_order):
        from apps.orders.models import OrderHistory

        order = create_order()
        entry = OrderHistory.objects.create(
            order=order,
            event_type="created",
            description="Order created",
        )
        assert "Created" in str(entry)


class TestOrderReturnModel:
    """Tests for the OrderReturn model."""

    def test_create_return(self, create_order):
        from apps.orders.models.order_return import OrderReturn, ReturnReason

        order = create_order()
        ret = OrderReturn.objects.create(
            order=order,
            return_number="RET-2025-00001",
            reason=ReturnReason.DEFECTIVE,
        )
        assert ret.pk is not None
        assert ret.status == "requested"

    def test_return_str(self, create_order):
        from apps.orders.models.order_return import OrderReturn

        order = create_order()
        ret = OrderReturn.objects.create(
            order=order,
            return_number="RET-2025-00002",
        )
        assert "RET-2025-00002" in str(ret)

    def test_return_is_refund_eligible(self, create_order):
        from apps.orders.models.order_return import OrderReturn, ReturnStatus

        order = create_order()
        ret = OrderReturn.objects.create(
            order=order,
            return_number="RET-2025-00003",
            status=ReturnStatus.RECEIVED,
        )
        assert ret.is_refund_eligible() is True

    def test_return_not_refund_eligible(self, create_order):
        from apps.orders.models.order_return import OrderReturn, ReturnStatus

        order = create_order()
        ret = OrderReturn.objects.create(
            order=order,
            return_number="RET-2025-00004",
            status=ReturnStatus.REQUESTED,
        )
        assert ret.is_refund_eligible() is False


class TestFulfillmentModel:
    """Tests for the Fulfillment model."""

    def test_create_fulfillment(self, create_order):
        from apps.orders.models.fulfillment import Fulfillment

        order = create_order()
        ful = Fulfillment.objects.create(
            order=order,
            fulfillment_number="FUL-TEST-01",
        )
        assert ful.pk is not None
        assert ful.status == "pending"
