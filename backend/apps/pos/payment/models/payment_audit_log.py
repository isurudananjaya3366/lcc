"""
PaymentAuditLog — immutable audit trail for payment events.
"""

import logging

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.pos.constants import PAYMENT_EVENT_CHOICES

logger = logging.getLogger(__name__)


class PaymentAuditLog(models.Model):
    """Immutable log of payment-related events for audit and compliance."""

    event_type = models.CharField(
        max_length=30,
        choices=PAYMENT_EVENT_CHOICES,
        verbose_name=_("Event Type"),
    )
    cart = models.ForeignKey(
        "pos.POSCart",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("Cart"),
    )
    payment = models.ForeignKey(
        "pos.POSPayment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("Payment"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment_audit_logs",
        verbose_name=_("User"),
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP Address"),
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Details"),
    )
    success = models.BooleanField(
        default=True,
        verbose_name=_("Success"),
    )
    error_message = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Error Message"),
    )

    class Meta:
        db_table = "pos_payment_audit_log"
        ordering = ["-timestamp"]
        verbose_name = _("Payment Audit Log")
        verbose_name_plural = _("Payment Audit Logs")
        indexes = [
            models.Index(fields=["cart", "-timestamp"], name="pos_audit_cart"),
            models.Index(fields=["event_type", "-timestamp"], name="pos_audit_event"),
        ]

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"


def log_payment_event(
    event_type,
    *,
    cart=None,
    payment=None,
    user=None,
    ip_address=None,
    details=None,
    success=True,
    error_message="",
):
    """Create a payment audit log entry (best-effort, never raises)."""
    try:
        PaymentAuditLog.objects.create(
            event_type=event_type,
            cart=cart,
            payment=payment,
            user=user,
            ip_address=ip_address,
            details=details or {},
            success=success,
            error_message=error_message,
        )
    except Exception:
        logger.exception("Failed to create payment audit log: %s", event_type)
