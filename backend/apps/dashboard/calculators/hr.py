"""HR KPI calculator — employee, attendance, leave, and payroll metrics."""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.attendance.constants import (
    ATTENDANCE_STATUS_ABSENT,
    ATTENDANCE_STATUS_PRESENT,
)
from apps.dashboard.calculators.base import BaseKPICalculator
from apps.employees.constants import (
    EMPLOYEE_STATUS_ACTIVE,
    EMPLOYEE_STATUS_RESIGNED,
    EMPLOYEE_STATUS_TERMINATED,
)
from apps.leave.constants import LeaveRequestStatus


class HRKPICalculator(BaseKPICalculator):
    """Calculates HR-related KPIs for workforce analytics."""

    kpi_category = "hr"

    def calculate(self, kpi_code: str, period: str = "month") -> dict:
        """Route to the appropriate HR KPI calculation."""
        methods = {
            "total_employees": self.total_employees,
            "new_hires": self.new_hires,
            "turnover_rate": self.turnover_rate,
            "attendance_rate": self.attendance_rate,
            "leave_balance_summary": self.leave_balance_summary,
            "pending_leave_requests": self.pending_leave_requests,
            "payroll_cost": self.payroll_cost,
            "department_headcount": self.department_headcount,
            "employee_gender_ratio": self.employee_gender_ratio,
            "overtime_summary": self.overtime_summary,
        }
        method = methods.get(kpi_code)
        if method is None:
            return {"error": f"Unknown HR KPI: {kpi_code}"}
        return method(period)

    # ── helpers ──────────────────────────────────────────────────────

    def _get_employee_qs(self):
        from apps.employees.models import Employee

        return Employee.objects.filter(is_deleted=False)

    def _get_active_employees(self):
        return self._get_employee_qs().filter(status=EMPLOYEE_STATUS_ACTIVE)

    # ── Task 66: Total Employee Count ────────────────────────────────

    def total_employees(self, period: str = "month") -> dict:
        """Total active employees with departmental breakdown."""
        qs = self._get_active_employees()
        total = qs.count()

        by_department = list(
            qs.values("department__name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        by_type = list(
            qs.values("employment_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return self.format_result(
            value=total,
            label="Total Active Employees",
            extra={
                "by_department": [
                    {
                        "department": r["department__name"] or "Unassigned",
                        "count": r["count"],
                    }
                    for r in by_department
                ],
                "by_employment_type": [
                    {"type": r["employment_type"], "count": r["count"]}
                    for r in by_type
                ],
            },
        )

    # ── Task 67: New Hires ───────────────────────────────────────────

    def new_hires(self, period: str = "month") -> dict:
        """Count of new hires within the selected period."""
        start, end = self.get_date_range(period)
        prev_start, prev_end = self.get_previous_date_range(period)

        qs = self._get_employee_qs()
        current = qs.filter(hire_date__gte=start, hire_date__lte=end).count()
        previous = qs.filter(
            hire_date__gte=prev_start, hire_date__lte=prev_end
        ).count()

        change = self.calculate_change(current, previous)

        return self.format_result(
            value=current,
            label="New Hires",
            change=change,
            extra={"previous_period": previous},
        )

    # ── Task 68: Turnover Rate ───────────────────────────────────────

    def turnover_rate(self, period: str = "month") -> dict:
        """Employee turnover rate for the period.

        Turnover = (Separations / Average Headcount) * 100
        """
        start, end = self.get_date_range(period)
        qs = self._get_employee_qs()

        separations = qs.filter(
            status__in=[EMPLOYEE_STATUS_RESIGNED, EMPLOYEE_STATUS_TERMINATED],
            termination_date__gte=start,
            termination_date__lte=end,
        ).count()

        # Average headcount: active at start + active at end / 2
        active_start = qs.filter(
            Q(hire_date__lte=start),
            Q(termination_date__isnull=True) | Q(termination_date__gt=start),
        ).count()
        active_end = qs.filter(
            Q(hire_date__lte=end),
            Q(termination_date__isnull=True) | Q(termination_date__gt=end),
        ).count()

        avg_headcount = (active_start + active_end) / 2 if (active_start + active_end) else 1
        rate = round((separations / avg_headcount) * 100, 2)

        # Previous period
        prev_start, prev_end = self.get_previous_date_range(period)
        prev_separations = qs.filter(
            status__in=[EMPLOYEE_STATUS_RESIGNED, EMPLOYEE_STATUS_TERMINATED],
            termination_date__gte=prev_start,
            termination_date__lte=prev_end,
        ).count()
        prev_active_start = qs.filter(
            Q(hire_date__lte=prev_start),
            Q(termination_date__isnull=True) | Q(termination_date__gt=prev_start),
        ).count()
        prev_active_end = qs.filter(
            Q(hire_date__lte=prev_end),
            Q(termination_date__isnull=True) | Q(termination_date__gt=prev_end),
        ).count()
        prev_avg = (prev_active_start + prev_active_end) / 2 if (prev_active_start + prev_active_end) else 1
        prev_rate = round((prev_separations / prev_avg) * 100, 2)

        change = self.calculate_change(rate, prev_rate)

        return self.format_result(
            value=rate,
            label="Turnover Rate (%)",
            change=change,
            extra={
                "separations": separations,
                "average_headcount": avg_headcount,
                "previous_rate": prev_rate,
            },
        )

    # ── Task 69: Attendance Rate ─────────────────────────────────────

    def attendance_rate(self, period: str = "month") -> dict:
        """Attendance rate for the period."""
        from apps.attendance.models import AttendanceRecord

        start, end = self.get_date_range(period)

        records = AttendanceRecord.objects.filter(
            date__gte=start,
            date__lte=end,
            is_deleted=False,
        )
        total = records.count()
        present = records.filter(
            status__in=[ATTENDANCE_STATUS_PRESENT, "late", "half_day"]
        ).count()

        rate = round((present / total) * 100, 2) if total else Decimal("0")

        # Today's snapshot
        today = timezone.localdate()
        today_records = AttendanceRecord.objects.filter(
            date=today, is_deleted=False
        )
        today_total = today_records.count()
        today_present = today_records.filter(
            status__in=[ATTENDANCE_STATUS_PRESENT, "late", "half_day"]
        ).count()
        today_rate = round((today_present / today_total) * 100, 2) if today_total else 0

        return self.format_result(
            value=rate,
            label="Attendance Rate (%)",
            extra={
                "total_records": total,
                "present_count": present,
                "absent_count": total - present,
                "today_rate": today_rate,
                "today_present": today_present,
                "today_total": today_total,
            },
        )

    # ── Task 70: Leave Balance Summary ───────────────────────────────

    def leave_balance_summary(self, period: str = "month") -> dict:
        """Summary of leave balances across all active employees."""
        from apps.leave.models import LeaveBalance

        current_year = timezone.localdate().year
        active_employees = self._get_active_employees()

        balances = LeaveBalance.objects.filter(
            employee__in=active_employees,
            year=current_year,
            is_deleted=False,
            is_active=True,
        )

        summary = list(
            balances.values("leave_type__name")
            .annotate(
                total_allocated=Coalesce(
                    Sum("allocated_days"), Decimal("0"), output_field=DecimalField()
                ),
                total_used=Coalesce(
                    Sum("used_days"), Decimal("0"), output_field=DecimalField()
                ),
                total_pending=Coalesce(
                    Sum("pending_days"), Decimal("0"), output_field=DecimalField()
                ),
            )
            .order_by("leave_type__name")
        )

        total_allocated = sum(r["total_allocated"] for r in summary)
        total_used = sum(r["total_used"] for r in summary)

        return self.format_result(
            value=float(total_allocated - total_used),
            label="Total Remaining Leave Days",
            extra={
                "total_allocated": float(total_allocated),
                "total_used": float(total_used),
                "by_type": [
                    {
                        "leave_type": r["leave_type__name"] or "Unknown",
                        "allocated": float(r["total_allocated"]),
                        "used": float(r["total_used"]),
                        "pending": float(r["total_pending"]),
                        "remaining": float(
                            r["total_allocated"] - r["total_used"]
                        ),
                    }
                    for r in summary
                ],
            },
        )

    # ── Task 71: Pending Leave Requests ──────────────────────────────

    def pending_leave_requests(self, period: str = "month") -> dict:
        """Count of pending leave requests awaiting approval."""
        from apps.leave.models import LeaveRequest

        pending = LeaveRequest.objects.filter(
            status=LeaveRequestStatus.PENDING,
            is_deleted=False,
        )
        total_pending = pending.count()

        by_type = list(
            pending.values("leave_type__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        oldest = pending.order_by("submitted_at").first()
        oldest_days = None
        if oldest and oldest.submitted_at:
            oldest_days = (timezone.now() - oldest.submitted_at).days

        return self.format_result(
            value=total_pending,
            label="Pending Leave Requests",
            extra={
                "by_type": [
                    {"leave_type": r["leave_type__name"], "count": r["count"]}
                    for r in by_type
                ],
                "oldest_pending_days": oldest_days,
            },
        )

    # ── Task 72: Payroll Cost ────────────────────────────────────────

    def payroll_cost(self, period: str = "month") -> dict:
        """Total payroll cost for the period including statutory contributions."""
        from apps.payroll.models import EmployeePayroll

        start, end = self.get_date_range(period)
        prev_start, prev_end = self.get_previous_date_range(period)

        qs = EmployeePayroll.objects.filter(
            payroll_run__payroll_period__start_date__gte=start,
            payroll_run__payroll_period__end_date__lte=end,
        )

        agg = qs.aggregate(
            total_gross=Coalesce(
                Sum("gross_salary"), Decimal("0"), output_field=DecimalField()
            ),
            total_net=Coalesce(
                Sum("net_salary"), Decimal("0"), output_field=DecimalField()
            ),
            total_epf_employer=Coalesce(
                Sum("epf_employer"), Decimal("0"), output_field=DecimalField()
            ),
            total_etf=Coalesce(
                Sum("etf"), Decimal("0"), output_field=DecimalField()
            ),
            total_deductions=Coalesce(
                Sum("total_deductions"), Decimal("0"), output_field=DecimalField()
            ),
            avg_gross=Coalesce(
                Avg("gross_salary"), Decimal("0"), output_field=DecimalField()
            ),
            employee_count=Count("employee", distinct=True),
        )

        # Total cost to company = gross + employer EPF + ETF
        total_cost = (
            agg["total_gross"] + agg["total_epf_employer"] + agg["total_etf"]
        )

        # Previous period
        prev_qs = EmployeePayroll.objects.filter(
            payroll_run__payroll_period__start_date__gte=prev_start,
            payroll_run__payroll_period__end_date__lte=prev_end,
        )
        prev_total = prev_qs.aggregate(
            total=Coalesce(
                Sum("gross_salary"), Decimal("0"), output_field=DecimalField()
            )
        )["total"]

        change = self.calculate_change(float(total_cost), float(prev_total))

        return self.format_result(
            value=float(total_cost),
            label="Total Payroll Cost",
            change=change,
            extra={
                "gross_salary": float(agg["total_gross"]),
                "net_salary": float(agg["total_net"]),
                "employer_epf": float(agg["total_epf_employer"]),
                "employer_etf": float(agg["total_etf"]),
                "total_deductions": float(agg["total_deductions"]),
                "average_gross": float(agg["avg_gross"]),
                "employee_count": agg["employee_count"],
            },
        )

    # ── Task 73: Department Headcount ────────────────────────────────

    def department_headcount(self, period: str = "month") -> dict:
        """Headcount breakdown by department."""
        qs = self._get_active_employees()

        by_dept = list(
            qs.values("department__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return self.format_result(
            value=qs.count(),
            label="Department Headcount",
            extra={
                "departments": [
                    {
                        "name": r["department__name"] or "Unassigned",
                        "count": r["count"],
                    }
                    for r in by_dept
                ],
            },
        )

    # ── Task 74: Gender Ratio ────────────────────────────────────────

    def employee_gender_ratio(self, period: str = "month") -> dict:
        """Employee gender distribution."""
        qs = self._get_active_employees()
        total = qs.count()

        by_gender = list(
            qs.values("gender").annotate(count=Count("id")).order_by("-count")
        )

        return self.format_result(
            value=total,
            label="Employee Gender Distribution",
            extra={
                "distribution": [
                    {
                        "gender": r["gender"] or "Not Specified",
                        "count": r["count"],
                        "percentage": round(
                            (r["count"] / total) * 100, 1
                        ) if total else 0,
                    }
                    for r in by_gender
                ],
            },
        )

    # ── Overtime Summary ─────────────────────────────────────────────

    def overtime_summary(self, period: str = "month") -> dict:
        """Overtime hours summary for the period."""
        from apps.attendance.models import AttendanceRecord

        start, end = self.get_date_range(period)

        records = AttendanceRecord.objects.filter(
            date__gte=start,
            date__lte=end,
            is_deleted=False,
            overtime_hours__gt=0,
        )

        agg = records.aggregate(
            total_hours=Coalesce(
                Sum("overtime_hours"), Decimal("0"), output_field=DecimalField()
            ),
            avg_hours=Coalesce(
                Avg("overtime_hours"), Decimal("0"), output_field=DecimalField()
            ),
            employee_count=Count("employee", distinct=True),
        )

        return self.format_result(
            value=float(agg["total_hours"]),
            label="Total Overtime Hours",
            extra={
                "average_per_record": float(agg["avg_hours"]),
                "employees_with_ot": agg["employee_count"],
            },
        )
