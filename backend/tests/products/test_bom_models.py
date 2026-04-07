"""
BOM model and manufacturing service tests.

Tests for BillOfMaterials, BOMItem models, CostCalculationService,
and ManufacturingStockService. Model unit tests are DB-free; service
tests use the tenant_context fixture.

Covers SP05 Tasks 85-88.
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from django.db import models

from apps.products.constants import PRODUCT_TYPES
from apps.products.models import BillOfMaterials, BOMItem
from apps.products.models.bom import BOMQuerySet, BOMManager


# ═══════════════════════════════════════════════════════════════════════
# Helpers — create model instances without hitting the database
# ═══════════════════════════════════════════════════════════════════════


def _make_bom(**kwargs):
    """Instantiate a BillOfMaterials via ``__new__`` (no DB)."""
    from django.db.models.base import ModelState

    obj = BillOfMaterials.__new__(BillOfMaterials)
    obj._state = ModelState()
    defaults = {
        "id": uuid.uuid4(),
        "product_id": uuid.uuid4(),
        "version": "1.0",
        "is_active": True,
        "notes": None,
        "yield_quantity": 1,
        "is_deleted": False,
        "created_on": None,
        "updated_on": None,
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_bom_item(**kwargs):
    """Instantiate a BOMItem via ``__new__`` (no DB)."""
    from django.db.models.base import ModelState

    obj = BOMItem.__new__(BOMItem)
    obj._state = ModelState()
    defaults = {
        "id": uuid.uuid4(),
        "bom_id": uuid.uuid4(),
        "raw_material_id": uuid.uuid4(),
        "quantity": Decimal("1.000"),
        "unit_id": None,
        "wastage_percent": Decimal("0.00"),
        "is_critical": False,
        "substitute_id": None,
        "sort_order": 0,
        "is_active": True,
        "is_deleted": False,
        "created_on": None,
        "updated_on": None,
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


# ═══════════════════════════════════════════════════════════════════════
# Task 85 & 86: BillOfMaterials Model Tests
# ═══════════════════════════════════════════════════════════════════════


class TestBillOfMaterialsModelMeta:
    """Verify BillOfMaterials model field definitions via _meta."""

    def test_db_table(self):
        assert BillOfMaterials._meta.db_table == "products_bom"

    def test_verbose_name(self):
        assert str(BillOfMaterials._meta.verbose_name) == "Bill of Materials"

    def test_default_ordering(self):
        assert BillOfMaterials._meta.ordering == ["-created_on"]

    def test_product_field_fk(self):
        field = BillOfMaterials._meta.get_field("product")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.on_delete == models.PROTECT

    def test_version_field(self):
        field = BillOfMaterials._meta.get_field("version")
        assert isinstance(field, models.CharField)
        assert field.max_length == 20
        assert field.default == "1.0"

    def test_is_active_field(self):
        field = BillOfMaterials._meta.get_field("is_active")
        assert isinstance(field, models.BooleanField)
        assert field.default is True

    def test_notes_field(self):
        field = BillOfMaterials._meta.get_field("notes")
        assert isinstance(field, models.TextField)
        assert field.null is True

    def test_yield_quantity_field(self):
        field = BillOfMaterials._meta.get_field("yield_quantity")
        assert isinstance(field, models.PositiveIntegerField)
        assert field.default == 1

    def test_unique_constraint_exists(self):
        constraint_names = [c.name for c in BillOfMaterials._meta.constraints]
        assert "unique_product_bom_version" in constraint_names


class TestBillOfMaterialsStr:
    """Test BillOfMaterials __str__ and __repr__."""

    def test_str_with_product(self):
        product = MagicMock()
        product.name = "Birthday Cake"
        bom = _make_bom(version="2.1")
        bom._state.fields_cache["product"] = product
        assert str(bom) == "Birthday Cake BOM v2.1"

    def test_repr_active(self):
        product = MagicMock()
        product.name = "Table"
        bom = _make_bom(version="1.0", is_active=True)
        bom._state.fields_cache["product"] = product
        r = repr(bom)
        assert "Table" in r
        assert "v1.0" in r
        assert "active" in r

    def test_repr_inactive(self):
        product = MagicMock()
        product.name = "Chair"
        bom = _make_bom(version="1.0", is_active=False)
        bom._state.fields_cache["product"] = product
        r = repr(bom)
        assert "inactive" in r


class TestBOMManagerSetup:
    """Verify BOMManager is wired correctly."""

    def test_default_manager_is_bom_manager(self):
        assert isinstance(BillOfMaterials.objects, BOMManager)

    def test_all_with_deleted_manager_exists(self):
        assert hasattr(BillOfMaterials, "all_with_deleted")


# ═══════════════════════════════════════════════════════════════════════
# Task 85 & 86: BOMItem Model Tests
# ═══════════════════════════════════════════════════════════════════════


class TestBOMItemModelMeta:
    """Verify BOMItem model field definitions via _meta."""

    def test_db_table(self):
        assert BOMItem._meta.db_table == "products_bom_item"

    def test_verbose_name(self):
        assert str(BOMItem._meta.verbose_name) == "BOM Item"

    def test_ordering(self):
        assert BOMItem._meta.ordering == ["sort_order", "raw_material__name"]

    def test_bom_field_fk_cascade(self):
        field = BOMItem._meta.get_field("bom")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.on_delete == models.CASCADE

    def test_raw_material_field_fk_protect(self):
        field = BOMItem._meta.get_field("raw_material")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.on_delete == models.PROTECT

    def test_quantity_field(self):
        field = BOMItem._meta.get_field("quantity")
        assert isinstance(field, models.DecimalField)
        assert field.max_digits == 10
        assert field.decimal_places == 3

    def test_unit_field_nullable(self):
        field = BOMItem._meta.get_field("unit")
        assert isinstance(field, models.ForeignKey)
        assert field.null is True

    def test_wastage_percent_field(self):
        field = BOMItem._meta.get_field("wastage_percent")
        assert isinstance(field, models.DecimalField)
        assert field.max_digits == 5
        assert field.decimal_places == 2

    def test_is_critical_field(self):
        field = BOMItem._meta.get_field("is_critical")
        assert isinstance(field, models.BooleanField)
        assert field.default is False

    def test_substitute_field_nullable(self):
        field = BOMItem._meta.get_field("substitute")
        assert isinstance(field, models.ForeignKey)
        assert field.null is True
        assert field.remote_field.on_delete == models.SET_NULL

    def test_unique_constraint(self):
        constraint_names = [c.name for c in BOMItem._meta.constraints]
        assert "unique_bom_raw_material" in constraint_names


class TestBOMItemStr:
    """Test BOMItem __str__ and __repr__."""

    def test_str_without_unit(self):
        raw_mat = MagicMock()
        raw_mat.name = "Flour"
        item = _make_bom_item(quantity=Decimal("500.000"))
        item._state.fields_cache["raw_material"] = raw_mat
        item.unit_id = None
        assert str(item) == "Flour (500.000)"

    def test_str_with_unit(self):
        raw_mat = MagicMock()
        raw_mat.name = "Sugar"
        unit = MagicMock()
        unit.symbol = "kg"
        item = _make_bom_item(quantity=Decimal("2.000"), unit_id=uuid.uuid4())
        item._state.fields_cache["raw_material"] = raw_mat
        item._state.fields_cache["unit"] = unit
        assert str(item) == "Sugar (2.000 kg)"

    def test_repr(self):
        raw_mat = MagicMock()
        raw_mat.name = "Eggs"
        bom_mock = MagicMock()
        bom_mock.product = MagicMock()
        bom_mock.product.name = "Cake"
        item = _make_bom_item(bom_id=uuid.uuid4(), raw_material_id=uuid.uuid4())
        item._state.fields_cache["raw_material"] = raw_mat
        item._state.fields_cache["bom"] = bom_mock
        r = repr(item)
        assert "Eggs" in r
        assert "Cake" in r


class TestBOMItemEffectiveQuantity:
    """Test BOMItem.get_effective_quantity method."""

    def test_no_wastage(self):
        item = _make_bom_item(quantity=Decimal("10.000"), wastage_percent=Decimal("0.00"))
        result = item.get_effective_quantity()
        assert result == Decimal("10.000")

    def test_with_wastage(self):
        item = _make_bom_item(quantity=Decimal("10.000"), wastage_percent=Decimal("10.00"))
        result = item.get_effective_quantity()
        assert result == Decimal("11.0000")

    def test_large_wastage(self):
        item = _make_bom_item(quantity=Decimal("100.000"), wastage_percent=Decimal("50.00"))
        result = item.get_effective_quantity()
        assert result == Decimal("150.0000")


# ═══════════════════════════════════════════════════════════════════════
# Task 86: BOM Database Integration Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBOMCreation:
    """Test BOM creation with real database objects."""

    def test_create_bom(self, tenant_context, category):
        from apps.products.models import Product

        product = Product.objects.create(
            name="Wooden Table",
            category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        bom = BillOfMaterials.objects.create(
            product=product,
            version="1.0",
            yield_quantity=1,
            notes="Standard table recipe",
        )
        assert bom.pk is not None
        assert bom.version == "1.0"
        assert bom.yield_quantity == 1
        assert str(bom) == "Wooden Table BOM v1.0"

    def test_create_bom_item(self, tenant_context, category):
        from apps.products.models import Product

        product = Product.objects.create(
            name="Cake", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        bom = BillOfMaterials.objects.create(product=product)
        flour = Product.objects.create(
            name="Flour", category=category,
            cost_price=Decimal("150.00"),
        )
        item = BOMItem.objects.create(
            bom=bom,
            raw_material=flour,
            quantity=Decimal("2.000"),
            wastage_percent=Decimal("5.00"),
            is_critical=True,
        )
        assert item.pk is not None
        assert item.wastage_percent == Decimal("5.00")
        assert item.is_critical is True

    def test_bom_version_unique_per_product(self, tenant_context, category):
        from django.db import IntegrityError
        from apps.products.models import Product

        product = Product.objects.create(
            name="Unique Test", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        BillOfMaterials.objects.create(product=product, version="1.0")
        with pytest.raises(IntegrityError):
            BillOfMaterials.objects.create(product=product, version="1.0")

    def test_bom_multiple_versions(self, tenant_context, category):
        from apps.products.models import Product

        product = Product.objects.create(
            name="Multi-Version", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        v1 = BillOfMaterials.objects.create(product=product, version="1.0")
        v2 = BillOfMaterials.objects.create(product=product, version="2.0")
        assert v1.pk != v2.pk

    def test_bom_items_cascade_on_bom_delete(self, tenant_context, category):
        from apps.products.models import Product

        product = Product.objects.create(
            name="Cascade BOM", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        bom = BillOfMaterials.objects.create(product=product)
        mat = Product.objects.create(name="Raw Mat", category=category)
        BOMItem.objects.create(bom=bom, raw_material=mat, quantity=Decimal("1.000"))

        count = BOMItem.objects.filter(bom=bom).count()
        assert count == 1

        # Soft-delete via BaseModel
        bom.delete()
        assert bom.is_deleted is True

    def test_bom_manager_active(self, tenant_context, category):
        from apps.products.models import Product

        p = Product.objects.create(
            name="Manager Test", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        active_bom = BillOfMaterials.objects.create(product=p, version="1.0", is_active=True)
        inactive_bom = BillOfMaterials.objects.create(product=p, version="2.0", is_active=False)

        active_pks = list(BillOfMaterials.objects.active().values_list("pk", flat=True))
        assert active_bom.pk in active_pks
        assert inactive_bom.pk not in active_pks

    def test_bom_manager_for_product(self, tenant_context, category):
        from apps.products.models import Product

        p1 = Product.objects.create(
            name="Product One", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        p2 = Product.objects.create(
            name="Product Two", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        b1 = BillOfMaterials.objects.create(product=p1, version="1.0")
        b2 = BillOfMaterials.objects.create(product=p2, version="1.0")

        result_pks = list(
            BillOfMaterials.objects.for_product(p1).values_list("pk", flat=True)
        )
        assert b1.pk in result_pks
        assert b2.pk not in result_pks


# ═══════════════════════════════════════════════════════════════════════
# Task 87: CostCalculationService Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestCostCalculationService:
    """Tests for CostCalculationService with real DB objects."""

    def _create_bom_with_items(self, tenant_context, category):
        """Helper: create a BOM with costed raw materials."""
        from apps.products.models import Product

        product = Product.objects.create(
            name="Custom Cake",
            category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        bom = BillOfMaterials.objects.create(
            product=product,
            version="1.0",
            yield_quantity=10,
        )

        # Material A: Rs. 50/unit × 2 units = Rs. 100
        mat_a = Product.objects.create(
            name="Material A", category=category,
            cost_price=Decimal("50.00"),
        )
        BOMItem.objects.create(
            bom=bom, raw_material=mat_a,
            quantity=Decimal("2.000"), wastage_percent=Decimal("0.00"),
        )

        # Material B: Rs. 30/unit × 3 units = Rs. 90
        mat_b = Product.objects.create(
            name="Material B", category=category,
            cost_price=Decimal("30.00"),
        )
        BOMItem.objects.create(
            bom=bom, raw_material=mat_b,
            quantity=Decimal("3.000"), wastage_percent=Decimal("0.00"),
        )

        # Material C: Rs. 20/unit × 1 unit, 10% wastage = Rs. 22
        mat_c = Product.objects.create(
            name="Material C", category=category,
            cost_price=Decimal("20.00"),
        )
        BOMItem.objects.create(
            bom=bom, raw_material=mat_c,
            quantity=Decimal("1.000"), wastage_percent=Decimal("10.00"),
        )

        return bom

    def test_calculate_material_cost(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(bom)
        # A: 50*2=100, B: 30*3=90, C: 20*1=20 → 210
        assert service.calculate_material_cost() == Decimal("210.000")

    def test_calculate_with_wastage(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(bom)
        # A: 50*2=100, B: 30*3=90, C: 20*1*1.10=22 → 212
        assert service.calculate_with_wastage() == Decimal("212.000")

    def test_calculate_labor_cost(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(bom, labor_cost=Decimal("50.00"))
        assert service.calculate_labor_cost() == Decimal("50.00")

    def test_calculate_labor_cost_default(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(bom)
        assert service.calculate_labor_cost() == Decimal("0.00")

    def test_calculate_overhead_fixed(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(bom, overhead_cost=Decimal("30.00"))
        assert service.calculate_overhead() == Decimal("30.00")

    def test_calculate_overhead_percentage(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(bom, overhead_percent=Decimal("10.00"))
        # 10% of material_with_wastage(212) = 21.20
        assert service.calculate_overhead() == Decimal("21.20")

    def test_calculate_overhead_default(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(bom)
        assert service.calculate_overhead() == Decimal("0.00")

    def test_calculate_total_cost(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(
            bom,
            labor_cost=Decimal("50.00"),
            overhead_percent=Decimal("10.00"),
        )
        # material_w_wastage=212, labor=50, overhead=10% of 212=21.20
        # total = 212 + 50 + 21.20 = 283.20
        assert service.calculate_total_cost() == Decimal("283.200")

    def test_calculate_unit_cost(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(
            bom,
            labor_cost=Decimal("50.00"),
            overhead_percent=Decimal("10.00"),
        )
        # total=283.20, yield=10 → unit_cost=28.32
        assert service.calculate_unit_cost() == Decimal("28.32")

    def test_suggest_selling_price(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(
            bom,
            labor_cost=Decimal("50.00"),
            overhead_percent=Decimal("10.00"),
        )
        result = service.suggest_selling_price(margin_percent=50)
        # unit_cost=28.32, 50% margin → 28.32 * 1.50 = 42.48
        assert result["unit_cost"] == Decimal("28.32")
        assert result["selling_price"] == Decimal("42.48")
        assert result["margin_percent"] == Decimal("50")

    def test_suggest_selling_price_default_margin(self, tenant_context, category):
        from apps.products.services import CostCalculationService

        bom = self._create_bom_with_items(tenant_context, category)
        service = CostCalculationService(bom)
        result = service.suggest_selling_price()
        # default margin = 30%
        assert result["margin_percent"] == Decimal("30")


# ═══════════════════════════════════════════════════════════════════════
# Task 87: ManufacturingStockService Tests
# ═══════════════════════════════════════════════════════════════════════


class TestManufacturingStockService:
    """Tests for ManufacturingStockService using mocks (stock_quantity is not a DB field)."""

    def _make_mock_bom(self, items, yield_quantity=5):
        """Create a mock BOM with items that have stock_quantity on raw_material."""
        bom = MagicMock()
        bom.yield_quantity = yield_quantity

        mock_bom_items = []
        for i in items:
            item = MagicMock()
            item.quantity = Decimal(str(i["qty"]))
            item.wastage_percent = Decimal(str(i.get("wastage", 0)))

            item.raw_material = MagicMock()
            item.raw_material.stock_quantity = i["stock"]
            item.raw_material.cost_price = Decimal(str(i.get("cost", "10.00")))

            item.substitute_id = i.get("substitute_id", None)
            if item.substitute_id:
                item.substitute = MagicMock()
                item.substitute.stock_quantity = i.get("sub_stock", 0)
            else:
                item.substitute = None

            mock_bom_items.append(item)

        mock_qs = MagicMock()
        mock_qs.exists.return_value = len(mock_bom_items) > 0
        mock_qs.__iter__ = lambda self: iter(mock_bom_items)
        mock_qs.select_related.return_value = mock_qs
        mock_qs.all.return_value = mock_qs

        bom.items = MagicMock()
        bom.items.select_related.return_value = mock_qs
        bom.items.all.return_value = mock_qs

        return bom

    # ── Placeholder to mark where old DB code started ──
    # The rest of the helper was removed; tests below use _make_mock_bom.

    def test_check_raw_materials(self):
        from apps.products.services import ManufacturingStockService

        bom = self._make_mock_bom([
            {"qty": 2, "stock": 20, "wastage": 0},
            {"qty": 3, "stock": 10, "wastage": 10},
        ])
        service = ManufacturingStockService(bom)
        results = service.check_raw_materials()
        assert len(results) == 2
        for r in results:
            assert "required" in r
            assert "available" in r
            assert "sufficient" in r

    def test_check_raw_materials_sufficient(self):
        from apps.products.services import ManufacturingStockService

        bom = self._make_mock_bom([
            {"qty": 2, "stock": 20, "wastage": 0},
            {"qty": 3, "stock": 10, "wastage": 10},
        ])
        service = ManufacturingStockService(bom)
        results = service.check_raw_materials()
        # mat_a: need 2, have 20 → sufficient
        # mat_b: need 3.3, have 10 → sufficient
        for r in results:
            assert r["sufficient"] is True

    def test_get_producible_quantity(self):
        from apps.products.services import ManufacturingStockService

        bom = self._make_mock_bom([
            {"qty": 2, "stock": 20, "wastage": 0},
            {"qty": 3, "stock": 10, "wastage": 10},
        ], yield_quantity=5)
        service = ManufacturingStockService(bom)
        qty = service.get_producible_quantity()
        # mat_a: 20/2 = 10 batches, mat_b: 10/3.3 = 3 batches → min = 3
        # yield = 5 → 3 * 5 = 15
        assert qty == 15

    def test_get_producible_quantity_no_items(self):
        from apps.products.services import ManufacturingStockService

        bom = self._make_mock_bom([], yield_quantity=1)
        service = ManufacturingStockService(bom)
        assert service.get_producible_quantity() == 0

    def test_check_raw_materials_with_substitute(self):
        from apps.products.services import ManufacturingStockService

        sub_id = uuid.uuid4()
        bom = self._make_mock_bom([
            {"qty": 5, "stock": 0, "wastage": 0, "substitute_id": sub_id, "sub_stock": 100},
        ], yield_quantity=1)
        service = ManufacturingStockService(bom)
        results = service.check_raw_materials()
        assert len(results) == 1
        assert results[0]["sufficient"] is False
        assert results[0]["substitute_available"] is True


# ═══════════════════════════════════════════════════════════════════════
# Task 88: Tenant Isolation Tests
# ═══════════════════════════════════════════════════════════════════════

# NOTE: Full cross-tenant isolation tests require a second tenant fixture.
# These tests verify that queries are properly scoped within the active
# tenant context. Cross-tenant tests are in test_integration.py.


@pytest.mark.django_db
class TestBundleTenantScoping:
    """Verify bundles and BOMs are scoped within tenant context."""

    def test_bundle_created_in_tenant_context(self, tenant_context, category):
        from apps.products.models import Product
        from apps.products.models.bundle import ProductBundle

        p = Product.objects.create(
            name="Tenant Bundle", category=category,
            product_type=PRODUCT_TYPES.BUNDLE,
        )
        bundle = ProductBundle.objects.create(product=p)
        # Queried within same tenant context — should exist
        assert ProductBundle.objects.filter(pk=bundle.pk).exists()

    def test_bom_created_in_tenant_context(self, tenant_context, category):
        from apps.products.models import Product

        p = Product.objects.create(
            name="Tenant BOM Product", category=category,
            product_type=PRODUCT_TYPES.COMPOSITE,
        )
        bom = BillOfMaterials.objects.create(product=p)
        assert BillOfMaterials.objects.filter(pk=bom.pk).exists()
