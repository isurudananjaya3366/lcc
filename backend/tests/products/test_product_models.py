"""
Product-related model unit tests.

Tests for Brand, TaxClass, UnitOfMeasure, and Product models.
All tests are database-free — they use mocks and introspection via
``_meta`` so they can run without a tenant database context.
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, PropertyMock, patch, call

import pytest
from django.db import models
from django.utils.text import slugify

from apps.products.models import Brand, TaxClass, UnitOfMeasure, Product
from apps.products.models.managers import ProductQuerySet, ProductManager
from apps.products.constants import PRODUCT_TYPES, PRODUCT_STATUS


# ═══════════════════════════════════════════════════════════════════════
# Helpers — create model instances without hitting the database
# ═══════════════════════════════════════════════════════════════════════


def _make_brand(**kwargs):
    """Instantiate a Brand via ``__new__`` (no DB) and set attributes."""
    obj = Brand.__new__(Brand)
    defaults = {
        "id": uuid.uuid4(),
        "name": "Test Brand",
        "slug": "test-brand",
        "logo": None,
        "description": "",
        "website": "",
        "is_active": True,
        "is_deleted": False,
        "created_on": None,
        "updated_on": None,
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_tax_class(**kwargs):
    """Instantiate a TaxClass via ``__new__`` (no DB) and set attributes."""
    obj = TaxClass.__new__(TaxClass)
    defaults = {
        "id": uuid.uuid4(),
        "name": "Standard VAT",
        "rate": Decimal("15.00"),
        "description": "",
        "is_default": False,
        "is_active": True,
        "is_deleted": False,
        "created_on": None,
        "updated_on": None,
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_uom(**kwargs):
    """Instantiate a UnitOfMeasure via ``__new__`` (no DB) and set attributes."""
    obj = UnitOfMeasure.__new__(UnitOfMeasure)
    defaults = {
        "id": uuid.uuid4(),
        "name": "Piece",
        "symbol": "pcs",
        "description": "",
        "conversion_factor": Decimal("1.0000"),
        "is_base_unit": True,
        "is_active": True,
        "is_deleted": False,
        "created_on": None,
        "updated_on": None,
    }
    defaults.update(kwargs)
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


def _make_product(**kwargs):
    """Instantiate a Product via ``__new__`` (no DB) and set attributes."""
    from django.db.models.base import ModelState

    obj = Product.__new__(Product)
    obj._state = ModelState()
    defaults = {
        "id": uuid.uuid4(),
        "name": "Test Product",
        "slug": "test-product",
        "sku": "PRD-TEST-00001",
        "barcode": "",
        "description": "",
        "short_description": "",
        "category_id": uuid.uuid4(),
        "brand_id": None,
        "product_type": PRODUCT_TYPES.SIMPLE,
        "status": PRODUCT_STATUS.DRAFT,
        "is_webstore_visible": True,
        "is_pos_visible": True,
        "featured": False,
        "tax_class_id": None,
        "unit_of_measure_id": None,
        "cost_price": Decimal("0.00"),
        "selling_price": Decimal("0.00"),
        "mrp": None,
        "wholesale_price": None,
        "weight": None,
        "length": None,
        "width": None,
        "height": None,
        "seo_title": "",
        "seo_description": "",
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
# 1. Brand Model Meta Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestBrandModelMeta:
    """Test Brand model Meta class configuration."""

    def test_app_label(self):
        assert Brand._meta.app_label == "products"

    def test_db_table(self):
        assert Brand._meta.db_table == "products_brand"

    def test_verbose_name(self):
        assert Brand._meta.verbose_name == "Brand"

    def test_verbose_name_plural(self):
        assert Brand._meta.verbose_name_plural == "Brands"

    def test_ordering(self):
        assert list(Brand._meta.ordering) == ["name"]

    def test_indexes_count(self):
        assert len(Brand._meta.indexes) >= 2

    def test_index_slug_exists(self):
        names = [idx.name for idx in Brand._meta.indexes]
        field_lists = [idx.fields for idx in Brand._meta.indexes]
        assert any("slug" in fields for fields in field_lists)

    def test_index_is_active_exists(self):
        field_lists = [idx.fields for idx in Brand._meta.indexes]
        assert any("is_active" in fields for fields in field_lists)


# ═══════════════════════════════════════════════════════════════════════
# 2. Brand Model Fields
# ═══════════════════════════════════════════════════════════════════════


class TestBrandModelFields:
    """Test every Brand field's type, constraints, and parameters."""

    # ── name ────────────────────────────────────────────────────────

    def test_name_field_type(self):
        field = Brand._meta.get_field("name")
        assert isinstance(field, models.CharField)

    def test_name_max_length(self):
        field = Brand._meta.get_field("name")
        assert field.max_length == 100

    def test_name_is_indexed(self):
        field = Brand._meta.get_field("name")
        assert field.db_index is True

    # ── slug ────────────────────────────────────────────────────────

    def test_slug_field_type(self):
        field = Brand._meta.get_field("slug")
        assert isinstance(field, models.SlugField)

    def test_slug_max_length(self):
        field = Brand._meta.get_field("slug")
        assert field.max_length == 100

    def test_slug_unique(self):
        field = Brand._meta.get_field("slug")
        assert field.unique is True

    def test_slug_blank(self):
        field = Brand._meta.get_field("slug")
        assert field.blank is True

    # ── logo ────────────────────────────────────────────────────────

    def test_logo_field_type(self):
        field = Brand._meta.get_field("logo")
        assert isinstance(field, models.ImageField)

    def test_logo_nullable(self):
        field = Brand._meta.get_field("logo")
        assert field.null is True

    def test_logo_blank(self):
        field = Brand._meta.get_field("logo")
        assert field.blank is True

    def test_logo_upload_to(self):
        field = Brand._meta.get_field("logo")
        assert field.upload_to == "brands/logos/"

    # ── description ─────────────────────────────────────────────────

    def test_description_field_type(self):
        field = Brand._meta.get_field("description")
        assert isinstance(field, models.TextField)

    def test_description_blank(self):
        field = Brand._meta.get_field("description")
        assert field.blank is True

    def test_description_default(self):
        field = Brand._meta.get_field("description")
        assert field.default == ""

    # ── website ─────────────────────────────────────────────────────

    def test_website_field_type(self):
        field = Brand._meta.get_field("website")
        assert isinstance(field, models.URLField)

    def test_website_max_length(self):
        field = Brand._meta.get_field("website")
        assert field.max_length == 200

    def test_website_blank(self):
        field = Brand._meta.get_field("website")
        assert field.blank is True

    def test_website_default(self):
        field = Brand._meta.get_field("website")
        assert field.default == ""


# ═══════════════════════════════════════════════════════════════════════
# 3. Brand String Representation
# ═══════════════════════════════════════════════════════════════════════


class TestBrandStringRepresentation:
    """Test the ``__str__`` method for Brand."""

    def test_str_returns_name(self):
        brand = _make_brand(name="Samsung")
        assert str(brand) == "Samsung"

    def test_str_with_long_name(self):
        long_name = "B" * 100
        brand = _make_brand(name=long_name)
        assert str(brand) == long_name

    def test_str_with_unicode_name(self):
        brand = _make_brand(name="සැම්සුන්ග්")
        assert str(brand) == "සැම්සුන්ග්"

    def test_str_with_special_characters(self):
        brand = _make_brand(name="Procter & Gamble (P&G)")
        assert str(brand) == "Procter & Gamble (P&G)"


# ═══════════════════════════════════════════════════════════════════════
# 4. Brand Slug Generation
# ═══════════════════════════════════════════════════════════════════════


class TestBrandSlugGeneration:
    """Test slug auto-generation in ``save()``."""

    @patch.object(Brand, "save", autospec=True)
    def test_save_generates_slug_when_empty(self, mock_super_save):
        brand = _make_brand(name="My Brand", slug="")
        if not brand.slug:
            brand.slug = slugify(brand.name)
        assert brand.slug == "my-brand"

    def test_slug_preserves_manual_value(self):
        brand = _make_brand(name="Test", slug="custom-slug")
        if not brand.slug:
            brand.slug = slugify(brand.name)
        assert brand.slug == "custom-slug"

    def test_slugify_lowercases(self):
        assert slugify("My Brand") == "my-brand"

    def test_slugify_replaces_spaces_with_hyphens(self):
        assert slugify("Some New Brand") == "some-new-brand"

    def test_slugify_strips_special_characters(self):
        assert slugify("Brands & More!") == "brands-more"


# ═══════════════════════════════════════════════════════════════════════
# 5. TaxClass Model Meta Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestTaxClassModelMeta:
    """Test TaxClass model Meta class configuration."""

    def test_app_label(self):
        assert TaxClass._meta.app_label == "products"

    def test_db_table(self):
        assert TaxClass._meta.db_table == "products_tax_class"

    def test_verbose_name(self):
        assert TaxClass._meta.verbose_name == "Tax Class"

    def test_verbose_name_plural(self):
        assert TaxClass._meta.verbose_name_plural == "Tax Classes"

    def test_ordering(self):
        assert list(TaxClass._meta.ordering) == ["name"]

    def test_indexes_count(self):
        assert len(TaxClass._meta.indexes) >= 1

    def test_index_is_default_exists(self):
        field_lists = [idx.fields for idx in TaxClass._meta.indexes]
        assert any("is_default" in fields for fields in field_lists)


# ═══════════════════════════════════════════════════════════════════════
# 6. TaxClass Model Fields
# ═══════════════════════════════════════════════════════════════════════


class TestTaxClassModelFields:
    """Test every TaxClass field's type, constraints, and parameters."""

    # ── name ────────────────────────────────────────────────────────

    def test_name_field_type(self):
        field = TaxClass._meta.get_field("name")
        assert isinstance(field, models.CharField)

    def test_name_max_length(self):
        field = TaxClass._meta.get_field("name")
        assert field.max_length == 50

    # ── rate ────────────────────────────────────────────────────────

    def test_rate_field_type(self):
        field = TaxClass._meta.get_field("rate")
        assert isinstance(field, models.DecimalField)

    def test_rate_max_digits(self):
        field = TaxClass._meta.get_field("rate")
        assert field.max_digits == 5

    def test_rate_decimal_places(self):
        field = TaxClass._meta.get_field("rate")
        assert field.decimal_places == 2

    def test_rate_default(self):
        field = TaxClass._meta.get_field("rate")
        assert field.default == Decimal("0.00")

    def test_rate_has_validators(self):
        field = TaxClass._meta.get_field("rate")
        assert len(field.validators) >= 2

    def test_rate_min_validator(self):
        from django.core.validators import MinValueValidator

        field = TaxClass._meta.get_field("rate")
        min_validators = [
            v for v in field.validators if isinstance(v, MinValueValidator)
        ]
        assert len(min_validators) >= 1
        assert min_validators[0].limit_value == Decimal("0")

    def test_rate_max_validator(self):
        from django.core.validators import MaxValueValidator

        field = TaxClass._meta.get_field("rate")
        max_validators = [
            v for v in field.validators if isinstance(v, MaxValueValidator)
        ]
        assert len(max_validators) >= 1
        assert max_validators[0].limit_value == Decimal("100")

    # ── description ─────────────────────────────────────────────────

    def test_description_field_type(self):
        field = TaxClass._meta.get_field("description")
        assert isinstance(field, models.TextField)

    def test_description_blank(self):
        field = TaxClass._meta.get_field("description")
        assert field.blank is True

    def test_description_default(self):
        field = TaxClass._meta.get_field("description")
        assert field.default == ""

    # ── is_default ──────────────────────────────────────────────────

    def test_is_default_field_type(self):
        field = TaxClass._meta.get_field("is_default")
        assert isinstance(field, models.BooleanField)

    def test_is_default_default_false(self):
        field = TaxClass._meta.get_field("is_default")
        assert field.default is False


# ═══════════════════════════════════════════════════════════════════════
# 7. TaxClass String Representation
# ═══════════════════════════════════════════════════════════════════════


class TestTaxClassStringRepresentation:
    """Test the ``__str__`` method for TaxClass."""

    def test_str_format(self):
        tc = _make_tax_class(name="Standard VAT", rate=Decimal("15.00"))
        assert str(tc) == "Standard VAT (15.00%)"

    def test_str_zero_rate(self):
        tc = _make_tax_class(name="Zero-rated", rate=Decimal("0.00"))
        assert str(tc) == "Zero-rated (0.00%)"

    def test_str_with_decimal_rate(self):
        tc = _make_tax_class(name="Reduced", rate=Decimal("8.50"))
        assert str(tc) == "Reduced (8.50%)"


# ═══════════════════════════════════════════════════════════════════════
# 8. TaxClass Default Logic
# ═══════════════════════════════════════════════════════════════════════


class TestTaxClassDefaultLogic:
    """Test single-default-per-tenant logic in save() via mock."""

    @patch("apps.products.models.tax_class.TaxClass.objects")
    def test_save_unsets_other_defaults_when_is_default_true(self, mock_objects):
        tc = _make_tax_class(is_default=True)
        mock_qs = MagicMock()
        mock_objects.filter.return_value = mock_qs
        mock_qs.exclude.return_value = mock_qs

        with patch.object(models.Model, "save"):
            TaxClass.save(tc)

        mock_objects.filter.assert_called_once_with(is_default=True)
        mock_qs.exclude.assert_called_once_with(pk=tc.pk)
        mock_qs.update.assert_called_once_with(is_default=False)

    @patch("apps.products.models.tax_class.TaxClass.objects")
    def test_save_does_not_unset_when_is_default_false(self, mock_objects):
        tc = _make_tax_class(is_default=False)

        with patch.object(models.Model, "save"):
            TaxClass.save(tc)

        mock_objects.filter.assert_not_called()


# ═══════════════════════════════════════════════════════════════════════
# 9. UnitOfMeasure Model Meta Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestUnitOfMeasureModelMeta:
    """Test UnitOfMeasure model Meta class configuration."""

    def test_app_label(self):
        assert UnitOfMeasure._meta.app_label == "products"

    def test_db_table(self):
        assert UnitOfMeasure._meta.db_table == "products_unit_of_measure"

    def test_verbose_name(self):
        assert UnitOfMeasure._meta.verbose_name == "Unit of Measure"

    def test_verbose_name_plural(self):
        assert UnitOfMeasure._meta.verbose_name_plural == "Units of Measure"

    def test_ordering(self):
        assert list(UnitOfMeasure._meta.ordering) == ["name"]

    def test_indexes_count(self):
        assert len(UnitOfMeasure._meta.indexes) >= 3

    def test_index_symbol_exists(self):
        field_lists = [idx.fields for idx in UnitOfMeasure._meta.indexes]
        assert any("symbol" in fields for fields in field_lists)

    def test_index_is_active_exists(self):
        field_lists = [idx.fields for idx in UnitOfMeasure._meta.indexes]
        assert any("is_active" in fields for fields in field_lists)

    def test_index_is_base_unit_exists(self):
        field_lists = [idx.fields for idx in UnitOfMeasure._meta.indexes]
        assert any("is_base_unit" in fields for fields in field_lists)


# ═══════════════════════════════════════════════════════════════════════
# 10. UnitOfMeasure Model Fields
# ═══════════════════════════════════════════════════════════════════════


class TestUnitOfMeasureModelFields:
    """Test every UnitOfMeasure field's type, constraints, and parameters."""

    # ── name ────────────────────────────────────────────────────────

    def test_name_field_type(self):
        field = UnitOfMeasure._meta.get_field("name")
        assert isinstance(field, models.CharField)

    def test_name_max_length(self):
        field = UnitOfMeasure._meta.get_field("name")
        assert field.max_length == 50

    # ── symbol ──────────────────────────────────────────────────────

    def test_symbol_field_type(self):
        field = UnitOfMeasure._meta.get_field("symbol")
        assert isinstance(field, models.CharField)

    def test_symbol_max_length(self):
        field = UnitOfMeasure._meta.get_field("symbol")
        assert field.max_length == 10

    # ── description ─────────────────────────────────────────────────

    def test_description_field_type(self):
        field = UnitOfMeasure._meta.get_field("description")
        assert isinstance(field, models.TextField)

    def test_description_blank(self):
        field = UnitOfMeasure._meta.get_field("description")
        assert field.blank is True

    def test_description_default(self):
        field = UnitOfMeasure._meta.get_field("description")
        assert field.default == ""

    # ── conversion_factor ───────────────────────────────────────────

    def test_conversion_factor_field_type(self):
        field = UnitOfMeasure._meta.get_field("conversion_factor")
        assert isinstance(field, models.DecimalField)

    def test_conversion_factor_max_digits(self):
        field = UnitOfMeasure._meta.get_field("conversion_factor")
        assert field.max_digits == 10

    def test_conversion_factor_decimal_places(self):
        field = UnitOfMeasure._meta.get_field("conversion_factor")
        assert field.decimal_places == 4

    def test_conversion_factor_nullable(self):
        field = UnitOfMeasure._meta.get_field("conversion_factor")
        assert field.null is True

    def test_conversion_factor_blank(self):
        field = UnitOfMeasure._meta.get_field("conversion_factor")
        assert field.blank is True

    # ── is_base_unit ────────────────────────────────────────────────

    def test_is_base_unit_field_type(self):
        field = UnitOfMeasure._meta.get_field("is_base_unit")
        assert isinstance(field, models.BooleanField)

    def test_is_base_unit_default_false(self):
        field = UnitOfMeasure._meta.get_field("is_base_unit")
        assert field.default is False


# ═══════════════════════════════════════════════════════════════════════
# 11. UnitOfMeasure String Representation
# ═══════════════════════════════════════════════════════════════════════


class TestUnitOfMeasureStringRepresentation:
    """Test the ``__str__`` method for UnitOfMeasure."""

    def test_str_format(self):
        uom = _make_uom(name="Kilogram", symbol="kg")
        assert str(uom) == "Kilogram (kg)"

    def test_str_with_piece(self):
        uom = _make_uom(name="Piece", symbol="pcs")
        assert str(uom) == "Piece (pcs)"

    def test_str_with_liter(self):
        uom = _make_uom(name="Liter", symbol="l")
        assert str(uom) == "Liter (l)"


# ═══════════════════════════════════════════════════════════════════════
# 12. Product Model Meta Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestProductModelMeta:
    """Test Product model Meta class configuration."""

    def test_app_label(self):
        assert Product._meta.app_label == "products"

    def test_db_table(self):
        assert Product._meta.db_table == "products_product"

    def test_verbose_name(self):
        assert Product._meta.verbose_name == "Product"

    def test_verbose_name_plural(self):
        assert Product._meta.verbose_name_plural == "Products"

    def test_ordering(self):
        assert list(Product._meta.ordering) == ["-created_on", "name"]

    def test_indexes_count(self):
        assert len(Product._meta.indexes) >= 5

    def test_index_status_created_exists(self):
        names = [idx.name for idx in Product._meta.indexes]
        assert "product_status_created" in names

    def test_index_category_status_exists(self):
        names = [idx.name for idx in Product._meta.indexes]
        assert "product_category_status" in names

    def test_index_sku_exists(self):
        names = [idx.name for idx in Product._meta.indexes]
        assert "product_sku" in names

    def test_index_product_type_exists(self):
        names = [idx.name for idx in Product._meta.indexes]
        assert "product_type_idx" in names

    def test_index_featured_exists(self):
        names = [idx.name for idx in Product._meta.indexes]
        assert "product_featured_idx" in names


# ═══════════════════════════════════════════════════════════════════════
# 13. Product Model Fields
# ═══════════════════════════════════════════════════════════════════════


class TestProductModelFields:
    """Test every Product field's type, constraints, and parameters."""

    # ── name ────────────────────────────────────────────────────────

    def test_name_field_type(self):
        field = Product._meta.get_field("name")
        assert isinstance(field, models.CharField)

    def test_name_max_length(self):
        field = Product._meta.get_field("name")
        assert field.max_length == 200

    def test_name_is_indexed(self):
        field = Product._meta.get_field("name")
        assert field.db_index is True

    # ── slug ────────────────────────────────────────────────────────

    def test_slug_field_type(self):
        field = Product._meta.get_field("slug")
        assert isinstance(field, models.SlugField)

    def test_slug_max_length(self):
        field = Product._meta.get_field("slug")
        assert field.max_length == 200

    def test_slug_unique(self):
        field = Product._meta.get_field("slug")
        assert field.unique is True

    def test_slug_blank(self):
        field = Product._meta.get_field("slug")
        assert field.blank is True

    # ── sku ─────────────────────────────────────────────────────────

    def test_sku_field_type(self):
        field = Product._meta.get_field("sku")
        assert isinstance(field, models.CharField)

    def test_sku_max_length(self):
        field = Product._meta.get_field("sku")
        assert field.max_length == 50

    def test_sku_unique(self):
        field = Product._meta.get_field("sku")
        assert field.unique is True

    def test_sku_blank(self):
        field = Product._meta.get_field("sku")
        assert field.blank is True

    def test_sku_is_indexed(self):
        field = Product._meta.get_field("sku")
        assert field.db_index is True

    # ── barcode ─────────────────────────────────────────────────────

    def test_barcode_field_type(self):
        field = Product._meta.get_field("barcode")
        assert isinstance(field, models.CharField)

    def test_barcode_max_length(self):
        field = Product._meta.get_field("barcode")
        assert field.max_length == 50

    def test_barcode_blank(self):
        field = Product._meta.get_field("barcode")
        assert field.blank is True

    def test_barcode_default(self):
        field = Product._meta.get_field("barcode")
        assert field.default == ""

    def test_barcode_is_indexed(self):
        field = Product._meta.get_field("barcode")
        assert field.db_index is True

    # ── description ─────────────────────────────────────────────────

    def test_description_field_type(self):
        field = Product._meta.get_field("description")
        assert isinstance(field, models.TextField)

    def test_description_blank(self):
        field = Product._meta.get_field("description")
        assert field.blank is True

    def test_description_default(self):
        field = Product._meta.get_field("description")
        assert field.default == ""

    # ── short_description ───────────────────────────────────────────

    def test_short_description_field_type(self):
        field = Product._meta.get_field("short_description")
        assert isinstance(field, models.CharField)

    def test_short_description_max_length(self):
        field = Product._meta.get_field("short_description")
        assert field.max_length == 500

    def test_short_description_blank(self):
        field = Product._meta.get_field("short_description")
        assert field.blank is True

    def test_short_description_default(self):
        field = Product._meta.get_field("short_description")
        assert field.default == ""

    # ── category (ForeignKey) ───────────────────────────────────────

    def test_category_field_type(self):
        field = Product._meta.get_field("category")
        assert isinstance(field, models.ForeignKey)

    def test_category_on_delete_protect(self):
        field = Product._meta.get_field("category")
        assert field.remote_field.on_delete is models.PROTECT

    def test_category_related_name(self):
        field = Product._meta.get_field("category")
        assert field.remote_field.related_name == "products"

    def test_category_not_nullable(self):
        field = Product._meta.get_field("category")
        assert field.null is False

    # ── brand (ForeignKey) ──────────────────────────────────────────

    def test_brand_field_type(self):
        field = Product._meta.get_field("brand")
        assert isinstance(field, models.ForeignKey)

    def test_brand_on_delete_set_null(self):
        field = Product._meta.get_field("brand")
        assert field.remote_field.on_delete is models.SET_NULL

    def test_brand_nullable(self):
        field = Product._meta.get_field("brand")
        assert field.null is True

    def test_brand_blank(self):
        field = Product._meta.get_field("brand")
        assert field.blank is True

    def test_brand_related_name(self):
        field = Product._meta.get_field("brand")
        assert field.remote_field.related_name == "products"

    # ── product_type ────────────────────────────────────────────────

    def test_product_type_field_type(self):
        field = Product._meta.get_field("product_type")
        assert isinstance(field, models.CharField)

    def test_product_type_max_length(self):
        field = Product._meta.get_field("product_type")
        assert field.max_length == 20

    def test_product_type_choices(self):
        field = Product._meta.get_field("product_type")
        assert field.choices == PRODUCT_TYPES.choices

    def test_product_type_default(self):
        field = Product._meta.get_field("product_type")
        assert field.default == PRODUCT_TYPES.SIMPLE

    # ── status ──────────────────────────────────────────────────────

    def test_status_field_type(self):
        field = Product._meta.get_field("status")
        assert isinstance(field, models.CharField)

    def test_status_max_length(self):
        field = Product._meta.get_field("status")
        assert field.max_length == 20

    def test_status_choices(self):
        field = Product._meta.get_field("status")
        assert field.choices == PRODUCT_STATUS.choices

    def test_status_default(self):
        field = Product._meta.get_field("status")
        assert field.default == PRODUCT_STATUS.DRAFT

    def test_status_is_indexed(self):
        field = Product._meta.get_field("status")
        assert field.db_index is True

    # ── is_webstore_visible ─────────────────────────────────────────

    def test_is_webstore_visible_field_type(self):
        field = Product._meta.get_field("is_webstore_visible")
        assert isinstance(field, models.BooleanField)

    def test_is_webstore_visible_default_true(self):
        field = Product._meta.get_field("is_webstore_visible")
        assert field.default is True

    # ── is_pos_visible ──────────────────────────────────────────────

    def test_is_pos_visible_field_type(self):
        field = Product._meta.get_field("is_pos_visible")
        assert isinstance(field, models.BooleanField)

    def test_is_pos_visible_default_true(self):
        field = Product._meta.get_field("is_pos_visible")
        assert field.default is True

    # ── featured ────────────────────────────────────────────────────

    def test_featured_field_type(self):
        field = Product._meta.get_field("featured")
        assert isinstance(field, models.BooleanField)

    def test_featured_default_false(self):
        field = Product._meta.get_field("featured")
        assert field.default is False

    def test_featured_is_indexed(self):
        field = Product._meta.get_field("featured")
        assert field.db_index is True

    # ── tax_class (ForeignKey) ──────────────────────────────────────

    def test_tax_class_field_type(self):
        field = Product._meta.get_field("tax_class")
        assert isinstance(field, models.ForeignKey)

    def test_tax_class_on_delete_set_null(self):
        field = Product._meta.get_field("tax_class")
        assert field.remote_field.on_delete is models.SET_NULL

    def test_tax_class_nullable(self):
        field = Product._meta.get_field("tax_class")
        assert field.null is True

    def test_tax_class_blank(self):
        field = Product._meta.get_field("tax_class")
        assert field.blank is True

    def test_tax_class_related_name(self):
        field = Product._meta.get_field("tax_class")
        assert field.remote_field.related_name == "products"

    # ── unit_of_measure (ForeignKey) ────────────────────────────────

    def test_unit_of_measure_field_type(self):
        field = Product._meta.get_field("unit_of_measure")
        assert isinstance(field, models.ForeignKey)

    def test_unit_of_measure_on_delete_set_null(self):
        field = Product._meta.get_field("unit_of_measure")
        assert field.remote_field.on_delete is models.SET_NULL

    def test_unit_of_measure_nullable(self):
        field = Product._meta.get_field("unit_of_measure")
        assert field.null is True

    def test_unit_of_measure_blank(self):
        field = Product._meta.get_field("unit_of_measure")
        assert field.blank is True

    def test_unit_of_measure_related_name(self):
        field = Product._meta.get_field("unit_of_measure")
        assert field.remote_field.related_name == "products"

    # ── cost_price ──────────────────────────────────────────────────

    def test_cost_price_field_type(self):
        field = Product._meta.get_field("cost_price")
        assert isinstance(field, models.DecimalField)

    def test_cost_price_max_digits(self):
        field = Product._meta.get_field("cost_price")
        assert field.max_digits == 10

    def test_cost_price_decimal_places(self):
        field = Product._meta.get_field("cost_price")
        assert field.decimal_places == 2

    def test_cost_price_default(self):
        field = Product._meta.get_field("cost_price")
        assert field.default == 0

    # ── selling_price ───────────────────────────────────────────────

    def test_selling_price_field_type(self):
        field = Product._meta.get_field("selling_price")
        assert isinstance(field, models.DecimalField)

    def test_selling_price_max_digits(self):
        field = Product._meta.get_field("selling_price")
        assert field.max_digits == 10

    def test_selling_price_decimal_places(self):
        field = Product._meta.get_field("selling_price")
        assert field.decimal_places == 2

    def test_selling_price_default(self):
        field = Product._meta.get_field("selling_price")
        assert field.default == 0

    # ── mrp ─────────────────────────────────────────────────────────

    def test_mrp_field_type(self):
        field = Product._meta.get_field("mrp")
        assert isinstance(field, models.DecimalField)

    def test_mrp_nullable(self):
        field = Product._meta.get_field("mrp")
        assert field.null is True

    def test_mrp_blank(self):
        field = Product._meta.get_field("mrp")
        assert field.blank is True

    # ── wholesale_price ─────────────────────────────────────────────

    def test_wholesale_price_field_type(self):
        field = Product._meta.get_field("wholesale_price")
        assert isinstance(field, models.DecimalField)

    def test_wholesale_price_nullable(self):
        field = Product._meta.get_field("wholesale_price")
        assert field.null is True

    def test_wholesale_price_blank(self):
        field = Product._meta.get_field("wholesale_price")
        assert field.blank is True

    # ── weight ──────────────────────────────────────────────────────

    def test_weight_field_type(self):
        field = Product._meta.get_field("weight")
        assert isinstance(field, models.DecimalField)

    def test_weight_nullable(self):
        field = Product._meta.get_field("weight")
        assert field.null is True

    def test_weight_blank(self):
        field = Product._meta.get_field("weight")
        assert field.blank is True

    def test_weight_max_digits(self):
        field = Product._meta.get_field("weight")
        assert field.max_digits == 10

    def test_weight_decimal_places(self):
        field = Product._meta.get_field("weight")
        assert field.decimal_places == 3

    # ── length ──────────────────────────────────────────────────────

    def test_length_field_type(self):
        field = Product._meta.get_field("length")
        assert isinstance(field, models.DecimalField)

    def test_length_nullable(self):
        field = Product._meta.get_field("length")
        assert field.null is True

    def test_length_blank(self):
        field = Product._meta.get_field("length")
        assert field.blank is True

    # ── width ───────────────────────────────────────────────────────

    def test_width_field_type(self):
        field = Product._meta.get_field("width")
        assert isinstance(field, models.DecimalField)

    def test_width_nullable(self):
        field = Product._meta.get_field("width")
        assert field.null is True

    def test_width_blank(self):
        field = Product._meta.get_field("width")
        assert field.blank is True

    # ── height ──────────────────────────────────────────────────────

    def test_height_field_type(self):
        field = Product._meta.get_field("height")
        assert isinstance(field, models.DecimalField)

    def test_height_nullable(self):
        field = Product._meta.get_field("height")
        assert field.null is True

    def test_height_blank(self):
        field = Product._meta.get_field("height")
        assert field.blank is True

    # ── seo_title ───────────────────────────────────────────────────

    def test_seo_title_field_type(self):
        field = Product._meta.get_field("seo_title")
        assert isinstance(field, models.CharField)

    def test_seo_title_max_length(self):
        field = Product._meta.get_field("seo_title")
        assert field.max_length == 100

    def test_seo_title_blank(self):
        field = Product._meta.get_field("seo_title")
        assert field.blank is True

    def test_seo_title_default(self):
        field = Product._meta.get_field("seo_title")
        assert field.default == ""

    # ── seo_description ─────────────────────────────────────────────

    def test_seo_description_field_type(self):
        field = Product._meta.get_field("seo_description")
        assert isinstance(field, models.CharField)

    def test_seo_description_max_length(self):
        field = Product._meta.get_field("seo_description")
        assert field.max_length == 300

    def test_seo_description_blank(self):
        field = Product._meta.get_field("seo_description")
        assert field.blank is True

    def test_seo_description_default(self):
        field = Product._meta.get_field("seo_description")
        assert field.default == ""


# ═══════════════════════════════════════════════════════════════════════
# 14. Product Mixin Inheritance
# ═══════════════════════════════════════════════════════════════════════


class TestProductMixins:
    """Verify the Product model inherits expected mixin fields from BaseModel."""

    def test_has_uuid_primary_key(self):
        pk = Product._meta.pk
        assert isinstance(pk, models.UUIDField)

    def test_uuid_is_primary_key(self):
        pk = Product._meta.pk
        assert pk.primary_key is True

    def test_has_created_on_field(self):
        field = Product._meta.get_field("created_on")
        assert isinstance(field, models.DateTimeField)

    def test_created_on_not_editable(self):
        field = Product._meta.get_field("created_on")
        assert field.editable is False

    def test_has_updated_on_field(self):
        field = Product._meta.get_field("updated_on")
        assert isinstance(field, models.DateTimeField)

    def test_updated_on_auto_now(self):
        field = Product._meta.get_field("updated_on")
        assert field.auto_now is True

    def test_has_is_active_field(self):
        field = Product._meta.get_field("is_active")
        assert isinstance(field, models.BooleanField)

    def test_is_active_default_true(self):
        field = Product._meta.get_field("is_active")
        assert field.default is True

    def test_has_is_deleted_field(self):
        field = Product._meta.get_field("is_deleted")
        assert isinstance(field, models.BooleanField)

    def test_is_deleted_default_false(self):
        field = Product._meta.get_field("is_deleted")
        assert field.default is False

    def test_inherits_base_model(self):
        from apps.core.models import BaseModel

        assert issubclass(Product, BaseModel)


# ═══════════════════════════════════════════════════════════════════════
# 15. Product String Representation
# ═══════════════════════════════════════════════════════════════════════


class TestProductStringRepresentation:
    """Test the ``__str__`` method for Product."""

    def test_str_returns_name_with_sku(self):
        p = _make_product(name="Test Phone", sku="PRD-ELEC-00001")
        assert str(p) == "Test Phone (PRD-ELEC-00001)"

    def test_str_without_sku(self):
        p = _make_product(name="Test Phone", sku="")
        assert str(p) == "Test Phone"

    def test_str_with_unicode_name(self):
        p = _make_product(name="ශ්‍රී ලංකා දුරකථනය", sku="PRD-00001")
        assert str(p) == "ශ්‍රී ලංකා දුරකථනය (PRD-00001)"

    def test_str_with_long_name(self):
        long_name = "P" * 200
        p = _make_product(name=long_name, sku="SKU-001")
        assert str(p) == f"{long_name} (SKU-001)"


# ═══════════════════════════════════════════════════════════════════════
# 16. Product Defaults
# ═══════════════════════════════════════════════════════════════════════


class TestProductDefaults:
    """Test default values for Product fields."""

    def test_default_status_is_draft(self):
        field = Product._meta.get_field("status")
        assert field.default == PRODUCT_STATUS.DRAFT

    def test_default_product_type_is_simple(self):
        field = Product._meta.get_field("product_type")
        assert field.default == PRODUCT_TYPES.SIMPLE

    def test_default_is_webstore_visible_true(self):
        field = Product._meta.get_field("is_webstore_visible")
        assert field.default is True

    def test_default_is_pos_visible_true(self):
        field = Product._meta.get_field("is_pos_visible")
        assert field.default is True

    def test_default_featured_false(self):
        field = Product._meta.get_field("featured")
        assert field.default is False

    def test_default_cost_price_zero(self):
        field = Product._meta.get_field("cost_price")
        assert field.default == 0

    def test_default_selling_price_zero(self):
        field = Product._meta.get_field("selling_price")
        assert field.default == 0


# ═══════════════════════════════════════════════════════════════════════
# 17. Product Profit Margin Property
# ═══════════════════════════════════════════════════════════════════════


class TestProductProfitMargin:
    """Test the profit_margin property."""

    def test_profit_margin_positive(self):
        p = _make_product(
            cost_price=Decimal("100.00"), selling_price=Decimal("150.00")
        )
        assert p.profit_margin == Decimal("50.0")

    def test_profit_margin_zero_cost(self):
        p = _make_product(cost_price=Decimal("0.00"), selling_price=Decimal("100.00"))
        assert p.profit_margin == 0

    def test_profit_margin_no_selling_price(self):
        p = _make_product(cost_price=Decimal("100.00"), selling_price=Decimal("0.00"))
        assert p.profit_margin == 0

    def test_profit_margin_both_zero(self):
        p = _make_product(cost_price=Decimal("0.00"), selling_price=Decimal("0.00"))
        assert p.profit_margin == 0

    def test_profit_margin_high_margin(self):
        p = _make_product(
            cost_price=Decimal("50.00"), selling_price=Decimal("200.00")
        )
        assert p.profit_margin == Decimal("300.0")

    def test_profit_margin_negative_margin(self):
        p = _make_product(
            cost_price=Decimal("200.00"), selling_price=Decimal("100.00")
        )
        assert p.profit_margin == Decimal("-50.0")

    def test_profit_margin_is_property(self):
        assert isinstance(Product.profit_margin, property)


# ═══════════════════════════════════════════════════════════════════════
# 18. Product Manager
# ═══════════════════════════════════════════════════════════════════════


class TestProductManager:
    """Test Product.objects is ProductManager and has expected methods."""

    def test_objects_is_product_manager(self):
        # ProductManager is assigned but BaseModel.objects (AliveManager) may
        # take precedence. Product explicitly sets objects = ProductManager().
        assert isinstance(Product.objects, ProductManager)

    def test_manager_has_active_method(self):
        assert hasattr(Product.objects, "active")

    def test_manager_has_published_method(self):
        assert hasattr(Product.objects, "published")

    def test_manager_has_in_stock_method(self):
        assert hasattr(Product.objects, "in_stock")

    def test_manager_has_by_category_method(self):
        assert hasattr(Product.objects, "by_category")

    def test_manager_has_by_brand_method(self):
        assert hasattr(Product.objects, "by_brand")

    def test_manager_has_simple_products_method(self):
        assert hasattr(Product.objects, "simple_products")

    def test_manager_has_variable_products_method(self):
        assert hasattr(Product.objects, "variable_products")

    def test_manager_has_featured_method(self):
        assert hasattr(Product.objects, "featured")

    def test_manager_has_for_pos_method(self):
        assert hasattr(Product.objects, "for_pos")

    def test_manager_has_for_webstore_method(self):
        assert hasattr(Product.objects, "for_webstore")

    def test_manager_has_by_status_method(self):
        assert hasattr(Product.objects, "by_status")

    def test_manager_has_search_method(self):
        assert hasattr(Product.objects, "search")

    def test_manager_has_get_queryset_method(self):
        assert hasattr(Product.objects, "get_queryset")


# ═══════════════════════════════════════════════════════════════════════
# 19. ProductQuerySet
# ═══════════════════════════════════════════════════════════════════════


class TestProductQuerySet:
    """Test ``ProductQuerySet`` methods via mock (no DB)."""

    def test_inherits_queryset(self):
        assert issubclass(ProductQuerySet, models.QuerySet)

    # ── active() ────────────────────────────────────────────────────

    def test_active_filters_correct_kwargs(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        ProductQuerySet.active(qs)
        qs.filter.assert_called_once_with(
            status=PRODUCT_STATUS.ACTIVE,
            is_active=True,
            is_deleted=False,
        )

    def test_active_returns_queryset(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        result = ProductQuerySet.active(qs)
        assert result is qs

    # ── published() ─────────────────────────────────────────────────

    def test_published_filters_correct_kwargs(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        ProductQuerySet.published(qs)
        qs.filter.assert_called_once_with(
            status=PRODUCT_STATUS.ACTIVE,
            is_active=True,
            is_deleted=False,
            is_webstore_visible=True,
        )

    def test_published_returns_queryset(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        result = ProductQuerySet.published(qs)
        assert result is qs

    # ── by_category() ───────────────────────────────────────────────

    def test_by_category_with_object(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        cat_mock = MagicMock()
        cat_mock.pk = uuid.uuid4()
        ProductQuerySet.by_category(qs, cat_mock)
        qs.filter.assert_called_once_with(category_id=cat_mock.pk)

    def test_by_category_with_uuid(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        cat_id = uuid.uuid4()
        ProductQuerySet.by_category(qs, cat_id)
        qs.filter.assert_called_once_with(category_id=cat_id)

    # ── by_brand() ──────────────────────────────────────────────────

    def test_by_brand_with_object(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        brand_mock = MagicMock()
        brand_mock.pk = uuid.uuid4()
        ProductQuerySet.by_brand(qs, brand_mock)
        qs.filter.assert_called_once_with(brand_id=brand_mock.pk)

    def test_by_brand_with_uuid(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        brand_id = uuid.uuid4()
        ProductQuerySet.by_brand(qs, brand_id)
        qs.filter.assert_called_once_with(brand_id=brand_id)

    # ── simple_products() ───────────────────────────────────────────

    def test_simple_products_filters(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        ProductQuerySet.simple_products(qs)
        qs.filter.assert_called_once_with(product_type=PRODUCT_TYPES.SIMPLE)

    # ── variable_products() ─────────────────────────────────────────

    def test_variable_products_filters(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        ProductQuerySet.variable_products(qs)
        qs.filter.assert_called_once_with(product_type=PRODUCT_TYPES.VARIABLE)

    # ── featured() ──────────────────────────────────────────────────

    def test_featured_filters(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        ProductQuerySet.featured(qs)
        qs.filter.assert_called_once_with(featured=True)

    # ── for_pos() ───────────────────────────────────────────────────

    def test_for_pos_calls_active_and_filter(self):
        qs = MagicMock(spec=ProductQuerySet)
        active_qs = MagicMock(spec=ProductQuerySet)
        qs.active = MagicMock(return_value=active_qs)
        active_qs.filter = MagicMock(return_value=active_qs)
        ProductQuerySet.for_pos(qs)
        qs.active.assert_called_once()
        active_qs.filter.assert_called_once_with(is_pos_visible=True)

    # ── for_webstore() ──────────────────────────────────────────────

    def test_for_webstore_calls_published(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.published = MagicMock(return_value=qs)
        ProductQuerySet.for_webstore(qs)
        qs.published.assert_called_once()

    # ── by_status() ─────────────────────────────────────────────────

    def test_by_status_filters(self):
        qs = MagicMock(spec=ProductQuerySet)
        qs.filter = MagicMock(return_value=qs)
        ProductQuerySet.by_status(qs, PRODUCT_STATUS.DRAFT)
        qs.filter.assert_called_once_with(status=PRODUCT_STATUS.DRAFT)


# ═══════════════════════════════════════════════════════════════════════
# 20. Product Manager Methods
# ═══════════════════════════════════════════════════════════════════════


class TestProductManagerMethods:
    """Test that ProductManager proxies all QuerySet methods."""

    def _make_manager(self):
        manager = ProductManager()
        manager.model = Product
        manager._db = None
        mock_qs = MagicMock(spec=ProductQuerySet)
        manager.get_queryset = MagicMock(return_value=mock_qs)
        return manager, mock_qs

    def test_active_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        manager.active()
        mock_qs.active.assert_called_once()

    def test_published_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        manager.published()
        mock_qs.published.assert_called_once()

    def test_in_stock_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        manager.in_stock()
        mock_qs.in_stock.assert_called_once()

    def test_by_category_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        cat_id = uuid.uuid4()
        manager.by_category(cat_id)
        mock_qs.by_category.assert_called_once_with(cat_id)

    def test_by_brand_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        brand_id = uuid.uuid4()
        manager.by_brand(brand_id)
        mock_qs.by_brand.assert_called_once_with(brand_id)

    def test_simple_products_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        manager.simple_products()
        mock_qs.simple_products.assert_called_once()

    def test_variable_products_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        manager.variable_products()
        mock_qs.variable_products.assert_called_once()

    def test_featured_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        manager.featured()
        mock_qs.featured.assert_called_once()

    def test_for_pos_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        manager.for_pos()
        mock_qs.for_pos.assert_called_once()

    def test_for_webstore_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        manager.for_webstore()
        mock_qs.for_webstore.assert_called_once()

    def test_by_status_proxies_to_queryset(self):
        manager, mock_qs = self._make_manager()
        manager.by_status(PRODUCT_STATUS.ACTIVE)
        mock_qs.by_status.assert_called_once_with(PRODUCT_STATUS.ACTIVE)

    def test_get_queryset_returns_product_queryset(self):
        manager = ProductManager()
        manager.model = Product
        manager._db = None
        with patch.object(
            ProductQuerySet, "__init__", return_value=None
        ) as mock_init:
            manager.get_queryset()
            mock_init.assert_called_once_with(Product, using=None)
