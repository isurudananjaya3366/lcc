"""Payment schedule model for vendor bills."""

from django.db import models

from apps.core.models import TimestampMixin, UUIDMixin
from apps.vendor_bills.constants import (
    SCHEDULE_STATUS_CHOICES,
    SCHEDULE_STATUS_SCHEDULED,
)


class PaymentSchedule(UUIDMixin, TimestampMixin, models.Model):
    """Tracks scheduled payments for vendor bills."""

    vendor_bill = models.ForeignKey(
        "vendor_bills.VendorBill",
        on_delete=models.CASCADE,
        related_name="payment_schedules",
    )
    scheduled_date = models.DateField(db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=SCHEDULE_STATUS_CHOICES,
        default=SCHEDULE_STATUS_SCHEDULED,
    )
    payment = models.ForeignKey(
        "vendor_bills.VendorPayment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedule_entries",
    )
    notes = models.TextField(blank=True, default="")
    reminder_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ["scheduled_date"]
        indexes = [
            models.Index(
                fields=["status", "scheduled_date"],
                name="idx_ps_status_date",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="chk_ps_amount_positive",
            ),
        ]

    def __str__(self):
        return (
            f"Schedule {self.scheduled_date} - "
            f"{self.amount} ({self.status})"
        )
