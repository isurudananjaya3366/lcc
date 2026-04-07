from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import BaseModel
from apps.pos.constants import (
    PRINTER_TYPE_CHOICES,
    PRINTER_TYPE_THERMAL,
    RECEIPT_LANGUAGE_CHOICES,
    RECEIPT_LANGUAGE_ENGLISH,
    SCANNER_INTERFACE_CHOICES,
    SCANNER_INTERFACE_USB,
    TERMINAL_STATUS_ACTIVE,
    TERMINAL_STATUS_CHOICES,
)


class POSTerminalManager(models.Manager):
    """Manager for POSTerminal with common queries."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_deleted=False)

    def active(self):
        return self.get_queryset().filter(status=TERMINAL_STATUS_ACTIVE)

    def by_warehouse(self, warehouse):
        return self.get_queryset().filter(warehouse=warehouse)

    def get_by_code(self, code):
        return self.get_queryset().get(code=code)


class POSTerminal(BaseModel):
    """
    Represents a Point of Sale terminal device or station.

    Each terminal is associated with a warehouse/store location and
    configured with hardware settings, receipt preferences, and
    operational rules.
    """

    # ── Basic Fields ──────────────────────────────────────────────────────
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
        related_name="terminals",
    )
    status = models.CharField(
        max_length=20,
        choices=TERMINAL_STATUS_CHOICES,
        default=TERMINAL_STATUS_ACTIVE,
        db_index=True,
    )
    description = models.TextField(blank=True, default="")

    # ── Hardware Configuration ────────────────────────────────────────────
    printer_type = models.CharField(
        max_length=20,
        choices=PRINTER_TYPE_CHOICES,
        default=PRINTER_TYPE_THERMAL,
    )
    receipt_printer_ip = models.GenericIPAddressField(blank=True, null=True)
    receipt_printer_port = models.PositiveIntegerField(
        default=9100, blank=True, null=True
    )
    cash_drawer_enabled = models.BooleanField(default=True)
    cash_drawer_auto_open = models.BooleanField(default=True)
    barcode_scanner_enabled = models.BooleanField(default=True)
    scanner_interface = models.CharField(
        max_length=20,
        choices=SCANNER_INTERFACE_CHOICES,
        default=SCANNER_INTERFACE_USB,
    )

    # ── Location Fields ───────────────────────────────────────────────────
    location = models.CharField(max_length=100, blank=True, default="")
    floor = models.CharField(max_length=50, blank=True, default="")
    section = models.CharField(max_length=50, blank=True, default="")
    is_mobile = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    # ── Settings ──────────────────────────────────────────────────────────
    default_tax = models.ForeignKey(
        "products.TaxClass",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pos_terminals_with_default_tax",
    )
    allow_price_override = models.BooleanField(default=False)
    allow_discount = models.BooleanField(default=True)
    max_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    require_customer = models.BooleanField(default=False)
    allow_negative_inventory = models.BooleanField(default=False)
    auto_print_receipt = models.BooleanField(default=True)
    receipt_copies = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    offline_mode_enabled = models.BooleanField(default=False)

    # ── Receipt Configuration ─────────────────────────────────────────────
    receipt_header = models.TextField(blank=True, default="")
    receipt_footer = models.TextField(blank=True, default="")
    receipt_language = models.CharField(
        max_length=10,
        choices=RECEIPT_LANGUAGE_CHOICES,
        default=RECEIPT_LANGUAGE_ENGLISH,
    )

    # ── Managers ──────────────────────────────────────────────────────────
    objects = POSTerminalManager()
    all_with_deleted = models.Manager()

    class Meta:
        db_table = "pos_terminals"
        verbose_name = "POS Terminal"
        verbose_name_plural = "POS Terminals"
        ordering = ["warehouse", "code"]
        indexes = [
            models.Index(fields=["code"], name="idx_pos_terminal_code"),
            models.Index(fields=["status"], name="idx_pos_terminal_status"),
            models.Index(fields=["warehouse"], name="idx_pos_terminal_warehouse"),
            models.Index(
                fields=["warehouse", "status"],
                name="idx_pos_terminal_wh_status",
            ),
            models.Index(
                fields=["warehouse", "is_mobile"],
                name="idx_pos_terminal_wh_mobile",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
