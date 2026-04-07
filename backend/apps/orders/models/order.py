"""
Order model for the orders application.

Defines the Order model which tracks customer purchases within a
tenant schema. Supports multiple order sources (POS, webstore, quote
conversion, manual entry), comprehensive status lifecycle, fulfillment
workflow, and financial tracking with multi-currency support.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.orders.constants import (
    ALLOWED_TRANSITIONS,
    CURRENCY_SYMBOLS,
    CurrencyChoice,
    DiscountType,
    EDITABLE_STATES,
    OrderSource,
    OrderStatus,
    PaymentStatus,
    TERMINAL_STATES,
)


PRICE_MAX_DIGITS = 12
PRICE_DECIMAL_PLACES = 2


class OrderManager(models.Manager):
    """Custom manager for Order model."""

    def pending(self):
        return self.filter(status=OrderStatus.PENDING)

    def confirmed(self):
        return self.filter(status=OrderStatus.CONFIRMED)

    def processing(self):
        return self.filter(status=OrderStatus.PROCESSING)

    def completed(self):
        return self.filter(status=OrderStatus.COMPLETED)

    def active(self):
        """Orders that are not cancelled, returned, or soft-deleted."""
        return self.exclude(
            status__in=[OrderStatus.CANCELLED, OrderStatus.RETURNED]
        ).filter(is_deleted=False)


class Order(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Customer purchase order.

    Tracks the full lifecycle of a customer order from creation to
    delivery or cancellation. Supports multiple sources (POS, webstore,
    quote conversion, manual) and multi-currency pricing.
    """

    # ── Order Number ────────────────────────────────────────────────
    order_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        blank=True,
        verbose_name="Order Number",
        help_text="Unique identifier. Format: ORD-YYYY-NNNNN",
    )

    # ── Status & Source ─────────────────────────────────────────────
    status = models.CharField(
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
        verbose_name="Order Status",
    )
    source = models.CharField(
        max_length=20,
        choices=OrderSource.choices,
        default=OrderSource.MANUAL,
        db_index=True,
        verbose_name="Order Source",
    )
    priority = models.IntegerField(
        default=5,
        verbose_name="Priority",
        help_text="1 (highest) to 10 (lowest)",
    )
    is_draft = models.BooleanField(
        default=False,
        verbose_name="Is Draft",
        help_text="Draft orders don't reserve stock.",
    )

    # ── Customer ────────────────────────────────────────────────────
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
        verbose_name="Customer",
    )
    customer_name = models.CharField(max_length=200, blank=True, default="")
    customer_email = models.EmailField(max_length=254, blank=True, default="", db_index=True)
    customer_phone = models.CharField(max_length=20, blank=True, default="")
    is_guest_order = models.BooleanField(default=False)
    customer_notes = models.TextField(blank=True, default="")

    # ── Addresses ───────────────────────────────────────────────────
    shipping_address = models.JSONField(default=dict, blank=True)
    billing_address = models.JSONField(default=dict, blank=True)
    use_shipping_as_billing = models.BooleanField(default=True)
    shipping_method = models.CharField(max_length=50, blank=True, default="")
    tracking_number = models.CharField(max_length=100, blank=True, default="")
    tracking_url = models.URLField(blank=True, default="")
    delivery_instructions = models.TextField(blank=True, default="")

    # ── Dates ───────────────────────────────────────────────────────
    order_date = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Order Date",
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    processing_at = models.DateTimeField(null=True, blank=True)
    picked_at = models.DateTimeField(null=True, blank=True)
    packed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, default="")
    cancellation_notes = models.TextField(blank=True, default="")
    returned_at = models.DateTimeField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    promised_delivery_date = models.DateField(null=True, blank=True)

    # ── Financial ───────────────────────────────────────────────────
    subtotal = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    discount_type = models.CharField(
        max_length=20, choices=DiscountType.choices, blank=True, default=""
    )
    discount_value = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    discount_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    tax_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    shipping_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    total_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    refund_amount = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    cost_of_goods = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    profit_margin = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    # ── Payment ─────────────────────────────────────────────────────
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        db_index=True,
    )
    amount_paid = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    balance_due = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )
    payment_method = models.CharField(max_length=50, blank=True, default="")
    payment_reference = models.CharField(max_length=100, blank=True, default="")

    # ── References ──────────────────────────────────────────────────
    quote = models.ForeignKey(
        "quotes.Quote",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="converted_orders",
    )
    pos_session = models.ForeignKey(
        "pos.POSSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    external_reference = models.CharField(max_length=100, blank=True, default="", db_index=True)
    parent_order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_orders",
    )
    external_system = models.CharField(max_length=50, blank=True, default="")
    external_url = models.URLField(blank=True, default="")
    campaign_code = models.CharField(max_length=50, blank=True, default="", db_index=True)
    affiliate_code = models.CharField(max_length=50, blank=True, default="", db_index=True)
    coupon_code = models.CharField(max_length=50, blank=True, default="")
    is_replacement_order = models.BooleanField(default=False)
    is_split_order = models.BooleanField(default=False)

    # ── Metadata ────────────────────────────────────────────────────
    notes = models.TextField(blank=True, default="")
    internal_notes = models.TextField(blank=True, default="")
    admin_notes = models.TextField(blank=True, default="")
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    fulfillment_notes = models.TextField(blank=True, default="")
    gift_message = models.TextField(max_length=500, blank=True, default="")
    is_gift = models.BooleanField(default=False)
    requires_insurance = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    special_instructions = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    # ── Lock & Duplication ──────────────────────────────────────────
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locked_orders",
    )
    lock_reason = models.CharField(max_length=50, blank=True, default="")
    lock_notes = models.TextField(blank=True, default="")
    duplicated_from = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duplicated_orders",
    )

    # ── User References ─────────────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_orders",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
    )
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_orders",
    )
    shipped_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipped_orders",
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_orders",
    )

    # ── Currency ────────────────────────────────────────────────────
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoice.choices,
        default=CurrencyChoice.LKR,
    )
    exchange_rate = models.DecimalField(
        max_digits=12, decimal_places=6, default=1
    )
    base_currency = models.CharField(max_length=3, default="LKR")
    base_total = models.DecimalField(
        max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES, default=0
    )

    objects = OrderManager()

    class Meta:
        db_table = "orders_order"
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-order_date"]
        indexes = [
            models.Index(fields=["status", "order_date"], name="idx_order_status_date"),
            models.Index(fields=["customer", "status"], name="idx_order_customer_status"),
            models.Index(fields=["status", "-created_on"], name="idx_order_status_created"),
            models.Index(fields=["source", "order_date"], name="idx_order_source_date"),
            models.Index(fields=["payment_status", "status"], name="idx_order_payment_status"),
            models.Index(fields=["-order_date"], name="idx_order_date_desc"),
            models.Index(fields=["order_number"], name="idx_order_number"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(subtotal__gte=0),
                name="order_positive_subtotal",
            ),
            models.CheckConstraint(
                check=models.Q(tax_amount__gte=0),
                name="order_positive_tax",
            ),
            models.CheckConstraint(
                check=models.Q(discount_amount__gte=0),
                name="order_positive_discount",
            ),
            models.CheckConstraint(
                check=models.Q(shipping_amount__gte=0),
                name="order_positive_shipping",
            ),
            models.CheckConstraint(
                check=models.Q(total_amount__gte=0),
                name="order_positive_total",
            ),
            models.CheckConstraint(
                check=models.Q(amount_paid__gte=0),
                name="order_positive_amount_paid",
            ),
            models.CheckConstraint(
                check=models.Q(exchange_rate__gt=0),
                name="order_positive_exchange_rate",
            ),
            models.CheckConstraint(
                check=models.Q(priority__gte=1, priority__lte=10),
                name="order_priority_range",
            ),
            models.CheckConstraint(
                check=models.Q(refund_amount__gte=0),
                name="order_positive_refund",
            ),
            models.CheckConstraint(
                check=models.Q(cost_of_goods__gte=0),
                name="order_positive_cogs",
            ),
        ]

    def __str__(self):
        name = self.get_customer_name()
        if self.order_number:
            return f"Order {self.order_number} — {name}"
        return f"Draft Order {self.pk}"

    def __repr__(self):
        return f"<Order(id={self.pk}, number={self.order_number!r}, status={self.status!r})>"

    # ── Properties ──────────────────────────────────────────────────

    @property
    def is_editable(self):
        return self.status in EDITABLE_STATES and not self.is_locked

    @property
    def is_completed(self):
        return self.status == OrderStatus.COMPLETED

    @property
    def is_cancelled(self):
        return self.status == OrderStatus.CANCELLED

    @property
    def is_terminal(self):
        return self.status in TERMINAL_STATES

    @property
    def is_guest(self):
        return self.customer is None

    @property
    def currency_symbol(self):
        return CURRENCY_SYMBOLS.get(self.currency, "₨")

    # ── Customer Helpers ────────────────────────────────────────────

    def get_customer_name(self):
        if self.customer_id:
            return self.customer.full_name
        return self.customer_name or "Guest"

    def get_customer_email(self):
        if self.customer_id:
            return self.customer.email
        return self.customer_email

    def get_customer_phone(self):
        if self.customer_id:
            return self.customer.phone
        return self.customer_phone

    # ── Address Helpers ─────────────────────────────────────────────

    def get_shipping_address(self):
        return self._format_address(self.shipping_address)

    def get_billing_address(self):
        if self.use_shipping_as_billing or not self.billing_address:
            return self.get_shipping_address()
        return self._format_address(self.billing_address)

    @staticmethod
    def _format_address(addr):
        if not addr:
            return ""
        parts = []
        if addr.get("name"):
            parts.append(addr["name"])
        if addr.get("line1"):
            parts.append(addr["line1"])
        if addr.get("line2"):
            parts.append(addr["line2"])
        city_postal = " ".join(
            filter(None, [addr.get("city"), addr.get("postal_code")])
        )
        if city_postal:
            parts.append(city_postal)
        if addr.get("state"):
            parts.append(addr["state"])
        return "\n".join(parts)

    # ── Financial ───────────────────────────────────────────────────

    def calculate_totals(self):
        """Recalculate order totals from stored values."""
        self.total_amount = (
            self.subtotal - self.discount_amount + self.tax_amount + self.shipping_amount
        )
        self.balance_due = self.total_amount - self.amount_paid
        if self.exchange_rate and self.exchange_rate > 0:
            self.base_total = self.total_amount * self.exchange_rate

    # ── Date Helpers ────────────────────────────────────────────────

    def get_lifecycle_duration(self):
        """Duration from order_date to completed_at."""
        if self.completed_at and self.order_date:
            return self.completed_at - self.order_date
        return None

    def get_processing_duration(self):
        """Duration from confirmed_at to shipped_at."""
        if self.shipped_at and self.confirmed_at:
            return self.shipped_at - self.confirmed_at
        return None

    def get_delivery_duration(self):
        """Duration from shipped_at to delivered_at."""
        if self.delivered_at and self.shipped_at:
            return self.delivered_at - self.shipped_at
        return None

    @property
    def is_overdue(self):
        """True if past promised_delivery_date and not yet delivered."""
        if not self.promised_delivery_date:
            return False
        if self.status in TERMINAL_STATES:
            return False
        return timezone.now().date() > self.promised_delivery_date

    # ── Payment Helpers ─────────────────────────────────────────────

    @property
    def is_fully_paid(self):
        """True if amount_paid covers total_amount."""
        return self.amount_paid >= self.total_amount and self.total_amount > 0

    @property
    def can_cancel(self):
        """True if order can be cancelled based on status and payment."""
        from apps.orders.constants import CANCELLABLE_STATES
        return self.status in CANCELLABLE_STATES

    @property
    def requires_payment(self):
        """True if there is outstanding balance."""
        return self.balance_due > 0

    def update_payment_status(self):
        """Auto-update payment_status based on amounts."""
        if self.refund_amount > 0:
            self.payment_status = PaymentStatus.REFUNDED
        elif self.amount_paid >= self.total_amount and self.total_amount > 0:
            self.payment_status = PaymentStatus.PAID
        elif self.amount_paid > 0:
            self.payment_status = PaymentStatus.PARTIAL
        else:
            self.payment_status = PaymentStatus.UNPAID

    # ── Financial Helpers ───────────────────────────────────────────

    def get_profit(self):
        """Calculate profit: total - cost_of_goods - refund_amount."""
        if self.cost_of_goods:
            return self.total_amount - self.cost_of_goods - self.refund_amount
        return None

    def get_effective_discount_percentage(self):
        """Effective discount as a percentage of subtotal."""
        if self.subtotal and self.subtotal > 0:
            from decimal import Decimal
            return (self.discount_amount / self.subtotal * Decimal("100")).quantize(
                Decimal("0.01")
            )
        return None

    # ── Tag Helpers ─────────────────────────────────────────────────

    def add_tag(self, tag):
        """Add a tag if not already present. Returns True if added."""
        tag = tag.strip().lower()
        if tag and tag not in [t.lower() for t in self.tags]:
            self.tags = [*self.tags, tag]
            return True
        return False

    def remove_tag(self, tag):
        """Remove a tag. Returns True if removed."""
        tag = tag.strip().lower()
        original_len = len(self.tags)
        self.tags = [t for t in self.tags if t.lower() != tag]
        return len(self.tags) < original_len

    def has_tag(self, tag):
        """Check if tag exists (case-insensitive)."""
        return tag.strip().lower() in [t.lower() for t in self.tags]

    # ── Custom Field Helpers ────────────────────────────────────────

    def get_custom_field(self, key, default=None):
        """Retrieve a value from custom_fields."""
        return self.custom_fields.get(key, default)

    def set_custom_field(self, key, value):
        """Set a value in custom_fields."""
        self.custom_fields[key] = value
