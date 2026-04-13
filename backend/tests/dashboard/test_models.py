"""Tests for dashboard KPI models."""

import pytest

from apps.dashboard.enums import KPICategory, KPIPeriod, WidgetType
from apps.dashboard.models import DashboardLayout, KPIAlert, KPIDefinition


@pytest.mark.django_db
class TestKPIDefinition:
    """Tests for KPIDefinition model."""

    def test_create_kpi_definition(self, tenant_context):
        kpi = KPIDefinition.objects.create(
            name="Test KPI",
            code="TEST_KPI_001",
            description="A test KPI",
            category=KPICategory.SALES,
            default_widget_type=WidgetType.NUMBER,
            format_type="number",
            is_active=True,
            sort_order=1,
        )
        assert kpi.name == "Test KPI"
        assert kpi.code == "TEST_KPI_001"
        assert kpi.category == KPICategory.SALES
        assert kpi.is_active is True

    def test_kpi_code_unique(self, tenant_context):
        KPIDefinition.objects.create(
            name="KPI A",
            code="UNIQUE_CODE",
            category=KPICategory.SALES,
        )
        with pytest.raises(Exception):
            KPIDefinition.objects.create(
                name="KPI B",
                code="UNIQUE_CODE",
                category=KPICategory.INVENTORY,
            )

    def test_kpi_str(self, tenant_context):
        kpi = KPIDefinition.objects.create(
            name="Daily Sales",
            code="DAILY_SALES",
            category=KPICategory.SALES,
        )
        assert "Daily Sales" in str(kpi)


@pytest.mark.django_db
class TestKPIAlert:
    """Tests for KPIAlert model."""

    @pytest.fixture
    def kpi_definition(self, tenant_context):
        return KPIDefinition.objects.create(
            name="Stock Level",
            code="STOCK_LEVEL_TEST",
            category=KPICategory.INVENTORY,
        )

    def test_create_alert(self, kpi_definition):
        alert = KPIAlert.objects.create(
            kpi=kpi_definition,
            warning_threshold=10,
            critical_threshold=5,
            comparison="lt",
            is_active=True,
        )
        assert alert.warning_threshold == 10
        assert alert.critical_threshold == 5
        assert alert.comparison == "lt"
        assert alert.is_active is True

    def test_alert_notification_defaults(self, kpi_definition):
        alert = KPIAlert.objects.create(
            kpi=kpi_definition,
            warning_threshold=100,
            critical_threshold=200,
            comparison="gt",
        )
        assert alert.notify_email is False
        assert alert.notify_dashboard is True

    def test_alert_last_triggered_null(self, kpi_definition):
        alert = KPIAlert.objects.create(
            kpi=kpi_definition,
            warning_threshold=10,
            critical_threshold=5,
        )
        assert alert.last_triggered is None


@pytest.mark.django_db
class TestDashboardLayout:
    """Tests for DashboardLayout model."""

    def test_create_layout(self, user):
        layout = DashboardLayout.objects.create(
            user=user,
            name="My Dashboard",
            widgets={"widgets": [{"kpi_code": "SALES_TODAY", "position": {"x": 0, "y": 0}}]},
            is_default=True,
        )
        assert layout.name == "My Dashboard"
        assert layout.is_default is True
        assert len(layout.widgets["widgets"]) == 1

    def test_layout_default_widgets(self, user):
        layout = DashboardLayout.objects.create(user=user)
        assert layout.widgets == {"widgets": []}

    def test_layout_str(self, user):
        layout = DashboardLayout.objects.create(
            user=user,
            name="Test Layout",
        )
        assert "Test Layout" in str(layout)
