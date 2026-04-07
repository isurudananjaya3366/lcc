"""Payroll integration service for attendance-based compensation calculations."""

import logging
from calendar import monthrange
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.attendance.constants import (
    ATTENDANCE_STATUS_HALF_DAY,
    ATTENDANCE_STATUS_LATE,
    ATTENDANCE_STATUS_PRESENT,
    DEFAULT_OVERTIME_MULTIPLIER,
)

logger = logging.getLogger(__name__)


class PayrollService:
    """Computes attendance-derived payroll components."""

    @classmethod
    def calculate_employee_payroll(cls, employee, year, month):
        """Calculate payroll-relevant attendance data for a single employee.

        Returns:
            dict with present_days, late_deduction_minutes, overtime_pay_hours,
            half_day_count, gross_attendance_factor, etc.
        """
        from apps.attendance.models import AttendanceRecord

        _, days_in_month = monthrange(year, month)
        start = timezone.datetime(year, month, 1).date()
        end = timezone.datetime(year, month, days_in_month).date()

        records = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=start,
            date__lte=end,
            is_deleted=False,
        )

        agg = records.aggregate(
            present=Count("id", filter=Q(status__in=[ATTENDANCE_STATUS_PRESENT, ATTENDANCE_STATUS_LATE])),
            half_days=Count("id", filter=Q(status=ATTENDANCE_STATUS_HALF_DAY)),
            total_hours=Sum("effective_hours"),
            overtime_hours=Sum("overtime_hours"),
            late_minutes=Sum("late_minutes"),
        )

        present = agg["present"] or 0
        half_days = agg["half_days"] or 0
        effective_days = present + (half_days * Decimal("0.5"))
        overtime_hours = Decimal(str(agg["overtime_hours"] or 0))
        overtime_pay_hours = overtime_hours * Decimal(str(DEFAULT_OVERTIME_MULTIPLIER))

        return {
            "employee_id": employee.employee_id,
            "employee_name": str(employee),
            "year": year,
            "month": month,
            "working_days": days_in_month,
            "present_days": present,
            "half_days": half_days,
            "effective_days": float(effective_days),
            "total_work_hours": float(agg["total_hours"] or 0),
            "overtime_hours": float(overtime_hours),
            "overtime_pay_hours": float(overtime_pay_hours),
            "total_late_minutes": agg["late_minutes"] or 0,
            "gross_attendance_factor": round(float(effective_days / days_in_month), 4) if days_in_month else 0,
        }

    @classmethod
    def generate_payroll_batch(cls, year, month, department=None):
        """Generate payroll data for all active employees.

        Args:
            year: Payroll year.
            month: Payroll month.
            department: Optional department filter.

        Returns:
            dict with summary and per-employee payroll data.
        """
        from apps.employees.models import Employee

        employees = Employee.objects.filter(is_deleted=False, status="active")
        if department:
            employees = employees.filter(department=department)

        results = []
        totals = {
            "total_present_days": 0,
            "total_overtime_hours": Decimal("0"),
            "total_late_minutes": 0,
        }

        for emp in employees:
            data = cls.calculate_employee_payroll(emp, year, month)
            results.append(data)
            totals["total_present_days"] += data["present_days"]
            totals["total_overtime_hours"] += Decimal(str(data["overtime_hours"]))
            totals["total_late_minutes"] += data["total_late_minutes"]

        return {
            "year": year,
            "month": month,
            "employee_count": len(results),
            "totals": {
                "total_present_days": totals["total_present_days"],
                "total_overtime_hours": float(totals["total_overtime_hours"]),
                "total_late_minutes": totals["total_late_minutes"],
            },
            "employees": results,
        }

    @classmethod
    def get_overtime_cost_estimate(cls, year, month, hourly_rate, department=None):
        """Estimate overtime cost for budget planning.

        Args:
            hourly_rate: Base hourly rate for overtime calculation.

        Returns:
            dict with total overtime hours and estimated cost.
        """
        batch = cls.generate_payroll_batch(year, month, department=department)
        total_ot_pay_hours = sum(
            emp["overtime_pay_hours"] for emp in batch["employees"]
        )
        estimated_cost = Decimal(str(total_ot_pay_hours)) * Decimal(str(hourly_rate))

        return {
            "year": year,
            "month": month,
            "total_overtime_pay_hours": total_ot_pay_hours,
            "hourly_rate": float(hourly_rate),
            "estimated_cost": float(estimated_cost),
        }
