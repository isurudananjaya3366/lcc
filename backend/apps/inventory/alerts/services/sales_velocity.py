"""
Sales velocity service for calculating product demand rates.

Provides daily/weekly velocity calculations, trend detection,
confidence intervals, and seasonality adjustment.
"""

import logging
import math
from datetime import timedelta
from decimal import Decimal
from statistics import mean, stdev

from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncWeek
from django.utils import timezone

logger = logging.getLogger(__name__)


class SalesVelocityService:
    """
    Analyse historical sales to compute product demand velocity.

    Used by ReorderCalculator for reorder-point and EOQ calculations.
    Falls back through multiple strategies when data is sparse.
    """

    # ── Main Entry Point ────────────────────────────────────────

    @staticmethod
    def calculate_velocity(product, days=30, warehouse=None):
        """
        Calculate overall daily sales velocity for a product.

        Returns:
            dict with avg_daily_velocity, total_sold, data_points, source
            or None when no data at all.
        """
        sales_data = SalesVelocityService.get_sales_data(
            product, days=days, warehouse=warehouse,
        )

        if sales_data:
            total_sold = sum(d["quantity"] for d in sales_data)
            avg_daily = Decimal(str(round(float(total_sold) / days, 3)))
            return {
                "avg_daily_velocity": avg_daily,
                "total_sold": total_sold,
                "data_points": len(sales_data),
                "days_analysed": days,
                "source": "order_history",
            }

        # Fallback chain
        return SalesVelocityService.handle_no_sales(product, days)

    # ── Data Retrieval ──────────────────────────────────────────

    @staticmethod
    def get_sales_data(product, days=30, warehouse=None):
        """
        Query completed-order items for the product over *days*.

        Returns list[dict] with keys ``date`` and ``quantity``, ordered
        by date ascending.  Returns an empty list when no orders exist.
        """
        try:
            from apps.orders.models import OrderItem
        except ImportError:
            logger.warning("Orders module not available – returning empty sales data")
            return []

        cutoff = timezone.now() - timedelta(days=days)

        qs = OrderItem.objects.filter(
            product=product,
            order__created_on__gte=cutoff,
        )
        # Restrict to completed / delivered orders if status field exists
        qs = qs.filter(order__status__in=["completed", "delivered"])

        if warehouse:
            qs = qs.filter(order__warehouse=warehouse)

        daily = (
            qs.annotate(date=TruncDate("order__created_on"))
            .values("date")
            .annotate(quantity=Sum("quantity"))
            .order_by("date")
        )
        return list(daily)

    # ── No-Sales Fallback ───────────────────────────────────────

    @staticmethod
    def handle_no_sales(product, days):
        """
        Fallback strategy when *days*-range has no data.

        1. Try a longer period (90 d).
        2. Fall back to category average.
        3. Return zero velocity.
        """
        if days < 90:
            longer_data = SalesVelocityService.get_sales_data(product, days=90)
            if longer_data:
                total = sum(d["quantity"] for d in longer_data)
                avg_daily = Decimal(str(round(float(total) / 90, 3)))
                return {
                    "avg_daily_velocity": avg_daily,
                    "total_sold": total,
                    "data_points": len(longer_data),
                    "days_analysed": 90,
                    "source": "extended_history",
                }

        cat_avg = SalesVelocityService.get_category_average(product)
        if cat_avg:
            return cat_avg

        return {
            "avg_daily_velocity": Decimal("0"),
            "total_sold": Decimal("0"),
            "data_points": 0,
            "days_analysed": days,
            "source": "no_data",
        }

    @staticmethod
    def get_category_average(product):
        """Average daily velocity across sibling products in same category."""
        if not hasattr(product, "category") or product.category is None:
            return None

        try:
            from apps.orders.models import OrderItem
        except ImportError:
            return None

        cutoff = timezone.now() - timedelta(days=30)
        from apps.products.models import Product

        siblings = Product.objects.filter(
            category=product.category, is_active=True,
        ).exclude(id=product.id)

        if not siblings.exists():
            return None

        total = (
            OrderItem.objects.filter(
                product__in=siblings,
                order__created_on__gte=cutoff,
                order__status__in=["completed", "delivered"],
            ).aggregate(total=Sum("quantity"))["total"]
        )

        if not total:
            return None

        sibling_count = siblings.count()
        avg_daily = Decimal(str(round(float(total) / (30 * sibling_count), 3)))
        return {
            "avg_daily_velocity": avg_daily,
            "total_sold": total,
            "data_points": sibling_count,
            "days_analysed": 30,
            "source": "category_average",
        }

    # ── Daily Velocity ──────────────────────────────────────────

    @staticmethod
    def calculate_daily_velocity(product, days=30, warehouse=None):
        """
        Detailed daily velocity with confidence intervals.

        Returns dict with avg, std_dev, confidence_interval, data.
        """
        daily_data = SalesVelocityService.get_sales_data(
            product, days=days, warehouse=warehouse,
        )

        if not daily_data:
            return None

        quantities = [float(d["quantity"]) for d in daily_data]
        avg = mean(quantities)
        sd = stdev(quantities) if len(quantities) > 1 else 0.0

        # Fill zero-days
        actual_days = days
        if len(quantities) < actual_days:
            zero_fill = actual_days - len(quantities)
            quantities.extend([0.0] * zero_fill)
            avg = mean(quantities)
            sd = stdev(quantities) if len(quantities) > 1 else 0.0

        result = {
            "avg_daily": Decimal(str(round(avg, 3))),
            "std_dev": round(sd, 3),
            "data_points": len(daily_data),
            "days_analysed": days,
        }

        if sd > 0 and len(quantities) > 1:
            se = sd / math.sqrt(len(quantities))
            result["confidence_interval"] = {
                "lower": round(avg - 1.96 * se, 3),
                "upper": round(avg + 1.96 * se, 3),
                "std_dev": round(sd, 3),
            }

        return result

    @staticmethod
    def get_daily_breakdown(product, days=30, warehouse=None):
        """Return raw day-by-day sales list."""
        return SalesVelocityService.get_sales_data(
            product, days=days, warehouse=warehouse,
        )

    @staticmethod
    def detect_trend(product, days=30, warehouse=None):
        """
        Detect demand trend using simple linear-regression slope.

        Returns dict with slope, direction ('up', 'down', 'flat').
        """
        daily_data = SalesVelocityService.get_sales_data(
            product, days=days, warehouse=warehouse,
        )
        if not daily_data or len(daily_data) < 3:
            return {"slope": 0.0, "direction": "flat"}

        quantities = [float(d["quantity"]) for d in daily_data]
        n = len(quantities)
        x_vals = list(range(n))
        x_mean = mean(x_vals)
        y_mean = mean(quantities)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, quantities))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)

        slope = numerator / denominator if denominator != 0 else 0.0

        if slope > 0.05:
            direction = "up"
        elif slope < -0.05:
            direction = "down"
        else:
            direction = "flat"

        return {"slope": round(slope, 4), "direction": direction}

    # ── Weekly Velocity ─────────────────────────────────────────

    @staticmethod
    def calculate_weekly_velocity(product, weeks=4, warehouse=None):
        """Aggregate weekly sales velocity."""
        try:
            from apps.orders.models import OrderItem
        except ImportError:
            return None

        cutoff = timezone.now() - timedelta(weeks=weeks)

        qs = OrderItem.objects.filter(
            product=product,
            order__created_on__gte=cutoff,
            order__status__in=["completed", "delivered"],
        )
        if warehouse:
            qs = qs.filter(order__warehouse=warehouse)

        weekly = (
            qs.annotate(week=TruncWeek("order__created_on"))
            .values("week")
            .annotate(quantity=Sum("quantity"))
            .order_by("week")
        )
        weekly_list = list(weekly)
        if not weekly_list:
            return None

        quantities = [float(w["quantity"]) for w in weekly_list]
        avg_weekly = mean(quantities)

        return {
            "avg_weekly": Decimal(str(round(avg_weekly, 3))),
            "weeks_analysed": weeks,
            "data_points": len(weekly_list),
            "weekly_data": weekly_list,
        }

    @staticmethod
    def get_weekly_breakdown(product, weeks=4, warehouse=None):
        """Return raw week-by-week list."""
        result = SalesVelocityService.calculate_weekly_velocity(
            product, weeks=weeks, warehouse=warehouse,
        )
        return result["weekly_data"] if result else []

    @staticmethod
    def week_over_week_growth(product, weeks=4, warehouse=None):
        """Calculate week-over-week growth rates."""
        result = SalesVelocityService.calculate_weekly_velocity(
            product, weeks=weeks, warehouse=warehouse,
        )
        if not result or len(result["weekly_data"]) < 2:
            return []

        data = result["weekly_data"]
        growth_rates = []
        for i in range(1, len(data)):
            prev = float(data[i - 1]["quantity"])
            curr = float(data[i]["quantity"])
            if prev > 0:
                rate = round(((curr - prev) / prev) * 100, 2)
            else:
                rate = 100.0 if curr > 0 else 0.0
            growth_rates.append({"week": data[i]["week"], "growth_pct": rate})
        return growth_rates

    # ── Seasonality ─────────────────────────────────────────────

    @staticmethod
    def detect_seasonality(product):
        """
        Return True if significant monthly demand variation detected.

        Uses coefficient-of-variation on monthly totals for the last year.
        """
        try:
            from apps.orders.models import OrderItem
        except ImportError:
            return False

        from django.db.models.functions import TruncMonth

        cutoff = timezone.now() - timedelta(days=365)
        monthly = (
            OrderItem.objects.filter(
                product=product,
                order__created_on__gte=cutoff,
                order__status__in=["completed", "delivered"],
            )
            .annotate(month=TruncMonth("order__created_on"))
            .values("month")
            .annotate(quantity=Sum("quantity"))
            .order_by("month")
        )
        monthly_list = list(monthly)
        if len(monthly_list) < 4:
            return False

        quantities = [float(m["quantity"]) for m in monthly_list]
        avg = mean(quantities)
        if avg == 0:
            return False
        cv = (stdev(quantities) / avg) if len(quantities) > 1 else 0
        return cv > 0.30  # >30% variation ⇒ seasonal

    @staticmethod
    def get_seasonal_factor(product):
        """
        Return a multiplier for current month vs yearly average.

        Falls back to ``1.0`` when insufficient data.
        """
        try:
            from apps.orders.models import OrderItem
        except ImportError:
            return 1.0

        from django.db.models.functions import TruncMonth

        cutoff = timezone.now() - timedelta(days=365)
        monthly = (
            OrderItem.objects.filter(
                product=product,
                order__created_on__gte=cutoff,
                order__status__in=["completed", "delivered"],
            )
            .annotate(month=TruncMonth("order__created_on"))
            .values("month")
            .annotate(quantity=Sum("quantity"))
            .order_by("month")
        )
        monthly_list = list(monthly)
        if len(monthly_list) < 4:
            return 1.0

        quantities = [float(m["quantity"]) for m in monthly_list]
        yearly_avg = mean(quantities)
        if yearly_avg == 0:
            return 1.0

        current_month = timezone.now().month
        current_qty = next(
            (float(m["quantity"]) for m in monthly_list if m["month"].month == current_month),
            yearly_avg,
        )
        factor = current_qty / yearly_avg
        return round(min(max(factor, 0.5), 2.0), 3)  # clamp 0.5–2.0
