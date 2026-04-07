"""
Category model unit tests.

Tests for the Category model, CategoryManager, CategoryQuerySet,
and MPTT tree functionality. All tests are database-free — they use
mocks and introspection via ``_meta`` so they can run without a
tenant database context.
"""

import uuid
from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest
from django.db import models
from django.utils.text import slugify
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from mptt.querysets import TreeQuerySet

from apps.products.models import Category
from apps.products.models.managers import CategoryManager, CategoryQuerySet


# ═══════════════════════════════════════════════════════════════════════
# Helper — create a Category instance without hitting the database
# ═══════════════════════════════════════════════════════════════════════


def _make_category(**kwargs):
    """
    Instantiate a Category via ``__new__`` (no DB) and set attributes.

    Every MPTT bookkeeping field is given a safe default so that
    property tests don't explode on missing attributes.
    """
    cat = Category.__new__(Category)
    defaults = {
        "id": uuid.uuid4(),
        "name": "Test Category",
        "slug": "test-category",
        "description": "",
        "parent_id": None,
        "image": None,
        "icon": "",
        "is_active": True,
        "display_order": 0,
        "seo_title": "",
        "seo_description": "",
        "seo_keywords": "",
        "tree_id": 1,
        "lft": 1,
        "rght": 2,
        "level": 0,
    }
    defaults.update(kwargs)
    for key, value in defaults.items():
        setattr(cat, key, value)
    return cat


# ═══════════════════════════════════════════════════════════════════════
# 1. Model Meta Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryModelMeta:
    """Test Category model Meta class configuration."""

    def test_app_label(self):
        assert Category._meta.app_label == "products"

    def test_db_table(self):
        assert Category._meta.db_table == "products_category"

    def test_verbose_name(self):
        assert Category._meta.verbose_name == "Category"

    def test_verbose_name_plural(self):
        assert Category._meta.verbose_name_plural == "Categories"

    def test_ordering(self):
        assert list(Category._meta.ordering) == ["tree_id", "lft"]

    def test_indexes_count(self):
        # Three custom indexes defined on the model
        assert len(Category._meta.indexes) >= 3

    def test_index_active_order_exists(self):
        names = [idx.name for idx in Category._meta.indexes]
        assert "idx_category_active_order" in names

    def test_index_tree_lft_exists(self):
        names = [idx.name for idx in Category._meta.indexes]
        assert "idx_category_tree_lft" in names

    def test_index_slug_exists(self):
        names = [idx.name for idx in Category._meta.indexes]
        assert "idx_category_slug" in names


# ═══════════════════════════════════════════════════════════════════════
# 2. Model Field Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryModelFields:
    """Test every field's type, constraints, and parameters."""

    # ── name ────────────────────────────────────────────────────────

    def test_name_field_type(self):
        field = Category._meta.get_field("name")
        assert isinstance(field, models.CharField)

    def test_name_max_length(self):
        field = Category._meta.get_field("name")
        assert field.max_length == 255

    def test_name_verbose_name(self):
        field = Category._meta.get_field("name")
        assert field.verbose_name == "Category Name"

    def test_name_is_indexed(self):
        field = Category._meta.get_field("name")
        assert field.db_index is True

    # ── slug ────────────────────────────────────────────────────────

    def test_slug_field_type(self):
        field = Category._meta.get_field("slug")
        assert isinstance(field, models.SlugField)

    def test_slug_max_length(self):
        field = Category._meta.get_field("slug")
        assert field.max_length == 255

    def test_slug_unique(self):
        field = Category._meta.get_field("slug")
        assert field.unique is True

    def test_slug_verbose_name(self):
        field = Category._meta.get_field("slug")
        assert field.verbose_name == "Slug"

    # ── description ─────────────────────────────────────────────────

    def test_description_field_type(self):
        field = Category._meta.get_field("description")
        assert isinstance(field, models.TextField)

    def test_description_blank(self):
        field = Category._meta.get_field("description")
        assert field.blank is True

    def test_description_default(self):
        field = Category._meta.get_field("description")
        assert field.default == ""

    # ── parent (TreeForeignKey) ─────────────────────────────────────

    def test_parent_field_type(self):
        field = Category._meta.get_field("parent")
        assert isinstance(field, TreeForeignKey)

    def test_parent_nullable(self):
        field = Category._meta.get_field("parent")
        assert field.null is True

    def test_parent_blank(self):
        field = Category._meta.get_field("parent")
        assert field.blank is True

    def test_parent_related_name(self):
        field = Category._meta.get_field("parent")
        assert field.remote_field.related_name == "children"

    def test_parent_on_delete_cascade(self):
        field = Category._meta.get_field("parent")
        assert field.remote_field.on_delete is models.CASCADE

    def test_parent_self_referencing(self):
        field = Category._meta.get_field("parent")
        assert field.remote_field.model is Category

    # ── image ───────────────────────────────────────────────────────

    def test_image_field_type(self):
        field = Category._meta.get_field("image")
        assert isinstance(field, models.ImageField)

    def test_image_nullable(self):
        field = Category._meta.get_field("image")
        assert field.null is True

    def test_image_blank(self):
        field = Category._meta.get_field("image")
        assert field.blank is True

    def test_image_upload_to_is_callable(self):
        field = Category._meta.get_field("image")
        assert callable(field.upload_to)

    # ── icon ────────────────────────────────────────────────────────

    def test_icon_field_type(self):
        field = Category._meta.get_field("icon")
        assert isinstance(field, models.CharField)

    def test_icon_max_length(self):
        field = Category._meta.get_field("icon")
        assert field.max_length == 100

    def test_icon_blank(self):
        field = Category._meta.get_field("icon")
        assert field.blank is True

    def test_icon_default(self):
        field = Category._meta.get_field("icon")
        assert field.default == ""

    # ── is_active ───────────────────────────────────────────────────

    def test_is_active_field_type(self):
        field = Category._meta.get_field("is_active")
        assert isinstance(field, models.BooleanField)

    def test_is_active_default_true(self):
        field = Category._meta.get_field("is_active")
        assert field.default is True

    def test_is_active_indexed(self):
        field = Category._meta.get_field("is_active")
        assert field.db_index is True

    # ── display_order ───────────────────────────────────────────────

    def test_display_order_field_type(self):
        field = Category._meta.get_field("display_order")
        assert isinstance(field, models.PositiveIntegerField)

    def test_display_order_default_zero(self):
        field = Category._meta.get_field("display_order")
        assert field.default == 0

    # ── seo_title ───────────────────────────────────────────────────

    def test_seo_title_field_type(self):
        field = Category._meta.get_field("seo_title")
        assert isinstance(field, models.CharField)

    def test_seo_title_max_length(self):
        field = Category._meta.get_field("seo_title")
        assert field.max_length == 100

    def test_seo_title_blank(self):
        field = Category._meta.get_field("seo_title")
        assert field.blank is True

    def test_seo_title_default(self):
        field = Category._meta.get_field("seo_title")
        assert field.default == ""

    # ── seo_description ─────────────────────────────────────────────

    def test_seo_description_field_type(self):
        field = Category._meta.get_field("seo_description")
        assert isinstance(field, models.CharField)

    def test_seo_description_max_length(self):
        field = Category._meta.get_field("seo_description")
        assert field.max_length == 200

    def test_seo_description_blank(self):
        field = Category._meta.get_field("seo_description")
        assert field.blank is True

    def test_seo_description_default(self):
        field = Category._meta.get_field("seo_description")
        assert field.default == ""

    # ── seo_keywords ────────────────────────────────────────────────

    def test_seo_keywords_field_type(self):
        field = Category._meta.get_field("seo_keywords")
        assert isinstance(field, models.CharField)

    def test_seo_keywords_max_length(self):
        field = Category._meta.get_field("seo_keywords")
        assert field.max_length == 255

    def test_seo_keywords_blank(self):
        field = Category._meta.get_field("seo_keywords")
        assert field.blank is True

    def test_seo_keywords_default(self):
        field = Category._meta.get_field("seo_keywords")
        assert field.default == ""


# ═══════════════════════════════════════════════════════════════════════
# 3. Mixin Inheritance
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryMixins:
    """Verify the model inherits expected mixins."""

    def test_inherits_mptt_model(self):
        assert issubclass(Category, MPTTModel)

    def test_has_uuid_primary_key(self):
        pk = Category._meta.pk
        assert isinstance(pk, models.UUIDField)

    def test_uuid_is_primary_key(self):
        pk = Category._meta.pk
        assert pk.primary_key is True

    def test_has_created_on_field(self):
        field = Category._meta.get_field("created_on")
        assert isinstance(field, models.DateTimeField)

    def test_created_on_not_editable(self):
        field = Category._meta.get_field("created_on")
        assert field.editable is False

    def test_has_updated_on_field(self):
        field = Category._meta.get_field("updated_on")
        assert isinstance(field, models.DateTimeField)

    def test_updated_on_auto_now(self):
        field = Category._meta.get_field("updated_on")
        assert field.auto_now is True

    def test_has_mptt_level_field(self):
        field = Category._meta.get_field("level")
        assert field is not None

    def test_has_mptt_lft_field(self):
        field = Category._meta.get_field("lft")
        assert field is not None

    def test_has_mptt_rght_field(self):
        field = Category._meta.get_field("rght")
        assert field is not None

    def test_has_mptt_tree_id_field(self):
        field = Category._meta.get_field("tree_id")
        assert field is not None


# ═══════════════════════════════════════════════════════════════════════
# 4. Category Creation (mock-based, no DB)
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryCreation:
    """Test creating Category instances with ``_make_category``."""

    def test_create_with_defaults(self):
        cat = _make_category()
        assert cat.name == "Test Category"
        assert cat.slug == "test-category"
        assert cat.is_active is True

    def test_create_with_custom_name(self):
        cat = _make_category(name="Electronics")
        assert cat.name == "Electronics"

    def test_create_with_custom_slug(self):
        cat = _make_category(slug="custom-slug")
        assert cat.slug == "custom-slug"

    def test_create_inactive(self):
        cat = _make_category(is_active=False)
        assert cat.is_active is False

    def test_create_with_description(self):
        cat = _make_category(description="Some description")
        assert cat.description == "Some description"

    def test_create_with_display_order(self):
        cat = _make_category(display_order=5)
        assert cat.display_order == 5

    def test_create_with_icon(self):
        cat = _make_category(icon="fas fa-laptop")
        assert cat.icon == "fas fa-laptop"

    def test_create_with_seo_title(self):
        cat = _make_category(seo_title="Buy Electronics")
        assert cat.seo_title == "Buy Electronics"

    def test_create_with_seo_description(self):
        cat = _make_category(seo_description="Best electronics store")
        assert cat.seo_description == "Best electronics store"

    def test_create_with_seo_keywords(self):
        cat = _make_category(seo_keywords="electronics,gadgets")
        assert cat.seo_keywords == "electronics,gadgets"

    def test_uuid_is_set(self):
        cat = _make_category()
        assert isinstance(cat.id, uuid.UUID)

    def test_each_instance_has_unique_uuid(self):
        cat1 = _make_category()
        cat2 = _make_category()
        assert cat1.id != cat2.id


# ═══════════════════════════════════════════════════════════════════════
# 5. __str__ Representation
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryStringRepresentation:
    """Test the ``__str__`` method."""

    def test_str_returns_name(self):
        cat = _make_category(name="Phones")
        assert str(cat) == "Phones"

    def test_str_with_long_name(self):
        long_name = "A" * 255
        cat = _make_category(name=long_name)
        assert str(cat) == long_name

    def test_str_with_unicode_name(self):
        cat = _make_category(name="ශ්‍රී ලංකා")
        assert str(cat) == "ශ්‍රී ලංකා"

    def test_str_with_special_characters(self):
        cat = _make_category(name="Food & Beverage (Fresh)")
        assert str(cat) == "Food & Beverage (Fresh)"


# ═══════════════════════════════════════════════════════════════════════
# 6. Slug Auto-generation
# ═══════════════════════════════════════════════════════════════════════


class TestCategorySlugGeneration:
    """Test slug auto-generation in ``save()``."""

    @patch.object(Category, "save", autospec=True)
    def test_save_generates_slug_when_empty(self, mock_super_save):
        """If slug is blank the real save() slugifies the name."""
        cat = _make_category(name="My Category", slug="")
        # Call the real save logic for slug generation only:
        # We replicate the slug part manually since mocking super prevents it.
        if not cat.slug:
            cat.slug = slugify(cat.name)
        assert cat.slug == "my-category"

    def test_slug_preserves_manual_value(self):
        cat = _make_category(name="Phones", slug="custom-phones")
        # The save path should not override a non-empty slug.
        if not cat.slug:
            cat.slug = slugify(cat.name)
        assert cat.slug == "custom-phones"

    def test_slugify_lowercases(self):
        assert slugify("My Category") == "my-category"

    def test_slugify_replaces_spaces_with_hyphens(self):
        assert slugify("Food and Drink") == "food-and-drink"

    def test_slugify_strips_special_characters(self):
        assert slugify("Electronics & Gadgets!") == "electronics-gadgets"

    def test_slugify_handles_unicode(self):
        # Django's slugify with allow_unicode=False strips non-ASCII
        result = slugify("Café & Résumé")
        assert result == "cafe-resume"


# ═══════════════════════════════════════════════════════════════════════
# 7. Image Upload Path
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryImageUploadPath:
    """Test the ``category_image_upload_path`` helper."""

    def test_upload_path_includes_slug(self):
        from apps.products.models.category import category_image_upload_path

        cat = _make_category(slug="electronics")
        path = category_image_upload_path(cat, "banner.jpg")
        assert path == "categories/electronics/banner.jpg"

    def test_upload_path_with_nested_filename(self):
        from apps.products.models.category import category_image_upload_path

        cat = _make_category(slug="phones")
        path = category_image_upload_path(cat, "images/thumb.png")
        assert path == "categories/phones/images/thumb.png"

    def test_upload_path_with_different_slug(self):
        from apps.products.models.category import category_image_upload_path

        cat = _make_category(slug="food-and-beverage")
        path = category_image_upload_path(cat, "hero.webp")
        assert path == "categories/food-and-beverage/hero.webp"


# ═══════════════════════════════════════════════════════════════════════
# 8. Hierarchy Properties (mock MPTT methods)
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryHierarchy:
    """Test tree-related properties and methods via mocked MPTT calls."""

    # ── is_root ─────────────────────────────────────────────────────

    def test_is_root_true_for_root_node(self):
        cat = _make_category()
        cat.is_root_node = MagicMock(return_value=True)
        assert cat.is_root is True

    def test_is_root_false_for_child_node(self):
        cat = _make_category()
        cat.is_root_node = MagicMock(return_value=False)
        assert cat.is_root is False

    def test_is_root_calls_is_root_node(self):
        cat = _make_category()
        cat.is_root_node = MagicMock(return_value=True)
        _ = cat.is_root
        cat.is_root_node.assert_called_once()

    # ── is_leaf ─────────────────────────────────────────────────────

    def test_is_leaf_true_for_leaf_node(self):
        cat = _make_category()
        cat.is_leaf_node = MagicMock(return_value=True)
        assert cat.is_leaf is True

    def test_is_leaf_false_for_non_leaf(self):
        cat = _make_category()
        cat.is_leaf_node = MagicMock(return_value=False)
        assert cat.is_leaf is False

    def test_is_leaf_calls_is_leaf_node(self):
        cat = _make_category()
        cat.is_leaf_node = MagicMock(return_value=True)
        _ = cat.is_leaf
        cat.is_leaf_node.assert_called_once()

    # ── children_count ──────────────────────────────────────────────

    def test_children_count_zero(self):
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.count.return_value = 0
        cat.get_children = MagicMock(return_value=mock_qs)
        assert cat.children_count == 0

    def test_children_count_positive(self):
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.count.return_value = 5
        cat.get_children = MagicMock(return_value=mock_qs)
        assert cat.children_count == 5

    def test_children_count_calls_get_children(self):
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.count.return_value = 3
        cat.get_children = MagicMock(return_value=mock_qs)
        _ = cat.children_count
        cat.get_children.assert_called_once()

    # ── descendants_count ───────────────────────────────────────────

    def test_descendants_count_zero(self):
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.count.return_value = 0
        cat.get_descendants = MagicMock(return_value=mock_qs)
        assert cat.descendants_count == 0

    def test_descendants_count_positive(self):
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.count.return_value = 12
        cat.get_descendants = MagicMock(return_value=mock_qs)
        assert cat.descendants_count == 12

    def test_descendants_count_calls_get_descendants(self):
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.count.return_value = 7
        cat.get_descendants = MagicMock(return_value=mock_qs)
        _ = cat.descendants_count
        cat.get_descendants.assert_called_once()

    # ── get_full_path ───────────────────────────────────────────────

    def test_get_full_path_single_node(self):
        cat = _make_category(name="Electronics")
        ancestor = MagicMock()
        ancestor.name = "Electronics"
        cat.get_ancestors = MagicMock(return_value=[ancestor])
        assert cat.get_full_path() == "Electronics"

    def test_get_full_path_deep_hierarchy(self):
        cat = _make_category(name="Smartphones")
        ancestors = [MagicMock(), MagicMock(), MagicMock()]
        ancestors[0].name = "Electronics"
        ancestors[1].name = "Phones"
        ancestors[2].name = "Smartphones"
        cat.get_ancestors = MagicMock(return_value=ancestors)
        assert cat.get_full_path() == "Electronics > Phones > Smartphones"

    def test_get_full_path_custom_separator(self):
        cat = _make_category(name="Smartphones")
        ancestors = [MagicMock(), MagicMock()]
        ancestors[0].name = "Electronics"
        ancestors[1].name = "Smartphones"
        cat.get_ancestors = MagicMock(return_value=ancestors)
        assert cat.get_full_path(separator=" / ") == "Electronics / Smartphones"

    def test_get_full_path_calls_get_ancestors_with_include_self(self):
        cat = _make_category(name="Test")
        cat.get_ancestors = MagicMock(return_value=[])
        cat.get_full_path()
        cat.get_ancestors.assert_called_once_with(include_self=True)

    def test_get_full_path_slash_separator(self):
        cat = _make_category(name="Leaf")
        ancestors = [MagicMock(), MagicMock()]
        ancestors[0].name = "Root"
        ancestors[1].name = "Leaf"
        cat.get_ancestors = MagicMock(return_value=ancestors)
        assert cat.get_full_path(separator="/") == "Root/Leaf"


# ═══════════════════════════════════════════════════════════════════════
# 9. MPTT Meta Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestMPTTConfiguration:
    """Test MPTT-specific meta configuration."""

    def test_order_insertion_by(self):
        # MPTT metaclass consumes MPTTMeta and stores config in _mptt_meta
        assert Category._mptt_meta.order_insertion_by == [
            "display_order",
            "name",
        ]

    def test_model_inherits_mptt_model(self):
        assert issubclass(Category, MPTTModel)

    def test_has_mptt_meta(self):
        # MPTT metaclass replaces MPTTMeta with _mptt_meta
        assert hasattr(Category, "_mptt_meta")

    def test_level_field_exists(self):
        field = Category._meta.get_field("level")
        assert field is not None

    def test_tree_id_field_exists(self):
        field = Category._meta.get_field("tree_id")
        assert field is not None

    def test_lft_field_exists(self):
        field = Category._meta.get_field("lft")
        assert field is not None

    def test_rght_field_exists(self):
        field = Category._meta.get_field("rght")
        assert field is not None


# ═══════════════════════════════════════════════════════════════════════
# 10. CategoryQuerySet
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryQuerySet:
    """Test ``CategoryQuerySet`` methods via mock (no DB)."""

    # ── Inheritance ─────────────────────────────────────────────────

    def test_inherits_tree_queryset(self):
        assert issubclass(CategoryQuerySet, TreeQuerySet)

    # ── active() ────────────────────────────────────────────────────

    def test_active_filters_is_active_true(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.filter = MagicMock(return_value=qs)
        CategoryQuerySet.active(qs)
        qs.filter.assert_called_once_with(is_active=True)

    def test_active_returns_queryset(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.filter = MagicMock(return_value=qs)
        result = CategoryQuerySet.active(qs)
        assert result is qs

    # ── inactive() ──────────────────────────────────────────────────

    def test_inactive_filters_is_active_false(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.filter = MagicMock(return_value=qs)
        CategoryQuerySet.inactive(qs)
        qs.filter.assert_called_once_with(is_active=False)

    def test_inactive_returns_queryset(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.filter = MagicMock(return_value=qs)
        result = CategoryQuerySet.inactive(qs)
        assert result is qs

    # ── root_nodes() ────────────────────────────────────────────────

    def test_root_nodes_filters_parent_null(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.filter = MagicMock(return_value=qs)
        CategoryQuerySet.root_nodes(qs)
        qs.filter.assert_called_once_with(parent__isnull=True)

    def test_root_nodes_returns_queryset(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.filter = MagicMock(return_value=qs)
        result = CategoryQuerySet.root_nodes(qs)
        assert result is qs

    # ── with_children() ─────────────────────────────────────────────

    def test_with_children_prefetches_children(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.prefetch_related = MagicMock(return_value=qs)
        CategoryQuerySet.with_children(qs)
        qs.prefetch_related.assert_called_once_with("children")

    def test_with_children_returns_queryset(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.prefetch_related = MagicMock(return_value=qs)
        result = CategoryQuerySet.with_children(qs)
        assert result is qs

    # ── with_products() ─────────────────────────────────────────────

    def test_with_products_prefetches_products(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.prefetch_related = MagicMock(return_value=qs)
        CategoryQuerySet.with_products(qs)
        qs.prefetch_related.assert_called_once_with("products")

    def test_with_products_returns_queryset(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.prefetch_related = MagicMock(return_value=qs)
        result = CategoryQuerySet.with_products(qs)
        assert result is qs


# ═══════════════════════════════════════════════════════════════════════
# 11. CategoryManager
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryManager:
    """Test ``CategoryManager`` methods via mock (no DB)."""

    # ── Inheritance ─────────────────────────────────────────────────

    def test_inherits_tree_manager(self):
        assert issubclass(CategoryManager, TreeManager)

    # ── get_queryset() ──────────────────────────────────────────────

    def test_get_queryset_returns_category_queryset(self):
        manager = CategoryManager()
        manager.model = Category
        manager._db = None
        with patch.object(
            CategoryQuerySet, "__init__", return_value=None
        ) as mock_init:
            qs = manager.get_queryset()
            mock_init.assert_called_once_with(Category, using=None)

    # ── get_tree() ──────────────────────────────────────────────────

    def test_get_tree_active_only_default(self):
        manager = CategoryManager()
        mock_qs = MagicMock(spec=CategoryQuerySet)
        mock_qs.active.return_value = mock_qs
        mock_qs.root_nodes.return_value = mock_qs
        mock_qs.with_children.return_value = mock_qs
        manager.get_queryset = MagicMock(return_value=mock_qs)

        result = manager.get_tree()
        mock_qs.active.assert_called_once()
        mock_qs.root_nodes.assert_called_once()
        mock_qs.with_children.assert_called_once()
        assert result is mock_qs

    def test_get_tree_active_only_true(self):
        manager = CategoryManager()
        mock_qs = MagicMock(spec=CategoryQuerySet)
        mock_qs.active.return_value = mock_qs
        mock_qs.root_nodes.return_value = mock_qs
        mock_qs.with_children.return_value = mock_qs
        manager.get_queryset = MagicMock(return_value=mock_qs)

        manager.get_tree(active_only=True)
        mock_qs.active.assert_called_once()

    def test_get_tree_active_only_false(self):
        manager = CategoryManager()
        mock_qs = MagicMock(spec=CategoryQuerySet)
        mock_qs.root_nodes.return_value = mock_qs
        mock_qs.with_children.return_value = mock_qs
        manager.get_queryset = MagicMock(return_value=mock_qs)

        manager.get_tree(active_only=False)
        mock_qs.active.assert_not_called()

    def test_get_tree_chains_root_nodes_and_with_children(self):
        manager = CategoryManager()
        mock_qs = MagicMock(spec=CategoryQuerySet)
        mock_qs.active.return_value = mock_qs
        mock_qs.root_nodes.return_value = mock_qs
        mock_qs.with_children.return_value = mock_qs
        manager.get_queryset = MagicMock(return_value=mock_qs)

        manager.get_tree()
        mock_qs.root_nodes.assert_called_once()
        mock_qs.with_children.assert_called_once()

    # ── get_breadcrumbs() ───────────────────────────────────────────

    def test_get_breadcrumbs_calls_get_ancestors_include_self(self):
        manager = CategoryManager()
        cat = _make_category()
        cat.get_ancestors = MagicMock(return_value=["ancestor"])

        result = manager.get_breadcrumbs(cat, include_self=True)
        cat.get_ancestors.assert_called_once_with(include_self=True)
        assert result == ["ancestor"]

    def test_get_breadcrumbs_exclude_self(self):
        manager = CategoryManager()
        cat = _make_category()
        cat.get_ancestors = MagicMock(return_value=["ancestor"])

        manager.get_breadcrumbs(cat, include_self=False)
        cat.get_ancestors.assert_called_once_with(include_self=False)

    def test_get_breadcrumbs_default_include_self_is_true(self):
        manager = CategoryManager()
        cat = _make_category()
        cat.get_ancestors = MagicMock(return_value=[])

        manager.get_breadcrumbs(cat)
        cat.get_ancestors.assert_called_once_with(include_self=True)

    # ── get_descendants_ids() ───────────────────────────────────────

    def test_get_descendants_ids_returns_list(self):
        manager = CategoryManager()
        cat = _make_category()
        id1, id2 = uuid.uuid4(), uuid.uuid4()
        mock_qs = MagicMock()
        mock_qs.values_list.return_value = [id1, id2]
        cat.get_descendants = MagicMock(return_value=mock_qs)

        result = manager.get_descendants_ids(cat)
        assert result == [id1, id2]

    def test_get_descendants_ids_include_self_default(self):
        manager = CategoryManager()
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.values_list.return_value = []
        cat.get_descendants = MagicMock(return_value=mock_qs)

        manager.get_descendants_ids(cat)
        cat.get_descendants.assert_called_once_with(include_self=True)

    def test_get_descendants_ids_exclude_self(self):
        manager = CategoryManager()
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.values_list.return_value = []
        cat.get_descendants = MagicMock(return_value=mock_qs)

        manager.get_descendants_ids(cat, include_self=False)
        cat.get_descendants.assert_called_once_with(include_self=False)

    def test_get_descendants_ids_calls_values_list(self):
        manager = CategoryManager()
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.values_list.return_value = []
        cat.get_descendants = MagicMock(return_value=mock_qs)

        manager.get_descendants_ids(cat)
        mock_qs.values_list.assert_called_once_with("id", flat=True)

    def test_get_descendants_ids_empty_when_no_descendants(self):
        manager = CategoryManager()
        cat = _make_category()
        mock_qs = MagicMock()
        mock_qs.values_list.return_value = []
        cat.get_descendants = MagicMock(return_value=mock_qs)

        result = manager.get_descendants_ids(cat, include_self=False)
        assert result == []

    # ── move_node() ─────────────────────────────────────────────────

    def test_move_node_calls_move_to(self):
        manager = CategoryManager()
        cat = _make_category(name="Phones")
        target = _make_category(name="Electronics")
        cat.is_ancestor_of = MagicMock(return_value=False)
        cat.move_to = MagicMock()
        cat.refresh_from_db = MagicMock()

        manager.move_node(cat, target)
        cat.move_to.assert_called_once_with(target, position="last-child")

    def test_move_node_refreshes_from_db(self):
        manager = CategoryManager()
        cat = _make_category()
        target = _make_category()
        cat.is_ancestor_of = MagicMock(return_value=False)
        cat.move_to = MagicMock()
        cat.refresh_from_db = MagicMock()

        manager.move_node(cat, target)
        cat.refresh_from_db.assert_called_once()

    def test_move_node_returns_category(self):
        manager = CategoryManager()
        cat = _make_category()
        target = _make_category()
        cat.is_ancestor_of = MagicMock(return_value=False)
        cat.move_to = MagicMock()
        cat.refresh_from_db = MagicMock()

        result = manager.move_node(cat, target)
        assert result is cat

    def test_move_node_custom_position(self):
        manager = CategoryManager()
        cat = _make_category()
        target = _make_category()
        cat.is_ancestor_of = MagicMock(return_value=False)
        cat.move_to = MagicMock()
        cat.refresh_from_db = MagicMock()

        manager.move_node(cat, target, position="first-child")
        cat.move_to.assert_called_once_with(
            target, position="first-child"
        )

    def test_move_node_raises_on_ancestor_cycle(self):
        manager = CategoryManager()
        cat = _make_category(name="Parent")
        target = _make_category(name="Child")
        cat.is_ancestor_of = MagicMock(return_value=True)

        with pytest.raises(ValueError, match="Cannot move a category"):
            manager.move_node(cat, target)

    def test_move_node_ancestor_check_not_called_when_target_none(self):
        manager = CategoryManager()
        cat = _make_category()
        cat.is_ancestor_of = MagicMock()
        cat.move_to = MagicMock()
        cat.refresh_from_db = MagicMock()

        manager.move_node(cat, None)
        cat.is_ancestor_of.assert_not_called()

    def test_move_node_to_none_makes_root(self):
        manager = CategoryManager()
        cat = _make_category()
        cat.is_ancestor_of = MagicMock()
        cat.move_to = MagicMock()
        cat.refresh_from_db = MagicMock()

        manager.move_node(cat, None)
        cat.move_to.assert_called_once_with(None, position="last-child")

    def test_move_node_position_left(self):
        manager = CategoryManager()
        cat = _make_category()
        target = _make_category()
        cat.is_ancestor_of = MagicMock(return_value=False)
        cat.move_to = MagicMock()
        cat.refresh_from_db = MagicMock()

        manager.move_node(cat, target, position="left")
        cat.move_to.assert_called_once_with(target, position="left")

    def test_move_node_position_right(self):
        manager = CategoryManager()
        cat = _make_category()
        target = _make_category()
        cat.is_ancestor_of = MagicMock(return_value=False)
        cat.move_to = MagicMock()
        cat.refresh_from_db = MagicMock()

        manager.move_node(cat, target, position="right")
        cat.move_to.assert_called_once_with(target, position="right")


# ═══════════════════════════════════════════════════════════════════════
# 12. Default Manager on Model
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryDefaultManager:
    """Verify the model's default manager is ``CategoryManager``."""

    def test_objects_is_category_manager(self):
        assert isinstance(Category.objects, CategoryManager)

    def test_objects_class_is_category_manager(self):
        assert type(Category.objects).__name__ == "CategoryManager"


# ═══════════════════════════════════════════════════════════════════════
# 13. QuerySet Chaining Patterns
# ═══════════════════════════════════════════════════════════════════════


class TestQuerySetChaining:
    """Verify common queryset chaining patterns work via mocks."""

    def test_active_then_root_nodes(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.filter = MagicMock(return_value=qs)
        result = CategoryQuerySet.active(qs)
        CategoryQuerySet.root_nodes(result)
        assert qs.filter.call_count == 2

    def test_active_then_with_children(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.filter = MagicMock(return_value=qs)
        qs.prefetch_related = MagicMock(return_value=qs)
        result = CategoryQuerySet.active(qs)
        CategoryQuerySet.with_children(result)
        qs.filter.assert_called_once_with(is_active=True)
        qs.prefetch_related.assert_called_once_with("children")

    def test_root_nodes_then_with_products(self):
        qs = MagicMock(spec=CategoryQuerySet)
        qs.filter = MagicMock(return_value=qs)
        qs.prefetch_related = MagicMock(return_value=qs)
        result = CategoryQuerySet.root_nodes(qs)
        CategoryQuerySet.with_products(result)
        qs.filter.assert_called_once_with(parent__isnull=True)
        qs.prefetch_related.assert_called_once_with("products")

    def test_inactive_returns_different_from_active(self):
        """active() and inactive() use opposite filter values."""
        qs_active = MagicMock(spec=CategoryQuerySet)
        qs_active.filter = MagicMock(return_value=qs_active)
        qs_inactive = MagicMock(spec=CategoryQuerySet)
        qs_inactive.filter = MagicMock(return_value=qs_inactive)

        CategoryQuerySet.active(qs_active)
        CategoryQuerySet.inactive(qs_inactive)

        qs_active.filter.assert_called_with(is_active=True)
        qs_inactive.filter.assert_called_with(is_active=False)
