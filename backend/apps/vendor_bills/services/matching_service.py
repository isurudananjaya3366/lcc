"""3-way matching service for PO → GRN → Bill matching."""

import logging
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.vendor_bills.constants import (
    DEFAULT_MATCHING_TOLERANCE,
    DEFAULT_MATCHING_TOLERANCE_PERCENT,
    MATCHING_STATUS_MATCHED,
    MATCHING_STATUS_NOT_MATCHED,
    MATCHING_STATUS_VARIANCE_EXCEEDS,
    MATCHING_STATUS_VARIANCE_WITHIN,
)
from apps.vendor_bills.models.matching_result import (
    MATCH_STATUS_MATCHED,
    MATCH_STATUS_UNMATCHED,
    MATCH_STATUS_VARIANCE,
    MatchingResult,
)

logger = logging.getLogger(__name__)


class MatchingService:
    """Service for 3-way matching between Purchase Orders, GRNs, and Bills."""

    def __init__(self, tolerance_amount=None, tolerance_percent=None):
        self.tolerance_amount = tolerance_amount or DEFAULT_MATCHING_TOLERANCE
        self.tolerance_percent = tolerance_percent or DEFAULT_MATCHING_TOLERANCE_PERCENT

    @staticmethod
    def get_bill(bill_id):
        """Get a vendor bill by ID."""
        from apps.vendor_bills.models import VendorBill
        return VendorBill.objects.get(pk=bill_id)

    @staticmethod
    def get_bill_lines(bill):
        """Get all line items for a bill."""
        return bill.line_items.all().order_by("line_number")

    @staticmethod
    def get_matchable_po_lines(purchase_order):
        """Get PO lines that can be matched to bill lines."""
        return purchase_order.line_items.all().order_by("line_number")

    @staticmethod
    def get_matchable_grn_lines(purchase_order):
        """Get GRN lines from all GRNs for a PO."""
        from apps.purchases.models import GRNLineItem
        return GRNLineItem.objects.filter(
            goods_receipt__purchase_order=purchase_order
        ).order_by("line_number")

    def is_within_tolerance(self, variance, reference_amount=None):
        """Check if a variance is within acceptable tolerance."""
        if abs(variance) <= self.tolerance_amount:
            return True
        if reference_amount and reference_amount > 0:
            pct = abs(variance / reference_amount) * Decimal("100")
            return pct <= self.tolerance_percent
        return variance == Decimal("0.00")

    def calculate_variance_percentage(self, variance, reference_amount):
        """Calculate variance as a percentage."""
        if reference_amount and reference_amount > 0:
            return (variance / reference_amount) * Decimal("100")
        return Decimal("0.00")

    @transaction.atomic
    def match_bill_to_po(self, bill):
        """Match bill lines to PO lines."""
        if not bill.purchase_order:
            return {"matched": 0, "unmatched": 0, "message": "No PO linked"}

        po_lines = {
            line.pk: line
            for line in self.get_matchable_po_lines(bill.purchase_order)
        }
        matched = 0
        unmatched = 0

        for bill_line in self.get_bill_lines(bill):
            if bill_line.po_line_id and bill_line.po_line_id in po_lines:
                matched += 1
                continue

            # Try auto-matching by product/variant
            match_found = False
            for po_line in po_lines.values():
                if (
                    bill_line.product_id
                    and po_line.product_id == bill_line.product_id
                    and (
                        not bill_line.variant_id
                        or po_line.variant_id == bill_line.variant_id
                    )
                ):
                    bill_line.po_line = po_line
                    bill_line.quantity_ordered = po_line.quantity_ordered
                    bill_line.unit_price = po_line.unit_price
                    bill_line.save(update_fields=[
                        "po_line", "quantity_ordered", "unit_price",
                    ])
                    matched += 1
                    match_found = True
                    break

            if not match_found:
                unmatched += 1

        return {"matched": matched, "unmatched": unmatched}

    @transaction.atomic
    def match_bill_to_grn(self, bill):
        """Match bill lines to GRN lines."""
        if not bill.purchase_order:
            return {"matched": 0, "unmatched": 0, "message": "No PO linked"}

        grn_lines = list(self.get_matchable_grn_lines(bill.purchase_order))
        matched = 0
        unmatched = 0

        for bill_line in self.get_bill_lines(bill):
            if bill_line.grn_line_id:
                matched += 1
                continue

            # Try matching via PO line
            match_found = False
            if bill_line.po_line_id:
                for grn_line in grn_lines:
                    if grn_line.po_line_id == bill_line.po_line_id:
                        bill_line.grn_line = grn_line
                        bill_line.quantity_received = grn_line.quantity_received
                        bill_line.save(update_fields=[
                            "grn_line", "quantity_received",
                        ])
                        matched += 1
                        match_found = True
                        break

            if not match_found:
                unmatched += 1

        return {"matched": matched, "unmatched": unmatched}

    @transaction.atomic
    def perform_3way_match(self, bill):
        """Perform full 3-way matching: PO → GRN → Bill."""
        # Step 1: Match to PO
        po_result = self.match_bill_to_po(bill)
        # Step 2: Match to GRN
        grn_result = self.match_bill_to_grn(bill)

        # Step 3: Create MatchingResult for each line
        results = []
        all_matched = True
        any_variance = False

        for bill_line in self.get_bill_lines(bill):
            result, _ = MatchingResult.objects.update_or_create(
                bill_line=bill_line,
                defaults={
                    "vendor_bill": bill,
                    "po_line": bill_line.po_line,
                    "grn_line": bill_line.grn_line,
                    "quantity_ordered": bill_line.quantity_ordered,
                    "quantity_received": bill_line.quantity_received,
                    "quantity_billed": bill_line.quantity,
                    "po_unit_price": bill_line.unit_price,
                    "billed_unit_price": bill_line.billed_price,
                },
            )
            result.calculate_variances()
            result.check_tolerance(self.tolerance_amount, self.tolerance_percent)

            if result.is_within_tolerance and result.total_variance == Decimal("0.00"):
                result.match_status = MATCH_STATUS_MATCHED
            elif result.is_within_tolerance:
                result.match_status = MATCH_STATUS_VARIANCE
                any_variance = True
            else:
                result.match_status = MATCH_STATUS_UNMATCHED
                all_matched = False

            result.save()
            results.append(result)

        # Step 4: Update bill matching status
        if all_matched and not any_variance:
            bill.matching_status = MATCHING_STATUS_MATCHED
            bill.is_matched = True
        elif all_matched:
            bill.matching_status = MATCHING_STATUS_VARIANCE_WITHIN
            bill.is_matched = True
        else:
            bill.matching_status = MATCHING_STATUS_VARIANCE_EXCEEDS
            bill.is_matched = False

        # Calculate overall variance
        total_variance = sum(r.total_variance for r in results)
        bill.matching_variance = total_variance
        if bill.purchase_order and bill.purchase_order.total_amount > 0:
            bill.matching_variance_percentage = self.calculate_variance_percentage(
                total_variance, bill.purchase_order.total_amount
            )

        bill.matched_at = timezone.now()
        bill.save(update_fields=[
            "matching_status", "is_matched", "matching_variance",
            "matching_variance_percentage", "matched_at",
        ])

        return {
            "bill": bill.bill_number,
            "matching_status": bill.matching_status,
            "total_variance": float(total_variance),
            "results": [r.get_variance_summary() for r in results],
            "po_match": po_result,
            "grn_match": grn_result,
        }

    def get_3way_match_report(self, bill):
        """Get a detailed 3-way match report for a bill."""
        results = MatchingResult.objects.filter(vendor_bill=bill).select_related(
            "bill_line", "po_line", "grn_line"
        )
        return {
            "bill_number": bill.bill_number,
            "vendor": str(bill.vendor),
            "matching_status": bill.matching_status,
            "total_variance": float(bill.matching_variance or 0),
            "line_results": [
                {
                    "line_number": r.bill_line.line_number,
                    "description": r.bill_line.item_description,
                    **r.get_variance_summary(),
                }
                for r in results
            ],
        }
