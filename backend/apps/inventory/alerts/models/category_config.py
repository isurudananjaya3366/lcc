"""
Category-level stock configuration with inheritance from parent categories.
"""

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class CategoryStockConfig(UUIDMixin, TimestampMixin, models.Model):
    """
    Category-level stock threshold overrides.

    Allows categories to override global settings. Supports inheritance
    from parent categories when inherit_from_parent is True.

    Inheritance chain:
        CategoryStockConfig → Parent CategoryStockConfig → GlobalStockSettings
    """

    MAX_INHERITANCE_DEPTH = 10

    category = models.OneToOneField(
        "products.Category",
        on_delete=models.CASCADE,
        related_name="stock_config",
        help_text="Category for these threshold settings.",
    )

    # ── Threshold Overrides (nullable = inherit) ────────────────
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

    # ── Inheritance Control ─────────────────────────────────────
    inherit_from_parent = models.BooleanField(
        default=True,
        help_text="Inherit unset values from parent category.",
    )

    # ── Alert Overrides (nullable = inherit from global) ────────
    alert_on_low_stock = models.BooleanField(null=True, blank=True)
    alert_on_critical_stock = models.BooleanField(null=True, blank=True)
    alert_on_out_of_stock = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = "Category Stock Configuration"
        verbose_name_plural = "Category Stock Configurations"
        db_table = "inventory_category_stock_config"
        indexes = [
            models.Index(fields=["category"], name="idx_catconfig_category"),
        ]

    def __str__(self):
        return f"Stock Config - {self.category.name}"

    def clean(self):
        super().clean()
        if (
            self.reorder_point is not None
            and self.low_stock_threshold is not None
            and self.reorder_point < self.low_stock_threshold
        ):
            raise ValidationError(
                {"reorder_point": "Reorder point must be ≥ low stock threshold."}
            )

    # ── Inheritance Resolution ──────────────────────────────────

    def get_parent_config(self):
        """Return parent category's stock config or None."""
        parent = self.category.parent
        if parent is None:
            return None
        try:
            return parent.stock_config
        except CategoryStockConfig.DoesNotExist:
            return None

    def _resolve_field(self, field_name, visited=None):
        """
        Resolve a single field through the inheritance chain.

        Returns (value, source) tuple.
        """
        if visited is None:
            visited = set()
        if self.category_id in visited:
            return None, "circular"
        visited.add(self.category_id)

        own_value = getattr(self, field_name)
        if own_value is not None:
            return own_value, "category"

        if self.inherit_from_parent and len(visited) < self.MAX_INHERITANCE_DEPTH:
            parent_config = self.get_parent_config()
            if parent_config:
                value, source = parent_config._resolve_field(field_name, visited)
                if value is not None:
                    return value, f"parent_category"

        # Fall back to global
        from apps.inventory.alerts.models.global_settings import GlobalStockSettings

        global_field_map = {
            "low_stock_threshold": "default_low_threshold",
            "reorder_point": "default_reorder_point",
            "reorder_quantity": "default_reorder_qty",
            "alert_on_low_stock": "alert_on_low_stock",
            "alert_on_critical_stock": "alert_on_critical_stock",
            "alert_on_out_of_stock": "alert_on_out_of_stock",
        }
        global_name = global_field_map.get(field_name)
        if global_name:
            settings = GlobalStockSettings.get_settings()
            return getattr(settings, global_name), "global"
        return None, "unknown"

    def get_effective_low_threshold(self):
        value, _ = self._resolve_field("low_stock_threshold")
        return value

    def get_effective_reorder_point(self):
        value, _ = self._resolve_field("reorder_point")
        return value

    def get_effective_reorder_quantity(self):
        value, _ = self._resolve_field("reorder_quantity")
        return value

    def get_effective_config(self):
        """Return dict with all effective values and their sources."""
        fields = ["low_stock_threshold", "reorder_point", "reorder_quantity"]
        config = {}
        sources = {}
        for field in fields:
            value, source = self._resolve_field(field)
            config[field] = value
            sources[field] = source
        config["sources"] = sources
        return config

    def resolve_inheritance_chain(self):
        """Build ordered list of configs in the inheritance chain (for debugging)."""
        chain = [self]
        visited = {self.category_id}
        current = self
        while current.inherit_from_parent:
            parent_config = current.get_parent_config()
            if parent_config is None or parent_config.category_id in visited:
                break
            visited.add(parent_config.category_id)
            chain.append(parent_config)
            current = parent_config
        return chain

    # ── Admin display helpers ───────────────────────────────────

    def effective_low_threshold_display(self):
        value, source = self._resolve_field("low_stock_threshold")
        return f"{value} (from {source})"

    def effective_reorder_point_display(self):
        value, source = self._resolve_field("reorder_point")
        return f"{value} (from {source})"
