"""
Tests for SP09 Journal Entry models, services, and validation.

Covers:
  - JournalEntry model creation and auto-numbering
  - JournalEntryLine model constraints
  - Double-entry validation (balance, minimum lines, zero amounts)
  - JournalEntryService (create, update, post, void)
  - ApprovalService workflow (request, approve, reject)
  - TemplateService (create from template, save as template)
  - AdjustingEntryService (accruals, deferrals)
  - ReversingEntryService (create reversal, schedule reversal)
  - AccountingPeriod model
"""

import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.accounting.models import (
    AccountingPeriod,
    JournalEntry,
    JournalEntryLine,
    JournalEntryTemplate,
    RecurringEntry,
)
from apps.accounting.models.enums import (
    JournalEntryStatus,
    JournalEntryType,
    JournalSource,
    PeriodStatus,
    RecurringFrequency,
    TemplateCategory,
)
from apps.accounting.services.adjusting_service import AdjustingEntryService
from apps.accounting.services.approval_service import (
    ApprovalService,
    ApprovalServiceError,
)
from apps.accounting.services.journal_service import (
    EntryNotEditableError,
    EntryNotPostableError,
    EntryNotVoidableError,
    JournalEntryService,
)
from apps.accounting.services.reversing_service import (
    ReversingEntryService,
    ReversingServiceError,
)
from apps.accounting.services.template_service import TemplateService
from apps.accounting.validators.entry_validators import (
    validate_entry,
    validate_entry_balance,
    validate_entry_minimum_lines,
    validate_entry_not_zero,
    validate_line_amounts,
)

pytestmark = pytest.mark.django_db


# ════════════════════════════════════════════════════════════════════════
# 1. JournalEntry Model Tests
# ════════════════════════════════════════════════════════════════════════


class TestJournalEntryModel:
    """Tests for JournalEntry header model."""

    def test_create_entry(self, journal_entry):
        """Entry is created with auto-generated entry_number."""
        assert journal_entry.pk is not None
        assert journal_entry.entry_number.startswith("JE-2026-")
        assert journal_entry.entry_status == JournalEntryStatus.DRAFT

    def test_entry_number_auto_increment(self, tenant_context, user, debit_account, credit_account):
        """Successive entries get incrementing numbers."""
        e1 = JournalEntry.objects.create(
            entry_date=datetime.date(2026, 3, 1),
            description="First",
            created_by=user,
        )
        e2 = JournalEntry.objects.create(
            entry_date=datetime.date(2026, 3, 2),
            description="Second",
            created_by=user,
        )
        seq1 = int(e1.entry_number.split("-")[2])
        seq2 = int(e2.entry_number.split("-")[2])
        assert seq2 == seq1 + 1

    def test_entry_str(self, journal_entry):
        assert journal_entry.entry_number in str(journal_entry)

    def test_is_balanced_property(self, journal_entry):
        assert journal_entry.is_balanced is True

    def test_is_draft_property(self, journal_entry):
        assert journal_entry.is_draft is True
        assert journal_entry.is_editable is True

    def test_is_posted_property(self, journal_entry):
        assert journal_entry.is_posted is False

    def test_is_void_property(self, journal_entry):
        assert journal_entry.is_void is False


# ════════════════════════════════════════════════════════════════════════
# 2. JournalEntryLine Model Tests
# ════════════════════════════════════════════════════════════════════════


class TestJournalEntryLineModel:
    """Tests for JournalEntryLine model."""

    def test_debit_line(self, journal_entry):
        debit_line = journal_entry.lines.filter(debit_amount__gt=0).first()
        assert debit_line.is_debit is True
        assert debit_line.is_credit is False
        assert debit_line.net_amount == Decimal("10000.00")

    def test_credit_line(self, journal_entry):
        credit_line = journal_entry.lines.filter(credit_amount__gt=0).first()
        assert credit_line.is_credit is True
        assert credit_line.is_debit is False
        assert credit_line.net_amount == Decimal("-10000.00")

    def test_line_str_debit(self, journal_entry):
        line = journal_entry.lines.filter(debit_amount__gt=0).first()
        assert "DR" in str(line)

    def test_line_str_credit(self, journal_entry):
        line = journal_entry.lines.filter(credit_amount__gt=0).first()
        assert "CR" in str(line)


# ════════════════════════════════════════════════════════════════════════
# 3. Double-Entry Validation Tests
# ════════════════════════════════════════════════════════════════════════


class TestDoubleEntryValidation:
    """Tests for double-entry bookkeeping validators."""

    def test_balanced_entry_passes(self, journal_entry):
        """Balanced entry passes validation."""
        validate_entry_balance(journal_entry)  # Should not raise

    def test_unbalanced_entry_fails(self, tenant_context, user, debit_account, credit_account):
        """Unbalanced entry fails validation."""
        entry = JournalEntry.objects.create(
            entry_date=datetime.date(2026, 1, 20),
            description="Unbalanced",
            created_by=user,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=debit_account,
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=credit_account,
            debit_amount=Decimal("0"),
            credit_amount=Decimal("50.00"),
        )
        entry.total_debit = Decimal("100.00")
        entry.total_credit = Decimal("50.00")
        entry.save(update_fields=["total_debit", "total_credit"])

        with pytest.raises(ValidationError):
            validate_entry_balance(entry)

    def test_zero_amount_entry_fails(self, tenant_context, user, debit_account, credit_account):
        """Entry with zero totals fails validation."""
        entry = JournalEntry.objects.create(
            entry_date=datetime.date(2026, 1, 20),
            description="Zero",
            created_by=user,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=debit_account,
            debit_amount=Decimal("0"),
            credit_amount=Decimal("0"),
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=credit_account,
            debit_amount=Decimal("0"),
            credit_amount=Decimal("0"),
        )
        entry.total_debit = Decimal("0")
        entry.total_credit = Decimal("0")
        entry.save(update_fields=["total_debit", "total_credit"])

        with pytest.raises(ValidationError):
            validate_entry_not_zero(entry)

    def test_minimum_lines_fails_with_one_line(self, tenant_context, user, debit_account):
        """Entry with fewer than 2 lines fails."""
        entry = JournalEntry.objects.create(
            entry_date=datetime.date(2026, 1, 20),
            description="Single line",
            created_by=user,
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=debit_account,
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0"),
        )
        with pytest.raises(ValidationError):
            validate_entry_minimum_lines(entry)

    def test_line_with_both_debit_and_credit_fails(self, journal_entry, debit_account):
        """A line with both debit and credit fails."""
        line = JournalEntryLine(
            journal_entry=journal_entry,
            account=debit_account,
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("50.00"),
        )
        with pytest.raises(ValidationError):
            validate_line_amounts(line)

    def test_negative_amount_fails(self, journal_entry, debit_account):
        """A line with negative amount fails."""
        line = JournalEntryLine(
            journal_entry=journal_entry,
            account=debit_account,
            debit_amount=Decimal("-100.00"),
            credit_amount=Decimal("0"),
        )
        with pytest.raises(ValidationError):
            validate_line_amounts(line)


# ════════════════════════════════════════════════════════════════════════
# 4. JournalEntryService Tests
# ════════════════════════════════════════════════════════════════════════


class TestJournalEntryService:
    """Tests for JournalEntryService CRUD and workflow."""

    def test_create_entry(self, tenant_context, user, debit_account, credit_account):
        lines = [
            {"account": debit_account, "debit_amount": Decimal("5000"), "credit_amount": Decimal("0")},
            {"account": credit_account, "debit_amount": Decimal("0"), "credit_amount": Decimal("5000")},
        ]
        entry = JournalEntryService.create_entry(
            entry_date=datetime.date(2026, 2, 1),
            lines_data=lines,
            description="Service test",
            created_by=user,
        )
        assert entry.pk is not None
        assert entry.total_debit == Decimal("5000")
        assert entry.lines.count() == 2

    def test_update_entry(self, journal_entry, debit_account, credit_account):
        updated = JournalEntryService.update_entry(
            journal_entry,
            description="Updated description",
        )
        assert updated.description == "Updated description"

    def test_update_non_draft_raises(self, journal_entry, user):
        journal_entry.entry_status = JournalEntryStatus.POSTED
        journal_entry.save()
        with pytest.raises(EntryNotEditableError):
            JournalEntryService.update_entry(journal_entry, description="fail")

    def test_post_entry(self, journal_entry, user):
        posted = JournalEntryService.post_entry(journal_entry, posted_by=user)
        assert posted.entry_status == JournalEntryStatus.POSTED
        assert posted.posted_by == user
        assert posted.posted_at is not None

    def test_post_already_posted_raises(self, journal_entry, user):
        JournalEntryService.post_entry(journal_entry, posted_by=user)
        with pytest.raises(EntryNotPostableError):
            JournalEntryService.post_entry(journal_entry, posted_by=user)

    def test_void_entry(self, journal_entry, user):
        JournalEntryService.post_entry(journal_entry, posted_by=user)
        voided, reversal = JournalEntryService.void_entry(
            journal_entry, voided_by=user, reason="Error"
        )
        assert voided.entry_status == JournalEntryStatus.VOID
        assert reversal.entry_type == JournalEntryType.REVERSING
        assert reversal.reversal_of == journal_entry

    def test_void_draft_raises(self, journal_entry, user):
        with pytest.raises(EntryNotVoidableError):
            JournalEntryService.void_entry(journal_entry, voided_by=user)


# ════════════════════════════════════════════════════════════════════════
# 5. ApprovalService Tests
# ════════════════════════════════════════════════════════════════════════


class TestApprovalService:
    """Tests for the approval workflow."""

    def test_auto_approve_below_threshold(self, journal_entry):
        service = ApprovalService(auto_approve_threshold=Decimal("50000"))
        result = service.request_approval(journal_entry)
        assert result.entry_status == JournalEntryStatus.APPROVED

    def test_pending_approval_above_threshold(self, journal_entry):
        service = ApprovalService(auto_approve_threshold=Decimal("5000"))
        result = service.request_approval(journal_entry)
        assert result.entry_status == JournalEntryStatus.PENDING_APPROVAL

    def test_approve_pending(self, journal_entry, second_user):
        service = ApprovalService(auto_approve_threshold=Decimal("5000"))
        service.request_approval(journal_entry)
        result = service.approve_entry(journal_entry, approved_by=second_user)
        assert result.entry_status == JournalEntryStatus.APPROVED

    def test_reject_pending(self, journal_entry, second_user):
        service = ApprovalService(auto_approve_threshold=Decimal("5000"))
        service.request_approval(journal_entry)
        result = service.reject_entry(journal_entry, rejected_by=second_user, reason="Incorrect")
        assert result.entry_status == JournalEntryStatus.DRAFT

    def test_approve_non_pending_raises(self, journal_entry, second_user):
        service = ApprovalService()
        with pytest.raises(ApprovalServiceError):
            service.approve_entry(journal_entry, approved_by=second_user)

    def test_segregation_of_duties(self, journal_entry, user):
        """Same user who created cannot approve."""
        service = ApprovalService(auto_approve_threshold=Decimal("5000"))
        service.request_approval(journal_entry)
        with pytest.raises(ApprovalServiceError):
            service.approve_entry(journal_entry, approved_by=user)

    def test_request_approval_non_draft_raises(self, journal_entry, user):
        service = ApprovalService()
        JournalEntryService.post_entry(journal_entry, posted_by=user)
        with pytest.raises(ApprovalServiceError):
            service.request_approval(journal_entry)


# ════════════════════════════════════════════════════════════════════════
# 6. TemplateService Tests
# ════════════════════════════════════════════════════════════════════════


class TestTemplateService:
    """Tests for template creation and usage."""

    def test_save_as_template(self, journal_entry, user):
        template = TemplateService.save_as_template(
            entry=journal_entry,
            name="Test Template",
            created_by=user,
        )
        assert template.pk is not None
        assert template.name == "Test Template"
        assert len(template.template_lines["lines"]) == 2

    def test_create_from_template(self, tenant_context, user, debit_account, credit_account):
        template = JournalEntryTemplate.objects.create(
            name="Rent Template",
            template_lines={
                "lines": [
                    {
                        "account_code": debit_account.code,
                        "description": "Rent debit",
                        "debit": "{{amount}}",
                        "credit": None,
                    },
                    {
                        "account_code": credit_account.code,
                        "description": "Rent credit",
                        "debit": None,
                        "credit": "{{amount}}",
                    },
                ]
            },
            category=TemplateCategory.GENERAL,
            created_by=user,
        )
        entry = TemplateService.create_from_template(
            template=template,
            entry_date=datetime.date(2026, 4, 1),
            amounts={"amount": Decimal("25000.00")},
            created_by=user,
        )
        assert entry.pk is not None
        assert entry.total_debit == Decimal("25000.00")
        assert entry.total_credit == Decimal("25000.00")
        assert entry.lines.count() == 2


# ════════════════════════════════════════════════════════════════════════
# 7. AdjustingEntryService Tests
# ════════════════════════════════════════════════════════════════════════


class TestAdjustingEntryService:
    """Tests for accrual and deferral entries."""

    def test_create_accrual_entry(self, tenant_context, user, debit_account, credit_account):
        entry = AdjustingEntryService.create_accrual_entry(
            entry_date=datetime.date(2026, 1, 31),
            expense_account=debit_account,
            liability_account=credit_account,
            amount=Decimal("15000.00"),
            description="Accrued salaries",
            created_by=user,
        )
        assert entry.entry_type == JournalEntryType.ADJUSTING
        assert entry.total_debit == Decimal("15000.00")
        assert entry.is_balanced

    def test_create_deferral_entry(self, tenant_context, user, debit_account, credit_account):
        entry = AdjustingEntryService.create_deferral_entry(
            entry_date=datetime.date(2026, 1, 31),
            deferred_account=debit_account,
            recognised_account=credit_account,
            amount=Decimal("8000.00"),
            description="Prepaid insurance",
            created_by=user,
        )
        assert entry.entry_type == JournalEntryType.ADJUSTING
        assert entry.total_debit == Decimal("8000.00")
        assert entry.is_balanced


# ════════════════════════════════════════════════════════════════════════
# 8. ReversingEntryService Tests
# ════════════════════════════════════════════════════════════════════════


class TestReversingEntryService:
    """Tests for reversing entries."""

    def test_create_reversal(self, journal_entry, user):
        JournalEntryService.post_entry(journal_entry, posted_by=user)
        reversal = ReversingEntryService.create_reversal(
            entry=journal_entry,
            created_by=user,
        )
        assert reversal.entry_type == JournalEntryType.REVERSING
        assert reversal.reversal_of == journal_entry
        assert reversal.total_debit == journal_entry.total_debit
        # Debits and credits should be swapped
        original_debit_line = journal_entry.lines.filter(debit_amount__gt=0).first()
        reversal_line = reversal.lines.filter(
            account=original_debit_line.account
        ).first()
        assert reversal_line.credit_amount == original_debit_line.debit_amount

    def test_create_reversal_non_posted_raises(self, journal_entry, user):
        with pytest.raises(ReversingServiceError):
            ReversingEntryService.create_reversal(entry=journal_entry, created_by=user)

    def test_schedule_reversal(self, tenant_context, user, debit_account, credit_account):
        """Schedule reversal creates entry on first day of next month."""
        entry = JournalEntryService.create_entry(
            entry_date=datetime.date(2026, 1, 31),
            lines_data=[
                {"account": debit_account, "debit_amount": Decimal("2000"), "credit_amount": Decimal("0")},
                {"account": credit_account, "debit_amount": Decimal("0"), "credit_amount": Decimal("2000")},
            ],
            entry_type=JournalEntryType.ADJUSTING,
            created_by=user,
        )
        JournalEntryService.post_entry(entry, posted_by=user)
        reversal = ReversingEntryService.schedule_reversal(entry=entry, created_by=user)
        assert reversal.entry_date == datetime.date(2026, 2, 1)

    def test_schedule_reversal_non_adjusting_raises(self, journal_entry, user):
        JournalEntryService.post_entry(journal_entry, posted_by=user)
        with pytest.raises(ReversingServiceError):
            ReversingEntryService.schedule_reversal(entry=journal_entry, created_by=user)

    def test_double_reversal_raises(self, journal_entry, user):
        """Cannot reverse an entry that already has a reversal."""
        JournalEntryService.post_entry(journal_entry, posted_by=user)
        ReversingEntryService.create_reversal(entry=journal_entry, created_by=user)
        with pytest.raises(ReversingServiceError):
            ReversingEntryService.create_reversal(entry=journal_entry, created_by=user)


# ════════════════════════════════════════════════════════════════════════
# 9. AccountingPeriod Model Tests
# ════════════════════════════════════════════════════════════════════════


class TestAccountingPeriodModel:
    """Tests for the AccountingPeriod model."""

    def test_create_period(self, tenant_context):
        period = AccountingPeriod.objects.create(
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 31),
            fiscal_year=2026,
            period_number=1,
            name="January 2026",
        )
        assert period.pk is not None
        assert period.is_open is True

    def test_period_status_lifecycle(self, tenant_context):
        period = AccountingPeriod.objects.create(
            start_date=datetime.date(2026, 2, 1),
            end_date=datetime.date(2026, 2, 28),
            fiscal_year=2026,
            period_number=2,
            name="February 2026",
        )
        assert period.is_open

        period.status = PeriodStatus.CLOSED
        period.save()
        assert period.is_closed

        period.status = PeriodStatus.LOCKED
        period.save()
        assert period.is_locked

    def test_period_date_validation(self, tenant_context):
        period = AccountingPeriod(
            start_date=datetime.date(2026, 3, 31),
            end_date=datetime.date(2026, 3, 1),
            fiscal_year=2026,
            period_number=3,
        )
        with pytest.raises(ValidationError):
            period.clean()


# ════════════════════════════════════════════════════════════════════════
# 10. RecurringEntry & Template Model Tests
# ════════════════════════════════════════════════════════════════════════


class TestRecurringEntryModel:
    """Tests for RecurringEntry model."""

    def test_create_recurring_entry(self, tenant_context, user, debit_account, credit_account):
        template = JournalEntryTemplate.objects.create(
            name="Monthly Rent",
            template_lines={
                "lines": [
                    {"account_code": debit_account.code, "description": "Rent", "debit": "{{amount}}", "credit": None},
                    {"account_code": credit_account.code, "description": "Bank", "debit": None, "credit": "{{amount}}"},
                ]
            },
            created_by=user,
        )
        recurring = RecurringEntry.objects.create(
            template=template,
            frequency=RecurringFrequency.MONTHLY,
            start_date=datetime.date(2026, 1, 1),
            next_run_date=datetime.date(2026, 1, 1),
            created_by=user,
        )
        assert recurring.pk is not None
        assert recurring.is_active is True
        assert recurring.frequency == RecurringFrequency.MONTHLY
