"""
Report scheduler service.

Provides the core logic for executing scheduled reports,
delegating actual generation to the appropriate generator.
"""

import logging
import time
from datetime import date, timedelta
from typing import Any

from django.utils import timezone

from apps.analytics.enums import ReportStatus, ScheduleFrequency

logger = logging.getLogger(__name__)


class ReportSchedulerService:
    """Execute scheduled reports and record results."""

    # ── Report-type → generator mapping ──────────────────────────

    GENERATOR_MAP: dict[str, str] = {
        "SALES_BY_PRODUCT": "apps.analytics.generators.sales.by_product.SalesByProductReport",
        "SALES_BY_CUSTOMER": "apps.analytics.generators.sales.by_customer.SalesByCustomerReport",
        "SALES_BY_PERIOD": "apps.analytics.generators.sales.by_period.SalesByPeriodReport",
        "SALES_BY_CHANNEL": "apps.analytics.generators.sales.by_channel.SalesByChannelReport",
        "SALES_BY_CASHIER": "apps.analytics.generators.sales.by_cashier.SalesByCashierReport",
        "STOCK_LEVEL": "apps.analytics.generators.inventory.stock_level.StockLevelReport",
        "STOCK_MOVEMENT": "apps.analytics.generators.inventory.stock_movement.StockMovementReport",
        "STOCK_VALUATION": "apps.analytics.generators.inventory.stock_valuation.StockValuationReport",
        "PURCHASE_VENDOR": "apps.analytics.generators.purchase.by_vendor.PurchaseByVendorReport",
        "PURCHASE_CATEGORY": "apps.analytics.generators.purchase.by_category.PurchaseByCategoryReport",
        "VENDOR_PERFORMANCE": "apps.analytics.generators.purchase.vendor_performance.VendorPerformanceReport",
        "CUSTOMER_ACQUISITION": "apps.analytics.generators.customer.acquisition.CustomerAcquisitionReport",
        "CUSTOMER_RETENTION": "apps.analytics.generators.customer.retention.CustomerRetentionReport",
        "CUSTOMER_LIFETIME_VALUE": "apps.analytics.generators.customer.lifetime_value.CustomerLifetimeValueReport",
        "STAFF_ATTENDANCE": "apps.analytics.generators.staff.attendance.AttendanceReport",
        "STAFF_LEAVE": "apps.analytics.generators.staff.leave.LeaveReport",
        "STAFF_OVERTIME": "apps.analytics.generators.staff.overtime.OvertimeReport",
    }

    @classmethod
    def get_generator_class(cls, report_code: str):
        """Dynamically import and return the generator class."""
        dotted_path = cls.GENERATOR_MAP.get(report_code)
        if not dotted_path:
            raise ValueError(f"No generator registered for code: {report_code}")
        module_path, class_name = dotted_path.rsplit(".", 1)
        import importlib

        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    # ── Default date range per frequency ─────────────────────────

    @staticmethod
    def get_default_date_range(frequency: str) -> dict[str, str]:
        """Return the default date range based on schedule frequency."""
        today = date.today()
        if frequency == ScheduleFrequency.DAILY:
            yesterday = today - timedelta(days=1)
            return {
                "start_date": yesterday.isoformat(),
                "end_date": yesterday.isoformat(),
            }
        if frequency == ScheduleFrequency.WEEKLY:
            start = today - timedelta(days=7)
            end = today - timedelta(days=1)
            return {
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
            }
        if frequency == ScheduleFrequency.MONTHLY:
            # Previous calendar month
            first_this_month = today.replace(day=1)
            last_prev = first_this_month - timedelta(days=1)
            first_prev = last_prev.replace(day=1)
            return {
                "start_date": first_prev.isoformat(),
                "end_date": last_prev.isoformat(),
            }
        return {}

    # ── Execute a single ScheduledReport ─────────────────────────

    @classmethod
    def execute(cls, scheduled_report) -> dict[str, Any]:
        """
        Generate a report for the given ScheduledReport.

        Returns a dict with keys: ``success``, ``report_data``,
        ``execution_time``, ``error``.
        """
        from apps.analytics.models import ReportInstance, ScheduleHistory

        start = time.time()
        saved = scheduled_report.saved_report
        report_def = saved.report_definition
        filters = dict(saved.filters_config or {})

        # Inject default date_range if not provided
        if "date_range" not in filters:
            filters["date_range"] = cls.get_default_date_range(
                scheduled_report.frequency
            )

        # Create instance record
        instance = ReportInstance.objects.create(
            report_definition=report_def,
            user=scheduled_report.created_by,
            filter_parameters=filters,
            output_format=saved.output_format,
            status=ReportStatus.GENERATING,
            started_at=timezone.now(),
        )

        try:
            generator_cls = cls.get_generator_class(report_def.code)
            generator = generator_cls(
                filter_parameters=filters,
                user=scheduled_report.created_by,
            )
            report_data = generator.generate()

            elapsed = round(time.time() - start, 2)
            instance.mark_completed(file_path="", file_size=0)
            instance.generation_time_seconds = elapsed
            instance.save(update_fields=["generation_time_seconds"])

            # Update schedule metadata
            scheduled_report.last_run = timezone.now()
            scheduled_report.last_status = "SUCCESS"
            scheduled_report.last_report_instance = instance
            scheduled_report.error_message = None
            scheduled_report.next_run = scheduled_report.calculate_next_run()
            scheduled_report.save(
                update_fields=[
                    "last_run",
                    "last_status",
                    "last_report_instance",
                    "error_message",
                    "next_run",
                ]
            )

            ScheduleHistory.create_history(
                scheduled_report=scheduled_report,
                status="SUCCESS",
                report_instance=instance,
                execution_time_seconds=elapsed,
            )

            return {
                "success": True,
                "report_data": report_data,
                "execution_time": elapsed,
                "error": None,
            }

        except Exception as exc:
            elapsed = round(time.time() - start, 2)
            error_msg = str(exc)
            instance.mark_failed(error_msg)

            scheduled_report.last_run = timezone.now()
            scheduled_report.last_status = "FAILED"
            scheduled_report.error_message = error_msg
            scheduled_report.next_run = scheduled_report.calculate_next_run()
            scheduled_report.save(
                update_fields=[
                    "last_run",
                    "last_status",
                    "error_message",
                    "next_run",
                ]
            )

            ScheduleHistory.create_history(
                scheduled_report=scheduled_report,
                status="FAILED",
                report_instance=instance,
                error_message=error_msg,
                execution_time_seconds=elapsed,
            )

            logger.exception(
                "Scheduled report %s failed: %s",
                scheduled_report.id,
                error_msg,
            )
            return {
                "success": False,
                "report_data": None,
                "execution_time": elapsed,
                "error": error_msg,
            }
