"""Tests for Payslip models — Task 85."""

import pytest
from datetime import date
from decimal import Decimal

from apps.payslip.constants import PayslipStatus

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────────────────────
# Payslip Model Tests
# ──────────────────────────────────────────────────────────────


class TestPayslipModel:
    """Tests for the core Payslip model."""

    def test_create_payslip(self, payslip):
        """Payslip is created with DRAFT status and auto slip number."""
        assert payslip.pk is not None
        assert payslip.status == PayslipStatus.DRAFT
        assert payslip.slip_number.startswith("PAY-2026-01-")
        assert payslip.email_sent is False
        assert payslip.view_count == 0
        assert payslip.download_count == 0

    def test_slip_number_auto_generated(self, payslip):
        """slip_number is auto-generated on first save."""
        assert payslip.slip_number == "PAY-2026-01-001"

    def test_unique_employee_period_constraint(
        self, tenant_context, payslip, employee, payroll_period, employee_payroll
    ):
        """Cannot create two payslips for same employee + period."""
        from django.db import IntegrityError, transaction
        from apps.payslip.models import Payslip

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Payslip.objects.create(
                    employee=employee,
                    payroll_period=payroll_period,
                    employee_payroll=employee_payroll,
                )

    def test_str_representation(self, payslip):
        """__str__ returns slip_number - employee."""
        s = str(payslip)
        assert payslip.slip_number in s

    def test_has_pdf_false_by_default(self, payslip):
        """has_pdf is False when no file attached."""
        assert payslip.has_pdf is False
        assert payslip.pdf_url is None

    def test_record_view(self, payslip):
        """record_view increments view_count and sets first_viewed_at."""
        payslip.status = PayslipStatus.GENERATED
        payslip.save(update_fields=["status"])

        payslip.record_view()
        payslip.refresh_from_db()

        assert payslip.view_count == 1
        assert payslip.first_viewed_at is not None
        assert payslip.status == PayslipStatus.VIEWED

    def test_record_view_increments(self, payslip):
        """Multiple views increment count, first_viewed_at stays."""
        payslip.record_view()
        first_view = payslip.first_viewed_at

        payslip.record_view()
        payslip.refresh_from_db()

        assert payslip.view_count == 2
        assert payslip.first_viewed_at == first_view

    def test_record_download(self, payslip):
        """record_download sets first_downloaded_at and increments count."""
        payslip.record_download()
        payslip.refresh_from_db()

        assert payslip.download_count == 1
        assert payslip.first_downloaded_at is not None
        assert payslip.status == PayslipStatus.DOWNLOADED

    def test_record_download_increments(self, payslip):
        """Multiple downloads increment count."""
        payslip.record_download()
        payslip.record_download()
        payslip.refresh_from_db()

        assert payslip.download_count == 2

    def test_mark_generated(self, payslip, admin_user):
        """mark_generated updates status and generated_at."""
        payslip.mark_generated(user=admin_user)
        payslip.refresh_from_db()

        assert payslip.status == PayslipStatus.GENERATED
        assert payslip.generated_at is not None
        assert payslip.generated_by == admin_user

    def test_mark_sent(self, payslip):
        """mark_sent updates email fields."""
        payslip.mark_sent("kamal@example.com")
        payslip.refresh_from_db()

        assert payslip.status == PayslipStatus.SENT
        assert payslip.email_sent is True
        assert payslip.sent_to == "kamal@example.com"
        assert payslip.sent_at is not None

    def test_ordering(self, tenant_context, employee, employee_payroll):
        """Payslips ordered by -period_year, -period_month."""
        from apps.payroll.models import PayrollPeriod
        from apps.payslip.models import Payslip

        period_feb = PayrollPeriod.objects.create(
            period_month=2,
            period_year=2026,
            name="February 2026",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 28),
            pay_date=date(2026, 2, 28),
        )
        # employee_payroll is linked to employee via payroll_run
        from apps.payroll.models import EmployeePayroll, PayrollRun
        run2 = PayrollRun.objects.create(
            payroll_period=period_feb,
        )
        ep2 = EmployeePayroll.objects.create(
            payroll_run=run2,
            employee=employee,
            days_worked=20,
        )
        Payslip.objects.create(
            employee=employee,
            payroll_period=period_feb,
            employee_payroll=ep2,
        )

        payslips = list(Payslip.objects.for_employee(employee))
        assert payslips[0].payroll_period.period_month == 2  # Feb first (newest)


# ──────────────────────────────────────────────────────────────
# PayslipManager Tests
# ──────────────────────────────────────────────────────────────


class TestPayslipManager:
    """Tests for PayslipManager queryset methods."""

    def test_for_employee(self, payslip, employee):
        """for_employee returns payslips for given employee."""
        from apps.payslip.models import Payslip

        qs = Payslip.objects.for_employee(employee)
        assert qs.count() == 1
        assert qs.first() == payslip

    def test_for_period(self, payslip, payroll_period):
        """for_period returns payslips for given period."""
        from apps.payslip.models import Payslip

        qs = Payslip.objects.for_period(payroll_period)
        assert qs.count() == 1

    def test_pending_generation(self, payslip):
        """pending_generation returns DRAFT payslips."""
        from apps.payslip.models import Payslip

        assert Payslip.objects.pending_generation().count() == 1

    def test_pending_email(self, payslip):
        """pending_email returns GENERATED + not emailed payslips."""
        from apps.payslip.models import Payslip

        assert Payslip.objects.pending_email().count() == 0
        payslip.status = PayslipStatus.GENERATED
        payslip.save(update_fields=["status"])
        assert Payslip.objects.pending_email().count() == 1


# ──────────────────────────────────────────────────────────────
# PayslipEarning / Deduction Tests
# ──────────────────────────────────────────────────────────────


class TestPayslipLineItems:
    """Tests for PayslipEarning, PayslipDeduction, PayslipEmployerContribution."""

    def test_create_earning(self, payslip_with_lines):
        """Earnings are created and linked to payslip."""
        assert payslip_with_lines.earnings.count() == 2

    def test_create_deduction(self, payslip_with_lines):
        """Deductions are created and linked to payslip."""
        assert payslip_with_lines.deductions.count() == 1

    def test_earning_unique_constraint(self, payslip):
        """Cannot duplicate component_code on same payslip."""
        from django.db import IntegrityError, transaction
        from apps.payslip.models import PayslipEarning

        PayslipEarning.objects.create(
            payslip=payslip,
            component_code="BASIC",
            component_name="Basic Salary",
            amount=Decimal("50000.00"),
            display_order=1,
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                PayslipEarning.objects.create(
                    payslip=payslip,
                    component_code="BASIC",
                    component_name="Basic Salary",
                    amount=Decimal("50000.00"),
                    display_order=2,
                )

    def test_employer_contribution(self, payslip):
        """PayslipEmployerContribution can be created."""
        from apps.payslip.models import PayslipEmployerContribution

        contrib = PayslipEmployerContribution.objects.create(
            payslip=payslip,
            component_code="EPF_ER",
            component_name="EPF (Employer)",
            amount=Decimal("6000.00"),
            display_order=1,
        )
        assert contrib.pk is not None
        assert payslip.employer_contributions.count() == 1

    def test_cascade_delete(self, payslip_with_lines):
        """Deleting payslip cascades to line items."""
        payslip_id = payslip_with_lines.pk
        payslip_with_lines.delete()

        from apps.payslip.models import PayslipEarning, PayslipDeduction
        assert PayslipEarning.objects.filter(payslip_id=payslip_id).count() == 0
        assert PayslipDeduction.objects.filter(payslip_id=payslip_id).count() == 0


# ──────────────────────────────────────────────────────────────
# PayslipTemplate Tests
# ──────────────────────────────────────────────────────────────


class TestPayslipTemplate:
    """Tests for PayslipTemplate model."""

    def test_create_template(self, payslip_template):
        """Template is created with defaults."""
        assert payslip_template.is_active is True
        assert payslip_template.paper_size == "A4"
        assert payslip_template.primary_color == "#2C3E50"

    def test_invalid_color_validation(self, payslip_template):
        """clean() raises ValidationError for invalid hex color."""
        from django.core.exceptions import ValidationError

        payslip_template.primary_color = "not-a-color"
        with pytest.raises(ValidationError):
            payslip_template.clean()

    def test_valid_color_passes(self, payslip_template):
        """clean() accepts valid hex colors."""
        payslip_template.primary_color = "#FF5733"
        payslip_template.secondary_color = "#333333"
        payslip_template.clean()  # Should not raise


# ──────────────────────────────────────────────────────────────
# PayslipBatch Tests
# ──────────────────────────────────────────────────────────────


class TestPayslipBatch:
    """Tests for PayslipBatch model."""

    def test_create_batch(self, tenant_context, payroll_period, admin_user):
        """Batch can be created with PENDING status."""
        from apps.payslip.models import PayslipBatch

        batch = PayslipBatch.objects.create(
            payroll_period=payroll_period,
            initiated_by=admin_user,
            batch_type="GENERATION",
            status="PENDING",
            total_count=10,
        )
        assert batch.pk is not None
        assert batch.success_count == 0
        assert batch.failed_count == 0

    def test_progress_percent(self, tenant_context, payroll_period, admin_user):
        """progress_percent calculates correctly."""
        from apps.payslip.models import PayslipBatch

        batch = PayslipBatch.objects.create(
            payroll_period=payroll_period,
            initiated_by=admin_user,
            batch_type="GENERATION",
            status="PROCESSING",
            total_count=10,
            success_count=3,
            failed_count=2,
        )
        assert batch.progress_percent == 50.0

    def test_progress_percent_zero_total(self, tenant_context, payroll_period, admin_user):
        """progress_percent returns 0 for zero total."""
        from apps.payslip.models import PayslipBatch

        batch = PayslipBatch.objects.create(
            payroll_period=payroll_period,
            initiated_by=admin_user,
            batch_type="GENERATION",
            status="PENDING",
            total_count=0,
        )
        assert batch.progress_percent == 0.0
