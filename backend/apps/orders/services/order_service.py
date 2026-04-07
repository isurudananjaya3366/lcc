"""
Order service for order creation, conversion, and management (Tasks 35-46).

Handles manual creation, quote-to-order conversion, POS order creation,
webstore orders, bulk import, duplication, editing, and lock management.
"""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.orders.constants import (
    ALLOWED_TRANSITIONS,
    CANCELLABLE_STATES,
    EDITABLE_STATES,
    OrderSource,
    OrderStatus,
    PaymentStatus,
)
from apps.orders.exceptions import (
    InvalidStatusTransition,
    OrderLockedError,
    OrderValidationError,
)

logger = logging.getLogger(__name__)


class OrderService:
    """
    Core service for all order operations.

    Follows the same pattern as QuoteService.
    """

    # ── Validation (Task 35) ────────────────────────────────────

    @classmethod
    def _validate_order_data(cls, data, items_data=None):
        """Validate order creation data."""
        if items_data is not None and not items_data:
            raise OrderValidationError("At least one line item is required.")

        if not data.get("customer") and not data.get("customer_name"):
            raise OrderValidationError(
                "Either a customer reference or customer_name is required."
            )

    @classmethod
    def _generate_order_number(cls):
        """Generate a unique order number."""
        from apps.orders.services.order_number_generator import OrderNumberGenerator

        return OrderNumberGenerator.generate()

    @classmethod
    def _create_line_items(cls, order, items_data):
        """Create line items from a list of dicts."""
        from apps.orders.models.order_item import OrderLineItem

        line_items = []
        for idx, item_data in enumerate(items_data, start=1):
            item = OrderLineItem(
                order=order,
                position=item_data.get("position", idx),
                product_id=item_data.get("product_id"),
                variant_id=item_data.get("variant_id"),
                item_name=item_data.get("item_name", ""),
                item_sku=item_data.get("item_sku", ""),
                item_description=item_data.get("item_description", ""),
                item_category=item_data.get("item_category", ""),
                quantity_ordered=item_data.get("quantity_ordered", 1),
                unit_price=item_data.get("unit_price", 0),
                original_price=item_data.get("original_price", 0),
                cost_price=item_data.get("cost_price", 0),
                discount_type=item_data.get("discount_type", ""),
                discount_value=item_data.get("discount_value", 0),
                is_taxable=item_data.get("is_taxable", True),
                tax_rate=item_data.get("tax_rate", 0),
                tax_code=item_data.get("tax_code", ""),
                notes=item_data.get("notes", ""),
            )
            # Snapshot product info if product linked but no name given
            if not item.item_name and (item.product_id or item.variant_id):
                item.snapshot_from_product()
            item.recalculate()
            line_items.append(item)

        OrderLineItem.objects.bulk_create(line_items)
        return line_items

    @classmethod
    def _calculate_order_totals(cls, order):
        """Run the full calculation pipeline."""
        from apps.orders.services.calculation_service import OrderCalculationService

        OrderCalculationService(order).calculate_all(save=True)

    @classmethod
    def _log_order_event(cls, order, event_type, user=None, **kwargs):
        """Log an event to order history."""
        from apps.orders.services.history_service import HistoryService

        return HistoryService.log_event(order, event_type, user=user, **kwargs)

    # ── Manual Creation (Task 36) ────────────────────────────────

    @classmethod
    @transaction.atomic
    def create_order(cls, data, items_data, user=None, auto_confirm=False):
        """
        Create an order manually.

        Args:
            data: dict with order-level fields
            items_data: list of dicts with line item fields
            user: creating user
            auto_confirm: if True, set status to CONFIRMED immediately

        Returns:
            Order instance
        """
        from apps.orders.models.order import Order

        cls._validate_order_data(data, items_data)

        order = Order(
            order_number=cls._generate_order_number(),
            status=OrderStatus.CONFIRMED if auto_confirm else OrderStatus.PENDING,
            source=data.get("source", OrderSource.MANUAL),
            priority=data.get("priority", 5),
            is_draft=data.get("is_draft", False),
            customer_id=data.get("customer_id") or data.get("customer"),
            customer_name=data.get("customer_name", ""),
            customer_email=data.get("customer_email", ""),
            customer_phone=data.get("customer_phone", ""),
            is_guest_order=data.get("is_guest_order", False),
            customer_notes=data.get("customer_notes", ""),
            shipping_address=data.get("shipping_address", {}),
            billing_address=data.get("billing_address", {}),
            shipping_method=data.get("shipping_method", ""),
            delivery_instructions=data.get("delivery_instructions", ""),
            notes=data.get("notes", ""),
            internal_notes=data.get("internal_notes", ""),
            tags=data.get("tags", []),
            currency=data.get("currency", "LKR"),
            created_by=user,
            order_date=timezone.now(),
        )
        if auto_confirm:
            order.confirmed_at = timezone.now()
            order.confirmed_by = user
        order.save()

        if items_data:
            cls._create_line_items(order, items_data)
            cls._calculate_order_totals(order)

        from apps.orders.services.history_service import HistoryService

        HistoryService.log_creation(order, user=user, source_detail="manual")

        return order

    # ── Quote Conversion (Task 37) ───────────────────────────────

    @classmethod
    @transaction.atomic
    def create_from_quote(cls, quote_id, user=None, auto_confirm=True):
        """
        Create an order from an accepted quote.

        Args:
            quote_id: UUID of the quote
            user: user performing the conversion
            auto_confirm: auto-confirm the resulting order

        Returns:
            Order instance
        """
        from apps.orders.models.order import Order
        from apps.orders.models.order_item import OrderLineItem
        from apps.quotes.models import Quote

        quote = (
            Quote.objects.prefetch_related("line_items__product", "line_items__variant")
            .select_for_update()
            .get(id=quote_id)
        )

        if hasattr(quote, "converted_to_order_id") and quote.converted_to_order_id:
            raise OrderValidationError("Quote has already been converted.")

        order = Order(
            order_number=cls._generate_order_number(),
            status=OrderStatus.CONFIRMED if auto_confirm else OrderStatus.PENDING,
            source=OrderSource.QUOTE,
            customer=quote.customer,
            customer_name=getattr(quote.customer, "full_name", "") if quote.customer else "",
            customer_email=getattr(quote.customer, "email", "") if quote.customer else "",
            notes=quote.notes or "",
            discount_type=quote.discount_type or "",
            discount_value=quote.discount_value or 0,
            currency=getattr(quote, "currency", "LKR") or "LKR",
            quote=quote,
            created_by=user,
            order_date=timezone.now(),
        )
        if auto_confirm:
            order.confirmed_at = timezone.now()
            order.confirmed_by = user
        order.save()

        # Copy line items from quote
        line_items = []
        for item in quote.line_items.order_by("position"):
            line_items.append(
                OrderLineItem(
                    order=order,
                    position=item.position,
                    product=item.product,
                    variant=getattr(item, "variant", None),
                    item_name=getattr(item, "product_name", "") or getattr(item, "item_name", ""),
                    item_sku=getattr(item, "sku", "") or getattr(item, "item_sku", ""),
                    item_description=getattr(item, "custom_description", "") or "",
                    quantity_ordered=getattr(item, "quantity", 1),
                    unit_price=item.unit_price,
                    discount_type=getattr(item, "discount_type", "") or "",
                    discount_value=getattr(item, "discount_value", 0) or 0,
                    is_taxable=getattr(item, "is_taxable", True),
                    tax_rate=getattr(item, "tax_rate", 0) or 0,
                )
            )
        OrderLineItem.objects.bulk_create(line_items)

        cls._calculate_order_totals(order)

        # Update quote status
        if hasattr(quote, "converted_to_order"):
            quote.converted_to_order = order
        quote.status = "CONVERTED"
        quote.converted_at = timezone.now()
        update_fields = ["status", "converted_at", "updated_on"]
        if hasattr(quote, "converted_to_order"):
            update_fields.append("converted_to_order")
        quote.save(update_fields=update_fields)

        from apps.orders.services.history_service import HistoryService

        HistoryService.log_creation(
            order, user=user, source_detail=f"from quote {quote.quote_number}"
        )

        return order

    # ── POS Order (Task 38) ──────────────────────────────────────

    @classmethod
    @transaction.atomic
    def create_from_pos(cls, session_id, cart_data, payment_data=None, user=None):
        """
        Create an order from a POS session.

        POS orders are auto-confirmed with immediate payment.

        Args:
            session_id: POS session UUID
            cart_data: dict with customer info and items
            payment_data: optional payment info
            user: POS operator

        Returns:
            Order instance
        """
        from apps.orders.models.order import Order

        items_data = cart_data.get("items", [])
        if not items_data:
            raise OrderValidationError("Cart is empty.")

        order = Order(
            order_number=cls._generate_order_number(),
            status=OrderStatus.CONFIRMED,
            source=OrderSource.POS,
            customer_id=cart_data.get("customer_id"),
            customer_name=cart_data.get("customer_name", "Walk-in Customer"),
            customer_phone=cart_data.get("customer_phone", ""),
            is_guest_order=not cart_data.get("customer_id"),
            pos_session_id=session_id,
            currency=cart_data.get("currency", "LKR"),
            created_by=user,
            confirmed_at=timezone.now(),
            confirmed_by=user,
            order_date=timezone.now(),
        )
        order.save()

        cls._create_line_items(order, items_data)
        cls._calculate_order_totals(order)

        # Handle immediate payment
        if payment_data:
            amount = Decimal(str(payment_data.get("amount", 0)))
            order.amount_paid = amount
            order.balance_due = order.total_amount - amount
            if order.balance_due <= 0:
                order.payment_status = PaymentStatus.PAID
                order.balance_due = Decimal("0")
            else:
                order.payment_status = PaymentStatus.PARTIAL
            order.save(update_fields=[
                "amount_paid", "balance_due", "payment_status", "updated_on"
            ])

        from apps.orders.services.history_service import HistoryService

        HistoryService.log_creation(order, user=user, source_detail="POS")

        return order

    # ── Webstore Order (Task 39) ─────────────────────────────────

    @classmethod
    @transaction.atomic
    def create_from_webstore(cls, cart_data, customer_id, shipping_data=None, user=None):
        """
        Create an order from a webstore cart.

        Args:
            cart_data: dict with items and cart metadata
            customer_id: customer UUID
            shipping_data: optional shipping info
            user: the authenticated webstore user

        Returns:
            Order instance
        """
        from apps.orders.models.order import Order

        items_data = cart_data.get("items", [])
        if not items_data:
            raise OrderValidationError("Cart is empty.")

        shipping_data = shipping_data or {}

        order = Order(
            order_number=cls._generate_order_number(),
            status=OrderStatus.PENDING,
            source=OrderSource.WEBSTORE,
            customer_id=customer_id,
            customer_notes=cart_data.get("notes", ""),
            shipping_address=shipping_data.get("shipping_address", {}),
            billing_address=shipping_data.get("billing_address", {}),
            shipping_method=shipping_data.get("shipping_method", ""),
            delivery_instructions=shipping_data.get("delivery_instructions", ""),
            currency=cart_data.get("currency", "LKR"),
            created_by=user,
            order_date=timezone.now(),
        )
        order.save()

        cls._create_line_items(order, items_data)

        # Apply shipping if provided
        if shipping_data.get("shipping_amount"):
            order.shipping_amount = Decimal(str(shipping_data["shipping_amount"]))
            order.save(update_fields=["shipping_amount", "updated_on"])

        cls._calculate_order_totals(order)

        from apps.orders.services.history_service import HistoryService

        HistoryService.log_creation(order, user=user, source_detail="webstore")

        return order

    # ── Status Transitions ───────────────────────────────────────

    @classmethod
    @transaction.atomic
    def transition_status(cls, order, new_status, user=None, notes="", request=None):
        """
        Transition an order to a new status.

        Validates the transition and records history.
        """
        old_status = order.status
        allowed = ALLOWED_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise InvalidStatusTransition(
                f"Cannot transition from '{old_status}' to '{new_status}'. "
                f"Allowed: {[s.value for s in allowed]}"
            )

        order.status = new_status
        now = timezone.now()

        # Set timestamp fields
        status_timestamps = {
            OrderStatus.CONFIRMED: "confirmed_at",
            OrderStatus.SHIPPED: "shipped_at",
            OrderStatus.DELIVERED: "delivered_at",
            OrderStatus.COMPLETED: "completed_at",
            OrderStatus.CANCELLED: "cancelled_at",
        }
        ts_field = status_timestamps.get(new_status)
        if ts_field:
            setattr(order, ts_field, now)

        # Set user fields
        status_users = {
            OrderStatus.CONFIRMED: "confirmed_by",
            OrderStatus.SHIPPED: "shipped_by",
            OrderStatus.CANCELLED: "cancelled_by",
        }
        user_field = status_users.get(new_status)
        if user_field and user:
            setattr(order, user_field, user)

        update_fields = ["status", "updated_on"]
        if ts_field:
            update_fields.append(ts_field)
        if user_field and user:
            update_fields.append(user_field)

        order.save(update_fields=update_fields)

        from apps.orders.services.history_service import HistoryService

        HistoryService.log_status_change(
            order, old_status, new_status, user=user, notes=notes, request=request
        )

        return order

    # ── Order Duplication (Task 44) ──────────────────────────────

    @classmethod
    @transaction.atomic
    def duplicate_order(cls, order_id, user=None, modifications=None):
        """
        Duplicate an existing order with fresh pricing.

        Args:
            order_id: UUID of the order to duplicate
            user: user performing the duplication
            modifications: optional dict of field overrides

        Returns:
            New Order instance
        """
        from apps.orders.models.order import Order
        from apps.orders.models.order_item import OrderLineItem

        source_order = Order.objects.prefetch_related(
            "line_items__product", "line_items__variant"
        ).get(id=order_id)

        modifications = modifications or {}

        new_order = Order(
            order_number=cls._generate_order_number(),
            status=OrderStatus.PENDING,
            source=source_order.source,
            priority=modifications.get("priority", source_order.priority),
            customer=source_order.customer,
            customer_name=source_order.customer_name,
            customer_email=source_order.customer_email,
            customer_phone=source_order.customer_phone,
            is_guest_order=source_order.is_guest_order,
            shipping_address=modifications.get(
                "shipping_address", source_order.shipping_address
            ),
            billing_address=modifications.get(
                "billing_address", source_order.billing_address
            ),
            shipping_method=source_order.shipping_method,
            delivery_instructions=source_order.delivery_instructions,
            notes=modifications.get("notes", ""),
            internal_notes=f"Duplicated from {source_order.order_number}",
            currency=source_order.currency,
            created_by=user,
            duplicated_from=source_order,
            order_date=timezone.now(),
        )
        new_order.save()

        # Copy line items with current pricing
        line_items = []
        for item in source_order.line_items.order_by("position"):
            new_item = OrderLineItem(
                order=new_order,
                position=item.position,
                product=item.product,
                variant=item.variant,
                item_name=item.item_name,
                item_sku=item.item_sku,
                item_description=item.item_description,
                item_category=item.item_category,
                quantity_ordered=item.quantity_ordered,
                unit_price=item.unit_price,
                original_price=item.original_price,
                cost_price=item.cost_price,
                discount_type=item.discount_type,
                discount_value=item.discount_value,
                is_taxable=item.is_taxable,
                tax_rate=item.tax_rate,
                tax_code=item.tax_code,
            )
            new_item.recalculate()
            line_items.append(new_item)
        OrderLineItem.objects.bulk_create(line_items)

        cls._calculate_order_totals(new_order)

        from apps.orders.services.history_service import HistoryService

        HistoryService.log_event(
            new_order,
            "duplicated",
            user=user,
            description=f"Duplicated from {source_order.order_number}",
            metadata={"source_order_id": str(source_order.id)},
        )

        return new_order

    # ── Order Editing (Task 45) ──────────────────────────────────

    @classmethod
    @transaction.atomic
    def edit_order(cls, order_id, data=None, items_data=None, user=None):
        """
        Edit an existing order.

        Only allowed for orders in editable states and not locked.

        Args:
            order_id: UUID of the order
            data: dict of order-level field updates
            items_data: optional new line items (replaces existing)
            user: user performing the edit

        Returns:
            Updated Order instance
        """
        from apps.orders.models.order import Order

        order = Order.objects.select_for_update().get(id=order_id)

        if not order.is_editable:
            raise OrderLockedError(
                f"Order {order.order_number} cannot be edited "
                f"(status: {order.status}, locked: {order.is_locked})."
            )

        data = data or {}
        field_changes = {}

        editable_fields = cls.get_editable_fields(order)

        for field, value in data.items():
            if field not in editable_fields:
                continue
            old_value = getattr(order, field, None)
            if old_value != value:
                field_changes[field] = {"old": str(old_value), "new": str(value)}
                setattr(order, field, value)

        if field_changes:
            order.save()

        if items_data is not None:
            order.line_items.all().delete()
            cls._create_line_items(order, items_data)

        cls._calculate_order_totals(order)

        if field_changes:
            from apps.orders.services.history_service import HistoryService

            HistoryService.log_field_update(order, field_changes, user=user)

        return order

    # ── Lock Management (Task 46) ────────────────────────────────

    @classmethod
    def get_editable_fields(cls, order):
        """Return the set of fields editable for the current order state."""
        if order.status not in EDITABLE_STATES:
            return set()

        always_editable = {
            "notes",
            "internal_notes",
            "tags",
            "customer_notes",
            "delivery_instructions",
        }
        if order.status == OrderStatus.PENDING:
            return always_editable | {
                "customer_id",
                "customer_name",
                "customer_email",
                "customer_phone",
                "shipping_address",
                "billing_address",
                "shipping_method",
                "discount_type",
                "discount_value",
                "priority",
                "assigned_to",
            }
        # CONFIRMED state: fewer editable fields
        return always_editable | {"assigned_to", "priority"}

    @classmethod
    @transaction.atomic
    def lock_order(cls, order, user=None, reason="", notes=""):
        """Lock an order to prevent editing."""
        order.is_locked = True
        order.locked_at = timezone.now()
        order.locked_by = user
        order.lock_reason = reason
        order.lock_notes = notes
        order.save(update_fields=[
            "is_locked", "locked_at", "locked_by",
            "lock_reason", "lock_notes", "updated_on",
        ])

        from apps.orders.services.history_service import HistoryService

        HistoryService.log_event(order, "locked", user=user, notes=notes)
        return order

    @classmethod
    @transaction.atomic
    def unlock_order(cls, order, user=None, reason=""):
        """Unlock an order to allow editing."""
        order.is_locked = False
        order.locked_at = None
        order.locked_by = None
        order.lock_reason = ""
        order.lock_notes = reason
        order.save(update_fields=[
            "is_locked", "locked_at", "locked_by",
            "lock_reason", "lock_notes", "updated_on",
        ])

        from apps.orders.services.history_service import HistoryService

        HistoryService.log_event(order, "unlocked", user=user)
        return order

    @classmethod
    def can_edit(cls, order, user=None):
        """Check if an order can be edited by the given user."""
        if order.is_locked:
            return False
        if order.status not in EDITABLE_STATES:
            return False
        return True

    # ── Cancellation ─────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def cancel_order(cls, order, user=None, reason="", request=None):
        """Cancel an order."""
        if order.status not in CANCELLABLE_STATES:
            raise InvalidStatusTransition(
                f"Cannot cancel order in '{order.status}' status."
            )
        return cls.transition_status(
            order,
            OrderStatus.CANCELLED,
            user=user,
            notes=reason,
            request=request,
        )

    # ── Bulk Import (Task 40) ────────────────────────────────────

    @classmethod
    def import_orders(cls, file, user, source="IMPORT"):
        """
        Import orders from a CSV or Excel file.

        Args:
            file: UploadedFile (CSV or Excel).
            user: User performing the import.
            source: Source identifier (default: 'IMPORT').

        Returns:
            dict: Import results with success, failed, and summary.
        """
        from apps.orders.services.import_service import ImportService

        return ImportService.execute_import(file, user)
