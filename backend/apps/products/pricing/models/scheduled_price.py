"""
ScheduledPrice model – time-bound price overrides for products / variants.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.core.models import BaseModel

from ..fields import PriceField


class ScheduledPrice(BaseModel):
    """
    A scheduled price override that activates/deactivates based on date-time range.

    Priority ladder (highest wins):
        Flash Sale (100+) > Scheduled (50-99) > Promotional (0-49) > Sale Price > Base Price
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending (Not Started)"
        ACTIVE = "ACTIVE", "Active (Currently Running)"
        EXPIRED = "EXPIRED", "Expired (Ended)"

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="scheduled_prices",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="scheduled_prices",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    sale_price = PriceField(validators=[MinValueValidator(0)])
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    priority = models.IntegerField(default=0, help_text="Higher priority wins when schedules overlap.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduled_prices_created",
    )

    class Meta:
        db_table = "pricing_scheduled"
        ordering = ["-start_datetime"]
        indexes = [
            models.Index(fields=["product", "start_datetime"], name="idx_sp_prod_start"),
            models.Index(fields=["variant", "start_datetime"], name="idx_sp_var_start"),
            models.Index(fields=["status", "start_datetime"], name="idx_sp_status_start"),
            models.Index(fields=["start_datetime", "end_datetime"], name="idx_sp_date_range"),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(product__isnull=False) | Q(variant__isnull=False),
                name="scheduled_price_product_or_variant",
            ),
            models.CheckConstraint(
                check=Q(end_datetime__gt=F("start_datetime")),
                name="scheduled_price_end_after_start",
            ),
        ]

    def __str__(self):
        target = self.get_item()
        label = getattr(target, "name", getattr(target, "sku", "?"))
        return f"{self.name} – {label} ({self.get_status_display()})"

    # ── Properties ─────────────────────────────────────────────

    @property
    def is_active_now(self) -> bool:
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime

    @property
    def is_pending(self) -> bool:
        return timezone.now() < self.start_datetime

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.end_datetime

    def get_item(self):
        return self.variant or self.product

    # ── Status management ──────────────────────────────────────

    def update_status(self) -> bool:
        """Update status based on current time. Returns True if changed."""
        now = timezone.now()
        old_status = self.status
        if now < self.start_datetime:
            self.status = self.Status.PENDING
        elif now > self.end_datetime:
            self.status = self.Status.EXPIRED
        else:
            self.status = self.Status.ACTIVE
        if self.status != old_status:
            self.save(update_fields=["status", "updated_on"])
            return True
        return False

    def get_status_display_html(self) -> str:
        colours = {
            self.Status.PENDING: "#f59e0b",
            self.Status.ACTIVE: "#10b981",
            self.Status.EXPIRED: "#ef4444",
        }
        colour = colours.get(self.status, "#6b7280")
        return f'<span style="color:{colour};font-weight:bold">{self.get_status_display()}</span>'

    # ── Validation ─────────────────────────────────────────────

    def clean(self):
        super().clean()
        errors = {}
        # Date range
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                errors["end_datetime"] = "End must be after start."
        # Product XOR variant (mutual exclusivity)
        if not self.product_id and not self.variant_id:
            errors["product"] = "Must assign a product or variant."
        if self.product_id and self.variant_id:
            errors["variant"] = "Cannot specify both product and variant."
        # Validate sale_price against regular price
        if not errors:
            sale_warning = self._validate_sale_price()
            if sale_warning:
                errors["sale_price"] = sale_warning
        # Overlap check
        overlap = self._check_overlaps()
        if overlap:
            errors["start_datetime"] = f"Overlaps with '{overlap.name}' at the same priority."
        if errors:
            raise ValidationError(errors)

    def _validate_sale_price(self) -> str | None:
        """Validate that sale_price is less than the product/variant base price."""
        item = self.get_item()
        if item is None:
            return None
        base_price = None
        if hasattr(item, "price"):
            try:
                price_obj = item.price
                base_price = getattr(price_obj, "base_price", None)
            except Exception:
                pass
        if base_price and self.sale_price and self.sale_price >= base_price:
            return f"Sale price ({self.sale_price}) should be less than base price ({base_price})."
        return None

    def _check_overlaps(self):
        qs = ScheduledPrice.objects.filter(
            priority=self.priority, status__in=[self.Status.PENDING, self.Status.ACTIVE]
        ).exclude(pk=self.pk)
        if self.product_id:
            qs = qs.filter(product=self.product)
        elif self.variant_id:
            qs = qs.filter(variant=self.variant)
        else:
            return None
        for other in qs:
            if self._time_ranges_overlap(other):
                return other
        return None

    def _time_ranges_overlap(self, other) -> bool:
        return self.start_datetime < other.end_datetime and other.start_datetime < self.end_datetime

    def save(self, *args, **kwargs):
        if not kwargs.get("update_fields"):
            self.full_clean()
        super().save(*args, **kwargs)

    # ── Class-level utilities ──────────────────────────────────

    @classmethod
    def get_highest_priority_schedule(cls, product=None, variant=None, at_time=None):
        """Return the highest-priority active scheduled price for a product/variant."""
        now = at_time or timezone.now()
        qs = cls.objects.filter(
            status=cls.Status.ACTIVE,
            start_datetime__lte=now,
            end_datetime__gte=now,
        )
        if variant:
            qs = qs.filter(variant=variant)
        elif product:
            qs = qs.filter(product=product)
        else:
            return None
        return qs.order_by("-priority").first()

    @classmethod
    def get_active_scheduled_price(cls, product=None, variant=None, at_time=None):
        """Convenience alias for get_highest_priority_schedule."""
        return cls.get_highest_priority_schedule(product=product, variant=variant, at_time=at_time)
