"""Dashboard Celery tasks — periodic KPI alert checking."""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="apps.dashboard.tasks.check_kpi_alerts",
    bind=True,
    max_retries=2,
    default_retry_delay=60,
    queue="default",
)
def check_kpi_alerts(self):
    """Periodically check all KPI alerts against current values.

    Runs all calculators, collects results, and checks active alerts
    for threshold breaches.
    """
    from apps.dashboard.calculators import (
        FinancialKPICalculator,
        HRKPICalculator,
        InventoryKPICalculator,
        SalesKPICalculator,
    )
    from apps.dashboard.services.alert_service import check_all_alerts

    try:
        kpi_results = {}

        # Collect KPI values from each calculator
        calculators = [
            ("sales", SalesKPICalculator()),
            ("inventory", InventoryKPICalculator()),
            ("financial", FinancialKPICalculator()),
            ("hr", HRKPICalculator()),
        ]

        for category, calc in calculators:
            try:
                for code in _get_kpi_codes(category):
                    result = calc.calculate(code)
                    if "value" in result:
                        kpi_results[f"{category}_{code}"] = result["value"]
            except Exception:
                logger.exception("Error calculating %s KPIs", category)

        triggered = check_all_alerts(kpi_results)

        if triggered:
            logger.info(
                "KPI alert check complete: %d alert(s) triggered", len(triggered)
            )
        else:
            logger.debug("KPI alert check complete: no alerts triggered")

        return {"checked": len(kpi_results), "triggered": len(triggered)}

    except Exception as exc:
        logger.exception("KPI alert check failed")
        raise self.retry(exc=exc)


def _get_kpi_codes(category: str) -> list[str]:
    """Return the list of KPI codes for a calculator category."""
    codes = {
        "sales": [
            "todays_sales",
            "weekly_sales",
            "monthly_sales",
            "average_order_value",
            "orders_count",
        ],
        "inventory": [
            "stock_value",
            "low_stock_items",
            "out_of_stock",
            "inventory_turnover",
        ],
        "financial": [
            "revenue",
            "expenses",
            "net_income",
            "accounts_receivable",
            "accounts_payable",
        ],
        "hr": [
            "total_employees",
            "turnover_rate",
            "attendance_rate",
            "pending_leave_requests",
            "payroll_cost",
        ],
    }
    return codes.get(category, [])
