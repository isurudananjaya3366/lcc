from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel
from apps.pos.constants import (
    CART_STATUS_ACTIVE,
    CART_STATUS_CHOICES,
    CART_STATUS_COMPLETED,
    CART_STATUS_HELD,
    CART_STATUS_VOIDED,
    CART_STATUS_ABANDONED,
    DISCOUNT_TYPE_FIXED,
    DISCOUNT_TYPE_PERCENT,
)


class POSCartManager(models.Manager):
    """Manager for POSCart."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_deleted=False)

    def active_carts(self):
        return self.get_queryset().filter(status=CART_STATUS_ACTIVE)

    def for_session(self, session):
        return self.get_queryset().filter(session=session)

    def held_carts(self):
        return self.get_queryset().filter(status=CART_STATUS_HELD)


class POSCart(BaseModel):
    """
    POS shopping cart / transaction builder.

    Tracks items, discounts, taxes, and totals for a POS transaction.
    """

    # ── Session & Customer ────────────────────────────────────────────────
    session = models.ForeignKey(
        "pos.POSSession",
        on_delete=models.CASCADE,
        related_name="carts",
        db_index=True,
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pos_carts",
    )
    status = models.CharField(
        max_length=20,
        choices=CART_STATUS_CHOICES,
        default=CART_STATUS_ACTIVE,
        db_index=True,
    )

    # ── Reference Number ──────────────────────────────────────────────────
    reference_number = models.CharField(
        max_length=50, unique=True, blank=True, editable=False, db_index=True
    )

    # ── Timestamps ────────────────────────────────────────────────────────
    completed_at = models.DateTimeField(null=True, blank=True)
    voided_at = models.DateTimeField(null=True, blank=True)
    held_at = models.DateTimeField(null=True, blank=True)
    abandoned_at = models.DateTimeField(null=True, blank=True)

    # ── Held Cart Fields ──────────────────────────────────────────────────
    held_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="held_carts",
        verbose_name=_("Held By"),
    )
    held_reason = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Held Reason"),
    )
    held_identifier = models.CharField(
        max_length=50,
        blank=True,
        default="",
        db_index=True,
        verbose_name=_("Held Identifier"),
        help_text=_("Unique identifier for retrieving held carts"),
    )

    # ── Totals ────────────────────────────────────────────────────────────
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    discount_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    tax_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        db_index=True,
    )

    # ── Cart-Level Discount ───────────────────────────────────────────────
    cart_discount_type = models.CharField(
        max_length=10,
        choices=[
            (DISCOUNT_TYPE_PERCENT, "Percentage"),
            (DISCOUNT_TYPE_FIXED, "Fixed Amount"),
        ],
        null=True,
        blank=True,
    )
    cart_discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        default=Decimal("0.00"),
    )
    cart_discount_reason = models.CharField(
        max_length=200, blank=True, default=""
    )
    coupon_code = models.CharField(
        max_length=50, blank=True, default="", db_index=True
    )
    cart_discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    # ── Notes ─────────────────────────────────────────────────────────────
    notes = models.TextField(blank=True, default="")

    # ── Managers ──────────────────────────────────────────────────────────
    objects = POSCartManager()
    all_with_deleted = models.Manager()

    class Meta:
        db_table = "pos_cart"
        verbose_name = "POS Cart"
        verbose_name_plural = "POS Carts"
        ordering = ["-created_on"]
        indexes = [
            models.Index(
                fields=["reference_number"], name="idx_pos_cart_ref"
            ),
            models.Index(fields=["status"], name="idx_pos_cart_status"),
            models.Index(
                fields=["session", "status"], name="idx_pos_cart_sess_stat"
            ),
        ]

    def __str__(self):
        return f"Cart {self.reference_number}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self._generate_reference_number()
        super().save(*args, **kwargs)

    def _generate_reference_number(self):
        """Generate reference: POS-{YEAR}-{TERMINAL_CODE}-{SEQUENCE}."""
        now = timezone.now()
        year = now.strftime("%Y")
        terminal_code = self.session.terminal.code

        prefix = f"POS-{year}-{terminal_code}-"
        last_cart = (
            POSCart.all_with_deleted.filter(
                reference_number__startswith=prefix
            )
            .order_by("-reference_number")
            .first()
        )

        if last_cart:
            last_seq = int(last_cart.reference_number.split("-")[-1])
            next_seq = last_seq + 1
        else:
            next_seq = 1

        return f"{prefix}{next_seq:06d}"

    # ── Status Methods ────────────────────────────────────────────────────
    def update_status(self, new_status):
        """Update cart status and set appropriate timestamp."""
        self.status = new_status
        now = timezone.now()
        if new_status == CART_STATUS_COMPLETED:
            self.completed_at = now
        elif new_status == CART_STATUS_VOIDED:
            self.voided_at = now
        elif new_status == CART_STATUS_HELD:
            self.held_at = now
        elif new_status == CART_STATUS_ABANDONED:
            self.abandoned_at = now
        self.save()

    @property
    def is_modifiable(self):
        """Cart can be modified if ACTIVE or HELD."""
        return self.status in (CART_STATUS_ACTIVE, CART_STATUS_HELD)

    @property
    def has_items(self):
        return self.items.exists()

    @property
    def item_count(self):
        return self.items.count()

    @property
    def has_notes(self):
        return bool(self.notes and self.notes.strip())

    @property
    def notes_preview(self):
        if len(self.notes) > 50:
            return self.notes[:50] + "..."
        return self.notes

    @property
    def duration_to_complete(self):
        """Time from cart creation to completion."""
        if self.completed_at and self.created_on:
            return self.completed_at - self.created_on
        return None

    @property
    def duration_active(self):
        """Time since cart was created (for active carts)."""
        if self.created_on:
            return timezone.now() - self.created_on
        return None

    @property
    def formatted_subtotal(self):
        return f"\u20A8 {self.subtotal:,.2f}"

    @property
    def formatted_grand_total(self):
        return f"\u20A8 {self.grand_total:,.2f}"

    @property
    def formatted_cart_discount(self):
        """Format cart discount for display."""
        if not self.has_cart_discount:
            return ""
        if self.cart_discount_type == DISCOUNT_TYPE_PERCENT:
            return f"{self.cart_discount_value}% (\u20A8 {self.cart_discount_amount:,.2f})"
        return f"\u20A8 {self.cart_discount_amount:,.2f}"

    @property
    def has_cart_discount(self):
        return (
            self.cart_discount_type is not None
            and self.cart_discount_value
            and self.cart_discount_value > 0
        )

    # ── Discount Calculation ──────────────────────────────────────────────
    def calculate_cart_discount(self):
        """Calculate cart-level discount amount."""
        if not self.has_cart_discount:
            self.cart_discount_amount = Decimal("0.00")
            return Decimal("0.00")

        if self.cart_discount_type == DISCOUNT_TYPE_PERCENT:
            amount = (self.subtotal * self.cart_discount_value / 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        elif self.cart_discount_type == DISCOUNT_TYPE_FIXED:
            amount = min(self.cart_discount_value, self.subtotal)
        else:
            amount = Decimal("0.00")

        self.cart_discount_amount = amount
        return amount

    def recalculate_totals(self):
        """Recalculate all cart totals from items."""
        from apps.pos.cart.services.cart_service import CartService

        return CartService.calculate_totals(self)
