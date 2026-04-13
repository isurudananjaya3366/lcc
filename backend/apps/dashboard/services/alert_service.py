"""Alert check service — checks KPI values against alert thresholds."""

import logging
from decimal import Decimal

from django.utils import timezone

logger = logging.getLogger(__name__)


def check_alert(kpi_alert, current_value) -> dict | None:
    """Check if a KPI value triggers an alert.

    Returns alert info dict if triggered, None otherwise.
    """
    value = Decimal(str(current_value))
    comparison = kpi_alert.comparison
    warning = kpi_alert.warning_threshold
    critical = kpi_alert.critical_threshold

    severity = None

    if comparison == "lt":
        if value < critical:
            severity = "critical"
        elif value < warning:
            severity = "warning"
    elif comparison == "gt":
        if value > critical:
            severity = "critical"
        elif value > warning:
            severity = "warning"
    elif comparison == "lte":
        if value <= critical:
            severity = "critical"
        elif value <= warning:
            severity = "warning"
    elif comparison == "gte":
        if value >= critical:
            severity = "critical"
        elif value >= warning:
            severity = "warning"

    if severity:
        kpi_alert.last_triggered = timezone.now()
        kpi_alert.save(update_fields=["last_triggered"])
        return {
            "kpi_id": kpi_alert.kpi_id,
            "kpi_name": kpi_alert.kpi.name,
            "severity": severity,
            "current_value": str(value),
            "warning_threshold": str(warning),
            "critical_threshold": str(critical),
            "triggered_at": timezone.now().isoformat(),
        }
    return None


def check_all_alerts(kpi_results: dict) -> list[dict]:
    """Check all active alerts against current KPI values.

    Args:
        kpi_results: Dict mapping KPI codes to their current values.

    Returns:
        List of triggered alert info dicts.
    """
    from apps.dashboard.models import KPIAlert

    triggered = []
    active_alerts = KPIAlert.objects.filter(is_active=True).select_related("kpi")

    for alert in active_alerts:
        code = alert.kpi.code
        if code in kpi_results:
            result = check_alert(alert, kpi_results[code])
            if result:
                triggered.append(result)
                logger.warning(
                    "KPI alert triggered: %s (%s) — value: %s",
                    result["kpi_name"],
                    result["severity"],
                    result["current_value"],
                )

    return triggered
