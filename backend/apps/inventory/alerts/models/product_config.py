"""
Product-level stock configuration model.

Supports per-product, per-variant, and per-warehouse threshold settings
with inheritance from category and global configurations.
"""

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.inventory.alerts.constants import (
    VISIBILITY_AUTO,
    VISIBILITY_CHOICES,
)


class ProductStockConfigManager(models.Manager):
    """Custom manager for ProductStockConfig."""

    def for_product(self, product, variant=None, warehouse=None):
        """Return config matching the given product/variant/warehouse."""
        return self.get_queryset().filter(
            product=product, variant=variant, warehouse=warehouse
        ).first()

    def for_warehouse(self, warehouse):
        """Return all configs for a specific warehouse (including generic)."""
        return self.get_queryset().filter(
            models.Q(warehouse=warehouse) | models.Q(warehouse__isnull=True)
        )

    def monitored(self):
        """Return only configs with monitoring enabled."""
        return self.get_queryset().filter(monitoring_enabled=True)


class ProductStockConfig(UUIDMixin, TimestampMixin, models.Model):
    """
    Product-specific stock configuration.

    Overrides category and global settings. Supports warehouse-specific
    configurations and webstore visibility / backorder controls.

    Inheritance chain (most specific wins):
        ProductStockConfig(warehouse) → ProductStockConfig(no warehouse)
        → CategoryStockConfig(recursive parents) → GlobalStockSettings
    """

    objects = ProductStockConfigManager()

    # ── Relationships ───────────────────────────────────────────
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="stock_configs",
        help_text="Product for these settings.",
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_configs",
        help_text="Optional specific variant.",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="product_stock_configs",
        help_text="Optional warehouse-specific settings.",
    )

    # ── Threshold Fields (Task 10) ──────────────────────────────
    low_stock_threshold = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Custom low stock alert threshold. Blank = inherit.",
    )
    reorder_point = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Custom reorder point. Blank = inherit.",
    )
    reorder_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Custom reorder quantity. Blank = inherit.",
    )
    calculated_reorder_point = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        help_text="Auto-calculated reorder point from sales velocity.",
    )

    # ── Per-Product Alert Overrides ─────────────────────────────
    alert_on_low_stock = models.BooleanField(
        null=True,
        blank=True,
        help_text="Override low stock alerts. None = inherit.",
    )
    alert_on_critical_stock = models.BooleanField(
        null=True,
        blank=True,
        help_text="Override critical stock alerts. None = inherit.",
    )
    alert_on_out_of_stock = models.BooleanField(
        null=True,
        blank=True,
        help_text="Override out of stock alerts. None = inherit.",
    )

    # ── Auto-Calculation Fields ─────────────────────────────────
    use_auto_calculation = models.BooleanField(
        default=False,
        help_text="Auto-calculate reorder point from sales velocity.",
    )
    safety_stock_days = models.PositiveIntegerField(
        default=7,
        validators=[MinValueValidator(1), MaxValueValidator(90)],
        help_text="Days of safety stock to maintain.",
    )
    lead_time_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Supplier lead time in days for this product.",
    )

    # ── Monitoring ──────────────────────────────────────────────
    monitoring_enabled = models.BooleanField(
        default=True,
        help_text="Include this product in stock monitoring checks.",
    )

    # ── Auto-Reorder (Task 64) ─────────────────────────────────
    allow_auto_reorder = models.BooleanField(
        default=False,
        help_text="Allow automatic reordering for this product.",
    )

    # ── Monitoring Exclusions (Task 46) ─────────────────────────
    exclude_from_monitoring = models.BooleanField(
        default=False,
        help_text="Exclude this product from stock monitoring.",
    )

    EXCLUSION_REASON_CHOICES = [
        ("discontinued", "Product Discontinued"),
        ("seasonal", "Seasonal Product (Off-Season)"),
        ("custom_order", "Custom Order Only"),
        ("consignment", "Consignment Item"),
        ("low_value", "Low Value Item"),
        ("manual", "Manual Stock Management"),
        ("other", "Other Reason"),
    ]

    exclusion_reason = models.CharField(
        max_length=50,
        choices=EXCLUSION_REASON_CHOICES,
        blank=True,
        default="",
        help_text="Reason for monitoring exclusion.",
    )
    exclusion_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Start date for temporary exclusion.",
    )
    exclusion_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date for temporary exclusion.",
    )

    # ── Webstore Visibility (Task 12) ──────────────────────────
    auto_hide_when_oos = models.BooleanField(
        default=False,
        help_text="Automatically hide product from webstore when out of stock.",
    )
    auto_show_when_restocked = models.BooleanField(
        default=True,
        help_text="Automatically show product when restocked.",
    )
    minimum_stock_for_display = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minimum stock to display on webstore (None = show at any level).",
    )
    hide_threshold_days = models.PositiveIntegerField(
        default=0,
        help_text="Days to wait before hiding (0 = hide immediately).",
    )
    display_as_coming_soon = models.BooleanField(
        default=False,
        help_text="Show as 'Coming Soon' instead of hiding.",
    )
    coming_soon_message = models.CharField(
        max_length=200,
        default="Coming Soon",
        help_text="Message to display when out of stock.",
    )
    webstore_visibility_override = models.CharField(
        max_length=15,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_AUTO,
        help_text="Manual override for webstore visibility.",
    )

    # ── Backorder Fields (Task 13) ──────────────────────────────
    allow_backorder = models.BooleanField(
        default=False,
        help_text="Allow orders when out of stock.",
    )
    max_backorder_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum units available for backorder (None = unlimited).",
    )
    backorder_lead_time_days = models.PositiveIntegerField(
        default=14,
        help_text="Expected days until backordered item ships.",
    )
    backorder_message = models.CharField(
        max_length=200,
        default="Available for backorder",
        help_text="Message shown when product is on backorder.",
    )
    show_expected_ship_date = models.BooleanField(
        default=True,
        help_text="Display estimated ship date for backorders.",
    )
    backorder_notification_email = models.BooleanField(
        default=True,
        help_text="Email customer when backorder ships.",
    )

    # ── Additional Fields ───────────────────────────────────────
    preferred_supplier = models.ForeignKey(
        "vendors.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_stock_configs",
        help_text="Preferred supplier for reorder suggestions.",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Internal notes about this product's stock configuration.",
    )
    last_calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time reorder calculations were run.",
    )

    class Meta:
        verbose_name = "Product Stock Configuration"
        verbose_name_plural = "Product Stock Configurations"
        db_table = "inventory_product_stock_config"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "variant", "warehouse"],
                name="uniq_product_variant_warehouse_config",
            ),
        ]
        indexes = [
            models.Index(fields=["product"], name="idx_psc_product"),
            models.Index(fields=["warehouse"], name="idx_psc_warehouse"),
            models.Index(fields=["product", "warehouse"], name="idx_psc_prod_wh"),
        ]

    def __str__(self):
        parts = [f"Stock Config - {self.product}"]
        if self.variant:
            parts.append(f"[{self.variant}]")
        parts.append(f"@ {self.get_warehouse_name()}")
        return " ".join(parts)

    def clean(self):
        super().clean()
        errors = {}
        if (
            self.reorder_point is not None
            and self.low_stock_threshold is not None
            and self.reorder_point < self.low_stock_threshold
        ):
            errors["reorder_point"] = "Reorder point must be ≥ low stock threshold."
        if errors:
            raise ValidationError(errors)

    # ── Warehouse Helpers (Task 11) ─────────────────────────────

    @property
    def warehouse_specific(self):
        """Return True if this config is warehouse-specific."""
        return self.warehouse_id is not None

    def get_warehouse_name(self):
        """Return warehouse name or 'All Warehouses'."""
        if self.warehouse:
            return self.warehouse.name
        return "All Warehouses"

    def get_other_warehouse_configs(self):
        """Return other warehouse configs for the same product."""
        return ProductStockConfig.objects.filter(
            product=self.product,
        ).exclude(pk=self.pk).exclude(warehouse__isnull=True)

    # ── Monitoring Exclusion (Task 46) ─────────────────────────

    def is_excluded_from_monitoring(self):
        """Check if product is currently excluded from monitoring."""
        if not self.exclude_from_monitoring:
            return False

        today = timezone.now().date()

        if self.exclusion_start_date and today < self.exclusion_start_date:
            return False

        if self.exclusion_end_date and today > self.exclusion_end_date:
            return False

        return True

    # ── Webstore Visibility (Task 12) ──────────────────────────

    def is_visible_on_webstore(self, available_stock, days_out_of_stock=0):
        """Calculate current webstore visibility."""
        from apps.inventory.alerts.constants import (
            VISIBILITY_ALWAYS_HIDE,
            VISIBILITY_ALWAYS_SHOW,
        )

        if self.webstore_visibility_override == VISIBILITY_ALWAYS_SHOW:
            return True
        if self.webstore_visibility_override == VISIBILITY_ALWAYS_HIDE:
            return False

        # AUTO mode
        if available_stock <= 0 and self.auto_hide_when_oos:
            if self.hide_threshold_days == 0:
                return False
            if days_out_of_stock >= self.hide_threshold_days:
                return False
        if self.minimum_stock_for_display is not None:
            if available_stock < self.minimum_stock_for_display:
                return False
        return True

    def get_webstore_status(self, available_stock, days_out_of_stock=0):
        """Return current webstore status dict."""
        visible = self.is_visible_on_webstore(available_stock, days_out_of_stock)
        if visible:
            return {"visible": True, "reason": "in_stock", "message": ""}
        if self.display_as_coming_soon:
            return {
                "visible": False,
                "reason": "coming_soon",
                "message": self.coming_soon_message,
            }
        return {"visible": False, "reason": "out_of_stock", "message": ""}

    def should_hide_now(self, available_stock, days_out_of_stock=0):
        """Determine if product should be hidden based on all visibility rules."""
        if not self.auto_hide_when_oos:
            return False
        if available_stock > 0:
            if self.minimum_stock_for_display is not None:
                return available_stock < self.minimum_stock_for_display
            return False
        # Out of stock
        if self.hide_threshold_days > 0 and days_out_of_stock < self.hide_threshold_days:
            return False
        return True

    # ── Backorder (Task 13) ─────────────────────────────────────

    def is_available_for_backorder(self, current_backorders=0):
        """Check if product can currently be backordered."""
        if not self.allow_backorder:
            return False
        if self.max_backorder_quantity is None:
            return True
        return current_backorders < self.max_backorder_quantity

    def get_backorder_capacity(self, current_backorders=0):
        """Calculate remaining backorder capacity."""
        if not self.allow_backorder:
            return 0
        if self.max_backorder_quantity is None:
            return None  # unlimited
        remaining = self.max_backorder_quantity - current_backorders
        return max(remaining, 0)

    def calculate_expected_ship_date(self):
        """Calculate expected ship date based on backorder lead time."""
        return timezone.now().date() + timedelta(days=self.backorder_lead_time_days)

    def get_backorder_info(self, current_backorders=0):
        """Return complete backorder details dict."""
        return {
            "allowed": self.allow_backorder,
            "capacity": self.get_backorder_capacity(current_backorders),
            "lead_time_days": self.backorder_lead_time_days,
            "expected_ship_date": (
                self.calculate_expected_ship_date() if self.allow_backorder else None
            ),
            "message": self.backorder_message if self.allow_backorder else "",
        }

    # ── Effective Config (Task 15) ──────────────────────────────

    def get_effective_config(self):
        """Get complete effective configuration with inheritance resolution."""
        from apps.inventory.alerts.services.config_resolver import ConfigResolver

        return ConfigResolver.resolve_for_product(
            product=self.product,
            warehouse=self.warehouse,
        )

    @property
    def effective_low_threshold(self):
        config = self.get_effective_config()
        return config.get("low_stock_threshold")

    @property
    def effective_reorder_point(self):
        config = self.get_effective_config()
        return config.get("reorder_point")

    @property
    def effective_reorder_quantity(self):
        config = self.get_effective_config()
        return config.get("reorder_quantity")

    def effective_low_threshold_display(self):
        config = self.get_effective_config()
        value = config.get("low_stock_threshold")
        source = config.get("sources", {}).get("low_stock_threshold", "unknown")
        return f"{value} (from {source})"

    def effective_reorder_point_display(self):
        config = self.get_effective_config()
        value = config.get("reorder_point")
        source = config.get("sources", {}).get("reorder_point", "unknown")
        return f"{value} (from {source})"

    def to_dict(self):
        """Serialize config including effective values."""
        effective = self.get_effective_config()
        return {
            "product_id": str(self.product_id),
            "variant_id": str(self.variant_id) if self.variant_id else None,
            "warehouse_id": str(self.warehouse_id) if self.warehouse_id else None,
            "own_values": {
                "low_stock_threshold": self.low_stock_threshold,
                "reorder_point": self.reorder_point,
                "reorder_quantity": self.reorder_quantity,
            },
            "effective_values": effective,
        }

    def refresh_effective_config(self):
        """Recalculate effective config and update calculated fields."""
        effective = self.get_effective_config()
        rp = effective.get("reorder_point")
        self.calculated_reorder_point = int(rp) if rp is not None else None
        self.last_calculated_at = timezone.now()
        self.save(update_fields=["calculated_reorder_point", "last_calculated_at"])

    def compare_to_effective(self):
        """Compare own values to effective config and highlight differences."""
        effective = self.get_effective_config()
        fields = ["low_stock_threshold", "reorder_point", "reorder_quantity"]
        differences = {}
        for field in fields:
            own_value = getattr(self, field, None)
            eff_value = effective.get(field)
            source = effective.get("sources", {}).get(field, "unknown")
            if own_value is not None:
                differences[field] = {
                    "own": own_value,
                    "effective": eff_value,
                    "source": "product",
                    "overridden": True,
                }
            else:
                differences[field] = {
                    "own": None,
                    "effective": eff_value,
                    "source": source,
                    "overridden": False,
                }
        return differences
