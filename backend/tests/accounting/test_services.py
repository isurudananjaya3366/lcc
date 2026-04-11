"""Tests for Group D — COATemplate, services, validators, archive."""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.accounting.models import Account, COATemplate, IndustryType
from apps.accounting.models.enums import AccountStatus
from apps.accounting.models.journal import JournalEntry
from apps.accounting.services.balance_service import AccountBalanceService
from apps.accounting.services.coa_initializer import (
    COAInitializerService,
    InvalidTemplateException,
    TenantAlreadyInitializedException,
)
from apps.accounting.services.validators import CODE_RANGES, AccountValidator

# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════
SAMPLE_TEMPLATE_ACCOUNTS = [
    {
        "code": "1000",
        "name": "Assets",
        "account_type": "asset",
        "is_header": True,
        "is_system": False,
        "parent_code": None,
        "description": "Root asset account.",
    },
    {
        "code": "1100",
        "name": "Cash",
        "account_type": "asset",
        "is_header": False,
        "is_system": False,
        "parent_code": "1000",
        "description": "Cash account.",
    },
    {
        "code": "2000",
        "name": "Liabilities",
        "account_type": "liability",
        "is_header": True,
        "is_system": False,
        "parent_code": None,
        "description": "Root liability.",
    },
]


# ═══════════════════════════════════════════════════════════════════
# COATemplate model tests
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestCOATemplateModel:
    def test_create_template(self, tenant_context):
        tpl = COATemplate.objects.create(
            template_name="Retail Standard",
            industry=IndustryType.RETAIL,
            template_accounts=SAMPLE_TEMPLATE_ACCOUNTS,
            description="Standard retail COA.",
        )
        assert tpl.pk is not None
        assert str(tpl) == "Retail Standard"

    def test_unique_template_name(self, tenant_context):
        COATemplate.objects.create(
            template_name="Unique Name",
            industry=IndustryType.SERVICE,
        )
        with pytest.raises(Exception):
            COATemplate.objects.create(
                template_name="Unique Name",
                industry=IndustryType.RETAIL,
            )

    def test_account_count_property(self, tenant_context):
        tpl = COATemplate(template_accounts=SAMPLE_TEMPLATE_ACCOUNTS)
        assert tpl.account_count == 3

    def test_account_count_empty(self, tenant_context):
        tpl = COATemplate(template_accounts=[])
        assert tpl.account_count == 0

    def test_get_accounts_by_type(self, tenant_context):
        tpl = COATemplate(template_accounts=SAMPLE_TEMPLATE_ACCOUNTS)
        assets = tpl.get_accounts_by_type("asset")
        assert len(assets) == 2

    def test_get_root_accounts(self, tenant_context):
        tpl = COATemplate(template_accounts=SAMPLE_TEMPLATE_ACCOUNTS)
        roots = tpl.get_root_accounts()
        assert len(roots) == 2

    def test_is_active_default(self, tenant_context):
        tpl = COATemplate.objects.create(
            template_name="Active Test",
            industry=IndustryType.RETAIL,
        )
        assert tpl.is_active is True

    def test_industry_choices(self, tenant_context):
        assert len(IndustryType.choices) >= 5

    def test_meta_table_name(self, tenant_context):
        assert COATemplate._meta.db_table == "accounting_coa_template"


# ═══════════════════════════════════════════════════════════════════
# COAInitializerService tests
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestCOAInitializerService:
    def test_has_accounts_empty(self, tenant_context):
        svc = COAInitializerService()
        assert svc.has_accounts() is False

    def test_create_default(self, tenant_context):
        svc = COAInitializerService()
        result = svc.create_default()
        assert result["total"] > 0
        assert "accounts_by_type" in result
        assert Account.objects.count() == result["total"]

    def test_create_default_prevents_duplicate(self, tenant_context):
        svc = COAInitializerService()
        svc.create_default()
        with pytest.raises(TenantAlreadyInitializedException):
            svc.create_default()

    def test_create_default_force(self, tenant_context):
        svc = COAInitializerService()
        svc.create_default()
        Account.objects.filter(code="1000").update(name="Modified")
        result = svc.create_default(force=True)
        assert Account.objects.get(code="1000").name == "Assets"
        assert result["total"] > 0

    def test_create_from_template(self, tenant_context):
        tpl = COATemplate.objects.create(
            template_name="Test Template",
            industry=IndustryType.SERVICE,
            template_accounts=SAMPLE_TEMPLATE_ACCOUNTS,
        )
        svc = COAInitializerService()
        result = svc.create_from_template(tpl.pk)
        assert result["total"] == 3
        assert result["template_name"] == "Test Template"

    def test_create_from_template_invalid(self, tenant_context):
        import uuid

        svc = COAInitializerService()
        with pytest.raises(InvalidTemplateException):
            svc.create_from_template(uuid.uuid4())

    def test_create_from_inactive_template(self, tenant_context):
        tpl = COATemplate.objects.create(
            template_name="Inactive",
            industry=IndustryType.RETAIL,
            template_accounts=SAMPLE_TEMPLATE_ACCOUNTS,
            is_active=False,
        )
        svc = COAInitializerService()
        with pytest.raises(InvalidTemplateException):
            svc.create_from_template(tpl.pk)

    def test_create_from_empty_template(self, tenant_context):
        tpl = COATemplate.objects.create(
            template_name="Empty",
            industry=IndustryType.RETAIL,
            template_accounts=[],
        )
        svc = COAInitializerService()
        with pytest.raises(InvalidTemplateException):
            svc.create_from_template(tpl.pk)


# ═══════════════════════════════════════════════════════════════════
# AccountBalanceService tests
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestAccountBalanceService:
    def _create_account(self):
        return Account.objects.create(
            code="1101",
            name="Cash on Hand",
            account_type="asset",
            opening_balance=Decimal("1000.00"),
        )

    def test_calculate_balance_no_entries(self, tenant_context):
        acc = self._create_account()
        bal = AccountBalanceService.calculate_balance(acc.pk)
        assert bal == Decimal("1000.00")

    def test_calculate_balance_with_entries(self, tenant_context, user):
        acc = self._create_account()
        JournalEntry.objects.create(
            reference_number="JE-001",
            account=acc,
            debit=Decimal("500.00"),
            status="posted",
            created_by=user,
        )
        JournalEntry.objects.create(
            reference_number="JE-002",
            account=acc,
            credit=Decimal("200.00"),
            status="posted",
            created_by=user,
        )
        bal = AccountBalanceService.calculate_balance(acc.pk)
        # asset: opening + debits - credits = 1000 + 500 - 200
        assert bal == Decimal("1300.00")

    def test_draft_entries_excluded(self, tenant_context, user):
        acc = self._create_account()
        JournalEntry.objects.create(
            reference_number="JE-DRAFT",
            account=acc,
            debit=Decimal("999.00"),
            status="draft",
            created_by=user,
        )
        bal = AccountBalanceService.calculate_balance(acc.pk)
        assert bal == Decimal("1000.00")

    def test_credit_normal_balance(self, tenant_context, user):
        acc = Account.objects.create(
            code="4100",
            name="Sales Revenue",
            account_type="revenue",
        )
        JournalEntry.objects.create(
            reference_number="JE-R01",
            account=acc,
            credit=Decimal("750.00"),
            status="posted",
            created_by=user,
        )
        bal = AccountBalanceService.calculate_balance(acc.pk)
        assert bal == Decimal("750.00")

    def test_update_balance(self, tenant_context):
        acc = self._create_account()
        new_bal = AccountBalanceService.update_balance(acc.pk)
        acc.refresh_from_db()
        assert acc.current_balance == new_bal

    def test_get_children_balances(self, tenant_context):
        parent = Account.objects.create(
            code="1100",
            name="Cash",
            account_type="asset",
            is_header=True,
        )
        Account.objects.create(
            code="1101",
            name="Cash on Hand",
            account_type="asset",
            parent=parent,
            opening_balance=Decimal("500.00"),
        )
        Account.objects.create(
            code="1102",
            name="Petty Cash",
            account_type="asset",
            parent=parent,
            opening_balance=Decimal("100.00"),
        )
        Account.objects.rebuild()
        result = AccountBalanceService.get_children_balances(parent.pk)
        assert result["1101"] == Decimal("500.00")
        assert result["1102"] == Decimal("100.00")
        assert result["aggregate"] == Decimal("600.00")

    def test_calculate_balance_historical(self, tenant_context, user):
        from datetime import date

        acc = self._create_account()
        JournalEntry.objects.create(
            reference_number="JE-H1",
            account=acc,
            debit=Decimal("100.00"),
            status="posted",
            entry_date=date(2025, 1, 10),
            created_by=user,
        )
        JournalEntry.objects.create(
            reference_number="JE-H2",
            account=acc,
            debit=Decimal("200.00"),
            status="posted",
            entry_date=date(2025, 2, 15),
            created_by=user,
        )
        bal = AccountBalanceService.calculate_balance(
            acc.pk, as_of_date=date(2025, 1, 31)
        )
        assert bal == Decimal("1100.00")


# ═══════════════════════════════════════════════════════════════════
# AccountValidator tests
# ═══════════════════════════════════════════════════════════════════
class TestAccountValidatorCodeFormat:
    def test_valid_code(self):
        assert AccountValidator.validate_code_format("1000") is True

    def test_short_code(self):
        with pytest.raises(ValidationError):
            AccountValidator.validate_code_format("100")

    def test_alpha_code(self):
        with pytest.raises(ValidationError):
            AccountValidator.validate_code_format("ABCD")

    def test_empty_code(self):
        with pytest.raises(ValidationError):
            AccountValidator.validate_code_format("")


class TestAccountValidatorCodeRange:
    def test_asset_in_range(self):
        assert AccountValidator.validate_code_range("1500", "asset") is True

    def test_asset_out_of_range(self):
        with pytest.raises(ValidationError):
            AccountValidator.validate_code_range("5000", "asset")

    def test_expense_in_range(self):
        assert AccountValidator.validate_code_range("5500", "expense") is True

    def test_expense_out_of_range(self):
        with pytest.raises(ValidationError):
            AccountValidator.validate_code_range("6500", "expense")

    def test_unknown_type(self):
        with pytest.raises(ValidationError):
            AccountValidator.validate_code_range("1000", "bogus")

    def test_boundary_min(self):
        assert AccountValidator.validate_code_range("1000", "asset") is True

    def test_boundary_max(self):
        assert AccountValidator.validate_code_range("1999", "asset") is True

    def test_just_below_min(self):
        with pytest.raises(ValidationError):
            AccountValidator.validate_code_range("0999", "asset")

    def test_just_above_max(self):
        with pytest.raises(ValidationError):
            AccountValidator.validate_code_range("2000", "asset")


@pytest.mark.django_db
class TestAccountValidatorDeletion:
    def test_can_delete_leaf(self, tenant_context):
        acc = Account.objects.create(
            code="9900",
            name="Deletable",
            account_type="expense",
        )
        assert AccountValidator.validate_can_delete(acc.pk) is True

    def test_cannot_delete_system(self, tenant_context):
        acc = Account.objects.create(
            code="9901",
            name="System",
            account_type="expense",
            is_system=True,
        )
        with pytest.raises(ValidationError):
            AccountValidator.validate_can_delete(acc.pk)

    def test_cannot_delete_with_children(self, tenant_context):
        parent = Account.objects.create(
            code="9800",
            name="Parent",
            account_type="expense",
            is_header=True,
        )
        Account.objects.create(
            code="9801",
            name="Child",
            account_type="expense",
            parent=parent,
        )
        Account.objects.rebuild()
        with pytest.raises(ValidationError):
            AccountValidator.validate_can_delete(parent.pk)

    def test_cannot_delete_with_entries(self, tenant_context, user):
        acc = Account.objects.create(
            code="9902",
            name="Has Entry",
            account_type="expense",
        )
        JournalEntry.objects.create(
            reference_number="JE-DEL",
            account=acc,
            debit=Decimal("10.00"),
            status="draft",
            created_by=user,
        )
        with pytest.raises(ValidationError):
            AccountValidator.validate_can_delete(acc.pk)


# ═══════════════════════════════════════════════════════════════════
# Archive tests
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestArchive:
    def test_archive_account(self, tenant_context):
        acc = Account.objects.create(
            code="9700",
            name="Archivable",
            account_type="expense",
        )
        result = AccountValidator.archive_account(acc.pk)
        assert result.status == AccountStatus.ARCHIVED
        assert result.is_active is False

    def test_archive_idempotent(self, tenant_context):
        acc = Account.objects.create(
            code="9701",
            name="Already Archived",
            account_type="expense",
            status=AccountStatus.ARCHIVED,
        )
        result = AccountValidator.archive_account(acc.pk)
        assert result.status == AccountStatus.ARCHIVED

    def test_archive_blocked_by_children(self, tenant_context):
        parent = Account.objects.create(
            code="9600",
            name="Parent",
            account_type="expense",
            is_header=True,
        )
        Account.objects.create(
            code="9601",
            name="Child",
            account_type="expense",
            parent=parent,
        )
        Account.objects.rebuild()
        with pytest.raises(ValidationError):
            AccountValidator.archive_account(parent.pk)

    def test_archive_with_children(self, tenant_context):
        parent = Account.objects.create(
            code="9500",
            name="Parent",
            account_type="expense",
            is_header=True,
        )
        child = Account.objects.create(
            code="9501",
            name="Child",
            account_type="expense",
            parent=parent,
        )
        Account.objects.rebuild()
        result = AccountValidator.archive_account(
            parent.pk, archive_children=True
        )
        child.refresh_from_db()
        assert result.status == AccountStatus.ARCHIVED
        assert child.status == AccountStatus.ARCHIVED
