"""
CustomerTag and CustomerTagAssignment models.

Provides a flexible tagging system for organising and categorising
customers. Tags have a name, colour, and optional description. The
many-to-many relationship is modelled explicitly via
CustomerTagAssignment to track who assigned each tag and when.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class CustomerTag(UUIDMixin, TimestampMixin, models.Model):
    """
    Reusable label that can be assigned to customers.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Tag Name",
        help_text="Unique tag name within this tenant.",
    )
    color = models.CharField(
        max_length=7,
        default="#808080",
        verbose_name="Colour",
        help_text="Hex colour code for visual display (#RRGGBB).",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_customer_tags",
        verbose_name="Created By",
    )

    class Meta:
        db_table = "customers_customer_tag"
        verbose_name = "Customer Tag"
        verbose_name_plural = "Customer Tags"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_customer_tag_name",
            ),
        ]

    def __str__(self):
        return self.name


class CustomerTagAssignment(UUIDMixin, models.Model):
    """
    Explicit many-to-many join between Customer and CustomerTag.
    """

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="tag_assignments",
        verbose_name="Customer",
    )
    tag = models.ForeignKey(
        "customers.CustomerTag",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Tag",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="customer_tag_assignments",
        verbose_name="Assigned By",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Assigned At",
    )

    class Meta:
        db_table = "customers_customer_tag_assignment"
        verbose_name = "Tag Assignment"
        verbose_name_plural = "Tag Assignments"
        ordering = ["-assigned_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "tag"],
                name="unique_customer_tag_assignment",
            ),
        ]
        indexes = [
            models.Index(
                fields=["customer"],
                name="idx_tagassign_customer",
            ),
            models.Index(
                fields=["tag"],
                name="idx_tagassign_tag",
            ),
        ]

    def __str__(self):
        return f"{self.customer} → {self.tag}"
