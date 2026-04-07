"""Leave Report Service for the Leave Management app.

Provides comprehensive leave reporting: balance summaries,
leave history, department reports, leave type usage,
pending approvals, and expiring leave reports.
"""

import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from apps.leave.constants import LeaveRequestStatus
from apps.leave.models.leave_balance import LeaveBalance
from apps.leave.models.leave_request import LeaveRequest
from apps.leave.models.leave_type import LeaveType

logger = logging.getLogger(__name__)


class LeaveReportService:
    """Service class for generating leave reports."""

    def __init__(self, tenant=None):
        self.tenant = tenant

    # ── Private Helpers ──────────────────────────────────────

    def _get_employee_queryset(self):
        from apps.employees.models import Employee

        return Employee.objects.filter(
            is_active=True,
            is_deleted=False,
        ).select_related("user", "department")

    def _get_leave_request_queryset(self):
        return LeaveRequest.objects.filter(
            is_deleted=False,
        ).select_related("employee", "leave_type", "approved_by")

    def _get_leave_balance_queryset(self):
        return LeaveBalance.objects.filter(
            is_active=True,
        ).select_related("employee", "leave_type")

    @staticmethod
    def _validate_date_range(start_date, end_date):
        if end_date < start_date:
            raise ValueError("End date cannot be before start date.")
        return start_date, end_date

    @staticmethod
    def _get_year_date_range(year):
        return date(year, 1, 1), date(year, 12, 31)

    def _filter_by_date_range(self, queryset, start_date, end_date):
        return queryset.filter(
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

    # ── Balance Summary Report (Task 68) ─────────────────────

    def balance_summary(self, year, department_id=None, employee_id=None):
        """Generate balance summary report for a given year."""
        now = timezone.now()
        balances = self._get_leave_balance_queryset().filter(year=year)

        if employee_id:
            balances = balances.filter(employee_id=employee_id)
        if department_id:
            balances = balances.filter(employee__department_id=department_id)

        # Group by employee
        employee_data = {}
        for bal in balances.select_related("employee__user", "employee__department", "leave_type"):
            emp_id = str(bal.employee_id)
            if emp_id not in employee_data:
                emp = bal.employee
                employee_data[emp_id] = {
                    "employee_id": emp_id,
                    "employee_code": getattr(emp, "employee_code", ""),
                    "name": self._format_name(emp),
                    "department": str(emp.department.name) if emp.department else "",
                    "position": getattr(emp, "designation_name", ""),
                    "balances": [],
                    "total_allocated": Decimal("0"),
                    "total_used": Decimal("0"),
                    "total_pending": Decimal("0"),
                    "total_available": Decimal("0"),
                }

            allocated = bal.allocated_days + bal.carried_from_previous
            used = bal.used_days
            pending = bal.pending_days
            available = bal.available_days
            utilization = float(used / allocated * 100) if allocated else 0

            employee_data[emp_id]["balances"].append({
                "leave_type_id": str(bal.leave_type_id),
                "leave_type_name": bal.leave_type.name,
                "allocated": allocated,
                "used": used,
                "pending": pending,
                "available": available,
                "utilization_percentage": round(utilization, 1),
            })
            employee_data[emp_id]["total_allocated"] += allocated
            employee_data[emp_id]["total_used"] += used
            employee_data[emp_id]["total_pending"] += pending
            employee_data[emp_id]["total_available"] += available

        employees_list = list(employee_data.values())
        for emp in employees_list:
            total_alloc = emp["total_allocated"]
            emp["overall_utilization"] = (
                round(float(emp["total_used"] / total_alloc * 100), 1)
                if total_alloc
                else 0
            )

        # Aggregate statistics
        total_alloc = sum(e["total_allocated"] for e in employees_list)
        total_used = sum(e["total_used"] for e in employees_list)
        total_pending = sum(e["total_pending"] for e in employees_list)
        total_avail = sum(e["total_available"] for e in employees_list)

        return {
            "report_type": "balance_summary",
            "year": year,
            "generated_at": now.isoformat(),
            "filters": {"department_id": department_id},
            "employees": employees_list,
            "aggregate_statistics": {
                "total_employees": len(employees_list),
                "total_allocated_days": total_alloc,
                "total_used_days": total_used,
                "total_pending_days": total_pending,
                "total_available_days": total_avail,
                "average_utilization_percentage": (
                    round(float(total_used / total_alloc * 100), 1)
                    if total_alloc
                    else 0
                ),
            },
        }

    # ── Leave History Report (Task 69) ───────────────────────

    def leave_history(
        self, employee_id, start_date=None, end_date=None,
        status_filter=None, leave_type_filter=None
    ):
        """Generate leave history report for an employee."""
        from apps.employees.models import Employee

        now = timezone.now()
        employee = Employee.objects.select_related("user", "department").get(
            id=employee_id
        )

        if not start_date or not end_date:
            year = now.year
            start_date, end_date = self._get_year_date_range(year)

        qs = self._get_leave_request_queryset().filter(
            employee_id=employee_id,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if status_filter:
            qs = qs.filter(status__in=status_filter)
        if leave_type_filter:
            qs = qs.filter(leave_type_id=leave_type_filter)

        qs = qs.order_by("-start_date")

        requests = []
        total_days_requested = Decimal("0")
        total_days_approved = Decimal("0")
        by_type = {}
        by_status = {}

        for lr in qs:
            requests.append({
                "request_id": str(lr.id),
                "leave_type": {
                    "id": str(lr.leave_type_id),
                    "name": lr.leave_type.name,
                    "code": lr.leave_type.code,
                },
                "dates": {
                    "start_date": lr.start_date.isoformat(),
                    "end_date": lr.end_date.isoformat(),
                    "total_days": str(lr.total_days),
                },
                "status": {
                    "code": lr.status,
                    "display": lr.get_status_display(),
                    "date": (
                        lr.approved_at.isoformat() if lr.approved_at else
                        lr.submitted_at.isoformat() if lr.submitted_at else ""
                    ),
                },
                "approval": {
                    "approver_name": str(lr.approved_by) if lr.approved_by else None,
                    "approval_date": lr.approved_at.isoformat() if lr.approved_at else None,
                },
                "application": {
                    "applied_date": lr.submitted_at.isoformat() if lr.submitted_at else "",
                    "reason": lr.reason,
                },
            })

            total_days_requested += lr.total_days
            if lr.status == LeaveRequestStatus.APPROVED:
                total_days_approved += lr.total_days

            type_name = lr.leave_type.name
            by_type.setdefault(type_name, {"requests": 0, "days": Decimal("0")})
            by_type[type_name]["requests"] += 1
            by_type[type_name]["days"] += lr.total_days

            by_status.setdefault(lr.status, {"requests": 0, "days": Decimal("0")})
            by_status[lr.status]["requests"] += 1
            by_status[lr.status]["days"] += lr.total_days

        return {
            "report_type": "leave_history",
            "employee": {
                "employee_id": str(employee.id),
                "name": self._format_name(employee),
                "department": str(employee.department.name) if employee.department else "",
            },
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "generated_at": now.isoformat(),
            "requests": requests,
            "summary": {
                "total_requests": len(requests),
                "total_days_requested": str(total_days_requested),
                "total_days_approved": str(total_days_approved),
                "by_leave_type": {
                    k: {"requests": v["requests"], "days": str(v["days"])}
                    for k, v in by_type.items()
                },
                "by_status": {
                    k: {"requests": v["requests"], "days": str(v["days"])}
                    for k, v in by_status.items()
                },
            },
        }

    # ── Department Leave Report (Task 70) ────────────────────

    def department_report(
        self, department_id, start_date, end_date, include_details=True
    ):
        """Generate department leave report."""
        from apps.employees.models import Employee
        from apps.organization.models import Department

        now = timezone.now()
        self._validate_date_range(start_date, end_date)

        dept = Department.objects.get(id=department_id)
        employees = Employee.objects.filter(
            department_id=department_id,
            is_active=True,
            is_deleted=False,
        ).select_related("user")

        emp_ids = list(employees.values_list("id", flat=True))

        leave_qs = self._get_leave_request_queryset().filter(
            employee_id__in=emp_ids,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        approved_qs = leave_qs.filter(status=LeaveRequestStatus.APPROVED)

        total_leave_days = approved_qs.aggregate(
            total=Sum("total_days")
        )["total"] or Decimal("0")

        total_emp = len(emp_ids)
        avg_per_emp = float(total_leave_days / total_emp) if total_emp else 0

        # By leave type
        by_type = {}
        for lr in approved_qs.select_related("leave_type"):
            t = lr.leave_type.name
            by_type.setdefault(t, {"requests": 0, "total_days": Decimal("0")})
            by_type[t]["requests"] += 1
            by_type[t]["total_days"] += lr.total_days

        result = {
            "report_type": "department_leave",
            "department": {
                "department_id": str(dept.id),
                "name": dept.name,
                "total_employees": total_emp,
            },
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "generated_at": now.isoformat(),
            "summary": {
                "total_leave_days": str(total_leave_days),
                "average_per_employee": round(avg_per_emp, 1),
                "employees_on_leave_count": approved_qs.values("employee").distinct().count(),
            },
            "by_leave_type": {
                k: {"requests": v["requests"], "total_days": str(v["total_days"])}
                for k, v in by_type.items()
            },
        }

        if include_details:
            detail_list = []
            for emp in employees:
                emp_leaves = approved_qs.filter(employee=emp)
                total = emp_leaves.aggregate(t=Sum("total_days"))["t"] or Decimal("0")
                detail_list.append({
                    "employee_id": str(emp.id),
                    "name": self._format_name(emp),
                    "total_days_taken": str(total),
                    "requests_count": emp_leaves.count(),
                })
            result["employee_details"] = detail_list

        return result

    # ── Leave Type Usage Report (Task 71) ────────────────────

    def leave_type_usage(
        self, leave_type_id, start_date, end_date, department_id=None
    ):
        """Generate leave type usage report."""
        now = timezone.now()
        self._validate_date_range(start_date, end_date)

        lt = LeaveType.objects.get(id=leave_type_id)

        qs = self._get_leave_request_queryset().filter(
            leave_type_id=leave_type_id,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )
        if department_id:
            qs = qs.filter(employee__department_id=department_id)

        total = qs.count()
        approved = qs.filter(status=LeaveRequestStatus.APPROVED)
        rejected = qs.filter(status=LeaveRequestStatus.REJECTED)
        pending = qs.filter(status=LeaveRequestStatus.PENDING)

        approved_days = approved.aggregate(t=Sum("total_days"))["t"] or Decimal("0")
        rejected_days = rejected.aggregate(t=Sum("total_days"))["t"] or Decimal("0")
        pending_days = pending.aggregate(t=Sum("total_days"))["t"] or Decimal("0")
        total_days = qs.aggregate(t=Sum("total_days"))["t"] or Decimal("0")

        approval_rate = round(approved.count() / total * 100, 1) if total else 0
        rejection_rate = round(rejected.count() / total * 100, 1) if total else 0

        # Duration distribution
        one_day = qs.filter(total_days=1).count()
        short = qs.filter(total_days__gte=2, total_days__lte=3).count()
        medium = qs.filter(total_days__gte=4, total_days__lte=7).count()
        long = qs.filter(total_days__gte=8).count()

        half_day_count = qs.filter(is_half_day=True).count()

        return {
            "report_type": "leave_type_usage",
            "leave_type": {
                "leave_type_id": str(lt.id),
                "name": lt.name,
                "code": lt.code,
                "is_paid": lt.is_paid,
            },
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "generated_at": now.isoformat(),
            "usage_statistics": {
                "total_requests": total,
                "total_days_requested": str(total_days),
                "total_days_approved": str(approved_days),
                "total_days_rejected": str(rejected_days),
                "total_days_pending": str(pending_days),
            },
            "approval_metrics": {
                "approval_rate": approval_rate,
                "rejection_rate": rejection_rate,
            },
            "request_patterns": {
                "duration_distribution": {
                    "1_day": {"count": one_day, "percentage": round(one_day / total * 100, 1) if total else 0},
                    "2_3_days": {"count": short, "percentage": round(short / total * 100, 1) if total else 0},
                    "4_7_days": {"count": medium, "percentage": round(medium / total * 100, 1) if total else 0},
                    "8_plus_days": {"count": long, "percentage": round(long / total * 100, 1) if total else 0},
                },
                "half_day_requests": {
                    "count": half_day_count,
                    "percentage": round(half_day_count / total * 100, 1) if total else 0,
                },
            },
        }

    # ── Pending Approvals Report (Task 72) ───────────────────

    def pending_approvals(
        self, manager_id=None, department_id=None,
        priority_filter=None, sort_by="urgency"
    ):
        """Generate pending approvals report."""
        now = timezone.now()
        today = now.date()

        qs = self._get_leave_request_queryset().filter(
            status=LeaveRequestStatus.PENDING,
        )

        if manager_id:
            from apps.employees.models import Employee
            team_ids = Employee.objects.filter(
                reporting_manager_id=manager_id,
                is_active=True,
                is_deleted=False,
            ).values_list("id", flat=True)
            qs = qs.filter(employee_id__in=team_ids)

        if department_id:
            qs = qs.filter(employee__department_id=department_id)

        pending_items = []
        for lr in qs.select_related("employee__user", "employee__department", "leave_type"):
            days_pending = (today - lr.submitted_at.date()).days if lr.submitted_at else 0
            days_until_start = (lr.start_date - today).days

            # Calculate priority score
            score = 50
            if days_pending > 5:
                score += 50
            if days_until_start <= 0:
                score += 45
            elif days_until_start <= 3:
                score += max(0, 30 - days_until_start * 10)
            score += min(days_pending * 5, 20)
            score = min(score, 100)

            if days_pending > 5 or days_until_start <= 0:
                urgency = "OVERDUE"
            elif days_until_start <= 3:
                urgency = "URGENT"
            elif days_until_start <= 7:
                urgency = "HIGH"
            else:
                urgency = "NORMAL"

            alerts = []
            if days_pending > 5:
                alerts.append(f"Pending for {days_pending} days — SLA breach.")
            if days_until_start <= 0:
                alerts.append("Leave start date has passed.")
            elif days_until_start <= 3:
                alerts.append(f"Leave starts in {days_until_start} day(s).")

            item = {
                "request_id": str(lr.id),
                "urgency_level": urgency,
                "priority_score": score,
                "employee": {
                    "employee_id": str(lr.employee_id),
                    "name": self._format_name(lr.employee),
                    "department": str(lr.employee.department.name) if lr.employee.department else "",
                },
                "leave_type": {
                    "id": str(lr.leave_type_id),
                    "name": lr.leave_type.name,
                    "code": lr.leave_type.code,
                },
                "dates": {
                    "start_date": lr.start_date.isoformat(),
                    "end_date": lr.end_date.isoformat(),
                    "total_days": str(lr.total_days),
                },
                "timeline": {
                    "applied_date": lr.submitted_at.isoformat() if lr.submitted_at else "",
                    "days_pending": days_pending,
                    "days_until_start": days_until_start,
                    "sla_breach": days_pending > 5,
                },
                "reason": lr.reason,
                "alerts": alerts,
            }
            pending_items.append(item)

        if priority_filter == "urgent":
            pending_items = [p for p in pending_items if p["urgency_level"] in ("OVERDUE", "URGENT")]
        elif priority_filter == "normal":
            pending_items = [p for p in pending_items if p["urgency_level"] == "NORMAL"]

        if sort_by == "urgency":
            pending_items.sort(key=lambda x: -x["priority_score"])
        elif sort_by == "start_date":
            pending_items.sort(key=lambda x: x["dates"]["start_date"])
        elif sort_by == "submitted_date":
            pending_items.sort(key=lambda x: x["timeline"]["applied_date"])

        urgent_count = sum(1 for p in pending_items if p["urgency_level"] in ("OVERDUE", "URGENT"))
        overdue_count = sum(1 for p in pending_items if p["urgency_level"] == "OVERDUE")

        return {
            "report_type": "pending_approvals",
            "generated_at": now.isoformat(),
            "summary": {
                "total_pending": len(pending_items),
                "urgent_count": urgent_count,
                "overdue_count": overdue_count,
            },
            "pending_requests": pending_items,
        }

    # ── Expiring Leaves Report (Task 73) ─────────────────────

    def expiring_leaves(
        self, days_until_expiry=30, department_id=None,
        leave_type_id=None, min_days_expiring=1
    ):
        """Generate report of expiring leave balances."""
        now = timezone.now()
        today = now.date()
        threshold_date = today + timedelta(days=days_until_expiry)

        balances = self._get_leave_balance_queryset().filter(
            carry_forward_expiry__isnull=False,
            carry_forward_expiry__lte=threshold_date,
            carry_forward_expiry__gte=today,
        ).select_related("employee__user", "employee__department", "leave_type")

        if department_id:
            balances = balances.filter(employee__department_id=department_id)
        if leave_type_id:
            balances = balances.filter(leave_type_id=leave_type_id)

        items = []
        for bal in balances:
            days_at_risk = bal.get_expired_carry_forward_days()
            if days_at_risk < min_days_expiring:
                continue

            days_left = (bal.carry_forward_expiry - today).days
            if days_left <= 7:
                urgency = "CRITICAL"
            elif days_left <= 14:
                urgency = "HIGH"
            elif days_left <= 30:
                urgency = "MEDIUM"
            else:
                urgency = "LOW"

            items.append({
                "urgency_level": urgency,
                "employee": {
                    "employee_id": str(bal.employee_id),
                    "name": self._format_name(bal.employee),
                    "department": str(bal.employee.department.name) if bal.employee.department else "",
                },
                "leave_type": {
                    "id": str(bal.leave_type_id),
                    "name": bal.leave_type.name,
                    "code": bal.leave_type.code,
                },
                "balance": {
                    "allocated_days": str(bal.allocated_days),
                    "used_days": str(bal.used_days),
                    "available_days": str(bal.available_days),
                },
                "expiry": {
                    "expiry_date": bal.carry_forward_expiry.isoformat(),
                    "days_until_expiry": days_left,
                    "days_at_risk": str(days_at_risk),
                },
            })

        items.sort(key=lambda x: x["expiry"]["days_until_expiry"])

        return {
            "report_type": "expiring_leaves",
            "generated_at": now.isoformat(),
            "threshold": {
                "days": days_until_expiry,
                "threshold_date": threshold_date.isoformat(),
            },
            "summary": {
                "total_employees_affected": len(items),
                "total_days_at_risk": str(sum(
                    Decimal(i["expiry"]["days_at_risk"]) for i in items
                )),
            },
            "expiring_balances": items,
        }

    # ── Helper ───────────────────────────────────────────────

    @staticmethod
    def _format_name(employee):
        user = getattr(employee, "user", None)
        if user:
            first = getattr(user, "first_name", "")
            last = getattr(user, "last_name", "")
            if first or last:
                return f"{first} {last}".strip()
            return str(user.email)
        return str(employee)
