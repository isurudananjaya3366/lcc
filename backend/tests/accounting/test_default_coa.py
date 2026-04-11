"""Tests for Group C — Default Chart of Accounts setup."""

import pytest

from apps.accounting.data.default_accounts import DEFAULT_ACCOUNTS
from apps.accounting.models import Account

# ═══════════════════════════════════════════════════════════════════
# Helper constants
# ═══════════════════════════════════════════════════════════════════
TOTAL_ACCOUNTS = len(DEFAULT_ACCOUNTS)


# ═══════════════════════════════════════════════════════════════════
# Tests for default_accounts data definition
# ═══════════════════════════════════════════════════════════════════
class TestDefaultAccountsData:
    """Validate the data definitions without touching the database."""

    def test_total_accounts_count(self):
        assert TOTAL_ACCOUNTS >= 50

    def test_all_codes_unique(self):
        codes = [a["code"] for a in DEFAULT_ACCOUNTS]
        assert len(codes) == len(set(codes))

    def test_all_codes_numeric(self):
        for acc in DEFAULT_ACCOUNTS:
            assert acc["code"].isdigit(), f"Non-numeric code: {acc['code']}"

    def test_five_root_accounts(self):
        roots = [a for a in DEFAULT_ACCOUNTS if a["parent_code"] is None]
        assert len(roots) == 5

    def test_root_account_types(self):
        roots = {a["account_type"] for a in DEFAULT_ACCOUNTS if a["parent_code"] is None}
        assert roots == {"asset", "liability", "equity", "revenue", "expense"}

    def test_code_ranges_per_type(self):
        type_ranges = {
            "asset": ("1", "1"),
            "liability": ("2", "2"),
            "equity": ("3", "3"),
            "revenue": ("4", "4"),
            "expense": ("5", "5"),
        }
        for acc in DEFAULT_ACCOUNTS:
            first = acc["code"][0]
            expected_start, expected_end = type_ranges[acc["account_type"]]
            assert expected_start <= first <= expected_end, (
                f"{acc['code']} ({acc['account_type']}) outside expected range"
            )

    def test_parent_codes_exist_or_null(self):
        codes = {a["code"] for a in DEFAULT_ACCOUNTS}
        for acc in DEFAULT_ACCOUNTS:
            if acc["parent_code"] is not None:
                assert acc["parent_code"] in codes, (
                    f"Parent code {acc['parent_code']} for {acc['code']} not found"
                )

    def test_header_accounts_have_children(self):
        parent_codes = {a["parent_code"] for a in DEFAULT_ACCOUNTS if a["parent_code"]}
        for acc in DEFAULT_ACCOUNTS:
            if acc["is_header"] and acc["code"] not in ("2500",):
                assert acc["code"] in parent_codes, (
                    f"Header account {acc['code']} has no children"
                )

    def test_system_accounts_not_headers(self):
        for acc in DEFAULT_ACCOUNTS:
            if acc["is_system"]:
                assert not acc["is_header"], (
                    f"System account {acc['code']} should not be a header"
                )

    def test_all_have_description(self):
        for acc in DEFAULT_ACCOUNTS:
            assert acc.get("description"), f"Missing description for {acc['code']}"


# ═══════════════════════════════════════════════════════════════════
# Tests for Sri Lanka statutory accounts
# ═══════════════════════════════════════════════════════════════════
class TestSriLankaStatutoryAccounts:
    """Verify Sri Lanka-specific statutory accounts are defined."""

    def _get_account(self, code):
        for a in DEFAULT_ACCOUNTS:
            if a["code"] == code:
                return a
        return None

    def test_vat_input_exists(self):
        acc = self._get_account("1250")
        assert acc is not None
        assert acc["is_system"] is True

    def test_vat_output_exists(self):
        acc = self._get_account("2150")
        assert acc is not None
        assert acc["is_system"] is True

    def test_epf_payable_exists(self):
        acc = self._get_account("2310")
        assert acc is not None
        assert acc["is_system"] is True

    def test_etf_payable_exists(self):
        acc = self._get_account("2320")
        assert acc is not None
        assert acc["is_system"] is True

    def test_paye_payable_exists(self):
        acc = self._get_account("2210")
        assert acc is not None
        assert acc["is_system"] is True

    def test_epf_expense_exists(self):
        acc = self._get_account("5220")
        assert acc is not None
        assert "EPF" in acc["name"]

    def test_etf_expense_exists(self):
        acc = self._get_account("5230")
        assert acc is not None
        assert "ETF" in acc["name"]


# ═══════════════════════════════════════════════════════════════════
# Tests for management command — database required
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestLoadDefaultCoaCommand:
    """Test the load_default_coa management command within a tenant."""

    def test_load_creates_all_accounts(self, tenant_context):
        from django.core.management import call_command

        call_command("load_default_coa", stdout=open("/dev/null", "w"))
        assert Account.objects.count() == TOTAL_ACCOUNTS

    def test_load_creates_hierarchy(self, tenant_context):
        from django.core.management import call_command

        call_command("load_default_coa", stdout=open("/dev/null", "w"))
        cash = Account.objects.get(code="1100")
        assert cash.parent.code == "1000"
        assert cash.get_children().count() == 2

    def test_load_idempotent(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        call_command("load_default_coa", stderr=io.StringIO(), stdout=io.StringIO())
        # Without --force, second run should not duplicate
        assert Account.objects.count() == TOTAL_ACCOUNTS

    def test_load_force_replaces(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        # Modify an account
        Account.objects.filter(code="1000").update(name="Modified")
        call_command("load_default_coa", "--force", stdout=io.StringIO())
        assert Account.objects.get(code="1000").name == "Assets"

    def test_asset_accounts_created(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        assets = Account.objects.filter(account_type="asset")
        assert assets.count() == 21  # 1 root + 20 sub-accounts

    def test_liability_accounts_created(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        liabilities = Account.objects.filter(account_type="liability")
        assert liabilities.count() == 13

    def test_equity_accounts_created(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        equity = Account.objects.filter(account_type="equity")
        assert equity.count() == 4

    def test_revenue_accounts_created(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        revenue = Account.objects.filter(account_type="revenue")
        assert revenue.count() == 10

    def test_expense_accounts_created(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        expenses = Account.objects.filter(account_type="expense")
        assert expenses.count() == 21

    def test_system_accounts_flagged(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        system_accounts = Account.objects.filter(is_system=True)
        system_codes = set(system_accounts.values_list("code", flat=True))
        expected = {
            "1201", "1250", "1301", "1599",  # asset
            "2101", "2150", "2210", "2310", "2320",  # liability
            "3200",  # equity
            "5100",  # expense
        }
        assert expected == system_codes

    def test_mptt_tree_integrity(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        root_assets = Account.objects.get(code="1000")
        # MPTT should correctly set tree fields
        assert root_assets.lft == 1
        assert root_assets.level == 0
        descendants = root_assets.get_descendant_count()
        assert descendants == 20  # all asset sub-accounts

    def test_contra_asset_accumulated_depreciation(self, tenant_context):
        import io

        from django.core.management import call_command

        call_command("load_default_coa", stdout=io.StringIO())
        acc_depr = Account.objects.get(code="1599")
        assert acc_depr.is_system is True
        assert acc_depr.parent.code == "1500"
        assert "contra" in acc_depr.description.lower()
