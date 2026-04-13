"""Tests for dashboard alert service."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from apps.dashboard.services.alert_service import check_alert, check_all_alerts


class TestCheckAlert:
    """Tests for check_alert function."""

    def _make_alert(self, warning, critical, comparison="lt"):
        alert = MagicMock()
        alert.warning_threshold = Decimal(str(warning))
        alert.critical_threshold = Decimal(str(critical))
        alert.comparison = comparison
        alert.kpi_id = 1
        alert.kpi.name = "Test KPI"
        return alert

    def test_no_alert_value_above_warning_lt(self):
        alert = self._make_alert(warning=10, critical=5, comparison="lt")
        result = check_alert(alert, 15)
        assert result is None

    def test_warning_triggered_lt(self):
        alert = self._make_alert(warning=10, critical=5, comparison="lt")
        result = check_alert(alert, 8)
        assert result is not None
        assert result["severity"] == "warning"

    def test_critical_triggered_lt(self):
        alert = self._make_alert(warning=10, critical=5, comparison="lt")
        result = check_alert(alert, 3)
        assert result is not None
        assert result["severity"] == "critical"

    def test_warning_triggered_gt(self):
        alert = self._make_alert(warning=80, critical=90, comparison="gt")
        result = check_alert(alert, 85)
        assert result is not None
        assert result["severity"] == "warning"

    def test_critical_triggered_gt(self):
        alert = self._make_alert(warning=80, critical=90, comparison="gt")
        result = check_alert(alert, 95)
        assert result is not None
        assert result["severity"] == "critical"

    def test_no_alert_gt(self):
        alert = self._make_alert(warning=80, critical=90, comparison="gt")
        result = check_alert(alert, 70)
        assert result is None

    def test_warning_triggered_lte(self):
        alert = self._make_alert(warning=10, critical=5, comparison="lte")
        result = check_alert(alert, 10)
        assert result is not None
        assert result["severity"] == "warning"

    def test_warning_triggered_gte(self):
        alert = self._make_alert(warning=80, critical=90, comparison="gte")
        result = check_alert(alert, 80)
        assert result is not None
        assert result["severity"] == "warning"

    def test_alert_updates_last_triggered(self):
        alert = self._make_alert(warning=10, critical=5, comparison="lt")
        check_alert(alert, 3)
        alert.save.assert_called_once()


@pytest.mark.django_db
class TestCheckAllAlerts:
    """Tests for check_all_alerts function."""

    def test_no_active_alerts(self, tenant_context):
        result = check_all_alerts({})
        assert result == []

    def test_no_matching_kpi_codes(self, tenant_context):
        result = check_all_alerts({"nonexistent_code": 100})
        assert result == []
