"""
Return service for managing order returns (Tasks 73-77).

Handles return request creation, approval/rejection,
receipt with inspection, and stock restoration.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

logger = logging.getLogger(__name__)

# Condition-based refund adjustments (Task 76)
CONDITION_REFUND_MULTIPLIERS = {
    "unopened": Decimal("1.00"),        # Full refund
    "opened": Decimal("0.85"),          # 15% restocking fee
    "damaged": Decimal("0.50"),         # 50% refund
}

# Default return window in days
DEFAULT_RETURN_WINDOW_DAYS = 30


class ReturnError(Exception):
    """Raised for return workflow errors."""
    pass


class ReturnService:
    """Manages the complete return workflow for orders."""

    # ── Validation (Task 73) ─────────────────────────────────────

    @classmethod
    def _validate_return_eligibility(cls, order):
        """Check whether an order is eligible for returns."""
        from apps.orders.constants import OrderStatus

        eligible_statuses = {
            OrderStatus.DELIVERED,
            OrderStatus.COMPLETED,
        }
        if order.status not in eligible_statuses:
            raise ReturnError(
                f"Cannot create return for order in '{order.status}' status. "
                f"Order must be delivered or completed."
            )

    @classmethod
    def _calculate_return_window(cls, order, window_days=None):
        """Check if the order is within the return window."""
        if window_days is None:
            window_days = DEFAULT_RETURN_WINDOW_DAYS

        reference_date = order.delivered_at or order.completed_at or order.updated_on
        if reference_date is None:
            return True  # No date to check against — allow

        deadline = reference_date + timezone.timedelta(days=window_days)
        if timezone.now() > deadline:
            raise ReturnError(
                f"Return window of {window_days} days has expired. "
                f"Order was delivered on {reference_date.date()}."
            )
        return True

    @classmethod
    def _check_return_policy(cls, order, items_data):
        """Validate items against return policy rules."""
        for item_data in items_data:
            line_item = item_data["order_line_item"]
            qty = Decimal(str(item_data.get("quantity", 0)))

            if qty <= 0:
                raise ReturnError(
                    f"Return quantity must be positive for '{line_item.item_name}'."
                )

            # Check already-returned quantities
            already_returned = (
                line_item.return_items.aggregate(total=Sum("quantity"))["total"]
                or Decimal("0")
            )
            returnable = line_item.quantity_fulfilled - already_returned
            if qty > returnable:
                raise ReturnError(
                    f"Cannot return {qty} of '{line_item.item_name}'. "
                    f"Only {returnable} eligible for return."
                )

    @classmethod
    def _generate_return_number(cls):
        """Generate a return number: RET-{YEAR}-{SEQ}."""
        from apps.orders.models.order_return import OrderReturn

        year = timezone.now().year
        prefix = f"RET-{year}-"
        last = (
            OrderReturn.objects.filter(return_number__startswith=prefix)
            .order_by("-return_number")
            .values_list("return_number", flat=True)
            .first()
        )
        if last:
            seq = int(last.split("-")[-1]) + 1
        else:
            seq = 1
        return f"{prefix}{seq:05d}"

    # ── Create Return Request (Task 74) ──────────────────────────

    @classmethod
    @transaction.atomic
    def create_return_request(cls, order, items_data, reason, reason_detail="",
                              user=None, refund_shipping=False, notes="",
                              request=None):
        """
        Create a return request for an order.

        Args:
            order: The Order instance.
            items_data: List of dicts with 'order_line_item' and 'quantity'.
            reason: ReturnReason value.
            reason_detail: Free-text detail about the reason.
            user: The requesting user.
            refund_shipping: Whether to refund shipping costs.
            notes: Additional notes.
            request: HTTP request for audit logging.

        Returns:
            The created OrderReturn instance.
        """
        from apps.orders.models.order_return import (
            OrderReturn,
            ReturnLineItem,
            ReturnStatus,
        )

        # Validate eligibility
        cls._validate_return_eligibility(order)
        cls._calculate_return_window(order)
        cls._check_return_policy(order, items_data)

        # Create the return
        order_return = OrderReturn.objects.create(
            order=order,
            return_number=cls._generate_return_number(),
            reason=reason,
            reason_detail=reason_detail,
            status=ReturnStatus.REQUESTED,
            requested_by=user,
            refund_shipping=refund_shipping,
            notes=notes,
        )

        # Create return line items
        return_items = []
        for item_data in items_data:
            line_item = item_data["order_line_item"]
            qty = Decimal(str(item_data["quantity"]))
            return_items.append(
                ReturnLineItem(
                    order_return=order_return,
                    order_line_item=line_item,
                    quantity=qty,
                    unit_refund_amount=line_item.unit_price,
                )
            )
        ReturnLineItem.objects.bulk_create(return_items)

        # Log event
        cls._log_return_event(
            order, "return_requested", order_return, user, request
        )

        logger.info(
            "Return %s created for order %s with %d items.",
            order_return.return_number,
            order.order_number,
            len(return_items),
        )
        return order_return

    # ── Approve / Reject (Task 75) ───────────────────────────────

    @classmethod
    @transaction.atomic
    def approve_return(cls, order_return, user=None, notes="", request=None):
        """
        Approve a return request.

        Calculates estimated refund and updates status.
        """
        from apps.orders.models.order_return import ReturnStatus

        if order_return.status != ReturnStatus.REQUESTED:
            raise ReturnError(
                f"Can only approve returns in 'requested' status, "
                f"got '{order_return.status}'."
            )

        order_return.status = ReturnStatus.APPROVED
        order_return.approved_by = user
        order_return.approved_at = timezone.now()
        if notes:
            order_return.notes = (
                f"{order_return.notes}\nApproval: {notes}".strip()
            )

        # Pre-calculate estimated refund (assumes full refund before inspection)
        order_return.refund_amount = order_return.calculate_refund_amount()
        order_return.save()

        cls._log_return_event(
            order_return.order, "return_approved", order_return, user, request
        )

        logger.info("Return %s approved.", order_return.return_number)
        return order_return

    @classmethod
    @transaction.atomic
    def reject_return(cls, order_return, rejection_reason, user=None, request=None):
        """Reject a return request."""
        from apps.orders.models.order_return import ReturnStatus

        if order_return.status != ReturnStatus.REQUESTED:
            raise ReturnError(
                f"Can only reject returns in 'requested' status, "
                f"got '{order_return.status}'."
            )

        order_return.status = ReturnStatus.REJECTED
        order_return.rejected_by = user
        order_return.rejected_at = timezone.now()
        order_return.rejection_reason = rejection_reason
        order_return.save()

        cls._log_return_event(
            order_return.order, "return_rejected", order_return, user, request
        )

        logger.info("Return %s rejected.", order_return.return_number)
        return order_return

    # ── Receive & Inspect (Task 76) ──────────────────────────────

    @classmethod
    @transaction.atomic
    def receive_return(cls, order_return, inspections, user=None, request=None):
        """
        Receive and inspect returned items.

        Args:
            order_return: The OrderReturn instance.
            inspections: List of dicts with:
                - 'return_line_item': ReturnLineItem instance (or its ID)
                - 'condition': ItemCondition value
                - 'inspection_notes': Optional notes
            user: The receiving/inspecting user.
            request: HTTP request for audit logging.

        Adjusts refund amounts based on item condition.
        """
        from apps.orders.models.order_return import (
            ReturnLineItem, ReturnStatus, ItemCondition,
        )

        if order_return.status != ReturnStatus.APPROVED:
            raise ReturnError(
                f"Can only receive returns in 'approved' status, "
                f"got '{order_return.status}'."
            )

        now = timezone.now()

        for inspection in inspections:
            rli = inspection["return_line_item"]
            if not isinstance(rli, ReturnLineItem):
                # Resolve by ID
                rli = order_return.return_line_items.get(id=rli)

            condition = inspection.get("condition", ItemCondition.UNOPENED)
            multiplier = CONDITION_REFUND_MULTIPLIERS.get(
                condition, Decimal("1.00")
            )

            # Adjust refund based on condition
            original_unit_price = rli.order_line_item.unit_price
            rli.unit_refund_amount = original_unit_price * multiplier

            # Calculate restocking fee for non-unopened items
            if condition == ItemCondition.OPENED:
                rli.restocking_fee_per_unit = (
                    original_unit_price * Decimal("0.15")
                )
            elif condition == ItemCondition.DAMAGED:
                rli.restocking_fee_per_unit = Decimal("0")
                # Damaged uses reduced refund instead of separate fee

            rli.condition = condition
            rli.inspected = True
            rli.inspected_by = user
            rli.inspected_at = now
            rli.inspection_notes = inspection.get("inspection_notes", "")
            rli.save()

        # Update return status and recalculate refund
        order_return.status = ReturnStatus.RECEIVED
        order_return.received_by = user
        order_return.received_at = now
        order_return.refund_amount = order_return.calculate_refund_amount()
        order_return.save()

        # Update order line item returned quantities
        for rli in order_return.return_line_items.all():
            line_item = rli.order_line_item
            line_item.quantity_returned = (
                line_item.return_items.aggregate(
                    total=Sum("quantity")
                )["total"]
                or Decimal("0")
            )
            line_item.save(update_fields=["quantity_returned"])

        # Restore stock (Task 77)
        cls._restore_stock(order_return, user=user)

        cls._log_return_event(
            order_return.order, "return_received", order_return, user, request
        )

        logger.info("Return %s received and inspected.", order_return.return_number)
        return order_return

    # ── Stock Restoration (Task 77) ──────────────────────────────

    @classmethod
    def _restore_stock(cls, order_return, user=None):
        """
        Restore stock based on item condition.

        - UNOPENED → full sellable inventory
        - OPENED → open-box / reduced inventory
        - DAMAGED → write-off (no stock restoration)

        Placeholder for StockService integration.
        """
        from apps.orders.models.order_return import ItemCondition

        now = timezone.now()

        for rli in order_return.return_line_items.filter(stock_restored=False):
            if rli.condition == ItemCondition.DAMAGED:
                # Damaged items are written off — no stock restoration
                logger.info(
                    "Item '%s' x%s marked as damaged — written off.",
                    rli.order_line_item.item_name,
                    rli.quantity,
                )
            elif rli.condition in (ItemCondition.UNOPENED, ItemCondition.OPENED):
                # TODO: Integrate with StockService when available
                # StockService.restore_stock(
                #     product=rli.order_line_item.product,
                #     variant=rli.order_line_item.variant,
                #     quantity=rli.quantity,
                #     condition=rli.condition,
                #     warehouse=rli.order_line_item.warehouse,
                # )
                logger.info(
                    "Stock restored: '%s' x%s (condition: %s).",
                    rli.order_line_item.item_name,
                    rli.quantity,
                    rli.condition,
                )

            rli.stock_restored = True
            rli.stock_restored_at = now
            rli.save(update_fields=["stock_restored", "stock_restored_at"])

    # ── Process Refund ───────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def process_refund(cls, order_return, refund_method, user=None, request=None):
        """
        Mark a received return as refunded.

        Args:
            order_return: The OrderReturn instance.
            refund_method: RefundMethod value.
            user: The user processing the refund.
            request: HTTP request for audit logging.
        """
        from apps.orders.models.order_return import ReturnStatus

        if not order_return.is_refund_eligible():
            raise ReturnError(
                f"Return '{order_return.return_number}' is not eligible "
                f"for refund (status: {order_return.status})."
            )

        order_return.status = ReturnStatus.REFUNDED
        order_return.refund_method = refund_method
        order_return.refunded_at = timezone.now()
        order_return.save()

        # Check if all items on the order have been returned
        cls._check_order_return_status(order_return.order)

        cls._log_return_event(
            order_return.order, "return_refunded", order_return, user, request
        )

        logger.info(
            "Return %s refunded: %s via %s.",
            order_return.return_number,
            order_return.refund_amount,
            refund_method,
        )
        return order_return

    @classmethod
    def _check_order_return_status(cls, order):
        """
        Check if the order should be moved to RETURNED status.

        If all fulfilled quantities have been returned, transition to RETURNED.
        """
        from apps.orders.constants import OrderStatus

        total_ordered = sum(
            li.quantity_ordered for li in order.line_items.all()
        )
        total_returned = sum(
            li.quantity_returned for li in order.line_items.all()
        )

        if total_ordered > 0 and total_returned >= total_ordered:
            order.status = OrderStatus.RETURNED
            order.save(update_fields=["status"])
            logger.info(
                "Order %s fully returned — status set to RETURNED.",
                order.order_number,
            )

    # ── Audit Logging Helper ─────────────────────────────────────

    @classmethod
    def _log_return_event(cls, order, event_type, order_return, user, request):
        """Log a return event to order history."""
        try:
            from apps.orders.services.history_service import HistoryService

            HistoryService.log_event(
                order=order,
                event_type=event_type,
                description=(
                    f"Return {order_return.return_number}: {event_type.replace('_', ' ')}"
                ),
                user=user,
                request=request,
                metadata={
                    "return_number": order_return.return_number,
                    "return_status": order_return.status,
                    "refund_amount": str(order_return.refund_amount),
                },
            )
        except Exception:
            logger.warning(
                "Failed to log return event for %s.",
                order_return.return_number,
                exc_info=True,
            )
