"""
Bundle model and service unit tests.

Tests for ProductBundle, BundleItem models, BundleStockService,
and BundlePricingService. All model tests are database-free — they
use mocks and introspection via ``_meta``.
Service tests use the tenant_context fixture with real DB objects.

Covers SP05 Tasks 81-84.
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.db import models

from apps.products.constants import BUNDLE_TYPE, DISCOUNT_TYPE, PRODUCT_TYPES
from apps.products.models import ProductBundle, BundleItem
from apps.products.models.managers import BundleQuerySet, BundleManager


# ═══════════════════════════════════════════════════════════════════════
# Helpers — create model instances without hitting the database
# ═══════════════════════════════════════════════════════════════════════


def _make_product_bundle(**kwargs):
    """Instantiate a ProductBundle via ``__new__`` (no DB)."""
    from django.db.models.base import ModelState

    obj = ProductBundle.__new__(ProductBundle)
    obj._state = ModelState()
    defaults = {
        "id": uuid.uuid4(),
        "product_id": uuid.uuid4(),
        "bundle_type": BUNDLE_TYPE.DYNAMIC,
        "fixed_price": None,
        "discount_type": DISCOUNT_TYPE.NONE,
        "discount_value": Decimal("0.00"),
        "is_active": True,
        "is_deleted": False,
        "created_on": None,
        "updated_on": None,
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_bundle_item(**kwargs):
    """Instantiate a BundleItem via ``__new__`` (no DB)."""
    from django.db.models.base import ModelState

    obj = BundleItem.__new__(BundleItem)
    obj._state = ModelState()
    defaults = {
        "id": uuid.uuid4(),
        "bundle_id": uuid.uuid4(),
        "product_id": uuid.uuid4(),
        "variant_id": None,
        "quantity": 1,
        "is_optional": False,
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
# Task 81 & 82: ProductBundle Model Tests
# ═══════════════════════════════════════════════════════════════════════


class TestProductBundleModelMeta:
    """Verify ProductBundle model field definitions via _meta."""

    def test_db_table(self):
        assert ProductBundle._meta.db_table == "products_bundle"

    def test_verbose_name(self):
        assert str(ProductBundle._meta.verbose_name) == "Product Bundle"

    def test_default_ordering(self):
        assert ProductBundle._meta.ordering == ["-created_on"]

    def test_product_field_one_to_one(self):
        field = ProductBundle._meta.get_field("product")
        assert isinstance(field, models.OneToOneField)
        assert field.remote_field.on_delete == models.PROTECT

    def test_bundle_type_field(self):
        field = ProductBundle._meta.get_field("bundle_type")
        assert isinstance(field, models.CharField)
        assert field.max_length == 20
        assert field.default == BUNDLE_TYPE.DYNAMIC

    def test_fixed_price_field(self):
        field = ProductBundle._meta.get_field("fixed_price")
        assert isinstance(field, models.DecimalField)
        assert field.max_digits == 12
        assert field.decimal_places == 2
        assert field.null is True

    def test_discount_type_field(self):
        field = ProductBundle._meta.get_field("discount_type")
        assert isinstance(field, models.CharField)
        assert field.default == DISCOUNT_TYPE.NONE

    def test_discount_value_field(self):
        field = ProductBundle._meta.get_field("discount_value")
        assert isinstance(field, models.DecimalField)
        assert field.max_digits == 10
        assert field.decimal_places == 2


class TestProductBundleStr:
    """Test ProductBundle __str__ and __repr__."""

    def test_str_with_product(self):
        product = MagicMock()
        product.name = "Gift Hamper"
        bundle = _make_product_bundle()
        bundle._state.fields_cache["product"] = product
        assert str(bundle) == "Bundle: Gift Hamper"

    def test_str_without_product(self):
        bundle = _make_product_bundle(product_id=None)
        # Remove product attribute to simulate unloaded relation
        if hasattr(bundle, "product"):
            delattr(bundle, "product")
        pk = bundle.pk
        assert str(bundle) == f"Bundle(pk={pk})"

    def test_repr(self):
        bundle = _make_product_bundle(bundle_type=BUNDLE_TYPE.FIXED, is_active=True)
        r = repr(bundle)
        assert "ProductBundle" in r
        assert "FIXED" in r or "fixed" in r
        assert "is_active=True" in r


class TestProductBundleTypeChoices:
    """Test BUNDLE_TYPE choices coverage."""

    def test_fixed_type_exists(self):
        assert BUNDLE_TYPE.FIXED == "fixed"

    def test_dynamic_type_exists(self):
        assert BUNDLE_TYPE.DYNAMIC == "dynamic"

    def test_bundle_type_choices_count(self):
        assert len(BUNDLE_TYPE.choices) == 2


class TestDiscountTypeChoices:
    """Test DISCOUNT_TYPE choices coverage."""

    def test_percentage_type(self):
        assert DISCOUNT_TYPE.PERCENTAGE == "percentage"

    def test_fixed_type(self):
        assert DISCOUNT_TYPE.FIXED == "fixed"

    def test_none_type(self):
        assert DISCOUNT_TYPE.NONE == "none"

    def test_discount_type_choices_count(self):
        assert len(DISCOUNT_TYPE.choices) == 3


# ═══════════════════════════════════════════════════════════════════════
# Task 81 & 82: BundleItem Model Tests
# ═══════════════════════════════════════════════════════════════════════


class TestBundleItemModelMeta:
    """Verify BundleItem model field definitions via _meta."""

    def test_db_table(self):
        assert BundleItem._meta.db_table == "products_bundle_item"

    def test_verbose_name(self):
        assert str(BundleItem._meta.verbose_name) == "Bundle Item"

    def test_ordering(self):
        assert BundleItem._meta.ordering == ["sort_order", "product__name"]

    def test_bundle_field_fk(self):
        field = BundleItem._meta.get_field("bundle")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.on_delete == models.CASCADE

    def test_product_field_fk(self):
        field = BundleItem._meta.get_field("product")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.on_delete == models.PROTECT

    def test_variant_field_nullable(self):
        field = BundleItem._meta.get_field("variant")
        assert isinstance(field, models.ForeignKey)
        assert field.null is True
        assert field.blank is True

    def test_quantity_field(self):
        field = BundleItem._meta.get_field("quantity")
        assert isinstance(field, models.PositiveIntegerField)
        assert field.default == 1

    def test_is_optional_field(self):
        field = BundleItem._meta.get_field("is_optional")
        assert isinstance(field, models.BooleanField)
        assert field.default is False

    def test_sort_order_field(self):
        field = BundleItem._meta.get_field("sort_order")
        assert isinstance(field, models.PositiveIntegerField)
        assert field.default == 0

    def test_unique_constraint_exists(self):
        constraint_names = [c.name for c in BundleItem._meta.constraints]
        assert "unique_bundle_product_variant" in constraint_names

    def test_index_exists(self):
        index_names = [i.name for i in BundleItem._meta.indexes]
        assert "idx_bundleitem_bundle_optional" in index_names


class TestBundleItemStr:
    """Test BundleItem __str__ and __repr__."""

    def test_str_without_variant(self):
        product = MagicMock()
        product.name = "Laptop"
        item = _make_bundle_item(quantity=2)
        item._state.fields_cache["product"] = product
        assert str(item) == "Laptop x2"

    def test_str_with_variant(self):
        product = MagicMock()
        product.name = "T-Shirt"
        variant = MagicMock()
        variant.__str__ = lambda self: "Large/Red"
        item = _make_bundle_item(quantity=1, variant_id=uuid.uuid4())
        item._state.fields_cache["product"] = product
        item._state.fields_cache["variant"] = variant
        assert str(item) == "T-Shirt (Large/Red) x1"

    def test_repr(self):
        item = _make_bundle_item()
        r = repr(item)
        assert "BundleItem" in r


# ═══════════════════════════════════════════════════════════════════════
# Task 82: BundleManager Tests (no DB - introspection only)
# ═══════════════════════════════════════════════════════════════════════


class TestBundleManagerSetup:
    """Verify BundleManager is wired correctly."""

    def test_default_manager_is_bundle_manager(self):
        assert isinstance(ProductBundle.objects, BundleManager)

    def test_all_with_deleted_manager_exists(self):
        assert hasattr(ProductBundle, "all_with_deleted")


# ═══════════════════════════════════════════════════════════════════════
# Task 82 & 83: Database Integration Tests (Bundle creation & services)
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestProductBundleCreation:
    """Test bundle creation with real database objects."""

    def test_create_dynamic_bundle(self, tenant_context, category):
        from apps.products.models import Product

        product = Product.objects.create(
            name="Lanka Gift Set",
            category=category,
            product_type=PRODUCT_TYPES.BUNDLE,
            selling_price=Decimal("5000.00"),
        )
        bundle = ProductBundle.objects.create(
            product=product,
            bundle_type=BUNDLE_TYPE.DYNAMIC,
            discount_type=DISCOUNT_TYPE.PERCENTAGE,
            discount_value=Decimal("10.00"),
        )
        assert bundle.pk is not None
        assert bundle.bundle_type == BUNDLE_TYPE.DYNAMIC
        assert bundle.discount_type == DISCOUNT_TYPE.PERCENTAGE
        assert bundle.discount_value == Decimal("10.00")
        assert str(bundle) == "Bundle: Lanka Gift Set"

    def test_create_fixed_bundle(self, tenant_context, category):
        from apps.products.models import Product

        product = Product.objects.create(
            name="Fixed Price Pack",
            category=category,
            product_type=PRODUCT_TYPES.BUNDLE,
        )
        bundle = ProductBundle.objects.create(
            product=product,
            bundle_type=BUNDLE_TYPE.FIXED,
            fixed_price=Decimal("9999.99"),
        )
        assert bundle.bundle_type == BUNDLE_TYPE.FIXED
        assert bundle.fixed_price == Decimal("9999.99")

    def test_create_bundle_item(self, tenant_context, category):
        from apps.products.models import Product

        parent = Product.objects.create(
            name="Office Kit",
            category=category,
            product_type=PRODUCT_TYPES.BUNDLE,
        )
        bundle = ProductBundle.objects.create(product=parent)
        component = Product.objects.create(
            name="Mouse",
            category=category,
            selling_price=Decimal("2500.00"),
        )
        item = BundleItem.objects.create(
            bundle=bundle,
            product=component,
            quantity=1,
            sort_order=0,
        )
        assert item.pk is not None
        assert item.bundle == bundle
        assert item.product == component
        assert item.is_optional is False

    def test_bundle_items_cascade_on_delete(self, tenant_context, category):
        from apps.products.models import Product

        parent = Product.objects.create(
            name="Cascade Test",
            category=category,
            product_type=PRODUCT_TYPES.BUNDLE,
        )
        bundle = ProductBundle.objects.create(product=parent)
        comp = Product.objects.create(name="Item A", category=category)
        BundleItem.objects.create(bundle=bundle, product=comp)
        item_count = BundleItem.objects.filter(bundle=bundle).count()
        assert item_count == 1

        # Soft-delete via BaseModel
        bundle.delete()
        assert bundle.is_deleted is True

    def test_bundle_manager_active(self, tenant_context, category):
        from apps.products.models import Product

        p1 = Product.objects.create(name="Active Bundle P", category=category,
                                    product_type=PRODUCT_TYPES.BUNDLE)
        p2 = Product.objects.create(name="Inactive Bundle P", category=category,
                                    product_type=PRODUCT_TYPES.BUNDLE)

        b1 = ProductBundle.objects.create(product=p1, is_active=True)
        b2 = ProductBundle.objects.create(product=p2, is_active=False)

        active = ProductBundle.objects.active()
        pks = list(active.values_list("pk", flat=True))
        assert b1.pk in pks
        assert b2.pk not in pks


# ═══════════════════════════════════════════════════════════════════════
# Task 83: BundleStockService Tests
# ═══════════════════════════════════════════════════════════════════════


class TestBundleStockService:
    """Tests for BundleStockService using mocks (stock_quantity is not a DB field)."""

    def _make_mock_bundle(self, items):
        """Create a mock bundle with items that have stock_quantity."""
        bundle = MagicMock()
        required = [i for i in items if not i.get("optional", False)]

        # Mock the items queryset for required items
        mock_qs = MagicMock()
        mock_qs.exists.return_value = len(required) > 0

        mock_items = []
        for i in required:
            item = MagicMock()
            item.variant_id = None
            item.product = MagicMock()
            item.product.stock_quantity = i["stock"]
            item.quantity = i["qty"]
            item.is_optional = False
            item.product_id = uuid.uuid4()
            mock_items.append(item)

        mock_qs.__iter__ = lambda self: iter(mock_items)
        mock_qs.filter.return_value = mock_qs

        bundle.items = MagicMock()
        bundle.items.filter.return_value = mock_qs
        # Make the filter return itself for chaining select_related
        mock_qs.select_related.return_value = mock_qs

        return bundle, mock_items

    def test_get_available_stock(self):
        from apps.products.services import BundleStockService

        bundle, _ = self._make_mock_bundle([
            {"stock": 10, "qty": 2},  # 10/2 = 5
            {"stock": 6, "qty": 3},   # 6/3 = 2
        ])
        service = BundleStockService(bundle)
        assert service.get_available_stock() == 2

    def test_check_availability_true(self):
        from apps.products.services import BundleStockService

        bundle, _ = self._make_mock_bundle([
            {"stock": 10, "qty": 2},
            {"stock": 6, "qty": 3},
        ])
        service = BundleStockService(bundle)
        assert service.check_availability(2) is True

    def test_check_availability_false(self):
        from apps.products.services import BundleStockService

        bundle, _ = self._make_mock_bundle([
            {"stock": 10, "qty": 2},
            {"stock": 6, "qty": 3},
        ])
        service = BundleStockService(bundle)
        assert service.check_availability(3) is False

    def test_check_availability_zero_quantity(self):
        from apps.products.services import BundleStockService

        bundle, _ = self._make_mock_bundle([{"stock": 10, "qty": 1}])
        service = BundleStockService(bundle)
        assert service.check_availability(0) is False

    def test_get_limiting_item(self):
        from apps.products.services import BundleStockService

        bundle, mock_items = self._make_mock_bundle([
            {"stock": 10, "qty": 2},  # 5 possible
            {"stock": 6, "qty": 3},   # 2 possible (limiting)
        ])
        service = BundleStockService(bundle)
        limiting = service.get_limiting_item()
        assert limiting is not None
        assert limiting["possible_bundles"] == 2

    def test_no_required_items_returns_zero(self):
        from apps.products.services import BundleStockService

        bundle, _ = self._make_mock_bundle([])
        service = BundleStockService(bundle)
        assert service.get_available_stock() == 0

    def test_reserve_stock_insufficient_raises(self):
        from apps.products.services import BundleStockService

        bundle, _ = self._make_mock_bundle([{"stock": 2, "qty": 3}])
        service = BundleStockService(bundle)
        with pytest.raises(ValueError):
            service.reserve_stock(1)

    def test_reserve_stock_zero_raises(self):
        from apps.products.services import BundleStockService

        bundle, _ = self._make_mock_bundle([{"stock": 10, "qty": 1}])
        service = BundleStockService(bundle)
        with pytest.raises(ValueError):
            service.reserve_stock(0)


# ═══════════════════════════════════════════════════════════════════════
# Task 84: BundlePricingService Tests
# ═══════════════════════════════════════════════════════════════════════


@pytest.mark.django_db
class TestBundlePricingService:
    """Tests for BundlePricingService with real DB objects."""

    def _create_priced_bundle(self, tenant_context, category, **bundle_kwargs):
        """Helper: create a bundle with priced components."""
        from apps.products.models import Product

        parent = Product.objects.create(
            name="Pricing Test Bundle",
            category=category,
            product_type=PRODUCT_TYPES.BUNDLE,
        )
        defaults = {
            "product": parent,
            "bundle_type": BUNDLE_TYPE.DYNAMIC,
            "discount_type": DISCOUNT_TYPE.NONE,
            "discount_value": Decimal("0.00"),
        }
        defaults.update(bundle_kwargs)
        bundle = ProductBundle.objects.create(**defaults)

        # Component A: Rs. 1000 x 2 = 2000
        comp_a = Product.objects.create(
            name="Pricing Comp A",
            category=category,
            selling_price=Decimal("1000.00"),
        )
        BundleItem.objects.create(bundle=bundle, product=comp_a, quantity=2)

        # Component B: Rs. 500 x 1 = 500
        comp_b = Product.objects.create(
            name="Pricing Comp B",
            category=category,
            selling_price=Decimal("500.00"),
        )
        BundleItem.objects.create(bundle=bundle, product=comp_b, quantity=1)

        return bundle  # total component price = 2500.00

    def test_dynamic_price_no_discount(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(tenant_context, category)
        service = BundlePricingService(bundle)
        assert service.calculate_dynamic_price() == Decimal("2500.00")

    def test_dynamic_price_percentage_discount(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(
            tenant_context,
            category,
            discount_type=DISCOUNT_TYPE.PERCENTAGE,
            discount_value=Decimal("10.00"),
        )
        service = BundlePricingService(bundle)
        # 2500 - 10% = 2500 - 250 = 2250
        assert service.calculate_dynamic_price() == Decimal("2250.00")

    def test_dynamic_price_fixed_discount(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(
            tenant_context,
            category,
            discount_type=DISCOUNT_TYPE.FIXED,
            discount_value=Decimal("300.00"),
        )
        service = BundlePricingService(bundle)
        # 2500 - 300 = 2200
        assert service.calculate_dynamic_price() == Decimal("2200.00")

    def test_fixed_price_bundle(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(
            tenant_context,
            category,
            bundle_type=BUNDLE_TYPE.FIXED,
            fixed_price=Decimal("2000.00"),
        )
        service = BundlePricingService(bundle)
        assert service.get_bundle_price() == Decimal("2000.00")

    def test_get_bundle_price_dynamic(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(tenant_context, category)
        service = BundlePricingService(bundle)
        assert service.get_bundle_price() == Decimal("2500.00")

    def test_get_individual_total(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(
            tenant_context,
            category,
            discount_type=DISCOUNT_TYPE.PERCENTAGE,
            discount_value=Decimal("20.00"),
        )
        service = BundlePricingService(bundle)
        # individual total ignores discount
        assert service.get_individual_total() == Decimal("2500.00")

    def test_get_savings_with_discount(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(
            tenant_context,
            category,
            discount_type=DISCOUNT_TYPE.FIXED,
            discount_value=Decimal("500.00"),
        )
        service = BundlePricingService(bundle)
        # individual=2500, bundle_price=2000, savings=500
        assert service.get_savings() == Decimal("500.00")

    def test_get_savings_fixed_price(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(
            tenant_context,
            category,
            bundle_type=BUNDLE_TYPE.FIXED,
            fixed_price=Decimal("1800.00"),
        )
        service = BundlePricingService(bundle)
        # individual=2500, fixed_price=1800, savings=700
        assert service.get_savings() == Decimal("700.00")

    def test_calculate_fixed_price_none(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(
            tenant_context, category, bundle_type=BUNDLE_TYPE.DYNAMIC
        )
        service = BundlePricingService(bundle)
        assert service.calculate_fixed_price() == Decimal("0.00")

    def test_discount_never_below_zero(self, tenant_context, category):
        from apps.products.services import BundlePricingService

        bundle = self._create_priced_bundle(
            tenant_context,
            category,
            discount_type=DISCOUNT_TYPE.FIXED,
            discount_value=Decimal("99999.00"),
        )
        service = BundlePricingService(bundle)
        assert service.calculate_dynamic_price() == Decimal("0.00")
