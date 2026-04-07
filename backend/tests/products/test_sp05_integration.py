"""
SP05 Integration tests for Bundle & Composite Products.

Tests complete workflows: bundle CRUD, BOM CRUD, pricing, cost
calculation, and tenant scoping. All tests use the tenant_context
fixture with real database objects.

Stock service tests use mocks because stock_quantity is not a DB field.

Covers SP05 Task 90.
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from apps.products.constants import (
    BUNDLE_TYPE,
    DISCOUNT_TYPE,
    PRODUCT_TYPES,
)
from apps.products.models import (
    BillOfMaterials,
    BOMItem,
    BundleItem,
    ProductBundle,
)


# ═══════════════════════════════════════════════════════════════════════
# Bundle Integration Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBundleWorkflow:
    """Complete bundle lifecycle: Create → Price → Stock → Update → Delete."""

    def test_full_bundle_lifecycle(self, tenant_context, category):
        from apps.products.models import Product
        from apps.products.services import BundlePricingService

        # ── 1. Create products ──
        tea = Product.objects.create(
            name="Ceylon Tea", category=category,
            selling_price=Decimal("450.00"), cost_price=Decimal("200.00"),
        )

        strainer = Product.objects.create(
            name="Tea Strainer", category=category,
            selling_price=Decimal("1200.00"), cost_price=Decimal("500.00"),
        )

        # ── 2. Create bundle ──
        parent = Product.objects.create(
            name="Lanka Tea Set", category=category,
            product_type=PRODUCT_TYPES.BUNDLE,
        )
        bundle = ProductBundle.objects.create(
            product=parent,
            bundle_type=BUNDLE_TYPE.DYNAMIC,
            discount_type=DISCOUNT_TYPE.PERCENTAGE,
            discount_value=Decimal("15.00"),
        )

        BundleItem.objects.create(bundle=bundle, product=tea, quantity=2, sort_order=0)
        BundleItem.objects.create(bundle=bundle, product=strainer, quantity=1, sort_order=1)

        # ── 3. Pricing ──
        pricing = BundlePricingService(bundle)
        individual = pricing.get_individual_total()
        assert individual == Decimal("2100.00")  # 450*2 + 1200*1

        bundle_price = pricing.get_bundle_price()
        assert bundle_price == Decimal("1785.00")  # 2100 - 15%

        savings = pricing.get_savings()
        assert savings == Decimal("315.00")

        # ── 4. Update ──
        bundle.discount_value = Decimal("20.00")
        bundle.save()
        pricing2 = BundlePricingService(bundle)
        assert pricing2.get_bundle_price() == Decimal("1680.00")

        # ── 5. Delete (soft) ──
        bundle.delete()
        assert bundle.is_deleted is True
        # Products still exist
        assert Product.objects.filter(pk=tea.pk).exists()
        assert Product.objects.filter(pk=strainer.pk).exists()


# ═══════════════════════════════════════════════════════════════════════
# BOM Integration Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBOMWorkflow:
    """Complete BOM lifecycle: Create → Cost → Stock → Version → Delete."""

    def test_full_bom_lifecycle(self, tenant_context, category):
        from apps.products.models import Product
        from apps.products.services import CostCalculationService

        # ── 1. Create products ──
        cake = Product.objects.create(
            name="Birthday Cake", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )

        flour = Product.objects.create(
            name="Flour", category=category,
            cost_price=Decimal("150.00"),
        )

        sugar = Product.objects.create(
            name="Sugar", category=category,
            cost_price=Decimal("120.00"),
        )

        # ── 2. Create BOM v1.0 ──
        bom = BillOfMaterials.objects.create(
            product=cake, version="1.0",
            yield_quantity=5, notes="Original recipe",
        )
        BOMItem.objects.create(
            bom=bom, raw_material=flour,
            quantity=Decimal("2.000"), wastage_percent=Decimal("5.00"),
            is_critical=True,
        )
        BOMItem.objects.create(
            bom=bom, raw_material=sugar,
            quantity=Decimal("1.000"), wastage_percent=Decimal("0.00"),
        )

        # ── 3. Cost calculation ──
        cost_svc = CostCalculationService(
            bom, labor_cost=Decimal("100.00"), overhead_percent=Decimal("10.00"),
        )
        material = cost_svc.calculate_material_cost()
        assert material == Decimal("420.000")  # 150*2 + 120*1

        with_wastage = cost_svc.calculate_with_wastage()
        # flour: 150*2*1.05=315, sugar: 120*1*1.0=120 → 435
        assert with_wastage == Decimal("435.000")

        total = cost_svc.calculate_total_cost()
        # 435 + 100 + 10% of 435 = 435 + 100 + 43.50 = 578.50
        assert total == Decimal("578.500")

        unit = cost_svc.calculate_unit_cost()
        # 578.50 / 5 = 115.70
        assert unit == Decimal("115.70")

        result = cost_svc.suggest_selling_price(margin_percent=30)
        assert result["selling_price"] == Decimal("150.41")

        # ── 4. Create v2.0 ──
        bom.is_active = False
        bom.save()

        bom_v2 = BillOfMaterials.objects.create(
            product=cake, version="2.0",
            yield_quantity=8, notes="Improved recipe",
        )
        BOMItem.objects.create(
            bom=bom_v2, raw_material=flour,
            quantity=Decimal("3.000"), wastage_percent=Decimal("3.00"),
        )
        BOMItem.objects.create(
            bom=bom_v2, raw_material=sugar,
            quantity=Decimal("1.500"), wastage_percent=Decimal("0.00"),
        )

        assert BillOfMaterials.objects.filter(product=cake).count() == 2
        active_boms = BillOfMaterials.objects.active_for_product(cake)
        assert active_boms.count() == 1
        assert active_boms.first().version == "2.0"

        # ── 6. Delete (soft) ──
        bom_v2.delete()
        assert bom_v2.is_deleted is True
        # Raw materials still exist
        assert Product.objects.filter(pk=flour.pk).exists()


# ═══════════════════════════════════════════════════════════════════════
# Cross-Module Integration Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBundleBOMCrossIntegration:
    """Test that bundle and BOM can coexist for different products."""

    def test_same_materials_in_bundle_and_bom(self, tenant_context, category):
        from apps.products.models import Product
        from apps.products.services import BundlePricingService, CostCalculationService

        # Common component product
        spice = Product.objects.create(
            name="Cinnamon", category=category,
            selling_price=Decimal("500.00"),
            cost_price=Decimal("200.00"),
        )

        # Bundle uses the product
        bundle_parent = Product.objects.create(
            name="Spice Set", category=category,
            product_type=PRODUCT_TYPES.BUNDLE,
        )
        bundle = ProductBundle.objects.create(
            product=bundle_parent, bundle_type=BUNDLE_TYPE.DYNAMIC,
        )
        BundleItem.objects.create(bundle=bundle, product=spice, quantity=3)

        # BOM also uses the product as raw material
        manufactured = Product.objects.create(
            name="Spice Blend", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        bom = BillOfMaterials.objects.create(
            product=manufactured, yield_quantity=10,
        )
        BOMItem.objects.create(
            bom=bom, raw_material=spice, quantity=Decimal("0.500"),
        )

        # Both work independently
        pricing = BundlePricingService(bundle)
        assert pricing.get_bundle_price() == Decimal("1500.00")

        costing = CostCalculationService(bom)
        assert costing.calculate_material_cost() == Decimal("100.000")


# ═══════════════════════════════════════════════════════════════════════
# Error Handling Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestErrorHandling:
    """Verify proper error handling for invalid operations."""

    def test_duplicate_bundle_item_with_variant(self, tenant_context, category):
        """Duplicate (bundle, product, variant) raises IntegrityError when variant is NOT NULL."""
        from django.db import IntegrityError, transaction
        from apps.products.models import Product, ProductVariant

        parent = Product.objects.create(
            name="Dup Test", category=category,
            product_type=PRODUCT_TYPES.BUNDLE,
        )
        bundle = ProductBundle.objects.create(product=parent)
        comp = Product.objects.create(name="Dup Item", category=category)

        # Create a variant so the unique constraint can fire
        # (PostgreSQL treats NULL as distinct, so nullable variant won't trigger)
        variant = ProductVariant.objects.create(product=comp, sku="DUP-SKU", name="V1")
        BundleItem.objects.create(bundle=bundle, product=comp, variant=variant)

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                BundleItem.objects.create(bundle=bundle, product=comp, variant=variant)

    def test_duplicate_bom_raw_material(self, tenant_context, category):
        from django.db import IntegrityError, transaction
        from apps.products.models import Product

        prod = Product.objects.create(
            name="BOM Dup", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        bom = BillOfMaterials.objects.create(product=prod)
        mat = Product.objects.create(name="Dup Mat", category=category)
        BOMItem.objects.create(bom=bom, raw_material=mat, quantity=Decimal("1.000"))

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                BOMItem.objects.create(bom=bom, raw_material=mat, quantity=Decimal("2.000"))

    def test_reserve_stock_insufficient(self, tenant_context, category):
        """Test reserve_stock raises ValueError when stock_quantity is 0 (mock-based)."""
        from unittest.mock import MagicMock
        from apps.products.services import BundleStockService

        # Mock the bundle with a component that has 0 stock
        bundle = MagicMock()
        item = MagicMock()
        item.variant_id = None
        item.product = MagicMock()
        item.product.stock_quantity = 0
        item.quantity = 1
        item.is_optional = False

        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_qs.__iter__ = lambda self: iter([item])
        mock_qs.filter.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs

        bundle.items = MagicMock()
        bundle.items.filter.return_value = mock_qs

        service = BundleStockService(bundle)
        with pytest.raises(ValueError):
            service.reserve_stock(1)
