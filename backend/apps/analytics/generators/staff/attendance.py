"""
Staff attendance report generator.

Analyses attendance rates, late arrivals, early departures,
and punctuality per employee/department.
"""

from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.query import QuerySet

from apps.analytics.generators.base import BaseReportGenerator


class AttendanceReport(BaseReportGenerator):
    """Attendance analytics with rate calculation and punctuality scoring."""

    REPORT_TYPE = "STAFF_ATTENDANCE"

    def get_base_queryset(self) -> QuerySet:
        from apps.attendance.models import AttendanceRecord

        qs = AttendanceRecord.objects.filter(is_deleted=False)
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

        return qs

    # ── Generate ──────────────────────────────────────────────────

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()

        # Group by employee
        employee_data = qs.values(
            "employee_id",
            "employee__employee_id",
            "employee__first_name",
            "employee__last_name",
            "employee__department__name",
        ).annotate(
            total_records=Count("id"),
            present_days=Count("id", filter=Q(status="present")),
            absent_days=Count("id", filter=Q(status="absent")),
            late_days=Count("id", filter=Q(status="late")),
            half_days=Count("id", filter=Q(status="half_day")),
            leave_days=Count("id", filter=Q(status="on_leave")),
            total_work_hours=Sum("work_hours"),
            total_effective_hours=Sum("effective_hours"),
            total_overtime_hours=Sum("overtime_hours"),
            total_late_minutes=Sum("late_minutes"),
            avg_late_minutes=Avg("late_minutes", filter=Q(late_minutes__gt=0)),
            total_early_departure_minutes=Sum("early_departure_minutes"),
            avg_early_departure=Avg(
                "early_departure_minutes",
                filter=Q(early_departure_minutes__gt=0),
            ),
        ).order_by(
            "employee__first_name",
        )

        data: list[dict[str, Any]] = []
        for row in employee_data:
            working_days = row["total_records"] - row["leave_days"]
            present = row["present_days"] + row["late_days"] + row["half_days"]
            attendance_rate = (
                round(present / working_days * 100, 2) if working_days else 0
            )
            punctuality_rate = (
                round(
                    (working_days - row["late_days"]) / working_days * 100, 2
                )
                if working_days
                else 0
            )

            # Rating
            if attendance_rate >= 95:
                rating = "Excellent"
            elif attendance_rate >= 90:
                rating = "Good"
            elif attendance_rate >= 85:
                rating = "Satisfactory"
            else:
                rating = "Needs Improvement"

            # Late severity breakdown
            late_qs = qs.filter(
                employee_id=row["employee_id"],
                late_minutes__gt=0,
            )
            minor_late = late_qs.filter(late_minutes__lte=15).count()
            moderate_late = late_qs.filter(
                late_minutes__gt=15, late_minutes__lte=30
            ).count()
            serious_late = late_qs.filter(
                late_minutes__gt=30, late_minutes__lte=60
            ).count()
            critical_late = late_qs.filter(late_minutes__gt=60).count()

            data.append(
                {
                    "employee_pk": str(row["employee_id"]),
                    "employee_id": row["employee__employee_id"],
                    "employee_name": (
                        f"{row['employee__first_name']} {row['employee__last_name']}"
                    ).strip(),
                    "department": row["employee__department__name"] or "",
                    "working_days": working_days,
                    "present_days": present,
                    "absent_days": row["absent_days"],
                    "late_days": row["late_days"],
                    "half_days": row["half_days"],
                    "leave_days": row["leave_days"],
                    "attendance_rate": float(attendance_rate),
                    "punctuality_rate": float(punctuality_rate),
                    "rating": rating,
                    "total_work_hours": float(row["total_work_hours"] or 0),
                    "total_effective_hours": float(
                        row["total_effective_hours"] or 0
                    ),
                    "total_overtime_hours": float(
                        row["total_overtime_hours"] or 0
                    ),
                    "total_late_minutes": row["total_late_minutes"] or 0,
                    "avg_late_minutes": round(
                        float(row["avg_late_minutes"] or 0), 1
                    ),
                    "total_early_departure_minutes": (
                        row["total_early_departure_minutes"] or 0
                    ),
                    "avg_early_departure_minutes": round(
                        float(row["avg_early_departure"] or 0), 1
                    ),
                    "late_severity": {
                        "minor": minor_late,
                        "moderate": moderate_late,
                        "serious": serious_late,
                        "critical": critical_late,
                    },
                }
            )

        # ── Aggregate totals ─────────────────────────────────────
        totals = {
            "total_employees": len(data),
            "avg_attendance_rate": (
                round(sum(d["attendance_rate"] for d in data) / len(data), 2)
                if data
                else 0
            ),
            "avg_punctuality_rate": (
                round(
                    sum(d["punctuality_rate"] for d in data) / len(data), 2
                )
                if data
                else 0
            ),
            "total_absent_days": sum(d["absent_days"] for d in data),
            "total_late_days": sum(d["late_days"] for d in data),
            "total_work_hours": round(
                sum(d["total_work_hours"] for d in data), 2
            ),
        }

        # Rating distribution for chart
        rating_dist: dict[str, int] = {}
        for d in data:
            r = d["rating"]
            rating_dist[r] = rating_dist.get(r, 0) + 1

        chart_data = {
            "rating_distribution": rating_dist,
        }

        return self.build_response(data, totals=totals, chart_data=chart_data)
