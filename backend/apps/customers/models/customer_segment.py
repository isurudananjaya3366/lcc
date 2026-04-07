"""
CustomerSegment model for dynamic customer segmentation.

Segments define rule-based groups of customers. Rules are stored
as JSON and evaluated at runtime to determine membership.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class CustomerSegment(UUIDMixin, TimestampMixin, models.Model):
    """
    Dynamic customer segment defined by JSON rules.

    Rule format::

        {
            "conditions": [
                {"field": "total_purchases", "operator": "gte", "value": 100000},
                {"field": "status", "operator": "eq", "value": "active"}
            ],
            "logic": "AND"
        }
    """

    name = models.CharField(
        max_length=200,
        verbose_name="Segment Name",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
    )
    rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Segment Rules",
        help_text="JSON conditions and logic for segment membership.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
    )
    auto_assign = models.BooleanField(
        default=False,
        verbose_name="Auto-Assign",
        help_text="Automatically assign matching customers.",
    )
    customer_count = models.IntegerField(
        default=0,
        verbose_name="Customer Count",
        help_text="Cached count of matching customers.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_customer_segments",
        verbose_name="Created By",
    )

    class Meta:
        db_table = "customers_customer_segment"
        verbose_name = "Customer Segment"
        verbose_name_plural = "Customer Segments"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_customer_segment_name",
            ),
        ]
        indexes = [
            models.Index(
                fields=["is_active"],
                name="idx_segment_active",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.customer_count} customers)"
