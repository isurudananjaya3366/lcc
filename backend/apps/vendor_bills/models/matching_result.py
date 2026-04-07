"""MatchingResult model for storing 3-way matching results."""

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import TimestampMixin, UUIDMixin


MATCH_STATUS_MATCHED = "matched"
MATCH_STATUS_VARIANCE = "variance"
MATCH_STATUS_UNMATCHED = "unmatched"

MATCH_STATUS_CHOICES = [
    (MATCH_STATUS_MATCHED, "Matched"),
    (MATCH_STATUS_VARIANCE, "Variance"),
    (MATCH_STATUS_UNMATCHED, "Unmatched"),
]


class MatchingResult(UUIDMixin, TimestampMixin, models.Model):
    """Stores the result of 3-way matching between PO, GRN, and Bill."""

    # References
    vendor_bill = models.ForeignKey(
        "vendor_bills.VendorBill",
        on_delete=models.CASCADE,
        related_name="matching_results",
        help_text="The vendor bill being matched",
    )
    bill_line = models.OneToOneField(
        "vendor_bills.BillLineItem",
        on_delete=models.CASCADE,
        related_name="matching_result",
        help_text="The specific bill line item",
    )
    po_line = models.ForeignKey(
        "purchases.POLineItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matching_results",
        help_text="Matched PO line item",
    )
    grn_line = models.ForeignKey(
        "purchases.GRNLineItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matching_results",
        help_text="Matched GRN line item",
    )

    # Match status
    match_status = models.CharField(
        max_length=20,
        choices=MATCH_STATUS_CHOICES,
        default=MATCH_STATUS_UNMATCHED,
        db_index=True,
        help_text="Result of the matching process",
    )

    # Quantity fields
    quantity_ordered = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantity from PO",
    )
    quantity_received = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantity from GRN",
    )
    quantity_billed = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Quantity from Bill",
    )
    quantity_variance = models.IntegerField(
        default=0,
        help_text="Variance in quantities",
    )

    # Price fields
    po_unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Unit price from PO",
    )
    grn_unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Unit price from GRN (if available)",
    )
    billed_unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Unit price on the bill",
    )
    price_variance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Price variance amount",
    )

    # Total variance
    total_variance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total variance amount",
    )

    # Tolerance
    is_within_tolerance = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the variance is within tolerance",
    )

    # Approval fields
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_matching_results",
        help_text="User who approved the variance",
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the variance was approved",
    )
    approval_notes = models.TextField(
        blank=True,
        help_text="Notes from variance approval",
    )

    # Metadata
    matched_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the matching was performed",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional matching metadata",
    )

    class Meta:
        ordering = ["-matched_at"]
        verbose_name = "Matching Result"
        verbose_name_plural = "Matching Results"
        indexes = [
            models.Index(fields=["match_status"], name="idx_matchresult_status"),
            models.Index(fields=["is_within_tolerance"], name="idx_matchresult_tolerance"),
        ]

    def __str__(self):
        return f"Match: {self.vendor_bill.bill_number} Line {self.bill_line.line_number} - {self.match_status}"

    def calculate_variances(self):
        """Calculate all variances from the linked documents."""
        if self.quantity_ordered and self.quantity_billed:
            self.quantity_variance = self.quantity_billed - self.quantity_ordered
        if self.po_unit_price and self.billed_unit_price:
            self.price_variance = self.billed_unit_price - self.po_unit_price
        qty = self.quantity_billed or 0
        self.total_variance = self.price_variance * Decimal(str(qty))

    def check_tolerance(self, tolerance_amount=None, tolerance_percent=None):
        """Check if variance is within acceptable tolerance."""
        from apps.vendor_bills.constants import (
            DEFAULT_MATCHING_TOLERANCE,
            DEFAULT_MATCHING_TOLERANCE_PERCENT,
        )

        tol_amt = tolerance_amount or DEFAULT_MATCHING_TOLERANCE
        tol_pct = tolerance_percent or DEFAULT_MATCHING_TOLERANCE_PERCENT

        if abs(self.total_variance) <= tol_amt:
            self.is_within_tolerance = True
        elif self.po_unit_price and self.po_unit_price > 0:
            pct = abs(self.price_variance / self.po_unit_price) * 100
            self.is_within_tolerance = pct <= tol_pct
        else:
            self.is_within_tolerance = self.total_variance == Decimal("0.00")

    def approve(self, user, notes=""):
        """Approve a variance result."""
        self.approved_by = user
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.match_status = MATCH_STATUS_MATCHED
        self.save(update_fields=[
            "approved_by", "approved_at", "approval_notes", "match_status",
        ])

    def get_variance_summary(self):
        """Return a summary dict of variances."""
        return {
            "quantity_variance": self.quantity_variance,
            "price_variance": float(self.price_variance),
            "total_variance": float(self.total_variance),
            "is_within_tolerance": self.is_within_tolerance,
            "match_status": self.match_status,
        }
