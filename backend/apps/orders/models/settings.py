"""
OrderSettings model for tenant-specific order configuration (Task 49).
"""

from decimal import Decimal

from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin


class OrderSettings(UUIDMixin, TimestampMixin, models.Model):
    """
    Tenant-scoped order configuration.

    Controls order numbering, auto-confirmation, stock management,
    pricing defaults, and workflow settings.
    """

    # ── Order Numbering ─────────────────────────────────────────────
    order_number_prefix = models.CharField(max_length=10, default="ORD")
    order_number_separator = models.CharField(max_length=5, default="-")
    order_number_padding = models.IntegerField(default=5)
    include_year_in_number = models.BooleanField(default=True)
    order_number_start = models.IntegerField(default=1)
    reset_numbering_yearly = models.BooleanField(default=True)
    use_sequential_numbering = models.BooleanField(default=True)

    # ── Auto-Confirmation ───────────────────────────────────────────
    auto_confirm_pos_orders = models.BooleanField(default=True)
    auto_confirm_webstore_orders = models.BooleanField(default=False)
    auto_confirm_manual_orders = models.BooleanField(default=False)
    auto_confirm_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Auto-confirm orders below this value.",
    )
    require_payment_for_confirmation = models.BooleanField(default=False)

    # ── Stock Management ────────────────────────────────────────────
    auto_reserve_stock = models.BooleanField(default=True)
    allow_backorders = models.BooleanField(default=False)
    allow_partial_fulfillment = models.BooleanField(default=True)
    cancel_on_insufficient_stock = models.BooleanField(default=False)
    low_stock_threshold = models.IntegerField(default=10)

    # ── Pricing Defaults ────────────────────────────────────────────
    default_currency = models.CharField(max_length=3, default="LKR")
    default_tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    tax_inclusive_pricing = models.BooleanField(default=False)
    allow_manual_price_override = models.BooleanField(default=False)
    require_approval_for_discounts = models.BooleanField(default=False)
    max_discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("100.00")
    )
    show_unit_price_to_customer = models.BooleanField(default=True)

    # ── Workflow ────────────────────────────────────────────────────
    require_approval_above = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Orders above this amount require manager approval.",
    )
    require_manager_approval_for_high_value = models.BooleanField(default=False)
    high_value_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("100000.00"),
    )
    auto_cancel_unpaid_after_days = models.IntegerField(default=7)
    allow_order_editing = models.BooleanField(default=True)
    lock_after_confirmation = models.BooleanField(default=False)
    send_confirmation_email = models.BooleanField(default=True)
    send_shipping_notifications = models.BooleanField(default=True)

    # ── Defaults ────────────────────────────────────────────────────
    default_shipping_method = models.CharField(
        max_length=50, blank=True, default=""
    )
    default_payment_terms = models.CharField(
        max_length=100, blank=True, default=""
    )
    default_priority = models.CharField(
        max_length=20, blank=True, default="medium"
    )

    class Meta:
        db_table = "orders_ordersettings"
        verbose_name = "Order Settings"
        verbose_name_plural = "Order Settings"

    def __str__(self):
        return "Order Settings"

    def can_auto_confirm(self, source, amount=None):
        """Check if an order from a given source can be auto-confirmed."""
        from apps.orders.constants import OrderSource

        source_flags = {
            OrderSource.POS: self.auto_confirm_pos_orders,
            OrderSource.WEBSTORE: self.auto_confirm_webstore_orders,
            OrderSource.MANUAL: self.auto_confirm_manual_orders,
        }
        if not source_flags.get(source, False):
            return False
        if self.auto_confirm_threshold and amount:
            return amount <= self.auto_confirm_threshold
        return True

    def requires_approval(self, amount):
        """Check if the order amount requires manager approval."""
        if self.require_approval_above is None:
            if self.require_manager_approval_for_high_value:
                return amount > self.high_value_threshold
            return False
        return amount > self.require_approval_above

    def get_next_order_number(self):
        """
        Generate the next order number based on settings.

        Returns:
            str: Formatted order number (e.g., 'ORD-2026-00001').
        """
        from django.utils import timezone

        from apps.orders.models.order import Order

        now = timezone.now()
        year = now.year

        last_order = (
            Order.objects.filter(order_date__year=year)
            .order_by("-order_date")
            .first()
        )

        if last_order and last_order.order_number:
            try:
                parts = last_order.order_number.split(self.order_number_separator)
                seq = int(parts[-1]) + 1
            except (ValueError, IndexError):
                seq = self.order_number_start
        else:
            seq = self.order_number_start

        if self.include_year_in_number:
            return (
                f"{self.order_number_prefix}{self.order_number_separator}"
                f"{year}{self.order_number_separator}"
                f"{seq:0{self.order_number_padding}d}"
            )
        return (
            f"{self.order_number_prefix}{self.order_number_separator}"
            f"{seq:0{self.order_number_padding}d}"
        )

    @classmethod
    def get_or_create_settings(cls):
        """Get or create the singleton settings instance."""
        settings, _ = cls.objects.get_or_create(
            pk=cls.objects.first().pk if cls.objects.exists() else None,
            defaults={},
        )
        return settings
