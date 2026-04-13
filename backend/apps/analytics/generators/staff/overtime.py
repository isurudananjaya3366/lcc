"""
Staff overtime report generator.

Tracks overtime hours and costs per employee/department with
Sri Lanka labour-law multipliers and compliance checks.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.functions import ExtractWeekDay, TruncMonth
from django.db.models.query import QuerySet

from apps.analytics.generators.base import BaseReportGenerator

# Sri Lanka overtime multipliers
OVERTIME_MULTIPLIERS = {
    "weekday": Decimal("1.5"),
    "weekend": Decimal("2.0"),
    "holiday": Decimal("2.5"),
}

# Default working parameters
WORKING_DAYS_PER_MONTH = 22
HOURS_PER_DAY = 8

# Compliance limits
DAILY_MAX_HOURS = 12
WEEKLY_MAX_HOURS = 60
MONTHLY_MAX_HOURS = 60


class OvertimeReport(BaseReportGenerator):
    """Overtime tracking with cost calculation and compliance checking."""

    REPORT_TYPE = "STAFF_OVERTIME"

    def get_base_queryset(self) -> QuerySet:
        from apps.attendance.models import OvertimeRequest

        qs = OvertimeRequest.objects.filter(is_deleted=False)
        qs = self.apply_date_filter(qs, date_field="date")

        employee_id = self.get_filter_value("employee_id")
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        department_id = self.get_filter_value("department_id")
        if department_id:
            qs = qs.filter(employee__department_id=department_id)

        status = self.get_filter_value("status")
        if status:
            qs = qs.filter(status=status)
        else:
            # Default: only approved overtime
            qs = qs.filter(status="approved")

        return qs

    # ── Generate ──────────────────────────────────────────────────

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()

        # Group by employee
        employee_data = (
            qs.values(
                "employee_id",
                "employee__employee_id",
                "employee__first_name",
                "employee__last_name",
                "employee__department__name",
            )
            .annotate(
                total_requests=Count("id"),
                total_planned_hours=Sum("planned_hours"),
                total_actual_hours=Sum("actual_hours"),
                avg_hours_per_request=Avg("actual_hours"),
            )
            .order_by("-total_actual_hours")
        )

        data: list[dict[str, Any]] = []
        total_cost = Decimal("0")

        for row in employee_data:
            emp_id = row["employee_id"]
            actual_hours = Decimal(str(row["total_actual_hours"] or 0))
            planned_hours = Decimal(str(row["total_planned_hours"] or 0))

            # Fetch salary for cost calculation
            hourly_rate = self._get_hourly_rate(emp_id)

            # Classify overtime by day type (weekend vs weekday)
            emp_qs = qs.filter(employee_id=emp_id)
            weekday_hours, weekend_hours = self._split_by_day_type(emp_qs)

            # Cost calculation
            weekday_cost = weekday_hours * hourly_rate * OVERTIME_MULTIPLIERS["weekday"]
            weekend_cost = weekend_hours * hourly_rate * OVERTIME_MULTIPLIERS["weekend"]
            emp_cost = round(weekday_cost + weekend_cost, 2)
            total_cost += emp_cost

            # Compliance checks
            violations = self._check_compliance(emp_qs, actual_hours)

            data.append(
                {
                    "employee_pk": str(emp_id),
                    "employee_id": row["employee__employee_id"],
                    "employee_name": (
                        f"{row['employee__first_name']} "
                        f"{row['employee__last_name']}"
                    ).strip(),
                    "department": row["employee__department__name"] or "",
                    "total_requests": row["total_requests"],
                    "total_planned_hours": float(planned_hours),
                    "total_actual_hours": float(actual_hours),
                    "avg_hours_per_request": round(
                        float(row["avg_hours_per_request"] or 0), 2
                    ),
                    "weekday_hours": float(weekday_hours),
                    "weekend_hours": float(weekend_hours),
                    "hourly_rate": float(hourly_rate),
                    "weekday_cost": float(weekday_cost),
                    "weekend_cost": float(weekend_cost),
                    "total_cost": float(emp_cost),
                    "compliance_violations": violations,
                }
            )

        # ── Monthly trend ─────────────────────────────────────────
        monthly = (
            qs.annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(
                hours=Sum("actual_hours"),
                requests=Count("id"),
            )
            .order_by("month")
        )
        trend = [
            {
                "period": row["month"].strftime("%Y-%m") if row["month"] else "",
                "hours": float(row["hours"] or 0),
                "requests": row["requests"],
            }
            for row in monthly
        ]

        # ── Totals ────────────────────────────────────────────────
        totals = {
            "total_employees": len(data),
            "total_requests": sum(d["total_requests"] for d in data),
            "total_actual_hours": round(
                sum(d["total_actual_hours"] for d in data), 2
            ),
            "total_cost": float(total_cost),
            "avg_hours_per_employee": (
                round(
                    sum(d["total_actual_hours"] for d in data) / len(data), 2
                )
                if data
                else 0
            ),
            "employees_with_violations": sum(
                1 for d in data if d["compliance_violations"]
            ),
        }

        chart_data = {
            "monthly_trend": trend,
            "top_5_overtime": [
                {
                    "employee_name": d["employee_name"],
                    "hours": d["total_actual_hours"],
                    "cost": d["total_cost"],
                }
                for d in data[:5]
            ],
        }

        return self.build_response(data, totals=totals, chart_data=chart_data)

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _get_hourly_rate(employee_id: Any) -> Decimal:
        """Return hourly rate from current salary or zero."""
        from apps.payroll.models import EmployeeSalary

        salary = (
            EmployeeSalary.objects.filter(
                employee_id=employee_id,
                is_current=True,
            )
            .first()
        )
        if not salary or not salary.basic_salary:
            return Decimal("0")
        return round(
            salary.basic_salary / (WORKING_DAYS_PER_MONTH * HOURS_PER_DAY), 2
        )

    @staticmethod
    def _split_by_day_type(qs: QuerySet) -> tuple[Decimal, Decimal]:
        """Split total actual hours into weekday vs weekend."""
        # Django ExtractWeekDay: Sunday=1, Saturday=7
        weekend = qs.filter(
            date__week_day__in=[1, 7],  # Sunday, Saturday
        ).aggregate(hours=Sum("actual_hours"))
        weekday = qs.exclude(
            date__week_day__in=[1, 7],
        ).aggregate(hours=Sum("actual_hours"))

        return (
            Decimal(str(weekday["hours"] or 0)),
            Decimal(str(weekend["hours"] or 0)),
        )

    @staticmethod
    def _check_compliance(
        qs: QuerySet, total_hours: Decimal
    ) -> list[dict[str, str]]:
        """Check overtime against Sri Lanka labour law limits."""
        violations: list[dict[str, str]] = []

        if float(total_hours) > MONTHLY_MAX_HOURS:
            violations.append(
                {
                    "type": "monthly_limit",
                    "description": (
                        f"Total {float(total_hours):.1f}h exceeds "
                        f"monthly limit of {MONTHLY_MAX_HOURS}h"
                    ),
                }
            )

        # Check individual days exceeding daily limit
        daily_over = (
            qs.filter(actual_hours__gt=DAILY_MAX_HOURS)
            .values_list("date", flat=True)
        )
        for d in daily_over:
            violations.append(
                {
                    "type": "daily_limit",
                    "description": (
                        f"Exceeded {DAILY_MAX_HOURS}h daily limit on {d}"
                    ),
                }
            )

        return violations
