"""Sales KPI calculator — computes sales-related KPI metrics."""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import TruncDate

from apps.dashboard.calculators.base import BaseKPICalculator
from apps.dashboard.services.cache_service import get_cached_kpi, set_cached_kpi


class SalesKPICalculator(BaseKPICalculator):
    """Calculates sales KPIs from order data."""

    CACHE_NAME = "sales"

    def _get_base_queryset(self):
        """Get base queryset excluding cancelled/returned/draft/deleted orders."""
        from apps.orders.models import Order

        return Order.objects.filter(
            is_draft=False,
            is_deleted=False,
        ).exclude(
            status__in=["cancelled", "returned"],
        )

    def calculate_todays_sales(self, period, filters=None):
        """Calculate today's total sales revenue."""
        start, end = self.get_date_range(period)
        qs = self._get_base_queryset().filter(
            order_date__date__gte=start,
            order_date__date__lte=end,
        )
        total = qs.aggregate(total=Sum("total_amount"))["total"] or Decimal("0")

        prev_start, prev_end = self.get_previous_date_range(period)
        prev_total = (
            self._get_base_queryset()
            .filter(order_date__date__gte=prev_start, order_date__date__lte=prev_end)
            .aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0")
        )

        change = self.calculate_change(total, prev_total)
        return self.format_result(
            value=total,
            label="Today's Sales",
            format_type="currency",
            **change,
        )

    def calculate_weekly_sales(self, period, filters=None):
        """Calculate this week's total sales."""
        start, end = self.get_date_range("WEEK")
        total = (
            self._get_base_queryset()
            .filter(order_date__date__gte=start, order_date__date__lte=end)
            .aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0")
        )

        prev_start, prev_end = self.get_previous_date_range("WEEK")
        prev_total = (
            self._get_base_queryset()
            .filter(order_date__date__gte=prev_start, order_date__date__lte=prev_end)
            .aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0")
        )

        change = self.calculate_change(total, prev_total)
        return self.format_result(
            value=total,
            label="Weekly Sales",
            format_type="currency",
            **change,
        )

    def calculate_monthly_sales(self, period, filters=None):
        """Calculate this month's total sales."""
        start, end = self.get_date_range("MONTH")
        total = (
            self._get_base_queryset()
            .filter(order_date__date__gte=start, order_date__date__lte=end)
            .aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0")
        )

        prev_start, prev_end = self.get_previous_date_range("MONTH")
        prev_total = (
            self._get_base_queryset()
            .filter(order_date__date__gte=prev_start, order_date__date__lte=prev_end)
            .aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0")
        )

        change = self.calculate_change(total, prev_total)
        return self.format_result(
            value=total,
            label="Monthly Sales",
            format_type="currency",
            **change,
        )

    def calculate_sales_growth(self, period, filters=None):
        """Calculate sales growth percentage vs previous period."""
        start, end = self.get_date_range(period)
        current = (
            self._get_base_queryset()
            .filter(order_date__date__gte=start, order_date__date__lte=end)
            .aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0")
        )

        prev_start, prev_end = self.get_previous_date_range(period)
        previous = (
            self._get_base_queryset()
            .filter(order_date__date__gte=prev_start, order_date__date__lte=prev_end)
            .aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0")
        )

        change = self.calculate_change(current, previous)
        return self.format_result(
            value=change["change_percent"],
            label="Sales Growth",
            format_type="percent",
            current_revenue=current,
            previous_revenue=previous,
            **change,
        )

    def calculate_average_order_value(self, period, filters=None):
        """Calculate average order value for the period."""
        start, end = self.get_date_range(period)
        qs = self._get_base_queryset().filter(
            order_date__date__gte=start,
            order_date__date__lte=end,
        )
        aov = qs.aggregate(avg=Avg("total_amount"))["avg"] or Decimal("0")

        prev_start, prev_end = self.get_previous_date_range(period)
        prev_aov = (
            self._get_base_queryset()
            .filter(order_date__date__gte=prev_start, order_date__date__lte=prev_end)
            .aggregate(avg=Avg("total_amount"))["avg"]
            or Decimal("0")
        )

        change = self.calculate_change(aov, prev_aov)
        return self.format_result(
            value=round(aov, 2),
            label="Average Order Value",
            format_type="currency",
            **change,
        )

    def calculate_orders_count(self, period, filters=None):
        """Calculate total order count for the period."""
        start, end = self.get_date_range(period)
        count = self._get_base_queryset().filter(
            order_date__date__gte=start,
            order_date__date__lte=end,
        ).count()

        prev_start, prev_end = self.get_previous_date_range(period)
        prev_count = self._get_base_queryset().filter(
            order_date__date__gte=prev_start,
            order_date__date__lte=prev_end,
        ).count()

        change = self.calculate_change(Decimal(count), Decimal(prev_count))
        return self.format_result(
            value=count,
            label="Orders Count",
            format_type="count",
            **change,
        )

    def calculate_top_selling_products(self, period, filters=None):
        """Get top 5 selling products by revenue."""
        from apps.orders.models import OrderLineItem

        start, end = self.get_date_range(period)
        top_products = (
            OrderLineItem.objects.filter(
                order__is_draft=False,
                order__is_deleted=False,
                order__order_date__date__gte=start,
                order__order_date__date__lte=end,
            )
            .exclude(order__status__in=["cancelled", "returned"])
            .values("product__name")
            .annotate(
                total_revenue=Sum(F("quantity_ordered") * F("unit_price")),
                total_quantity=Sum("quantity_ordered"),
            )
            .order_by("-total_revenue")[:5]
        )

        items = [
            {
                "name": p["product__name"] or "Unknown",
                "revenue": p["total_revenue"] or Decimal("0"),
                "quantity": p["total_quantity"] or Decimal("0"),
            }
            for p in top_products
        ]

        return self.format_result(
            value=items,
            label="Top Selling Products",
            format_type="number",
        )

    def calculate_top_customers(self, period, filters=None):
        """Get top 5 customers by spend."""
        start, end = self.get_date_range(period)
        top_customers = (
            self._get_base_queryset()
            .filter(
                order_date__date__gte=start,
                order_date__date__lte=end,
                customer__isnull=False,
            )
            .values("customer__display_name", "customer_id")
            .annotate(
                total_spent=Sum("total_amount"),
                order_count=Count("id"),
            )
            .order_by("-total_spent")[:5]
        )

        items = [
            {
                "name": c["customer__display_name"] or "Unknown",
                "total_spent": c["total_spent"] or Decimal("0"),
                "order_count": c["order_count"],
            }
            for c in top_customers
        ]

        return self.format_result(
            value=items,
            label="Top Customers",
            format_type="number",
        )

    def calculate_sales_by_category(self, period, filters=None):
        """Calculate sales breakdown by product category."""
        from apps.orders.models import OrderLineItem

        start, end = self.get_date_range(period)
        by_category = (
            OrderLineItem.objects.filter(
                order__is_draft=False,
                order__is_deleted=False,
                order__order_date__date__gte=start,
                order__order_date__date__lte=end,
            )
            .exclude(order__status__in=["cancelled", "returned"])
            .values("product__category__name")
            .annotate(
                total_revenue=Sum(F("quantity_ordered") * F("unit_price")),
                product_count=Count("product", distinct=True),
            )
            .order_by("-total_revenue")
        )

        items = [
            {
                "category": c["product__category__name"] or "Uncategorized",
                "revenue": c["total_revenue"] or Decimal("0"),
                "product_count": c["product_count"],
            }
            for c in by_category
        ]

        return self.format_result(
            value=items,
            label="Sales by Category",
            format_type="number",
        )

    def calculate_sales_by_channel(self, period, filters=None):
        """Calculate sales breakdown by channel (POS vs Webstore)."""
        start, end = self.get_date_range(period)
        by_channel = (
            self._get_base_queryset()
            .filter(
                order_date__date__gte=start,
                order_date__date__lte=end,
            )
            .values("source")
            .annotate(
                total_revenue=Sum("total_amount"),
                order_count=Count("id"),
            )
            .order_by("-total_revenue")
        )

        items = [
            {
                "channel": c["source"],
                "revenue": c["total_revenue"] or Decimal("0"),
                "order_count": c["order_count"],
            }
            for c in by_channel
        ]

        return self.format_result(
            value=items,
            label="Sales by Channel",
            format_type="number",
        )

    def calculate_sales_trend(self, period, filters=None):
        """Generate daily sales data for trend charts."""
        start, end = self.get_date_range(period)
        daily_sales = (
            self._get_base_queryset()
            .filter(
                order_date__date__gte=start,
                order_date__date__lte=end,
            )
            .annotate(date=TruncDate("order_date"))
            .values("date")
            .annotate(
                revenue=Sum("total_amount"),
                count=Count("id"),
            )
            .order_by("date")
        )

        items = [
            {
                "date": str(d["date"]),
                "revenue": d["revenue"] or Decimal("0"),
                "count": d["count"],
            }
            for d in daily_sales
        ]

        return self.format_result(
            value=items,
            label="Sales Trend",
            format_type="number",
        )

    def calculate_comparison_data(self, period, filters=None):
        """Compare current period to prior period."""
        start, end = self.get_date_range(period)
        prev_start, prev_end = self.get_previous_date_range(period)

        current_data = self._get_base_queryset().filter(
            order_date__date__gte=start, order_date__date__lte=end
        ).aggregate(
            revenue=Sum("total_amount"),
            orders=Count("id"),
            avg_order=Avg("total_amount"),
        )
        previous_data = self._get_base_queryset().filter(
            order_date__date__gte=prev_start, order_date__date__lte=prev_end
        ).aggregate(
            revenue=Sum("total_amount"),
            orders=Count("id"),
            avg_order=Avg("total_amount"),
        )

        current_rev = current_data["revenue"] or Decimal("0")
        previous_rev = previous_data["revenue"] or Decimal("0")

        return self.format_result(
            value={
                "current": {
                    "revenue": current_rev,
                    "orders": current_data["orders"],
                    "avg_order": current_data["avg_order"] or Decimal("0"),
                    "period": f"{start} to {end}",
                },
                "previous": {
                    "revenue": previous_rev,
                    "orders": previous_data["orders"],
                    "avg_order": previous_data["avg_order"] or Decimal("0"),
                    "period": f"{prev_start} to {prev_end}",
                },
                **self.calculate_change(current_rev, previous_rev),
            },
            label="Period Comparison",
            format_type="number",
        )

    def calculate(self, kpi_code: str, period: str = "month") -> dict:
        """Route to the appropriate sales KPI calculation."""
        methods = {
            "todays_sales": self.calculate_todays_sales,
            "weekly_sales": self.calculate_weekly_sales,
            "monthly_sales": self.calculate_monthly_sales,
            "sales_growth": self.calculate_sales_growth,
            "average_order_value": self.calculate_average_order_value,
            "orders_count": self.calculate_orders_count,
            "top_selling_products": self.calculate_top_selling_products,
            "top_customers": self.calculate_top_customers,
            "sales_by_category": self.calculate_sales_by_category,
            "sales_by_channel": self.calculate_sales_by_channel,
            "sales_trend": self.calculate_sales_trend,
            "comparison_data": self.calculate_comparison_data,
        }
        method = methods.get(kpi_code)
        if method is None:
            return {"error": f"Unknown sales KPI: {kpi_code}"}
        return method(period)
