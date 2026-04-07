"""Vendor statement service — generates account statement data."""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Q, Sum
from django.utils import timezone

from apps.vendor_bills.constants import (
    BILL_STATUS_APPROVED,
    BILL_STATUS_PAID,
    BILL_STATUS_PARTIAL_PAID,
    VENDOR_PAYMENT_STATUS_COMPLETED,
)
from apps.vendor_bills.models.vendor_bill import VendorBill
from apps.vendor_bills.models.vendor_payment import VendorPayment


class VendorStatementService:
    """Generate vendor account statements for a given period."""

    @classmethod
    def generate_statement(
        cls,
        vendor,
        start_date=None,
        end_date=None,
    ):
        """Return a dict summarising bills and payments in the period.

        Parameters
        ----------
        vendor : Vendor model instance
        start_date : date | None — defaults to 30 days ago
        end_date   : date | None — defaults to today
        """
        today = timezone.now().date()
        if end_date is None:
            end_date = today
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        opening_balance = cls._get_opening_balance(vendor, start_date)

        bills = cls._get_period_bills(vendor, start_date, end_date)
        payments = cls._get_period_payments(vendor, start_date, end_date)

        total_billed = (
            bills.aggregate(total=Sum("total"))["total"] or Decimal("0")
        )
        total_paid = (
            payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        )
        closing_balance = opening_balance + total_billed - total_paid

        return {
            "vendor_id": str(vendor.pk),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "opening_balance": opening_balance,
            "total_billed": total_billed,
            "total_paid": total_paid,
            "closing_balance": closing_balance,
            "bills": list(
                bills.values(
                    "id",
                    "bill_number",
                    "bill_date",
                    "due_date",
                    "total",
                    "amount_paid",
                    "status",
                )
            ),
            "payments": list(
                payments.values(
                    "id",
                    "payment_number",
                    "payment_date",
                    "amount",
                    "payment_method",
                    "status",
                )
            ),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @classmethod
    def _get_opening_balance(cls, vendor, as_of_date):
        """Outstanding balance for bills created before *as_of_date*."""
        bills_before = VendorBill.objects.filter(
            vendor=vendor,
            bill_date__lt=as_of_date,
            status__in=[
                BILL_STATUS_APPROVED,
                BILL_STATUS_PARTIAL_PAID,
                BILL_STATUS_PAID,
            ],
        )
        total_billed = (
            bills_before.aggregate(t=Sum("total"))["t"] or Decimal("0")
        )
        total_paid = (
            bills_before.aggregate(p=Sum("amount_paid"))["p"] or Decimal("0")
        )
        return total_billed - total_paid

    @classmethod
    def _get_period_bills(cls, vendor, start_date, end_date):
        return VendorBill.objects.filter(
            vendor=vendor,
            bill_date__gte=start_date,
            bill_date__lte=end_date,
        ).exclude(status="cancelled").order_by("bill_date")

    @classmethod
    def _get_period_payments(cls, vendor, start_date, end_date):
        return VendorPayment.objects.filter(
            vendor=vendor,
            payment_date__gte=start_date,
            payment_date__lte=end_date,
            status=VENDOR_PAYMENT_STATUS_COMPLETED,
        ).order_by("payment_date")
