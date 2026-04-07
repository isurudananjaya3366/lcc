"""Payroll Integration for Leave Management.

Provides leave data to the payroll system including
paid/unpaid breakdowns, deductions, and monthly exports.
"""

import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum

from apps.leave.constants import LeaveRequestStatus
from apps.leave.models.leave_request import LeaveRequest

logger = logging.getLogger(__name__)


class PayrollIntegration:
    """Integrates leave data with the payroll system."""

    def __init__(self, tenant=None):
        self.tenant = tenant

    # ── Core Methods ─────────────────────────────────────────

    def get_leave_data_for_payroll(self, employee_id, payroll_period):
        """Get approved leave data for payroll processing.

        Args:
            employee_id: UUID of the employee.
            payroll_period: Tuple of (start_date, end_date).

        Returns:
            Dict with leave summary, paid/unpaid breakdown, deductions.
        """
        start_date, end_date = payroll_period

        leaves = LeaveRequest.objects.filter(
            employee_id=employee_id,
            status=LeaveRequestStatus.APPROVED,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_deleted=False,
        ).select_related("leave_type")

        paid_days = self.calculate_paid_leave_days(leaves)
        unpaid_days = self.calculate_unpaid_leave_days(leaves)

        by_type = {}
        for lr in leaves:
            t = lr.leave_type.name
            by_type.setdefault(t, {
                "days": Decimal("0"),
                "is_paid": lr.leave_type.is_paid,
                "requests": 0,
            })
            by_type[t]["days"] += lr.total_days
            by_type[t]["requests"] += 1

        total_days = paid_days + unpaid_days

        return {
            "employee_id": str(employee_id),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "leave_summary": {
                "total_leave_days": str(total_days),
                "paid_leave_days": str(paid_days),
                "unpaid_leave_days": str(unpaid_days),
                "by_type": {
                    k: {
                        "days": str(v["days"]),
                        "is_paid": v["is_paid"],
                        "requests": v["requests"],
                    }
                    for k, v in by_type.items()
                },
            },
        }

    def calculate_paid_leave_days(self, leave_requests):
        """Calculate total paid leave days from a queryset.

        Args:
            leave_requests: QuerySet of LeaveRequest.

        Returns:
            Decimal total of paid leave days.
        """
        total = Decimal("0")
        for lr in leave_requests:
            if lr.leave_type.is_paid:
                total += lr.total_days
        return total

    def calculate_unpaid_leave_days(self, leave_requests):
        """Calculate total unpaid leave days from a queryset.

        Args:
            leave_requests: QuerySet of LeaveRequest.

        Returns:
            Decimal total of unpaid leave days.
        """
        total = Decimal("0")
        for lr in leave_requests:
            if not lr.leave_type.is_paid:
                total += lr.total_days
        return total

    def get_leave_summary_by_type(self, employee_id, period):
        """Get leave summary grouped by type for payroll.

        Args:
            employee_id: UUID of the employee.
            period: Tuple of (start_date, end_date).

        Returns:
            Dict grouped by leave type with paid/unpaid per type.
        """
        start_date, end_date = period
        leaves = LeaveRequest.objects.filter(
            employee_id=employee_id,
            status=LeaveRequestStatus.APPROVED,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_deleted=False,
        ).select_related("leave_type")

        summary = {}
        for lr in leaves:
            t = lr.leave_type.name
            summary.setdefault(t, {
                "total_days": Decimal("0"),
                "paid_days": Decimal("0"),
                "unpaid_days": Decimal("0"),
                "requests": 0,
            })
            summary[t]["total_days"] += lr.total_days
            summary[t]["requests"] += 1
            if lr.leave_type.is_paid:
                summary[t]["paid_days"] += lr.total_days
            else:
                summary[t]["unpaid_days"] += lr.total_days

        return {
            k: {key: str(val) if isinstance(val, Decimal) else val for key, val in v.items()}
            for k, v in summary.items()
        }

    def calculate_leave_deductions(self, employee_id, period):
        """Calculate salary deductions for unpaid leave.

        Args:
            employee_id: UUID of the employee.
            period: Tuple of (start_date, end_date).

        Returns:
            Decimal deduction amount (unpaid_days * daily_rate).
        """
        start_date, end_date = period
        leaves = LeaveRequest.objects.filter(
            employee_id=employee_id,
            status=LeaveRequestStatus.APPROVED,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_deleted=False,
        ).select_related("leave_type")

        unpaid_days = self.calculate_unpaid_leave_days(leaves)
        daily_rate = self._get_employee_daily_rate(employee_id, period)

        return unpaid_days * daily_rate

    def get_leave_balance_snapshot(self, employee_id, snapshot_date):
        """Get leave balance at a specific date.

        Args:
            employee_id: UUID of the employee.
            snapshot_date: Date for the snapshot.

        Returns:
            Dict with balance details per leave type.
        """
        from apps.leave.models.leave_balance import LeaveBalance

        year = snapshot_date.year
        balances = LeaveBalance.objects.filter(
            employee_id=employee_id,
            year=year,
            is_active=True,
        ).select_related("leave_type")

        result = {}
        for bal in balances:
            result[bal.leave_type.name] = {
                "allocated": str(bal.allocated_days),
                "used": str(bal.used_days),
                "pending": str(bal.pending_days),
                "available": str(bal.available_days),
            }

        return {
            "employee_id": str(employee_id),
            "snapshot_date": snapshot_date.isoformat(),
            "balances": result,
        }

    def export_monthly_leave_data(self, month, year, employee_id=None):
        """Export leave data for all employees for a given month.

        Args:
            month: Month number (1-12).
            year: Year.
            employee_id: Optional single employee filter.

        Returns:
            List of dicts with leave data per employee.
        """
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        leaves_qs = LeaveRequest.objects.filter(
            status=LeaveRequestStatus.APPROVED,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_deleted=False,
        ).select_related("employee__user", "employee__department", "leave_type")

        if employee_id:
            leaves_qs = leaves_qs.filter(employee_id=employee_id)

        # Group by employee
        employee_data = {}
        for lr in leaves_qs:
            emp_id = str(lr.employee_id)
            if emp_id not in employee_data:
                employee_data[emp_id] = {
                    "employee_id": emp_id,
                    "employee_code": getattr(lr.employee, "employee_code", ""),
                    "name": self._format_name(lr.employee),
                    "department": (
                        str(lr.employee.department.name)
                        if lr.employee.department
                        else ""
                    ),
                    "period": {
                        "month": month,
                        "year": year,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                    },
                    "leave_summary": {
                        "total_leave_days": Decimal("0"),
                        "paid_leave_days": Decimal("0"),
                        "unpaid_leave_days": Decimal("0"),
                        "by_type": {},
                    },
                }

            data = employee_data[emp_id]
            data["leave_summary"]["total_leave_days"] += lr.total_days
            if lr.leave_type.is_paid:
                data["leave_summary"]["paid_leave_days"] += lr.total_days
            else:
                data["leave_summary"]["unpaid_leave_days"] += lr.total_days

            t = lr.leave_type.name
            by_type = data["leave_summary"]["by_type"]
            by_type.setdefault(t, {"days": Decimal("0"), "is_paid": lr.leave_type.is_paid, "requests": 0})
            by_type[t]["days"] += lr.total_days
            by_type[t]["requests"] += 1

        # Convert Decimals to strings for serialization
        result = []
        for data in employee_data.values():
            summary = data["leave_summary"]
            summary["total_leave_days"] = str(summary["total_leave_days"])
            summary["paid_leave_days"] = str(summary["paid_leave_days"])
            summary["unpaid_leave_days"] = str(summary["unpaid_leave_days"])
            for v in summary["by_type"].values():
                v["days"] = str(v["days"])
            result.append(data)

        return result

    # ── Private Helpers ──────────────────────────────────────

    def _get_employee_daily_rate(self, employee_id, period):
        """Calculate daily rate for an employee.

        Attempts to retrieve the latest salary from EmploymentHistory.
        Falls back to zero if salary info is unavailable.
        """
        try:
            from apps.employees.models.employment_history import EmploymentHistory

            latest = (
                EmploymentHistory.objects.filter(
                    employee_id=employee_id,
                    new_salary__isnull=False,
                    effective_date__lte=period.get("end_date", date.today()),
                )
                .order_by("-effective_date")
                .values_list("new_salary", flat=True)
                .first()
            )
            if latest and latest > 0:
                # Standard working days per month (26 days)
                return (Decimal(str(latest)) / Decimal("26")).quantize(
                    Decimal("0.01")
                )
        except Exception:
            logger.debug("Could not retrieve salary for employee %s", employee_id)
        return Decimal("0")

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
