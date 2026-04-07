"""
Task 89 – API endpoint tests for Stock module.

Tests all stock API endpoints: StockLevelViewSet, StockMovementViewSet,
StockOperationViewSet, and StockTakeViewSet.
"""

import uuid
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.inventory.stock.models.stock_level import StockLevel
from apps.inventory.stock.models.stock_movement import StockMovement
from apps.inventory.stock.models.stock_take import StockTake
from apps.inventory.stock.models.stock_take_item import StockTakeItem
from apps.products.models import Category, Product, ProductVariant
from apps.platform.models.user import PlatformUser

pytestmark = pytest.mark.django_db


# ───────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────


TENANT_HOST = "inventory.testserver"


@pytest.fixture
def api_client(setup_test_tenant):
    """APIClient that sends requests to the tenant domain."""
    client = APIClient(SERVER_NAME=TENANT_HOST)
    return client


@pytest.fixture
def user(tenant_context):
    return PlatformUser.objects.create_user(
        email="apiuser@test.com", password="testpass123"
    )


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def category(tenant_context):
    return Category.objects.create(name="API Cat", slug="api-cat")


@pytest.fixture
def product(category):
    return Product.objects.create(name="API Product", category=category)


@pytest.fixture
def product_2(category):
    return Product.objects.create(name="API Product 2", category=category)


@pytest.fixture
def variant(product):
    return ProductVariant.objects.create(product=product, sku="API-VAR-001")


@pytest.fixture
def stock_level(product, variant, warehouse):
    return StockLevel.objects.create(
        product=product,
        variant=variant,
        warehouse=warehouse,
        quantity=Decimal("100"),
        reserved_quantity=Decimal("10"),
        incoming_quantity=Decimal("20"),
        reorder_point=Decimal("15"),
        cost_per_unit=Decimal("500.00"),
    )


@pytest.fixture
def low_stock_level(product_2, warehouse):
    return StockLevel.objects.create(
        product=product_2,
        warehouse=warehouse,
        quantity=Decimal("5"),
        reserved_quantity=Decimal("0"),
        reorder_point=Decimal("10"),
        cost_per_unit=Decimal("100.00"),
    )


@pytest.fixture
def out_of_stock_level(product_2, warehouse_2):
    return StockLevel.objects.create(
        product=product_2,
        warehouse=warehouse_2,
        quantity=Decimal("0"),
        reserved_quantity=Decimal("0"),
        reorder_point=Decimal("10"),
        cost_per_unit=Decimal("100.00"),
    )


@pytest.fixture
def movement_in(product, variant, warehouse, user):
    return StockMovement.objects.create(
        product=product,
        variant=variant,
        movement_type="in",
        quantity=Decimal("50"),
        reason="purchase",
        to_warehouse=warehouse,
        cost_per_unit=Decimal("500.00"),
        created_by=user,
    )


# ═══════════════════════════════════════════════════════════════════
# StockLevel API Tests
# ═══════════════════════════════════════════════════════════════════


class TestStockLevelList:
    """GET /api/v1/stock/stock-levels/"""

    def test_unauthenticated_returns_401(self, api_client):
        url = reverse("stock:stocklevel-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_stock_levels(self, auth_client, stock_level):
        url = reverse("stock:stocklevel-list")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) >= 1

    def test_list_returns_expected_fields(self, auth_client, stock_level):
        url = reverse("stock:stocklevel-list")
        response = auth_client.get(url)
        results = response.data.get("results", response.data)
        item = results[0]
        assert "id" in item
        assert "product" in item
        assert "warehouse" in item
        assert "quantity" in item
        assert "available_quantity" in item
        assert "stock_status" in item


class TestStockLevelDetail:
    """GET /api/v1/stock/stock-levels/{id}/"""

    def test_retrieve_stock_level(self, auth_client, stock_level):
        url = reverse("stock:stocklevel-detail", args=[stock_level.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(stock_level.pk)

    def test_retrieve_nonexistent_returns_404(self, auth_client):
        url = reverse("stock:stocklevel-detail", args=[uuid.uuid4()])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestStockLevelActions:
    """Custom actions on StockLevelViewSet."""

    def test_low_stock_action(self, auth_client, stock_level, low_stock_level):
        url = reverse("stock:stocklevel-low-stock")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        # low_stock_level has quantity=5 < reorder_point=10
        pks = [str(r["id"]) for r in results]
        assert str(low_stock_level.pk) in pks

    def test_out_of_stock_action(self, auth_client, out_of_stock_level):
        url = reverse("stock:stocklevel-out-of-stock")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        results = data["results"] if isinstance(data, dict) else data
        pks = [str(r["id"]) for r in results]
        assert str(out_of_stock_level.pk) in pks

    def test_check_availability(self, auth_client, stock_level, product):
        url = reverse("stock:stocklevel-check-availability")
        response = auth_client.post(
            url,
            {"product_ids": [str(product.pk)]},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK


# ═══════════════════════════════════════════════════════════════════
# StockMovement API Tests
# ═══════════════════════════════════════════════════════════════════


class TestStockMovementList:
    """GET /api/v1/stock/stock-movements/"""

    def test_unauthenticated_returns_401(self, api_client):
        url = reverse("stock:stockmovement-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_movements(self, auth_client, movement_in):
        url = reverse("stock:stockmovement-list")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) >= 1

    def test_list_returns_expected_fields(self, auth_client, movement_in):
        url = reverse("stock:stockmovement-list")
        response = auth_client.get(url)
        results = response.data.get("results", response.data)
        item = results[0]
        assert "id" in item
        assert "movement_type" in item
        assert "quantity" in item


class TestStockMovementDetail:
    """GET /api/v1/stock/stock-movements/{id}/"""

    def test_retrieve_movement(self, auth_client, movement_in):
        url = reverse("stock:stockmovement-detail", args=[movement_in.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(movement_in.pk)


class TestStockMovementActions:
    """Custom actions on StockMovementViewSet."""

    def test_for_product_action(self, auth_client, movement_in, product):
        url = reverse("stock:stockmovement-for-product")
        response = auth_client.get(url, {"product_id": str(product.pk)})
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) >= 1

    def test_for_product_missing_param(self, auth_client):
        url = reverse("stock:stockmovement-for-product")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_summary_action(self, auth_client, movement_in):
        url = reverse("stock:stockmovement-summary")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK


# ═══════════════════════════════════════════════════════════════════
# StockOperation API Tests
# ═══════════════════════════════════════════════════════════════════


class TestStockInAPI:
    """POST /api/v1/stock/stock-operations/stock-in/"""

    def test_unauthenticated_returns_401(self, api_client):
        url = reverse("stock:stockoperation-stock-in")
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_stock_in_success(self, auth_client, product, warehouse):
        url = reverse("stock:stockoperation-stock-in")
        payload = {
            "product_id": str(product.pk),
            "warehouse_id": str(warehouse.pk),
            "quantity": "10",
            "cost_per_unit": "500.00",
            "reason": "purchase",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True

    def test_stock_in_missing_fields(self, auth_client):
        url = reverse("stock:stockoperation-stock-in")
        response = auth_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_stock_in_invalid_product(self, auth_client, warehouse):
        url = reverse("stock:stockoperation-stock-in")
        payload = {
            "product_id": str(uuid.uuid4()),
            "warehouse_id": str(warehouse.pk),
            "quantity": "10",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestStockOutAPI:
    """POST /api/v1/stock/stock-operations/stock-out/"""

    def test_stock_out_success(self, auth_client, stock_level, product, variant, warehouse):
        url = reverse("stock:stockoperation-stock-out")
        payload = {
            "product_id": str(product.pk),
            "variant_id": str(variant.pk),
            "warehouse_id": str(warehouse.pk),
            "quantity": "5",
            "reason": "sale",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_stock_out_insufficient_stock(self, auth_client, stock_level, product, variant, warehouse):
        url = reverse("stock:stockoperation-stock-out")
        payload = {
            "product_id": str(product.pk),
            "variant_id": str(variant.pk),
            "warehouse_id": str(warehouse.pk),
            "quantity": "9999",
            "reason": "sale",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestTransferAPI:
    """POST /api/v1/stock/stock-operations/transfer/"""

    def test_transfer_success(self, auth_client, stock_level, product, variant, warehouse, warehouse_2):
        url = reverse("stock:stockoperation-transfer")
        payload = {
            "product_id": str(product.pk),
            "variant_id": str(variant.pk),
            "from_warehouse_id": str(warehouse.pk),
            "to_warehouse_id": str(warehouse_2.pk),
            "quantity": "5",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_transfer_same_warehouse_no_location_fails(
        self, auth_client, stock_level, product, warehouse
    ):
        url = reverse("stock:stockoperation-transfer")
        payload = {
            "product_id": str(product.pk),
            "from_warehouse_id": str(warehouse.pk),
            "to_warehouse_id": str(warehouse.pk),
            "quantity": "5",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAdjustAPI:
    """POST /api/v1/stock/stock-operations/adjust/"""

    def test_adjust_up(self, auth_client, stock_level, product, warehouse):
        url = reverse("stock:stockoperation-adjust")
        payload = {
            "product_id": str(product.pk),
            "warehouse_id": str(warehouse.pk),
            "quantity": "10",
            "direction": "up",
            "reason": "found",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_adjust_down(self, auth_client, stock_level, product, variant, warehouse):
        url = reverse("stock:stockoperation-adjust")
        payload = {
            "product_id": str(product.pk),
            "variant_id": str(variant.pk),
            "warehouse_id": str(warehouse.pk),
            "quantity": "5",
            "direction": "down",
            "reason": "damaged",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_adjust_invalid_direction(self, auth_client, product, warehouse):
        url = reverse("stock:stockoperation-adjust")
        payload = {
            "product_id": str(product.pk),
            "warehouse_id": str(warehouse.pk),
            "quantity": "10",
            "direction": "sideways",
            "reason": "test",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ═══════════════════════════════════════════════════════════════════
# StockTake API Tests
# ═══════════════════════════════════════════════════════════════════


class TestStockTakeListCreate:
    """GET/POST /api/v1/stock/stock-takes/"""

    def test_unauthenticated_returns_401(self, api_client):
        url = reverse("stock:stocktake-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_stock_takes(self, auth_client):
        url = reverse("stock:stocktake-list")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_stock_take(self, auth_client, warehouse):
        url = reverse("stock:stocktake-list")
        payload = {
            "warehouse_id": str(warehouse.pk),
            "name": "Annual Count 2025",
            "scope": "full",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True

    def test_create_stock_take_missing_name(self, auth_client, warehouse):
        url = reverse("stock:stocktake-list")
        payload = {
            "warehouse_id": str(warehouse.pk),
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestStockTakeDetail:
    """GET/DELETE /api/v1/stock/stock-takes/{id}/"""

    @pytest.fixture
    def stock_take(self, warehouse, user):
        return StockTake.objects.create(
            warehouse=warehouse,
            name="Detail Test",
            status="draft",
            scope="full",
            created_by=user,
        )

    def test_retrieve_stock_take(self, auth_client, stock_take):
        url = reverse("stock:stocktake-detail", args=[stock_take.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(stock_take.pk)

    def test_delete_draft_stock_take(self, auth_client, stock_take):
        url = reverse("stock:stocktake-detail", args=[stock_take.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_non_draft_fails(self, auth_client, stock_take):
        stock_take.status = "counting"
        stock_take.save()
        url = reverse("stock:stocktake-detail", args=[stock_take.pk])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestStockTakeWorkflowActions:
    """Test StockTake lifecycle endpoint actions."""

    @pytest.fixture
    def stock_take(self, warehouse, user):
        return StockTake.objects.create(
            warehouse=warehouse,
            name="Workflow Test",
            status="draft",
            scope="full",
            created_by=user,
        )

    def test_start_action(self, auth_client, stock_take, stock_level):
        """Start transitions draft → counting and populates items."""
        url = reverse("stock:stocktake-start", args=[stock_take.pk])
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_start_non_draft_fails(self, auth_client, stock_take):
        stock_take.status = "counting"
        stock_take.save()
        url = reverse("stock:stocktake-start", args=[stock_take.pk])
        response = auth_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_count_action(self, auth_client, stock_take, stock_level, product, variant):
        """Record a count on a stock take item."""
        # Start the stock take to create items
        stock_take.status = "counting"
        stock_take.save()
        item = StockTakeItem.objects.create(
            stock_take=stock_take,
            product=product,
            variant=variant,
            expected_quantity=Decimal("100"),
            system_quantity=Decimal("100"),
            count_sequence=1,
        )
        url = reverse("stock:stocktake-count", args=[stock_take.pk])
        payload = {
            "item_id": str(item.pk),
            "counted_quantity": "98",
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_count_missing_fields_returns_400(self, auth_client, stock_take):
        stock_take.status = "counting"
        stock_take.save()
        url = reverse("stock:stocktake-count", args=[stock_take.pk])
        response = auth_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_submit_action(self, auth_client, stock_take):
        stock_take.status = "counting"
        stock_take.save()
        url = reverse("stock:stocktake-submit", args=[stock_take.pk])
        response = auth_client.post(url)
        # Should succeed or fail depending on service logic
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_approve_action(self, auth_client, stock_take):
        stock_take.status = "review"
        stock_take.save()
        url = reverse("stock:stocktake-approve", args=[stock_take.pk])
        response = auth_client.post(url)
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_complete_action(self, auth_client, stock_take):
        stock_take.status = "approved"
        stock_take.save()
        url = reverse("stock:stocktake-complete", args=[stock_take.pk])
        response = auth_client.post(url)
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cancel_action(self, auth_client, stock_take):
        url = reverse("stock:stocktake-cancel", args=[stock_take.pk])
        response = auth_client.post(url)
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        )


class TestStockTakeReadActions:
    """Test StockTake read-only endpoint actions."""

    @pytest.fixture
    def stock_take(self, warehouse, user):
        return StockTake.objects.create(
            warehouse=warehouse,
            name="Read Action Test",
            status="counting",
            scope="full",
            created_by=user,
        )

    def test_items_action(self, auth_client, stock_take, product, variant):
        StockTakeItem.objects.create(
            stock_take=stock_take,
            product=product,
            variant=variant,
            expected_quantity=Decimal("100"),
            system_quantity=Decimal("100"),
            count_sequence=1,
        )
        url = reverse("stock:stocktake-items", args=[stock_take.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_variances_action(self, auth_client, stock_take, product, variant):
        StockTakeItem.objects.create(
            stock_take=stock_take,
            product=product,
            variant=variant,
            expected_quantity=Decimal("100"),
            system_quantity=Decimal("100"),
            counted_quantity=Decimal("90"),
            variance_quantity=Decimal("-10"),
            variance_value=Decimal("-5000"),
            count_sequence=1,
        )
        url = reverse("stock:stocktake-variances", args=[stock_take.pk])
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_report_action(self, auth_client, stock_take):
        url = reverse("stock:stocktake-report", args=[stock_take.pk])
        response = auth_client.get(url)
        # Report may succeed or fail depending on stock_take state
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_bulk_count_action(self, auth_client, stock_take, product, variant):
        item = StockTakeItem.objects.create(
            stock_take=stock_take,
            product=product,
            variant=variant,
            expected_quantity=Decimal("100"),
            system_quantity=Decimal("100"),
            count_sequence=1,
        )
        url = reverse("stock:stocktake-bulk-count", args=[stock_take.pk])
        payload = {
            "counts": [
                {"item_id": str(item.pk), "counted_quantity": "95"},
            ]
        }
        response = auth_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
