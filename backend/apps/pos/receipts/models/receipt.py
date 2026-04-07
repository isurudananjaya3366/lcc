"""
Receipt model — stores generated receipt data for each POS transaction.

Tasks 17-22, 34: Receipt core fields, reference, transaction links,
type, timestamps, JSON data, and duplicate handling.
"""

import copy
import logging

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.pos.receipts.constants import RECEIPT_TYPES

logger = logging.getLogger(__name__)

RECEIPT_TYPE_CHOICES = [
    ("SALE", "Sale Receipt"),
    ("REFUND", "Refund Receipt"),
    ("VOID", "Void Receipt"),
    ("DUPLICATE", "Duplicate Receipt"),
]


class ReceiptManager(models.Manager):
    """Custom manager with receipt-specific queries."""

    def for_cart(self, cart):
        return self.get_queryset().filter(cart=cart)

    def for_transaction(self, transaction_id):
        return self.get_queryset().filter(transaction_id=transaction_id)

    def by_type(self, receipt_type):
        return self.get_queryset().filter(receipt_type=receipt_type)

    def originals(self):
        return self.get_queryset().exclude(receipt_type="DUPLICATE")


class Receipt(BaseModel):
    """
    Stores generated receipt data for a POS transaction.

    Each receipt is linked to a cart and preserves the exact receipt content
    at the time of generation for reprinting, emailing, and auditing.
    """

    # Task 18: Receipt reference
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Unique receipt identifier (auto-generated: REC-YYYYMMDD-NNNNN)",
    )

    # Task 19: Transaction links
    cart = models.ForeignKey(
        "pos.POSCart",
        related_name="receipts",
        on_delete=models.PROTECT,
        db_index=True,
        help_text="The POS cart this receipt was generated from",
    )
    transaction_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text="External transaction identifier (optional)",
    )

    # Task 20: Receipt type
    receipt_type = models.CharField(
        max_length=20,
        choices=RECEIPT_TYPE_CHOICES,
        default="SALE",
        db_index=True,
        help_text="Type of receipt: SALE, REFUND, VOID, or DUPLICATE",
    )

    # Task 19: Template used
    template = models.ForeignKey(
        "pos.ReceiptTemplate",
        related_name="receipts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Template used to generate this receipt",
    )

    # Task 21: Generation timestamp fields
    generated_at = models.DateTimeField(
        db_index=True,
        help_text="When this receipt was generated",
    )
    printed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this receipt was last printed (null if never printed)",
    )
    emailed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this receipt was last emailed (null if never emailed)",
    )

    # Task 22: Receipt data JSON
    receipt_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete receipt data in JSON format (immutable after generation)",
    )

    # Task 34: Duplicate handling
    original_receipt = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duplicates",
        help_text="Original receipt if this is a duplicate",
    )
    reprint_count = models.IntegerField(
        default=0,
        help_text="Number of times this receipt has been reprinted",
    )

    # Created by
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="generated_receipts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    objects = ReceiptManager()

    class Meta(BaseModel.Meta):
        db_table = "pos_receipt"
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"
        ordering = ["-generated_at"]
        indexes = [
            models.Index(fields=["cart", "receipt_type"]),
        ]

    def __str__(self):
        return f"{self.receipt_number} ({self.receipt_type})"

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("pos:receipt-detail", kwargs={"pk": self.pk})

    # ── Task 20: Type helper methods ──────────────────────────

    def is_sale(self):
        return self.receipt_type == "SALE"

    def is_refund(self):
        return self.receipt_type == "REFUND"

    def is_void(self):
        return self.receipt_type == "VOID"

    def is_duplicate(self):
        return self.receipt_type == "DUPLICATE"

    def get_watermark_text(self):
        if self.is_refund():
            return "REFUND"
        if self.is_void():
            return "VOID"
        if self.is_duplicate():
            return "DUPLICATE COPY"
        return None

    # ── Task 21: Timestamp management ─────────────────────────

    def mark_as_printed(self):
        self.printed_at = timezone.now()
        self.save(update_fields=["printed_at", "updated_on"])

    def mark_as_emailed(self):
        self.emailed_at = timezone.now()
        self.save(update_fields=["emailed_at", "updated_on"])

    @property
    def was_printed(self):
        return self.printed_at is not None

    @property
    def was_emailed(self):
        return self.emailed_at is not None

    # ── Task 22: Receipt data accessors ───────────────────────

    def get_header_data(self):
        return self.receipt_data.get("header", {})

    def get_items_data(self):
        return self.receipt_data.get("items", [])

    def get_totals_data(self):
        return self.receipt_data.get("totals", {})

    def get_payments_data(self):
        return self.receipt_data.get("payments", [])

    def get_qr_code_data(self):
        return self.receipt_data.get("qr_code", {})

    # ── Task 34: Duplicate handling ───────────────────────────

    def generate_duplicate(self, requested_by=None):
        """Create a duplicate copy of this receipt."""
        from django.core.exceptions import ValidationError

        self._validate_can_duplicate()

        duplicate = Receipt(
            cart=self.cart,
            transaction_id=self.transaction_id,
            receipt_type="DUPLICATE",
            receipt_number=self.receipt_number,
            template=self.template,
            original_receipt=self,
            generated_at=timezone.now(),
            receipt_data=self._prepare_duplicate_data(),
            generated_by=requested_by,
        )
        duplicate.save()

        self.reprint_count += 1
        self.save(update_fields=["reprint_count", "updated_on"])

        logger.info(
            "Receipt reprinted: %s (count=%d)",
            self.receipt_number,
            self.reprint_count,
            extra={
                "original_receipt_id": str(self.id),
                "duplicate_receipt_id": str(duplicate.id),
            },
        )
        return duplicate

    @property
    def is_duplicate_receipt(self):
        """True if this is a duplicate copy."""
        return self.receipt_type == "DUPLICATE"

    @property
    def is_original_receipt(self):
        """True if this is an original (non-duplicate) receipt."""
        return self.original_receipt is None

    def get_original(self):
        """Return the original receipt, or self if already an original."""
        if self.original_receipt is not None:
            return self.original_receipt
        return self

    def _validate_can_duplicate(self):
        from django.core.exceptions import ValidationError

        if self.receipt_type == "DUPLICATE":
            raise ValidationError(
                "Cannot duplicate a duplicate receipt. Use the original receipt."
            )
        if self.receipt_type == "VOID":
            raise ValidationError("Cannot duplicate a voided receipt.")

    def _prepare_duplicate_data(self):
        duplicate_data = copy.deepcopy(self.receipt_data)
        duplicate_data["is_duplicate"] = True
        duplicate_data["original_receipt_number"] = self.receipt_number
        duplicate_data["original_generated_at"] = (
            self.generated_at.isoformat() if self.generated_at else None
        )
        duplicate_data["reprinted_at"] = timezone.now().isoformat()

        if "header" in duplicate_data:
            duplicate_data["header"]["duplicate_marker"] = True
            duplicate_data["header"]["duplicate_text"] = "DUPLICATE COPY"

        if "transaction" in duplicate_data:
            duplicate_data["transaction"]["is_duplicate"] = True
            duplicate_data["transaction"]["original_date"] = duplicate_data[
                "transaction"
            ].get("date")
            now = timezone.now()
            duplicate_data["transaction"]["reprint_date"] = now.strftime("%Y-%m-%d")
            duplicate_data["transaction"]["reprint_time"] = now.strftime("%H:%M:%S")

        return duplicate_data
