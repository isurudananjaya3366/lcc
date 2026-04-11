"""Tests for accounting models — Group A & B."""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.accounting.models import (
    Account,
    AccountCategory,
    AccountStatus,
    AccountType,
    AccountTypeConfig,
    NormalBalance,
)

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────────────────────
# Group A: Enum Tests
# ──────────────────────────────────────────────────────────────


class TestAccountTypeEnum:
    def test_has_five_choices(self):
        assert len(AccountType.choices) == 5

    def test_values(self):
        assert AccountType.ASSET == "ASSET"
        assert AccountType.LIABILITY == "LIABILITY"
        assert AccountType.EQUITY == "EQUITY"
        assert AccountType.REVENUE == "REVENUE"
        assert AccountType.EXPENSE == "EXPENSE"

    def test_labels(self):
        assert AccountType.ASSET.label == "Asset"
        assert AccountType.LIABILITY.label == "Liability"
        assert AccountType.EQUITY.label == "Equity"
        assert AccountType.REVENUE.label == "Revenue"
        assert AccountType.EXPENSE.label == "Expense"


class TestAccountCategoryEnum:
    def test_has_seven_choices(self):
        assert len(AccountCategory.choices) == 7

    def test_values(self):
        assert AccountCategory.CURRENT == "CURRENT"
        assert AccountCategory.NON_CURRENT == "NON_CURRENT"
        assert AccountCategory.OPERATING == "OPERATING"
        assert AccountCategory.NON_OPERATING == "NON_OPERATING"
        assert AccountCategory.OWNER_CAPITAL == "OWNER_CAPITAL"
        assert AccountCategory.RETAINED_EARNINGS == "RETAINED_EARNINGS"
        assert AccountCategory.OTHER == "OTHER"


class TestAccountStatusEnum:
    def test_has_three_choices(self):
        assert len(AccountStatus.choices) == 3

    def test_values(self):
        assert AccountStatus.ACTIVE == "ACTIVE"
        assert AccountStatus.INACTIVE == "INACTIVE"
        assert AccountStatus.ARCHIVED == "ARCHIVED"


class TestNormalBalanceEnum:
    def test_has_two_choices(self):
        assert len(NormalBalance.choices) == 2

    def test_values(self):
        assert NormalBalance.DEBIT == "DEBIT"
        assert NormalBalance.CREDIT == "CREDIT"


# ──────────────────────────────────────────────────────────────
# Group A: AccountTypeConfig Model Tests
# ──────────────────────────────────────────────────────────────


class TestAccountTypeConfigModel:
    def test_create_config(self, account_type_config):
        assert account_type_config.pk is not None
        assert account_type_config.type_name == "ASSET"
        assert account_type_config.normal_balance == "DEBIT"
        assert account_type_config.code_start == 1000
        assert account_type_config.code_end == 1999
        assert account_type_config.display_order == 1

    def test_str(self, account_type_config):
        assert str(account_type_config) == "Asset"

    def test_unique_type_name(self, account_type_config, tenant_context):
        with pytest.raises(IntegrityError):
            AccountTypeConfig.objects.create(
                type_name="ASSET",
                normal_balance="DEBIT",
                code_start=1000,
                code_end=1999,
                display_order=10,
            )

    def test_unique_display_order(self, account_type_config, tenant_context):
        with pytest.raises(IntegrityError):
            AccountTypeConfig.objects.create(
                type_name="LIABILITY",
                normal_balance="CREDIT",
                code_start=2000,
                code_end=2999,
                display_order=1,
            )

    def test_all_five_configs(self, all_account_type_configs):
        assert len(all_account_type_configs) == 5
        assert AccountTypeConfig.objects.count() == 5

    def test_ordering_by_display_order(self, all_account_type_configs):
        configs = list(AccountTypeConfig.objects.values_list("type_name", flat=True))
        assert configs == ["ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE"]

    def test_code_ranges_no_overlap(self, all_account_type_configs):
        configs = AccountTypeConfig.objects.order_by("code_start")
        prev_end = 0
        for cfg in configs:
            assert cfg.code_start > prev_end
            assert cfg.code_end >= cfg.code_start
            prev_end = cfg.code_end

    def test_normal_balance_assignment(self, all_account_type_configs):
        debit_types = AccountTypeConfig.objects.filter(
            normal_balance="DEBIT"
        ).values_list("type_name", flat=True)
        credit_types = AccountTypeConfig.objects.filter(
            normal_balance="CREDIT"
        ).values_list("type_name", flat=True)
        assert set(debit_types) == {"ASSET", "EXPENSE"}
        assert set(credit_types) == {"LIABILITY", "EQUITY", "REVENUE"}

    def test_description_optional(self, tenant_context):
        cfg = AccountTypeConfig.objects.create(
            type_name="ASSET",
            normal_balance="DEBIT",
            code_start=1000,
            code_end=1999,
            display_order=1,
        )
        assert cfg.description == ""

    def test_meta_table_name(self):
        assert AccountTypeConfig._meta.db_table == "accounting_account_type_config"


# ──────────────────────────────────────────────────────────────
# Group B: Account Model (MPTT) Tests
# ──────────────────────────────────────────────────────────────


class TestAccountModel:
    def test_create_account(self, account):
        assert account.pk is not None
        assert account.code == "1000"
        assert account.name == "Cash on Hand"

    def test_str(self, account):
        assert str(account) == "1000 — Cash on Hand"

    def test_default_values(self, account):
        assert account.status == "ACTIVE"
        assert account.category == "OTHER"
        assert account.currency == "LKR"
        assert account.is_header is False
        assert account.is_system is False
        assert account.opening_balance == Decimal("0.00")
        assert account.current_balance == Decimal("0.00")

    def test_is_debit_normal(self, tenant_context):
        asset = Account.objects.create(code="1001", name="Cash", account_type="asset")
        expense = Account.objects.create(code="5001", name="Rent", account_type="expense")
        assert asset.is_debit_normal is True
        assert expense.is_debit_normal is True

    def test_is_credit_normal(self, tenant_context):
        liability = Account.objects.create(code="2001", name="AP", account_type="liability")
        equity = Account.objects.create(code="3001", name="Capital", account_type="equity")
        revenue = Account.objects.create(code="4001", name="Sales", account_type="revenue")
        assert liability.is_credit_normal is True
        assert equity.is_credit_normal is True
        assert revenue.is_credit_normal is True

    def test_parent_child_hierarchy(self, tenant_context):
        parent = Account.objects.create(
            code="1000", name="Current Assets", account_type="asset", is_header=True,
        )
        child = Account.objects.create(
            code="1100", name="Cash", account_type="asset", parent=parent,
        )
        assert child.parent == parent
        assert child in parent.children.all()
        assert child.level == 1
        assert parent.level == 0

    def test_mptt_tree_fields(self, tenant_context):
        root = Account.objects.create(
            code="1000", name="Assets", account_type="asset",
        )
        assert root.tree_id is not None
        assert root.lft is not None
        assert root.rght is not None
        assert root.level == 0

    def test_full_path(self, tenant_context):
        root = Account.objects.create(
            code="1000", name="Assets", account_type="asset", is_header=True,
        )
        child = Account.objects.create(
            code="1100", name="Current Assets", account_type="asset",
            parent=root, is_header=True,
        )
        leaf = Account.objects.create(
            code="1110", name="Cash on Hand", account_type="asset", parent=child,
        )
        assert leaf.full_path == "Assets > Current Assets > Cash on Hand"

    def test_account_type_config_fk(self, tenant_context, account_type_config):
        acct = Account.objects.create(
            code="1001", name="Bank", account_type="asset",
            account_type_config=account_type_config,
        )
        assert acct.account_type_config == account_type_config
        assert acct in account_type_config.accounts.all()

    def test_unique_code(self, account, tenant_context):
        with pytest.raises(IntegrityError):
            Account.objects.create(code="1000", name="Duplicate", account_type="asset")

    def test_balance_fields(self, tenant_context):
        acct = Account.objects.create(
            code="1000", name="Cash", account_type="asset",
            opening_balance=Decimal("10000.00"),
            current_balance=Decimal("15000.00"),
        )
        assert acct.opening_balance == Decimal("10000.00")
        assert acct.current_balance == Decimal("15000.00")

    def test_meta_table_name(self):
        assert Account._meta.db_table == "accounting_account"
