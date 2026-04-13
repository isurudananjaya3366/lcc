"""Dashboard ViewSet — KPI retrieval, layout management, and alerts."""

import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.dashboard.calculators import (
    FinancialKPICalculator,
    HRKPICalculator,
    InventoryKPICalculator,
    SalesKPICalculator,
)
from apps.dashboard.models import DashboardLayout, KPIAlert
from apps.dashboard.serializers import DashboardLayoutSerializer, KPIAlertSerializer
from apps.dashboard.services.cache_service import get_cached_kpi, set_cached_kpi

logger = logging.getLogger(__name__)


class DashboardViewSet(viewsets.ViewSet):
    """Dashboard API providing KPI data, alerts, and layout management.

    Endpoints:
        GET /dashboard/sales/      — Sales KPIs
        GET /dashboard/inventory/  — Inventory KPIs
        GET /dashboard/financial/  — Financial KPIs
        GET /dashboard/hr/         — HR KPIs
        GET /dashboard/all/        — All KPIs combined
        GET /dashboard/alerts/     — Active alerts
        GET /dashboard/layout/     — Get user layout
        PUT /dashboard/layout/     — Save user layout
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Dashboard overview — redirects to all KPIs."""
        return self.all_kpis(request)

    # ── KPI Category Endpoints ───────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="sales")
    def sales(self, request):
        """Retrieve sales KPIs."""
        period = request.query_params.get("period", "month")
        refresh = request.query_params.get("refresh", "false").lower() == "true"

        if not refresh:
            cached = get_cached_kpi("dashboard:sales", period)
            if cached is not None:
                return Response(cached)

        calc = SalesKPICalculator()
        codes = [
            "todays_sales", "weekly_sales", "monthly_sales",
            "sales_growth", "average_order_value", "orders_count",
            "top_selling_products", "top_customers",
            "sales_by_category", "sales_by_channel",
            "sales_trend", "comparison_data",
        ]
        data = {}
        for code in codes:
            try:
                data[code] = calc.calculate(code, period)
            except Exception:
                logger.exception("Error calculating sales KPI %s", code)
                data[code] = {"error": f"Failed to calculate {code}"}

        set_cached_kpi("dashboard:sales", period, data)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="inventory")
    def inventory(self, request):
        """Retrieve inventory KPIs."""
        period = request.query_params.get("period", "month")
        refresh = request.query_params.get("refresh", "false").lower() == "true"

        if not refresh:
            cached = get_cached_kpi("dashboard:inventory", period)
            if cached is not None:
                return Response(cached)

        calc = InventoryKPICalculator()
        codes = [
            "stock_value", "low_stock_items", "out_of_stock",
            "overstock_items", "inventory_turnover", "days_of_inventory",
            "fast_moving_products", "slow_moving_products", "dead_stock",
            "stock_by_category", "stock_by_warehouse", "reorder_alerts",
        ]
        data = {}
        for code in codes:
            try:
                data[code] = calc.calculate(code, period)
            except Exception:
                logger.exception("Error calculating inventory KPI %s", code)
                data[code] = {"error": f"Failed to calculate {code}"}

        set_cached_kpi("dashboard:inventory", period, data)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="financial")
    def financial(self, request):
        """Retrieve financial KPIs."""
        period = request.query_params.get("period", "month")
        refresh = request.query_params.get("refresh", "false").lower() == "true"

        if not refresh:
            cached = get_cached_kpi("dashboard:financial", period)
            if cached is not None:
                return Response(cached)

        calc = FinancialKPICalculator()
        codes = [
            "revenue", "expenses", "net_income",
            "gross_profit_margin", "net_profit_margin",
            "cash_position", "accounts_receivable", "ar_aging",
            "accounts_payable", "ap_aging",
            "current_ratio", "quick_ratio", "revenue_trend",
        ]
        data = {}
        for code in codes:
            try:
                data[code] = calc.calculate(code, period)
            except Exception:
                logger.exception("Error calculating financial KPI %s", code)
                data[code] = {"error": f"Failed to calculate {code}"}

        set_cached_kpi("dashboard:financial", period, data)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="hr")
    def hr(self, request):
        """Retrieve HR KPIs."""
        period = request.query_params.get("period", "month")
        refresh = request.query_params.get("refresh", "false").lower() == "true"

        if not refresh:
            cached = get_cached_kpi("dashboard:hr", period)
            if cached is not None:
                return Response(cached)

        calc = HRKPICalculator()
        codes = [
            "total_employees", "new_hires", "turnover_rate",
            "attendance_rate", "leave_balance_summary",
            "pending_leave_requests", "payroll_cost",
            "department_headcount", "employee_gender_ratio",
            "overtime_summary",
        ]
        data = {}
        for code in codes:
            try:
                data[code] = calc.calculate(code, period)
            except Exception:
                logger.exception("Error calculating HR KPI %s", code)
                data[code] = {"error": f"Failed to calculate {code}"}

        set_cached_kpi("dashboard:hr", period, data)
        return Response(data)

    # ── Combined Endpoint ────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="all")
    def all_kpis(self, request):
        """Retrieve all KPIs across categories in a single response."""
        period = request.query_params.get("period", "month")
        refresh = request.query_params.get("refresh", "false").lower() == "true"

        if not refresh:
            cached = get_cached_kpi("dashboard:all", period)
            if cached is not None:
                return Response(cached)

        data = {}

        # Sales
        try:
            calc = SalesKPICalculator()
            data["sales"] = {
                code: calc.calculate(code, period)
                for code in ["todays_sales", "monthly_sales", "average_order_value", "orders_count"]
            }
        except Exception:
            logger.exception("Error calculating sales KPIs")
            data["sales"] = {"error": "Failed to load sales KPIs"}

        # Inventory
        try:
            calc = InventoryKPICalculator()
            data["inventory"] = {
                code: calc.calculate(code, period)
                for code in ["stock_value", "low_stock_items", "out_of_stock"]
            }
        except Exception:
            logger.exception("Error calculating inventory KPIs")
            data["inventory"] = {"error": "Failed to load inventory KPIs"}

        # Financial
        try:
            calc = FinancialKPICalculator()
            data["financial"] = {
                code: calc.calculate(code, period)
                for code in ["revenue", "expenses", "net_income"]
            }
        except Exception:
            logger.exception("Error calculating financial KPIs")
            data["financial"] = {"error": "Failed to load financial KPIs"}

        # HR
        try:
            calc = HRKPICalculator()
            data["hr"] = {
                code: calc.calculate(code, period)
                for code in ["total_employees", "attendance_rate", "pending_leave_requests"]
            }
        except Exception:
            logger.exception("Error calculating HR KPIs")
            data["hr"] = {"error": "Failed to load HR KPIs"}

        # Active alerts
        alerts = KPIAlert.objects.filter(is_active=True).select_related("kpi")
        data["alerts"] = KPIAlertSerializer(alerts, many=True).data

        set_cached_kpi("dashboard:all", period, data)
        return Response(data)

    # ── Alerts ───────────────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="alerts")
    def alerts(self, request):
        """Retrieve active KPI alerts."""
        alerts = KPIAlert.objects.filter(is_active=True).select_related("kpi")
        serializer = KPIAlertSerializer(alerts, many=True)
        return Response(serializer.data)

    # ── Layout Management ────────────────────────────────────────────

    @action(detail=False, methods=["get", "put"], url_path="layout")
    def layout(self, request):
        """Get or save user's dashboard layout."""
        if request.method == "GET":
            return self._get_layout(request)
        return self._save_layout(request)

    def _get_layout(self, request):
        """Retrieve user's layout or return default."""
        reset = request.query_params.get("reset", "false").lower() == "true"

        if reset:
            DashboardLayout.objects.filter(
                user=request.user, is_default=True
            ).delete()

        layout = (
            DashboardLayout.objects.filter(user=request.user, is_default=True)
            .first()
        )
        if layout:
            return Response(DashboardLayoutSerializer(layout).data)

        return Response(
            {
                "name": "Default Dashboard",
                "widgets": {"widgets": []},
                "is_default": True,
            }
        )

    def _save_layout(self, request):
        """Save or update user's default layout."""
        serializer = DashboardLayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        layout, created = DashboardLayout.objects.update_or_create(
            user=request.user,
            is_default=True,
            defaults={
                "name": serializer.validated_data.get("name", "Default Dashboard"),
                "widgets": serializer.validated_data.get("widgets", {"widgets": []}),
            },
        )

        return Response(
            DashboardLayoutSerializer(layout).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
