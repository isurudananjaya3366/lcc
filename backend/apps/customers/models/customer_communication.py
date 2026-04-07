"""
CustomerCommunication model for the customers application.

Tracks all interactions with a customer including emails, phone calls,
SMS messages, in-person visits, and internal notes.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.customers.constants import (
    COMMUNICATION_TYPE_CHOICES,
    COMMUNICATION_TYPE_NOTE,
)


class CustomerCommunication(UUIDMixin, TimestampMixin, models.Model):
    """
    Communication log entry for a customer interaction.

    Each record represents one interaction (email, call, SMS, visit,
    or note) with a customer. Supports optional references to related
    orders and invoices, plus follow-up scheduling.
    """

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="communications",
        verbose_name="Customer",
    )
    contacted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="customer_communications",
        verbose_name="Contacted By",
    )

    # ── Communication Details ───────────────────────────────────────
    communication_type = models.CharField(
        max_length=20,
        choices=COMMUNICATION_TYPE_CHOICES,
        default=COMMUNICATION_TYPE_NOTE,
        verbose_name="Type",
        help_text="Type of communication.",
    )
    subject = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Subject",
        help_text="Brief subject line for the communication.",
    )
    content = models.TextField(
        blank=True,
        default="",
        verbose_name="Content",
        help_text="Full communication content or notes.",
    )

    # ── Related References (optional) ───────────────────────────────
    related_order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="customer_communications",
        verbose_name="Related Order",
    )
    related_invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="customer_communications",
        verbose_name="Related Invoice",
    )

    # ── Date Fields ─────────────────────────────────────────────────
    communication_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Communication Date",
    )
    follow_up_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Follow-Up Date",
        help_text="Scheduled follow-up date.",
    )
    follow_up_completed = models.BooleanField(
        default=False,
        verbose_name="Follow-Up Completed",
    )

    class Meta:
        db_table = "customers_customer_communication"
        verbose_name = "Customer Communication"
        verbose_name_plural = "Customer Communications"
        ordering = ["-communication_date"]
        indexes = [
            models.Index(
                fields=["customer", "-communication_date"],
                name="idx_comm_customer_date",
            ),
            models.Index(
                fields=["communication_type"],
                name="idx_comm_type",
            ),
            models.Index(
                fields=["follow_up_date"],
                name="idx_comm_follow_up",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_communication_type_display()} – "
            f"{self.subject or '(no subject)'} "
            f"({self.communication_date:%Y-%m-%d})"
        )
