"""Tests for SP06 Payroll Processing models."""

import pytest
from datetime import date
from decimal import Decimal

from apps.payroll.constants import PayrollStatus, PaymentStatus, LineType, HistoryAction

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────────────────────
# PayrollPeriod Model Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollPeriod:
    """Tests for the PayrollPeriod model."""

    def test_create_period(self, payroll_period):
        assert payroll_period.period_month == 1
        assert payroll_period.period_year == 2024
        assert payroll_period.name == "January 2024"
        assert payroll_period.status == PayrollStatus.DRAFT

    def test_period_str(self, payroll_period):
        assert str(payroll_period) == "January 2024"

    def test_period_defaults(self, payroll_period):
        assert payroll_period.is_locked is False
        assert payroll_period.locked_at is None
        assert payroll_period.locked_by is None

    def test_period_unique_together(self, payroll_period, tenant_context):
        """Cannot create two periods for the same month/year."""
        from apps.payroll.models import PayrollPeriod
        from django.db import IntegrityError
        from django.db import transaction

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                PayrollPeriod.objects.create(
                    period_month=1,
                    period_year=2024,
                    name="January 2024 Dup",
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 1, 31),
                    pay_date=date(2024, 1, 25),
                )

    def test_period_lock(self, payroll_period, user):
        from django.utils import timezone

        payroll_period.is_locked = True
        payroll_period.locked_at = timezone.now()
        payroll_period.locked_by = user
        payroll_period.save()
        payroll_period.refresh_from_db()
        assert payroll_period.is_locked is True
        assert payroll_period.locked_by == user

    def test_period_status_transition(self, payroll_period):
        payroll_period.status = PayrollStatus.PROCESSING
        payroll_period.save()
        payroll_period.refresh_from_db()
        assert payroll_period.status == PayrollStatus.PROCESSING


# ──────────────────────────────────────────────────────────────
# PayrollSettings Model Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollSettings:
    """Tests for the PayrollSettings model."""

    def test_create_settings(self, payroll_settings):
        assert payroll_settings.default_pay_day == 25
        assert payroll_settings.attendance_cutoff_day == 20
        assert payroll_settings.require_approval is True
        assert payroll_settings.auto_create_period is False

    def test_settings_defaults(self, payroll_settings):
        assert payroll_settings.adjust_for_weekends is True
        assert payroll_settings.use_cutoff_period is False
        assert payroll_settings.min_approvals == 1


# ──────────────────────────────────────────────────────────────
# PayrollRun Model Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollRun:
    """Tests for the PayrollRun model."""

    def test_create_run(self, payroll_run):
        assert payroll_run.run_number == 1
        assert payroll_run.status == PayrollStatus.DRAFT
        assert payroll_run.total_employees == 0

    def test_run_unique_together(self, payroll_run, payroll_period, tenant_context):
        """Cannot create two runs with same run_number for same period."""
        from apps.payroll.models import PayrollRun
        from django.db import IntegrityError
        from django.db import transaction

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                PayrollRun.objects.create(
                    payroll_period=payroll_period,
                    run_number=1,
                )

    def test_run_can_approve_draft(self, payroll_run):
        assert payroll_run.can_approve() is False

    def test_run_can_approve_processed(self, processed_run):
        assert processed_run.can_approve() is True

    def test_run_financial_totals(self, processed_run):
        assert processed_run.total_gross == Decimal("108000.00")
        assert processed_run.total_net == Decimal("95000.00")


# ──────────────────────────────────────────────────────────────
# EmployeePayroll Model Tests
# ──────────────────────────────────────────────────────────────


class TestEmployeePayroll:
    """Tests for the EmployeePayroll model."""

    def test_create_employee_payroll(self, employee_payroll_record):
        assert employee_payroll_record.days_worked == 22
        assert employee_payroll_record.basic_salary == Decimal("100000.00")
        assert employee_payroll_record.gross_salary == Decimal("108000.00")
        assert employee_payroll_record.net_salary == Decimal("100000.00")
        assert employee_payroll_record.payment_status == PaymentStatus.PENDING

    def test_employee_payroll_unique_together(self, employee_payroll_record, payroll_run, employee, tenant_context):
        """Cannot have duplicate employee payroll for same run+employee."""
        from apps.payroll.models import EmployeePayroll
        from django.db import IntegrityError
        from django.db import transaction

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                EmployeePayroll.objects.create(
                    payroll_run=payroll_run,
                    employee=employee,
                    basic_salary=Decimal("50000.00"),
                    gross_salary=Decimal("50000.00"),
                    net_salary=Decimal("50000.00"),
                )

    def test_statutory_contributions(self, employee_payroll_record):
        assert employee_payroll_record.epf_employee == Decimal("8000.00")
        assert employee_payroll_record.epf_employer == Decimal("12000.00")
        assert employee_payroll_record.etf == Decimal("3000.00")


# ──────────────────────────────────────────────────────────────
# PayrollLineItem Model Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollLineItem:
    """Tests for the PayrollLineItem model."""

    def test_create_line_item(self, payroll_line_item):
        assert payroll_line_item.line_type == LineType.EARNING
        assert payroll_line_item.final_amount == Decimal("100000.00")
        assert payroll_line_item.base_amount == Decimal("100000.00")

    def test_line_item_component_relation(self, payroll_line_item, basic_component):
        assert payroll_line_item.component == basic_component

    def test_line_items_reverse_relation(self, payroll_line_item, employee_payroll_record):
        items = employee_payroll_record.line_items.all()
        assert items.count() == 1
        assert items.first() == payroll_line_item


# ──────────────────────────────────────────────────────────────
# EPFContribution Model Tests
# ──────────────────────────────────────────────────────────────


class TestEPFContribution:
    """Tests for the EPFContribution model."""

    def test_create_epf_contribution(self, employee_payroll_record, tenant_context):
        from apps.payroll.models import EPFContribution

        epf = EPFContribution.objects.create(
            employee_payroll=employee_payroll_record,
            epf_base=Decimal("100000.00"),
            employee_amount=Decimal("8000.00"),
            employer_amount=Decimal("12000.00"),
            total_amount=Decimal("20000.00"),
            employee_rate=Decimal("8.00"),
            employer_rate=Decimal("12.00"),
            calculation_date=date(2024, 1, 25),
        )
        assert epf.total_amount == Decimal("20000.00")

    def test_epf_reverse_relation(self, employee_payroll_record, tenant_context):
        from apps.payroll.models import EPFContribution

        EPFContribution.objects.create(
            employee_payroll=employee_payroll_record,
            epf_base=Decimal("100000.00"),
            employee_amount=Decimal("8000.00"),
            employer_amount=Decimal("12000.00"),
            total_amount=Decimal("20000.00"),
            calculation_date=date(2024, 1, 25),
        )
        assert employee_payroll_record.epf_contributions.count() == 1


# ──────────────────────────────────────────────────────────────
# ETFContribution Model Tests
# ──────────────────────────────────────────────────────────────


class TestETFContribution:
    """Tests for the ETFContribution model."""

    def test_create_etf_contribution(self, employee_payroll_record, tenant_context):
        from apps.payroll.models import ETFContribution

        etf = ETFContribution.objects.create(
            employee_payroll=employee_payroll_record,
            etf_base=Decimal("100000.00"),
            employer_amount=Decimal("3000.00"),
            etf_rate=Decimal("3.00"),
            calculation_date=date(2024, 1, 25),
        )
        assert etf.employer_amount == Decimal("3000.00")


# ──────────────────────────────────────────────────────────────
# PAYECalculation Model Tests
# ──────────────────────────────────────────────────────────────


class TestPAYECalculation:
    """Tests for the PAYECalculation model."""

    def test_create_paye_calculation(self, employee_payroll_record, tenant_context):
        from apps.payroll.models import PAYECalculation

        paye = PAYECalculation.objects.create(
            employee_payroll=employee_payroll_record,
            gross_income=Decimal("108000.00"),
            taxable_income=Decimal("100000.00"),
            epf_deduction=Decimal("8000.00"),
            monthly_tax=Decimal("0.00"),
            ytd_gross=Decimal("108000.00"),
            ytd_tax=Decimal("0.00"),
            calculation_date=date(2024, 1, 25),
        )
        assert paye.taxable_income == Decimal("100000.00")


# ──────────────────────────────────────────────────────────────
# PayrollHistory Model Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollHistory:
    """Tests for the PayrollHistory model."""

    def test_create_history(self, payroll_run, user, tenant_context):
        from apps.payroll.models import PayrollHistory

        history = PayrollHistory.objects.create(
            payroll_run=payroll_run,
            action=HistoryAction.CREATED,
            previous_status="",
            new_status=PayrollStatus.DRAFT,
            performed_by=user,
            reason="Initial creation",
        )
        assert history.action == HistoryAction.CREATED
        assert history.performed_at is not None

    def test_history_ordering(self, payroll_run, user, tenant_context):
        from apps.payroll.models import PayrollHistory

        PayrollHistory.objects.create(
            payroll_run=payroll_run,
            action=HistoryAction.CREATED,
            performed_by=user,
        )
        PayrollHistory.objects.create(
            payroll_run=payroll_run,
            action=HistoryAction.PROCESSED,
            performed_by=user,
        )
        history = PayrollHistory.objects.filter(payroll_run=payroll_run)
        assert history.count() == 2
        # Newest first due to ordering = ["-performed_at"]
        assert history.first().action == HistoryAction.PROCESSED
