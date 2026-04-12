"""
Tests for SP11 Financial Reports.

Covers:
- Report enums (ReportType, ReportPeriod, DetailLevel, ComparisonType)
- Report models (ReportConfig, ReportResult)
- Report generators (TrialBalance, ProfitLoss, BalanceSheet, CashFlow, GeneralLedger)
- Base generator template method pattern
- Celery task (generate_scheduled_report)
"""

import datetime
from decimal import Decimal

import pytest

from apps.accounting.models import (
    Account,
    JournalEntry,
    JournalEntryLine,
    ReportConfig,
    ReportResult,
)
from apps.accounting.models.enums import JournalEntryStatus
from apps.accounting.reports.enums import (
    ComparisonType,
    DetailLevel,
    ReportPeriod,
    ReportType,
)
from apps.accounting.reports.generators import (
    BalanceSheetGenerator,
    CashFlowGenerator,
    GeneralLedgerGenerator,
    ProfitLossGenerator,
    TrialBalanceGenerator,
)

# ════════════════════════════════════════════════════════════════════════
# Fixtures
# ════════════════════════════════════════════════════════════════════════


@pytest.fixture
def report_accounts(tenant_context):
    """Create a full set of accounts for financial reporting tests."""
    accounts = {}

    # ── Asset accounts ──────────────────────────────────────────
    accounts["cash"] = Account.objects.create(
        code="1010", name="Cash on Hand", account_type="asset",
    )
    accounts["bank"] = Account.objects.create(
        code="1100", name="Bank Account", account_type="asset",
    )
    accounts["ar"] = Account.objects.create(
        code="1150", name="Accounts Receivable", account_type="asset",
    )
    accounts["inventory"] = Account.objects.create(
        code="1160", name="Inventory", account_type="asset",
    )
    accounts["equipment"] = Account.objects.create(
        code="1200", name="Equipment", account_type="asset",
    )
    accounts["acc_depreciation"] = Account.objects.create(
        code="1800", name="Accumulated Depreciation", account_type="asset",
    )

    # ── Liability accounts ──────────────────────────────────────
    accounts["ap"] = Account.objects.create(
        code="2100", name="Accounts Payable", account_type="liability",
    )
    accounts["long_term_loan"] = Account.objects.create(
        code="2200", name="Long-term Loan", account_type="liability",
    )

    # ── Equity accounts ─────────────────────────────────────────
    accounts["capital"] = Account.objects.create(
        code="3100", name="Owner Capital", account_type="equity",
    )
    accounts["retained_earnings"] = Account.objects.create(
        code="3200", name="Retained Earnings", account_type="equity",
    )

    # ── Revenue accounts ────────────────────────────────────────
    accounts["sales"] = Account.objects.create(
        code="4100", name="Sales Revenue", account_type="revenue",
    )
    accounts["other_income"] = Account.objects.create(
        code="4900", name="Other Income", account_type="revenue",
    )

    # ── Expense accounts ────────────────────────────────────────
    accounts["cogs"] = Account.objects.create(
        code="5100", name="Cost of Goods Sold", account_type="expense",
    )
    accounts["rent"] = Account.objects.create(
        code="5200", name="Rent Expense", account_type="expense",
    )
    accounts["salaries"] = Account.objects.create(
        code="5300", name="Salaries Expense", account_type="expense",
    )
    accounts["depreciation_exp"] = Account.objects.create(
        code="5600", name="Depreciation Expense", account_type="expense",
    )
    accounts["other_expense"] = Account.objects.create(
        code="5800", name="Other Expense", account_type="expense",
    )

    return accounts


@pytest.fixture
def posted_entries(tenant_context, report_accounts, user):
    """Create posted journal entries for January 2026."""
    entries = []
    accts = report_accounts

    def _create_posted(date, description, lines):
        entry = JournalEntry.objects.create(
            entry_date=date,
            description=description,
            created_by=user,
            entry_status=JournalEntryStatus.POSTED,
        )
        total_dr = Decimal("0")
        total_cr = Decimal("0")
        for i, (account, dr, cr) in enumerate(lines):
            JournalEntryLine.objects.create(
                journal_entry=entry,
                account=account,
                debit_amount=dr,
                credit_amount=cr,
                description=f"Line {i+1}",
                sort_order=i,
            )
            total_dr += dr
            total_cr += cr
        entry.total_debit = total_dr
        entry.total_credit = total_cr
        entry.save(update_fields=["total_debit", "total_credit"])
        return entry

    # 1. Capital investment
    entries.append(_create_posted(
        datetime.date(2026, 1, 1),
        "Capital investment",
        [
            (accts["bank"], Decimal("500000.00"), Decimal("0")),
            (accts["capital"], Decimal("0"), Decimal("500000.00")),
        ],
    ))

    # 2. Sales revenue
    entries.append(_create_posted(
        datetime.date(2026, 1, 10),
        "Sales invoice",
        [
            (accts["ar"], Decimal("100000.00"), Decimal("0")),
            (accts["sales"], Decimal("0"), Decimal("100000.00")),
        ],
    ))

    # 3. COGS
    entries.append(_create_posted(
        datetime.date(2026, 1, 10),
        "Cost of goods sold",
        [
            (accts["cogs"], Decimal("60000.00"), Decimal("0")),
            (accts["inventory"], Decimal("0"), Decimal("60000.00")),
        ],
    ))

    # 4. Rent expense
    entries.append(_create_posted(
        datetime.date(2026, 1, 15),
        "Office rent",
        [
            (accts["rent"], Decimal("15000.00"), Decimal("0")),
            (accts["bank"], Decimal("0"), Decimal("15000.00")),
        ],
    ))

    # 5. Salary expense
    entries.append(_create_posted(
        datetime.date(2026, 1, 31),
        "Monthly salaries",
        [
            (accts["salaries"], Decimal("25000.00"), Decimal("0")),
            (accts["bank"], Decimal("0"), Decimal("25000.00")),
        ],
    ))

    # 6. Depreciation
    entries.append(_create_posted(
        datetime.date(2026, 1, 31),
        "Monthly depreciation",
        [
            (accts["depreciation_exp"], Decimal("5000.00"), Decimal("0")),
            (accts["acc_depreciation"], Decimal("0"), Decimal("5000.00")),
        ],
    ))

    # 7. Purchase equipment (investing)
    entries.append(_create_posted(
        datetime.date(2026, 1, 20),
        "Equipment purchase",
        [
            (accts["equipment"], Decimal("50000.00"), Decimal("0")),
            (accts["bank"], Decimal("0"), Decimal("50000.00")),
        ],
    ))

    # 8. Customer collection
    entries.append(_create_posted(
        datetime.date(2026, 1, 25),
        "Customer payment received",
        [
            (accts["bank"], Decimal("80000.00"), Decimal("0")),
            (accts["ar"], Decimal("0"), Decimal("80000.00")),
        ],
    ))

    # 9. Other income
    entries.append(_create_posted(
        datetime.date(2026, 1, 28),
        "Interest income",
        [
            (accts["bank"], Decimal("2000.00"), Decimal("0")),
            (accts["other_income"], Decimal("0"), Decimal("2000.00")),
        ],
    ))

    return entries


@pytest.fixture
def tb_config(tenant_context, user):
    """ReportConfig for Trial Balance."""
    return ReportConfig.objects.create(
        name="January 2026 Trial Balance",
        report_type=ReportType.TRIAL_BALANCE,
        period_type=ReportPeriod.MONTHLY,
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
        as_of_date=datetime.date(2026, 1, 31),
        detail_level=DetailLevel.DETAIL,
        include_zero_balances=False,
        created_by=user,
    )


@pytest.fixture
def pl_config(tenant_context, user):
    """ReportConfig for Profit & Loss."""
    return ReportConfig.objects.create(
        name="January 2026 P&L",
        report_type=ReportType.PROFIT_LOSS,
        period_type=ReportPeriod.MONTHLY,
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
        detail_level=DetailLevel.DETAIL,
        include_zero_balances=False,
        created_by=user,
    )


@pytest.fixture
def bs_config(tenant_context, user):
    """ReportConfig for Balance Sheet."""
    return ReportConfig.objects.create(
        name="Balance Sheet Jan 31 2026",
        report_type=ReportType.BALANCE_SHEET,
        period_type=ReportPeriod.MONTHLY,
        as_of_date=datetime.date(2026, 1, 31),
        end_date=datetime.date(2026, 1, 31),
        detail_level=DetailLevel.DETAIL,
        include_zero_balances=False,
        created_by=user,
    )


@pytest.fixture
def cf_config(tenant_context, user):
    """ReportConfig for Cash Flow."""
    return ReportConfig.objects.create(
        name="January 2026 Cash Flow",
        report_type=ReportType.CASH_FLOW,
        period_type=ReportPeriod.MONTHLY,
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
        detail_level=DetailLevel.SUMMARY,
        include_zero_balances=False,
        created_by=user,
    )


@pytest.fixture
def gl_config(tenant_context, user):
    """ReportConfig for General Ledger."""
    return ReportConfig.objects.create(
        name="January 2026 General Ledger",
        report_type=ReportType.GENERAL_LEDGER,
        period_type=ReportPeriod.MONTHLY,
        start_date=datetime.date(2026, 1, 1),
        end_date=datetime.date(2026, 1, 31),
        detail_level=DetailLevel.DETAIL,
        include_zero_balances=False,
        created_by=user,
    )


# ════════════════════════════════════════════════════════════════════════
# Enum Tests
# ════════════════════════════════════════════════════════════════════════


class TestReportEnums:
    """Test report enumeration values."""

    def test_report_type_values(self):
        assert ReportType.TRIAL_BALANCE == "TRIAL_BALANCE"
        assert ReportType.PROFIT_LOSS == "PROFIT_LOSS"
        assert ReportType.BALANCE_SHEET == "BALANCE_SHEET"
        assert ReportType.CASH_FLOW == "CASH_FLOW"
        assert ReportType.GENERAL_LEDGER == "GENERAL_LEDGER"

    def test_report_type_choices(self):
        choices = dict(ReportType.choices)
        assert len(choices) == 5
        assert choices["TRIAL_BALANCE"] == "Trial Balance"

    def test_report_period_values(self):
        assert ReportPeriod.MONTHLY == "MONTHLY"
        assert ReportPeriod.QUARTERLY == "QUARTERLY"
        assert ReportPeriod.YEARLY == "YEARLY"
        assert ReportPeriod.CUSTOM == "CUSTOM"

    def test_detail_level_values(self):
        assert DetailLevel.SUMMARY == "SUMMARY"
        assert DetailLevel.DETAIL == "DETAIL"

    def test_comparison_type_values(self):
        assert ComparisonType.PRIOR_PERIOD == "PRIOR_PERIOD"
        assert ComparisonType.PRIOR_YEAR == "PRIOR_YEAR"
        assert ComparisonType.CUSTOM == "CUSTOM"


# ════════════════════════════════════════════════════════════════════════
# ReportConfig Model Tests
# ════════════════════════════════════════════════════════════════════════


class TestReportConfigModel:
    """Test ReportConfig model."""

    def test_create_report_config(self, tb_config):
        assert tb_config.pk is not None
        assert tb_config.name == "January 2026 Trial Balance"
        assert tb_config.report_type == ReportType.TRIAL_BALANCE
        assert tb_config.is_active is True

    def test_report_config_str(self, tb_config):
        s = str(tb_config)
        assert "January 2026 Trial Balance" in s
        assert "Trial Balance" in s

    def test_report_config_date_fields(self, pl_config):
        assert pl_config.start_date == datetime.date(2026, 1, 1)
        assert pl_config.end_date == datetime.date(2026, 1, 31)

    def test_report_config_defaults(self, tb_config):
        assert tb_config.include_comparison is False
        assert tb_config.comparison_period_type is None

    def test_report_config_with_comparison(self, tenant_context, user):
        config = ReportConfig.objects.create(
            name="TB with Comparison",
            report_type=ReportType.TRIAL_BALANCE,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 31),
            as_of_date=datetime.date(2026, 1, 31),
            include_comparison=True,
            comparison_period_type=ComparisonType.PRIOR_PERIOD,
            comparison_start_date=datetime.date(2025, 12, 1),
            comparison_end_date=datetime.date(2025, 12, 31),
            created_by=user,
        )
        assert config.include_comparison is True
        assert config.comparison_period_type == ComparisonType.PRIOR_PERIOD

    def test_report_config_ordering(self, tenant_context, user):
        """Configs are ordered by -created_at."""
        c1 = ReportConfig.objects.create(
            name="First", report_type=ReportType.TRIAL_BALANCE,
            as_of_date=datetime.date(2026, 1, 31), created_by=user,
        )
        c2 = ReportConfig.objects.create(
            name="Second", report_type=ReportType.PROFIT_LOSS,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 31), created_by=user,
        )
        configs = list(ReportConfig.objects.all())
        assert configs[0].pk == c2.pk  # Most recent first


# ════════════════════════════════════════════════════════════════════════
# ReportResult Model Tests
# ════════════════════════════════════════════════════════════════════════


class TestReportResultModel:
    """Test ReportResult model."""

    def test_create_report_result(self, tb_config):
        result = ReportResult.objects.create(
            config=tb_config,
            report_type=ReportType.TRIAL_BALANCE,
            report_data={"title": "Trial Balance"},
            report_metadata={"generated_at": "2026-01-31T12:00:00"},
            generation_time_ms=150,
            is_success=True,
        )
        assert result.pk is not None
        assert result.report_data["title"] == "Trial Balance"
        assert result.generation_time_ms == 150

    def test_report_result_str(self, tb_config):
        result = ReportResult.objects.create(
            config=tb_config,
            report_type=ReportType.TRIAL_BALANCE,
            is_success=True,
        )
        s = str(result)
        assert "Trial Balance" in s

    def test_report_result_error(self, tb_config):
        result = ReportResult.objects.create(
            config=tb_config,
            report_type=ReportType.TRIAL_BALANCE,
            is_success=False,
            error_message="Configuration validation failed",
        )
        assert result.is_success is False
        assert "validation failed" in result.error_message

    def test_report_result_cascade_delete(self, tb_config):
        ReportResult.objects.create(
            config=tb_config,
            report_type=ReportType.TRIAL_BALANCE,
            is_success=True,
        )
        config_pk = tb_config.pk
        tb_config.delete()
        assert ReportResult.objects.filter(
            config_id=config_pk
        ).count() == 0


# ════════════════════════════════════════════════════════════════════════
# Trial Balance Generator Tests
# ════════════════════════════════════════════════════════════════════════


class TestTrialBalanceGenerator:
    """Test TrialBalanceGenerator."""

    def test_trial_balance_report_type(self):
        assert TrialBalanceGenerator.report_type == ReportType.TRIAL_BALANCE

    def test_trial_balance_is_balanced(self, tb_config, posted_entries):
        """TB should always balance: total debits == total credits."""
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        assert result.is_success is True, f"Generation failed: {result.error_message}"
        data = result.report_data
        assert data["is_balanced"] is True

    def test_trial_balance_grand_totals(self, tb_config, posted_entries):
        """Grand totals debits should equal credits."""
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        data = result.report_data
        totals = data["grand_totals"]
        assert Decimal(str(totals["closing_debit"])) == Decimal(
            str(totals["closing_credit"])
        )

    def test_trial_balance_has_account_groups(self, tb_config, posted_entries):
        """TB should group accounts by type."""
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        groups = result.report_data["account_groups"]
        assert len(groups) > 0
        group_names = {g["display_name"] for g in groups}
        assert "Assets" in group_names
        assert "Revenue" in group_names
        assert "Expenses" in group_names

    def test_trial_balance_format_output(self, tb_config, posted_entries):
        """Formatted output has required fields."""
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        data = result.report_data
        assert data["title"] == "Trial Balance"
        assert "period" in data
        assert "display_options" in data
        assert "validation" in data

    def test_trial_balance_excludes_zero_balances(
        self, tb_config, posted_entries, report_accounts,
    ):
        """Zero-balance accounts excluded when include_zero_balances=False."""
        tb_config.include_zero_balances = False
        tb_config.save()
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        data = result.report_data
        # Flatten all account codes from groups
        all_codes = []
        for group in data["account_groups"]:
            for acct in group["accounts"]:
                all_codes.append(acct["account_code"])
        # Accounts with no transactions should not appear
        # account "other_expense" 5800 has no entries
        assert "5800" not in all_codes

    def test_trial_balance_includes_zero_balances(
        self, tb_config, posted_entries, report_accounts,
    ):
        """Zero-balance accounts included when include_zero_balances=True."""
        tb_config.include_zero_balances = True
        tb_config.save()
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        data = result.report_data
        all_codes = []
        for group in data["account_groups"]:
            for acct in group["accounts"]:
                all_codes.append(acct["account_code"])
        # "other_expense" 5800 has no entries but should appear
        assert "5800" in all_codes

    def test_trial_balance_no_data(self, tb_config):
        """TB with no journal entries returns empty but balanced result."""
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        assert result.is_success is True, f"TB no-data failed: {result.error_message}"
        data = result.report_data
        assert data["is_balanced"] is True

    def test_trial_balance_result_saved(self, tb_config, posted_entries):
        """Successful TB result is persisted to database."""
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        assert result.pk is not None
        assert ReportResult.objects.filter(pk=result.pk).exists()


# ════════════════════════════════════════════════════════════════════════
# Profit & Loss Generator Tests
# ════════════════════════════════════════════════════════════════════════


class TestProfitLossGenerator:
    """Test ProfitLossGenerator."""

    def test_profit_loss_report_type(self):
        assert ProfitLossGenerator.report_type == ReportType.PROFIT_LOSS

    def test_profit_loss_generates_successfully(
        self, pl_config, posted_entries,
    ):
        generator = ProfitLossGenerator(pl_config)
        result = generator.generate()
        assert result.is_success is True, f"P&L failed: {result.error_message}"

    def test_profit_loss_revenue(self, pl_config, posted_entries):
        """Revenue should reflect sales amount."""
        generator = ProfitLossGenerator(pl_config)
        result = generator.generate()
        data = result.report_data
        total_revenue = Decimal(str(data["revenue"]["total"]))
        assert total_revenue == Decimal("100000.00")

    def test_profit_loss_cogs(self, pl_config, posted_entries):
        """COGS should reflect cost of goods sold."""
        generator = ProfitLossGenerator(pl_config)
        result = generator.generate()
        data = result.report_data
        total_cogs = Decimal(str(data["cost_of_goods_sold"]["total"]))
        assert total_cogs == Decimal("60000.00")

    def test_profit_loss_gross_profit(self, pl_config, posted_entries):
        """Gross profit = Revenue - COGS."""
        generator = ProfitLossGenerator(pl_config)
        result = generator.generate()
        data = result.report_data
        gross_profit = Decimal(str(data["gross_profit"]["amount"]))
        expected = Decimal("100000.00") - Decimal("60000.00")
        assert gross_profit == expected

    def test_profit_loss_operating_expenses(self, pl_config, posted_entries):
        """OpEx should include rent (5200), salaries (5300), depreciation (5600)."""
        generator = ProfitLossGenerator(pl_config)
        result = generator.generate()
        data = result.report_data
        total_opex = Decimal(str(data["operating_expenses"]["total"]))
        # Rent: 15,000 + Salaries: 25,000 + Depreciation: 5,000 = 45,000
        expected = Decimal("15000.00") + Decimal("25000.00") + Decimal("5000.00")
        assert total_opex == expected

    def test_profit_loss_net_income(self, pl_config, posted_entries):
        """Net income = Revenue - COGS - OpEx - Other Exp + Other Income."""
        generator = ProfitLossGenerator(pl_config)
        result = generator.generate()
        data = result.report_data
        net_income = Decimal(str(data["net_income"]["amount"]))
        # Revenue: 100,000 - COGS: 60,000 - Rent: 15,000 - Salaries: 25,000
        # - Depreciation(5600): 5,000 + Other Income(4900): 2,000
        # Net = 100,000 - 60,000 - 15,000 - 25,000 - 5,000 + 2,000 = -3,000
        expected = Decimal("-3000.00")
        assert net_income == expected

    def test_profit_loss_title(self, pl_config, posted_entries):
        generator = ProfitLossGenerator(pl_config)
        result = generator.generate()
        assert result.report_data["title"] == "Profit & Loss Statement"

    def test_profit_loss_no_data(self, pl_config):
        """P&L with no entries shows zero net income."""
        generator = ProfitLossGenerator(pl_config)
        result = generator.generate()
        assert result.is_success is True, f"P&L no-data failed: {result.error_message}"
        data = result.report_data
        assert Decimal(str(data["net_income"]["amount"])) == Decimal("0")


# ════════════════════════════════════════════════════════════════════════
# Balance Sheet Generator Tests
# ════════════════════════════════════════════════════════════════════════


class TestBalanceSheetGenerator:
    """Test BalanceSheetGenerator."""

    def test_balance_sheet_report_type(self):
        assert BalanceSheetGenerator.report_type == ReportType.BALANCE_SHEET

    def test_balance_sheet_generates_successfully(
        self, bs_config, posted_entries,
    ):
        generator = BalanceSheetGenerator(bs_config)
        result = generator.generate()
        assert result.is_success is True, f"BS failed: {result.error_message}"

    def test_balance_sheet_equation(self, bs_config, posted_entries):
        """Assets = Liabilities + Equity (fundamental equation)."""
        generator = BalanceSheetGenerator(bs_config)
        result = generator.generate()
        assert result.is_success is True, f"BS failed: {result.error_message}"
        data = result.report_data
        total_assets = Decimal(str(data["assets"]["total_assets"]))
        total_liab_equity = Decimal(str(data["total_liabilities_equity"]))
        assert abs(total_assets - total_liab_equity) < Decimal("0.01")

    def test_balance_sheet_assets_breakdown(self, bs_config, posted_entries):
        """Balance sheet has asset sections."""
        generator = BalanceSheetGenerator(bs_config)
        result = generator.generate()
        data = result.report_data
        assert "assets" in data
        total_assets = Decimal(str(data["assets"]["total_assets"]))
        assert total_assets > Decimal("0")

    def test_balance_sheet_equity(self, bs_config, posted_entries):
        """Equity includes capital contribution."""
        generator = BalanceSheetGenerator(bs_config)
        result = generator.generate()
        data = result.report_data
        total_equity = Decimal(str(data["equity"]["total_equity"]))
        # Capital: 500,000 + Net Income(retained): -3,000 = 497,000
        assert total_equity > Decimal("0")

    def test_balance_sheet_title(self, bs_config, posted_entries):
        generator = BalanceSheetGenerator(bs_config)
        result = generator.generate()
        assert "Balance Sheet" in result.report_data["title"]

    def test_balance_sheet_no_data(self, bs_config):
        """BS with no entries still balances (zeros)."""
        generator = BalanceSheetGenerator(bs_config)
        result = generator.generate()
        assert result.is_success is True, f"BS no-data failed: {result.error_message}"


# ════════════════════════════════════════════════════════════════════════
# Cash Flow Generator Tests
# ════════════════════════════════════════════════════════════════════════


class TestCashFlowGenerator:
    """Test CashFlowGenerator."""

    def test_cash_flow_report_type(self):
        assert CashFlowGenerator.report_type == ReportType.CASH_FLOW

    def test_cash_flow_generates_successfully(
        self, cf_config, posted_entries,
    ):
        generator = CashFlowGenerator(cf_config)
        result = generator.generate()
        assert result.is_success is True, f"CF failed: {result.error_message}"

    def test_cash_flow_has_sections(self, cf_config, posted_entries):
        """Cash flow should have operating/investing/financing sections."""
        generator = CashFlowGenerator(cf_config)
        result = generator.generate()
        assert result.is_success is True, f"CF failed: {result.error_message}"
        data = result.report_data
        assert "operating_activities" in data
        assert "investing_activities" in data
        assert "financing_activities" in data

    def test_cash_flow_title(self, cf_config, posted_entries):
        generator = CashFlowGenerator(cf_config)
        result = generator.generate()
        assert "Cash Flow" in result.report_data["title"]

    def test_cash_flow_no_data(self, cf_config):
        """CF with no entries generates successfully."""
        generator = CashFlowGenerator(cf_config)
        result = generator.generate()
        assert result.is_success is True, f"CF no-data failed: {result.error_message}"


# ════════════════════════════════════════════════════════════════════════
# General Ledger Generator Tests
# ════════════════════════════════════════════════════════════════════════


class TestGeneralLedgerGenerator:
    """Test GeneralLedgerGenerator."""

    def test_general_ledger_report_type(self):
        assert GeneralLedgerGenerator.report_type == ReportType.GENERAL_LEDGER

    def test_general_ledger_generates_successfully(
        self, gl_config, posted_entries,
    ):
        generator = GeneralLedgerGenerator(gl_config)
        result = generator.generate()
        assert result.is_success is True, f"GL failed: {result.error_message}"

    def test_general_ledger_has_accounts(self, gl_config, posted_entries):
        """GL should list accounts with their transactions."""
        generator = GeneralLedgerGenerator(gl_config)
        result = generator.generate()
        assert result.is_success is True, f"GL failed: {result.error_message}"
        data = result.report_data
        assert "accounts" in data

    def test_general_ledger_single_account_filter(
        self, gl_config, posted_entries,
    ):
        """GL can be filtered to a single account."""
        generator = GeneralLedgerGenerator(
            gl_config, account_code="1100",
        )
        result = generator.generate()
        assert result.is_success is True, f"GL filter failed: {result.error_message}"
        data = result.report_data
        account_list = data["accounts"]
        codes = [a["account_code"] for a in account_list]
        assert len(codes) >= 1
        assert all(c == "1100" for c in codes)

    def test_general_ledger_code_range_filter(
        self, gl_config, posted_entries,
    ):
        """GL can be filtered to an account code range."""
        generator = GeneralLedgerGenerator(
            gl_config, code_from="5000", code_to="5999",
        )
        result = generator.generate()
        assert result.is_success is True, f"GL range failed: {result.error_message}"
        data = result.report_data
        account_list = data["accounts"]
        for acct in account_list:
            assert "5000" <= acct["account_code"] <= "5999"

    def test_general_ledger_running_balance(
        self, gl_config, posted_entries,
    ):
        """GL transactions should have running balances."""
        generator = GeneralLedgerGenerator(
            gl_config, account_code="1100",
        )
        result = generator.generate()
        assert result.is_success is True, f"GL balance failed: {result.error_message}"
        data = result.report_data
        account_list = data["accounts"]
        if account_list:
            acct = account_list[0]
            transactions = acct.get("transactions", [])
            if transactions:
                last_txn = transactions[-1]
                assert "running_balance" in last_txn

    def test_general_ledger_title(self, gl_config, posted_entries):
        generator = GeneralLedgerGenerator(gl_config)
        result = generator.generate()
        assert "General Ledger" in result.report_data["title"]

    def test_general_ledger_no_data(self, gl_config):
        """GL with no entries generates successfully."""
        generator = GeneralLedgerGenerator(gl_config)
        result = generator.generate()
        assert result.is_success is True, f"GL no-data failed: {result.error_message}"


# ════════════════════════════════════════════════════════════════════════
# Base Generator Tests
# ════════════════════════════════════════════════════════════════════════


class TestBaseReportGenerator:
    """Test BaseReportGenerator template method pattern."""

    def test_invalid_report_type_config(self, tenant_context, user):
        """Generator rejects mismatched report type."""
        config = ReportConfig.objects.create(
            name="Wrong Type",
            report_type=ReportType.PROFIT_LOSS,
            start_date=datetime.date(2026, 1, 1),
            end_date=datetime.date(2026, 1, 31),
            created_by=user,
        )
        generator = TrialBalanceGenerator(config)
        result = generator.generate()
        assert result.is_success is False
        assert "Invalid report type" in result.error_message

    def test_generation_time_tracked(self, tb_config, posted_entries):
        """Generation time in milliseconds is recorded."""
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        assert result.generation_time_ms >= 0

    def test_report_metadata_generated(self, tb_config, posted_entries):
        """Report metadata contains generation info."""
        generator = TrialBalanceGenerator(tb_config)
        result = generator.generate()
        assert result.is_success is True, f"Meta failed: {result.error_message}"
        meta = result.report_metadata
        assert "generated_at" in meta
        assert meta["report_type"] == ReportType.TRIAL_BALANCE


# ════════════════════════════════════════════════════════════════════════
# Celery Task Tests
# ════════════════════════════════════════════════════════════════════════


class TestGenerateScheduledReportTask:
    """Test generate_scheduled_report Celery task."""

    def test_task_generates_report(self, tb_config, posted_entries):
        """Task generates a report and returns result PK."""
        from apps.accounting.tasks import generate_scheduled_report

        result_pk = generate_scheduled_report(str(tb_config.pk))
        assert result_pk is not None
        report_result = ReportResult.objects.get(pk=result_pk)
        assert report_result.is_success is True
        assert report_result.report_data is not None

    def test_task_missing_config(self, tenant_context):
        """Task returns None for nonexistent config."""
        import uuid

        from apps.accounting.tasks import generate_scheduled_report
        result = generate_scheduled_report(str(uuid.uuid4()))
        assert result is None

    def test_task_creates_report_result(self, pl_config, posted_entries):
        """Task persists a ReportResult to the database."""
        from apps.accounting.tasks import generate_scheduled_report

        initial_count = ReportResult.objects.count()
        generate_scheduled_report(str(pl_config.pk))
        assert ReportResult.objects.count() == initial_count + 1
