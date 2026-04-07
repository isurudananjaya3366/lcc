"""Production-level tests for Leave Management models.

Tests run against real PostgreSQL via Docker with tenant isolation.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.leave.constants import (
    GenderRestriction,
    HalfDayType,
    HolidayScope,
    HolidayType,
    LeaveRequestStatus,
    LeaveTypeCategory,
)

pytestmark = pytest.mark.django_db


# ══════════════════════════════════════════════════════════════
# LeaveType Model Tests
# ══════════════════════════════════════════════════════════════


class TestLeaveTypeModel:
    """Tests for LeaveType model creation, validation, and constraints."""

    def test_create_annual_leave_type(self, annual_leave_type):
        assert annual_leave_type.name == "Annual Leave"
        assert annual_leave_type.code == "AL"
        assert annual_leave_type.category == LeaveTypeCategory.ANNUAL
        assert annual_leave_type.default_days_per_year == 14
        assert annual_leave_type.is_paid is True
        assert annual_leave_type.is_active is True

    def test_create_no_pay_leave_type(self, no_pay_leave_type):
        assert no_pay_leave_type.is_paid is False
        assert no_pay_leave_type.category == LeaveTypeCategory.NO_PAY

    def test_leave_type_str_representation(self, annual_leave_type):
        assert str(annual_leave_type) == "Annual Leave (AL)"

    def test_leave_type_code_uppercased_on_clean(self, tenant_context):
        from apps.leave.models import LeaveType

        lt = LeaveType(
            name="Test Leave",
            code="tl",
            category=LeaveTypeCategory.OTHER,
        )
        lt.full_clean()
        assert lt.code == "TL"

    def test_leave_type_invalid_color(self, tenant_context):
        from apps.leave.models import LeaveType

        lt = LeaveType(
            name="Bad Color",
            code="BC",
            category=LeaveTypeCategory.OTHER,
            color="not-a-color",
        )
        with pytest.raises(ValidationError) as exc:
            lt.full_clean()
        assert "color" in exc.value.message_dict

    def test_maternity_gender_restriction(self, tenant_context):
        from apps.leave.models import LeaveType

        lt = LeaveType(
            name="Maternity Leave",
            code="ML",
            category=LeaveTypeCategory.MATERNITY,
            applicable_gender=GenderRestriction.ALL,
        )
        with pytest.raises(ValidationError) as exc:
            lt.full_clean()
        assert "applicable_gender" in exc.value.message_dict

    def test_paternity_gender_restriction(self, tenant_context):
        from apps.leave.models import LeaveType

        lt = LeaveType(
            name="Paternity Leave",
            code="PL",
            category=LeaveTypeCategory.PATERNITY,
            applicable_gender=GenderRestriction.ALL,
        )
        with pytest.raises(ValidationError) as exc:
            lt.full_clean()
        assert "applicable_gender" in exc.value.message_dict

    def test_maternity_with_correct_gender(self, tenant_context):
        from apps.leave.models import LeaveType

        lt = LeaveType(
            name="Maternity Leave",
            code="ML",
            category=LeaveTypeCategory.MATERNITY,
            applicable_gender=GenderRestriction.FEMALE,
            default_days_per_year=84,
        )
        lt.full_clean()
        lt.save()
        assert lt.pk is not None

    def test_inactive_leave_type(self, inactive_leave_type):
        assert inactive_leave_type.is_active is False


# ══════════════════════════════════════════════════════════════
# LeavePolicy Model Tests
# ══════════════════════════════════════════════════════════════


class TestLeavePolicyModel:
    """Tests for LeavePolicy model and entitlement resolution."""

    def test_create_policy(self, annual_leave_policy):
        assert annual_leave_policy.name == "Annual Leave Policy (All)"
        assert annual_leave_policy.days_per_year == 14
        assert annual_leave_policy.is_active is True

    def test_policy_str(self, annual_leave_policy):
        assert "Annual Leave" in str(annual_leave_policy)

    def test_get_applicable_days_with_override(self, annual_leave_policy):
        assert annual_leave_policy.get_applicable_days() == 14

    def test_get_applicable_days_falls_back_to_leave_type(self, tenant_context, annual_leave_type):
        from apps.leave.models import LeavePolicy

        policy = LeavePolicy.objects.create(
            name="No Override Policy",
            leave_type=annual_leave_type,
            days_per_year=None,
            is_active=True,
            effective_from=date(2024, 1, 1),
        )
        assert policy.get_applicable_days() == 14  # falls back to leave type default

    def test_policy_date_range_validation(self, tenant_context, annual_leave_type):
        from apps.leave.models import LeavePolicy

        policy = LeavePolicy(
            name="Bad Dates Policy",
            leave_type=annual_leave_type,
            effective_from=date(2025, 12, 31),
            effective_to=date(2025, 1, 1),
        )
        with pytest.raises(ValidationError) as exc:
            policy.full_clean()
        assert "effective_to" in exc.value.message_dict

    def test_get_entitlement_days(self, employee, annual_leave_type, annual_leave_policy):
        from apps.leave.models import LeavePolicy

        days = LeavePolicy.get_entitlement_days(employee, annual_leave_type)
        assert days == 14

    def test_get_entitlement_days_no_policy(self, employee, sick_leave_type):
        """Falls back to leave type default_days_per_year."""
        from apps.leave.models import LeavePolicy

        days = LeavePolicy.get_entitlement_days(employee, sick_leave_type)
        assert days == 7  # from leave type default

    def test_is_currently_effective(self, annual_leave_policy):
        assert annual_leave_policy.is_currently_effective is True


# ══════════════════════════════════════════════════════════════
# LeaveBalance Model Tests
# ══════════════════════════════════════════════════════════════


class TestLeaveBalanceModel:
    """Tests for LeaveBalance model including computed properties."""

    def test_create_balance(self, annual_balance):
        assert annual_balance.opening_balance == Decimal("14.00")
        assert annual_balance.used_days == Decimal("0.00")
        assert annual_balance.year == date.today().year

    def test_available_days_full_balance(self, annual_balance):
        assert annual_balance.available_days == Decimal("14.00")

    def test_available_days_with_usage(self, annual_balance):
        annual_balance.used_days = Decimal("3.00")
        annual_balance.save()
        assert annual_balance.available_days == Decimal("11.00")

    def test_available_days_with_pending(self, annual_balance):
        annual_balance.pending_days = Decimal("2.00")
        annual_balance.save()
        assert annual_balance.available_days == Decimal("12.00")

    def test_available_days_with_encashment(self, annual_balance):
        annual_balance.encashed_days = Decimal("1.00")
        annual_balance.save()
        assert annual_balance.available_days == Decimal("13.00")

    def test_available_days_with_carry_forward(self, balance_with_carry_forward):
        """Carry forward adds to available days when not expired."""
        bal = balance_with_carry_forward
        # If carry forward is not expired, total = opening + allocated + carry - used - pending - encashed
        # = 14 + 0 + 5 - 0 - 0 - 0 = 19 (before expiry check)
        # Expiry depends on whether carry_forward_expiry is past
        today = date.today()
        if today > bal.carry_forward_expiry:
            # Expired: available = 14 + 0 + 5 - 5 - 0 - 0 - 0 = 14
            assert bal.available_days == Decimal("14.00")
        else:
            # Not expired: available = 14 + 0 + 5 - 0 - 0 - 0 = 19
            assert bal.available_days == Decimal("19.00")

    def test_available_days_expired_carry_forward(self, tenant_context, employee, annual_leave_type):
        """Expired carry-forward days are excluded from available."""
        from apps.leave.models import LeaveBalance

        bal = LeaveBalance.objects.create(
            employee=employee,
            leave_type=annual_leave_type,
            year=date.today().year - 1,
            opening_balance=Decimal("14.00"),
            carried_from_previous=Decimal("5.00"),
            carry_forward_expiry=date(2020, 1, 1),  # definitely expired
            is_active=True,
        )
        # Expired: 14 + 0 + 5 - 0 - 0 - 0 - 5 (expired) = 14
        assert bal.available_days == Decimal("14.00")

    def test_available_days_never_negative(self, annual_balance):
        annual_balance.used_days = Decimal("20.00")
        annual_balance.save()
        assert annual_balance.available_days == Decimal("0.00")

    def test_has_sufficient_balance(self, annual_balance):
        assert annual_balance.has_sufficient_balance(Decimal("10.00")) is True
        assert annual_balance.has_sufficient_balance(Decimal("14.00")) is True
        assert annual_balance.has_sufficient_balance(Decimal("15.00")) is False

    def test_is_carry_forward_expired_no_expiry(self, annual_balance):
        assert annual_balance.is_carry_forward_expired() is False

    def test_get_expired_carry_forward_days(self, tenant_context, employee, annual_leave_type):
        from apps.leave.models import LeaveBalance

        bal = LeaveBalance.objects.create(
            employee=employee,
            leave_type=annual_leave_type,
            year=date.today().year - 2,
            opening_balance=Decimal("10.00"),
            carried_from_previous=Decimal("3.00"),
            carry_forward_expiry=date(2020, 6, 30),
            is_active=True,
        )
        assert bal.get_expired_carry_forward_days() == Decimal("3.00")

    def test_can_encash_paid_leave(self, annual_balance):
        ok, msg = annual_balance.can_encash_days(Decimal("5.00"))
        assert ok is True

    def test_cannot_encash_unpaid_leave(self, tenant_context, employee, no_pay_leave_type):
        from apps.leave.models import LeaveBalance

        bal = LeaveBalance.objects.create(
            employee=employee,
            leave_type=no_pay_leave_type,
            year=date.today().year,
            opening_balance=Decimal("10.00"),
            is_active=True,
        )
        ok, msg = bal.can_encash_days(Decimal("5.00"))
        assert ok is False
        assert "Unpaid" in msg

    def test_cannot_encash_more_than_available(self, annual_balance):
        ok, msg = annual_balance.can_encash_days(Decimal("20.00"))
        assert ok is False
        assert "Insufficient" in msg

    def test_unique_constraint(self, annual_balance):
        """Same employee + leave_type + year must be unique."""
        from apps.leave.models import LeaveBalance

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                LeaveBalance.objects.create(
                    employee=annual_balance.employee,
                    leave_type=annual_balance.leave_type,
                    year=annual_balance.year,
                    opening_balance=Decimal("10.00"),
                )

    def test_balance_str(self, annual_balance):
        s = str(annual_balance)
        assert str(annual_balance.year) in s


# ══════════════════════════════════════════════════════════════
# LeaveRequest Model Tests
# ══════════════════════════════════════════════════════════════


class TestLeaveRequestModel:
    """Tests for LeaveRequest model and validation."""

    def test_create_draft_request(self, draft_leave_request):
        assert draft_leave_request.status == LeaveRequestStatus.DRAFT
        assert draft_leave_request.total_days == Decimal("5.00")
        assert draft_leave_request.reason == "Annual vacation"

    def test_pending_request(self, pending_leave_request):
        assert pending_leave_request.status == LeaveRequestStatus.PENDING
        assert pending_leave_request.submitted_at is not None

    def test_approved_request(self, approved_leave_request):
        assert approved_leave_request.status == LeaveRequestStatus.APPROVED
        assert approved_leave_request.approved_by is not None
        assert approved_leave_request.approved_at is not None

    def test_request_str(self, draft_leave_request):
        s = str(draft_leave_request)
        assert "Annual Leave" in s

    def test_end_date_before_start_date_validation(self, tenant_context, employee, annual_leave_type):
        from apps.leave.models import LeaveRequest

        req = LeaveRequest(
            employee=employee,
            leave_type=annual_leave_type,
            start_date=date(2025, 7, 10),
            end_date=date(2025, 7, 5),
            total_days=Decimal("5.00"),
        )
        with pytest.raises(ValidationError) as exc:
            req.full_clean()
        assert "end_date" in exc.value.message_dict

    def test_half_day_requires_type(self, tenant_context, employee, annual_leave_type):
        from apps.leave.models import LeaveRequest

        req = LeaveRequest(
            employee=employee,
            leave_type=annual_leave_type,
            start_date=date(2025, 7, 10),
            end_date=date(2025, 7, 10),
            total_days=Decimal("0.50"),
            is_half_day=True,
            half_day_type=None,
        )
        with pytest.raises(ValidationError) as exc:
            req.full_clean()
        assert "half_day_type" in exc.value.message_dict

    def test_half_day_same_date_required(self, tenant_context, employee, annual_leave_type):
        from apps.leave.models import LeaveRequest

        req = LeaveRequest(
            employee=employee,
            leave_type=annual_leave_type,
            start_date=date(2025, 7, 10),
            end_date=date(2025, 7, 11),
            total_days=Decimal("0.50"),
            is_half_day=True,
            half_day_type=HalfDayType.FIRST_HALF,
        )
        with pytest.raises(ValidationError) as exc:
            req.full_clean()
        assert "is_half_day" in exc.value.message_dict

    def test_valid_half_day_request(self, tenant_context, employee, annual_leave_type):
        from apps.leave.models import LeaveRequest

        req = LeaveRequest(
            employee=employee,
            leave_type=annual_leave_type,
            start_date=date(2025, 7, 10),
            end_date=date(2025, 7, 10),
            total_days=Decimal("0.50"),
            is_half_day=True,
            half_day_type=HalfDayType.FIRST_HALF,
        )
        req.full_clean()
        req.save()
        assert req.pk is not None

    def test_employee_fk_protect(self, draft_leave_request):
        """Deleting employee with leave requests should raise ProtectedError."""
        from django.db.models import ProtectedError

        with pytest.raises(ProtectedError):
            draft_leave_request.employee.delete()

    def test_leave_type_fk_protect(self, draft_leave_request):
        """Deleting leave type with leave requests should raise ProtectedError."""
        from django.db.models import ProtectedError

        with pytest.raises(ProtectedError):
            draft_leave_request.leave_type.delete()


# ══════════════════════════════════════════════════════════════
# Holiday Model Tests
# ══════════════════════════════════════════════════════════════


class TestHolidayModel:
    """Tests for Holiday model."""

    def test_create_public_holiday(self, public_holiday):
        assert public_holiday.name == "Sinhala and Tamil New Year"
        assert public_holiday.holiday_type == HolidayType.PUBLIC
        assert public_holiday.applies_to == HolidayScope.ALL

    def test_create_company_holiday(self, company_holiday):
        assert company_holiday.holiday_type == HolidayType.COMPANY

    def test_department_holiday(self, department_holiday):
        assert department_holiday.applies_to == HolidayScope.DEPARTMENT
        assert department_holiday.department is not None

    def test_holiday_str(self, public_holiday):
        s = str(public_holiday)
        assert "Sinhala and Tamil New Year" in s
        assert "Public Holiday" in s

    def test_create_recurring_holiday(self, tenant_context):
        from apps.leave.models import Holiday

        h = Holiday.objects.create(
            name="Independence Day",
            date=date(2025, 2, 4),
            holiday_type=HolidayType.PUBLIC,
            applies_to=HolidayScope.ALL,
            is_recurring=True,
            is_active=True,
        )
        assert h.is_recurring is True
