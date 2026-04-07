"""
Purchase history service.

Aggregates order, invoice, and payment data to provide purchase
summaries, top-product analysis, and customer statistics.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, F, Max, Min, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


class PurchaseHistoryService:
    """
    Service for aggregating and analysing customer purchase data.
    """

    # ── Purchase Summary (Task 59) ──────────────────────────────────

    @classmethod
    def get_purchase_summary(cls, customer_id: str) -> dict[str, Any]:
        """
        Return a summary of the customer's purchase history.

        Keys: total_orders, total_spent, average_order_value,
        total_items_purchased, first_purchase_date, last_purchase_date.
        """
        from apps.orders.models import Order

        orders = Order.objects.filter(customer_id=customer_id)

        agg = orders.aggregate(
            total_orders=Count("id"),
            total_spent=Sum("total_amount"),
            avg_order=Avg("total_amount"),
            first_purchase=Min("created_on"),
            last_purchase=Max("created_on"),
        )

        total_items = (
            orders.aggregate(
                total=Sum("line_items__quantity_ordered"),
            )["total"]
            or 0
        )

        return {
            "total_orders": agg["total_orders"] or 0,
            "total_spent": agg["total_spent"] or Decimal("0.00"),
            "average_order_value": agg["avg_order"] or Decimal("0.00"),
            "total_items_purchased": total_items,
            "first_purchase_date": (
                agg["first_purchase"].date() if agg["first_purchase"] else None
            ),
            "last_purchase_date": (
                agg["last_purchase"].date() if agg["last_purchase"] else None
            ),
        }

    # ── Top Products (Task 60) ──────────────────────────────────────

    @classmethod
    def get_top_products(
        cls,
        customer_id: str,
        *,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Return the top *limit* products purchased by this customer,
        ordered by total quantity.
        """
        from apps.orders.models import OrderLineItem

        items = (
            OrderLineItem.objects.filter(
                order__customer_id=customer_id,
                product__isnull=False,
            )
            .values(
                product_id=F("product__id"),
                product_name=F("product__name"),
            )
            .annotate(
                quantity=Sum("quantity_ordered"),
                total_spent=Sum(
                    F("quantity_ordered") * F("unit_price"),
                ),
            )
            .order_by("-quantity")[:limit]
        )

        return list(items)

    # ── Last Purchase (Task 61) ─────────────────────────────────────

    @classmethod
    def get_last_purchase(cls, customer_id: str) -> dict[str, Any] | None:
        """
        Return details of the most recent order for a customer.
        """
        from apps.orders.models import Order

        order = (
            Order.objects.filter(customer_id=customer_id)
            .select_related("customer")
            .prefetch_related("line_items", "payments")
            .order_by("-created_on")
            .first()
        )

        if not order:
            return None

        return {
            "order_id": str(order.pk),
            "order_number": order.order_number,
            "date": order.created_on,
            "total_amount": order.total_amount,
            "status": order.status,
            "items": [
                {
                    "product_name": getattr(item.product, "name", "N/A"),
                    "quantity": item.quantity_ordered,
                    "unit_price": item.unit_price,
                }
                for item in order.line_items.all()
            ],
            "payments": [
                {
                    "amount": p.amount,
                    "method": p.method,
                    "status": p.status,
                }
                for p in order.payments.all()
            ],
        }

    # ── Customer Statistics (Task 62) ───────────────────────────────

    @classmethod
    def get_customer_statistics(cls, customer_id: str) -> dict[str, Any]:
        """
        Comprehensive customer statistics including RFM metrics.
        """
        from apps.customers.models import Customer

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return {}

        now = timezone.now().date()

        days_since_last_purchase = None
        if customer.last_purchase_date:
            days_since_last_purchase = (now - customer.last_purchase_date).days

        purchase_frequency_days = None
        if (
            customer.order_count
            and customer.order_count > 1
            and customer.first_purchase_date
            and customer.last_purchase_date
        ):
            span = (customer.last_purchase_date - customer.first_purchase_date).days
            purchase_frequency_days = round(span / (customer.order_count - 1))

        return {
            "lifetime_value": customer.total_purchases,
            "average_order_value": customer.average_order_value,
            "purchase_frequency_days": purchase_frequency_days,
            "days_since_last_purchase": days_since_last_purchase,
            "total_orders": customer.order_count,
            "outstanding_balance": customer.outstanding_balance,
        }
