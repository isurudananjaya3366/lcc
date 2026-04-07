"""Payment Report Views — summary, breakdown, and reconciliation endpoints."""

import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncMonth
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.constants import PaymentMethod, PaymentStatus
from apps.payments.models import Payment, Refund

logger = logging.getLogger(__name__)


class PaymentReportView(APIView):
    """
    Payment reporting endpoint.

    GET /reports/?report_type=summary       — aggregate totals
    GET /reports/?report_type=daily         — daily breakdown
    GET /reports/?report_type=monthly       — monthly breakdown
    GET /reports/?report_type=reconciliation — expected vs actual
    GET /reports/?report_type=analytics     — method breakdown & analytics
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        report_type = request.query_params.get("report_type", "summary")

        # Date range filters
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        currency = request.query_params.get("currency", "LKR")

        payments = Payment.objects.filter(is_deleted=False)

        if date_from:
            payments = payments.filter(payment_date__gte=date_from)
        if date_to:
            payments = payments.filter(payment_date__lte=date_to)

        handlers = {
            "summary": self._payment_summary,
            "daily": self._daily_report,
            "monthly": self._monthly_report,
            "reconciliation": self._reconciliation_report,
            "analytics": self._payment_analytics,
        }

        handler = handlers.get(report_type)
        if not handler:
            return Response(
                {"detail": f"Invalid report_type '{report_type}'. "
                 f"Valid options: {', '.join(handlers.keys())}"},
                status=400,
            )

        return Response(handler(payments, currency=currency))

    # ── Report Generators ───────────────────────────────────────

    def _payment_summary(self, payments, **kwargs):
        """Aggregate payment totals."""
        currency = kwargs.get("currency", "LKR")
        filtered = payments.filter(currency=currency)

        completed = filtered.filter(status=PaymentStatus.COMPLETED)
        agg = completed.aggregate(
            total_collected=Sum("amount"),
            payment_count=Count("id"),
        )

        refund_agg = Refund.objects.filter(
            original_payment__in=completed,
            status="PROCESSED",
        ).aggregate(total_refunded=Sum("amount"))

        total_collected = agg["total_collected"] or Decimal("0.00")
        total_refunded = refund_agg["total_refunded"] or Decimal("0.00")

        return {
            "report_type": "summary",
            "currency": currency,
            "total_collected": str(total_collected),
            "total_refunded": str(total_refunded),
            "net_collected": str(total_collected - total_refunded),
            "payment_count": agg["payment_count"] or 0,
            "pending_count": filtered.filter(status=PaymentStatus.PENDING).count(),
            "failed_count": filtered.filter(status=PaymentStatus.FAILED).count(),
            "cancelled_count": filtered.filter(status=PaymentStatus.CANCELLED).count(),
        }

    def _daily_report(self, payments, **kwargs):
        """Per-day payment breakdown."""
        currency = kwargs.get("currency", "LKR")
        filtered = payments.filter(
            currency=currency, status=PaymentStatus.COMPLETED
        )

        daily = (
            filtered.annotate(day=TruncDate("payment_date"))
            .values("day")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-day")[:30]
        )

        return {
            "report_type": "daily",
            "currency": currency,
            "data": [
                {
                    "date": str(row["day"]),
                    "total": str(row["total"]),
                    "count": row["count"],
                }
                for row in daily
            ],
        }

    def _monthly_report(self, payments, **kwargs):
        """Per-month payment breakdown."""
        currency = kwargs.get("currency", "LKR")
        filtered = payments.filter(
            currency=currency, status=PaymentStatus.COMPLETED
        )

        monthly = (
            filtered.annotate(month=TruncMonth("payment_date"))
            .values("month")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-month")[:12]
        )

        return {
            "report_type": "monthly",
            "currency": currency,
            "data": [
                {
                    "month": str(row["month"].date()) if row["month"] else None,
                    "total": str(row["total"]),
                    "count": row["count"],
                }
                for row in monthly
            ],
        }

    def _reconciliation_report(self, payments, **kwargs):
        """Expected vs actual payment reconciliation."""
        currency = kwargs.get("currency", "LKR")
        filtered = payments.filter(currency=currency)

        completed_agg = filtered.filter(
            status=PaymentStatus.COMPLETED
        ).aggregate(total=Sum("amount"), count=Count("id"))

        pending_agg = filtered.filter(
            status=PaymentStatus.PENDING
        ).aggregate(total=Sum("amount"), count=Count("id"))

        failed_agg = filtered.filter(
            status=PaymentStatus.FAILED
        ).aggregate(total=Sum("amount"), count=Count("id"))

        refund_agg = Refund.objects.filter(
            original_payment__in=filtered.filter(status=PaymentStatus.COMPLETED),
            status="PROCESSED",
        ).aggregate(total=Sum("amount"))

        actual = completed_agg["total"] or Decimal("0.00")
        outstanding = pending_agg["total"] or Decimal("0.00")
        failed = failed_agg["total"] or Decimal("0.00")
        refunded = refund_agg["total"] or Decimal("0.00")

        return {
            "report_type": "reconciliation",
            "currency": currency,
            "actual_collected": str(actual),
            "outstanding": str(outstanding),
            "failed": str(failed),
            "refunded": str(refunded),
            "net_collected": str(actual - refunded),
            "expected_total": str(actual + outstanding),
            "completed_count": completed_agg["count"] or 0,
            "pending_count": pending_agg["count"] or 0,
            "failed_count": failed_agg["count"] or 0,
        }

    def _payment_analytics(self, payments, **kwargs):
        """Method breakdown and analytics."""
        currency = kwargs.get("currency", "LKR")
        completed = payments.filter(
            currency=currency, status=PaymentStatus.COMPLETED
        )

        by_method = (
            completed.values("method")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )

        total_amount = completed.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        return {
            "report_type": "analytics",
            "currency": currency,
            "total_amount": str(total_amount),
            "by_method": [
                {
                    "method": row["method"],
                    "method_display": dict(PaymentMethod.choices).get(
                        row["method"], row["method"]
                    ),
                    "total": str(row["total"]),
                    "count": row["count"],
                    "percentage": str(
                        round((row["total"] / total_amount * 100), 2)
                    ) if total_amount else "0.00",
                }
                for row in by_method
            ],
        }
