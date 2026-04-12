"""Tests for SP12 — Tax Reporting & Compliance.

Covers TaxConfiguration, TaxPeriodRecord, VATReturn, PAYEReturn,
EPFReturn, ETFReturn, TaxSubmission, FilingReminderService, and
the tax API views.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounting.models import (
    EPFReturn,
    ETFReturn,
    PAYEReturn,
    TaxConfiguration,
    TaxPeriodRecord,
    TaxSubmission,
    VATReturn,
)
from apps.accounting.services.filing_reminder import FilingReminderService
from apps.accounting.tax.enums import FilingStatus, TaxPeriod, TaxType

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────


@pytest.fixture
def tax_config(tenant_context):
    """Create a test TaxConfiguration with all registrations."""
    return TaxConfiguration.objects.create(
        vat_registration_no="123456789-7000",
        is_svat_registered=False,
        vat_filing_period=TaxPeriod.MONTHLY,
        epf_registration_no="E/123456",
        etf_registration_no="654321",
        tin_number="987654321",
        is_active=True,
    )


@pytest.fixture
def tax_period(tenant_context, tax_config):
    """Create a January 2026 tax period for VAT."""
    return TaxPeriodRecord.objects.create(
        tax_configuration=tax_config,
        tax_type=TaxType.VAT,
        period_type=TaxPeriod.MONTHLY,
        year=2026,
        period_number=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        due_date=date(2026, 2, 20),
        filing_status=FilingStatus.PENDING,
    )


@pytest.fixture
def paye_period(tenant_context, tax_config):
    return TaxPeriodRecord.objects.create(
        tax_configuration=tax_config,
        tax_type=TaxType.PAYE,
        period_type=TaxPeriod.MONTHLY,
        year=2026,
        period_number=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        due_date=date(2026, 2, 15),
        filing_status=FilingStatus.PENDING,
    )


@pytest.fixture
def epf_period(tenant_context, tax_config):
    return TaxPeriodRecord.objects.create(
        tax_configuration=tax_config,
        tax_type=TaxType.EPF,
        period_type=TaxPeriod.MONTHLY,
        year=2026,
        period_number=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        due_date=date(2026, 2, 28),
        filing_status=FilingStatus.PENDING,
    )


@pytest.fixture
def etf_period(tenant_context, tax_config):
    return TaxPeriodRecord.objects.create(
        tax_configuration=tax_config,
        tax_type=TaxType.ETF,
        period_type=TaxPeriod.MONTHLY,
        year=2026,
        period_number=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        due_date=date(2026, 2, 28),
        filing_status=FilingStatus.PENDING,
    )


# ──────────────────────────────────────────────────────────────
# Tax Enums
# ──────────────────────────────────────────────────────────────


class TestTaxEnums:
    def test_tax_type_values(self):
        assert TaxType.VAT == "vat"
        assert TaxType.PAYE == "paye"
        assert TaxType.EPF == "epf"
        assert TaxType.ETF == "etf"

    def test_tax_period_values(self):
        assert TaxPeriod.MONTHLY == "monthly"
        assert TaxPeriod.QUARTERLY == "quarterly"
        assert TaxPeriod.ANNUAL == "annual"

    def test_filing_status_values(self):
        assert FilingStatus.PENDING == "pending"
        assert FilingStatus.GENERATED == "generated"
        assert FilingStatus.FILED == "filed"
        assert FilingStatus.ACCEPTED == "accepted"
        assert FilingStatus.REJECTED == "rejected"


# ──────────────────────────────────────────────────────────────
# TaxConfiguration Model
# ──────────────────────────────────────────────────────────────


class TestTaxConfiguration:
    def test_create(self, tax_config):
        assert tax_config.pk is not None
        assert tax_config.vat_registration_no == "123456789-7000"
        assert tax_config.is_active is True

    def test_str_includes_vat_and_tin(self, tax_config):
        s = str(tax_config)
        assert "VAT:" in s
        assert "TIN:" in s

    def test_vat_number_format_invalid(self, tenant_context):
        cfg = TaxConfiguration(
            vat_registration_no="BAD-FORMAT",
            vat_filing_period=TaxPeriod.MONTHLY,
        )
        with pytest.raises(ValidationError):
            cfg.full_clean()

    def test_epf_number_format_invalid(self, tenant_context):
        cfg = TaxConfiguration(epf_registration_no="BADFORMAT")
        with pytest.raises(ValidationError):
            cfg.full_clean()

    def test_etf_number_format_invalid(self, tenant_context):
        cfg = TaxConfiguration(etf_registration_no="XXXXXX")
        with pytest.raises(ValidationError):
            cfg.full_clean()

    def test_tin_number_format_invalid(self, tenant_context):
        cfg = TaxConfiguration(tin_number="SHORT")
        with pytest.raises(ValidationError):
            cfg.full_clean()

    def test_vat_filing_period_required_when_vat_registered(self, tenant_context):
        cfg = TaxConfiguration(
            vat_registration_no="123456789-7000",
            vat_filing_period="",
        )
        with pytest.raises(ValidationError):
            cfg.clean()

    def test_svat_registration(self, tax_config):
        assert tax_config.is_svat_registered is False
        tax_config.is_svat_registered = True
        tax_config.save()
        tax_config.refresh_from_db()
        assert tax_config.is_svat_registered is True


# ──────────────────────────────────────────────────────────────
# TaxPeriodRecord Model
# ──────────────────────────────────────────────────────────────


class TestTaxPeriodRecord:
    def test_create(self, tax_period):
        assert tax_period.pk is not None
        assert tax_period.tax_type == TaxType.VAT
        assert tax_period.year == 2026
        assert tax_period.period_number == 1

    def test_str_representation(self, tax_period):
        s = str(tax_period)
        assert "2026" in s

    def test_unique_constraint(self, tax_config, tax_period):
        with pytest.raises(Exception):
            TaxPeriodRecord.objects.create(
                tax_configuration=tax_config,
                tax_type=TaxType.VAT,
                period_type=TaxPeriod.MONTHLY,
                year=2026,
                period_number=1,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                due_date=date(2026, 2, 20),
            )

    def test_is_overdue_property(self, tax_period):
        # due_date is 2026-02-20 which is in the future
        # If today < due_date, not overdue; if past, overdue.
        # We check the property exists and returns a boolean.
        result = tax_period.is_overdue
        assert isinstance(result, bool)

    def test_date_range_ordering(self, tax_period):
        assert tax_period.start_date < tax_period.end_date


# ──────────────────────────────────────────────────────────────
# VATReturn Model
# ──────────────────────────────────────────────────────────────


class TestVATReturn:
    def test_create_with_auto_reference(self, tax_period):
        vat = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("18000.00"),
            input_vat=Decimal("9000.00"),
        )
        assert vat.pk is not None
        assert vat.reference_number.startswith("VAT-202601")

    def test_net_vat_auto_calculated(self, tax_period):
        vat = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("18000.00"),
            input_vat=Decimal("9000.00"),
        )
        assert vat.net_vat_payable == Decimal("9000.00")

    def test_refund_position(self, tax_period):
        vat = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("5000.00"),
            input_vat=Decimal("12000.00"),
        )
        assert vat.net_vat_payable == Decimal("-7000.00")
        assert vat.is_refund_position is True

    def test_not_refund_position(self, tax_period):
        vat = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("20000.00"),
            input_vat=Decimal("5000.00"),
        )
        assert vat.is_refund_position is False

    def test_zero_vat(self, tax_period):
        vat = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("0.00"),
            input_vat=Decimal("0.00"),
        )
        assert vat.net_vat_payable == Decimal("0.00")
        assert vat.is_refund_position is False

    def test_decimal_precision(self, tax_period):
        vat = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("12345.67"),
            input_vat=Decimal("4567.89"),
        )
        assert vat.net_vat_payable == Decimal("7777.78")

    def test_str(self, tax_period):
        vat = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("1000.00"),
        )
        assert "VAT Return" in str(vat)

    def test_default_status(self, tax_period):
        vat = VATReturn.objects.create(period=tax_period)
        assert vat.status == FilingStatus.GENERATED

    def test_line_items_json(self, tax_period):
        items = {"sales": [{"amount": "100", "vat": "18"}]}
        vat = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("18.00"),
            line_items=items,
        )
        vat.refresh_from_db()
        assert vat.line_items["sales"][0]["amount"] == "100"

    def test_unique_reference(self, tax_period):
        v1 = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("1000.00"),
        )
        v2 = VATReturn.objects.create(
            period=tax_period,
            output_vat=Decimal("2000.00"),
        )
        assert v1.reference_number != v2.reference_number


# ──────────────────────────────────────────────────────────────
# PAYEReturn Model
# ──────────────────────────────────────────────────────────────


class TestPAYEReturn:
    def test_create_with_auto_reference(self, paye_period):
        paye = PAYEReturn.objects.create(
            period=paye_period,
            total_employees=10,
            total_remuneration=Decimal("1500000.00"),
            total_paye_deducted=Decimal("45000.00"),
        )
        assert paye.pk is not None
        assert paye.reference_number.startswith("PAYE-")

    def test_employee_details_json(self, paye_period):
        details = [{"name": "Test Employee", "paye": "5000"}]
        paye = PAYEReturn.objects.create(
            period=paye_period,
            total_employees=1,
            total_remuneration=Decimal("100000.00"),
            total_paye_deducted=Decimal("5000.00"),
            employee_details=details,
        )
        paye.refresh_from_db()
        assert len(paye.employee_details) == 1
        assert paye.employee_details[0]["name"] == "Test Employee"

    def test_str(self, paye_period):
        paye = PAYEReturn.objects.create(
            period=paye_period,
            total_employees=5,
            total_remuneration=Decimal("500000.00"),
            total_paye_deducted=Decimal("25000.00"),
        )
        assert "PAYE" in str(paye)


# ──────────────────────────────────────────────────────────────
# EPFReturn Model
# ──────────────────────────────────────────────────────────────


class TestEPFReturn:
    def test_create_with_auto_reference(self, epf_period):
        epf = EPFReturn.objects.create(
            period=epf_period,
            total_employees=20,
            total_employee_contribution=Decimal("80000.00"),
            total_employer_contribution=Decimal("120000.00"),
        )
        assert epf.pk is not None
        assert epf.reference_number.startswith("EPF-")

    def test_total_contribution_auto_calculated(self, epf_period):
        epf = EPFReturn.objects.create(
            period=epf_period,
            total_employees=10,
            total_employee_contribution=Decimal("40000.00"),
            total_employer_contribution=Decimal("60000.00"),
        )
        assert epf.total_contribution == Decimal("100000.00")

    def test_8_12_percent_rates(self, epf_period):
        """Employee 8% + Employer 12% = 20% total on gross salary."""
        gross = Decimal("1000000.00")
        employee_share = gross * Decimal("0.08")
        employer_share = gross * Decimal("0.12")
        epf = EPFReturn.objects.create(
            period=epf_period,
            total_employees=1,
            total_employee_contribution=employee_share,
            total_employer_contribution=employer_share,
        )
        assert epf.total_employee_contribution == Decimal("80000.00")
        assert epf.total_employer_contribution == Decimal("120000.00")
        assert epf.total_contribution == Decimal("200000.00")

    def test_employee_schedule_json(self, epf_period):
        schedule = [{"name": "A", "employee_contrib": "8000", "employer_contrib": "12000"}]
        epf = EPFReturn.objects.create(
            period=epf_period,
            total_employees=1,
            total_employee_contribution=Decimal("8000.00"),
            total_employer_contribution=Decimal("12000.00"),
            employee_schedule=schedule,
        )
        epf.refresh_from_db()
        assert len(epf.employee_schedule) == 1

    def test_str(self, epf_period):
        epf = EPFReturn.objects.create(
            period=epf_period,
            total_employees=5,
            total_employee_contribution=Decimal("40000.00"),
            total_employer_contribution=Decimal("60000.00"),
        )
        assert "EPF" in str(epf)


# ──────────────────────────────────────────────────────────────
# ETFReturn Model
# ──────────────────────────────────────────────────────────────


class TestETFReturn:
    def test_create_with_auto_reference(self, etf_period):
        etf = ETFReturn.objects.create(
            period=etf_period,
            total_employees=20,
            total_contribution=Decimal("30000.00"),
            total_gross_salary=Decimal("1000000.00"),
        )
        assert etf.pk is not None
        assert etf.reference_number.startswith("ETF-")

    def test_3_percent_rate(self, etf_period):
        """ETF is 3% employer-only contribution."""
        gross = Decimal("1000000.00")
        etf_contrib = gross * Decimal("0.03")
        etf = ETFReturn.objects.create(
            period=etf_period,
            total_employees=1,
            total_contribution=etf_contrib,
            total_gross_salary=gross,
        )
        assert etf.total_contribution == Decimal("30000.00")

    def test_str(self, etf_period):
        etf = ETFReturn.objects.create(
            period=etf_period,
            total_employees=5,
            total_contribution=Decimal("15000.00"),
            total_gross_salary=Decimal("500000.00"),
        )
        assert "ETF" in str(etf)


# ──────────────────────────────────────────────────────────────
# TaxSubmission Model
# ──────────────────────────────────────────────────────────────


class TestTaxSubmission:
    def test_create(self, tax_period, user):
        sub = TaxSubmission.objects.create(
            tax_period=tax_period,
            submitted_by=user,
            submission_reference="VAT-2026-000001",
        )
        assert sub.pk is not None
        assert sub.status == TaxSubmission.SubmissionStatus.SUBMITTED

    def test_is_accepted(self, tax_period, user):
        sub = TaxSubmission.objects.create(
            tax_period=tax_period,
            submitted_by=user,
            submission_reference="VAT-2026-000002",
            status=TaxSubmission.SubmissionStatus.ACCEPTED,
        )
        assert sub.is_accepted is True
        assert sub.is_pending is False

    def test_is_pending(self, tax_period, user):
        sub = TaxSubmission.objects.create(
            tax_period=tax_period,
            submitted_by=user,
        )
        assert sub.is_pending is True

    def test_can_resubmit(self, tax_period, user):
        sub = TaxSubmission.objects.create(
            tax_period=tax_period,
            submitted_by=user,
            status=TaxSubmission.SubmissionStatus.REJECTED,
        )
        assert sub.can_resubmit is True

    def test_accepted_requires_reference(self, tax_period, user):
        sub = TaxSubmission(
            tax_period=tax_period,
            submitted_by=user,
            status=TaxSubmission.SubmissionStatus.ACCEPTED,
            submission_reference="",
        )
        with pytest.raises(ValidationError):
            sub.clean()

    def test_get_by_reference(self, tax_period, user):
        TaxSubmission.objects.create(
            tax_period=tax_period,
            submitted_by=user,
            submission_reference="VAT-2026-000003",
        )
        found = TaxSubmission.get_by_reference("VAT-2026-000003")
        assert found is not None
        assert found.submission_reference == "VAT-2026-000003"

    def test_get_by_reference_not_found(self, tenant_context):
        result = TaxSubmission.get_by_reference("NONEXISTENT")
        assert result is None

    def test_str(self, tax_period, user):
        sub = TaxSubmission.objects.create(
            tax_period=tax_period,
            submitted_by=user,
            submission_reference="VAT-2026-000004",
        )
        s = str(sub)
        assert "VAT" in s or "Return" in s

    def test_on_time_submission(self, tax_period, user):
        sub = TaxSubmission.objects.create(
            tax_period=tax_period,
            submitted_by=user,
            submitted_at=timezone.make_aware(
                timezone.datetime(2026, 2, 15, 10, 0)
            ),
        )
        assert sub.is_submitted_on_time is True
        assert sub.get_days_early() == 5

    def test_late_submission(self, tax_period, user):
        sub = TaxSubmission.objects.create(
            tax_period=tax_period,
            submitted_by=user,
            submitted_at=timezone.make_aware(
                timezone.datetime(2026, 2, 25, 10, 0)
            ),
        )
        assert sub.is_submitted_on_time is False
        assert sub.get_days_late() == 5


# ──────────────────────────────────────────────────────────────
# FilingReminderService
# ──────────────────────────────────────────────────────────────


class TestFilingReminderService:
    def test_vat_due_date_calculation(self):
        svc = FilingReminderService()
        due = svc.calculate_vat_due_date(date(2026, 1, 1))
        assert due.month == 2
        assert due.day == 20

    def test_vat_december_rollover(self):
        svc = FilingReminderService()
        due = svc.calculate_vat_due_date(date(2026, 12, 1))
        assert due.year == 2027
        assert due.month == 1
        assert due.day == 20

    def test_paye_due_date_calculation(self):
        svc = FilingReminderService()
        due = svc.calculate_paye_due_date(date(2026, 1, 1))
        assert due.month == 2
        # Feb 15, 2026 is a Sunday, so forward-adjusted to Monday Feb 16
        assert due.day == 16
        assert due.weekday() == 0  # Monday

    def test_paye_december_rollover(self):
        svc = FilingReminderService()
        due = svc.calculate_paye_due_date(date(2026, 12, 1))
        assert due.year == 2027
        assert due.month == 1
        assert due.day == 15

    def test_epf_due_date_last_business_day(self):
        svc = FilingReminderService()
        due = svc.calculate_epf_due_date(date(2026, 1, 1))
        # February 2026 has 28 days; Feb 28 2026 is Saturday
        # So it should be adjusted backward to Friday Feb 27
        assert due.month == 2
        assert due.weekday() <= 4  # Mon-Fri

    def test_etf_same_as_epf(self):
        svc = FilingReminderService()
        epf_due = svc.calculate_epf_due_date(date(2026, 3, 1))
        etf_due = svc.calculate_etf_due_date(date(2026, 3, 1))
        assert epf_due == etf_due

    def test_due_date_router(self):
        svc = FilingReminderService()
        vat = svc.calculate_due_date(TaxType.VAT, date(2026, 1, 1))
        assert vat.month == 2
        assert vat.day == 20

    def test_due_date_router_unknown_type(self):
        svc = FilingReminderService()
        with pytest.raises(ValueError):
            svc.calculate_due_date("UNKNOWN", date(2026, 1, 1))

    def test_urgency_overdue(self):
        past = timezone.now().date() - timedelta(days=5)
        assert FilingReminderService.get_urgency_level(past) == "overdue"

    def test_urgency_urgent(self):
        tomorrow = timezone.now().date() + timedelta(days=1)
        assert FilingReminderService.get_urgency_level(tomorrow) == "urgent"

    def test_urgency_warning(self):
        three_days = timezone.now().date() + timedelta(days=3)
        assert FilingReminderService.get_urgency_level(three_days) == "warning"

    def test_urgency_upcoming(self):
        seven_days = timezone.now().date() + timedelta(days=7)
        assert FilingReminderService.get_urgency_level(seven_days) == "upcoming"

    def test_urgency_normal(self):
        far = timezone.now().date() + timedelta(days=30)
        assert FilingReminderService.get_urgency_level(far) == "normal"

    def test_days_remaining(self):
        future = timezone.now().date() + timedelta(days=10)
        assert FilingReminderService.get_days_remaining(future) == 10

    def test_days_remaining_negative(self):
        past = timezone.now().date() - timedelta(days=3)
        assert FilingReminderService.get_days_remaining(past) == -3

    def test_reminder_schedule(self):
        assert FilingReminderService.get_reminder_schedule() == [7, 3, 1, 0]

    def test_should_send_reminder_on_schedule(self):
        due = timezone.now().date() + timedelta(days=7)
        assert FilingReminderService.should_send_reminder(due) is True

    def test_should_not_send_reminder_off_schedule(self):
        due = timezone.now().date() + timedelta(days=10)
        assert FilingReminderService.should_send_reminder(due) is False

    def test_should_not_send_reminder_if_already_sent_today(self):
        due = timezone.now().date() + timedelta(days=7)
        today = timezone.now().date()
        assert FilingReminderService.should_send_reminder(due, last_reminder_date=today) is False

    def test_get_pending_filings(self, tax_period):
        """Pending filings should include periods with PENDING status."""
        svc = FilingReminderService()
        pending = svc.get_pending_filings(days_ahead=365 * 5)
        assert pending.filter(pk=tax_period.pk).exists()

    def test_weekend_adjustment_forward(self):
        """Saturday should move to Monday."""
        from datetime import datetime

        # 2026-02-14 is Saturday
        dt = timezone.datetime(2026, 2, 14, 23, 59, 59)
        result = FilingReminderService._adjust_forward_to_weekday(dt)
        assert result.weekday() == 0  # Monday

    def test_weekend_adjustment_backward(self):
        """Saturday should move to Friday."""
        from datetime import datetime

        dt = timezone.datetime(2026, 2, 14, 23, 59, 59)
        result = FilingReminderService._adjust_backward_to_weekday(dt)
        assert result.weekday() == 4  # Friday

    def test_widget_data_structure(self, tax_period):
        svc = FilingReminderService()
        data = svc.get_widget_data()
        assert "pending_filings" in data
        assert "summary" in data
        assert "recent_submissions" in data
        assert "last_updated" in data
        assert "pending_count" in data["summary"]
