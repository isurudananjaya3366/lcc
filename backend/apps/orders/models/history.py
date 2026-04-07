"""
OrderHistory model for tracking all order lifecycle events (Task 47).
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class OrderHistory(UUIDMixin, TimestampMixin, models.Model):
    """
    Audit trail for order events.

    Records every significant event in an order's lifecycle,
    including status changes, edits, payments, fulfillment, etc.
    """

    # Event type choices
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    FIELD_UPDATED = "field_updated"
    LINE_ITEM_ADDED = "line_item_added"
    LINE_ITEM_UPDATED = "line_item_updated"
    LINE_ITEM_REMOVED = "line_item_removed"
    DISCOUNT_APPLIED = "discount_applied"
    DISCOUNT_REMOVED = "discount_removed"
    TAX_RECALCULATED = "tax_recalculated"
    TOTALS_RECALCULATED = "totals_recalculated"
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_REFUNDED = "payment_refunded"
    STOCK_RESERVED = "stock_reserved"
    STOCK_RELEASED = "stock_released"
    FULFILLMENT_STARTED = "fulfillment_started"
    FULFILLMENT_COMPLETED = "fulfillment_completed"
    SHIPMENT_CREATED = "shipment_created"
    NOTE_ADDED = "note_added"
    CUSTOMER_NOTIFIED = "customer_notified"
    DUPLICATED = "duplicated"
    CONVERTED_FROM_QUOTE = "converted_from_quote"
    CONVERTED_FROM_POS = "converted_from_pos"
    IMPORTED = "imported"
    LOCKED = "locked"
    UNLOCKED = "unlocked"

    EVENT_TYPE_CHOICES = [
        (CREATED, "Order Created"),
        (STATUS_CHANGED, "Status Changed"),
        (CONFIRMED, "Order Confirmed"),
        (PROCESSING, "Processing Started"),
        (SHIPPED, "Order Shipped"),
        (DELIVERED, "Order Delivered"),
        (COMPLETED, "Order Completed"),
        (CANCELLED, "Order Cancelled"),
        (RETURNED, "Order Returned"),
        (FIELD_UPDATED, "Field Updated"),
        (LINE_ITEM_ADDED, "Line Item Added"),
        (LINE_ITEM_UPDATED, "Line Item Updated"),
        (LINE_ITEM_REMOVED, "Line Item Removed"),
        (DISCOUNT_APPLIED, "Discount Applied"),
        (DISCOUNT_REMOVED, "Discount Removed"),
        (TAX_RECALCULATED, "Tax Recalculated"),
        (TOTALS_RECALCULATED, "Totals Recalculated"),
        (PAYMENT_RECEIVED, "Payment Received"),
        (PAYMENT_REFUNDED, "Payment Refunded"),
        (STOCK_RESERVED, "Stock Reserved"),
        (STOCK_RELEASED, "Stock Released"),
        (FULFILLMENT_STARTED, "Fulfillment Started"),
        (FULFILLMENT_COMPLETED, "Fulfillment Completed"),
        (SHIPMENT_CREATED, "Shipment Created"),
        (NOTE_ADDED, "Note Added"),
        (CUSTOMER_NOTIFIED, "Customer Notified"),
        (DUPLICATED, "Order Duplicated"),
        (CONVERTED_FROM_QUOTE, "Converted From Quote"),
        (CONVERTED_FROM_POS, "Converted From POS"),
        (IMPORTED, "Order Imported"),
        (LOCKED, "Order Locked"),
        (UNLOCKED, "Order Unlocked"),
    ]

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="history",
    )
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
    )
    description = models.TextField(blank=True, default="")

    # Change tracking
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    changes = models.JSONField(default=dict, blank=True)

    # Actor
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_history_actions",
    )
    actor_name = models.CharField(max_length=200, blank=True, default="")
    actor_email = models.EmailField(blank=True, default="")
    actor_role = models.CharField(max_length=100, blank=True, default="")

    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    session_id = models.CharField(max_length=100, blank=True, default="")

    # Event source
    HISTORY_SOURCE_CHOICES = [
        ("web", "Web"),
        ("api", "API"),
        ("system", "System"),
        ("import", "Import"),
    ]
    source = models.CharField(
        max_length=20,
        choices=HISTORY_SOURCE_CHOICES,
        default="system",
        blank=True,
    )

    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        db_table = "orders_orderhistory"
        verbose_name = "Order History"
        verbose_name_plural = "Order Histories"
        ordering = ["-created_on"]
        indexes = [
            models.Index(
                fields=["order", "-created_on"], name="idx_orderhist_order_date"
            ),
            models.Index(
                fields=["event_type"], name="idx_orderhist_event_type"
            ),
        ]

    def __str__(self):
        return f"{self.order.order_number} — {self.get_event_type_display()}"

    def get_changes_summary(self):
        """Format changes for display."""
        if self.changes:
            parts = []
            for field, change in self.changes.items():
                old = change.get("old", "")
                new = change.get("new", "")
                parts.append(f"{field}: {old} → {new}")
            return "; ".join(parts)
        return self.description or ""

    def get_actor_display(self):
        """Return actor name or 'System'."""
        return self.actor_name or "System"
