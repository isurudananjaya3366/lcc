import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def mark_daily_absent(self):
    """Mark employees as ABSENT if they have no clock-in by end of shift + grace.

    Runs daily (e.g., at configured mark_absent_after_hours after shift start).
    Iterates over all tenants. Skips employees without a shift on the given day.
    """
    try:
        from django_tenants.utils import tenant_context

        from apps.attendance.constants import ATTENDANCE_STATUS_ABSENT
        from apps.attendance.models import AttendanceRecord
        from apps.attendance.models.attendance_settings import AttendanceSettings
        from apps.attendance.models.shift_schedule import ShiftSchedule
        from apps.employees.models import Employee
        from apps.tenants.models import Tenant

        today = timezone.localdate()

        for tenant in Tenant.objects.exclude(schema_name="public"):
            with tenant_context(tenant):
                settings = AttendanceSettings.get_for_tenant(tenant)
                if not settings.auto_absence_marking_enabled:
                    continue

                active_employees = Employee.objects.filter(
                    is_deleted=False, status="active"
                )
                existing_records = set(
                    AttendanceRecord.objects.filter(
                        date=today, is_deleted=False
                    ).values_list("employee_id", flat=True)
                )

                # Determine which employees have a shift today
                today_schedules = ShiftSchedule.objects.filter(
                    is_active=True,
                    is_deleted=False,
                    effective_from__lte=today,
                ).filter(
                    models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=today)
                )
                employees_with_shift = set()
                for schedule in today_schedules:
                    if schedule.applies_on_date(today):
                        if schedule.employee_id:
                            employees_with_shift.add(schedule.employee_id)
                        elif schedule.department_id:
                            dept_emp_ids = Employee.objects.filter(
                                department_id=schedule.department_id,
                                is_deleted=False,
                                status="active",
                            ).values_list("pk", flat=True)
                            employees_with_shift.update(dept_emp_ids)

                absent_records = []
                for emp in active_employees:
                    if emp.pk in existing_records:
                        continue
                    # Only mark absent if employee has a shift today
                    if employees_with_shift and emp.pk not in employees_with_shift:
                        continue
                    absent_records.append(
                        AttendanceRecord(
                            employee=emp,
                            date=today,
                            status=ATTENDANCE_STATUS_ABSENT,
                        )
                    )

                if absent_records:
                    AttendanceRecord.objects.bulk_create(absent_records, ignore_conflicts=True)
                    logger.info(
                        "Marked %d employees absent for tenant=%s date=%s",
                        len(absent_records), tenant.schema_name, today,
                    )

    except Exception as exc:
        logger.error("mark_daily_absent failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def auto_clock_out(self):
    """Auto clock-out employees who forgot to punch out.

    Runs at the configured auto_clock_out_time (e.g., 23:00).
    Uses AttendanceSettings.auto_clock_out_time if set, otherwise uses current time.
    """
    try:
        from django_tenants.utils import tenant_context

        from apps.attendance.models import AttendanceRecord
        from apps.attendance.models.attendance_settings import AttendanceSettings
        from apps.attendance.services.attendance_service import AttendanceService
        from apps.tenants.models import Tenant

        today = timezone.localdate()
        now = timezone.now()

        for tenant in Tenant.objects.exclude(schema_name="public"):
            with tenant_context(tenant):
                settings = AttendanceSettings.get_for_tenant(tenant)
                if not settings.auto_clock_out_enabled:
                    continue

                # Determine the clock-out timestamp
                if settings.auto_clock_out_time:
                    clock_out_dt = timezone.make_aware(
                        datetime.combine(today, settings.auto_clock_out_time)
                    )
                else:
                    clock_out_dt = now

                open_records = AttendanceRecord.objects.filter(
                    date=today,
                    clock_in__isnull=False,
                    clock_out__isnull=True,
                    is_deleted=False,
                )

                count = 0
                for record in open_records:
                    record.clock_out = clock_out_dt
                    record.clock_out_method = "system"
                    record.notes = (
                        record.notes + "\n[Auto clock-out by system]"
                    ).strip()

                    AttendanceService.calculate_work_hours(record)
                    AttendanceService.determine_status(record)
                    record.save()
                    count += 1

                if count:
                    logger.info(
                        "Auto clock-out for %d records tenant=%s",
                        count, tenant.schema_name,
                    )

    except Exception as exc:
        logger.error("auto_clock_out failed: %s", exc)
        raise self.retry(exc=exc)
