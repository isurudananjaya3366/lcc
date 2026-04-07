"""
Offline Transaction model.

Stores transactions created while a POS terminal is offline.  Each record
queues a complete transaction payload for synchronisation when connectivity
is restored.  Includes metadata for troubleshooting, integrity hashing,
priority-based sync ordering, and payload extraction helpers.
"""

import hashlib
import json
import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.pos.offline.constants import (
    DATA_SOURCE_CHOICES,
    DATA_SOURCE_WEB_POS,
    NETWORK_QUALITY_CHOICES,
    NETWORK_QUALITY_UNKNOWN,
    SYNC_STATUS_CHOICES,
    SYNC_STATUS_COMPLETED,
    SYNC_STATUS_FAILED,
    SYNC_STATUS_PENDING,
    TRANSACTION_TYPE_CHOICES,
    TRANSACTION_TYPE_SALE,
)


class OfflineTransactionManager(models.Manager):
    """Manager providing common offline-transaction queries."""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_deleted=False)

    def pending(self):
        return self.get_queryset().filter(sync_status=SYNC_STATUS_PENDING)

    def failed(self):
        return self.get_queryset().filter(sync_status=SYNC_STATUS_FAILED)

    def for_terminal(self, terminal):
        return self.get_queryset().filter(terminal=terminal)


class OfflineTransaction(BaseModel):
    """
    A transaction created while the POS terminal was offline.

    The complete sale data lives in the ``payload`` JSONField; additional
    metadata fields capture device context, network quality, and
    integrity information.  Helper methods support sync lifecycle
    management and payload extraction.
    """

    objects = OfflineTransactionManager()
    all_with_deleted = models.Manager()

    # ── Identification ────────────────────────────────────────────────────
    offline_id = models.UUIDField(
        default=uuid.uuid4,
        help_text="Client-generated UUID for this transaction.",
    )
    terminal = models.ForeignKey(
        "pos.POSTerminal",
        on_delete=models.PROTECT,
        related_name="offline_transactions",
        help_text="Terminal that created this transaction.",
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        default=TRANSACTION_TYPE_SALE,
        help_text="Type of offline transaction.",
    )

    # ── Temporal Tracking ─────────────────────────────────────────────────
    offline_timestamp = models.DateTimeField(
        help_text="When the transaction was created offline.",
    )
    received_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the server received this transaction.",
    )
    synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the transaction was successfully synced.",
    )
    last_sync_attempt = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last sync attempt.",
    )

    # ── Sync Status ───────────────────────────────────────────────────────
    sync_status = models.CharField(
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default=SYNC_STATUS_PENDING,
        help_text="Current sync status.",
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of sync retry attempts.",
    )
    max_retries = models.PositiveIntegerField(
        default=3,
        help_text="Maximum allowed retry attempts.",
    )

    # ── Relationships ─────────────────────────────────────────────────────
    sync_log = models.ForeignKey(
        "pos.SyncLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offline_transactions",
        help_text="Sync log entry associated with this transaction.",
    )
    related_sale_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of the Sale record created after successful sync.",
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="offline_transactions",
        help_text="Employee who created the transaction.",
    )

    # ── Metadata (Task 13) ────────────────────────────────────────────────
    device_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Client device information.",
    )
    app_version = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="POS app version at time of transaction.",
    )
    offline_duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Minutes the terminal was offline.",
    )
    transaction_hash = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="SHA-256 hash for payload integrity check.",
    )
    network_quality_at_sync = models.CharField(
        max_length=20,
        choices=NETWORK_QUALITY_CHOICES,
        default=NETWORK_QUALITY_UNKNOWN,
        help_text="Network quality during sync.",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Error message from last sync attempt.",
    )
    validation_errors = models.JSONField(
        null=True,
        blank=True,
        help_text="Detailed validation errors.",
    )
    customer_id_offline = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Customer reference from offline data.",
    )
    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Transaction total for quick reference.",
    )
    items_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of line items.",
    )
    sync_priority = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Sync priority (1=low, 10=urgent).",
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Additional notes or comments.",
    )
    data_source = models.CharField(
        max_length=50,
        choices=DATA_SOURCE_CHOICES,
        default=DATA_SOURCE_WEB_POS,
        help_text="Source application type.",
    )

    # ── Payload (Task 14) ─────────────────────────────────────────────────
    payload = models.JSONField(
        default=dict,
        help_text="Complete transaction data in JSON format.",
    )
    payload_size_bytes = models.PositiveIntegerField(
        default=0,
        help_text="Size of payload JSON in bytes.",
    )
    payload_compressed = models.BooleanField(
        default=False,
        help_text="Whether the payload is gzip-compressed.",
    )

    class Meta(BaseModel.Meta):
        db_table = "pos_offline_transaction"
        verbose_name = "Offline Transaction"
        verbose_name_plural = "Offline Transactions"
        ordering = ["sync_priority", "offline_timestamp"]
        constraints = [
            models.UniqueConstraint(
                fields=["offline_id"],
                name="uq_offline_transaction_id",
            ),
        ]
        indexes = [
            models.Index(
                fields=["sync_status"],
                name="idx_offtxn_status",
            ),
            models.Index(
                fields=["terminal", "offline_timestamp"],
                name="idx_offtxn_terminal_date",
            ),
            models.Index(
                fields=["sync_status", "retry_count"],
                name="idx_offtxn_status_retry",
            ),
            models.Index(
                fields=["sync_priority", "offline_timestamp"],
                name="idx_offtxn_priority_date",
            ),
        ]

    def __str__(self):
        return f"{self.offline_id} ({self.transaction_type})"

    # ── Status Helpers ────────────────────────────────────────────────────

    def is_pending(self):
        """Return True if the transaction is awaiting sync."""
        return self.sync_status == SYNC_STATUS_PENDING

    def is_synced(self):
        """Return True if the transaction has been successfully synced."""
        return self.sync_status == SYNC_STATUS_COMPLETED

    def can_retry(self):
        """Return True if more retry attempts are available."""
        return (
            self.sync_status == SYNC_STATUS_FAILED
            and self.retry_count < self.max_retries
        )

    def increment_retry(self):
        """Increment the retry counter and update timestamps."""
        self.retry_count += 1
        self.last_sync_attempt = timezone.now()
        if self.retry_count >= self.max_retries:
            self.sync_status = SYNC_STATUS_FAILED
        else:
            self.sync_status = SYNC_STATUS_PENDING
        self.save()

    def mark_synced(self, sale_id=None):
        """Mark the transaction as successfully synced."""
        self.sync_status = SYNC_STATUS_COMPLETED
        self.synced_at = timezone.now()
        if sale_id is not None:
            self.related_sale_id = sale_id
        self.save()

    # ── Payload Helpers ───────────────────────────────────────────────────

    def get_header(self):
        """Extract the transaction header from the payload."""
        header = self.payload.get("header")
        if header is None:
            raise ValueError("Payload is missing 'header' key.")
        return header

    def get_line_items(self):
        """Extract line items from the payload."""
        return self.payload.get("line_items", [])

    def get_payments(self):
        """Extract payments from the payload."""
        return self.payload.get("payments", [])

    def get_customer_data(self):
        """Extract customer data from the payload, or None."""
        return self.payload.get("customer")

    def get_payload_stats(self):
        """Return summary statistics extracted from the payload."""
        header = self.payload.get("header", {})
        return {
            "line_items_count": len(self.get_line_items()),
            "payments_count": len(self.get_payments()),
            "grand_total": Decimal(str(header.get("grand_total", "0.00"))),
            "has_customer": self.get_customer_data() is not None,
            "transaction_type": header.get("transaction_type", ""),
            "payload_size_kb": round(self.payload_size_bytes / 1024, 2),
        }

    def validate_payload(self):
        """
        Validate required payload keys and basic integrity.

        Returns a dict ``{"valid": bool, "errors": [str]}``.
        """
        errors = []
        if "header" not in self.payload:
            errors.append("Missing transaction header.")
        else:
            required_header = [
                "offline_id", "transaction_type", "offline_timestamp",
                "terminal_id", "employee_id", "grand_total",
            ]
            for field in required_header:
                if field not in self.payload["header"]:
                    errors.append(f"Missing required header field: {field}")

        line_items = self.payload.get("line_items")
        if not line_items or not isinstance(line_items, list) or len(line_items) < 1:
            errors.append("No line items in transaction.")

        payments = self.payload.get("payments")
        if not payments or not isinstance(payments, list) or len(payments) < 1:
            errors.append("No payments in transaction.")

        return {"valid": len(errors) == 0, "errors": errors}

    def verify_payload_integrity(self):
        """Return True if the stored hash matches a fresh calculation."""
        if not self.transaction_hash:
            return False
        calculated = self._calculate_hash()
        return calculated == self.transaction_hash

    # ── Save Override ─────────────────────────────────────────────────────

    def save(self, *args, **kwargs):
        """Auto-calculate hash, size, and quick-reference fields on save."""
        if self.payload:
            self.payload_size_bytes = len(
                json.dumps(self.payload, sort_keys=True).encode("utf-8")
            )
            self.transaction_hash = self._calculate_hash()
            # Extract quick-reference totals from header
            header = self.payload.get("header", {})
            if "grand_total" in header:
                self.grand_total = Decimal(str(header["grand_total"]))
            line_items = self.payload.get("line_items")
            if isinstance(line_items, list):
                self.items_count = len(line_items)
        super().save(*args, **kwargs)

    # ── Internal ──────────────────────────────────────────────────────────

    def _calculate_hash(self):
        """Return SHA-256 hex digest of the normalised payload JSON."""
        normalised = json.dumps(self.payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalised.encode("utf-8")).hexdigest()

    # ── Sale Creation ─────────────────────────────────────────────────────

    def create_sale_from_payload(self):
        """
        Parse the stored payload and create a Sale (Order) with related items
        and payments.  Returns the created order instance.

        Raises ``RuntimeError`` if the payload is missing or invalid, or if
        this transaction is not in a state suitable for conversion.
        """
        from apps.orders.models import Order, OrderItem  # late import

        if not self.payload:
            raise RuntimeError("Cannot create sale: payload is empty.")
        if self.sync_status != "completed":
            raise RuntimeError(
                f"Cannot create sale: transaction status is '{self.sync_status}', "
                "expected 'completed'."
            )

        header = self.get_header()
        line_items = self.get_line_items()
        payments = self.get_payments()

        if not header:
            raise RuntimeError("Payload missing 'header'.")
        if not line_items:
            raise RuntimeError("Payload missing 'line_items'.")

        # Create the order (sale) ------------------------------------------
        order = Order.objects.create(
            order_type=header.get("transaction_type", "sale"),
            subtotal=Decimal(str(header.get("subtotal", 0))),
            tax_total=Decimal(str(header.get("tax_total", 0))),
            discount_total=Decimal(str(header.get("discount_total", 0))),
            grand_total=Decimal(str(header.get("grand_total", self.grand_total or 0))),
            notes=header.get("notes", ""),
            source="offline",
        )

        # Create line items ------------------------------------------------
        for item in line_items:
            OrderItem.objects.create(
                order=order,
                product_id=item.get("product_id"),
                variant_id=item.get("variant_id"),
                quantity=Decimal(str(item.get("quantity", 0))),
                unit_price=Decimal(str(item.get("unit_price", 0))),
                subtotal=Decimal(str(item.get("subtotal", 0))),
                tax_amount=Decimal(str(item.get("tax_amount", 0))),
                discount_amount=Decimal(str(item.get("discount_amount", 0))),
            )

        # Link back to this offline transaction ----------------------------
        self.related_sale_id = order.pk
        self.synced_at = timezone.now()
        self.save(update_fields=["related_sale_id", "synced_at"])

        return order
