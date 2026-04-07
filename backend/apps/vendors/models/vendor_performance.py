"""VendorPerformance model for tracking vendor performance metrics."""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class VendorPerformance(UUIDMixin, TimestampMixin, models.Model):
    """Performance metrics record for a vendor over a period."""

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.CASCADE,
        related_name="performance_records",
    )

    # Metrics
    on_time_delivery_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        help_text="On-time delivery percentage (0-100).",
    )
    quality_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        help_text="Quality score percentage (0-100).",
    )
    avg_response_time_hours = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        help_text="Average response time in hours.",
    )
    overall_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal("0.00"),
        help_text="Overall rating (0.00-5.00).",
    )

    # Order metrics
    total_orders_count = models.IntegerField(default=0)
    orders_on_time = models.IntegerField(default=0)
    orders_late = models.IntegerField(default=0)

    # Quality metrics
    items_received = models.IntegerField(default=0)
    items_defective = models.IntegerField(default=0)

    # Period
    period_start = models.DateField()
    period_end = models.DateField()

    # Calculation metadata
    calculated_at = models.DateTimeField(null=True, blank=True)
    calculated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendor_perf_calculations",
    )

    class Meta:
        db_table = "vendors_vendor_performance"
        verbose_name = "Vendor Performance"
        verbose_name_plural = "Vendor Performance Records"
        ordering = ["-period_start"]
        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "period_start", "period_end"],
                name="uq_vendor_performance_period",
            ),
        ]

    def __str__(self):
        return (
            f"{self.vendor.company_name} "
            f"({self.period_start} to {self.period_end})"
        )
