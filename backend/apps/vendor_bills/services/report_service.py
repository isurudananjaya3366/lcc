"""Payment history & reporting services for vendor bills."""

from collections import defaultdict
from decimal import Decimal

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from apps.vendor_bills.constants import (
    BILL_STATUS_APPROVED,
    BILL_STATUS_PAID,
    BILL_STATUS_PARTIAL_PAID,
    VENDOR_PAYMENT_STATUS_COMPLETED,
)
from apps.vendor_bills.models.vendor_bill import VendorBill
from apps.vendor_bills.models.vendor_payment import VendorPayment


class PaymentHistoryService:
    """Query and aggregate payment history."""

    @classmethod
    def get_payment_history(
        cls,
        vendor_id=None,
        start_date=None,
        end_date=None,
        payment_method=None,
        status=None,
    ):
        """Return filtered payment records."""
        qs = VendorPayment.objects.select_related("vendor", "vendor_bill")
        if vendor_id:
            qs = qs.filter(vendor_id=vendor_id)
        if start_date:
            qs = qs.filter(payment_date__gte=start_date)
        if end_date:
            qs = qs.filter(payment_date__lte=end_date)
        if payment_method:
            qs = qs.filter(payment_method=payment_method)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-payment_date")

    @classmethod
    def get_payment_summary(cls, vendor_id=None, start_date=None, end_date=None):
        """Aggregate payment stats."""
        qs = VendorPayment.objects.filter(status=VENDOR_PAYMENT_STATUS_COMPLETED)
        if vendor_id:
            qs = qs.filter(vendor_id=vendor_id)
        if start_date:
            qs = qs.filter(payment_date__gte=start_date)
        if end_date:
            qs = qs.filter(payment_date__lte=end_date)
        agg = qs.aggregate(
            total_paid=Sum("amount"),
            payment_count=Count("id"),
            average_payment=Avg("amount"),
        )
        return {
            "total_paid": agg["total_paid"] or Decimal("0"),
            "payment_count": agg["payment_count"] or 0,
            "average_payment": agg["average_payment"] or Decimal("0"),
        }


class ReportService:
    """Accounts-payable summary and dashboard widget data."""

    @classmethod
    def accounts_payable_summary(cls):
        """High-level AP snapshot."""
        outstanding_qs = VendorBill.objects.filter(
            status__in=[BILL_STATUS_APPROVED, BILL_STATUS_PARTIAL_PAID],
        )
        total_outstanding = (
            outstanding_qs.aggregate(
                s=Sum("total") - Sum("amount_paid")
            )["s"]
            or Decimal("0")
        )
        total_overdue = Decimal("0")
        today = timezone.now().date()
        for b in outstanding_qs.filter(due_date__lt=today).iterator():
            total_overdue += b.amount_due

        paid_this_month = (
            VendorPayment.objects.filter(
                status=VENDOR_PAYMENT_STATUS_COMPLETED,
                payment_date__year=today.year,
                payment_date__month=today.month,
            ).aggregate(s=Sum("amount"))["s"]
            or Decimal("0")
        )

        return {
            "total_outstanding": total_outstanding,
            "total_overdue": total_overdue,
            "bills_pending": outstanding_qs.count(),
            "paid_this_month": paid_this_month,
        }

    @classmethod
    def dashboard_widgets(cls):
        """Data for dashboard cards."""
        today = timezone.now().date()
        bills_due_soon = VendorBill.objects.filter(
            status__in=[BILL_STATUS_APPROVED, BILL_STATUS_PARTIAL_PAID],
            due_date__gte=today,
            due_date__lte=today + timezone.timedelta(days=7),
        ).count()

        overdue_count = VendorBill.objects.filter(
            status__in=[BILL_STATUS_APPROVED, BILL_STATUS_PARTIAL_PAID],
            due_date__lt=today,
        ).count()

        recent_payments = (
            VendorPayment.objects.filter(
                status=VENDOR_PAYMENT_STATUS_COMPLETED,
            )
            .order_by("-payment_date")[:5]
            .values("id", "payment_number", "amount", "payment_date", "vendor_id")
        )

        return {
            "bills_due_soon": bills_due_soon,
            "overdue_count": overdue_count,
            "recent_payments": list(recent_payments),
        }
