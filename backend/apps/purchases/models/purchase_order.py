"""
PurchaseOrder model for the purchases application.

Defines the full PurchaseOrder model with core identification, vendor,
dates, shipping, financial, payment, user tracking, notes, approval,
warehouse, PDF storage, indexes, and constraints.
"""

from datetime import date
from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.core.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from apps.purchases.constants import (
    DEFAULT_PAYMENT_STATUS,
    DEFAULT_PO_STATUS,
    PAYMENT_STATUS_CHOICES,
    PO_STATUS_CHOICES,
)


class PurchaseOrder(UUIDMixin, TimestampMixin, SoftDeleteMixin, models.Model):
    """
    Full purchase order record for a tenant.

    Represents a purchase order sent to a vendor for goods/services,
    tracking the complete lifecycle from draft through receiving and closure.
    """

    # ── Core Fields ─────────────────────────────────────────────────
    po_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        db_index=True,
        help_text="Auto-generated PO number (PO-YYYY-NNNNN)",
    )
    status = models.CharField(
        max_length=20,
        choices=PO_STATUS_CHOICES,
        default=DEFAULT_PO_STATUS,
        db_index=True,
    )

    # ── Vendor Fields (Task 05) ─────────────────────────────────────
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        help_text="Supplier for this PO",
    )
    vendor_reference = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Vendor's own order/reference number",
    )

    # ── Date Fields (Task 06) ───────────────────────────────────────
    order_date = models.DateField(
        default=date.today,
        help_text="Date the PO was created",
    )
    expected_delivery_date = models.DateField(
        blank=True,
        null=True,
        db_index=True,
        help_text="Expected delivery date from vendor",
    )
    acknowledged_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When vendor acknowledged the order",
    )
    received_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When all items were received",
    )

    # ── Shipping Fields (Task 07) ───────────────────────────────────
    ship_to_address = models.TextField(
        blank=True,
        default="",
        help_text="Delivery address",
    )
    shipping_method = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Transport method (e.g. Ground, Air Freight)",
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Shipping charges",
    )
    carrier = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Shipping company name",
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Shipment tracking ID",
    )

    # ── Financial Fields (Task 08) ──────────────────────────────────
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Sum of line item totals",
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Order-level discount (monetary)",
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Order-level discount (percentage)",
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total tax",
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Grand total",
    )
    currency = models.CharField(
        max_length=3,
        default="LKR",
        help_text="ISO currency code",
    )

    # ── Payment Fields (Task 09) ────────────────────────────────────
    payment_terms = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Payment terms description (e.g. Net 30)",
    )
    payment_terms_days = models.IntegerField(
        blank=True,
        null=True,
        help_text="Days until payment due",
    )
    payment_due_date = models.DateField(
        blank=True,
        null=True,
        help_text="Payment deadline",
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=DEFAULT_PAYMENT_STATUS,
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total payments made",
    )

    # ── User Fields (Task 10) ───────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_purchase_orders",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="approved_purchase_orders",
        blank=True,
        null=True,
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="received_purchase_orders",
        blank=True,
        null=True,
    )

    # ── Notes Fields (Task 11) ──────────────────────────────────────
    notes = models.TextField(blank=True, default="")
    internal_notes = models.TextField(blank=True, default="")
    vendor_notes = models.TextField(blank=True, default="")
    delivery_instructions = models.TextField(blank=True, default="")

    # ── Approval Fields (Task 12) ───────────────────────────────────
    requires_approval = models.BooleanField(default=False)
    approved_at = models.DateTimeField(blank=True, null=True)
    approval_notes = models.TextField(blank=True, default="")
    rejected_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, default="")

    # ── Warehouse Field (Task 13) ───────────────────────────────────
    receiving_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        blank=True,
        null=True,
        help_text="Destination warehouse for receiving",
    )

    # ── PDF Storage Fields (Task 15) ────────────────────────────────
    pdf_file = models.FileField(
        upload_to="purchase_orders/pdfs/%Y/%m/",
        blank=True,
        null=True,
    )
    pdf_generated_at = models.DateTimeField(blank=True, null=True)
    pdf_version = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        ordering = ["-created_on"]

        # Task 16: Indexes
        indexes = [
            models.Index(fields=["status"], name="idx_po_status"),
            models.Index(fields=["order_date"], name="idx_po_order_date"),
            models.Index(
                fields=["expected_delivery_date"], name="idx_po_exp_delivery"
            ),
            models.Index(
                fields=["status", "vendor"], name="idx_po_status_vendor"
            ),
            models.Index(
                fields=["status", "order_date"], name="idx_po_status_date"
            ),
            models.Index(
                fields=["vendor", "order_date"], name="idx_po_vendor_date"
            ),
            models.Index(
                fields=["status", "expected_delivery_date"],
                name="idx_po_status_exp_del",
            ),
            models.Index(
                fields=["payment_status"], name="idx_po_payment_status"
            ),
        ]

        # Task 17: Constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(subtotal__gte=0),
                name="po_subtotal_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(tax_amount__gte=0),
                name="po_tax_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(total__gte=0),
                name="po_total_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(shipping_cost__gte=0),
                name="po_shipping_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(discount_amount__gte=0),
                name="po_discount_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(amount_paid__gte=0),
                name="po_amount_paid_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(pdf_version__gte=1),
                name="po_pdf_version_positive",
            ),
        ]

    def __str__(self):
        return self.po_number or "New PO"

    def save(self, *args, **kwargs):
        if not self.po_number:
            self.po_number = self._generate_po_number()
        super().save(*args, **kwargs)

    def _generate_po_number(self):
        """Auto-generate PO number: PO-YYYY-NNNNN."""
        from django.db.models import Max

        year = date.today().year
        prefix = f"PO-{year}-"
        last_po = (
            PurchaseOrder.objects.filter(po_number__startswith=prefix)
            .aggregate(max_num=Max("po_number"))
        )
        max_num = last_po["max_num"]
        if max_num:
            try:
                seq = int(max_num.split("-")[-1]) + 1
            except (ValueError, IndexError):
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:05d}"
