"""
Product integration tests — production-level database tests.

Tests model CRUD operations, API endpoints, tenant isolation, and business
logic using a real PostgreSQL database with tenant schema isolation.

Run with:
    DJANGO_SETTINGS_MODULE=config.settings.test_pg pytest tests/products/test_product_integration.py

All tests in this module require @pytest.mark.django_db.
"""

import uuid
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection
from django_tenants.utils import get_tenant_model, get_tenant_domain_model

TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()

TENANT_DOMAIN = "products.testserver"

pytestmark = pytest.mark.django_db


# ═══════════════════════════════════════════════════════════════════════
# 1. Brand — CRUD Operations
# ═══════════════════════════════════════════════════════════════════════


class TestBrandCRUD:
    """Test Brand model CRUD with real database."""

    def test_create_brand(self, tenant_context):
        from apps.products.models import Brand

        brand = Brand.objects.create(
            name="TestBrand",
            description="A test brand",
            website="https://example.com",
        )
        assert brand.pk is not None
        assert isinstance(brand.pk, uuid.UUID)
        assert brand.name == "TestBrand"
        assert brand.description == "A test brand"
        assert brand.website == "https://example.com"
        assert brand.is_active is True
        assert brand.is_deleted is False

    def test_auto_slug_generation(self, tenant_context):
        from apps.products.models import Brand

        brand = Brand.objects.create(name="My New Brand")
        assert brand.slug == "my-new-brand"

    def test_slug_not_overwritten_on_update(self, brand):
        original_slug = brand.slug
        brand.name = "Updated Brand Name"
        brand.save()
        brand.refresh_from_db()
        assert brand.slug == original_slug

    def test_read_brand(self, brand):
        from apps.products.models import Brand

        fetched = Brand.objects.get(pk=brand.pk)
        assert fetched.name == brand.name
        assert fetched.slug == brand.slug

    def test_update_brand(self, brand):
        brand.description = "Updated description"
        brand.save()
        brand.refresh_from_db()
        assert brand.description == "Updated description"

    def test_str_representation(self, brand):
        assert str(brand) == "Samsung"

    def test_unique_slug_enforcement(self, brand, tenant_context):
        from apps.products.models import Brand

        with pytest.raises(IntegrityError):
            Brand.objects.create(name="Other", slug=brand.slug)

    def test_uuid_primary_key(self, brand):
        assert isinstance(brand.pk, uuid.UUID)

    def test_timestamps_auto_populated(self, brand):
        assert brand.created_on is not None
        assert brand.updated_on is not None

    def test_soft_delete(self, brand):
        brand.soft_delete()
        brand.refresh_from_db()
        assert brand.is_deleted is True
        assert brand.deleted_on is not None

    def test_restore_after_soft_delete(self, brand):
        brand.soft_delete()
        brand.restore()
        brand.refresh_from_db()
        assert brand.is_deleted is False
        assert brand.deleted_on is None


# ═══════════════════════════════════════════════════════════════════════
# 2. TaxClass — CRUD Operations
# ═══════════════════════════════════════════════════════════════════════


class TestTaxClassCRUD:
    """Test TaxClass model CRUD with real database."""

    def test_create_tax_class(self, tenant_context):
        from apps.products.models import TaxClass

        tc = TaxClass.objects.create(
            name="Test Tax",
            rate=Decimal("12.50"),
            description="A test tax class",
        )
        assert tc.pk is not None
        assert isinstance(tc.pk, uuid.UUID)
        assert tc.name == "Test Tax"
        assert tc.rate == Decimal("12.50")
        assert tc.is_default is False
        assert tc.is_active is True

    def test_str_representation(self, tax_class):
        assert str(tax_class) == "Standard VAT (15.00%)"

    def test_update_tax_class(self, tax_class):
        tax_class.rate = Decimal("18.00")
        tax_class.save()
        tax_class.refresh_from_db()
        assert tax_class.rate == Decimal("18.00")

    def test_rate_decimal_precision(self, tenant_context):
        from apps.products.models import TaxClass

        tc = TaxClass.objects.create(name="Precise", rate=Decimal("8.75"))
        tc.refresh_from_db()
        assert tc.rate == Decimal("8.75")

    def test_single_default_logic(self, tenant_context):
        from apps.products.models import TaxClass

        tc1 = TaxClass.objects.create(
            name="Default One", rate=Decimal("15.00"), is_default=True
        )
        tc2 = TaxClass.objects.create(
            name="Default Two", rate=Decimal("10.00"), is_default=True
        )
        tc1.refresh_from_db()
        tc2.refresh_from_db()
        assert tc1.is_default is False
        assert tc2.is_default is True

    def test_uuid_primary_key(self, tax_class):
        assert isinstance(tax_class.pk, uuid.UUID)

    def test_timestamps_auto_populated(self, tax_class):
        assert tax_class.created_on is not None
        assert tax_class.updated_on is not None


# ═══════════════════════════════════════════════════════════════════════
# 3. UnitOfMeasure — CRUD Operations
# ═══════════════════════════════════════════════════════════════════════


class TestUnitOfMeasureCRUD:
    """Test UnitOfMeasure model CRUD with real database."""

    def test_create_uom(self, tenant_context):
        from apps.products.models import UnitOfMeasure

        uom = UnitOfMeasure.objects.create(
            name="Meter",
            symbol="m",
            is_base_unit=True,
        )
        assert uom.pk is not None
        assert isinstance(uom.pk, uuid.UUID)
        assert uom.name == "Meter"
        assert uom.symbol == "m"
        assert uom.is_base_unit is True
        assert uom.is_active is True

    def test_str_representation(self, unit_of_measure):
        assert str(unit_of_measure) == "Piece (pcs)"

    def test_update_uom(self, unit_of_measure):
        unit_of_measure.description = "Count of pieces"
        unit_of_measure.save()
        unit_of_measure.refresh_from_db()
        assert unit_of_measure.description == "Count of pieces"

    def test_base_unit_flag(self, unit_of_measure):
        assert unit_of_measure.is_base_unit is True

    def test_conversion_factor(self, tenant_context):
        from apps.products.models import UnitOfMeasure

        uom = UnitOfMeasure.objects.create(
            name="Gram",
            symbol="g",
            is_base_unit=False,
            conversion_factor=Decimal("0.0010"),
        )
        uom.refresh_from_db()
        assert uom.conversion_factor == Decimal("0.0010")

    def test_uuid_primary_key(self, unit_of_measure):
        assert isinstance(unit_of_measure.pk, uuid.UUID)

    def test_timestamps_auto_populated(self, unit_of_measure):
        assert unit_of_measure.created_on is not None
        assert unit_of_measure.updated_on is not None


# ═══════════════════════════════════════════════════════════════════════
# 4. Product — CRUD Operations
# ═══════════════════════════════════════════════════════════════════════


class TestProductCRUD:
    """Test Product model CRUD with real database."""

    def test_create_product_minimal(self, category, tenant_context):
        from apps.products.models import Product

        p = Product.objects.create(name="Basic Product", category=category)
        assert p.pk is not None
        assert isinstance(p.pk, uuid.UUID)
        assert p.name == "Basic Product"
        assert p.category == category

    def test_create_product_all_fields(
        self, category, brand, tax_class, unit_of_measure, tenant_context
    ):
        from apps.products.constants import PRODUCT_STATUS, PRODUCT_TYPES
        from apps.products.models import Product

        p = Product.objects.create(
            name="Full Product",
            category=category,
            brand=brand,
            product_type=PRODUCT_TYPES.SIMPLE,
            status=PRODUCT_STATUS.ACTIVE,
            tax_class=tax_class,
            unit_of_measure=unit_of_measure,
            cost_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            mrp=Decimal("200.00"),
            wholesale_price=Decimal("120.00"),
            weight=Decimal("1.500"),
            length=Decimal("10.00"),
            width=Decimal("5.00"),
            height=Decimal("3.00"),
            seo_title="Full Product SEO",
            seo_description="Full product description",
            is_webstore_visible=True,
            is_pos_visible=True,
            featured=True,
        )
        p.refresh_from_db()
        assert p.brand == brand
        assert p.tax_class == tax_class
        assert p.unit_of_measure == unit_of_measure
        assert p.cost_price == Decimal("100.00")
        assert p.selling_price == Decimal("150.00")
        assert p.mrp == Decimal("200.00")
        assert p.featured is True

    def test_str_representation_with_sku(self, product):
        # product is created via fixture; save() auto-generates SKU
        assert product.sku != ""
        assert str(product) == f"{product.name} ({product.sku})"

    def test_auto_slug_generation(self, category, tenant_context):
        from apps.products.models import Product

        p = Product.objects.create(name="My New Product", category=category)
        assert p.slug == "my-new-product"

    def test_auto_sku_generation(self, product):
        assert product.sku.startswith("PRD-")
        assert len(product.sku) > 4

    def test_sku_format(self, category, tenant_context):
        from apps.products.models import Product

        p = Product.objects.create(name="SKU Test", category=category)
        # SKU format: PRD-{uuid[:5].upper()}
        assert p.sku.startswith("PRD-")
        assert len(p.sku.split("-")) >= 2

    def test_status_default_draft(self, product):
        from apps.products.constants import PRODUCT_STATUS

        assert product.status == PRODUCT_STATUS.DRAFT

    def test_visibility_defaults(self, product):
        assert product.is_webstore_visible is True
        assert product.is_pos_visible is True

    def test_featured_default_false(self, product):
        assert product.featured is False

    def test_foreign_key_category(self, product, category):
        assert product.category == category
        assert product.category_id == category.pk

    def test_foreign_key_brand(self, category, brand, tenant_context):
        from apps.products.models import Product

        p = Product.objects.create(
            name="Branded Product", category=category, brand=brand
        )
        assert p.brand == brand

    def test_product_type_choices(self, category, tenant_context):
        from apps.products.constants import PRODUCT_TYPES
        from apps.products.models import Product

        for ptype in [
            PRODUCT_TYPES.SIMPLE,
            PRODUCT_TYPES.VARIABLE,
            PRODUCT_TYPES.BUNDLE,
            PRODUCT_TYPES.COMPOSITE,
        ]:
            p = Product.objects.create(
                name=f"Product {ptype}",
                category=category,
                product_type=ptype,
            )
            assert p.product_type == ptype

    def test_update_product(self, product):
        product.name = "Updated Product"
        product.save()
        product.refresh_from_db()
        assert product.name == "Updated Product"

    def test_soft_delete(self, product):
        product.soft_delete()
        product.refresh_from_db()
        assert product.is_deleted is True
        assert product.deleted_on is not None

    def test_uuid_primary_key(self, product):
        assert isinstance(product.pk, uuid.UUID)

    def test_timestamps_auto_populated(self, product):
        assert product.created_on is not None
        assert product.updated_on is not None

    def test_profit_margin_property(self, category, tenant_context):
        from apps.products.models import Product

        p = Product.objects.create(
            name="Margin Product",
            category=category,
            cost_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
        )
        assert p.profit_margin == Decimal("50.0")


# ═══════════════════════════════════════════════════════════════════════
# 5. Product QuerySet Integration
# ═══════════════════════════════════════════════════════════════════════


class TestProductQuerySetIntegration:
    """Test ProductQuerySet methods with real database."""

    def test_active_queryset(self, product_active, product, tenant_context):
        from apps.products.models import Product

        active_qs = Product.objects.active()
        assert product_active in active_qs
        # product is DRAFT so should not be in active()
        assert product not in active_qs

    def test_published_queryset(self, product_active, tenant_context):
        from apps.products.models import Product

        published = Product.objects.published()
        assert product_active in published

    def test_by_category(self, product, category, tenant_context):
        from apps.products.models import Product

        by_cat = Product.objects.all().by_category(category)
        assert product in by_cat

    def test_by_brand(self, product_active, brand, tenant_context):
        from apps.products.models import Product

        by_brand = Product.objects.all().by_brand(brand)
        assert product_active in by_brand

    def test_simple_products(self, product, tenant_context):
        from apps.products.models import Product

        simple = Product.objects.all().simple_products()
        assert product in simple

    def test_variable_products(self, category, tenant_context):
        from apps.products.constants import PRODUCT_TYPES
        from apps.products.models import Product

        vp = Product.objects.create(
            name="Variable PD",
            category=category,
            product_type=PRODUCT_TYPES.VARIABLE,
        )
        variable = Product.objects.all().variable_products()
        assert vp in variable

    def test_featured_queryset(self, category, tenant_context):
        from apps.products.models import Product

        fp = Product.objects.create(
            name="Featured PD", category=category, featured=True
        )
        featured_qs = Product.objects.all().featured()
        assert fp in featured_qs

    def test_for_pos(self, product_active, tenant_context):
        from apps.products.models import Product

        pos_qs = Product.objects.for_pos()
        assert product_active in pos_qs

    def test_for_webstore(self, product_active, tenant_context):
        from apps.products.models import Product

        web_qs = Product.objects.for_webstore()
        assert product_active in web_qs

    def test_by_status(self, product, tenant_context):
        from apps.products.constants import PRODUCT_STATUS
        from apps.products.models import Product

        drafts = Product.objects.all().by_status(PRODUCT_STATUS.DRAFT)
        assert product in drafts


# ═══════════════════════════════════════════════════════════════════════
# 6. Product Manager Search
# ═══════════════════════════════════════════════════════════════════════


class TestProductManagerSearch:
    """Test Product.objects.search() with real database."""

    def test_search_by_name(self, product, tenant_context):
        from apps.products.models import Product

        results = Product.objects.search("Test Phone")
        assert product in results

    def test_search_by_sku(self, product, tenant_context):
        from apps.products.models import Product

        results = Product.objects.search(product.sku)
        assert product in results

    def test_search_no_results(self, product, tenant_context):
        from apps.products.models import Product

        results = Product.objects.search("nonexistent_xyz_999")
        assert results.count() == 0

    def test_search_empty_query_returns_all(self, product, tenant_context):
        from apps.products.models import Product

        results = Product.objects.search("")
        assert results.count() >= 1

    def test_search_by_description(self, category, tenant_context):
        from apps.products.models import Product

        p = Product.objects.create(
            name="Described Product",
            category=category,
            description="unique searchable description",
        )
        results = Product.objects.search("unique searchable")
        assert p in results


# ═══════════════════════════════════════════════════════════════════════
# 7. Product API Endpoints
# ═══════════════════════════════════════════════════════════════════════


class TestProductAPIEndpoints:
    """Test API endpoints with real database using authenticated client."""

    # ── Brand API ───────────────────────────────────────────────────

    def test_brand_list(self, authenticated_client, brand):
        response = authenticated_client.get("/api/v1/brands/")
        assert response.status_code == 200

    def test_brand_create(self, authenticated_client, tenant_context):
        response = authenticated_client.post(
            "/api/v1/brands/",
            {"name": "New Brand", "description": "Test"},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["name"] == "New Brand"

    def test_brand_detail(self, authenticated_client, brand):
        response = authenticated_client.get(
            f"/api/v1/brands/{brand.pk}/"
        )
        assert response.status_code == 200
        assert response.data["name"] == "Samsung"

    def test_brand_update(self, authenticated_client, brand):
        response = authenticated_client.patch(
            f"/api/v1/brands/{brand.pk}/",
            {"description": "Updated"},
            format="json",
        )
        assert response.status_code == 200

    # ── TaxClass API ────────────────────────────────────────────────

    def test_tax_class_list(self, authenticated_client, tax_class):
        response = authenticated_client.get("/api/v1/tax-classes/")
        assert response.status_code == 200

    def test_tax_class_create(self, authenticated_client, tenant_context):
        response = authenticated_client.post(
            "/api/v1/tax-classes/",
            {"name": "New Tax", "rate": "10.00"},
            format="json",
        )
        assert response.status_code == 201

    def test_tax_class_detail(self, authenticated_client, tax_class):
        response = authenticated_client.get(
            f"/api/v1/tax-classes/{tax_class.pk}/"
        )
        assert response.status_code == 200

    # ── Product API ─────────────────────────────────────────────────

    def test_product_list(self, authenticated_client, product):
        response = authenticated_client.get("/api/v1/products/")
        assert response.status_code == 200

    def test_product_create(self, authenticated_client, category, tenant_context):
        response = authenticated_client.post(
            "/api/v1/products/",
            {"name": "API Product", "category": str(category.pk)},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["name"] == "API Product"

    def test_product_detail(self, authenticated_client, product):
        response = authenticated_client.get(
            f"/api/v1/products/{product.pk}/"
        )
        assert response.status_code == 200

    def test_product_update(self, authenticated_client, product):
        response = authenticated_client.patch(
            f"/api/v1/products/{product.pk}/",
            {"name": "Updated Phone"},
            format="json",
        )
        assert response.status_code == 200

    def test_product_published_endpoint(self, authenticated_client, product_active):
        response = authenticated_client.get(
            "/api/v1/products/published/"
        )
        assert response.status_code == 200

    def test_product_featured_endpoint(self, authenticated_client, tenant_context):
        response = authenticated_client.get(
            "/api/v1/products/featured/"
        )
        assert response.status_code == 200

    def test_unauthenticated_returns_401(self, tenant_context):
        from rest_framework.test import APIClient

        client = APIClient(HTTP_HOST="products.testserver")
        response = client.get("/api/v1/products/")
        assert response.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════
# 8. Product SKU Generation
# ═══════════════════════════════════════════════════════════════════════


class TestProductSKUGeneration:
    """Test auto-generated SKU format and uniqueness."""

    def test_auto_sku_starts_with_prd(self, product):
        assert product.sku.startswith("PRD-")

    def test_auto_sku_not_empty(self, product):
        assert product.sku != ""

    def test_sku_uniqueness(self, category, tenant_context):
        from apps.products.models import Product

        p1 = Product.objects.create(name="Product One", category=category)
        p2 = Product.objects.create(name="Product Two", category=category)
        assert p1.sku != p2.sku

    def test_explicit_sku_preserved(self, category, tenant_context):
        from apps.products.models import Product

        p = Product.objects.create(
            name="Custom SKU Product",
            category=category,
            sku="CUSTOM-001",
        )
        assert p.sku == "CUSTOM-001"

    def test_slug_auto_generated(self, category, tenant_context):
        from apps.products.models import Product

        p = Product.objects.create(name="Slug Test Product", category=category)
        assert p.slug == "slug-test-product"

    def test_explicit_slug_preserved(self, category, tenant_context):
        from apps.products.models import Product

        p = Product.objects.create(
            name="Custom Slug Product",
            category=category,
            slug="my-custom-slug",
        )
        assert p.slug == "my-custom-slug"


# ═══════════════════════════════════════════════════════════════════════
# 9. Extended API Integration Tests (Task 93)
# ═══════════════════════════════════════════════════════════════════════


class TestBrandAPIExtended:
    """Extended Brand API tests — delete, filter, search."""

    def test_brand_delete(self, authenticated_client, brand):
        response = authenticated_client.delete(
            f"/api/v1/brands/{brand.pk}/"
        )
        assert response.status_code == 204

    def test_brand_filter_active(self, authenticated_client, brand, tenant_context):
        from apps.products.models import Brand

        Brand.objects.create(name="Inactive Brand", is_active=False)
        response = authenticated_client.get(
            "/api/v1/brands/", {"is_active": "true"}
        )
        assert response.status_code == 200
        names = [b["name"] for b in response.data["results"]]
        assert "Inactive Brand" not in names

    def test_brand_search(self, authenticated_client, brand, tenant_context):
        from apps.products.models import Brand

        Brand.objects.create(name="Nike")
        response = authenticated_client.get(
            "/api/v1/brands/", {"search": "Samsung"}
        )
        assert response.status_code == 200
        names = [b["name"] for b in response.data["results"]]
        assert "Samsung" in names
        assert "Nike" not in names

    def test_brand_put_update(self, authenticated_client, brand):
        response = authenticated_client.put(
            f"/api/v1/brands/{brand.pk}/",
            {"name": "Samsung Updated", "description": "Full update"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["name"] == "Samsung Updated"


class TestTaxClassAPIExtended:
    """Extended TaxClass API tests — update, delete, filter."""

    def test_tax_class_update(self, authenticated_client, tax_class):
        response = authenticated_client.patch(
            f"/api/v1/tax-classes/{tax_class.pk}/",
            {"name": "Updated Tax", "rate": "18.00"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["rate"] == "18.00"

    def test_tax_class_delete(self, authenticated_client, tax_class):
        response = authenticated_client.delete(
            f"/api/v1/tax-classes/{tax_class.pk}/"
        )
        assert response.status_code == 204

    def test_tax_class_filter_default(self, authenticated_client, tenant_context):
        from apps.products.models import TaxClass

        TaxClass.objects.create(
            name="Default Tax", rate=Decimal("10.00"), is_default=True
        )
        TaxClass.objects.create(
            name="Non-Default", rate=Decimal("5.00"), is_default=False
        )
        response = authenticated_client.get(
            "/api/v1/tax-classes/", {"is_default": "true"}
        )
        assert response.status_code == 200
        results = response.data["results"]
        for tc in results:
            assert tc["is_default"] is True


class TestProductAPIExtended:
    """Extended Product API tests — delete, filters, search, pagination, auto-SKU."""

    def test_product_delete(self, authenticated_client, product):
        response = authenticated_client.delete(
            f"/api/v1/products/{product.pk}/"
        )
        assert response.status_code == 204

    def test_product_create_auto_sku(self, authenticated_client, category, tenant_context):
        response = authenticated_client.post(
            "/api/v1/products/",
            {"name": "Auto SKU Product", "category": str(category.pk)},
            format="json",
        )
        assert response.status_code == 201
        assert response.data["sku"].startswith("PRD-")
        assert len(response.data["sku"]) > 4

    def test_product_filter_by_category(
        self, authenticated_client, product, category, tenant_context
    ):
        response = authenticated_client.get(
            "/api/v1/products/", {"category": str(category.pk)}
        )
        assert response.status_code == 200
        results = response.data["results"]
        assert len(results) >= 1
        for p in results:
            assert p["category"] == str(category.pk) or p.get("category_name")

    def test_product_filter_by_brand(
        self, authenticated_client, product_active, brand, tenant_context
    ):
        response = authenticated_client.get(
            "/api/v1/products/", {"brand": str(brand.pk)}
        )
        assert response.status_code == 200
        results = response.data["results"]
        assert len(results) >= 1

    def test_product_filter_by_product_type(
        self, authenticated_client, product, tenant_context
    ):
        response = authenticated_client.get(
            "/api/v1/products/", {"product_type": "simple"}
        )
        assert response.status_code == 200
        for p in response.data["results"]:
            assert p["product_type"] == "simple"

    def test_product_filter_by_status(
        self, authenticated_client, product_active, tenant_context
    ):
        response = authenticated_client.get(
            "/api/v1/products/", {"status": "active"}
        )
        assert response.status_code == 200
        for p in response.data["results"]:
            assert p["status"] == "active"

    def test_product_search(
        self, authenticated_client, product, tenant_context
    ):
        response = authenticated_client.get(
            "/api/v1/products/", {"search": "Test Phone"}
        )
        assert response.status_code == 200
        names = [p["name"] for p in response.data["results"]]
        assert "Test Phone" in names

    def test_product_pagination(
        self, authenticated_client, category, tenant_context
    ):
        from apps.products.models import Product

        for i in range(15):
            Product.objects.create(
                name=f"Pagination Product {i}", category=category
            )
        response = authenticated_client.get("/api/v1/products/")
        assert response.status_code == 200
        # paginated response has count, next, previous, results
        assert "count" in response.data
        assert "results" in response.data
        assert response.data["count"] >= 15


# ═══════════════════════════════════════════════════════════════════════
# 10. Tenant Isolation Tests (Task 94)
# ═══════════════════════════════════════════════════════════════════════


class TestTenantIsolation:
    """Test product data is isolated between tenants."""

    @pytest.fixture
    def second_tenant(self, setup_test_tenant, db, django_db_blocker):
        """Create a second tenant for isolation testing."""
        schema = "test_products_iso"
        domain_name = "products-iso.testserver"

        with django_db_blocker.unblock():
            # Must be on public schema to create tenants
            connection.set_schema_to_public()

            # Clean up if exists from a previous run
            if TenantModel.objects.filter(schema_name=schema).exists():
                try:
                    t = TenantModel.objects.get(schema_name=schema)
                    t.delete(force_drop=True)
                except Exception:
                    pass  # schema may already be gone

            tenant = TenantModel(
                schema_name=schema,
                name="Isolation Test Tenant",
                slug="products-iso-test",
            )
            tenant.save(verbosity=0)

            domain = DomainModel(
                tenant=tenant,
                domain=domain_name,
                is_primary=True,
            )
            domain.save()

        yield tenant

        # Cleanup is handled at the start of the next run.
        # Dropping schema inside a test transaction causes
        # "pending trigger events" errors, so we skip teardown.
        connection.set_schema_to_public()

    def test_products_isolated_by_tenant(
        self, setup_test_tenant, second_tenant, db
    ):
        """Products created in one tenant shouldn't be visible in another."""
        from apps.products.models import Category, Product

        # Create data in tenant 1
        connection.set_tenant(setup_test_tenant)
        cat = Category.objects.create(name="Tenant1 Cat", slug="t1-cat")
        Product.objects.create(name="Tenant1 Product", category=cat)
        t1_count = Product.objects.count()
        assert t1_count >= 1

        # Switch to tenant 2
        connection.set_tenant(second_tenant)
        cat2 = Category.objects.create(name="Tenant2 Cat", slug="t2-cat")
        Product.objects.create(name="Tenant2 Product", category=cat2)
        t2_count = Product.objects.count()
        assert t2_count == 1  # only tenant 2's product

        # Switch back to tenant 1 — should still see tenant 1's data
        connection.set_tenant(setup_test_tenant)
        assert "Tenant1 Product" in [
            p.name for p in Product.objects.all()
        ]
        assert "Tenant2 Product" not in [
            p.name for p in Product.objects.all()
        ]

        connection.set_schema_to_public()

    def test_brands_isolated_by_tenant(
        self, setup_test_tenant, second_tenant, db
    ):
        """Brands in one tenant aren't visible in another."""
        from apps.products.models import Brand

        connection.set_tenant(setup_test_tenant)
        Brand.objects.create(name="Tenant1 Brand")
        assert Brand.objects.filter(name="Tenant1 Brand").exists()

        connection.set_tenant(second_tenant)
        assert not Brand.objects.filter(name="Tenant1 Brand").exists()

        connection.set_schema_to_public()

    def test_sku_unique_per_tenant(
        self, setup_test_tenant, second_tenant, db
    ):
        """Same SKU can exist in different tenants."""
        from apps.products.models import Category, Product

        connection.set_tenant(setup_test_tenant)
        cat1 = Category.objects.create(name="Cat1", slug="cat-sku-1")
        Product.objects.create(
            name="Product A", category=cat1, sku="SHARED-SKU-001"
        )

        connection.set_tenant(second_tenant)
        cat2 = Category.objects.create(name="Cat2", slug="cat-sku-2")
        # Same SKU in different tenant should NOT raise IntegrityError
        p2 = Product.objects.create(
            name="Product B", category=cat2, sku="SHARED-SKU-001"
        )
        assert p2.sku == "SHARED-SKU-001"

        connection.set_schema_to_public()

    def test_api_tenant_isolation(
        self, setup_test_tenant, second_tenant, db
    ):
        """API responses only show data for the requesting tenant."""
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient

        from apps.products.models import Brand

        connection.set_tenant(setup_test_tenant)
        Brand.objects.create(name="API Tenant1 Brand")

        connection.set_tenant(second_tenant)
        Brand.objects.create(name="API Tenant2 Brand")

        User = get_user_model()
        user2 = User.objects.create_user(
            email="tenant2@example.com", password="testpass123"
        )
        client2 = APIClient(HTTP_HOST="products-iso.testserver")
        client2.force_authenticate(user=user2)
        response = client2.get("/api/v1/brands/")
        assert response.status_code == 200
        names = [b["name"] for b in response.data["results"]]
        assert "API Tenant2 Brand" in names
        assert "API Tenant1 Brand" not in names

        connection.set_schema_to_public()


# ═══════════════════════════════════════════════════════════════════════
# 11. Permission Tests (Task 95)
# ═══════════════════════════════════════════════════════════════════════


class TestProductPermissions:
    """Test API permission enforcement."""

    def test_unauthenticated_list_denied(self, tenant_context):
        from rest_framework.test import APIClient

        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        response = client.get("/api/v1/products/")
        assert response.status_code in (401, 403)

    def test_unauthenticated_create_denied(self, tenant_context):
        from rest_framework.test import APIClient

        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        response = client.post(
            "/api/v1/products/",
            {"name": "Unauth Product"},
            format="json",
        )
        assert response.status_code in (401, 403)

    def test_unauthenticated_update_denied(self, product):
        from rest_framework.test import APIClient

        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        response = client.patch(
            f"/api/v1/products/{product.pk}/",
            {"name": "Hacked"},
            format="json",
        )
        assert response.status_code in (401, 403)

    def test_unauthenticated_delete_denied(self, product):
        from rest_framework.test import APIClient

        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        response = client.delete(f"/api/v1/products/{product.pk}/")
        assert response.status_code in (401, 403)

    def test_unauthenticated_brands_denied(self, tenant_context):
        from rest_framework.test import APIClient

        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        response = client.get("/api/v1/brands/")
        assert response.status_code in (401, 403)

    def test_unauthenticated_tax_classes_denied(self, tenant_context):
        from rest_framework.test import APIClient

        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        response = client.get("/api/v1/tax-classes/")
        assert response.status_code in (401, 403)

    def test_authenticated_can_list(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/products/")
        assert response.status_code == 200

    def test_authenticated_can_create(
        self, authenticated_client, category, tenant_context
    ):
        response = authenticated_client.post(
            "/api/v1/products/",
            {"name": "Auth Product", "category": str(category.pk)},
            format="json",
        )
        assert response.status_code == 201

    def test_authenticated_can_update(self, authenticated_client, product):
        response = authenticated_client.patch(
            f"/api/v1/products/{product.pk}/",
            {"name": "Auth Updated"},
            format="json",
        )
        assert response.status_code == 200

    def test_authenticated_can_delete(self, authenticated_client, product):
        response = authenticated_client.delete(
            f"/api/v1/products/{product.pk}/"
        )
        assert response.status_code == 204
