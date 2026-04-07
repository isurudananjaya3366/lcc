"""
SP05 API Tests for Bundle & Composite Products.

Production-level tests using real PostgreSQL database through Docker.
Tests all ViewSet CRUD operations, custom actions, filtering, and search.

Covers SP05 Tasks 84 (Bundle API tests) and 88 (BOM API tests).
"""

from decimal import Decimal

import pytest
from django.urls import reverse

from apps.products.constants import BUNDLE_TYPE, DISCOUNT_TYPE
from apps.products.models import (
    BillOfMaterials,
    BOMItem,
    BundleItem,
    Product,
    ProductBundle,
)


# ═══════════════════════════════════════════════════════════════════════
# Bundle API Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def bundle_product(tenant_context, category):
    """Create a product to act as the bundle parent."""
    return Product.objects.create(
        name="Holiday Gift Set",
        category=category,
        selling_price=Decimal("5000.00"),
        cost_price=Decimal("3000.00"),
    )


@pytest.fixture
def component_product_1(tenant_context, category):
    """First bundle component product."""
    return Product.objects.create(
        name="Ceylon Tea Box",
        category=category,
        selling_price=Decimal("1200.00"),
        cost_price=Decimal("800.00"),
    )


@pytest.fixture
def component_product_2(tenant_context, category):
    """Second bundle component product."""
    return Product.objects.create(
        name="Chocolate Cookies",
        category=category,
        selling_price=Decimal("900.00"),
        cost_price=Decimal("500.00"),
    )


@pytest.fixture
def component_product_3(tenant_context, category):
    """Third bundle component product."""
    return Product.objects.create(
        name="Spice Collection",
        category=category,
        selling_price=Decimal("1500.00"),
        cost_price=Decimal("900.00"),
    )


@pytest.fixture
def bundle_with_items(bundle_product, component_product_1, component_product_2):
    """Create a complete bundle with items."""
    bundle = ProductBundle.objects.create(
        product=bundle_product,
        bundle_type=BUNDLE_TYPE.DYNAMIC,
        discount_type=DISCOUNT_TYPE.PERCENTAGE,
        discount_value=Decimal("10.00"),
    )
    BundleItem.objects.create(
        bundle=bundle,
        product=component_product_1,
        quantity=1,
        sort_order=1,
    )
    BundleItem.objects.create(
        bundle=bundle,
        product=component_product_2,
        quantity=2,
        sort_order=2,
    )
    return bundle


# ═══════════════════════════════════════════════════════════════════════
# BOM API Fixtures
# ═══════════════════════════════════════════════════════════════════════


@pytest.fixture
def composite_product(tenant_context, category):
    """Product used as the composite/manufactured item."""
    return Product.objects.create(
        name="Custom Birthday Cake",
        category=category,
        selling_price=Decimal("2500.00"),
    )


@pytest.fixture
def raw_material_flour(tenant_context, category):
    """Raw material: Flour."""
    return Product.objects.create(
        name="Flour",
        category=category,
        cost_price=Decimal("300.00"),
    )


@pytest.fixture
def raw_material_sugar(tenant_context, category):
    """Raw material: Sugar."""
    return Product.objects.create(
        name="Sugar",
        category=category,
        cost_price=Decimal("400.00"),
    )


@pytest.fixture
def raw_material_butter(tenant_context, category):
    """Raw material: Butter."""
    return Product.objects.create(
        name="Butter",
        category=category,
        cost_price=Decimal("800.00"),
    )


@pytest.fixture
def bom_with_items(
    composite_product,
    raw_material_flour,
    raw_material_sugar,
    raw_material_butter,
    unit_of_measure_kg,
):
    """Create a complete BOM with items."""
    bom = BillOfMaterials.objects.create(
        product=composite_product,
        version="1.0",
        is_active=True,
        yield_quantity=1,
        notes="Birthday cake recipe",
    )
    BOMItem.objects.create(
        bom=bom,
        raw_material=raw_material_flour,
        quantity=Decimal("0.500"),
        unit=unit_of_measure_kg,
        wastage_percent=Decimal("5.00"),
        sort_order=1,
    )
    BOMItem.objects.create(
        bom=bom,
        raw_material=raw_material_sugar,
        quantity=Decimal("0.200"),
        unit=unit_of_measure_kg,
        wastage_percent=Decimal("2.00"),
        sort_order=2,
    )
    BOMItem.objects.create(
        bom=bom,
        raw_material=raw_material_butter,
        quantity=Decimal("0.100"),
        unit=unit_of_measure_kg,
        wastage_percent=Decimal("3.00"),
        is_critical=True,
        sort_order=3,
    )
    return bom


# ═══════════════════════════════════════════════════════════════════════
# Bundle API Tests (Task 84)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBundleListAPI:
    """Test Bundle list endpoint."""

    def test_list_bundles_empty(self, authenticated_client):
        url = reverse("products:bundle-list")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert response.data["results"] == [] or response.data == []

    def test_list_bundles_with_data(self, authenticated_client, bundle_with_items):
        url = reverse("products:bundle-list")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        assert len(data) == 1
        assert data[0]["bundle_type"] == BUNDLE_TYPE.DYNAMIC

    def test_list_bundles_filter_by_type(
        self,
        authenticated_client,
        bundle_with_items,
        component_product_3,
        category,
    ):
        """Test filtering bundles by bundle_type."""
        # Create a fixed bundle
        fixed_product = Product.objects.create(
            name="Fixed Bundle", category=category
        )
        ProductBundle.objects.create(
            product=fixed_product,
            bundle_type=BUNDLE_TYPE.FIXED,
            fixed_price=Decimal("3000.00"),
        )
        url = reverse("products:bundle-list")
        response = authenticated_client.get(url, {"bundle_type": BUNDLE_TYPE.FIXED})
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        assert len(data) == 1
        assert data[0]["bundle_type"] == BUNDLE_TYPE.FIXED

    def test_list_bundles_search_by_product_name(
        self, authenticated_client, bundle_with_items
    ):
        url = reverse("products:bundle-list")
        response = authenticated_client.get(url, {"search": "Holiday"})
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        assert len(data) == 1

    def test_list_bundles_ordering(self, authenticated_client, bundle_with_items):
        url = reverse("products:bundle-list")
        response = authenticated_client.get(url, {"ordering": "-created_on"})
        assert response.status_code == 200


@pytest.mark.django_db
class TestBundleCreateAPI:
    """Test Bundle create endpoint."""

    def test_create_bundle(self, authenticated_client, bundle_product):
        url = reverse("products:bundle-list")
        data = {
            "product": str(bundle_product.id),
            "bundle_type": BUNDLE_TYPE.FIXED,
            "fixed_price": "4500.00",
            "discount_type": DISCOUNT_TYPE.NONE,
            "discount_value": "0.00",
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == 201
        assert ProductBundle.objects.count() == 1
        bundle = ProductBundle.objects.first()
        assert bundle.bundle_type == BUNDLE_TYPE.FIXED
        assert bundle.fixed_price == Decimal("4500.00")

    def test_create_dynamic_bundle(self, authenticated_client, bundle_product):
        url = reverse("products:bundle-list")
        data = {
            "product": str(bundle_product.id),
            "bundle_type": BUNDLE_TYPE.DYNAMIC,
            "discount_type": DISCOUNT_TYPE.PERCENTAGE,
            "discount_value": "15.00",
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == 201
        bundle = ProductBundle.objects.first()
        assert bundle.discount_type == DISCOUNT_TYPE.PERCENTAGE
        assert bundle.discount_value == Decimal("15.00")


@pytest.mark.django_db
class TestBundleRetrieveAPI:
    """Test Bundle retrieve endpoint with detail serializer."""

    def test_retrieve_bundle(self, authenticated_client, bundle_with_items):
        url = reverse("products:bundle-detail", kwargs={"pk": bundle_with_items.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "items" in response.data
        assert len(response.data["items"]) == 2
        assert "component_count" in response.data
        assert response.data["component_count"] == 2

    def test_retrieve_includes_calculated_fields(
        self, authenticated_client, bundle_with_items
    ):
        url = reverse("products:bundle-detail", kwargs={"pk": bundle_with_items.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "calculated_price" in response.data
        assert "available_stock" in response.data
        assert "savings" in response.data


@pytest.mark.django_db
class TestBundleUpdateAPI:
    """Test Bundle update endpoint."""

    def test_update_bundle_type(self, authenticated_client, bundle_with_items):
        url = reverse("products:bundle-detail", kwargs={"pk": bundle_with_items.pk})
        data = {
            "product": str(bundle_with_items.product_id),
            "bundle_type": BUNDLE_TYPE.FIXED,
            "fixed_price": "3500.00",
            "discount_type": DISCOUNT_TYPE.NONE,
            "discount_value": "0.00",
        }
        response = authenticated_client.put(url, data, format="json")
        assert response.status_code == 200
        bundle_with_items.refresh_from_db()
        assert bundle_with_items.bundle_type == BUNDLE_TYPE.FIXED

    def test_partial_update_discount(self, authenticated_client, bundle_with_items):
        url = reverse("products:bundle-detail", kwargs={"pk": bundle_with_items.pk})
        data = {"discount_value": "20.00"}
        response = authenticated_client.patch(url, data, format="json")
        assert response.status_code == 200
        bundle_with_items.refresh_from_db()
        assert bundle_with_items.discount_value == Decimal("20.00")


@pytest.mark.django_db
class TestBundleDeleteAPI:
    """Test Bundle delete endpoint."""

    def test_delete_bundle(self, authenticated_client, bundle_with_items):
        url = reverse("products:bundle-detail", kwargs={"pk": bundle_with_items.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == 204
        # Soft-delete: BundleManager filters is_deleted=False, so it shouldn't appear
        assert ProductBundle.objects.filter(pk=bundle_with_items.pk).count() == 0 or (
            # If hard-delete is not configured, verify soft-delete
            ProductBundle.all_with_deleted.filter(
                pk=bundle_with_items.pk, is_deleted=True
            ).exists()
        )


@pytest.mark.django_db
class TestBundleCustomActions:
    """Test custom bundle actions: availability, pricing."""

    def test_availability_action(self, authenticated_client, bundle_with_items):
        url = reverse("products:bundle-availability", kwargs={"pk": bundle_with_items.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "available_stock" in response.data
        assert "is_available" in response.data

    def test_pricing_action(self, authenticated_client, bundle_with_items):
        url = reverse("products:bundle-pricing", kwargs={"pk": bundle_with_items.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "bundle_price" in response.data
        assert "individual_total" in response.data
        assert "savings" in response.data
        # Dynamic bundle with 10% off: (1200 + 900*2) * 0.9 = 2700
        assert Decimal(response.data["bundle_price"]) == Decimal("2700.00")
        assert Decimal(response.data["savings"]) == Decimal("300.00")


# ═══════════════════════════════════════════════════════════════════════
# Bundle Item API Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBundleItemAPI:
    """Test BundleItem CRUD operations."""

    def test_list_bundle_items(self, authenticated_client, bundle_with_items):
        url = reverse("products:bundle-item-list")
        response = authenticated_client.get(
            url, {"bundle": str(bundle_with_items.pk)}
        )
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        assert len(data) == 2

    def test_create_bundle_item(
        self, authenticated_client, bundle_with_items, component_product_3
    ):
        url = reverse("products:bundle-item-list")
        data = {
            "bundle": str(bundle_with_items.pk),
            "product": str(component_product_3.pk),
            "quantity": 1,
            "is_optional": True,
            "sort_order": 3,
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == 201
        assert BundleItem.objects.filter(bundle=bundle_with_items).count() == 3

    def test_delete_bundle_item(self, authenticated_client, bundle_with_items):
        item = bundle_with_items.items.first()
        url = reverse("products:bundle-item-detail", kwargs={"pk": item.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == 204

    def test_filter_bundle_items_by_optional(
        self, authenticated_client, bundle_with_items
    ):
        url = reverse("products:bundle-item-list")
        response = authenticated_client.get(
            url,
            {"bundle": str(bundle_with_items.pk), "is_optional": "false"},
        )
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════
# BOM API Tests (Task 88)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBOMListAPI:
    """Test BOM list endpoint."""

    def test_list_bom_empty(self, authenticated_client):
        url = reverse("products:bom-list")
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_list_bom_with_data(self, authenticated_client, bom_with_items):
        url = reverse("products:bom-list")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        assert len(data) >= 1

    def test_list_bom_filter_by_active(self, authenticated_client, bom_with_items):
        url = reverse("products:bom-list")
        response = authenticated_client.get(url, {"is_active": "true"})
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        assert len(data) >= 1

    def test_list_bom_filter_by_product(
        self, authenticated_client, bom_with_items, composite_product
    ):
        url = reverse("products:bom-list")
        response = authenticated_client.get(
            url, {"product": str(composite_product.pk)}
        )
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        assert len(data) == 1

    def test_list_bom_search_by_product_name(
        self, authenticated_client, bom_with_items
    ):
        url = reverse("products:bom-list")
        response = authenticated_client.get(url, {"search": "Birthday"})
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        assert len(data) == 1


@pytest.mark.django_db
class TestBOMCreateAPI:
    """Test BOM create endpoint."""

    def test_create_bom(self, authenticated_client, composite_product):
        url = reverse("products:bom-list")
        data = {
            "product": str(composite_product.pk),
            "version": "1.0",
            "is_active": True,
            "yield_quantity": 1,
            "notes": "Test BOM",
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == 201
        assert BillOfMaterials.objects.count() == 1
        bom = BillOfMaterials.objects.first()
        assert bom.version == "1.0"
        assert bom.yield_quantity == 1

    def test_create_bom_batch_yield(self, authenticated_client, composite_product):
        url = reverse("products:bom-list")
        data = {
            "product": str(composite_product.pk),
            "version": "2.0",
            "is_active": False,
            "yield_quantity": 12,
            "notes": "Cookie batch - yields 12",
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == 201
        bom = BillOfMaterials.objects.get(version="2.0")
        assert bom.yield_quantity == 12


@pytest.mark.django_db
class TestBOMRetrieveAPI:
    """Test BOM retrieve endpoint with detail serializer."""

    def test_retrieve_bom(self, authenticated_client, bom_with_items):
        url = reverse("products:bom-detail", kwargs={"pk": bom_with_items.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "items" in response.data
        assert len(response.data["items"]) == 3
        assert "component_count" in response.data
        assert response.data["component_count"] == 3

    def test_retrieve_bom_includes_cost_fields(
        self, authenticated_client, bom_with_items
    ):
        url = reverse("products:bom-detail", kwargs={"pk": bom_with_items.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "total_cost" in response.data
        assert "unit_cost" in response.data

    def test_retrieve_bom_item_has_effective_quantity(
        self, authenticated_client, bom_with_items
    ):
        """BOM items should include effective_quantity, unit_price, item_cost."""
        url = reverse("products:bom-detail", kwargs={"pk": bom_with_items.pk})
        response = authenticated_client.get(url)
        first_item = response.data["items"][0]
        assert "effective_quantity" in first_item
        assert "unit_price" in first_item
        assert "item_cost" in first_item


@pytest.mark.django_db
class TestBOMUpdateAPI:
    """Test BOM update endpoint."""

    def test_update_bom_notes(self, authenticated_client, bom_with_items):
        url = reverse("products:bom-detail", kwargs={"pk": bom_with_items.pk})
        data = {"notes": "Updated recipe notes"}
        response = authenticated_client.patch(url, data, format="json")
        assert response.status_code == 200
        bom_with_items.refresh_from_db()
        assert bom_with_items.notes == "Updated recipe notes"

    def test_deactivate_bom(self, authenticated_client, bom_with_items):
        url = reverse("products:bom-detail", kwargs={"pk": bom_with_items.pk})
        data = {"is_active": False}
        response = authenticated_client.patch(url, data, format="json")
        assert response.status_code == 200
        bom_with_items.refresh_from_db()
        assert bom_with_items.is_active is False


@pytest.mark.django_db
class TestBOMDeleteAPI:
    """Test BOM delete endpoint."""

    def test_delete_bom(self, authenticated_client, bom_with_items):
        url = reverse("products:bom-detail", kwargs={"pk": bom_with_items.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == 204


@pytest.mark.django_db
class TestBOMCustomActions:
    """Test custom BOM actions: cost_breakdown, stock_check."""

    def test_cost_breakdown_action(self, authenticated_client, bom_with_items):
        url = reverse("products:bom-cost-breakdown", kwargs={"pk": bom_with_items.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "material_cost" in response.data
        assert "material_cost_with_wastage" in response.data
        assert "labor_cost" in response.data
        assert "overhead_cost" in response.data
        assert "total_cost" in response.data
        assert "unit_cost" in response.data
        assert "suggested_price" in response.data
        # Verify material cost is non-zero (we have 3 items with cost prices)
        assert Decimal(response.data["material_cost"]) > 0

    def test_stock_check_action(self, authenticated_client, bom_with_items):
        url = reverse("products:bom-stock-check", kwargs={"pk": bom_with_items.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "producible_quantity" in response.data
        assert "materials" in response.data
        assert len(response.data["materials"]) == 3


# ═══════════════════════════════════════════════════════════════════════
# BOM Item API Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBOMItemAPI:
    """Test BOMItem CRUD operations."""

    def test_list_bom_items(self, authenticated_client, bom_with_items):
        url = reverse("products:bom-item-list")
        response = authenticated_client.get(
            url, {"bom": str(bom_with_items.pk)}
        )
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        assert len(data) == 3

    def test_create_bom_item(
        self,
        authenticated_client,
        bom_with_items,
        tenant_context,
        category,
    ):
        new_material = Product.objects.create(
            name="Eggs", category=category, cost_price=Decimal("30.00")
        )
        url = reverse("products:bom-item-list")
        data = {
            "bom": str(bom_with_items.pk),
            "raw_material": str(new_material.pk),
            "quantity": "4.000",
            "wastage_percent": "0.00",
            "is_critical": False,
            "sort_order": 4,
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == 201
        assert BOMItem.objects.filter(bom=bom_with_items).count() == 4

    def test_update_bom_item_wastage(self, authenticated_client, bom_with_items):
        item = bom_with_items.items.first()
        url = reverse("products:bom-item-detail", kwargs={"pk": item.pk})
        data = {"wastage_percent": "10.00"}
        response = authenticated_client.patch(url, data, format="json")
        assert response.status_code == 200
        item.refresh_from_db()
        assert item.wastage_percent == Decimal("10.00")

    def test_delete_bom_item(self, authenticated_client, bom_with_items):
        item = bom_with_items.items.first()
        url = reverse("products:bom-item-detail", kwargs={"pk": item.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == 204

    def test_filter_bom_items_by_critical(
        self, authenticated_client, bom_with_items
    ):
        url = reverse("products:bom-item-list")
        response = authenticated_client.get(
            url,
            {"bom": str(bom_with_items.pk), "is_critical": "true"},
        )
        assert response.status_code == 200
        data = response.data.get("results", response.data)
        # Butter is the only critical item
        assert len(data) == 1


# ═══════════════════════════════════════════════════════════════════════
# Authentication / Permission Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestAPIAuthentication:
    """Verify endpoints require authentication."""

    def test_bundle_list_requires_auth(self, tenant_context):
        from rest_framework.test import APIClient
        from tests.products.conftest import TENANT_DOMAIN

        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("products:bundle-list")
        response = client.get(url)
        assert response.status_code in (401, 403)

    def test_bom_list_requires_auth(self, tenant_context):
        from rest_framework.test import APIClient
        from tests.products.conftest import TENANT_DOMAIN

        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        url = reverse("products:bom-list")
        response = client.get(url)
        assert response.status_code in (401, 403)
