"""
DefaultWarehouseConfig & POSWarehouseMapping models.

Stores per-tenant and per-user default warehouse preferences,
and maps POS terminal IDs to warehouses.
"""

from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.inventory.warehouses.constants import (
    CONFIG_SCOPE_CHOICES,
    CONFIG_SCOPE_TENANT,
)


class DefaultWarehouseConfig(UUIDMixin, TimestampMixin, models.Model):
    """
    Default warehouse preferences.

    Scope can be ``tenant_default`` (exactly one per tenant) or
    ``user_default`` (one per user).  Resolution order:
    user default → tenant default → ``Warehouse.is_default=True``.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="warehouse_configs",
        help_text="Leave blank for a tenant-level default",
    )

    scope = models.CharField(
        max_length=20,
        choices=CONFIG_SCOPE_CHOICES,
        default=CONFIG_SCOPE_TENANT,
        db_index=True,
    )

    default_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="+",
    )

    default_receiving_zone = models.ForeignKey(
        "inventory.WarehouseZone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    default_picking_zone = models.ForeignKey(
        "inventory.WarehouseZone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    class Meta:
        app_label = "inventory"
        db_table = "inventory_default_warehouse_configs"
        verbose_name = "Default Warehouse Config"
        verbose_name_plural = "Default Warehouse Configs"
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(user__isnull=False),
                name="uq_default_config_per_user",
            ),
        ]

    def __str__(self):
        if self.user:
            return f"User default: {self.user} → {self.default_warehouse.code}"
        return f"Tenant default → {self.default_warehouse.code}"

    # ── resolution helper ─────────────────────────────────────────────

    @classmethod
    def get_default_warehouse(cls, user=None):
        """
        Resolve the default warehouse for *user*.

        Fallback chain: user config → tenant config → Warehouse.is_default.
        Returns a Warehouse instance or None.
        """
        from apps.inventory.warehouses.models import Warehouse

        # 1) User-level default
        if user:
            try:
                cfg = cls.objects.select_related("default_warehouse").get(user=user)
                return cfg.default_warehouse
            except cls.DoesNotExist:
                pass

        # 2) Tenant-level default
        try:
            cfg = (
                cls.objects.filter(user__isnull=True)
                .select_related("default_warehouse")
                .first()
            )
            if cfg:
                return cfg.default_warehouse
        except cls.DoesNotExist:
            pass

        # 3) Warehouse flagged as is_default
        try:
            return Warehouse.objects.get_default()
        except Warehouse.DoesNotExist:
            return None


class POSWarehouseMapping(UUIDMixin, TimestampMixin, models.Model):
    """Maps a POS terminal identifier to a warehouse."""

    terminal_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="POS terminal identifier (e.g. POS-TERM-001)",
    )

    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="pos_terminals",
    )

    terminal_location = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Physical location of the POS device",
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "inventory"
        db_table = "inventory_pos_warehouse_mappings"
        verbose_name = "POS Warehouse Mapping"
        verbose_name_plural = "POS Warehouse Mappings"

    def __str__(self):
        return f"{self.terminal_id} → {self.warehouse.code}"

    @classmethod
    def get_warehouse_for_terminal(cls, terminal_id):
        """Return the Warehouse for *terminal_id*, or None."""
        try:
            mapping = cls.objects.select_related("warehouse").get(
                terminal_id=terminal_id, is_active=True
            )
            return mapping.warehouse
        except cls.DoesNotExist:
            return None
