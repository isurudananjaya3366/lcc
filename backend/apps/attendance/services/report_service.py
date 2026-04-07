import logging
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from apps.attendance.constants import (
    ATTENDANCE_STATUS_ABSENT,
    ATTENDANCE_STATUS_HALF_DAY,
    ATTENDANCE_STATUS_HOLIDAY,
    ATTENDANCE_STATUS_LATE,
    ATTENDANCE_STATUS_ON_LEAVE,
    ATTENDANCE_STATUS_PRESENT,
    ATTENDANCE_STATUS_WEEKEND,
)

logger = logging.getLogger(__name__)


class AttendanceReportService:
    """Service for generating attendance reports and analytics."""

    @classmethod
    def daily_summary(cls, date, department=None):
        """Generate daily attendance summary.

        Returns dict with totals, attendance rate, and per-employee details.
        """
        from apps.attendance.models import AttendanceRecord
        from apps.employees.models import Employee

        employees_qs = Employee.objects.filter(is_deleted=False, status="active")
        if department:
            employees_qs = employees_qs.filter(department=department)

        total_employees = employees_qs.count()

        records_qs = AttendanceRecord.objects.filter(
            date=date, is_deleted=False,
        ).select_related("employee", "shift")

        if department:
            records_qs = records_qs.filter(employee__department=department)

        status_counts = records_qs.values("status").annotate(count=Count("id"))
        counts = {item["status"]: item["count"] for item in status_counts}

        present_count = counts.get(ATTENDANCE_STATUS_PRESENT, 0) + counts.get(ATTENDANCE_STATUS_LATE, 0)
        attendance_rate = round((present_count / total_employees) * 100, 1) if total_employees else 0

        employees = []
        for record in records_qs:
            employees.append({
                "id": str(record.employee.pk),
                "employee_id": record.employee.employee_id,
                "name": record.employee.full_name if hasattr(record.employee, "full_name") else str(record.employee),
                "status": record.status,
                "clock_in": record.clock_in.strftime("%H:%M") if record.clock_in else None,
                "clock_out": record.clock_out.strftime("%H:%M") if record.clock_out else None,
                "work_hours": float(record.effective_hours),
                "late_minutes": record.late_minutes,
            })

        return {
            "date": str(date),
            "total_employees": total_employees,
            "present": counts.get(ATTENDANCE_STATUS_PRESENT, 0),
            "late": counts.get(ATTENDANCE_STATUS_LATE, 0),
            "absent": counts.get(ATTENDANCE_STATUS_ABSENT, 0),
            "half_day": counts.get(ATTENDANCE_STATUS_HALF_DAY, 0),
            "on_leave": counts.get(ATTENDANCE_STATUS_ON_LEAVE, 0),
            "holiday": counts.get(ATTENDANCE_STATUS_HOLIDAY, 0),
            "attendance_rate": attendance_rate,
            "employees": employees,
        }

    @classmethod
    def weekly_summary(cls, start_date, end_date, employee=None):
        """Generate weekly attendance summary for an employee or all."""
        from apps.attendance.models import AttendanceRecord

        qs = AttendanceRecord.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False,
        ).select_related("employee", "shift").order_by("employee", "date")

        if employee:
            qs = qs.filter(employee=employee)

        # Group by employee
        summaries = defaultdict(lambda: {
            "days": {},
            "days_present": 0,
            "days_late": 0,
            "days_absent": 0,
            "days_leave": 0,
            "total_hours": Decimal("0"),
            "overtime_hours": Decimal("0"),
            "total_late_minutes": 0,
        })

        for record in qs:
            emp_key = str(record.employee.pk)
            summary = summaries[emp_key]
            summary["employee_id"] = record.employee.employee_id
            summary["employee_name"] = str(record.employee)

            summary["days"][str(record.date)] = {
                "status": record.status,
                "hours": float(record.effective_hours),
            }

            if record.status == ATTENDANCE_STATUS_PRESENT:
                summary["days_present"] += 1
            elif record.status == ATTENDANCE_STATUS_LATE:
                summary["days_late"] += 1
                summary["days_present"] += 1
            elif record.status == ATTENDANCE_STATUS_ABSENT:
                summary["days_absent"] += 1
            elif record.status == ATTENDANCE_STATUS_ON_LEAVE:
                summary["days_leave"] += 1

            summary["total_hours"] += record.effective_hours
            summary["overtime_hours"] += record.overtime_hours
            summary["total_late_minutes"] += record.late_minutes

        result = []
        for emp_key, summary in summaries.items():
            summary["total_hours"] = float(summary["total_hours"])
            summary["overtime_hours"] = float(summary["overtime_hours"])
            result.append(summary)

        return {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "summaries": result,
        }

    @classmethod
    def monthly_summary(cls, year, month, employee=None):
        """Generate monthly attendance summary."""
        from calendar import monthrange

        from apps.attendance.models import AttendanceRecord

        _, days_in_month = monthrange(year, month)
        start_date = timezone.datetime(year, month, 1).date()
        end_date = timezone.datetime(year, month, days_in_month).date()

        qs = AttendanceRecord.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False,
        )
        if employee:
            qs = qs.filter(employee=employee)

        aggregated = qs.aggregate(
            total_records=Count("id"),
            present_days=Count("id", filter=Q(status=ATTENDANCE_STATUS_PRESENT)),
            late_days=Count("id", filter=Q(status=ATTENDANCE_STATUS_LATE)),
            absent_days=Count("id", filter=Q(status=ATTENDANCE_STATUS_ABSENT)),
            half_days=Count("id", filter=Q(status=ATTENDANCE_STATUS_HALF_DAY)),
            leave_days=Count("id", filter=Q(status=ATTENDANCE_STATUS_ON_LEAVE)),
            total_work_hours=Sum("effective_hours"),
            total_overtime_hours=Sum("overtime_hours"),
            total_late_minutes=Sum("late_minutes"),
        )

        working_days = days_in_month  # Simplified; can subtract weekends/holidays
        present = (aggregated["present_days"] or 0) + (aggregated["late_days"] or 0)
        attendance_pct = round((present / working_days) * 100, 1) if working_days else 0

        return {
            "year": year,
            "month": month,
            "working_days": working_days,
            "present_days": aggregated["present_days"] or 0,
            "late_days": aggregated["late_days"] or 0,
            "absent_days": aggregated["absent_days"] or 0,
            "half_days": aggregated["half_days"] or 0,
            "leave_days": aggregated["leave_days"] or 0,
            "total_work_hours": float(aggregated["total_work_hours"] or 0),
            "total_overtime_hours": float(aggregated["total_overtime_hours"] or 0),
            "total_late_minutes": aggregated["total_late_minutes"] or 0,
            "attendance_percentage": attendance_pct,
        }

    @classmethod
    def employee_history(cls, employee, start_date, end_date):
        """Get individual employee attendance history."""
        from apps.attendance.models import AttendanceRecord

        records = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False,
        ).select_related("shift").order_by("date")

        history = []
        for r in records:
            history.append({
                "date": str(r.date),
                "status": r.status,
                "clock_in": r.clock_in.isoformat() if r.clock_in else None,
                "clock_out": r.clock_out.isoformat() if r.clock_out else None,
                "effective_hours": float(r.effective_hours),
                "late_minutes": r.late_minutes,
                "overtime_hours": float(r.overtime_hours),
                "shift": r.shift.name if r.shift else None,
            })

        return {
            "employee_id": employee.employee_id,
            "employee_name": str(employee),
            "start_date": str(start_date),
            "end_date": str(end_date),
            "records": history,
        }

    @classmethod
    def department_metrics(cls, department, start_date, end_date):
        """Department-level attendance metrics."""
        from apps.attendance.models import AttendanceRecord
        from apps.employees.models import Employee

        emp_count = Employee.objects.filter(
            department=department, is_deleted=False, status="active"
        ).count()

        records = AttendanceRecord.objects.filter(
            employee__department=department,
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False,
        )

        agg = records.aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status=ATTENDANCE_STATUS_PRESENT)),
            late=Count("id", filter=Q(status=ATTENDANCE_STATUS_LATE)),
            absent=Count("id", filter=Q(status=ATTENDANCE_STATUS_ABSENT)),
            avg_hours=Avg("effective_hours"),
            total_overtime=Sum("overtime_hours"),
            total_late_min=Sum("late_minutes"),
        )

        total_days = (end_date - start_date).days + 1
        expected_records = emp_count * total_days
        present_total = (agg["present"] or 0) + (agg["late"] or 0)
        attendance_rate = round((present_total / expected_records) * 100, 1) if expected_records else 0

        return {
            "department": str(department),
            "employee_count": emp_count,
            "date_range": f"{start_date} to {end_date}",
            "attendance_rate": attendance_rate,
            "total_present": agg["present"] or 0,
            "total_late": agg["late"] or 0,
            "total_absent": agg["absent"] or 0,
            "avg_daily_hours": float(agg["avg_hours"] or 0),
            "total_overtime_hours": float(agg["total_overtime"] or 0),
            "total_late_minutes": agg["total_late_min"] or 0,
        }

    @classmethod
    def late_arrivals_report(cls, start_date, end_date, department=None):
        """Report of late arrivals within a date range."""
        from apps.attendance.models import AttendanceRecord

        qs = AttendanceRecord.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            late_minutes__gt=0,
            is_deleted=False,
        ).select_related("employee", "shift").order_by("date")

        if department:
            qs = qs.filter(employee__department=department)

        records = []
        for r in qs:
            records.append({
                "date": str(r.date),
                "employee_id": r.employee.employee_id,
                "employee_name": str(r.employee),
                "shift_start": r.shift.start_time.strftime("%H:%M") if r.shift else None,
                "clock_in": r.clock_in.strftime("%H:%M") if r.clock_in else None,
                "late_minutes": r.late_minutes,
            })

        return {
            "date_range": f"{start_date} to {end_date}",
            "total_late_instances": len(records),
            "records": records,
        }

    @classmethod
    def overtime_report(cls, start_date, end_date, department=None):
        """Overtime hours summary by employee."""
        from apps.attendance.models import AttendanceRecord

        qs = AttendanceRecord.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            overtime_hours__gt=0,
            is_deleted=False,
        ).select_related("employee")

        if department:
            qs = qs.filter(employee__department=department)

        by_employee = qs.values(
            "employee__employee_id",
            "employee__first_name",
            "employee__last_name",
        ).annotate(
            total_ot_hours=Sum("overtime_hours"),
            ot_days=Count("id"),
        ).order_by("-total_ot_hours")

        records = []
        for item in by_employee:
            records.append({
                "employee_id": item["employee__employee_id"],
                "employee_name": f"{item['employee__first_name']} {item['employee__last_name']}",
                "total_overtime_hours": float(item["total_ot_hours"]),
                "overtime_days": item["ot_days"],
            })

        return {
            "date_range": f"{start_date} to {end_date}",
            "total_overtime_instances": len(records),
            "records": records,
        }

    @classmethod
    def absence_report(cls, start_date, end_date, department=None):
        """List of absences for a date range with analytics."""
        from apps.attendance.models import AttendanceRecord

        qs = AttendanceRecord.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            status__in=[ATTENDANCE_STATUS_ABSENT, ATTENDANCE_STATUS_ON_LEAVE, ATTENDANCE_STATUS_HALF_DAY],
            is_deleted=False,
        ).select_related("employee").order_by("date")

        if department:
            qs = qs.filter(employee__department=department)

        records = []
        # Track per-employee absence spells for Bradford Factor
        employee_spells = defaultdict(list)
        employee_days = defaultdict(int)

        for r in qs:
            absence_type = "absent"
            if r.status == ATTENDANCE_STATUS_ON_LEAVE:
                absence_type = "leave"
            elif r.status == ATTENDANCE_STATUS_HALF_DAY:
                absence_type = "half_day"

            records.append({
                "date": str(r.date),
                "employee_id": r.employee.employee_id,
                "employee_name": str(r.employee),
                "absence_type": absence_type,
            })

            emp_key = str(r.employee.pk)
            employee_days[emp_key] += 1

            # Track spells (consecutive absence sequences)
            spells = employee_spells[emp_key]
            if spells and (r.date - spells[-1]["end"]).days <= 1:
                spells[-1]["end"] = r.date
                spells[-1]["days"] += 1
            else:
                spells.append({"start": r.date, "end": r.date, "days": 1})

        # Calculate Bradford Factor: S² × D (S=spells, D=total days)
        bradford_scores = []
        for emp_key, spells in employee_spells.items():
            s = len(spells)
            d = employee_days[emp_key]
            bradford_scores.append({
                "employee_key": emp_key,
                "spells": s,
                "total_days": d,
                "bradford_factor": s * s * d,
            })
        bradford_scores.sort(key=lambda x: x["bradford_factor"], reverse=True)

        return {
            "date_range": f"{start_date} to {end_date}",
            "total_absences": len(records),
            "records": records,
            "bradford_top_10": bradford_scores[:10],
        }

    @classmethod
    def attendance_percentage(cls, employee, start_date, end_date):
        """Calculate attendance metrics for an employee.

        Returns basic attendance %, adjusted % (with approved leave), and punctuality rate.
        """
        from apps.attendance.models import AttendanceRecord

        total_days = (end_date - start_date).days + 1

        records = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=end_date,
            is_deleted=False,
        )

        present_count = records.filter(
            status__in=[ATTENDANCE_STATUS_PRESENT, ATTENDANCE_STATUS_LATE]
        ).count()

        on_time_count = records.filter(status=ATTENDANCE_STATUS_PRESENT).count()
        late_count = records.filter(status=ATTENDANCE_STATUS_LATE).count()
        leave_count = records.filter(status=ATTENDANCE_STATUS_ON_LEAVE).count()
        holiday_count = records.filter(
            status__in=[ATTENDANCE_STATUS_HOLIDAY, ATTENDANCE_STATUS_WEEKEND]
        ).count()

        # Basic Attendance % = Present / Total Working Days × 100
        working_days = total_days - holiday_count
        percentage = round((present_count / working_days) * 100, 1) if working_days else 0

        # Adjusted % = (Present + Approved Leave) / Working Days × 100
        adjusted_pct = round(
            ((present_count + leave_count) / working_days) * 100, 1
        ) if working_days else 0

        # Punctuality Rate = On-Time / Total Present × 100
        punctuality_rate = round(
            (on_time_count / present_count) * 100, 1
        ) if present_count else 0

        return {
            "employee_id": employee.employee_id,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "total_days": total_days,
            "working_days": working_days,
            "present_days": present_count,
            "on_time_days": on_time_count,
            "late_days": late_count,
            "leave_days": leave_count,
            "attendance_percentage": percentage,
            "adjusted_attendance_percentage": adjusted_pct,
            "punctuality_rate": punctuality_rate,
        }

    @classmethod
    def dashboard_data(cls, date=None, department=None):
        """Aggregate data for attendance dashboard widgets.

        Includes summary, trend data (last 7 days), department breakdown,
        and top late employees.
        """
        if date is None:
            date = timezone.localdate()

        daily = cls.daily_summary(date, department=department)

        from apps.attendance.models import AttendanceRecord

        # Currently clocked in (no clock-out yet)
        clocked_in_count = AttendanceRecord.objects.filter(
            date=date,
            clock_in__isnull=False,
            clock_out__isnull=True,
            is_deleted=False,
        ).count()

        # ── Trend data (last 7 days) ────────────────────────
        trend_data = []
        for i in range(6, -1, -1):
            d = date - timedelta(days=i)
            records = AttendanceRecord.objects.filter(date=d, is_deleted=False)
            present = records.filter(
                status__in=[ATTENDANCE_STATUS_PRESENT, ATTENDANCE_STATUS_LATE]
            ).count()
            absent = records.filter(status=ATTENDANCE_STATUS_ABSENT).count()
            trend_data.append({
                "date": str(d),
                "present": present,
                "absent": absent,
            })

        # ── Department breakdown ─────────────────────────────
        department_breakdown = []
        dept_data = (
            AttendanceRecord.objects.filter(date=date, is_deleted=False)
            .values("employee__department__name")
            .annotate(
                total=Count("id"),
                present=Count("id", filter=Q(
                    status__in=[ATTENDANCE_STATUS_PRESENT, ATTENDANCE_STATUS_LATE]
                )),
                absent=Count("id", filter=Q(status=ATTENDANCE_STATUS_ABSENT)),
                late=Count("id", filter=Q(status=ATTENDANCE_STATUS_LATE)),
            )
        )
        for dept in dept_data:
            department_breakdown.append({
                "department": dept["employee__department__name"] or "Unassigned",
                "total": dept["total"],
                "present": dept["present"],
                "absent": dept["absent"],
                "late": dept["late"],
            })

        # ── Top late employees (current month) ───────────────
        month_start = date.replace(day=1)
        top_late = (
            AttendanceRecord.objects.filter(
                date__gte=month_start,
                date__lte=date,
                late_minutes__gt=0,
                is_deleted=False,
            )
            .values("employee__employee_id", "employee__first_name", "employee__last_name")
            .annotate(
                total_late_minutes=Sum("late_minutes"),
                late_count=Count("id"),
            )
            .order_by("-total_late_minutes")[:10]
        )
        top_late_employees = [
            {
                "employee_id": item["employee__employee_id"],
                "name": f"{item['employee__first_name']} {item['employee__last_name']}",
                "total_late_minutes": item["total_late_minutes"],
                "late_count": item["late_count"],
            }
            for item in top_late
        ]

        return {
            "date": str(date),
            "summary": daily,
            "currently_clocked_in": clocked_in_count,
            "trend_data": trend_data,
            "department_breakdown": department_breakdown,
            "top_late_employees": top_late_employees,
        }

    @classmethod
    def payroll_integration_data(cls, year, month, department=None):
        """Export attendance data formatted for payroll processing."""
        from calendar import monthrange

        from apps.attendance.models import AttendanceRecord
        from apps.employees.models import Employee

        _, days_in_month = monthrange(year, month)
        start_date = timezone.datetime(year, month, 1).date()
        end_date = timezone.datetime(year, month, days_in_month).date()

        employees_qs = Employee.objects.filter(is_deleted=False, status="active")
        if department:
            employees_qs = employees_qs.filter(department=department)

        payroll_data = []
        for emp in employees_qs:
            records = AttendanceRecord.objects.filter(
                employee=emp,
                date__gte=start_date,
                date__lte=end_date,
                is_deleted=False,
            )

            agg = records.aggregate(
                present_days=Count("id", filter=Q(status__in=[ATTENDANCE_STATUS_PRESENT, ATTENDANCE_STATUS_LATE])),
                absent_days=Count("id", filter=Q(status=ATTENDANCE_STATUS_ABSENT)),
                half_days=Count("id", filter=Q(status=ATTENDANCE_STATUS_HALF_DAY)),
                total_hours=Sum("effective_hours"),
                total_ot_hours=Sum("overtime_hours"),
                total_late_min=Sum("late_minutes"),
            )

            payroll_data.append({
                "employee_id": emp.employee_id,
                "employee_name": str(emp),
                "present_days": agg["present_days"] or 0,
                "absent_days": agg["absent_days"] or 0,
                "half_days": agg["half_days"] or 0,
                "total_work_hours": float(agg["total_hours"] or 0),
                "total_overtime_hours": float(agg["total_ot_hours"] or 0),
                "total_late_minutes": agg["total_late_min"] or 0,
            })

        return {
            "year": year,
            "month": month,
            "generated_at": timezone.now().isoformat(),
            "employees": payroll_data,
        }
