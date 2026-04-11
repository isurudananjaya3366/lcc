"""
Group F — API integration tests for the accounting module.

Tests for AccountViewSet CRUD operations, custom endpoints
(tree, types, initialize), filtering, search, and ordering.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounting.models import Account, AccountTypeConfig, COATemplate

pytestmark = pytest.mark.django_db

TENANT_DOMAIN = "accounting.testserver"
BASE_URL = "/api/v1/accounting/accounts/"


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def api_client(user):
    """Authenticated API client with tenant host header."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def unauthenticated_client():
    """Unauthenticated API client with tenant host header."""
    return APIClient(HTTP_HOST=TENANT_DOMAIN)


@pytest.fixture
def parent_account(tenant_context):
    """Create a parent (header) account."""
    return Account.objects.create(
        code="1000",
        name="Current Assets",
        account_type="asset",
        is_header=True,
    )


@pytest.fixture
def child_account(parent_account):
    """Create a child account under parent_account."""
    return Account.objects.create(
        code="1001",
        name="Cash on Hand",
        account_type="asset",
        parent=parent_account,
    )


@pytest.fixture
def expense_account(tenant_context):
    """Create an expense account."""
    return Account.objects.create(
        code="5000",
        name="Cost of Goods Sold",
        account_type="expense",
    )


@pytest.fixture
def multiple_accounts(tenant_context):
    """Create several accounts across types for filtering tests."""
    accounts = []
    data = [
        ("1000", "Current Assets", "asset", True),
        ("1001", "Cash", "asset", False),
        ("1002", "Bank Account", "asset", False),
        ("2000", "Current Liabilities", "liability", True),
        ("2001", "Accounts Payable", "liability", False),
        ("4000", "Sales Revenue", "revenue", False),
        ("5000", "COGS", "expense", False),
    ]
    parent_map = {}
    for code, name, atype, is_header in data:
        parent = None
        if code in ("1001", "1002"):
            parent = parent_map.get("1000")
        elif code == "2001":
            parent = parent_map.get("2000")
        acc = Account.objects.create(
            code=code,
            name=name,
            account_type=atype,
            is_header=is_header,
            parent=parent,
        )
        parent_map[code] = acc
        accounts.append(acc)
    Account.objects.rebuild()
    return accounts


# ═══════════════════════════════════════════════════════════════════
# CRUD Tests
# ═══════════════════════════════════════════════════════════════════


class TestAccountList:
    """Tests for GET /api/v1/accounting/accounts/"""

    def test_list_accounts(self, api_client, parent_account):
        response = api_client.get(BASE_URL)
        assert response.status_code == status.HTTP_200_OK
        # DRF paginated or list response
        data = response.data
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data
        assert len(results) >= 1
        codes = [a["code"] for a in results]
        assert "1000" in codes

    def test_list_empty(self, api_client, tenant_context):
        response = api_client.get(BASE_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_list(self, unauthenticated_client, parent_account):
        response = unauthenticated_client.get(BASE_URL)
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )


class TestAccountCreate:
    """Tests for POST /api/v1/accounting/accounts/"""

    def test_create_account(self, api_client, tenant_context):
        data = {
            "code": "1100",
            "name": "Petty Cash",
            "account_type": "asset",
        }
        response = api_client.post(BASE_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["code"] == "1100"
        assert response.data["name"] == "Petty Cash"
        assert response.data["account_type"] == "asset"
        assert Account.objects.filter(code="1100").exists()

    def test_create_with_parent(self, api_client, parent_account):
        data = {
            "code": "1010",
            "name": "Cash Register",
            "account_type": "asset",
            "parent": str(parent_account.pk),
        }
        response = api_client.post(BASE_URL, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert str(response.data["parent"]) == str(parent_account.pk)

    def test_create_duplicate_code_rejected(self, api_client, parent_account):
        data = {
            "code": "1000",
            "name": "Duplicate",
            "account_type": "asset",
        }
        response = api_client.post(BASE_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_invalid_code_format(self, api_client, tenant_context):
        data = {
            "code": "ABC",
            "name": "Bad Code",
            "account_type": "asset",
        }
        response = api_client.post(BASE_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_code_out_of_range(self, api_client, tenant_context):
        data = {
            "code": "9999",
            "name": "Out of Range",
            "account_type": "asset",
        }
        response = api_client.post(BASE_URL, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_create(self, unauthenticated_client, tenant_context):
        data = {"code": "1100", "name": "Test", "account_type": "asset"}
        response = unauthenticated_client.post(BASE_URL, data, format="json")
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )


class TestAccountRetrieve:
    """Tests for GET /api/v1/accounting/accounts/{id}/"""

    def test_retrieve_account(self, api_client, parent_account):
        url = f"{BASE_URL}{parent_account.pk}/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["code"] == "1000"
        assert response.data["name"] == "Current Assets"
        assert "children_count" in response.data

    def test_retrieve_nonexistent(self, api_client, tenant_context):
        import uuid

        url = f"{BASE_URL}{uuid.uuid4()}/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAccountUpdate:
    """Tests for PUT/PATCH /api/v1/accounting/accounts/{id}/"""

    def test_partial_update(self, api_client, parent_account):
        url = f"{BASE_URL}{parent_account.pk}/"
        response = api_client.patch(
            url,
            {"name": "Updated Current Assets"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Current Assets"

    def test_update_system_account_code_blocked(self, api_client, tenant_context):
        system_acc = Account.objects.create(
            code="1599",
            name="System Account",
            account_type="asset",
            is_system=True,
        )
        url = f"{BASE_URL}{system_acc.pk}/"
        response = api_client.patch(
            url,
            {"code": "1600"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_system_account_name_allowed(self, api_client, tenant_context):
        system_acc = Account.objects.create(
            code="1599",
            name="System Account",
            account_type="asset",
            is_system=True,
        )
        url = f"{BASE_URL}{system_acc.pk}/"
        response = api_client.patch(
            url,
            {"name": "Renamed System Account"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Renamed System Account"


class TestAccountDelete:
    """Tests for DELETE /api/v1/accounting/accounts/{id}/"""

    def test_delete_archives_account(self, api_client, parent_account):
        url = f"{BASE_URL}{parent_account.pk}/"
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        parent_account.refresh_from_db()
        assert parent_account.status == "ARCHIVED"


# ═══════════════════════════════════════════════════════════════════
# Filtering / Search / Ordering Tests
# ═══════════════════════════════════════════════════════════════════


class TestAccountFiltering:
    """Tests for query param filtering."""

    def _results(self, response):
        data = response.data
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    def test_filter_by_account_type(self, api_client, multiple_accounts):
        response = api_client.get(BASE_URL, {"account_type": "asset"})
        assert response.status_code == status.HTTP_200_OK
        results = self._results(response)
        assert all(a["account_type"] == "asset" for a in results)
        assert len(results) == 3  # 1000, 1001, 1002

    def test_filter_by_is_header(self, api_client, multiple_accounts):
        response = api_client.get(BASE_URL, {"is_header": True})
        assert response.status_code == status.HTTP_200_OK
        results = self._results(response)
        assert all(a["is_header"] is True for a in results)

    def test_filter_by_parent_isnull(self, api_client, multiple_accounts):
        response = api_client.get(BASE_URL, {"parent__isnull": True})
        assert response.status_code == status.HTTP_200_OK
        results = self._results(response)
        assert all(a["parent"] is None for a in results)

    def test_search_by_name(self, api_client, multiple_accounts):
        response = api_client.get(BASE_URL, {"search": "Cash"})
        assert response.status_code == status.HTTP_200_OK
        results = self._results(response)
        assert len(results) >= 1
        assert any("Cash" in a["name"] for a in results)

    def test_search_by_code(self, api_client, multiple_accounts):
        response = api_client.get(BASE_URL, {"search": "4000"})
        assert response.status_code == status.HTTP_200_OK
        results = self._results(response)
        assert any(a["code"] == "4000" for a in results)

    def test_ordering_by_code(self, api_client, multiple_accounts):
        response = api_client.get(BASE_URL, {"ordering": "code"})
        assert response.status_code == status.HTTP_200_OK
        results = self._results(response)
        codes = [a["code"] for a in results]
        assert codes == sorted(codes)

    def test_ordering_by_name_desc(self, api_client, multiple_accounts):
        response = api_client.get(BASE_URL, {"ordering": "-name"})
        assert response.status_code == status.HTTP_200_OK
        results = self._results(response)
        names = [a["name"] for a in results]
        assert names == sorted(names, reverse=True)


# ═══════════════════════════════════════════════════════════════════
# Custom Endpoint Tests
# ═══════════════════════════════════════════════════════════════════


class TestAccountTreeEndpoint:
    """Tests for GET /api/v1/accounting/accounts/tree/"""

    TREE_URL = f"{BASE_URL}tree/"

    def test_tree_returns_root_nodes(self, api_client, parent_account, child_account):
        Account.objects.rebuild()
        response = api_client.get(self.TREE_URL)
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        # Should contain only root nodes at top level
        root_codes = [n["code"] for n in data]
        assert "1000" in root_codes
        assert "1001" not in root_codes  # child is nested

    def test_tree_includes_children(self, api_client, parent_account, child_account):
        Account.objects.rebuild()
        response = api_client.get(self.TREE_URL)
        assert response.status_code == status.HTTP_200_OK
        root = next(n for n in response.data if n["code"] == "1000")
        assert len(root["children"]) == 1
        assert root["children"][0]["code"] == "1001"

    def test_tree_empty(self, api_client, tenant_context):
        response = api_client.get(self.TREE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_tree_unauthenticated(self, unauthenticated_client, parent_account):
        response = unauthenticated_client.get(self.TREE_URL)
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )


class TestAccountTypesEndpoint:
    """Tests for GET /api/v1/accounting/accounts/types/"""

    TYPES_URL = f"{BASE_URL}types/"

    def test_types_returns_configs(self, api_client, all_account_type_configs):
        response = api_client.get(self.TYPES_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5
        type_names = [c["type_name"] for c in response.data]
        assert "ASSET" in type_names
        assert "LIABILITY" in type_names

    def test_types_ordered_by_display_order(self, api_client, all_account_type_configs):
        response = api_client.get(self.TYPES_URL)
        assert response.status_code == status.HTTP_200_OK
        orders = [c["display_order"] for c in response.data]
        assert orders == sorted(orders)

    def test_types_includes_code_range(self, api_client, all_account_type_configs):
        response = api_client.get(self.TYPES_URL)
        assert response.status_code == status.HTTP_200_OK
        asset_config = next(c for c in response.data if c["type_name"] == "ASSET")
        assert "code_range_display" in asset_config
        assert asset_config["code_range_display"] == "1000-1999"

    def test_types_empty(self, api_client, tenant_context):
        response = api_client.get(self.TYPES_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_types_unauthenticated(self, unauthenticated_client, all_account_type_configs):
        response = unauthenticated_client.get(self.TYPES_URL)
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )


class TestInitializeEndpoint:
    """Tests for POST /api/v1/accounting/accounts/initialize/"""

    INIT_URL = f"{BASE_URL}initialize/"

    def test_initialize_default(self, api_client, tenant_context):
        response = api_client.post(self.INIT_URL, {}, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "total" in response.data
        assert response.data["total"] > 0
        assert "accounts_by_type" in response.data
        assert Account.objects.count() > 0

    def test_initialize_already_exists_conflict(self, api_client, parent_account):
        response = api_client.post(self.INIT_URL, {}, format="json")
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "detail" in response.data

    def test_initialize_force(self, api_client, parent_account):
        response = api_client.post(
            self.INIT_URL,
            {"force": True},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["total"] > 0

    def test_initialize_from_template(self, api_client, tenant_context):
        template = COATemplate.objects.create(
            template_name="Test Template",
            industry="RETAIL",
            template_accounts=[
                {"code": "1000", "name": "Assets", "account_type": "asset", "is_header": True},
                {"code": "1001", "name": "Cash", "account_type": "asset"},
                {"code": "2000", "name": "Liabilities", "account_type": "liability", "is_header": True},
            ],
            is_active=True,
        )
        response = api_client.post(
            self.INIT_URL,
            {"template_id": str(template.pk)},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["total"] == 3
        assert "template_name" in response.data

    def test_initialize_invalid_template(self, api_client, tenant_context):
        import uuid

        response = api_client.post(
            self.INIT_URL,
            {"template_id": str(uuid.uuid4())},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_initialize_unauthenticated(self, unauthenticated_client, tenant_context):
        response = unauthenticated_client.post(self.INIT_URL, {}, format="json")
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )
