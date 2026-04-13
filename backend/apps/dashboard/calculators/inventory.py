"""Inventory KPI calculator — computes inventory-related KPI metrics."""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, F, Q, Sum
from django.utils import timezone

from apps.dashboard.calculators.base import BaseKPICalculator
from apps.dashboard.services.cache_service import get_cached_kpi, set_cached_kpi


class InventoryKPICalculator(BaseKPICalculator):
    """Calculates inventory KPIs from stock and product data."""

    CACHE_NAME = "inventory"

    def _get_stock_queryset(self):
        """Get active stock records with product info."""
        from apps.inventory.models import Stock

        return Stock.objects.filter(
            product__is_active=True,
        ).select_related("product", "location")

    def calculate_stock_value(self, period=None, filters=None):
        """Calculate total inventory value (quantity * cost_price)."""
        total = (
            self._get_stock_queryset()
            .filter(quantity__gt=0)
            .aggregate(
                total_value=Sum(F("quantity") * F("product__cost_price"))
            )["total_value"]
            or Decimal("0")
        )

        return self.format_result(
            value=total,
            label="Stock Value",
            format_type="currency",
        )

    def calculate_low_stock_items(self, period=None, filters=None):
        """Count items below reorder threshold."""
        qs = self._get_stock_queryset().filter(
            quantity__gt=0,
            reorder_level__gt=0,
            quantity__lt=F("reorder_level"),
        )
        count = qs.count()

        items = list(
            qs.values(
                "product__name",
                "product__sku",
                "quantity",
                "reorder_level",
                "location__name",
            )[:10]
        )

        return self.format_result(
            value=count,
            label="Low Stock Items",
            format_type="count",
            items=items,
        )

    def calculate_out_of_stock(self, period=None, filters=None):
        """Count items with zero stock."""
        count = self._get_stock_queryset().filter(quantity__lte=0).count()

        return self.format_result(
            value=count,
            label="Out of Stock",
            format_type="count",
        )

    def calculate_overstock_items(self, period=None, filters=None):
        """Count overstocked items (quantity > 3x reorder level)."""
        qs = self._get_stock_queryset().filter(
            reorder_level__gt=0,
            quantity__gt=F("reorder_level") * 3,
        )
        count = qs.count()

        return self.format_result(
            value=count,
            label="Overstock Items",
            format_type="count",
        )

    def calculate_inventory_turnover(self, period=None, filters=None):
        """Calculate inventory turnover ratio (COGS / Avg Inventory Value)."""
        from apps.orders.models import OrderLineItem

        # Use past 365 days for turnover calculation
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)

        cogs = (
            OrderLineItem.objects.filter(
                order__is_draft=False,
                order__is_deleted=False,
                order__order_date__date__gte=start_date,
                order__order_date__date__lte=end_date,
            )
            .exclude(order__status__in=["cancelled", "returned"])
            .aggregate(
                total_cogs=Sum(F("quantity_ordered") * F("unit_price"))
            )["total_cogs"]
            or Decimal("0")
        )

        avg_inventory = (
            self._get_stock_queryset()
            .filter(quantity__gt=0)
            .aggregate(
                total=Sum(F("quantity") * F("product__cost_price"))
            )["total"]
            or Decimal("1")
        )

        turnover = cogs / avg_inventory if avg_inventory else Decimal("0")

        return self.format_result(
            value=round(turnover, 2),
            label="Inventory Turnover",
            format_type="decimal",
        )

    def calculate_days_of_inventory(self, period=None, filters=None):
        """Calculate average days of inventory on hand."""
        turnover_result = self.calculate_inventory_turnover(period, filters)
        turnover = Decimal(str(turnover_result["value"]))

        if turnover > 0:
            days = round(Decimal("365") / turnover, 1)
        else:
            days = Decimal("0")

        return self.format_result(
            value=days,
            label="Days of Inventory",
            format_type="number",
        )

    def calculate_fast_moving_products(self, period=None, filters=None):
        """Get top 5 products by sales velocity."""
        from apps.inventory.models import StockMovement

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        fast_movers = (
            StockMovement.objects.filter(
                movement_type="out",
                movement_date__date__gte=start_date,
                movement_date__date__lte=end_date,
                product__is_active=True,
            )
            .values("product__name", "product__sku")
            .annotate(total_moved=Sum("quantity"))
            .order_by("-total_moved")[:5]
        )

        items = [
            {
                "name": p["product__name"],
                "sku": p["product__sku"],
                "units_moved": p["total_moved"] or Decimal("0"),
            }
            for p in fast_movers
        ]

        return self.format_result(
            value=items,
            label="Fast Moving Products",
            format_type="number",
        )

    def calculate_slow_moving_products(self, period=None, filters=None):
        """Get bottom 5 products by velocity."""
        from apps.inventory.models import StockMovement

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=90)

        # Get products with stock but minimal movement
        slow_movers = (
            StockMovement.objects.filter(
                movement_type="out",
                movement_date__date__gte=start_date,
                movement_date__date__lte=end_date,
                product__is_active=True,
            )
            .values("product__name", "product__sku")
            .annotate(total_moved=Sum("quantity"))
            .order_by("total_moved")[:5]
        )

        items = [
            {
                "name": p["product__name"],
                "sku": p["product__sku"],
                "units_moved": p["total_moved"] or Decimal("0"),
            }
            for p in slow_movers
        ]

        return self.format_result(
            value=items,
            label="Slow Moving Products",
            format_type="number",
        )

    def calculate_dead_stock(self, period=None, filters=None):
        """Count items with no sales in 90 days."""
        from apps.inventory.models import Stock, StockMovement

        end_date = timezone.now().date()
        cutoff_date = end_date - timedelta(days=90)

        # Products that had outbound movement in last 90 days
        active_product_ids = (
            StockMovement.objects.filter(
                movement_type="out",
                movement_date__date__gte=cutoff_date,
            )
            .values_list("product_id", flat=True)
            .distinct()
        )

        # Products with stock but no recent movement
        dead_stock = (
            Stock.objects.filter(
                quantity__gt=0,
                product__is_active=True,
            )
            .exclude(product_id__in=active_product_ids)
        )
        count = dead_stock.values("product_id").distinct().count()

        dead_value = dead_stock.aggregate(
            total=Sum(F("quantity") * F("product__cost_price"))
        )["total"] or Decimal("0")

        return self.format_result(
            value=count,
            label="Dead Stock",
            format_type="count",
            dead_stock_value=dead_value,
        )

    def calculate_stock_by_category(self, period=None, filters=None):
        """Calculate stock value breakdown by product category."""
        by_category = (
            self._get_stock_queryset()
            .filter(quantity__gt=0)
            .values("product__category__name")
            .annotate(
                total_value=Sum(F("quantity") * F("product__cost_price")),
                item_count=Count("product", distinct=True),
            )
            .order_by("-total_value")
        )

        items = [
            {
                "category": c["product__category__name"] or "Uncategorized",
                "value": c["total_value"] or Decimal("0"),
                "item_count": c["item_count"],
            }
            for c in by_category
        ]

        return self.format_result(
            value=items,
            label="Stock by Category",
            format_type="number",
        )

    def calculate_stock_by_warehouse(self, period=None, filters=None):
        """Calculate stock value by warehouse location."""
        by_warehouse = (
            self._get_stock_queryset()
            .filter(quantity__gt=0)
            .values("location__name")
            .annotate(
                total_value=Sum(F("quantity") * F("product__cost_price")),
                item_count=Count("product", distinct=True),
            )
            .order_by("-total_value")
        )

        items = [
            {
                "warehouse": w["location__name"],
                "value": w["total_value"] or Decimal("0"),
                "item_count": w["item_count"],
            }
            for w in by_warehouse
        ]

        return self.format_result(
            value=items,
            label="Stock by Warehouse",
            format_type="number",
        )

    def calculate_reorder_alerts(self, period=None, filters=None):
        """Get items needing reorder, sorted by urgency."""
        alerts = (
            self._get_stock_queryset()
            .filter(
                reorder_level__gt=0,
                quantity__lt=F("reorder_level"),
            )
            .annotate(
                deficit=F("reorder_level") - F("quantity"),
            )
            .values(
                "product__name",
                "product__sku",
                "quantity",
                "reorder_level",
                "deficit",
                "location__name",
            )
            .order_by("-deficit")[:20]
        )

        items = list(alerts)
        return self.format_result(
            value=items,
            label="Reorder Alerts",
            format_type="number",
        )

    def calculate(self, kpi_code: str, period: str = "month") -> dict:
        """Route to the appropriate inventory KPI calculation."""
        methods = {
            "stock_value": self.calculate_stock_value,
            "low_stock_items": self.calculate_low_stock_items,
            "out_of_stock": self.calculate_out_of_stock,
            "overstock_items": self.calculate_overstock_items,
            "inventory_turnover": self.calculate_inventory_turnover,
            "days_of_inventory": self.calculate_days_of_inventory,
            "fast_moving_products": self.calculate_fast_moving_products,
            "slow_moving_products": self.calculate_slow_moving_products,
            "dead_stock": self.calculate_dead_stock,
            "stock_by_category": self.calculate_stock_by_category,
            "stock_by_warehouse": self.calculate_stock_by_warehouse,
            "reorder_alerts": self.calculate_reorder_alerts,
        }
        method = methods.get(kpi_code)
        if method is None:
            return {"error": f"Unknown inventory KPI: {kpi_code}"}
        return method(period)
