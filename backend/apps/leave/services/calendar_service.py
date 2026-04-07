"""Leave Calendar Service for the Leave Management app.

Provides team calendars, department calendars, holiday management,
working day calculations, and FullCalendar JSON export.
"""

import logging
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q

from apps.leave.constants import HolidayScope, HolidayType, LeaveRequestStatus
from apps.leave.models.holiday import Holiday
from apps.leave.models.leave_request import LeaveRequest

logger = logging.getLogger(__name__)

# ── Color Maps ───────────────────────────────────────────────
LEAVE_TYPE_COLORS = {
    "ANNUAL": "#4CAF50",
    "SICK": "#F44336",
    "CASUAL": "#2196F3",
    "MATERNITY": "#E91E63",
    "PATERNITY": "#9C27B0",
    "UNPAID": "#FF9800",
    "NO_PAY": "#FF9800",
    "COMPENSATORY": "#00BCD4",
    "STUDY": "#795548",
}
DEFAULT_LEAVE_COLOR = "#757575"

HOLIDAY_TYPE_COLORS = {
    "PUBLIC": "#F44336",
    "BANK": "#FF9800",
    "COMPANY": "#9C27B0",
    "OPTIONAL": "#00BCD4",
}
DEFAULT_HOLIDAY_COLOR = "#757575"


class LeaveCalendarService:
    """Service class for leave calendar operations."""

    # ── Private Helpers ──────────────────────────────────────

    @staticmethod
    def _get_date_range(start_date, end_date):
        """Parse and validate date range.

        Returns:
            Tuple[date, date]

        Raises:
            ValueError: If end < start.
        """
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        if end_date < start_date:
            raise ValueError("End date cannot be before start date.")
        return start_date, end_date

    @staticmethod
    def _format_employee_name(employee):
        """Format employee display name."""
        user = getattr(employee, "user", None)
        if user:
            first = getattr(user, "first_name", "")
            last = getattr(user, "last_name", "")
            if first or last:
                return f"{first} {last}".strip()
            return str(user.email)
        return str(employee)

    @staticmethod
    def _get_leave_color(leave_type_code, status):
        """Get color for a leave type with status-based transparency."""
        color = LEAVE_TYPE_COLORS.get(leave_type_code, DEFAULT_LEAVE_COLOR)
        if status == LeaveRequestStatus.PENDING:
            return f"{color}80"  # 50% transparency
        return color

    @staticmethod
    def _get_holiday_color(holiday_type):
        """Get color for a holiday type."""
        return HOLIDAY_TYPE_COLORS.get(holiday_type, DEFAULT_HOLIDAY_COLOR)

    @staticmethod
    def _get_my_leave_color(status, leave_type_code):
        """Get color for own leaves — gray for REJECTED."""
        if status == LeaveRequestStatus.REJECTED:
            return "#9E9E9E"
        return LEAVE_TYPE_COLORS.get(leave_type_code, DEFAULT_LEAVE_COLOR)

    @staticmethod
    def _is_weekend(check_date):
        """Return True if date is Saturday (5) or Sunday (6)."""
        return check_date.weekday() in (5, 6)

    @classmethod
    def _get_weekends_in_range(cls, start_date, end_date):
        """Count weekend days in a date range."""
        count = 0
        current = start_date
        while current <= end_date:
            if cls._is_weekend(current):
                count += 1
            current += timedelta(days=1)
        return count

    @classmethod
    def _get_holidays_for_employee(cls, employee, start_date, end_date):
        """Get holiday dates applicable to an employee.

        Returns:
            List of date objects.
        """
        scope_q = Q(applies_to=HolidayScope.ALL)

        dept = getattr(employee, "department", None)
        if dept:
            scope_q |= Q(applies_to=HolidayScope.DEPARTMENT, department=dept)

        holidays = Holiday.objects.filter(
            scope_q,
            date__gte=start_date,
            date__lte=end_date,
            is_active=True,
            is_deleted=False,
            is_recurring=False,
        ).values_list("date", flat=True)

        return list(holidays)

    @classmethod
    def _calculate_department_statistics(
        cls, employees, leave_requests, start_date, end_date
    ):
        """Calculate department-level leave statistics.

        Returns:
            Tuple of (statistics_dict, coverage_analysis_dict).
        """
        total_employees = employees.count()
        approved = leave_requests.filter(
            status=LeaveRequestStatus.APPROVED
        ).count()
        pending = leave_requests.filter(
            status=LeaveRequestStatus.PENDING
        ).count()

        # Daily coverage analysis
        coverage = {}
        peak_date = None
        peak_count = 0
        total_absence_days = 0

        current = start_date
        num_days = (end_date - start_date).days + 1

        while current <= end_date:
            on_leave = leave_requests.filter(
                start_date__lte=current,
                end_date__gte=current,
                status=LeaveRequestStatus.APPROVED,
            ).count()

            coverage_pct = (
                round((1 - on_leave / total_employees) * 100, 1)
                if total_employees
                else 100
            )
            is_critical = (
                total_employees > 0 and on_leave / total_employees > 0.3
            )

            coverage[current.isoformat()] = {
                "employees_on_leave": on_leave,
                "coverage_percentage": coverage_pct,
                "critical": is_critical,
            }

            if on_leave > peak_count:
                peak_count = on_leave
                peak_date = current

            total_absence_days += on_leave
            current += timedelta(days=1)

        statistics = {
            "total_leaves": leave_requests.count(),
            "peak_leave_date": peak_date.isoformat() if peak_date else None,
            "peak_leave_count": peak_count,
            "average_daily_absences": round(
                total_absence_days / num_days, 2
            )
            if num_days
            else 0,
            "approved_leaves": approved,
            "pending_leaves": pending,
        }

        return statistics, coverage

    # ── Public Methods ───────────────────────────────────────

    @classmethod
    def get_team_calendar(cls, manager_id, date_range):
        """Get team calendar for a manager's direct reports.

        Args:
            manager_id: Manager's employee ID.
            date_range: Tuple of (start_date, end_date).

        Returns:
            Dict with team_members, leave_entries, summary, date_range.
        """
        from apps.employees.models import Employee

        start_date, end_date = cls._get_date_range(*date_range)

        team = Employee.objects.filter(
            reporting_manager_id=manager_id,
            is_active=True,
            is_deleted=False,
        ).select_related("user", "department")

        team_members = []
        team_ids = []
        for emp in team:
            team_members.append(
                {
                    "id": str(emp.id),
                    "name": cls._format_employee_name(emp),
                    "department": (
                        str(emp.department.name) if emp.department else None
                    ),
                    "position": getattr(emp, "designation_name", ""),
                }
            )
            team_ids.append(emp.id)

        if not team_ids:
            return {
                "team_members": [],
                "leave_entries": [],
                "summary": {
                    "total_team_members": 0,
                    "total_leave_requests": 0,
                    "approved_leaves": 0,
                    "pending_leaves": 0,
                },
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }

        leave_requests = LeaveRequest.objects.filter(
            employee_id__in=team_ids,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status__in=[
                LeaveRequestStatus.APPROVED,
                LeaveRequestStatus.PENDING,
            ],
            is_deleted=False,
        ).select_related("employee__user", "leave_type")

        leave_entries = []
        for lr in leave_requests:
            leave_entries.append(
                {
                    "id": str(lr.id),
                    "employee_id": str(lr.employee_id),
                    "employee_name": cls._format_employee_name(lr.employee),
                    "leave_type": lr.leave_type.name,
                    "leave_type_code": lr.leave_type.code,
                    "start_date": lr.start_date.isoformat(),
                    "end_date": lr.end_date.isoformat(),
                    "total_days": str(lr.total_days),
                    "status": lr.status,
                    "color": cls._get_leave_color(
                        lr.leave_type.code, lr.status
                    ),
                    "reason": lr.reason,
                }
            )

        approved = sum(
            1
            for e in leave_entries
            if e["status"] == LeaveRequestStatus.APPROVED
        )
        pending = sum(
            1
            for e in leave_entries
            if e["status"] == LeaveRequestStatus.PENDING
        )

        return {
            "team_members": team_members,
            "leave_entries": leave_entries,
            "summary": {
                "total_team_members": len(team_members),
                "total_leave_requests": len(leave_entries),
                "approved_leaves": approved,
                "pending_leaves": pending,
            },
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

    @classmethod
    def get_department_calendar(cls, department_id, date_range):
        """Get department calendar with coverage analysis.

        Args:
            department_id: Department ID.
            date_range: Tuple of (start_date, end_date).

        Returns:
            Dict with department, employees, leave_entries,
            statistics, coverage_analysis, date_range.
        """
        from apps.employees.models import Employee
        from apps.organization.models import Department

        start_date, end_date = cls._get_date_range(*date_range)

        dept = Department.objects.get(id=department_id)
        employees = Employee.objects.filter(
            department_id=department_id,
            is_active=True,
            is_deleted=False,
        ).select_related("user")

        emp_ids = list(employees.values_list("id", flat=True))

        leave_requests = LeaveRequest.objects.filter(
            employee_id__in=emp_ids,
            start_date__lte=end_date,
            end_date__gte=start_date,
            status__in=[
                LeaveRequestStatus.APPROVED,
                LeaveRequestStatus.PENDING,
            ],
            is_deleted=False,
        ).select_related("employee__user", "leave_type")

        emp_list = [
            {
                "id": str(emp.id),
                "name": cls._format_employee_name(emp),
                "position": getattr(emp, "designation_name", ""),
                "manager": str(
                    getattr(emp, "reporting_manager_id", "")
                ),
            }
            for emp in employees
        ]

        leave_entries = [
            {
                "id": str(lr.id),
                "employee_id": str(lr.employee_id),
                "employee_name": cls._format_employee_name(lr.employee),
                "leave_type": lr.leave_type.name,
                "leave_type_code": lr.leave_type.code,
                "start_date": lr.start_date.isoformat(),
                "end_date": lr.end_date.isoformat(),
                "total_days": str(lr.total_days),
                "status": lr.status,
                "color": cls._get_leave_color(
                    lr.leave_type.code, lr.status
                ),
                "reason": lr.reason,
            }
            for lr in leave_requests
        ]

        statistics, coverage = cls._calculate_department_statistics(
            employees, leave_requests, start_date, end_date
        )

        return {
            "department": {
                "id": str(dept.id),
                "name": dept.name,
                "total_employees": len(emp_ids),
            },
            "employees": emp_list,
            "leave_entries": leave_entries,
            "statistics": statistics,
            "coverage_analysis": coverage,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

    @classmethod
    def get_holidays(cls, date_range, department_id=None, location=None):
        """Get holidays for a date range with optional scope filtering.

        Args:
            date_range: Tuple of (start_date, end_date).
            department_id: Optional department filter.
            location: Optional location filter.

        Returns:
            List of holiday dicts.
        """
        start_date, end_date = cls._get_date_range(*date_range)

        scope_q = Q(applies_to=HolidayScope.ALL)
        if department_id:
            scope_q |= Q(
                applies_to=HolidayScope.DEPARTMENT,
                department_id=department_id,
            )
        if location:
            scope_q |= Q(
                applies_to=HolidayScope.LOCATION, location=location
            )

        holidays = (
            Holiday.objects.filter(
                scope_q,
                date__gte=start_date,
                date__lte=end_date,
                is_active=True,
                is_deleted=False,
                is_recurring=False,
            )
            .select_related("department")
            .order_by("date", "name")
        )

        return [
            {
                "id": str(h.id),
                "name": h.name,
                "date": h.date.isoformat(),
                "holiday_type": h.holiday_type,
                "holiday_type_display": h.get_holiday_type_display(),
                "description": h.description or "",
                "applies_to": h.applies_to,
                "department": (
                    str(h.department.name) if h.department else None
                ),
                "location": h.location,
                "color": cls._get_holiday_color(h.holiday_type),
                "is_poya": "Poya" in h.name,
            }
            for h in holidays
        ]

    @classmethod
    def generate_calendar_json(cls, employee_id, date_range):
        """Generate FullCalendar-compatible JSON for an employee.

        Args:
            employee_id: Employee ID.
            date_range: Tuple of (start_date, end_date).

        Returns:
            Dict with events and meta.
        """
        from apps.employees.models import Employee

        start_date, end_date = cls._get_date_range(*date_range)
        employee = Employee.objects.select_related(
            "user", "department"
        ).get(id=employee_id)

        events = []

        # 1. My leaves (all statuses)
        my_leaves = LeaveRequest.objects.filter(
            employee=employee,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_deleted=False,
        ).select_related("leave_type")

        for lr in my_leaves:
            events.append(
                {
                    "id": f"my-leave-{lr.id}",
                    "title": f"{lr.leave_type.name} ({lr.get_status_display()})",
                    "start": lr.start_date.isoformat(),
                    "end": (lr.end_date + timedelta(days=1)).isoformat(),
                    "color": cls._get_my_leave_color(
                        lr.status, lr.leave_type.code
                    ),
                    "allDay": True,
                    "extendedProps": {
                        "type": "my-leave",
                        "status": lr.status,
                        "leave_type": lr.leave_type.name,
                        "total_days": str(lr.total_days),
                    },
                }
            )

        # 2. Team leaves (if manager — only APPROVED)
        is_manager = Employee.objects.filter(
            reporting_manager=employee,
            is_active=True,
            is_deleted=False,
        ).exists()

        if is_manager:
            team_ids = Employee.objects.filter(
                reporting_manager=employee,
                is_active=True,
                is_deleted=False,
            ).values_list("id", flat=True)

            team_leaves = LeaveRequest.objects.filter(
                employee_id__in=team_ids,
                start_date__lte=end_date,
                end_date__gte=start_date,
                status=LeaveRequestStatus.APPROVED,
                is_deleted=False,
            ).select_related("employee__user", "leave_type")

            for lr in team_leaves:
                events.append(
                    {
                        "id": f"team-leave-{lr.id}",
                        "title": (
                            f"{cls._format_employee_name(lr.employee)} - "
                            f"{lr.leave_type.name}"
                        ),
                        "start": lr.start_date.isoformat(),
                        "end": (
                            lr.end_date + timedelta(days=1)
                        ).isoformat(),
                        "color": cls._get_leave_color(
                            lr.leave_type.code, lr.status
                        ),
                        "allDay": True,
                        "extendedProps": {
                            "type": "team-leave",
                            "employee_name": cls._format_employee_name(
                                lr.employee
                            ),
                            "leave_type": lr.leave_type.name,
                        },
                    }
                )

        # 3. Holidays (background display)
        holiday_dates = cls._get_holidays_for_employee(
            employee, start_date, end_date
        )
        holidays = Holiday.objects.filter(
            date__in=holiday_dates,
            is_active=True,
            is_deleted=False,
            is_recurring=False,
        )
        for h in holidays:
            events.append(
                {
                    "id": f"holiday-{h.id}",
                    "title": h.name,
                    "start": h.date.isoformat(),
                    "end": (h.date + timedelta(days=1)).isoformat(),
                    "color": cls._get_holiday_color(h.holiday_type),
                    "allDay": True,
                    "display": "background",
                    "extendedProps": {
                        "type": "holiday",
                        "holiday_type": h.holiday_type,
                        "is_poya": "Poya" in h.name,
                    },
                }
            )

        return {
            "events": events,
            "meta": {
                "employee_id": str(employee.id),
                "employee_name": cls._format_employee_name(employee),
                "is_manager": is_manager,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            },
        }

    @classmethod
    def calculate_working_days(cls, start_date, end_date, employee_id):
        """Calculate working days excluding weekends and holidays.

        Args:
            start_date: Start date (inclusive).
            end_date: End date (inclusive).
            employee_id: Employee ID for holiday scope.

        Returns:
            int: Number of working days.
        """
        from apps.employees.models import Employee

        start_date, end_date = cls._get_date_range(start_date, end_date)
        employee = Employee.objects.select_related("department").get(
            id=employee_id
        )

        total_days = (end_date - start_date).days + 1
        weekends = cls._get_weekends_in_range(start_date, end_date)

        holiday_dates = cls._get_holidays_for_employee(
            employee, start_date, end_date
        )
        # Exclude holidays that fall on weekends (avoid double-counting)
        holidays_not_on_weekend = sum(
            1 for d in holiday_dates if not cls._is_weekend(d)
        )

        working_days = total_days - weekends - holidays_not_on_weekend
        return max(working_days, 0)

    @classmethod
    def auto_adjust_leave_days(cls, leave_request_data):
        """Auto-adjust leave days excluding weekends and holidays.

        Args:
            leave_request_data: Dict with start_date, end_date, employee_id.

        Returns:
            Dict with adjustment details, breakdown, and warnings.
        """
        from apps.employees.models import Employee

        start_date = leave_request_data["start_date"]
        end_date = leave_request_data["end_date"]
        employee_id = leave_request_data["employee_id"]

        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)

        if end_date < start_date:
            raise ValueError("End date cannot be before start date.")

        employee = Employee.objects.select_related(
            "user", "department"
        ).get(id=employee_id)

        calendar_days = (end_date - start_date).days + 1

        # Find weekends
        excluded_weekends = []
        current = start_date
        while current <= end_date:
            if cls._is_weekend(current):
                day_name = current.strftime("%A")
                excluded_weekends.append(
                    {
                        "date": current.isoformat(),
                        "day": day_name,
                    }
                )
            current += timedelta(days=1)

        # Find holidays
        holiday_dates = cls._get_holidays_for_employee(
            employee, start_date, end_date
        )
        holidays_qs = Holiday.objects.filter(
            date__in=holiday_dates,
            is_active=True,
            is_deleted=False,
            is_recurring=False,
        )
        weekend_dates = {w["date"] for w in excluded_weekends}
        excluded_holidays = [
            {
                "date": h.date.isoformat(),
                "name": h.name,
                "type": h.holiday_type,
                "is_poya": "Poya" in h.name,
            }
            for h in holidays_qs
            if h.date.isoformat() not in weekend_dates
        ]

        working_days = cls.calculate_working_days(
            start_date, end_date, employee_id
        )

        breakdown = (
            f"Leave request: {calendar_days} calendar days "
            f"- {len(excluded_weekends)} weekends "
            f"- {len(excluded_holidays)} holidays "
            f"= {working_days} working days"
        )

        warnings = []
        if calendar_days > 10:
            warnings.append("Extended leave: request spans more than 10 days.")
        if excluded_holidays:
            warnings.append(
                f"{len(excluded_holidays)} holiday(s) fall within the leave range."
            )
        if working_days == 0:
            warnings.append(
                "Zero working days — the entire range consists of weekends/holidays."
            )

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "calendar_days": calendar_days,
            "working_days": working_days,
            "excluded_weekends": excluded_weekends,
            "excluded_holidays": excluded_holidays,
            "breakdown": breakdown,
            "warnings": warnings,
            "employee": {
                "id": str(employee.id),
                "name": cls._format_employee_name(employee),
                "department": (
                    str(employee.department.name)
                    if employee.department
                    else None
                ),
            },
        }
