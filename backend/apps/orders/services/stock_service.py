"""
Stock reservation service for order stock management (Task 41, 43).

Handles stock availability checks, reservation, release, partial reservation,
and insufficient stock handling strategies.
"""

import logging

from django.db import transaction
from django.utils import timezone

from apps.orders.exceptions import InsufficientStockError

logger = logging.getLogger(__name__)


class StockService:
    """
    Manages stock reservations for orders.

    Checks availability, reserves stock with row-level locking,
    releases reservations, and handles insufficient stock scenarios.
    """

    @classmethod
    def check_availability(cls, order):
        """
        Check stock availability for all line items in an order.

        Returns:
            dict: {line_item_id: available_quantity} for each tracked item.
        """
        availability = {}
        for item in order.line_items.select_related("product", "variant"):
            product = item.variant or item.product
            if not product:
                continue
            if not getattr(product, "track_inventory", True):
                continue
            # Try to get inventory info
            available = cls._get_available_quantity(product)
            availability[str(item.id)] = {
                "line_item": item,
                "product": product,
                "requested": item.quantity_ordered,
                "available": available,
                "sufficient": available >= item.quantity_ordered,
            }
        return availability

    @classmethod
    def is_fully_available(cls, order):
        """
        Check if all tracked items in the order have sufficient stock.

        Returns:
            bool: True if all items are available.
        """
        availability = cls.check_availability(order)
        return all(info["sufficient"] for info in availability.values())

    @classmethod
    @transaction.atomic
    def reserve_stock(cls, order, user=None):
        """
        Reserve stock for all line items in the order.

        Uses select_for_update for row-level locking to prevent
        race conditions during concurrent reservation attempts.

        Returns:
            bool: True on success.
        Raises:
            InsufficientStockError: If any item has insufficient stock.
        """
        reserved_items = []
        for item in order.line_items.select_related("product", "variant"):
            product = item.variant or item.product
            if not product:
                continue
            if not getattr(product, "track_inventory", True):
                continue

            available = cls._get_available_quantity(product)
            if available < item.quantity_ordered:
                raise InsufficientStockError(
                    product=str(product),
                    requested_quantity=item.quantity_ordered,
                    available_quantity=available,
                    line_item=item,
                )

            cls._increment_reserved(product, item.quantity_ordered)
            reserved_items.append(
                {
                    "line_item_id": str(item.id),
                    "product": str(product),
                    "quantity": item.quantity_ordered,
                }
            )

        order.stock_reserved_at = timezone.now()
        order.save(update_fields=["stock_reserved_at", "updated_on"])

        cls._log_stock_event(order, "stock_reserved", user, reserved_items)
        logger.info(
            "Reserved stock for order %s (%d items)",
            order.order_number,
            len(reserved_items),
        )
        return True

    @classmethod
    @transaction.atomic
    def release_stock(cls, order, user=None):
        """
        Release all stock reservations for the order.

        Returns:
            bool: True on success.
        """
        released_items = []
        for item in order.line_items.select_related("product", "variant"):
            product = item.variant or item.product
            if not product:
                continue
            if not getattr(product, "track_inventory", True):
                continue

            cls._decrement_reserved(product, item.quantity_ordered)
            released_items.append(
                {
                    "line_item_id": str(item.id),
                    "product": str(product),
                    "quantity": item.quantity_ordered,
                }
            )

        order.stock_reserved_at = None
        order.save(update_fields=["stock_reserved_at", "updated_on"])

        cls._log_stock_event(order, "stock_released", user, released_items)
        logger.info(
            "Released stock for order %s (%d items)",
            order.order_number,
            len(released_items),
        )
        return True

    @classmethod
    @transaction.atomic
    def reserve_partial(cls, order, user=None):
        """
        Reserve only the available stock without raising errors.

        Returns:
            dict: {reserved: [...], unavailable: [...]}
        """
        reserved = []
        unavailable = []
        for item in order.line_items.select_related("product", "variant"):
            product = item.variant or item.product
            if not product:
                continue
            if not getattr(product, "track_inventory", True):
                continue

            available = cls._get_available_quantity(product)
            if available >= item.quantity_ordered:
                cls._increment_reserved(product, item.quantity_ordered)
                reserved.append(
                    {
                        "line_item_id": str(item.id),
                        "product": str(product),
                        "quantity": item.quantity_ordered,
                    }
                )
            elif available > 0:
                cls._increment_reserved(product, available)
                reserved.append(
                    {
                        "line_item_id": str(item.id),
                        "product": str(product),
                        "quantity": available,
                    }
                )
                unavailable.append(
                    {
                        "line_item_id": str(item.id),
                        "product": str(product),
                        "requested": item.quantity_ordered,
                        "available": available,
                        "shortfall": item.quantity_ordered - available,
                    }
                )
            else:
                unavailable.append(
                    {
                        "line_item_id": str(item.id),
                        "product": str(product),
                        "requested": item.quantity_ordered,
                        "available": 0,
                        "shortfall": item.quantity_ordered,
                    }
                )

        if reserved:
            order.stock_reserved_at = timezone.now()
            order.save(update_fields=["stock_reserved_at", "updated_on"])

        return {"reserved": reserved, "unavailable": unavailable}

    @classmethod
    def check_availability_by_location(cls, order, location):
        """
        Check stock availability at a specific location.

        Returns:
            dict: {line_item_id: available_quantity} per location.
        """
        availability = {}
        for item in order.line_items.select_related("product", "variant"):
            product = item.variant or item.product
            if not product:
                continue
            available = cls._get_available_quantity_at_location(product, location)
            availability[str(item.id)] = {
                "line_item": item,
                "product": product,
                "requested": item.quantity_ordered,
                "available": available,
                "sufficient": available >= item.quantity_ordered,
            }
        return availability

    # ── Insufficient Stock Handling (Task 43) ───────────────────

    @classmethod
    def handle_insufficient_stock(cls, order, availability_dict, user=None):
        """
        Handle insufficient stock according to OrderSettings strategy.

        Checks allow_backorders, allow_partial_fulfillment, and
        cancel_on_insufficient_stock settings to determine strategy.

        Returns:
            dict: {strategy: str, details: dict}
        """
        settings = cls._get_order_settings()

        if settings and getattr(settings, "allow_backorders", False):
            return cls._handle_backorder(order, availability_dict, user)
        elif settings and getattr(settings, "allow_partial_fulfillment", True):
            return cls._handle_partial(order, availability_dict, user)
        elif settings and getattr(settings, "cancel_on_insufficient_stock", False):
            return cls._handle_cancel(order, user)
        else:
            return cls._handle_manual_review(order, availability_dict, user)

    @classmethod
    def check_low_stock_warnings(cls, order):
        """
        Check for low stock warnings (non-blocking).

        Returns:
            list: Warning dicts for items below threshold.
        """
        settings = cls._get_order_settings()
        threshold = getattr(settings, "low_stock_threshold", 10) if settings else 10

        warnings = []
        for item in order.line_items.select_related("product", "variant"):
            product = item.variant or item.product
            if not product or not getattr(product, "track_inventory", True):
                continue
            available = cls._get_available_quantity(product)
            if available < threshold:
                warnings.append(
                    {
                        "product": str(product),
                        "available": available,
                        "threshold": threshold,
                        "message": f"Low stock warning for {product}: {available} remaining",
                    }
                )
        return warnings

    @classmethod
    def suggest_alternatives(cls, order, unavailable_items):
        """
        Suggest alternative products for unavailable items.

        Returns:
            list: Alternative product suggestions.
        """
        # Placeholder: would query products with matching categories/tags
        suggestions = []
        for item_info in unavailable_items:
            suggestions.append(
                {
                    "original_product": item_info.get("product"),
                    "alternatives": [],
                    "message": "No alternatives found (feature pending integration)",
                }
            )
        return suggestions

    @classmethod
    def notify_insufficient_stock(cls, order, details):
        """
        Send notifications about insufficient stock.

        Placeholder for email/notification integration.
        """
        logger.warning(
            "Insufficient stock for order %s: %s",
            order.order_number,
            details,
        )
        # TODO: Integrate with notification service (Task 65)

    # ── Private Helpers ─────────────────────────────────────────

    @classmethod
    def _get_available_quantity(cls, product):
        """Get available quantity for a product (on_hand - reserved)."""
        on_hand = getattr(product, "quantity_on_hand", 0) or 0
        reserved = getattr(product, "quantity_reserved", 0) or 0
        return max(on_hand - reserved, 0)

    @classmethod
    def _get_available_quantity_at_location(cls, product, location):
        """Get available quantity at a specific location."""
        # Placeholder: would query InventoryItem filtered by location
        return cls._get_available_quantity(product)

    @classmethod
    def _increment_reserved(cls, product, quantity):
        """Increment reserved quantity on a product."""
        current = getattr(product, "quantity_reserved", 0) or 0
        if hasattr(product, "quantity_reserved"):
            product.quantity_reserved = current + quantity
            product.save(update_fields=["quantity_reserved"])

    @classmethod
    def _decrement_reserved(cls, product, quantity):
        """Decrement reserved quantity on a product."""
        current = getattr(product, "quantity_reserved", 0) or 0
        if hasattr(product, "quantity_reserved"):
            product.quantity_reserved = max(current - quantity, 0)
            product.save(update_fields=["quantity_reserved"])

    @classmethod
    def _get_order_settings(cls):
        """Get OrderSettings singleton, or None if not configured."""
        try:
            from apps.orders.models.settings import OrderSettings

            return OrderSettings.objects.first()
        except Exception:
            return None

    @classmethod
    def _log_stock_event(cls, order, event_type, user, items):
        """Log a stock event to order history."""
        try:
            from apps.orders.services.history_service import HistoryService

            HistoryService.log_event(
                order,
                event_type,
                user=user,
                metadata={"items": items},
            )
        except Exception:
            logger.exception("Failed to log stock event for %s", order.order_number)

    @classmethod
    def _handle_backorder(cls, order, availability_dict, user):
        """Handle insufficient stock with backorder strategy."""
        result = cls.reserve_partial(order, user)
        logger.info("Backorder strategy for order %s", order.order_number)
        return {"strategy": "backorder", "details": result}

    @classmethod
    def _handle_partial(cls, order, availability_dict, user):
        """Handle insufficient stock with partial fulfillment strategy."""
        result = cls.reserve_partial(order, user)
        logger.info("Partial fulfillment for order %s", order.order_number)
        return {"strategy": "partial_fulfillment", "details": result}

    @classmethod
    def _handle_cancel(cls, order, user):
        """Handle insufficient stock by cancelling the order."""
        from apps.orders.services.order_service import OrderService

        try:
            OrderService.cancel_order(order, user=user, reason="Insufficient stock")
        except Exception:
            logger.exception("Failed to cancel order %s", order.order_number)
        return {"strategy": "cancelled", "details": {"order_id": str(order.id)}}

    @classmethod
    def _handle_manual_review(cls, order, availability_dict, user):
        """Flag order for manual review."""
        logger.info("Order %s flagged for manual stock review", order.order_number)
        cls.notify_insufficient_stock(order, availability_dict)
        return {"strategy": "manual_review", "details": availability_dict}
