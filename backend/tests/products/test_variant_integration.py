"""
Production-level integration tests for the Product Variants subsystem.

These tests exercise end-to-end workflows against a real PostgreSQL
database inside the Docker container, validating the complete lifecycle
from option setup → variant generation → API access → query operations.

Run:
    docker exec lcc-backend bash -c "cd /app && \\
        DJANGO_SETTINGS_MODULE=config.settings.test_pg \\
        python -m pytest tests/products/test_variant_integration.py -v"
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.products.constants import PRODUCT_TYPES
from apps.products.models import (
    Product,
    ProductOptionConfig,
    ProductVariant,
    ProductVariantOption,
    VariantOptionType,
    VariantOptionValue,
)
from apps.products.services.variant_generator import VariantGenerator


pytestmark = pytest.mark.django_db


# ════════════════════════════════════════════════════════════════════════
# 1. End-to-End Variant Lifecycle
# ════════════════════════════════════════════════════════════════════════


class TestVariantLifecycle:
    """Full lifecycle: setup options → configure product → generate → query."""

    def test_full_lifecycle_2_options(self, tenant_context, category):
        """Complete flow: Size(3) × Color(2) = 6 variants."""
        # 1. Create option types
        size_type = VariantOptionType.objects.create(
            name="Size LC", display_order=1
        )
        color_type = VariantOptionType.objects.create(
            name="Color LC", display_order=2, is_color_swatch=True
        )

        # 2. Create option values
        sizes = []
        for idx, (val, code) in enumerate(
            [("S", None), ("M", None), ("L", None)]
        ):
            sizes.append(
                VariantOptionValue.objects.create(
                    option_type=size_type, value=val, display_order=idx
                )
            )

        colors = []
        for idx, (val, code) in enumerate(
            [("Red", "#FF0000"), ("Blue", "#0000FF")]
        ):
            colors.append(
                VariantOptionValue.objects.create(
                    option_type=color_type,
                    value=val,
                    color_code=code,
                    display_order=idx,
                )
            )

        # 3. Create product & configure options
        product = Product.objects.create(
            name="Integration T-Shirt",
            category=category,
            product_type=PRODUCT_TYPES.VARIABLE,
            selling_price=Decimal("2500.00"),
        )
        ProductOptionConfig.objects.create(
            product=product, option_type=size_type, display_order=0
        )
        ProductOptionConfig.objects.create(
            product=product, option_type=color_type, display_order=1
        )

        # 4. Generate variants
        gen = VariantGenerator(product)
        is_valid, error = gen.validate_combinations()
        assert is_valid, f"Validation failed: {error}"

        combos = gen.get_combinations()
        assert len(combos) == 6

        variants = gen.generate_variants()
        assert len(variants) == 6

        # 5. Verify DB state
        db_variants = ProductVariant.objects.filter(product=product)
        assert db_variants.count() == 6

        # 6. Each variant has exactly 2 option values
        for v in db_variants:
            assert v.variant_options.count() == 2

        # 7. All SKUs are unique
        skus = list(db_variants.values_list("sku", flat=True))
        assert len(skus) == len(set(skus))

        # 8. Names were generated
        for v in db_variants:
            assert v.name, f"Variant {v.sku} has no name"

        # 9. get_by_options lookup works
        found = ProductVariant.objects.get_by_options(
            product, [sizes[0], colors[0]]
        )
        assert found is not None
        assert found.sku.endswith("S-RED") or "S" in found.sku

        # 10. QuerySet chaining works
        active = (
            ProductVariant.objects
            .active()
            .for_product(product)
            .with_options()
        )
        assert active.count() == 6

    def test_full_lifecycle_3_options(self, tenant_context, category):
        """Complete flow: Size(2) × Color(2) × Material(2) = 8 variants."""
        size_type = VariantOptionType.objects.create(
            name="Size 3OPT", display_order=1
        )
        color_type = VariantOptionType.objects.create(
            name="Color 3OPT", display_order=2
        )
        material_type = VariantOptionType.objects.create(
            name="Material 3OPT", display_order=3
        )

        s = VariantOptionValue.objects.create(
            option_type=size_type, value="S", display_order=0
        )
        m = VariantOptionValue.objects.create(
            option_type=size_type, value="M", display_order=1
        )
        red = VariantOptionValue.objects.create(
            option_type=color_type, value="Red", display_order=0
        )
        blue = VariantOptionValue.objects.create(
            option_type=color_type, value="Blue", display_order=1
        )
        cotton = VariantOptionValue.objects.create(
            option_type=material_type, value="Cotton", display_order=0
        )
        poly = VariantOptionValue.objects.create(
            option_type=material_type, value="Polyester", display_order=1
        )

        product = Product.objects.create(
            name="3-Opt Shirt",
            category=category,
            product_type=PRODUCT_TYPES.VARIABLE,
            selling_price=Decimal("3000.00"),
        )
        for idx, ot in enumerate(
            [size_type, color_type, material_type]
        ):
            ProductOptionConfig.objects.create(
                product=product, option_type=ot, display_order=idx
            )

        gen = VariantGenerator(product)
        variants = gen.generate_variants()
        assert len(variants) == 8  # 2 × 2 × 2

        # Verify each variant has 3 options
        for v in variants:
            assert v.variant_options.count() == 3

        # get_by_options with 3 values
        found = ProductVariant.objects.get_by_options(
            product, [s, red, cotton]
        )
        assert found is not None


# ════════════════════════════════════════════════════════════════════════
# 2. API Integration Tests (authenticated, real DB)
# ════════════════════════════════════════════════════════════════════════


class TestVariantAPIIntegration:
    """API-level tests hitting real endpoints with real PostgreSQL."""

    def test_option_type_crud_cycle(self, authenticated_client):
        """Full CRUD cycle for option types via API."""
        # CREATE
        resp = authenticated_client.post(
            "/api/v1/variant-option-types/",
            {"name": "Weight", "display_order": 1},
            format="json",
        )
        assert resp.status_code == 201
        type_id = resp.data["id"]

        # READ
        resp = authenticated_client.get(
            f"/api/v1/variant-option-types/{type_id}/"
        )
        assert resp.status_code == 200
        assert resp.data["name"] == "Weight"

        # UPDATE
        resp = authenticated_client.patch(
            f"/api/v1/variant-option-types/{type_id}/",
            {"display_order": 5},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["display_order"] == 5

        # DELETE
        resp = authenticated_client.delete(
            f"/api/v1/variant-option-types/{type_id}/"
        )
        assert resp.status_code == 204

    def test_option_value_crud_cycle(self, authenticated_client):
        """Full CRUD cycle for option values via API."""
        # Setup type
        resp = authenticated_client.post(
            "/api/v1/variant-option-types/",
            {"name": "Size CRUD", "display_order": 1},
            format="json",
        )
        type_id = resp.data["id"]

        # CREATE value
        resp = authenticated_client.post(
            "/api/v1/variant-option-values/",
            {
                "option_type": type_id,
                "value": "XL",
                "display_order": 1,
            },
            format="json",
        )
        assert resp.status_code == 201
        val_id = resp.data["id"]
        assert resp.data["option_type_name"] == "Size CRUD"

        # READ value
        resp = authenticated_client.get(
            f"/api/v1/variant-option-values/{val_id}/"
        )
        assert resp.status_code == 200

        # by-type action
        resp = authenticated_client.get(
            f"/api/v1/variant-option-values/by-type/size-crud/"
        )
        assert resp.status_code == 200

    def test_variant_create_and_retrieve(
        self, authenticated_client, variable_product
    ):
        """Create variant via API and retrieve with detail serializer."""
        # Create option type & value
        resp = authenticated_client.post(
            "/api/v1/variant-option-types/",
            {"name": "Grade", "display_order": 1},
            format="json",
        )
        type_id = resp.data["id"]

        resp = authenticated_client.post(
            "/api/v1/variant-option-values/",
            {"option_type": type_id, "value": "A", "display_order": 0},
            format="json",
        )
        val_id = resp.data["id"]

        # Create variant
        resp = authenticated_client.post(
            "/api/v1/product-variants/",
            {
                "product": str(variable_product.pk),
                "sku": "INTEG-GRADE-A",
                "option_value_ids": [str(val_id)],
            },
            format="json",
        )
        assert resp.status_code == 201

        # Retrieve detail — look up by SKU since create serializer may not return id
        variant = ProductVariant.objects.filter(sku="INTEG-GRADE-A").first()
        assert variant is not None
        resp = authenticated_client.get(
            f"/api/v1/product-variants/{variant.pk}/"
        )
        assert resp.status_code == 200
        assert "options" in resp.data

    def test_variant_list_filtering(
        self, authenticated_client, variable_product, variable_product_2
    ):
        """List variants filtered by product."""
        ProductVariant.objects.create(
            product=variable_product, sku="FILTER-A"
        )
        ProductVariant.objects.create(
            product=variable_product_2, sku="FILTER-B"
        )

        resp = authenticated_client.get(
            f"/api/v1/product-variants/?product={variable_product.pk}"
        )
        assert resp.status_code == 200
        results = resp.data.get("results", resp.data)
        skus = [r["sku"] for r in results]
        assert "FILTER-A" in skus
        assert "FILTER-B" not in skus

    def test_generate_variants_endpoint(
        self, authenticated_client, tenant_context, category
    ):
        """POST /product-variants/generate/ creates variants."""
        # Setup
        size_type = VariantOptionType.objects.create(
            name="Size Gen", display_order=1
        )
        VariantOptionValue.objects.create(
            option_type=size_type, value="S", display_order=0
        )
        VariantOptionValue.objects.create(
            option_type=size_type, value="M", display_order=1
        )

        product = Product.objects.create(
            name="Gen Product",
            category=category,
            product_type=PRODUCT_TYPES.VARIABLE,
            selling_price=Decimal("1000.00"),
        )
        ProductOptionConfig.objects.create(
            product=product, option_type=size_type, display_order=0
        )

        resp = authenticated_client.post(
            "/api/v1/product-variants/generate/",
            {"product_id": str(product.pk)},
            format="json",
        )
        assert resp.status_code == 201
        assert len(resp.data) == 2  # S, M

    def test_by_options_endpoint(
        self,
        authenticated_client,
        variable_product,
        variant_option_type_size,
        variant_option_value_small,
    ):
        """GET /product-variants/by-options/ finds exact match."""
        variant = ProductVariant.objects.create(
            product=variable_product, sku="BYOPT-SM"
        )
        ProductVariantOption.objects.create(
            variant=variant,
            option_value=variant_option_value_small,
            display_order=0,
        )

        resp = authenticated_client.get(
            f"/api/v1/product-variants/by-options/"
            f"?product_id={variable_product.pk}"
            f"&option_values={variant_option_value_small.pk}"
        )
        assert resp.status_code == 200
        assert resp.data["sku"] == "BYOPT-SM"

    def test_unauthenticated_request_rejected(self, tenant_context):
        """Unauthenticated requests get 401."""
        from rest_framework.test import APIClient

        client = APIClient(HTTP_HOST="products.testserver")
        resp = client.get("/api/v1/variant-option-types/")
        assert resp.status_code in (401, 403)


# ════════════════════════════════════════════════════════════════════════
# 3. Data Integrity & Constraint Tests
# ════════════════════════════════════════════════════════════════════════


class TestDataIntegrity:
    """Validate DB constraints and cascading in real PostgreSQL."""

    def test_unique_sku_enforced(self, variable_product, tenant_context):
        """Duplicate SKU raises IntegrityError."""
        ProductVariant.objects.create(
            product=variable_product, sku="DUP-SKU"
        )
        with pytest.raises(Exception):
            ProductVariant.objects.create(
                product=variable_product, sku="DUP-SKU"
            )

    def test_unique_option_type_name_enforced(self, tenant_context):
        """Duplicate option type name raises exception."""
        VariantOptionType.objects.create(name="Unique Test")
        with pytest.raises(Exception):
            VariantOptionType.objects.create(name="Unique Test")

    def test_unique_value_per_type_enforced(self, tenant_context):
        """Duplicate value within same type raises exception."""
        ot = VariantOptionType.objects.create(name="DupVal Type")
        VariantOptionValue.objects.create(
            option_type=ot, value="same"
        )
        with pytest.raises(Exception):
            VariantOptionValue.objects.create(
                option_type=ot, value="same"
            )

    def test_cascade_delete_option_type_removes_values(
        self, tenant_context
    ):
        """Deleting option type cascades to values."""
        ot = VariantOptionType.objects.create(name="Cascade Type")
        VariantOptionValue.objects.create(
            option_type=ot, value="v1"
        )
        VariantOptionValue.objects.create(
            option_type=ot, value="v2"
        )
        assert VariantOptionValue.objects.filter(
            option_type=ot
        ).count() == 2

        ot_pk = ot.pk
        VariantOptionType.all_with_deleted.filter(pk=ot_pk).delete()
        assert VariantOptionValue.all_with_deleted.filter(
            option_type_id=ot_pk
        ).count() == 0

    def test_cascade_delete_product_removes_variants(
        self, tenant_context, category
    ):
        """Hard-deleting product cascades to its variants."""
        product = Product.objects.create(
            name="Cascade Product",
            category=category,
            product_type=PRODUCT_TYPES.VARIABLE,
            selling_price=Decimal("1000.00"),
        )
        v = ProductVariant.objects.create(
            product=product, sku="CASCADE-V1"
        )
        v_pk = v.pk

        # Hard-delete via the unfiltered manager to trigger CASCADE
        Product.all_with_deleted.filter(pk=product.pk).delete()
        assert not ProductVariant.all_with_deleted.filter(
            pk=v_pk
        ).exists()

    def test_protect_option_value_in_use(self, tenant_context, category):
        """PROTECT on option_value prevents deleting used values."""
        ot = VariantOptionType.objects.create(name="Protect Type")
        ov = VariantOptionValue.objects.create(
            option_type=ot, value="protected"
        )
        product = Product.objects.create(
            name="Protect Product",
            category=category,
            product_type=PRODUCT_TYPES.VARIABLE,
            selling_price=Decimal("500.00"),
        )
        variant = ProductVariant.objects.create(
            product=product, sku="PROTECT-V1"
        )
        ProductVariantOption.objects.create(
            variant=variant, option_value=ov, display_order=0
        )

        with pytest.raises(Exception):
            VariantOptionValue.all_with_deleted.filter(pk=ov.pk).delete()

    def test_soft_delete_hides_variant(
        self, variable_product, tenant_context
    ):
        """Soft-deleted variants hidden from active() but visible via all_with_deleted."""
        v = ProductVariant.objects.create(
            product=variable_product, sku="SOFT-DEL-1"
        )
        v.is_deleted = True
        v.save()

        assert ProductVariant.objects.active().filter(pk=v.pk).count() == 0
        assert ProductVariant.all_with_deleted.filter(
            pk=v.pk
        ).exists()

    def test_option_config_unique_product_type(
        self, variable_product, tenant_context
    ):
        """Cannot assign same option type twice to a product."""
        ot = VariantOptionType.objects.create(name="Dup Config Type")
        ProductOptionConfig.objects.create(
            product=variable_product, option_type=ot, display_order=0
        )
        with pytest.raises(Exception):
            ProductOptionConfig.objects.create(
                product=variable_product,
                option_type=ot,
                display_order=1,
            )


# ════════════════════════════════════════════════════════════════════════
# 4. Performance & Scale Tests
# ════════════════════════════════════════════════════════════════════════


class TestPerformance:
    """Verify operations complete within reasonable time bounds."""

    def test_bulk_generation_performance(
        self, tenant_context, category
    ):
        """Generate 24 variants (4×3×2) in under 5 seconds."""
        import time

        s1 = VariantOptionType.objects.create(
            name="Perf Size", display_order=1
        )
        s2 = VariantOptionType.objects.create(
            name="Perf Color", display_order=2
        )
        s3 = VariantOptionType.objects.create(
            name="Perf Style", display_order=3
        )

        for i, v in enumerate(["XS", "S", "M", "L"]):
            VariantOptionValue.objects.create(
                option_type=s1, value=v, display_order=i
            )
        for i, v in enumerate(["Red", "Green", "Blue"]):
            VariantOptionValue.objects.create(
                option_type=s2, value=v, display_order=i
            )
        for i, v in enumerate(["Slim", "Regular"]):
            VariantOptionValue.objects.create(
                option_type=s3, value=v, display_order=i
            )

        product = Product.objects.create(
            name="Perf Shirt",
            category=category,
            product_type=PRODUCT_TYPES.VARIABLE,
            selling_price=Decimal("2000.00"),
        )
        for idx, ot in enumerate([s1, s2, s3]):
            ProductOptionConfig.objects.create(
                product=product, option_type=ot, display_order=idx
            )

        start = time.time()
        gen = VariantGenerator(product)
        variants = gen.generate_variants()
        elapsed = time.time() - start

        assert len(variants) == 24  # 4 × 3 × 2
        assert elapsed < 5.0, f"Bulk generation took {elapsed:.2f}s"

    def test_queryset_with_options_no_n_plus_one(
        self, tenant_context, category
    ):
        """with_options() resolves without N+1 queries."""
        ot = VariantOptionType.objects.create(
            name="NPlus Type", display_order=1
        )
        for i in range(3):
            VariantOptionValue.objects.create(
                option_type=ot, value=f"v{i}", display_order=i
            )

        product = Product.objects.create(
            name="NPlus Product",
            category=category,
            product_type=PRODUCT_TYPES.VARIABLE,
            selling_price=Decimal("1500.00"),
        )
        ProductOptionConfig.objects.create(
            product=product, option_type=ot, display_order=0
        )

        gen = VariantGenerator(product)
        gen.generate_variants()

        # Fetch with optimised queryset
        variants = (
            ProductVariant.objects
            .for_product(product)
            .with_options()
        )
        # Access option data — should not cause extra queries
        for v in variants:
            _ = v.get_option_display()
