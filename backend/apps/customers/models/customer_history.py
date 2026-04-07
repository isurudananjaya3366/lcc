"""
CustomerHistory model for the customers application.

Tracks changes to customer records for audit purposes. Each change
to a tracked field creates a history entry with the old and new values.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin


# Change type choices for history entries
CHANGE_TYPE_CREATE = "create"
CHANGE_TYPE_UPDATE = "update"
CHANGE_TYPE_DELETE = "delete"
CHANGE_TYPE_STATUS_CHANGE = "status_change"
CHANGE_TYPE_MERGE = "merge"

CHANGE_TYPE_CHOICES = [
    (CHANGE_TYPE_CREATE, "Created"),
    (CHANGE_TYPE_UPDATE, "Updated"),
    (CHANGE_TYPE_DELETE, "Deleted"),
    (CHANGE_TYPE_STATUS_CHANGE, "Status Change"),
    (CHANGE_TYPE_MERGE, "Merged"),
]


class CustomerHistory(UUIDMixin, models.Model):
    """
    Audit log entry for a customer record change.

    Stores the field name, old value, new value, and who made the
    change. Created automatically by the HistoryService when
    CustomerService modifies a customer.
    """

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name="Customer",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="customer_changes",
        verbose_name="Changed By",
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Changed At",
    )
    field_name = models.CharField(
        max_length=100,
        verbose_name="Field Name",
        help_text="Name of the field that was changed.",
    )
    old_value = models.TextField(
        blank=True,
        default="",
        verbose_name="Old Value",
    )
    new_value = models.TextField(
        blank=True,
        default="",
        verbose_name="New Value",
    )
    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES,
        default=CHANGE_TYPE_UPDATE,
        verbose_name="Change Type",
    )

    class Meta:
        db_table = "customers_customer_history"
        verbose_name = "Customer History"
        verbose_name_plural = "Customer History"
        ordering = ["-changed_at"]
        indexes = [
            models.Index(
                fields=["customer", "-changed_at"],
                name="idx_history_customer_date",
            ),
            models.Index(
                fields=["change_type"],
                name="idx_history_change_type",
            ),
            models.Index(
                fields=["changed_by"],
                name="idx_history_changed_by",
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_change_type_display()} – "
            f"{self.field_name} on {self.changed_at:%Y-%m-%d %H:%M}"
        )
