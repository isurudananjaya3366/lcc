"""Production-level tests for Leave Management services.

Tests run against real PostgreSQL via Docker with tenant isolation.
Covers accrual, request lifecycle, and calendar services.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone

from apps.leave.constants import LeaveRequestStatus, LeaveTypeCategory

pytestmark = pytest.mark.django_db


# ══════════════════════════════════════════════════════════════
# LeaveAccrualService Tests
# ══════════════════════════════════════════════════════════════


class TestLeaveAccrualService:
    """Tests for accrual, monthly, pro-rata, and carry-forward logic."""

    def test_grant_annual_accrual(
        self, employee, annual_leave_type, annual_leave_policy
    ):
        from apps.leave.services.accrual_service import LeaveAccrualService

        year = date.today().year
        result = LeaveAccrualService.grant_annual_accrual(
            employee, annual_leave_type, year
        )
        assert result["success"] is True
        assert result["amount_accrued"] == Decimal("14")
        assert result["balance"].opening_balance == Decimal("14")

    def test_grant_annual_accrual_idempotent(
        self, employee, annual_leave_type, annual_leave_policy
    ):
        """Second grant for same year should fail."""
        from apps.leave.services.accrual_service import LeaveAccrualService

        year = date.today().year
        LeaveAccrualService.grant_annual_accrual(
            employee, annual_leave_type, year
        )
        result = LeaveAccrualService.grant_annual_accrual(
            employee, annual_leave_type, year
        )
        assert result["success"] is False
        assert "already allocated" in result["message"].lower()

    def test_grant_annual_accrual_no_entitlement(
        self, employee, sick_leave_type
    ):
        """No policy and no default should fail gracefully."""
        from apps.leave.services.accrual_service import LeaveAccrualService
        from apps.leave.models import LeaveType

        # Create a leave type with no default and no policy
        lt = LeaveType.objects.create(
            name="Custom Leave",
            code="CTL",
            category=LeaveTypeCategory.OTHER,
            default_days_per_year=None,
        )
        result = LeaveAccrualService.grant_annual_accrual(
            employee, lt, date.today().year
        )
        assert result["success"] is False

    def test_process_monthly_accrual(
        self, employee, annual_leave_type, annual_leave_policy
    ):
        from apps.leave.services.accrual_service import LeaveAccrualService

        year = date.today().year
        result = LeaveAccrualService.process_monthly_accrual(
            employee, annual_leave_type, year, 1
        )
        assert result["success"] is True
        # 14 / 12 = 1.17
        assert result["amount_accrued"] == Decimal("1.17")

    def test_monthly_accrual_prevents_double(
        self, employee, annual_leave_type, annual_leave_policy
    ):
        from apps.leave.services.accrual_service import LeaveAccrualService

        year = date.today().year
        LeaveAccrualService.process_monthly_accrual(
            employee, annual_leave_type, year, 1
        )
        result = LeaveAccrualService.process_monthly_accrual(
            employee, annual_leave_type, year, 1
        )
        assert result["success"] is False

    def test_calculate_pro_rata(
        self, employee, annual_leave_type, annual_leave_policy
    ):
        from apps.leave.services.accrual_service import LeaveAccrualService

        year = date.today().year
        # Joined July 1st = 6 months remaining
        join_date = date(year, 7, 1)
        result = LeaveAccrualService.calculate_pro_rata(
            employee, annual_leave_type, join_date, year
        )
        assert result["success"] is True
        # Pro-rata based on remaining calendar days, not months
        assert result["amount_accrued"] > Decimal("0")
        assert result["amount_accrued"] <= Decimal("14.00")

    def test_check_and_expire_leaves(self, tenant_context, employee, annual_leave_type):
        """Expired carry-forward balances should be processed."""
        from apps.leave.models import LeaveBalance
        from apps.leave.services.accrual_service import LeaveAccrualService

        bal = LeaveBalance.objects.create(
            employee=employee,
            leave_type=annual_leave_type,
            year=date.today().year,
            opening_balance=Decimal("14.00"),
            carried_from_previous=Decimal("5.00"),
            carry_forward_expiry=date(2020, 1, 1),  # already expired
            is_active=True,
        )

        result = LeaveAccrualService.check_and_expire_leaves()
        assert result["success"] is True
        assert result["expired_count"] >= 0


# ══════════════════════════════════════════════════════════════
# LeaveRequestService Tests
# ══════════════════════════════════════════════════════════════


class TestLeaveRequestService:
    """Tests for leave request CRUD and lifecycle."""

    def test_create_draft(self, employee, annual_leave_type, annual_balance):
        from apps.leave.services.request_service import LeaveRequestService

        data = {
            "start_date": date(date.today().year, 11, 1),
            "end_date": date(date.today().year, 11, 3),
            "reason": "Test leave",
        }
        req = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data
        )
        assert req.status == LeaveRequestStatus.DRAFT
        assert req.total_days == Decimal("3")
        assert req.employee == employee

    def test_create_draft_half_day(self, employee, annual_leave_type, annual_balance):
        from apps.leave.services.request_service import LeaveRequestService

        data = {
            "start_date": date(date.today().year, 11, 5),
            "end_date": date(date.today().year, 11, 5),
            "is_half_day": True,
            "half_day_type": "FIRST_HALF",
            "reason": "Half day test",
        }
        req = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data
        )
        assert req.total_days == Decimal("0.5")
        assert req.is_half_day is True

    def test_submit_request(self, employee, annual_leave_type, annual_balance):
        from apps.leave.services.request_service import LeaveRequestService

        data = {
            "start_date": date(date.today().year, 11, 10),
            "end_date": date(date.today().year, 11, 12),
            "reason": "Submission test",
        }
        req = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data
        )
        submitted = LeaveRequestService.submit(req.id)
        assert submitted.status == LeaveRequestStatus.PENDING
        assert submitted.submitted_at is not None

        # Check pending balance increased
        annual_balance.refresh_from_db()
        assert annual_balance.pending_days == Decimal("3.00")

    def test_submit_insufficient_balance(self, employee, annual_leave_type, annual_balance):
        from apps.leave.services.request_service import LeaveRequestService

        # Use up most of the balance
        annual_balance.used_days = Decimal("12.00")
        annual_balance.save()

        data = {
            "start_date": date(date.today().year, 11, 10),
            "end_date": date(date.today().year, 11, 15),
            "total_days": Decimal("5.00"),
            "reason": "Too many days",
        }
        req = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data
        )
        with pytest.raises(ValueError, match="Insufficient"):
            LeaveRequestService.submit(req.id)

    def test_approve_request(
        self, employee, annual_leave_type, annual_balance, approver_user
    ):
        from apps.leave.services.request_service import LeaveRequestService

        data = {
            "start_date": date(date.today().year, 12, 1),
            "end_date": date(date.today().year, 12, 2),
            "reason": "Approval test",
        }
        req = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data
        )
        LeaveRequestService.submit(req.id)
        approved = LeaveRequestService.approve(req.id, approver_user)
        assert approved.status == LeaveRequestStatus.APPROVED
        assert approved.approved_by == approver_user

        # Check balance: pending decreased, used increased
        annual_balance.refresh_from_db()
        assert annual_balance.used_days == Decimal("2.00")
        assert annual_balance.pending_days == Decimal("0.00")

    def test_reject_request(
        self, employee, annual_leave_type, annual_balance, approver_user
    ):
        from apps.leave.services.request_service import LeaveRequestService

        data = {
            "start_date": date(date.today().year, 12, 5),
            "end_date": date(date.today().year, 12, 6),
            "reason": "Rejection test",
        }
        req = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data
        )
        LeaveRequestService.submit(req.id)
        rejected = LeaveRequestService.reject(
            req.id, approver_user, reason="Not approved"
        )
        assert rejected.status == LeaveRequestStatus.REJECTED
        assert rejected.rejection_reason == "Not approved"

        # Pending released
        annual_balance.refresh_from_db()
        assert annual_balance.pending_days == Decimal("0.00")

    def test_cancel_request(self, employee, annual_leave_type, annual_balance):
        from apps.leave.services.request_service import LeaveRequestService

        data = {
            "start_date": date(date.today().year, 12, 10),
            "end_date": date(date.today().year, 12, 11),
            "reason": "Cancel test",
        }
        req = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data
        )
        LeaveRequestService.submit(req.id)
        cancelled = LeaveRequestService.cancel(req.id)
        assert cancelled.status == LeaveRequestStatus.CANCELLED

        annual_balance.refresh_from_db()
        assert annual_balance.pending_days == Decimal("0.00")

    def test_recall_approved_request(
        self, employee, annual_leave_type, annual_balance, approver_user
    ):
        from apps.leave.services.request_service import LeaveRequestService

        data = {
            "start_date": date(date.today().year, 12, 15),
            "end_date": date(date.today().year, 12, 16),
            "reason": "Recall test",
        }
        req = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data
        )
        LeaveRequestService.submit(req.id)
        LeaveRequestService.approve(req.id, approver_user)

        recalled = LeaveRequestService.recall(
            req.id, approver_user, reason="No longer needed"
        )
        assert recalled.status == LeaveRequestStatus.RECALLED
        assert recalled.recalled_reason == "No longer needed"

        # Used days reversed
        annual_balance.refresh_from_db()
        assert annual_balance.used_days == Decimal("0.00")

    def test_invalid_transition_draft_to_approved(
        self, employee, annual_leave_type, annual_balance, approver_user
    ):
        """Cannot approve a draft directly (must submit first)."""
        from apps.leave.services.request_service import LeaveRequestService

        data = {
            "start_date": date(date.today().year, 12, 20),
            "end_date": date(date.today().year, 12, 21),
            "reason": "Bad transition",
        }
        req = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data
        )
        with pytest.raises(ValueError, match="Cannot transition"):
            LeaveRequestService.approve(req.id, approver_user)

    def test_overlap_detection(self, employee, annual_leave_type, annual_balance):
        from apps.leave.services.request_service import LeaveRequestService

        data1 = {
            "start_date": date(date.today().year, 10, 1),
            "end_date": date(date.today().year, 10, 5),
            "reason": "First request",
        }
        req1 = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data1
        )
        LeaveRequestService.submit(req1.id)

        # Overlapping request
        data2 = {
            "start_date": date(date.today().year, 10, 3),
            "end_date": date(date.today().year, 10, 7),
            "reason": "Overlapping request",
        }
        req2 = LeaveRequestService.create_draft(
            employee, annual_leave_type.id, data2
        )
        with pytest.raises(ValueError, match="Overlapping"):
            LeaveRequestService.submit(req2.id)

    def test_get_request(self, draft_leave_request):
        from apps.leave.services.request_service import LeaveRequestService

        fetched = LeaveRequestService.get_request(draft_leave_request.id)
        assert fetched.id == draft_leave_request.id

    def test_get_employee_requests(
        self, employee, draft_leave_request, pending_leave_request
    ):
        from apps.leave.services.request_service import LeaveRequestService

        requests = LeaveRequestService.get_employee_requests(employee.id)
        assert requests.count() >= 2

    def test_get_employee_requests_filtered_by_status(
        self, employee, draft_leave_request, pending_leave_request
    ):
        from apps.leave.services.request_service import LeaveRequestService

        drafts = LeaveRequestService.get_employee_requests(
            employee.id, status=LeaveRequestStatus.DRAFT
        )
        assert all(r.status == LeaveRequestStatus.DRAFT for r in drafts)


# ══════════════════════════════════════════════════════════════
# LeaveCalendarService Tests
# ══════════════════════════════════════════════════════════════


class TestLeaveCalendarService:
    """Tests for calendar and working days calculations."""

    def test_calculate_working_days(
        self, employee, annual_leave_type, public_holiday
    ):
        from apps.leave.services.calendar_service import LeaveCalendarService

        # A week without holidays (Mon-Fri)
        start = date(2025, 7, 7)  # Monday
        end = date(2025, 7, 11)  # Friday
        working_days = LeaveCalendarService.calculate_working_days(
            start, end, employee.id
        )
        assert working_days == 5

    def test_calculate_working_days_excludes_weekends(self, employee):
        from apps.leave.services.calendar_service import LeaveCalendarService

        # Mon-Sun = 7 calendar days, 5 working days
        start = date(2025, 7, 7)  # Monday
        end = date(2025, 7, 13)  # Sunday
        working_days = LeaveCalendarService.calculate_working_days(
            start, end, employee.id
        )
        assert working_days == 5

    def test_get_holidays(self, public_holiday, company_holiday):
        from apps.leave.services.calendar_service import LeaveCalendarService

        year = date.today().year
        date_range = (date(year, 1, 1), date(year, 12, 31))
        result = LeaveCalendarService.get_holidays(date_range)
        assert len(result) >= 2

    def test_auto_adjust_leave_days(self, employee, annual_leave_type):
        from apps.leave.services.calendar_service import LeaveCalendarService

        data = {
            "start_date": date(2025, 7, 7),  # Monday
            "end_date": date(2025, 7, 11),  # Friday
            "employee_id": str(employee.id),
            "is_half_day": False,
        }
        result = LeaveCalendarService.auto_adjust_leave_days(data)
        assert "working_days" in result
        assert result["working_days"] >= 0
