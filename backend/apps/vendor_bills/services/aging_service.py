"""Bill aging service — aging analysis for vendor bills."""

from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone

from apps.vendor_bills.constants import (
    AGING_1_30,
    AGING_31_60,
    AGING_61_90,
    AGING_CURRENT,
    AGING_OVER_90,
    BILL_STATUS_APPROVED,
    BILL_STATUS_PARTIAL_PAID,
)
from apps.vendor_bills.models.vendor_bill import VendorBill


class BillAgingService:
    """Provides aging analysis for unpaid / partially-paid vendor bills."""

    BUCKET_RANGES = [
        (AGING_CURRENT, 0, 0),
        (AGING_1_30, 1, 30),
        (AGING_31_60, 31, 60),
        (AGING_61_90, 61, 90),
        (AGING_OVER_90, 91, None),
    ]

    @classmethod
    def calculate_aging(cls, vendor_id=None, as_of_date=None):
        """Return aging buckets for outstanding bills.

        Returns a dict with bucket totals and a list of per-bill details.
        """
        if as_of_date is None:
            as_of_date = timezone.now().date()

        qs = VendorBill.objects.filter(
            status__in=[BILL_STATUS_APPROVED, BILL_STATUS_PARTIAL_PAID],
        )
        if vendor_id is not None:
            qs = qs.filter(vendor_id=vendor_id)

        buckets = {label: Decimal("0") for label, *_ in cls.BUCKET_RANGES}
        details = []

        for bill in qs.iterator():
            outstanding = bill.amount_due
            if outstanding <= 0:
                continue
            days = cls._days_overdue(bill, as_of_date)
            bucket = cls.classify_into_bucket(days)
            buckets[bucket] += outstanding
            details.append(
                {
                    "bill_id": str(bill.pk),
                    "bill_number": bill.bill_number,
                    "vendor_id": str(bill.vendor_id),
                    "due_date": bill.due_date.isoformat() if bill.due_date else None,
                    "days_overdue": days,
                    "outstanding": outstanding,
                    "bucket": bucket,
                }
            )

        return {
            "as_of_date": as_of_date.isoformat(),
            "buckets": buckets,
            "total_outstanding": sum(buckets.values()),
            "details": details,
        }

    @classmethod
    def get_vendor_aging(cls, vendor_id, as_of_date=None):
        """Aging for a single vendor."""
        return cls.calculate_aging(vendor_id=vendor_id, as_of_date=as_of_date)

    @classmethod
    def get_overdue_bills(cls, days_overdue=0, vendor_id=None):
        """Return bills that are past due by at least *days_overdue* days."""
        today = timezone.now().date()
        cutoff = today - timezone.timedelta(days=days_overdue)
        qs = VendorBill.objects.filter(
            status__in=[BILL_STATUS_APPROVED, BILL_STATUS_PARTIAL_PAID],
            due_date__lt=cutoff,
        )
        if vendor_id:
            qs = qs.filter(vendor_id=vendor_id)
        return qs.order_by("due_date")

    @classmethod
    def get_aging_summary(cls, vendor_id=None, as_of_date=None):
        """Return only the bucket totals (no per-bill detail)."""
        result = cls.calculate_aging(vendor_id=vendor_id, as_of_date=as_of_date)
        return {
            "as_of_date": result["as_of_date"],
            "buckets": result["buckets"],
            "total_outstanding": result["total_outstanding"],
        }

    @classmethod
    def get_payment_priority_list(cls, limit=50, as_of_date=None):
        """Bills sorted by urgency — most overdue first."""
        if as_of_date is None:
            as_of_date = timezone.now().date()
        qs = VendorBill.objects.filter(
            status__in=[BILL_STATUS_APPROVED, BILL_STATUS_PARTIAL_PAID],
        ).order_by("due_date")[:limit]
        return qs

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    def classify_into_bucket(cls, days_overdue):
        """Map an integer days-overdue value to the right bucket label."""
        if days_overdue <= 0:
            return AGING_CURRENT
        for label, low, high in cls.BUCKET_RANGES:
            if high is None and days_overdue >= low:
                return label
            if high is not None and low <= days_overdue <= high:
                return label
        return AGING_OVER_90

    @classmethod
    def _days_overdue(cls, bill, as_of_date):
        """Calculate how many days past due a bill is."""
        if bill.due_date is None:
            return 0
        delta = as_of_date - bill.due_date
        return max(delta.days, 0)
