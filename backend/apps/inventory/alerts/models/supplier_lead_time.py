"""
Supplier Lead Time tracking model.

Task 65: Track supplier delivery performance to improve
reorder point calculations and supplier selection.
"""

import logging
from datetime import timedelta

from django.db import models
from django.db.models import Avg, Max, Min, StdDev
from django.utils import timezone

logger = logging.getLogger(__name__)


class SupplierLeadTimeManager(models.Manager):
    """Manager for SupplierLeadTimeLog queries."""

    def for_supplier(self, supplier):
        """Get lead time logs for a specific supplier."""
        return self.filter(supplier=supplier).order_by("-ordered_date")

    def for_product(self, product, supplier=None):
        """Get lead time logs for a specific product, optionally filtered by supplier."""
        qs = self.filter(product=product)
        if supplier:
            qs = qs.filter(supplier=supplier)
        return qs.order_by("-ordered_date")

    def get_supplier_stats(self, supplier, months=12):
        """Calculate delivery performance statistics for a supplier."""
        cutoff = timezone.now() - timedelta(days=months * 30)
        qs = self.filter(
            supplier=supplier,
            actual_delivery_date__isnull=False,
            ordered_date__gte=cutoff,
        )

        if not qs.exists():
            return None

        stats = qs.aggregate(
            avg_days=Avg("days_taken"),
            min_days=Min("days_taken"),
            max_days=Max("days_taken"),
            std_dev=StdDev("days_taken"),
            total_deliveries=models.Count("id"),
            on_time_count=models.Count("id", filter=models.Q(on_time=True)),
        )

        total = stats["total_deliveries"] or 1
        stats["on_time_rate"] = round((stats["on_time_count"] / total) * 100, 2)

        return stats

    def get_lead_time_for_product(self, product, supplier):
        """Get average lead time for a specific product-supplier combination."""
        qs = self.filter(
            product=product,
            supplier=supplier,
            actual_delivery_date__isnull=False,
        ).order_by("-ordered_date")[:10]  # Last 10 deliveries

        if not qs.exists():
            return None

        avg = qs.aggregate(avg_days=Avg("days_taken"))
        return avg["avg_days"]


class SupplierLeadTimeLog(models.Model):
    """
    Tracks actual delivery times from suppliers.

    Used to calculate average lead times for reorder point
    calculations and supplier ranking.
    """

    supplier = models.ForeignKey(
        "vendors.Supplier",
        on_delete=models.CASCADE,
        related_name="lead_time_logs",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="lead_time_logs",
        null=True,
        blank=True,
        help_text="Specific product (null for general supplier tracking).",
    )
    purchase_order_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Reference to the purchase order.",
    )
    ordered_date = models.DateField(
        help_text="Date the PO was placed.",
    )
    expected_delivery_date = models.DateField(
        null=True,
        blank=True,
        help_text="Original expected delivery date.",
    )
    actual_delivery_date = models.DateField(
        null=True,
        blank=True,
        help_text="Actual date goods were received.",
    )
    days_taken = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        help_text="Actual days from order to delivery.",
    )
    days_late = models.IntegerField(
        default=0,
        editable=False,
        help_text="Days late vs expected (negative = early).",
    )
    on_time = models.BooleanField(
        default=True,
        editable=False,
        help_text="Whether delivery was on time.",
    )
    notes = models.TextField(
        blank=True,
        default="",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SupplierLeadTimeManager()

    class Meta:
        verbose_name = "Supplier Lead Time Log"
        verbose_name_plural = "Supplier Lead Time Logs"
        db_table = "inventory_supplier_lead_time_log"
        ordering = ["-ordered_date"]
        indexes = [
            models.Index(fields=["supplier", "-ordered_date"]),
            models.Index(fields=["product", "supplier"]),
        ]

    def __str__(self):
        return (
            f"{self.supplier} - {self.ordered_date} "
            f"({self.days_taken or '?'} days)"
        )

    def save(self, *args, **kwargs):
        if self.actual_delivery_date and self.ordered_date:
            delta = self.actual_delivery_date - self.ordered_date
            self.days_taken = max(delta.days, 0)

            if self.expected_delivery_date:
                late_delta = self.actual_delivery_date - self.expected_delivery_date
                self.days_late = late_delta.days
                self.on_time = self.days_late <= 0
            else:
                self.days_late = 0
                self.on_time = True

        super().save(*args, **kwargs)

    @classmethod
    def record_delivery(cls, supplier, ordered_date, actual_delivery_date,
                        expected_delivery_date=None, product=None,
                        purchase_order_id=None, notes=""):
        """Record a PO delivery for lead time tracking."""
        return cls.objects.create(
            supplier=supplier,
            product=product,
            purchase_order_id=purchase_order_id,
            ordered_date=ordered_date,
            expected_delivery_date=expected_delivery_date,
            actual_delivery_date=actual_delivery_date,
            notes=notes,
        )
