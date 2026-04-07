"""
Order history service for logging all order lifecycle events (Task 48).
"""

import logging

logger = logging.getLogger(__name__)


class HistoryService:
    """
    Logs events to OrderHistory.

    Provides specialized methods for common event types and handles
    actor snapshot, request metadata extraction, and change diffing.
    """

    @classmethod
    def log_event(
        cls,
        order,
        event_type,
        user=None,
        description="",
        old_values=None,
        new_values=None,
        changes=None,
        notes="",
        request=None,
        metadata=None,
    ):
        """Create an OrderHistory entry."""
        from apps.orders.models.history import OrderHistory

        entry = OrderHistory(
            order=order,
            event_type=event_type,
            description=description,
            old_values=old_values or {},
            new_values=new_values or {},
            changes=changes or {},
            notes=notes,
            metadata=metadata or {},
        )

        if user:
            entry.actor = user
            entry.actor_name = getattr(user, "get_full_name", lambda: str(user))()
            entry.actor_email = getattr(user, "email", "")

        if request:
            entry.ip_address = cls._get_client_ip(request)
            entry.user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
            entry.session_id = getattr(
                getattr(request, "session", None), "session_key", ""
            ) or ""

        entry.save()
        return entry

    @classmethod
    def log_creation(cls, order, user=None, source_detail="", **kwargs):
        """Log order creation."""
        desc = f"Order {order.order_number} created"
        if source_detail:
            desc += f" ({source_detail})"
        return cls.log_event(
            order,
            "created",
            user=user,
            description=desc,
            new_values={
                "order_number": order.order_number,
                "status": order.status,
                "source": order.source,
            },
            **kwargs,
        )

    @classmethod
    def log_status_change(cls, order, old_status, new_status, user=None, **kwargs):
        """Log a status transition."""
        return cls.log_event(
            order,
            "status_changed",
            user=user,
            description=f"Status changed from {old_status} to {new_status}",
            old_values={"status": old_status},
            new_values={"status": new_status},
            **kwargs,
        )

    @classmethod
    def log_field_update(cls, order, field_changes, user=None, **kwargs):
        """Log field-level updates."""
        old_vals = {k: v["old"] for k, v in field_changes.items()}
        new_vals = {k: v["new"] for k, v in field_changes.items()}
        fields_str = ", ".join(field_changes.keys())
        return cls.log_event(
            order,
            "field_updated",
            user=user,
            description=f"Updated fields: {fields_str}",
            old_values=old_vals,
            new_values=new_vals,
            changes=field_changes,
            **kwargs,
        )

    @classmethod
    def log_payment(cls, order, amount, payment_type="received", user=None, **kwargs):
        """Log a payment event."""
        event_type = "payment_received" if payment_type == "received" else "payment_refunded"
        return cls.log_event(
            order,
            event_type,
            user=user,
            description=f"Payment {payment_type}: {amount}",
            new_values={
                "amount": str(amount),
                "payment_status": order.payment_status,
                "amount_paid": str(order.amount_paid),
            },
            **kwargs,
        )

    @classmethod
    def log_shipment(cls, order, tracking_number="", user=None, **kwargs):
        """Log shipment creation."""
        return cls.log_event(
            order,
            "shipment_created",
            user=user,
            description=f"Shipment created. Tracking: {tracking_number or 'N/A'}",
            new_values={"tracking_number": tracking_number},
            **kwargs,
        )

    @classmethod
    def log_cancellation(cls, order, reason="", user=None, **kwargs):
        """Log order cancellation."""
        return cls.log_event(
            order,
            "cancelled",
            user=user,
            description=f"Order cancelled. Reason: {reason or 'Not specified'}",
            new_values={"status": "cancelled", "reason": reason},
            **kwargs,
        )

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
