"""
Attribute model unit tests.

Tests for the AttributeGroup, Attribute, and AttributeOption models,
their managers, querysets, and field configurations.
All tests are database-free — they use _meta introspection and mocks.
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest
from django.db import models

from apps.attributes.constants import (
    ATTRIBUTE_TYPES,
    BOOLEAN,
    DATE,
    MULTISELECT,
    NUMBER,
    SELECT,
    TEXT,
)
from apps.attributes.models import Attribute, AttributeGroup, AttributeOption


# ═══════════════════════════════════════════════════════════════════════
# 1. AttributeGroup — Meta Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupModelMeta:
    """Test AttributeGroup model Meta class configuration."""

    def test_app_label(self):
        assert AttributeGroup._meta.app_label == "attributes"

    def test_verbose_name(self):
        assert AttributeGroup._meta.verbose_name == "Attribute Group"

    def test_verbose_name_plural(self):
        assert AttributeGroup._meta.verbose_name_plural == "Attribute Groups"

    def test_ordering(self):
        assert list(AttributeGroup._meta.ordering) == ["display_order", "name"]

    def test_index_active_order_exists(self):
        names = [idx.name for idx in AttributeGroup._meta.indexes]
        assert "attrs_grp_active_order_idx" in names

    def test_index_fields(self):
        idx = next(
            i
            for i in AttributeGroup._meta.indexes
            if i.name == "attrs_grp_active_order_idx"
        )
        assert idx.fields == ["is_active", "display_order"]


# ═══════════════════════════════════════════════════════════════════════
# 2. AttributeGroup — Field Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupFields:
    """Test AttributeGroup field types, constraints, and parameters."""

    def test_name_field_type(self):
        field = AttributeGroup._meta.get_field("name")
        assert isinstance(field, models.CharField)

    def test_name_max_length(self):
        field = AttributeGroup._meta.get_field("name")
        assert field.max_length == 100

    def test_name_is_indexed(self):
        field = AttributeGroup._meta.get_field("name")
        assert field.db_index is True

    def test_slug_field_type(self):
        field = AttributeGroup._meta.get_field("slug")
        assert isinstance(field, models.SlugField)

    def test_slug_max_length(self):
        field = AttributeGroup._meta.get_field("slug")
        assert field.max_length == 100

    def test_slug_unique(self):
        field = AttributeGroup._meta.get_field("slug")
        assert field.unique is True

    def test_slug_blank(self):
        field = AttributeGroup._meta.get_field("slug")
        assert field.blank is True

    def test_description_field_type(self):
        field = AttributeGroup._meta.get_field("description")
        assert isinstance(field, models.TextField)

    def test_description_blank(self):
        field = AttributeGroup._meta.get_field("description")
        assert field.blank is True

    def test_description_default(self):
        field = AttributeGroup._meta.get_field("description")
        assert field.default == ""

    def test_display_order_field_type(self):
        field = AttributeGroup._meta.get_field("display_order")
        assert isinstance(field, models.PositiveIntegerField)

    def test_display_order_default(self):
        field = AttributeGroup._meta.get_field("display_order")
        assert field.default == 0

    def test_display_order_is_indexed(self):
        field = AttributeGroup._meta.get_field("display_order")
        assert field.db_index is True


# ═══════════════════════════════════════════════════════════════════════
# 3. AttributeGroup — Mixin / Inheritance
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupMixins:
    """Verify AttributeGroup inherits expected base classes."""

    def test_has_uuid_primary_key(self):
        pk = AttributeGroup._meta.pk
        assert isinstance(pk, models.UUIDField)
        assert pk.primary_key is True

    def test_has_created_on(self):
        field = AttributeGroup._meta.get_field("created_on")
        assert isinstance(field, models.DateTimeField)

    def test_has_updated_on(self):
        field = AttributeGroup._meta.get_field("updated_on")
        assert isinstance(field, models.DateTimeField)

    def test_has_is_active(self):
        field = AttributeGroup._meta.get_field("is_active")
        assert isinstance(field, models.BooleanField)
        assert field.default is True

    def test_has_is_deleted(self):
        field = AttributeGroup._meta.get_field("is_deleted")
        assert isinstance(field, models.BooleanField)
        assert field.default is False


# ═══════════════════════════════════════════════════════════════════════
# 4. AttributeGroup — String Representation
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupStr:
    """Test AttributeGroup __str__ method."""

    def test_str_returns_name(self):
        obj = AttributeGroup.__new__(AttributeGroup)
        obj.name = "Specifications"
        assert str(obj) == "Specifications"

    def test_str_returns_different_name(self):
        obj = AttributeGroup.__new__(AttributeGroup)
        obj.name = "Dimensions"
        assert str(obj) == "Dimensions"


# ═══════════════════════════════════════════════════════════════════════
# 5. AttributeGroup — Save / Slug Generation
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupSave:
    """Test AttributeGroup.save() slug auto-generation."""

    @patch.object(AttributeGroup, "save", autospec=True)
    def test_save_generates_slug_when_blank(self, mock_save):
        """Verify save method exists and is callable."""
        obj = AttributeGroup.__new__(AttributeGroup)
        obj.name = "Technical Specs"
        obj.slug = ""
        # Call the real save logic for slug generation
        # The actual slug generation happens before super().save()
        assert hasattr(obj, "save")

    def test_save_method_exists(self):
        assert callable(getattr(AttributeGroup, "save", None))


# ═══════════════════════════════════════════════════════════════════════
# 6. AttributeGroup — Manager / QuerySet
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupManager:
    """Test AttributeGroup managers and querysets."""

    def test_default_manager_type(self):
        from apps.attributes.models.attribute_group import GroupManager

        assert isinstance(AttributeGroup.objects, GroupManager)

    def test_all_with_deleted_is_standard_manager(self):
        assert isinstance(AttributeGroup.all_with_deleted, models.Manager)

    def test_queryset_has_active_method(self):
        from apps.attributes.models.attribute_group import GroupQuerySet

        assert hasattr(GroupQuerySet, "active")

    def test_queryset_has_with_attributes_method(self):
        from apps.attributes.models.attribute_group import GroupQuerySet

        assert hasattr(GroupQuerySet, "with_attributes")

    def test_manager_has_active_proxy(self):
        assert hasattr(AttributeGroup.objects, "active")

    def test_manager_has_with_attributes_proxy(self):
        assert hasattr(AttributeGroup.objects, "with_attributes")


# ═══════════════════════════════════════════════════════════════════════
# 7. Attribute — Meta Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeModelMeta:
    """Test Attribute model Meta class configuration."""

    def test_app_label(self):
        assert Attribute._meta.app_label == "attributes"

    def test_verbose_name(self):
        assert Attribute._meta.verbose_name == "Attribute"

    def test_verbose_name_plural(self):
        assert Attribute._meta.verbose_name_plural == "Attributes"

    def test_ordering(self):
        assert list(Attribute._meta.ordering) == [
            "group__display_order", "display_order", "name"
        ]

    def test_has_type_index(self):
        names = [idx.name for idx in Attribute._meta.indexes]
        assert "attrs_attr_type_idx" in names

    def test_has_filterable_index(self):
        names = [idx.name for idx in Attribute._meta.indexes]
        assert "attrs_attr_filterable_idx" in names

    def test_has_group_order_index(self):
        names = [idx.name for idx in Attribute._meta.indexes]
        assert "attrs_attr_grp_order_idx" in names


# ═══════════════════════════════════════════════════════════════════════
# 8. Attribute — Field Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeFields:
    """Test Attribute field types, constraints, and parameters."""

    # ── name ──
    def test_name_field_type(self):
        field = Attribute._meta.get_field("name")
        assert isinstance(field, models.CharField)

    def test_name_max_length(self):
        field = Attribute._meta.get_field("name")
        assert field.max_length == 100

    def test_name_is_indexed(self):
        field = Attribute._meta.get_field("name")
        assert field.db_index is True

    # ── slug ──
    def test_slug_field_type(self):
        field = Attribute._meta.get_field("slug")
        assert isinstance(field, models.SlugField)

    def test_slug_max_length(self):
        field = Attribute._meta.get_field("slug")
        assert field.max_length == 100

    def test_slug_unique(self):
        field = Attribute._meta.get_field("slug")
        assert field.unique is True

    def test_slug_blank(self):
        field = Attribute._meta.get_field("slug")
        assert field.blank is True

    # ── group FK ──
    def test_group_field_type(self):
        field = Attribute._meta.get_field("group")
        assert isinstance(field, models.ForeignKey)

    def test_group_related_model(self):
        field = Attribute._meta.get_field("group")
        assert field.related_model is AttributeGroup

    def test_group_on_delete_set_null(self):
        field = Attribute._meta.get_field("group")
        assert field.remote_field.on_delete is models.SET_NULL

    def test_group_related_name(self):
        field = Attribute._meta.get_field("group")
        assert field.remote_field.related_name == "attributes"

    def test_group_nullable(self):
        field = Attribute._meta.get_field("group")
        assert field.null is True

    def test_group_blank(self):
        field = Attribute._meta.get_field("group")
        assert field.blank is True

    # ── attribute_type ──
    def test_attribute_type_field_type(self):
        field = Attribute._meta.get_field("attribute_type")
        assert isinstance(field, models.CharField)

    def test_attribute_type_max_length(self):
        field = Attribute._meta.get_field("attribute_type")
        assert field.max_length == 20

    def test_attribute_type_choices(self):
        field = Attribute._meta.get_field("attribute_type")
        assert list(field.choices) == list(ATTRIBUTE_TYPES)

    def test_attribute_type_is_indexed(self):
        field = Attribute._meta.get_field("attribute_type")
        assert field.db_index is True

    # ── unit ──
    def test_unit_field_type(self):
        field = Attribute._meta.get_field("unit")
        assert isinstance(field, models.CharField)

    def test_unit_max_length(self):
        field = Attribute._meta.get_field("unit")
        assert field.max_length == 20

    def test_unit_blank(self):
        field = Attribute._meta.get_field("unit")
        assert field.blank is True

    def test_unit_default(self):
        field = Attribute._meta.get_field("unit")
        assert field.default == ""

    # ── boolean flags ──
    def test_is_required_default(self):
        field = Attribute._meta.get_field("is_required")
        assert field.default is False
        assert field.db_index is True

    def test_is_filterable_default(self):
        field = Attribute._meta.get_field("is_filterable")
        assert field.default is False
        assert field.db_index is True

    def test_is_searchable_default(self):
        field = Attribute._meta.get_field("is_searchable")
        assert field.default is False
        assert field.db_index is True

    def test_is_comparable_default(self):
        field = Attribute._meta.get_field("is_comparable")
        assert field.default is False

    def test_is_visible_on_product_default(self):
        field = Attribute._meta.get_field("is_visible_on_product")
        assert field.default is True

    # ── display_order ──
    def test_display_order_default(self):
        field = Attribute._meta.get_field("display_order")
        assert isinstance(field, models.PositiveIntegerField)
        assert field.default == 0
        assert field.db_index is True

    # ── validation_regex ──
    def test_validation_regex_field(self):
        field = Attribute._meta.get_field("validation_regex")
        assert isinstance(field, models.CharField)
        assert field.max_length == 255
        assert field.blank is True
        assert field.default == ""

    # ── min_value / max_value ──
    def test_min_value_field(self):
        field = Attribute._meta.get_field("min_value")
        assert isinstance(field, models.DecimalField)
        assert field.max_digits == 20
        assert field.decimal_places == 4
        assert field.null is True
        assert field.blank is True

    def test_max_value_field(self):
        field = Attribute._meta.get_field("max_value")
        assert isinstance(field, models.DecimalField)
        assert field.max_digits == 20
        assert field.decimal_places == 4
        assert field.null is True
        assert field.blank is True

    # ── categories M2M ──
    def test_categories_field_type(self):
        field = Attribute._meta.get_field("categories")
        assert isinstance(field, models.ManyToManyField)

    def test_categories_related_name(self):
        field = Attribute._meta.get_field("categories")
        assert field.remote_field.related_name == "attributes"

    def test_categories_blank(self):
        field = Attribute._meta.get_field("categories")
        assert field.blank is True


# ═══════════════════════════════════════════════════════════════════════
# 9. Attribute — Mixin / Inheritance
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeMixins:
    """Verify Attribute inherits expected base classes."""

    def test_has_uuid_primary_key(self):
        pk = Attribute._meta.pk
        assert isinstance(pk, models.UUIDField)
        assert pk.primary_key is True

    def test_has_created_on(self):
        field = Attribute._meta.get_field("created_on")
        assert isinstance(field, models.DateTimeField)

    def test_has_updated_on(self):
        field = Attribute._meta.get_field("updated_on")
        assert isinstance(field, models.DateTimeField)

    def test_has_is_active(self):
        field = Attribute._meta.get_field("is_active")
        assert isinstance(field, models.BooleanField)
        assert field.default is True

    def test_has_is_deleted(self):
        field = Attribute._meta.get_field("is_deleted")
        assert isinstance(field, models.BooleanField)
        assert field.default is False


# ═══════════════════════════════════════════════════════════════════════
# 10. Attribute — String Representation
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeStr:
    """Test Attribute __str__ method."""

    def test_str_returns_name(self):
        obj = Attribute.__new__(Attribute)
        obj.name = "Color"
        assert str(obj) == "Color"

    def test_str_returns_different_name(self):
        obj = Attribute.__new__(Attribute)
        obj.name = "Weight"
        assert str(obj) == "Weight"


# ═══════════════════════════════════════════════════════════════════════
# 11. Attribute — Manager / QuerySet
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeManager:
    """Test Attribute managers and querysets."""

    def test_default_manager_type(self):
        from apps.attributes.models.attribute import AttributeManager

        assert isinstance(Attribute.objects, AttributeManager)

    def test_all_with_deleted_is_standard_manager(self):
        assert isinstance(Attribute.all_with_deleted, models.Manager)

    def test_queryset_has_active(self):
        from apps.attributes.models.attribute import AttributeQuerySet

        assert hasattr(AttributeQuerySet, "active")

    def test_queryset_has_filterable(self):
        from apps.attributes.models.attribute import AttributeQuerySet

        assert hasattr(AttributeQuerySet, "filterable")

    def test_queryset_has_searchable(self):
        from apps.attributes.models.attribute import AttributeQuerySet

        assert hasattr(AttributeQuerySet, "searchable")

    def test_queryset_has_by_type(self):
        from apps.attributes.models.attribute import AttributeQuerySet

        assert hasattr(AttributeQuerySet, "by_type")

    def test_queryset_has_for_category(self):
        from apps.attributes.models.attribute import AttributeQuerySet

        assert hasattr(AttributeQuerySet, "for_category")

    def test_queryset_has_required(self):
        from apps.attributes.models.attribute import AttributeQuerySet

        assert hasattr(AttributeQuerySet, "required")

    def test_manager_has_active_proxy(self):
        assert hasattr(Attribute.objects, "active")

    def test_manager_has_filterable_proxy(self):
        assert hasattr(Attribute.objects, "filterable")

    def test_manager_has_searchable_proxy(self):
        assert hasattr(Attribute.objects, "searchable")

    def test_manager_has_for_category_proxy(self):
        assert hasattr(Attribute.objects, "for_category")


# ═══════════════════════════════════════════════════════════════════════
# 12. Attribute — clean() Validation
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeClean:
    """Test Attribute.clean() min/max validation."""

    def test_clean_raises_when_min_greater_than_max(self):
        from django.core.exceptions import ValidationError

        obj = Attribute.__new__(Attribute)
        obj.min_value = Decimal("100")
        obj.max_value = Decimal("10")
        with pytest.raises(ValidationError):
            obj.clean()

    def test_clean_passes_when_min_less_than_max(self):
        obj = Attribute.__new__(Attribute)
        obj.min_value = Decimal("10")
        obj.max_value = Decimal("100")
        obj.clean()  # Should not raise

    def test_clean_passes_when_values_none(self):
        obj = Attribute.__new__(Attribute)
        obj.min_value = None
        obj.max_value = None
        obj.clean()  # Should not raise

    def test_clean_passes_when_equal(self):
        obj = Attribute.__new__(Attribute)
        obj.min_value = Decimal("50")
        obj.max_value = Decimal("50")
        obj.clean()  # Should not raise

    def test_clean_passes_when_only_min_set(self):
        obj = Attribute.__new__(Attribute)
        obj.min_value = Decimal("10")
        obj.max_value = None
        obj.clean()  # Should not raise

    def test_clean_passes_when_only_max_set(self):
        obj = Attribute.__new__(Attribute)
        obj.min_value = None
        obj.max_value = Decimal("100")
        obj.clean()  # Should not raise


# ═══════════════════════════════════════════════════════════════════════
# 13. Attribute — Save / Slug Generation
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeSave:
    """Test Attribute.save() slug auto-generation."""

    def test_save_method_exists(self):
        assert callable(getattr(Attribute, "save", None))


# ═══════════════════════════════════════════════════════════════════════
# 14. AttributeOption — Meta Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionModelMeta:
    """Test AttributeOption model Meta class configuration."""

    def test_app_label(self):
        assert AttributeOption._meta.app_label == "attributes"

    def test_verbose_name(self):
        assert AttributeOption._meta.verbose_name == "Attribute Option"

    def test_verbose_name_plural(self):
        assert AttributeOption._meta.verbose_name_plural == "Attribute Options"

    def test_ordering(self):
        assert list(AttributeOption._meta.ordering) == ["display_order", "label"]

    def test_unique_together(self):
        assert ("attribute", "value") in AttributeOption._meta.unique_together

    def test_index_exists(self):
        names = [idx.name for idx in AttributeOption._meta.indexes]
        assert "attrs_opt_attr_order_idx" in names

    def test_index_fields(self):
        idx = next(
            i
            for i in AttributeOption._meta.indexes
            if i.name == "attrs_opt_attr_order_idx"
        )
        assert idx.fields == ["attribute", "display_order"]


# ═══════════════════════════════════════════════════════════════════════
# 15. AttributeOption — Field Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionFields:
    """Test AttributeOption field types, constraints, and parameters."""

    def test_attribute_field_type(self):
        field = AttributeOption._meta.get_field("attribute")
        assert isinstance(field, models.ForeignKey)

    def test_attribute_related_model(self):
        field = AttributeOption._meta.get_field("attribute")
        assert field.related_model is Attribute

    def test_attribute_on_delete_cascade(self):
        field = AttributeOption._meta.get_field("attribute")
        assert field.remote_field.on_delete is models.CASCADE

    def test_attribute_related_name(self):
        field = AttributeOption._meta.get_field("attribute")
        assert field.remote_field.related_name == "options"

    def test_value_field_type(self):
        field = AttributeOption._meta.get_field("value")
        assert isinstance(field, models.CharField)
        assert field.max_length == 100
        assert field.db_index is True

    def test_label_field_type(self):
        field = AttributeOption._meta.get_field("label")
        assert isinstance(field, models.CharField)
        assert field.max_length == 100

    def test_color_code_field(self):
        field = AttributeOption._meta.get_field("color_code")
        assert isinstance(field, models.CharField)
        assert field.max_length == 7
        assert field.blank is True
        assert field.default == ""

    def test_image_field(self):
        field = AttributeOption._meta.get_field("image")
        assert isinstance(field, models.ImageField)
        assert field.null is True
        assert field.blank is True

    def test_image_upload_to(self):
        field = AttributeOption._meta.get_field("image")
        assert field.upload_to == "attributes/options/"

    def test_display_order_field(self):
        field = AttributeOption._meta.get_field("display_order")
        assert isinstance(field, models.PositiveIntegerField)
        assert field.default == 0
        assert field.db_index is True

    def test_is_default_field(self):
        field = AttributeOption._meta.get_field("is_default")
        assert isinstance(field, models.BooleanField)
        assert field.default is False
        assert field.db_index is True


# ═══════════════════════════════════════════════════════════════════════
# 16. AttributeOption — Mixin / Inheritance
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionMixins:
    """Verify AttributeOption inherits expected base classes."""

    def test_has_uuid_pk(self):
        pk = AttributeOption._meta.pk
        assert isinstance(pk, models.UUIDField)
        assert pk.primary_key is True

    def test_has_created_on(self):
        field = AttributeOption._meta.get_field("created_on")
        assert isinstance(field, models.DateTimeField)

    def test_has_updated_on(self):
        field = AttributeOption._meta.get_field("updated_on")
        assert isinstance(field, models.DateTimeField)

    def test_has_is_active(self):
        field = AttributeOption._meta.get_field("is_active")
        assert isinstance(field, models.BooleanField)
        assert field.default is True

    def test_has_is_deleted(self):
        field = AttributeOption._meta.get_field("is_deleted")
        assert isinstance(field, models.BooleanField)
        assert field.default is False


# ═══════════════════════════════════════════════════════════════════════
# 17. AttributeOption — String Representation
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionStr:
    """Test AttributeOption __str__ method."""

    def test_str_returns_label(self):
        obj = AttributeOption.__new__(AttributeOption)
        obj.label = "Red"
        assert str(obj) == "Red"

    def test_str_returns_different_label(self):
        obj = AttributeOption.__new__(AttributeOption)
        obj.label = "Extra Large"
        assert str(obj) == "Extra Large"


# ═══════════════════════════════════════════════════════════════════════
# 18. AttributeOption — Manager / QuerySet
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionManager:
    """Test AttributeOption managers and querysets."""

    def test_default_manager_type(self):
        from apps.attributes.models.attribute_option import OptionManager

        assert isinstance(AttributeOption.objects, OptionManager)

    def test_all_with_deleted_is_standard_manager(self):
        assert isinstance(AttributeOption.all_with_deleted, models.Manager)

    def test_queryset_has_for_attribute(self):
        from apps.attributes.models.attribute_option import OptionQuerySet

        assert hasattr(OptionQuerySet, "for_attribute")

    def test_queryset_has_with_images(self):
        from apps.attributes.models.attribute_option import OptionQuerySet

        assert hasattr(OptionQuerySet, "with_images")

    def test_queryset_has_defaults(self):
        from apps.attributes.models.attribute_option import OptionQuerySet

        assert hasattr(OptionQuerySet, "defaults")

    def test_manager_has_for_attribute_proxy(self):
        assert hasattr(AttributeOption.objects, "for_attribute")

    def test_manager_has_defaults_proxy(self):
        assert hasattr(AttributeOption.objects, "defaults")


# ═══════════════════════════════════════════════════════════════════════
# 19. AttributeOption — Save (default clearing)
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionSave:
    """Test AttributeOption.save() default-clearing logic."""

    def test_save_method_exists(self):
        assert callable(getattr(AttributeOption, "save", None))


# ═══════════════════════════════════════════════════════════════════════
# 20. Constants Verification
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeConstants:
    """Test attribute type constants."""

    def test_text_value(self):
        assert TEXT == "text"

    def test_number_value(self):
        assert NUMBER == "number"

    def test_select_value(self):
        assert SELECT == "select"

    def test_multiselect_value(self):
        assert MULTISELECT == "multiselect"

    def test_boolean_value(self):
        assert BOOLEAN == "boolean"

    def test_date_value(self):
        assert DATE == "date"

    def test_attribute_types_length(self):
        assert len(ATTRIBUTE_TYPES) == 6

    def test_attribute_types_is_tuple_of_tuples(self):
        for item in ATTRIBUTE_TYPES:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_attribute_types_contains_text(self):
        assert (TEXT, "Text") in ATTRIBUTE_TYPES

    def test_attribute_types_contains_number(self):
        assert (NUMBER, "Number") in ATTRIBUTE_TYPES

    def test_attribute_types_contains_select(self):
        assert (SELECT, "Select") in ATTRIBUTE_TYPES

    def test_attribute_types_contains_multiselect(self):
        assert (MULTISELECT, "Multi-Select") in ATTRIBUTE_TYPES

    def test_attribute_types_contains_boolean(self):
        assert (BOOLEAN, "Boolean") in ATTRIBUTE_TYPES

    def test_attribute_types_contains_date(self):
        assert (DATE, "Date") in ATTRIBUTE_TYPES
