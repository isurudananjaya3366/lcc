"""
Order number generator service.

Generates unique order numbers in format ORD-YYYY-NNNNN.
"""

from django.db import models, transaction
from django.utils import timezone


class OrderSequence(models.Model):
    """Tracks the yearly order number sequence per tenant."""

    year = models.IntegerField()
    last_number = models.IntegerField(default=0)

    class Meta:
        app_label = "orders"
        db_table = "orders_ordersequence"
        unique_together = [("year",)]

    def __str__(self):
        return f"OrderSequence({self.year}: {self.last_number})"


class OrderNumberGenerator:
    """Generates unique order numbers: ORD-YYYY-NNNNN."""

    PREFIX = "ORD"

    @classmethod
    def generate(cls):
        year = timezone.now().year
        with transaction.atomic():
            seq, _ = OrderSequence.objects.select_for_update().get_or_create(
                year=year, defaults={"last_number": 0}
            )
            seq.last_number += 1
            seq.save(update_fields=["last_number"])
            return f"{cls.PREFIX}-{year}-{seq.last_number:05d}"
