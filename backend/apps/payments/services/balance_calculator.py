"""
Balance calculator service.

Provides invoice balance calculation, customer balance summaries,
and aging analysis for accounts receivable.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

from apps.payments.constants import PaymentStatus

logger = logging.getLogger(__name__)


class BalanceCalculator:
    """
    Utility class for calculating payment balances and aging.
    """

    @staticmethod
    def calculate_invoice_balance(invoice):
        """
        Calculate outstanding balance for an invoice from completed payments.

        Returns:
            dict: {total, paid, outstanding, payment_count}
        """
        from apps.payments.models import PaymentAllocation

        total = getattr(invoice, "total_amount", Decimal("0"))
        if total is None:
            total = Decimal("0")

        allocations = PaymentAllocation.objects.filter(
            invoice=invoice,
            payment__status=PaymentStatus.COMPLETED,
        )
        paid = allocations.aggregate(
            total=models.Sum("amount"),
        )["total"] or Decimal("0")

        return {
            "total": Decimal(str(total)),
            "paid": paid,
            "outstanding": Decimal(str(total)) - paid,
            "payment_count": allocations.values("payment").distinct().count(),
        }

    @staticmethod
    def calculate_customer_balance(customer):
        """
        Calculate total outstanding balance for a customer across invoices.

        Returns:
            dict: {total_invoiced, total_paid, total_outstanding, invoice_count}
        """
        from apps.payments.models import PaymentAllocation

        # Get all invoices for the customer
        invoices = customer.invoices.all() if hasattr(customer, "invoices") else []

        total_invoiced = Decimal("0")
        total_paid = Decimal("0")
        invoice_count = 0

        for invoice in invoices:
            balance = BalanceCalculator.calculate_invoice_balance(invoice)
            total_invoiced += balance["total"]
            total_paid += balance["paid"]
            invoice_count += 1

        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "total_outstanding": total_invoiced - total_paid,
            "invoice_count": invoice_count,
        }

    @staticmethod
    def calculate_aging_balance(invoices):
        """
        Calculate aging buckets for a set of invoices.

        Buckets: Current (not due), 1-30, 31-60, 61-90, 90+ days.

        Args:
            invoices: QuerySet of invoices with due_date and total_amount.

        Returns:
            dict: {current, days_1_30, days_31_60, days_61_90, days_90_plus, total}
        """
        today = timezone.now().date()
        buckets = {
            "current": Decimal("0"),
            "days_1_30": Decimal("0"),
            "days_31_60": Decimal("0"),
            "days_61_90": Decimal("0"),
            "days_90_plus": Decimal("0"),
        }

        for invoice in invoices:
            balance = BalanceCalculator.calculate_invoice_balance(invoice)
            outstanding = balance["outstanding"]
            if outstanding <= 0:
                continue

            due_date = getattr(invoice, "due_date", None)
            if not due_date:
                buckets["current"] += outstanding
                continue

            days_past = (today - due_date).days

            if days_past <= 0:
                buckets["current"] += outstanding
            elif days_past <= 30:
                buckets["days_1_30"] += outstanding
            elif days_past <= 60:
                buckets["days_31_60"] += outstanding
            elif days_past <= 90:
                buckets["days_61_90"] += outstanding
            else:
                buckets["days_90_plus"] += outstanding

        buckets["total"] = sum(buckets.values())
        return buckets
