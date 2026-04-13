"""
Celery tasks for the analytics application.

Handles asynchronous report generation and scheduled report processing.
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="analytics.process_scheduled_reports")
def process_scheduled_reports():
    """
    Find and execute all scheduled reports that are due.

    This task should be called periodically (e.g. every minute via
    Celery Beat) to process overdue schedules.
    """
    from apps.analytics.models import ScheduledReport
    from apps.analytics.services.scheduler import ReportSchedulerService

    now = timezone.now()
    due = ScheduledReport.objects.filter(
        is_active=True,
        next_run__lte=now,
    ).select_related(
        "saved_report",
        "saved_report__report_definition",
    )

    processed = 0
    failed = 0
    for schedule in due:
        result = ReportSchedulerService.execute(schedule)
        if result["success"]:
            processed += 1
        else:
            failed += 1

    if processed or failed:
        logger.info(
            "Scheduled reports: %d processed, %d failed", processed, failed
        )
    return {"processed": processed, "failed": failed}
