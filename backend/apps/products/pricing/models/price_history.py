"""
PriceHistory model – audit trail for every price change.

Uses a GenericForeignKey so the same model can track changes to
both ``ProductPrice`` and ``VariantPrice`` (and any future priceable
entity).  Direct FKs to product and variant are also stored for
convenient querying.
"""

from decimal import Decimal

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.core.models import BaseModel

from ..constants import CHANGE_SOURCE_CHOICES, PRICE_TYPE_CHOICES
from ..fields import PriceField


class PriceHistory(BaseModel):
    """
    Immutable audit record of a price change.
    """

    # ── Generic relation to the priceable entity ───────────────
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Content Type",
    )
    object_id = models.UUIDField(verbose_name="Object ID")
    content_object = GenericForeignKey("content_type", "object_id")

    # ── Convenience FKs ────────────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="price_history",
        verbose_name="Product",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="price_history",
        verbose_name="Variant",
    )

    # ── Change data ────────────────────────────────────────────
    price_type = models.CharField(
        max_length=20,
        choices=PRICE_TYPE_CHOICES,
        verbose_name="Price Type",
        help_text="Which price field changed.",
    )
    old_value = PriceField(
        null=True,
        blank=True,
        verbose_name="Old Value",
    )
    new_value = PriceField(
        null=True,
        blank=True,
        verbose_name="New Value",
    )
    change_amount = PriceField(
        null=True,
        blank=True,
        verbose_name="Change Amount",
        help_text="new_value − old_value",
    )
    change_percentage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Change %",
    )

    # ── Meta ───────────────────────────────────────────────────
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="price_changes",
        verbose_name="Changed By",
    )
    change_reason = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Change Reason",
    )
    automated_change = models.BooleanField(
        default=False,
        verbose_name="Automated Change",
        help_text="True if this change was made by a scheduled task or signal.",
    )
    change_source = models.CharField(
        max_length=20,
        choices=CHANGE_SOURCE_CHOICES,
        default="manual",
        verbose_name="Change Source",
    )

    class Meta:
        db_table = "pricing_price_history"
        verbose_name = "Price History"
        verbose_name_plural = "Price Histories"
        ordering = ["-created_on"]
        indexes = [
            models.Index(
                fields=["content_type", "object_id"],
                name="idx_ph_ct_oid",
            ),
            models.Index(fields=["product"], name="idx_ph_product"),
            models.Index(fields=["price_type"], name="idx_ph_ptype"),
            models.Index(fields=["created_on"], name="idx_ph_created"),
        ]

    def __str__(self):
        return (
            f"{self.price_type} change on "
            f"{getattr(self.product, 'name', '?')}: "
            f"{self.old_value} → {self.new_value}"
        )

    def save(self, *args, **kwargs):
        """Auto-compute change_amount and change_percentage on save."""
        if self.old_value is not None and self.new_value is not None:
            self.change_amount = self.new_value - self.old_value
            if self.old_value != Decimal("0"):
                self.change_percentage = (
                    (self.new_value - self.old_value) / self.old_value * 100
                ).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)
