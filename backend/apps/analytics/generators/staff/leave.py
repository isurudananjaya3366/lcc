"""
Staff leave utilization report generator.

Analyses leave balances, utilization rates, patterns,
and flags anomalies per employee/department.
"""

from datetime import date
from decimal import Decimal
from typing import Any

from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.query import QuerySet

from apps.analytics.generators.base import BaseReportGenerator


class LeaveReport(BaseReportGenerator):
    """Leave utilization and balance analysis per employee."""

    REPORT_TYPE = "STAFF_LEAVE"

    def get_base_queryset(self) -> QuerySet:
        from apps.leave.models import LeaveBalance

        year = int(self.get_filter_value("year", date.today().year))
        qs = LeaveBalance.objects.filter(
            is_deleted=False,
            is_active=True,
            year=year,
        )

        employee_id = self.get_filter_value("employee_id")
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        department_id = self.get_filter_value("department_id")
        if department_id:
            qs = qs.filter(employee__department_id=department_id)

        leave_type_id = self.get_filter_value("leave_type_id")
        if leave_type_id:
            qs = qs.filter(leave_type_id=leave_type_id)

        return qs

    # ── Generate ──────────────────────────────────────────────────

    def generate(self) -> dict[str, Any]:
        self.start_timer()
        qs = self.get_base_queryset()
        year = int(self.get_filter_value("year", date.today().year))

        # Group by employee
        employee_balances = (
            qs.values(
                "employee_id",
                "employee__employee_id",
                "employee__first_name",
                "employee__last_name",
                "employee__department__name",
            )
            .annotate(
                total_allocated=Sum("allocated_days"),
                total_used=Sum("used_days"),
                total_pending=Sum("pending_days"),
                total_carried=Sum("carried_from_previous"),
                total_encashed=Sum("encashed_days"),
            )
            .order_by("employee__first_name")
        )

        data: list[dict[str, Any]] = []
        for row in employee_balances:
            allocated = float(row["total_allocated"] or 0)
            used = float(row["total_used"] or 0)
            pending = float(row["total_pending"] or 0)
            balance = round(allocated - used - pending, 2)
            utilization = (
                round(used / allocated * 100, 2) if allocated else 0
            )

            # Utilization category
            if utilization > 100:
                category = "Over-utilized"
            elif utilization > 90:
                category = "Critical"
            elif utilization > 70:
                category = "High"
            elif utilization >= 30:
                category = "Normal"
            else:
                category = "Under-utilized"

            # Per-type breakdown for this employee
            type_breakdown = list(
                qs.filter(employee_id=row["employee_id"])
                .values(
                    "leave_type__name",
                    "allocated_days",
                    "used_days",
                    "pending_days",
                    "carried_from_previous",
                )
                .order_by("leave_type__name")
            )
            types: list[dict[str, Any]] = []
            for t in type_breakdown:
                t_alloc = float(t["allocated_days"] or 0)
                t_used = float(t["used_days"] or 0)
                types.append(
                    {
                        "leave_type": t["leave_type__name"],
                        "allocated": t_alloc,
                        "used": t_used,
                        "pending": float(t["pending_days"] or 0),
                        "carried": float(t["carried_from_previous"] or 0),
                        "balance": round(t_alloc - t_used, 2),
                        "utilization": (
                            round(t_used / t_alloc * 100, 2)
                            if t_alloc
                            else 0
                        ),
                    }
                )

            data.append(
                {
                    "employee_pk": str(row["employee_id"]),
                    "employee_id": row["employee__employee_id"],
                    "employee_name": (
                        f"{row['employee__first_name']} "
                        f"{row['employee__last_name']}"
                    ).strip(),
                    "department": row["employee__department__name"] or "",
                    "total_allocated": allocated,
                    "total_used": used,
                    "total_pending": pending,
                    "total_carried": float(row["total_carried"] or 0),
                    "total_encashed": float(row["total_encashed"] or 0),
                    "balance": balance,
                    "utilization_rate": float(utilization),
                    "utilization_category": category,
                    "leave_types": types,
                }
            )

        # ── Pattern flags ─────────────────────────────────────────
        flags = self._detect_patterns(year)

        # ── Totals ────────────────────────────────────────────────
        totals = {
            "total_employees": len(data),
            "total_allocated": round(sum(d["total_allocated"] for d in data), 2),
            "total_used": round(sum(d["total_used"] for d in data), 2),
            "total_pending": round(sum(d["total_pending"] for d in data), 2),
            "avg_utilization": (
                round(
                    sum(d["utilization_rate"] for d in data) / len(data), 2
                )
                if data
                else 0
            ),
            "pattern_flags": len(flags),
        }

        # Utilization category distribution
        cat_dist: dict[str, int] = {}
        for d in data:
            c = d["utilization_category"]
            cat_dist[c] = cat_dist.get(c, 0) + 1

        chart_data = {
            "utilization_distribution": cat_dist,
        }

        response = self.build_response(data, totals=totals, chart_data=chart_data)
        response["pattern_flags"] = flags
        return response

    # ── Pattern detection (Task 67) ──────────────────────────────

    def _detect_patterns(self, year: int) -> list[dict[str, Any]]:
        """Flag suspicious leave patterns."""
        from apps.leave.models import LeaveRequest

        flags: list[dict[str, Any]] = []
        approved_leaves = LeaveRequest.objects.filter(
            is_deleted=False,
            status="APPROVED",
            start_date__year=year,
        )

        # Frequent Friday/Monday leaves per employee
        from django.db.models.functions import ExtractWeekDay

        weekend_adjacent = (
            approved_leaves.annotate(dow=ExtractWeekDay("start_date"))
            .filter(dow__in=[2, 6])  # Monday=2, Friday=6 in Django
            .values("employee_id", "employee__first_name", "employee__last_name")
            .annotate(count=Count("id"))
            .filter(count__gt=4)
        )
        for row in weekend_adjacent:
            flags.append(
                {
                    "type": "frequent_monday_friday",
                    "employee_id": str(row["employee_id"]),
                    "employee_name": (
                        f"{row['employee__first_name']} "
                        f"{row['employee__last_name']}"
                    ).strip(),
                    "count": row["count"],
                    "description": (
                        f"Took {row['count']} Monday/Friday leaves"
                    ),
                }
            )

        # Excessive sick leave (>15 days/year)
        sick_heavy = (
            approved_leaves.filter(leave_type__name__icontains="sick")
            .values("employee_id", "employee__first_name", "employee__last_name")
            .annotate(total=Sum("total_days"))
            .filter(total__gt=15)
        )
        for row in sick_heavy:
            flags.append(
                {
                    "type": "excessive_sick_leave",
                    "employee_id": str(row["employee_id"]),
                    "employee_name": (
                        f"{row['employee__first_name']} "
                        f"{row['employee__last_name']}"
                    ).strip(),
                    "count": float(row["total"]),
                    "description": (
                        f"Used {float(row['total'])} sick leave days"
                    ),
                }
            )

        return flags
