"""
Fulfillment service for managing the order fulfillment workflow (Tasks 56-64).

Handles confirming, processing, picking, packing, shipping, partial
fulfillment, delivery confirmation, and order completion.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


class FulfillmentError(Exception):
    """Raised for fulfillment workflow errors."""
    pass


class FulfillmentService:
    """Manages the complete fulfillment workflow for orders."""

    # ── Validation Helpers ───────────────────────────────────────

    @classmethod
    def _validate_fulfillment_data(cls, order, items_data):
        """Validate that the order can be fulfilled with the given items."""
        from apps.orders.constants import OrderStatus

        if order.status not in (
            OrderStatus.CONFIRMED,
            OrderStatus.PROCESSING,
            OrderStatus.PARTIALLY_FULFILLED,
        ):
            raise FulfillmentError(
                f"Cannot create fulfillment for order in '{order.status}' status."
            )

        for item_data in items_data:
            line_item = item_data.get("order_line_item")
            qty = Decimal(str(item_data.get("quantity", 0)))

            if qty <= 0:
                raise FulfillmentError(
                    f"Quantity must be positive for item {line_item}."
                )

            already_fulfilled = (
                line_item.fulfillment_items.aggregate(
                    total=Sum("quantity")
                )["total"]
                or Decimal("0")
            )
            remaining = line_item.quantity_ordered - already_fulfilled
            if qty > remaining:
                raise FulfillmentError(
                    f"Cannot fulfill {qty} of '{line_item.item_name}'. "
                    f"Only {remaining} remaining."
                )

    @classmethod
    def _generate_fulfillment_number(cls, order):
        """Generate a fulfillment number: FUL-{ORDER_NUM}-{SEQ}."""
        from apps.orders.models.fulfillment import Fulfillment

        count = Fulfillment.objects.filter(order=order).count()
        order_suffix = order.order_number.replace("ORD-", "")
        return f"FUL-{order_suffix}-{count + 1:02d}"

    @classmethod
    def _create_fulfillment_record(cls, order, warehouse=None, notes=""):
        """Create a new Fulfillment record."""
        from apps.orders.models.fulfillment import Fulfillment

        return Fulfillment.objects.create(
            order=order,
            fulfillment_number=cls._generate_fulfillment_number(order),
            warehouse=warehouse,
            notes=notes,
        )

    @classmethod
    def _create_fulfillment_line_items(cls, fulfillment, items_data):
        """Create FulfillmentLineItem records."""
        from apps.orders.models.fulfillment_item import FulfillmentLineItem

        line_items = []
        for item_data in items_data:
            line_items.append(
                FulfillmentLineItem(
                    fulfillment=fulfillment,
                    order_line_item=item_data["order_line_item"],
                    quantity=item_data["quantity"],
                    warehouse=item_data.get("warehouse"),
                    bin_location=item_data.get("bin_location", ""),
                    serial_number=item_data.get("serial_number", ""),
                    batch_number=item_data.get("batch_number", ""),
                )
            )
        FulfillmentLineItem.objects.bulk_create(line_items)
        return line_items

    # ── Order Confirmation (Task 57) ────────────────────────────

    @classmethod
    @transaction.atomic
    def confirm_order(cls, order, user=None):
        """Confirm a pending order — PENDING → CONFIRMED."""
        from apps.orders.services.order_service import OrderService
        from apps.orders.constants import OrderStatus
        from apps.orders.services.notification_service import NotificationService

        result = OrderService.transition_status(
            order, OrderStatus.CONFIRMED, user=user
        )
        NotificationService.notify_order_confirmed(order, user=user)
        return result

    # ── Start Processing (Task 58) ──────────────────────────────

    @classmethod
    @transaction.atomic
    def start_processing(cls, order, warehouse=None, user=None):
        """
        Start processing an order — CONFIRMED → PROCESSING.

        Creates an initial fulfillment record and generates a picking list.
        """
        from apps.orders.services.order_service import OrderService
        from apps.orders.constants import OrderStatus

        OrderService.transition_status(
            order, OrderStatus.PROCESSING, user=user
        )

        fulfillment = cls._create_fulfillment_record(
            order, warehouse=warehouse, notes="Auto-created on processing start"
        )
        fulfillment.processing_started_at = timezone.now()
        fulfillment.created_by = user
        fulfillment.save(update_fields=["processing_started_at", "created_by", "updated_on"])

        # Create fulfillment line items for all order items
        items_data = []
        for line_item in order.line_items.order_by("position"):
            if line_item.quantity_remaining > 0:
                items_data.append({
                    "order_line_item": line_item,
                    "quantity": line_item.quantity_remaining,
                    "warehouse": warehouse,
                })

        if items_data:
            cls._create_fulfillment_line_items(fulfillment, items_data)

        from apps.orders.services.notification_service import NotificationService
        NotificationService.notify_warehouse_team(order, fulfillment, action="pick")

        return fulfillment

    @classmethod
    def generate_picking_list(cls, fulfillment):
        """Generate a picking list sorted by warehouse location."""
        return (
            fulfillment.line_items.select_related(
                "order_line_item__product",
                "order_line_item__variant",
                "warehouse",
            )
            .order_by("warehouse__name", "bin_location", "order_line_item__position")
            .values_list(
                "order_line_item__item_name",
                "order_line_item__item_sku",
                "quantity",
                "bin_location",
                "warehouse__name",
            )
        )

    # ── Pick Order (Task 59) ────────────────────────────────────

    @classmethod
    @transaction.atomic
    def pick_items(cls, fulfillment, picked_items, user=None):
        """
        Mark fulfillment line items as picked.

        picked_items: list of dicts with {fulfillment_line_item_id, bin_location}
        """
        from apps.orders.models.fulfillment import FulfillmentStatus

        if fulfillment.status not in (
            FulfillmentStatus.PENDING,
            FulfillmentStatus.PROCESSING,
            FulfillmentStatus.PICKING,
        ):
            raise FulfillmentError(
                f"Cannot pick items for fulfillment in '{fulfillment.status}' status."
            )

        if fulfillment.status != FulfillmentStatus.PICKING:
            fulfillment.status = FulfillmentStatus.PICKING
            fulfillment.save(update_fields=["status", "updated_on"])

        now = timezone.now()
        for item_data in picked_items:
            item = fulfillment.line_items.get(id=item_data["fulfillment_line_item_id"])
            item.picked_at = now
            item.picked_by = user
            if item_data.get("bin_location"):
                item.bin_location = item_data["bin_location"]
            item.save(update_fields=["picked_at", "picked_by", "bin_location", "updated_on"])

        # Check if all items are picked
        all_picked = not fulfillment.line_items.filter(picked_at__isnull=True).exists()
        if all_picked:
            fulfillment.status = FulfillmentStatus.PICKED
            fulfillment.save(update_fields=["status", "updated_on"])

        return fulfillment

    # ── Pack Order (Task 60) ────────────────────────────────────

    @classmethod
    @transaction.atomic
    def pack_order(cls, fulfillment, package_data=None, user=None):
        """
        Mark fulfillment as packed with package details.

        package_data: dict with weight, dimensions, special_handling_notes
        """
        from apps.orders.models.fulfillment import FulfillmentStatus

        if fulfillment.status not in (
            FulfillmentStatus.PICKED,
            FulfillmentStatus.PACKING,
        ):
            raise FulfillmentError(
                f"Cannot pack fulfillment in '{fulfillment.status}' status. "
                "Must be PICKED first."
            )

        now = timezone.now()
        package_data = package_data or {}

        # Update package details
        if package_data.get("weight"):
            fulfillment.weight = Decimal(str(package_data["weight"]))
        if package_data.get("dimensions"):
            fulfillment.dimensions = package_data["dimensions"]
            fulfillment.calculate_volumetric_weight()
        if package_data.get("special_handling_notes"):
            fulfillment.requires_special_handling = True
            fulfillment.special_handling_notes = package_data["special_handling_notes"]

        # Mark all items as packed
        fulfillment.line_items.filter(packed_at__isnull=True).update(
            packed_at=now, packed_by=user
        )

        fulfillment.status = FulfillmentStatus.PACKED
        fulfillment.packed_at = now
        fulfillment.save()

        return fulfillment

    # ── Ship Order (Task 61) ────────────────────────────────────

    @classmethod
    @transaction.atomic
    def ship_order(cls, fulfillment, carrier, tracking_number, user=None,
                   carrier_service="", estimated_delivery_date=None):
        """
        Mark fulfillment as shipped with carrier and tracking.
        """
        from apps.orders.models.fulfillment import FulfillmentStatus
        from apps.orders.constants import OrderStatus

        if fulfillment.status != FulfillmentStatus.PACKED:
            raise FulfillmentError(
                f"Cannot ship fulfillment in '{fulfillment.status}' status. "
                "Must be PACKED first."
            )

        now = timezone.now()

        fulfillment.carrier = carrier
        fulfillment.carrier_service = carrier_service or ""
        if estimated_delivery_date:
            fulfillment.estimated_delivery_date = estimated_delivery_date
        fulfillment.tracking_number = tracking_number
        fulfillment.generate_tracking_url()
        fulfillment.shipped_at = now
        fulfillment.shipped_by = user
        fulfillment.status = FulfillmentStatus.SHIPPED
        fulfillment.save()

        # Update order line item quantities
        for fli in fulfillment.line_items.select_related("order_line_item"):
            oli = fli.order_line_item
            oli.quantity_fulfilled = (
                oli.quantity_fulfilled + fli.quantity
            )
            oli.shipped_at = now
            oli.save(update_fields=["quantity_fulfilled", "shipped_at", "updated_on"])

        # Update order status to SHIPPED if not already
        order = fulfillment.order
        if order.status in (OrderStatus.PROCESSING, OrderStatus.PARTIALLY_FULFILLED):
            from apps.orders.services.order_service import OrderService

            OrderService.transition_status(order, OrderStatus.SHIPPED, user=user)

        from apps.orders.services.history_service import HistoryService

        HistoryService.log_shipment(
            order, tracking_number=tracking_number, user=user
        )

        from apps.orders.services.notification_service import NotificationService
        NotificationService.notify_order_shipped(order, fulfillment=fulfillment, user=user)

        return fulfillment

    # ── Partial Fulfillment (Task 62) ────────────────────────────

    @classmethod
    @transaction.atomic
    def create_partial_fulfillment(cls, order, items_data, warehouse=None, user=None):
        """
        Create a partial fulfillment for selected items/quantities.

        items_data: list of {order_line_item: obj, quantity: Decimal}
        """
        cls._validate_fulfillment_data(order, items_data)

        fulfillment = cls._create_fulfillment_record(
            order, warehouse=warehouse, notes="Partial fulfillment"
        )
        cls._create_fulfillment_line_items(fulfillment, [
            {**item, "warehouse": warehouse} for item in items_data
        ])

        # Set order to PARTIALLY_FULFILLED if applicable
        from apps.orders.constants import OrderStatus
        if order.status == OrderStatus.PROCESSING:
            from apps.orders.services.order_service import OrderService
            OrderService.transition_status(
                order, OrderStatus.PARTIALLY_FULFILLED, user=user
            )

        from apps.orders.services.notification_service import NotificationService
        NotificationService.notify_partial_fulfillment(order, fulfillment, user=user)

        logger.info(
            "Partial fulfillment %s created for order %s with %d items",
            fulfillment.fulfillment_number,
            order.order_number,
            len(items_data),
        )

        return fulfillment

    # ── Delivery Confirmation (Task 63) ──────────────────────────

    @classmethod
    @transaction.atomic
    def confirm_delivery(cls, fulfillment, recipient="", signature="", photo_url="", user=None):
        """Mark a fulfillment as delivered."""
        from apps.orders.models.fulfillment import FulfillmentStatus
        from apps.orders.constants import OrderStatus

        if fulfillment.status != FulfillmentStatus.SHIPPED:
            raise FulfillmentError(
                f"Cannot confirm delivery for fulfillment in '{fulfillment.status}' status. "
                "Must be SHIPPED first."
            )

        now = timezone.now()
        fulfillment.status = FulfillmentStatus.DELIVERED
        fulfillment.delivered_at = now
        fulfillment.delivery_confirmed = True
        fulfillment.delivery_recipient = recipient
        fulfillment.delivery_signature = signature
        fulfillment.delivery_photo_url = photo_url
        fulfillment.delivery_attempts += 1
        fulfillment.save()

        # Update order line items
        for fli in fulfillment.line_items.select_related("order_line_item"):
            oli = fli.order_line_item
            oli.delivered_at = now
            oli.save(update_fields=["delivered_at", "updated_on"])

        # Check if all fulfillments are delivered
        order = fulfillment.order
        all_delivered = not order.fulfillments.exclude(
            status=FulfillmentStatus.DELIVERED
        ).exclude(
            status=FulfillmentStatus.CANCELLED
        ).exists()

        if all_delivered and order.status in (
            OrderStatus.SHIPPED,
            OrderStatus.PARTIALLY_FULFILLED,
        ):
            from apps.orders.services.order_service import OrderService

            OrderService.transition_status(order, OrderStatus.DELIVERED, user=user)

        from apps.orders.services.history_service import HistoryService
        HistoryService.log_event(
            order,
            event_type="delivery_confirmed",
            description=f"Fulfillment {fulfillment.fulfillment_number} delivered.",
            user=user,
        )

        from apps.orders.services.notification_service import NotificationService
        NotificationService.notify_order_delivered(order, fulfillment=fulfillment, user=user)

        return fulfillment

    # ── Order Completion (Task 64) ───────────────────────────────

    @classmethod
    @transaction.atomic
    def complete_order(cls, order, user=None):
        """
        Complete an order — finalize financial records, lock the order.
        """
        from apps.orders.constants import OrderStatus
        from apps.orders.services.order_service import OrderService

        if order.status != OrderStatus.DELIVERED:
            raise FulfillmentError(
                f"Cannot complete order in '{order.status}' status. "
                "Must be DELIVERED first."
            )

        OrderService.transition_status(order, OrderStatus.COMPLETED, user=user)
        OrderService.lock_order(
            order, user=user, lock_reason="completed",
            lock_notes="Order completed and locked automatically.",
        )

        from apps.orders.services.notification_service import NotificationService
        NotificationService.notify_order_completed(order, user=user)

        logger.info("Order %s completed and locked.", order.order_number)

        return order

    # ── Fulfillment Progress ─────────────────────────────────────

    @classmethod
    def get_fulfillment_progress(cls, order):
        """Get fulfillment progress for an order."""
        line_items = order.line_items.all()
        total_ordered = sum(li.quantity_ordered for li in line_items) or Decimal("1")
        total_fulfilled = sum(li.quantity_fulfilled for li in line_items)

        return {
            "total_ordered": total_ordered,
            "total_fulfilled": total_fulfilled,
            "percentage": (
                (total_fulfilled / total_ordered * 100)
                if total_ordered > 0
                else Decimal("0")
            ),
            "is_fully_fulfilled": all(li.is_fully_fulfilled for li in line_items),
            "fulfillment_count": order.fulfillments.count(),
        }
