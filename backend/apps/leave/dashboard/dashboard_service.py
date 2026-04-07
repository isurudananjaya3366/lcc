"""Leave Dashboard Service for the Leave Management app.

Provides aggregated dashboard data for personal and team
leave views, including balance summaries, pending requests,
upcoming leaves, and team availability.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from apps.leave.constants import LeaveRequestStatus
from apps.leave.models.leave_balance import LeaveBalance
from apps.leave.models.leave_request import LeaveRequest

logger = logging.getLogger(__name__)


class LeaveDashboardService:
    """Service class for leave dashboard widget data."""

    def __init__(self, tenant=None, user=None):
        self.tenant = tenant
        self.user = user

    # ── Personal Dashboard ───────────────────────────────────

    def get_my_leave_data(self, employee_id):
        """Get all personal leave dashboard data.

        Args:
            employee_id: UUID of the employee.

        Returns:
            Dict with balances, pending, upcoming, recent history.
        """
        return {
            "my_balance": self.get_my_balance_summary(employee_id),
            "pending_requests": self.get_pending_requests_summary(employee_id),
            "upcoming_leaves": self.get_upcoming_leaves(employee_id),
            "recent_history": self._get_recent_history(employee_id),
        }

    def get_my_balance_summary(self, employee_id):
        """Get balance summary per leave type for current year.

        Args:
            employee_id: UUID of the employee.

        Returns:
            Dict keyed by leave type with balance details.
        """
        year = timezone.now().year
        balances = LeaveBalance.objects.filter(
            employee_id=employee_id,
            year=year,
            is_active=True,
        ).select_related("leave_type")

        result = {}
        for bal in balances:
            allocated = bal.allocated_days + bal.carried_from_previous
            utilization = (
                round(float(bal.used_days / allocated * 100), 1)
                if allocated
                else 0
            )
            result[bal.leave_type.code] = {
                "leave_type_name": bal.leave_type.name,
                "allocated": str(allocated),
                "used": str(bal.used_days),
                "pending": str(bal.pending_days),
                "available": str(bal.available_days),
                "utilization_percentage": utilization,
            }

        return result

    def get_pending_requests_summary(self, employee_id):
        """Get summary of pending requests for an employee.

        Returns:
            Dict with count, total_days, oldest_request.
        """
        pending = LeaveRequest.objects.filter(
            employee_id=employee_id,
            status=LeaveRequestStatus.PENDING,
            is_deleted=False,
        ).order_by("submitted_at")

        count = pending.count()
        total_days = Decimal("0")
        oldest = None

        for lr in pending:
            total_days += lr.total_days
            if oldest is None:
                oldest = lr

        result = {
            "count": count,
            "total_days": str(total_days),
        }

        if oldest and oldest.submitted_at:
            days_ago = (timezone.now() - oldest.submitted_at).days
            result["oldest_request"] = {
                "id": str(oldest.id),
                "submitted_days_ago": days_ago,
                "start_date": oldest.start_date.isoformat(),
            }

        return result

    def get_upcoming_leaves(self, employee_id, days_ahead=30):
        """Get upcoming approved leaves.

        Args:
            employee_id: UUID of the employee.
            days_ahead: Number of days to look ahead.

        Returns:
            List of upcoming leave dicts.
        """
        today = timezone.now().date()
        end = today + timedelta(days=days_ahead)

        upcoming = LeaveRequest.objects.filter(
            employee_id=employee_id,
            start_date__gte=today,
            start_date__lte=end,
            status=LeaveRequestStatus.APPROVED,
            is_deleted=False,
        ).select_related("leave_type").order_by("start_date")

        return [
            {
                "id": str(lr.id),
                "leave_type": lr.leave_type.name,
                "start_date": lr.start_date.isoformat(),
                "end_date": lr.end_date.isoformat(),
                "days": str(lr.total_days),
                "days_until_start": (lr.start_date - today).days,
            }
            for lr in upcoming
        ]

    # ── Team/Manager Dashboard ───────────────────────────────

    def get_team_dashboard_data(self, manager_id=None, department_id=None):
        """Get team dashboard data for a manager.

        Args:
            manager_id: UUID of the manager (employee).
            department_id: UUID of the department.

        Returns:
            Dict with team summary, on_leave_today, pending approvals.
        """
        from apps.employees.models import Employee

        today = timezone.now().date()

        if manager_id:
            team = Employee.objects.filter(
                reporting_manager_id=manager_id,
                is_active=True,
                is_deleted=False,
            )
        elif department_id:
            team = Employee.objects.filter(
                department_id=department_id,
                is_active=True,
                is_deleted=False,
            )
        else:
            team = Employee.objects.none()

        team_ids = list(team.values_list("id", flat=True))
        total_team = len(team_ids)

        # On leave today
        on_leave = LeaveRequest.objects.filter(
            employee_id__in=team_ids,
            start_date__lte=today,
            end_date__gte=today,
            status=LeaveRequestStatus.APPROVED,
            is_deleted=False,
        ).select_related("employee__user", "leave_type")

        on_leave_list = [
            {
                "employee_id": str(lr.employee_id),
                "name": self._format_name(lr.employee),
                "leave_type": lr.leave_type.name,
                "return_date": lr.end_date.isoformat(),
            }
            for lr in on_leave
        ]

        # Pending approvals
        pending = LeaveRequest.objects.filter(
            employee_id__in=team_ids,
            status=LeaveRequestStatus.PENDING,
            is_deleted=False,
        )
        pending_count = pending.count()
        urgent_count = 0
        for lr in pending:
            if lr.submitted_at:
                days_pending = (timezone.now() - lr.submitted_at).days
                if days_pending > 3:
                    urgent_count += 1

        availability = (
            round((1 - len(on_leave_list) / total_team) * 100, 1)
            if total_team
            else 100
        )

        return {
            "team_on_leave_today": on_leave_list,
            "pending_for_approval": {
                "count": pending_count,
                "urgent_count": urgent_count,
            },
            "team_summary": {
                "total_team_members": total_team,
                "on_leave_today": len(on_leave_list),
                "availability_percentage": availability,
            },
        }

    def get_team_on_leave_today(self, department_id=None):
        """Get employees on leave today.

        Returns:
            List of employee dicts on leave today.
        """
        from apps.employees.models import Employee

        today = timezone.now().date()

        qs = LeaveRequest.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            status=LeaveRequestStatus.APPROVED,
            is_deleted=False,
        ).select_related("employee__user", "leave_type")

        if department_id:
            qs = qs.filter(employee__department_id=department_id)

        return [
            {
                "employee_id": str(lr.employee_id),
                "name": self._format_name(lr.employee),
                "leave_type": lr.leave_type.name,
                "return_date": lr.end_date.isoformat(),
            }
            for lr in qs
        ]

    def get_approval_queue(self, manager_id):
        """Get pending approvals sorted by urgency.

        Args:
            manager_id: UUID of the manager.

        Returns:
            List of pending request dicts sorted by urgency.
        """
        from apps.employees.models import Employee

        today = timezone.now().date()

        team_ids = Employee.objects.filter(
            reporting_manager_id=manager_id,
            is_active=True,
            is_deleted=False,
        ).values_list("id", flat=True)

        pending = LeaveRequest.objects.filter(
            employee_id__in=team_ids,
            status=LeaveRequestStatus.PENDING,
            is_deleted=False,
        ).select_related("employee__user", "leave_type").order_by("submitted_at")

        items = []
        for lr in pending:
            days_pending = (
                (timezone.now() - lr.submitted_at).days
                if lr.submitted_at
                else 0
            )
            days_until = (lr.start_date - today).days

            if days_pending > 5 or days_until <= 0:
                urgency = "OVERDUE"
            elif days_until <= 3:
                urgency = "URGENT"
            else:
                urgency = "NORMAL"

            items.append({
                "id": str(lr.id),
                "employee_name": self._format_name(lr.employee),
                "leave_type": lr.leave_type.name,
                "start_date": lr.start_date.isoformat(),
                "end_date": lr.end_date.isoformat(),
                "total_days": str(lr.total_days),
                "days_pending": days_pending,
                "urgency": urgency,
            })

        # Sort: OVERDUE first, then URGENT, then NORMAL
        priority_order = {"OVERDUE": 0, "URGENT": 1, "NORMAL": 2}
        items.sort(key=lambda x: priority_order.get(x["urgency"], 3))

        return items

    # ── Unified Methods ──────────────────────────────────────

    def get_dashboard_widgets(self, employee_id, is_manager=False, manager_id=None):
        """Get all dashboard widget data in one call.

        Args:
            employee_id: UUID of the employee.
            is_manager: Whether the user is a manager.
            manager_id: UUID of the manager (if is_manager).

        Returns:
            Dict with personal_dashboard, team_dashboard (if manager),
            and quick_stats.
        """
        result = {
            "personal_dashboard": self.get_my_leave_data(employee_id),
            "quick_stats": self.get_quick_stats(employee_id, manager_id),
        }

        if is_manager and manager_id:
            result["team_dashboard"] = self.get_team_dashboard_data(
                manager_id=manager_id
            )

        return result

    def get_quick_stats(self, employee_id, manager_id=None):
        """Get quick stats for dashboard header.

        Returns:
            Dict with key metrics.
        """
        year = timezone.now().year
        today = timezone.now().date()

        # Total balance
        balances = LeaveBalance.objects.filter(
            employee_id=employee_id,
            year=year,
            is_active=True,
        )
        total_balance = sum(b.available_days for b in balances)
        total_used = sum(b.used_days for b in balances)

        # Pending requests
        pending = LeaveRequest.objects.filter(
            employee_id=employee_id,
            status=LeaveRequestStatus.PENDING,
            is_deleted=False,
        ).count()

        # Upcoming leaves
        upcoming = LeaveRequest.objects.filter(
            employee_id=employee_id,
            start_date__gte=today,
            status=LeaveRequestStatus.APPROVED,
            is_deleted=False,
        ).count()

        # Team on leave (if manager)
        team_on_leave = 0
        if manager_id:
            from apps.employees.models import Employee

            team_ids = Employee.objects.filter(
                reporting_manager_id=manager_id,
                is_active=True,
                is_deleted=False,
            ).values_list("id", flat=True)

            team_on_leave = LeaveRequest.objects.filter(
                employee_id__in=team_ids,
                start_date__lte=today,
                end_date__gte=today,
                status=LeaveRequestStatus.APPROVED,
                is_deleted=False,
            ).count()

        return {
            "total_balance": str(total_balance),
            "total_used_this_year": str(total_used),
            "pending_requests": pending,
            "upcoming_leaves_count": upcoming,
            "team_on_leave": team_on_leave,
        }

    # ── Private Helpers ──────────────────────────────────────

    def _get_recent_history(self, employee_id, limit=5):
        """Get recent leave history."""
        recent = LeaveRequest.objects.filter(
            employee_id=employee_id,
            is_deleted=False,
        ).select_related("leave_type").order_by("-created_on")[:limit]

        return [
            {
                "id": str(lr.id),
                "leave_type": lr.leave_type.name,
                "dates": f"{lr.start_date.isoformat()} to {lr.end_date.isoformat()}",
                "days": str(lr.total_days),
                "status": lr.get_status_display(),
            }
            for lr in recent
        ]

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
