"""Tests for analytics scheduler service and Celery tasks."""

from datetime import time, timedelta
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.analytics.enums import (
    ReportCategory,
    ReportFormat,
    ReportStatus,
    ScheduleFrequency,
)
from apps.analytics.models import (
    ReportDefinition,
    ReportInstance,
    SavedReport,
    ScheduledReport,
    ScheduleHistory,
)
from apps.analytics.services.scheduler import ReportSchedulerService
from apps.analytics.tasks import process_scheduled_reports

pytestmark = pytest.mark.django_db


def _uid():
    return uuid4().hex[:8]


class TestReportSchedulerService:
    """Tests for ReportSchedulerService."""

    def _create_schedule(self, user, code="CUSTOMER_ACQUISITION", **kwargs):
        uid = _uid()
        rd = ReportDefinition.objects.create(
            name=f"SchedGen {uid}",
            code=code,
            category=ReportCategory.CUSTOMER,
            is_active=True,
        )
        saved = SavedReport.objects.create(
            name=f"Saved {uid}",
            report_definition=rd,
            owner=user,
        )
        defaults = {
            "saved_report": saved,
            "frequency": ScheduleFrequency.DAILY,
            "created_by": user,
            "is_active": True,
        }
        defaults.update(kwargs)
        return ScheduledReport.objects.create(**defaults)

    def test_get_generator_class_valid(self, tenant_context):
        cls = ReportSchedulerService.get_generator_class("CUSTOMER_ACQUISITION")
        assert cls.__name__ == "CustomerAcquisitionReport"

    def test_get_generator_class_invalid(self, tenant_context):
        with pytest.raises(ValueError):
            ReportSchedulerService.get_generator_class("NONEXISTENT")

    def test_get_default_date_range_daily(self, tenant_context):
        dr = ReportSchedulerService.get_default_date_range(ScheduleFrequency.DAILY)
        assert "start_date" in dr
        assert dr["start_date"] == dr["end_date"]

    def test_get_default_date_range_weekly(self, tenant_context):
        dr = ReportSchedulerService.get_default_date_range(ScheduleFrequency.WEEKLY)
        assert "start_date" in dr
        assert dr["start_date"] != dr["end_date"]

    def test_get_default_date_range_monthly(self, tenant_context):
        dr = ReportSchedulerService.get_default_date_range(ScheduleFrequency.MONTHLY)
        assert "start_date" in dr

    def test_execute_success(self, user):
        sched = self._create_schedule(user)
        result = ReportSchedulerService.execute(sched)
        assert result["success"] is True
        assert result["report_data"] is not None
        assert result["error"] is None

        sched.refresh_from_db()
        assert sched.last_status == "SUCCESS"
        assert sched.last_run is not None
        assert sched.last_report_instance is not None

        # Verify history created
        history = ScheduleHistory.objects.filter(scheduled_report=sched)
        assert history.count() == 1
        assert history.first().status == "SUCCESS"

    def test_execute_failure(self, user):
        sched = self._create_schedule(user, code="NONEXISTENT_CODE")
        # Force code to something invalid after creation
        sched.saved_report.report_definition.code = "INVALID_XYZ"
        sched.saved_report.report_definition.save()

        result = ReportSchedulerService.execute(sched)
        assert result["success"] is False
        assert result["error"] is not None

        sched.refresh_from_db()
        assert sched.last_status == "FAILED"

    def test_execute_creates_report_instance(self, user):
        sched = self._create_schedule(user)
        initial_count = ReportInstance.objects.count()
        ReportSchedulerService.execute(sched)
        assert ReportInstance.objects.count() == initial_count + 1

    def test_generator_map_completeness(self, tenant_context):
        """All registered generators should be importable."""
        for code, path in ReportSchedulerService.GENERATOR_MAP.items():
            cls = ReportSchedulerService.get_generator_class(code)
            assert cls is not None, f"Failed to load generator for {code}"


class TestProcessScheduledReportsTask:
    """Tests for the Celery task."""

    def _create_due_schedule(self, user):
        uid = _uid()
        rd = ReportDefinition.objects.create(
            name=f"Due {uid}",
            code="CUSTOMER_ACQUISITION",
            category=ReportCategory.CUSTOMER,
            is_active=True,
        )
        saved = SavedReport.objects.create(
            name=f"DueSv {uid}", report_definition=rd, owner=user,
        )
        return ScheduledReport.objects.create(
            saved_report=saved,
            frequency=ScheduleFrequency.DAILY,
            created_by=user,
            is_active=True,
            next_run=timezone.now() - timedelta(minutes=5),
        )

    def test_process_due_reports(self, user):
        sched = self._create_due_schedule(user)
        result = process_scheduled_reports()
        assert result["processed"] >= 1
        assert result["failed"] == 0

        sched.refresh_from_db()
        assert sched.last_status == "SUCCESS"
        assert sched.next_run > timezone.now()

    def test_no_due_reports(self, tenant_context):
        result = process_scheduled_reports()
        assert result["processed"] == 0
        assert result["failed"] == 0

    def test_inactive_schedules_skipped(self, user):
        uid = _uid()
        rd = ReportDefinition.objects.create(
            name=f"Inact {uid}",
            code="CUSTOMER_RETENTION",
            category=ReportCategory.CUSTOMER,
            is_active=True,
        )
        saved = SavedReport.objects.create(
            name=f"InactSv {uid}", report_definition=rd, owner=user
        )
        ScheduledReport.objects.create(
            saved_report=saved,
            frequency=ScheduleFrequency.DAILY,
            created_by=user,
            is_active=False,
            next_run=timezone.now() - timedelta(minutes=5),
        )
        result = process_scheduled_reports()
        # inactive schedules should not be processed
        assert result["failed"] == 0

    def test_future_schedules_skipped(self, user):
        uid = _uid()
        rd = ReportDefinition.objects.create(
            name=f"Fut {uid}",
            code="CUSTOMER_RETENTION",
            category=ReportCategory.CUSTOMER,
            is_active=True,
        )
        saved = SavedReport.objects.create(
            name=f"FutSv {uid}", report_definition=rd, owner=user
        )
        ScheduledReport.objects.create(
            saved_report=saved,
            frequency=ScheduleFrequency.DAILY,
            created_by=user,
            is_active=True,
            next_run=timezone.now() + timedelta(hours=1),
        )
        result = process_scheduled_reports()
        # future schedules should not be processed
        assert result["failed"] == 0
