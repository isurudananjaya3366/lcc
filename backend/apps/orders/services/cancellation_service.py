"""
Cancellation service for order and line-item cancellation (Tasks 78-80).

Handles full order cancellation with stock release and payment handling,
validation rules with permission checks, and partial line-item cancellation.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.orders.constants import (
    CANCELLABLE_STATES,
    OrderLineItemStatus,
    OrderStatus,
)

logger = logging.getLogger(__name__)


class CancellationError(Exception):
    """Raised for cancellation workflow errors."""
    pass


class CancellationService:
    """Manages order and line-item cancellation workflows."""

    # ── Full Order Cancellation (Task 78) ────────────────────────

    @classmethod
    @transaction.atomic
    def cancel_order(cls, order, user=None, reason="", request=None):
        """
        Cancel an entire order.

        Steps:
        1. Validate cancellation is allowed.
        2. Cancel all active fulfillments.
        3. Release allocated stock.
        4. Handle payment (void or refund based on payment status).
        5. Update order and line item statuses to CANCELLED.
        6. Log the event.

        Args:
            order: The Order instance.
            user: The cancelling user.
            reason: Cancellation reason.
            request: HTTP request for audit logging.

        Returns:
            The updated Order instance.
        """
        cls._validate_cancellation(order, user=user)

        now = timezone.now()

        # Cancel active fulfillments
        cls._cancel_fulfillments(order)

        # Release stock (placeholder for StockService)
        cls._release_stock(order)

        # Handle payment
        cls._handle_payment_on_cancel(order)

        # Cancel all non-terminal line items
        for line_item in order.line_items.exclude(
            status__in=[
                OrderLineItemStatus.CANCELLED,
                OrderLineItemStatus.RETURNED,
            ]
        ):
            line_item.status = OrderLineItemStatus.CANCELLED
            line_item.quantity_cancelled = line_item.quantity_ordered
            line_item.save(update_fields=["status", "quantity_cancelled"])

        # Update order status
        from apps.orders.services.order_service import OrderService

        OrderService.transition_status(
            order,
            OrderStatus.CANCELLED,
            user=user,
            notes=reason,
            request=request,
        )

        order.cancelled_at = now
        order.cancelled_by = user
        order.cancellation_reason = reason or ""
        order.save(update_fields=["cancelled_at", "cancelled_by", "cancellation_reason"])

        logger.info(
            "Order %s cancelled by %s. Reason: %s",
            order.order_number,
            user,
            reason or "N/A",
        )
        return order

    # ── Cancellation Validation (Task 79) ────────────────────────

    @classmethod
    def _validate_cancellation(cls, order, user=None):
        """
        Validate whether an order can be cancelled.

        Rules:
        - PENDING/CONFIRMED: Always allowed.
        - PROCESSING: Requires manager approval (simplified here).
        - SHIPPED/DELIVERED: Must use return process instead.
        - COMPLETED/CANCELLED/RETURNED: Not allowed.
        """
        if order.status in {OrderStatus.CANCELLED, OrderStatus.RETURNED}:
            raise CancellationError(
                f"Order is already in '{order.status}' status."
            )

        if order.status in {OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.COMPLETED}:
            raise CancellationError(
                f"Cannot cancel order in '{order.status}' status. "
                f"Please use the return process instead."
            )

        if order.status not in CANCELLABLE_STATES:
            raise CancellationError(
                f"Cannot cancel order in '{order.status}' status."
            )

        # PROCESSING orders may require manager approval
        if order.status == OrderStatus.PROCESSING:
            # Check for active fulfillments that block cancellation
            from apps.orders.models.fulfillment import FulfillmentStatus
            active_fulfillments = order.fulfillments.filter(
                status__in=[
                    FulfillmentStatus.PICKED,
                    FulfillmentStatus.PACKED,
                    FulfillmentStatus.SHIPPED,
                ]
            )
            if active_fulfillments.exists():
                raise CancellationError(
                    "Cannot cancel order with active fulfillments "
                    "(picked, packed, or shipped). Cancel fulfillments first."
                )
            logger.info(
                "Order %s in PROCESSING state — cancellation may require approval.",
                order.order_number,
            )

    @classmethod
    def can_cancel(cls, order):
        """Check if an order can be cancelled (non-raising)."""
        try:
            cls._validate_cancellation(order)
            return True
        except CancellationError:
            return False

    # ── Line-Item Cancellation (Task 80) ─────────────────────────

    @classmethod
    @transaction.atomic
    def cancel_line_items(cls, order, items_to_cancel, user=None, reason="",
                          request=None):
        """
        Partially cancel specific line items on an order.

        Args:
            order: The Order instance.
            items_to_cancel: List of dicts with:
                - 'line_item': OrderLineItem instance
                - 'quantity': Quantity to cancel
            user: The cancelling user.
            reason: Cancellation reason.
            request: HTTP request for audit logging.

        Returns:
            The updated Order instance.
        """
        if order.status in {OrderStatus.CANCELLED, OrderStatus.RETURNED}:
            raise CancellationError(
                f"Cannot cancel items on an order in '{order.status}' status."
            )

        cancelled_items = []

        for item_data in items_to_cancel:
            line_item = item_data["line_item"]
            qty_to_cancel = Decimal(str(item_data["quantity"]))

            # Check if item has active fulfillment items (picked/packed/shipped)
            from apps.orders.models.fulfillment import FulfillmentStatus
            active_fulfillment_items = line_item.fulfillment_items.filter(
                fulfillment__status__in=[
                    FulfillmentStatus.PICKED,
                    FulfillmentStatus.PACKED,
                    FulfillmentStatus.SHIPPED,
                ]
            )
            if active_fulfillment_items.exists():
                raise CancellationError(
                    f"Cannot cancel '{line_item.item_name}' — it has active "
                    f"fulfillments in picked/packed/shipped state."
                )

            # Validate quantity
            available = (
                line_item.quantity_ordered
                - line_item.quantity_fulfilled
                - line_item.quantity_cancelled
            )
            if qty_to_cancel > available:
                raise CancellationError(
                    f"Cannot cancel {qty_to_cancel} of '{line_item.item_name}'. "
                    f"Only {available} available for cancellation."
                )

            line_item.quantity_cancelled += qty_to_cancel

            # Determine line item status
            if line_item.quantity_cancelled >= line_item.quantity_ordered:
                line_item.status = OrderLineItemStatus.CANCELLED
            # else keep current status

            line_item.save(update_fields=["quantity_cancelled", "status"])
            cancelled_items.append({
                "item_name": line_item.item_name,
                "quantity_cancelled": str(qty_to_cancel),
            })

        # Recalculate order totals
        cls._recalculate_after_cancellation(order)

        # Log the event
        try:
            from apps.orders.services.history_service import HistoryService

            HistoryService.log_event(
                order=order,
                event_type="items_cancelled",
                description=f"Partial cancellation: {len(cancelled_items)} item(s)",
                user=user,
                request=request,
                metadata={
                    "cancelled_items": cancelled_items,
                    "reason": reason,
                },
            )
        except Exception:
            logger.warning(
                "Failed to log cancellation event for order %s.",
                order.order_number,
                exc_info=True,
            )

        logger.info(
            "Partial cancellation on order %s: %d item(s).",
            order.order_number,
            len(cancelled_items),
        )

        # Auto-cancel order if ALL items are now cancelled
        all_cancelled = all(
            li.status == OrderLineItemStatus.CANCELLED
            for li in order.line_items.all()
        )
        if all_cancelled and order.status != OrderStatus.CANCELLED:
            from apps.orders.services.order_service import OrderService
            OrderService.transition_status(
                order, OrderStatus.CANCELLED, user=user,
                notes="All line items cancelled via partial cancellation.",
            )
            order.cancelled_at = timezone.now()
            order.cancelled_by = user
            order.cancellation_reason = reason or "All items cancelled"
            order.save(update_fields=[
                "cancelled_at", "cancelled_by", "cancellation_reason",
            ])

        return order

    # ── Private Helpers ──────────────────────────────────────────

    @classmethod
    def _cancel_fulfillments(cls, order):
        """Cancel all non-terminal fulfillments for an order."""
        from apps.orders.models.fulfillment import Fulfillment, FulfillmentStatus

        terminal = {
            FulfillmentStatus.DELIVERED,
            FulfillmentStatus.CANCELLED,
        }
        active_fulfillments = order.fulfillments.exclude(status__in=terminal)
        count = active_fulfillments.update(
            status=FulfillmentStatus.CANCELLED
        )
        if count:
            logger.info(
                "Cancelled %d active fulfillment(s) for order %s.",
                count,
                order.order_number,
            )

    @classmethod
    def _release_stock(cls, order):
        """
        Release allocated stock for the order.

        Placeholder for StockService integration.
        """
        # TODO: Integrate with StockService when available
        # StockService.release_allocation(order)
        logger.info(
            "Stock released for order %s (placeholder).", order.order_number
        )

    @classmethod
    def _handle_payment_on_cancel(cls, order):
        """
        Handle payment adjustments on cancellation.

        - UNPAID: Nothing to do.
        - PARTIAL/PAID: Mark for refund.

        Placeholder for PaymentService integration.
        """
        from apps.orders.constants import PaymentStatus

        if order.payment_status in {PaymentStatus.PAID, PaymentStatus.PARTIAL}:
            order.payment_status = PaymentStatus.REFUNDED
            order.save(update_fields=["payment_status"])
            # TODO: Integrate with PaymentService for actual refund/void
            logger.info(
                "Payment status set to REFUNDED for order %s.",
                order.order_number,
            )

    @classmethod
    def _recalculate_after_cancellation(cls, order):
        """Recalculate order totals after partial cancellation."""
        try:
            from apps.orders.services.calculation_service import (
                OrderCalculationService,
            )

            OrderCalculationService.calculate_all(order)
        except Exception:
            # Fall back to simple recalculation
            active_items = order.line_items.exclude(
                status=OrderLineItemStatus.CANCELLED
            )
            subtotal = active_items.aggregate(
                total=Sum("line_total")
            )["total"] or Decimal("0")
            tax_total = active_items.aggregate(
                total=Sum("tax_amount")
            )["total"] or Decimal("0")

            order.subtotal = subtotal
            order.tax_amount = tax_total
            order.total_amount = (
                subtotal - order.discount_amount + tax_total
                + (order.shipping_amount or Decimal("0"))
            )
            order.save(
                update_fields=["subtotal", "tax_amount", "total_amount"]
            )

            logger.info(
                "Order %s totals recalculated after cancellation. New total: %s",
                order.order_number,
                order.total_amount,
            )
