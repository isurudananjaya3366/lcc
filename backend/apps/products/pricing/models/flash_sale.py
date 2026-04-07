"""
FlashSale model – time-limited, quantity-limited promotional pricing.

Inherits from ScheduledPrice and adds stock tracking + urgency logic.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class FlashSale(models.Model):
    """
    Proxy-style extension of ScheduledPrice with quantity limits.

    Uses a separate table (multi-table inheritance) to keep the flash-sale-
    specific columns isolated.
    """

    # We import here to avoid circular import at module level.
    from .scheduled_price import ScheduledPrice  # noqa: F811

    scheduled_price = models.OneToOneField(
        "pricing.ScheduledPrice",
        on_delete=models.CASCADE,
        related_name="flash_sale_detail",
        primary_key=True,
    )
    max_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    quantity_sold = models.PositiveIntegerField(default=0)
    is_sold_out = models.BooleanField(default=False)

    class Meta:
        db_table = "pricing_flash_sale"
        verbose_name = "Flash Sale"
        verbose_name_plural = "Flash Sales"

    def __str__(self):
        return f"Flash Sale: {self.scheduled_price.name} ({self.quantity_remaining} remaining)"

    # ── Delegate common attrs to scheduled_price ───────────────

    def _sp(self):
        return self.scheduled_price

    @property
    def name(self):
        return self._sp().name

    @property
    def sale_price(self):
        return self._sp().sale_price

    @property
    def start_datetime(self):
        return self._sp().start_datetime

    @property
    def end_datetime(self):
        return self._sp().end_datetime

    @property
    def status(self):
        return self._sp().status

    @property
    def priority(self):
        return self._sp().priority

    @property
    def is_active_now(self):
        return self._sp().is_active_now

    @property
    def product(self):
        return self._sp().product

    @property
    def variant(self):
        return self._sp().variant

    # ── Flash-sale specific properties ─────────────────────────

    @property
    def quantity_remaining(self) -> int:
        return max(0, self.max_quantity - self.quantity_sold)

    @property
    def percent_sold(self) -> float:
        if not self.max_quantity:
            return 0.0
        return round((self.quantity_sold / self.max_quantity) * 100, 1)

    @property
    def time_remaining(self):
        if self.is_active_now:
            return self._sp().end_datetime - timezone.now()
        return timedelta(0)

    @property
    def urgency_level(self) -> str:
        if self.is_sold_out or self.percent_sold >= 90:
            return "critical"
        hours_left = self.time_remaining.total_seconds() / 3600 if self.time_remaining else 0
        if hours_left <= 1:
            return "critical"
        if self.percent_sold >= 75 or hours_left <= 3:
            return "high"
        if hours_left <= 6:
            return "medium"
        return "low"

    # ── Methods ────────────────────────────────────────────────

    def increment_sold(self, quantity: int = 1) -> bool:
        """Increment quantity_sold. Returns False if would exceed max."""
        if self.quantity_sold + quantity > self.max_quantity:
            return False
        self.quantity_sold += quantity
        if self.quantity_sold >= self.max_quantity:
            self.is_sold_out = True
            sp = self._sp()
            sp.status = sp.Status.EXPIRED
            sp.save(update_fields=["status", "updated_on"])
        self.save(update_fields=["quantity_sold", "is_sold_out"])
        return True

    def get_urgency_message(self) -> str:
        if self.is_sold_out:
            return "SOLD OUT"
        if not self.is_active_now:
            return "Sale Ended"
        if self.quantity_remaining <= 5:
            return f"Only {self.quantity_remaining} left!"
        if self.percent_sold >= 75:
            remaining_pct = 100 - self.percent_sold
            return f"{remaining_pct:.0f}% left!"
        hours_left = self.time_remaining.total_seconds() / 3600
        if hours_left < 1:
            minutes = int(self.time_remaining.total_seconds() / 60)
            return f"Ends in {minutes} minutes!"
        if hours_left < 24:
            return f"Ends in {int(hours_left)} hours!"
        return f"Ends {self._sp().end_datetime.strftime('%b %d')}"

    def clean(self):
        sp = self._sp()
        if sp.start_datetime and sp.end_datetime:
            duration = sp.end_datetime - sp.start_datetime
            if duration > timedelta(days=3):
                raise ValidationError({"max_quantity": "Flash sales cannot exceed 3 days."})
        if self.quantity_sold > self.max_quantity:
            raise ValidationError({"quantity_sold": "Sold quantity exceeds maximum."})

    def save(self, *args, **kwargs):
        # Ensure high priority on the parent ScheduledPrice
        sp = self._sp()
        if sp.priority < 100:
            sp.priority = 100
            sp.save(update_fields=["priority", "updated_on"])
        if self.quantity_sold >= self.max_quantity:
            self.is_sold_out = True
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)
