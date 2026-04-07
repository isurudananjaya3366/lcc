"""
Attribute API tests.

Tests for Attribute serializers, ViewSets, and URL routing.
All tests are database-free — they use mocks and plain Python objects.
"""

import uuid
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory

from apps.attributes.constants import ATTRIBUTE_TYPES, MULTISELECT, SELECT

factory = APIRequestFactory()


# ═══════════════════════════════════════════════════════════════════════
# 1. AttributeGroupSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupSerializer:
    """Test AttributeGroupSerializer configuration."""

    def test_meta_model(self):
        from apps.attributes.models import AttributeGroup
        from apps.attributes.serializers import AttributeGroupSerializer

        assert AttributeGroupSerializer.Meta.model is AttributeGroup

    def test_meta_fields(self):
        from apps.attributes.serializers import AttributeGroupSerializer

        expected = [
            "id",
            "name",
            "slug",
            "description",
            "display_order",
            "is_active",
            "attribute_count",
            "created_on",
            "updated_on",
        ]
        assert AttributeGroupSerializer.Meta.fields == expected

    def test_read_only_fields(self):
        from apps.attributes.serializers import AttributeGroupSerializer

        assert AttributeGroupSerializer.Meta.read_only_fields == [
            "id",
            "slug",
            "created_on",
            "updated_on",
        ]

    def test_inherits_model_serializer(self):
        from apps.attributes.serializers import AttributeGroupSerializer

        assert issubclass(
            AttributeGroupSerializer, drf_serializers.ModelSerializer
        )

    def test_attribute_count_is_method_field(self):
        from apps.attributes.serializers import AttributeGroupSerializer

        serializer = AttributeGroupSerializer()
        assert isinstance(
            serializer.fields["attribute_count"],
            drf_serializers.SerializerMethodField,
        )

    def test_get_attribute_count_calls_count(self):
        from apps.attributes.serializers import AttributeGroupSerializer

        obj = MagicMock()
        obj.attributes.count.return_value = 5
        serializer = AttributeGroupSerializer()
        result = serializer.get_attribute_count(obj)
        assert result == 5
        obj.attributes.count.assert_called_once()

    def test_fields_count(self):
        from apps.attributes.serializers import AttributeGroupSerializer

        assert len(AttributeGroupSerializer.Meta.fields) == 9


# ═══════════════════════════════════════════════════════════════════════
# 2. AttributeOptionSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionSerializer:
    """Test AttributeOptionSerializer configuration."""

    def test_meta_model(self):
        from apps.attributes.models import AttributeOption
        from apps.attributes.serializers import AttributeOptionSerializer

        assert AttributeOptionSerializer.Meta.model is AttributeOption

    def test_meta_fields(self):
        from apps.attributes.serializers import AttributeOptionSerializer

        expected = [
            "id",
            "attribute",
            "attribute_name",
            "value",
            "label",
            "color_code",
            "image",
            "display_order",
            "is_default",
            "created_on",
            "updated_on",
        ]
        assert AttributeOptionSerializer.Meta.fields == expected

    def test_read_only_fields(self):
        from apps.attributes.serializers import AttributeOptionSerializer

        assert AttributeOptionSerializer.Meta.read_only_fields == [
            "id",
            "created_on",
            "updated_on",
        ]

    def test_attribute_name_source(self):
        from apps.attributes.serializers import AttributeOptionSerializer

        serializer = AttributeOptionSerializer()
        field = serializer.fields["attribute_name"]
        assert field.source == "attribute.name"
        assert field.read_only is True

    def test_inherits_model_serializer(self):
        from apps.attributes.serializers import AttributeOptionSerializer

        assert issubclass(
            AttributeOptionSerializer, drf_serializers.ModelSerializer
        )

    def test_fields_count(self):
        from apps.attributes.serializers import AttributeOptionSerializer

        assert len(AttributeOptionSerializer.Meta.fields) == 11


# ═══════════════════════════════════════════════════════════════════════
# 3. AttributeListSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeListSerializer:
    """Test AttributeListSerializer configuration."""

    def test_meta_model(self):
        from apps.attributes.models import Attribute
        from apps.attributes.serializers import AttributeListSerializer

        assert AttributeListSerializer.Meta.model is Attribute

    def test_meta_fields(self):
        from apps.attributes.serializers import AttributeListSerializer

        expected = [
            "id",
            "name",
            "slug",
            "attribute_type",
            "type_display",
            "group",
            "group_name",
            "is_required",
            "is_filterable",
            "is_searchable",
            "display_order",
            "option_count",
        ]
        assert AttributeListSerializer.Meta.fields == expected

    def test_read_only_fields(self):
        from apps.attributes.serializers import AttributeListSerializer

        assert AttributeListSerializer.Meta.read_only_fields == ["id", "slug"]

    def test_group_name_source(self):
        from apps.attributes.serializers import AttributeListSerializer

        serializer = AttributeListSerializer()
        field = serializer.fields["group_name"]
        assert field.source == "group.name"
        assert field.read_only is True

    def test_type_display_source(self):
        from apps.attributes.serializers import AttributeListSerializer

        serializer = AttributeListSerializer()
        field = serializer.fields["type_display"]
        assert field.source == "get_attribute_type_display"
        assert field.read_only is True

    def test_option_count_is_method_field(self):
        from apps.attributes.serializers import AttributeListSerializer

        serializer = AttributeListSerializer()
        assert isinstance(
            serializer.fields["option_count"],
            drf_serializers.SerializerMethodField,
        )

    def test_get_option_count_for_select(self):
        from apps.attributes.serializers import AttributeListSerializer

        obj = MagicMock()
        obj.attribute_type = SELECT
        obj.options.count.return_value = 3
        serializer = AttributeListSerializer()
        assert serializer.get_option_count(obj) == 3

    def test_get_option_count_for_multiselect(self):
        from apps.attributes.serializers import AttributeListSerializer

        obj = MagicMock()
        obj.attribute_type = MULTISELECT
        obj.options.count.return_value = 5
        serializer = AttributeListSerializer()
        assert serializer.get_option_count(obj) == 5

    def test_get_option_count_for_text_returns_none(self):
        from apps.attributes.serializers import AttributeListSerializer

        obj = MagicMock()
        obj.attribute_type = "text"
        serializer = AttributeListSerializer()
        assert serializer.get_option_count(obj) is None

    def test_get_option_count_for_boolean_returns_none(self):
        from apps.attributes.serializers import AttributeListSerializer

        obj = MagicMock()
        obj.attribute_type = "boolean"
        serializer = AttributeListSerializer()
        assert serializer.get_option_count(obj) is None

    def test_get_option_count_for_number_returns_none(self):
        from apps.attributes.serializers import AttributeListSerializer

        obj = MagicMock()
        obj.attribute_type = "number"
        serializer = AttributeListSerializer()
        assert serializer.get_option_count(obj) is None

    def test_fields_count(self):
        from apps.attributes.serializers import AttributeListSerializer

        assert len(AttributeListSerializer.Meta.fields) == 12

    def test_inherits_model_serializer(self):
        from apps.attributes.serializers import AttributeListSerializer

        assert issubclass(
            AttributeListSerializer, drf_serializers.ModelSerializer
        )


# ═══════════════════════════════════════════════════════════════════════
# 4. AttributeSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeSerializer:
    """Test AttributeSerializer configuration."""

    def test_meta_model(self):
        from apps.attributes.models import Attribute
        from apps.attributes.serializers import AttributeSerializer

        assert AttributeSerializer.Meta.model is Attribute

    def test_meta_fields_include_categories(self):
        from apps.attributes.serializers import AttributeSerializer

        assert "categories" in AttributeSerializer.Meta.fields

    def test_meta_fields_include_is_active(self):
        from apps.attributes.serializers import AttributeSerializer

        assert "is_active" in AttributeSerializer.Meta.fields

    def test_meta_fields_include_timestamps(self):
        from apps.attributes.serializers import AttributeSerializer

        assert "created_on" in AttributeSerializer.Meta.fields
        assert "updated_on" in AttributeSerializer.Meta.fields

    def test_meta_fields_include_validation(self):
        from apps.attributes.serializers import AttributeSerializer

        assert "validation_regex" in AttributeSerializer.Meta.fields
        assert "min_value" in AttributeSerializer.Meta.fields
        assert "max_value" in AttributeSerializer.Meta.fields

    def test_meta_fields_include_flags(self):
        from apps.attributes.serializers import AttributeSerializer

        fields = AttributeSerializer.Meta.fields
        assert "is_required" in fields
        assert "is_filterable" in fields
        assert "is_searchable" in fields
        assert "is_comparable" in fields
        assert "is_visible_on_product" in fields

    def test_read_only_fields(self):
        from apps.attributes.serializers import AttributeSerializer

        assert AttributeSerializer.Meta.read_only_fields == [
            "id",
            "slug",
            "created_on",
            "updated_on",
        ]

    def test_group_name_source(self):
        from apps.attributes.serializers import AttributeSerializer

        serializer = AttributeSerializer()
        field = serializer.fields["group_name"]
        assert field.source == "group.name"
        assert field.read_only is True

    def test_type_display_source(self):
        from apps.attributes.serializers import AttributeSerializer

        serializer = AttributeSerializer()
        field = serializer.fields["type_display"]
        assert field.source == "get_attribute_type_display"
        assert field.read_only is True

    def test_validate_min_max_raises_on_invalid(self):
        from apps.attributes.serializers import AttributeSerializer

        serializer = AttributeSerializer()
        with pytest.raises(drf_serializers.ValidationError):
            serializer.validate(
                {
                    "attribute_type": "number",
                    "min_value": 100,
                    "max_value": 10,
                }
            )

    def test_validate_min_max_passes_when_valid(self):
        from apps.attributes.serializers import AttributeSerializer

        serializer = AttributeSerializer()
        data = serializer.validate(
            {
                "attribute_type": "number",
                "min_value": 10,
                "max_value": 100,
                "unit": "kg",
            }
        )
        assert data["min_value"] == 10
        assert data["max_value"] == 100

    def test_validate_passes_when_no_min_max(self):
        from apps.attributes.serializers import AttributeSerializer

        serializer = AttributeSerializer()
        data = serializer.validate({"attribute_type": "text"})
        assert data["attribute_type"] == "text"

    def test_validate_number_without_unit_raises(self):
        from apps.attributes.serializers import AttributeSerializer

        serializer = AttributeSerializer()
        with pytest.raises(drf_serializers.ValidationError):
            serializer.validate({"attribute_type": "number", "unit": ""})

    def test_validate_number_with_unit_passes(self):
        from apps.attributes.serializers import AttributeSerializer

        serializer = AttributeSerializer()
        data = serializer.validate({"attribute_type": "number", "unit": "kg"})
        assert data["unit"] == "kg"

    def test_validate_text_without_unit_passes(self):
        from apps.attributes.serializers import AttributeSerializer

        serializer = AttributeSerializer()
        data = serializer.validate({"attribute_type": "text", "unit": ""})
        assert data["attribute_type"] == "text"

    def test_inherits_model_serializer(self):
        from apps.attributes.serializers import AttributeSerializer

        assert issubclass(
            AttributeSerializer, drf_serializers.ModelSerializer
        )


# ═══════════════════════════════════════════════════════════════════════
# 5. AttributeDetailSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeDetailSerializer:
    """Test AttributeDetailSerializer configuration."""

    def test_meta_model(self):
        from apps.attributes.models import Attribute
        from apps.attributes.serializers import AttributeDetailSerializer

        assert AttributeDetailSerializer.Meta.model is Attribute

    def test_options_in_fields(self):
        from apps.attributes.serializers import AttributeDetailSerializer

        assert "options" in AttributeDetailSerializer.Meta.fields

    def test_option_count_in_fields(self):
        from apps.attributes.serializers import AttributeDetailSerializer

        assert "option_count" in AttributeDetailSerializer.Meta.fields

    def test_group_id_in_fields(self):
        from apps.attributes.serializers import AttributeDetailSerializer

        assert "group_id" in AttributeDetailSerializer.Meta.fields

    def test_group_is_nested_serializer(self):
        from apps.attributes.serializers import (
            AttributeDetailSerializer,
            AttributeGroupSerializer,
        )

        serializer = AttributeDetailSerializer()
        group_field = serializer.fields["group"]
        assert isinstance(group_field, AttributeGroupSerializer)
        assert group_field.read_only is True

    def test_options_is_nested_serializer(self):
        from apps.attributes.serializers import (
            AttributeDetailSerializer,
            AttributeOptionSerializer,
        )

        serializer = AttributeDetailSerializer()
        options_field = serializer.fields["options"]
        assert options_field.child.__class__ is AttributeOptionSerializer
        assert options_field.read_only is True

    def test_group_id_is_write_only(self):
        from apps.attributes.serializers import AttributeDetailSerializer

        serializer = AttributeDetailSerializer()
        field = serializer.fields["group_id"]
        assert field.write_only is True

    def test_get_option_count_calls_count(self):
        from apps.attributes.serializers import AttributeDetailSerializer

        obj = MagicMock()
        obj.options.count.return_value = 4
        serializer = AttributeDetailSerializer()
        assert serializer.get_option_count(obj) == 4

    def test_type_display_in_fields(self):
        from apps.attributes.serializers import AttributeDetailSerializer

        assert "type_display" in AttributeDetailSerializer.Meta.fields

    def test_read_only_fields(self):
        from apps.attributes.serializers import AttributeDetailSerializer

        assert AttributeDetailSerializer.Meta.read_only_fields == [
            "id",
            "slug",
            "created_on",
            "updated_on",
        ]

    def test_inherits_model_serializer(self):
        from apps.attributes.serializers import AttributeDetailSerializer

        assert issubclass(
            AttributeDetailSerializer, drf_serializers.ModelSerializer
        )

    def test_categories_in_fields(self):
        from apps.attributes.serializers import AttributeDetailSerializer

        assert "categories" in AttributeDetailSerializer.Meta.fields


# ═══════════════════════════════════════════════════════════════════════
# 6. AttributeGroupViewSet — Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupViewSetConfig:
    """Test AttributeGroupViewSet configuration."""

    def test_serializer_class(self):
        from apps.attributes.serializers import AttributeGroupSerializer
        from apps.attributes.views import AttributeGroupViewSet

        assert AttributeGroupViewSet.serializer_class is AttributeGroupSerializer

    def test_permission_classes(self):
        from apps.attributes.views import AttributeGroupViewSet

        assert IsAuthenticated in AttributeGroupViewSet.permission_classes

    def test_filter_backends(self):
        from apps.attributes.views import AttributeGroupViewSet

        assert SearchFilter in AttributeGroupViewSet.filter_backends
        assert OrderingFilter in AttributeGroupViewSet.filter_backends

    def test_search_fields(self):
        from apps.attributes.views import AttributeGroupViewSet

        assert "name" in AttributeGroupViewSet.search_fields
        assert "description" in AttributeGroupViewSet.search_fields

    def test_ordering_fields(self):
        from apps.attributes.views import AttributeGroupViewSet

        assert "display_order" in AttributeGroupViewSet.ordering_fields
        assert "name" in AttributeGroupViewSet.ordering_fields
        assert "created_on" in AttributeGroupViewSet.ordering_fields

    def test_default_ordering(self):
        from apps.attributes.views import AttributeGroupViewSet

        assert AttributeGroupViewSet.ordering == ["display_order", "name"]

    def test_is_model_viewset(self):
        from rest_framework.viewsets import ModelViewSet

        from apps.attributes.views import AttributeGroupViewSet

        assert issubclass(AttributeGroupViewSet, ModelViewSet)

    def test_has_get_queryset(self):
        from apps.attributes.views import AttributeGroupViewSet

        assert hasattr(AttributeGroupViewSet, "get_queryset")


# ═══════════════════════════════════════════════════════════════════════
# 7. AttributeViewSet — Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeViewSetConfig:
    """Test AttributeViewSet configuration."""

    def test_permission_classes(self):
        from apps.attributes.views import AttributeViewSet

        assert IsAuthenticated in AttributeViewSet.permission_classes

    def test_filter_backends(self):
        from apps.attributes.views import AttributeViewSet

        assert DjangoFilterBackend in AttributeViewSet.filter_backends
        assert SearchFilter in AttributeViewSet.filter_backends
        assert OrderingFilter in AttributeViewSet.filter_backends

    def test_filterset_fields(self):
        from apps.attributes.views import AttributeViewSet

        assert "attribute_type" in AttributeViewSet.filterset_fields
        assert "is_required" in AttributeViewSet.filterset_fields
        assert "is_filterable" in AttributeViewSet.filterset_fields
        assert "group" in AttributeViewSet.filterset_fields

    def test_search_fields(self):
        from apps.attributes.views import AttributeViewSet

        assert "name" in AttributeViewSet.search_fields

    def test_ordering_fields(self):
        from apps.attributes.views import AttributeViewSet

        assert "display_order" in AttributeViewSet.ordering_fields
        assert "name" in AttributeViewSet.ordering_fields
        assert "created_on" in AttributeViewSet.ordering_fields

    def test_default_ordering(self):
        from apps.attributes.views import AttributeViewSet

        assert AttributeViewSet.ordering == [
            "group__display_order", "display_order", "name"
        ]

    def test_get_serializer_class_list(self):
        from apps.attributes.serializers import AttributeListSerializer
        from apps.attributes.views import AttributeViewSet

        view = AttributeViewSet()
        view.action = "list"
        assert view.get_serializer_class() is AttributeListSerializer

    def test_get_serializer_class_retrieve(self):
        from apps.attributes.serializers import AttributeDetailSerializer
        from apps.attributes.views import AttributeViewSet

        view = AttributeViewSet()
        view.action = "retrieve"
        assert view.get_serializer_class() is AttributeDetailSerializer

    def test_get_serializer_class_create(self):
        from apps.attributes.serializers import AttributeSerializer
        from apps.attributes.views import AttributeViewSet

        view = AttributeViewSet()
        view.action = "create"
        assert view.get_serializer_class() is AttributeSerializer

    def test_get_serializer_class_update(self):
        from apps.attributes.serializers import AttributeSerializer
        from apps.attributes.views import AttributeViewSet

        view = AttributeViewSet()
        view.action = "update"
        assert view.get_serializer_class() is AttributeSerializer

    def test_get_serializer_class_partial_update(self):
        from apps.attributes.serializers import AttributeSerializer
        from apps.attributes.views import AttributeViewSet

        view = AttributeViewSet()
        view.action = "partial_update"
        assert view.get_serializer_class() is AttributeSerializer

    def test_has_by_category_action(self):
        from apps.attributes.views import AttributeViewSet

        assert hasattr(AttributeViewSet, "by_category")

    def test_has_filterable_action(self):
        from apps.attributes.views import AttributeViewSet

        assert hasattr(AttributeViewSet, "filterable")

    def test_by_category_url_path(self):
        from apps.attributes.views import AttributeViewSet

        action_func = getattr(AttributeViewSet, "by_category")
        assert action_func.url_path == "by-category"

    def test_filterable_url_path(self):
        from apps.attributes.views import AttributeViewSet

        action_func = getattr(AttributeViewSet, "filterable")
        assert action_func.url_path == "filterable"

    def test_by_category_is_get_only(self):
        from apps.attributes.views import AttributeViewSet

        action_func = getattr(AttributeViewSet, "by_category")
        assert action_func.mapping == {"get": "by_category"}

    def test_filterable_is_get_only(self):
        from apps.attributes.views import AttributeViewSet

        action_func = getattr(AttributeViewSet, "filterable")
        assert action_func.mapping == {"get": "filterable"}

    def test_is_model_viewset(self):
        from rest_framework.viewsets import ModelViewSet

        from apps.attributes.views import AttributeViewSet

        assert issubclass(AttributeViewSet, ModelViewSet)

    def test_has_get_queryset(self):
        from apps.attributes.views import AttributeViewSet

        assert hasattr(AttributeViewSet, "get_queryset")


# ═══════════════════════════════════════════════════════════════════════
# 8. AttributeOptionViewSet — Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeOptionViewSetConfig:
    """Test AttributeOptionViewSet configuration."""

    def test_serializer_class(self):
        from apps.attributes.serializers import AttributeOptionSerializer
        from apps.attributes.views import AttributeOptionViewSet

        assert (
            AttributeOptionViewSet.serializer_class is AttributeOptionSerializer
        )

    def test_permission_classes(self):
        from apps.attributes.views import AttributeOptionViewSet

        assert IsAuthenticated in AttributeOptionViewSet.permission_classes

    def test_filter_backends(self):
        from apps.attributes.views import AttributeOptionViewSet

        assert DjangoFilterBackend in AttributeOptionViewSet.filter_backends
        assert OrderingFilter in AttributeOptionViewSet.filter_backends

    def test_filterset_fields(self):
        from apps.attributes.views import AttributeOptionViewSet

        assert "attribute" in AttributeOptionViewSet.filterset_fields
        assert "is_default" in AttributeOptionViewSet.filterset_fields

    def test_ordering_fields(self):
        from apps.attributes.views import AttributeOptionViewSet

        assert "display_order" in AttributeOptionViewSet.ordering_fields
        assert "label" in AttributeOptionViewSet.ordering_fields

    def test_default_ordering(self):
        from apps.attributes.views import AttributeOptionViewSet

        assert AttributeOptionViewSet.ordering == ["display_order", "label"]

    def test_is_model_viewset(self):
        from rest_framework.viewsets import ModelViewSet

        from apps.attributes.views import AttributeOptionViewSet

        assert issubclass(AttributeOptionViewSet, ModelViewSet)

    def test_has_get_queryset(self):
        from apps.attributes.views import AttributeOptionViewSet

        assert hasattr(AttributeOptionViewSet, "get_queryset")


# ═══════════════════════════════════════════════════════════════════════
# 9. URL Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeURLConfiguration:
    """Test attributes URL configuration."""

    def test_app_name(self):
        from apps.attributes import urls

        assert urls.app_name == "attributes"

    def test_urlpatterns_not_empty(self):
        from apps.attributes import urls

        assert len(urls.urlpatterns) > 0

    def test_attribute_groups_route_registered(self):
        from apps.attributes import urls

        patterns = [str(p.pattern) for p in urls.urlpatterns]
        assert any("attribute-groups" in p for p in patterns)

    def test_attributes_route_registered(self):
        from apps.attributes import urls

        patterns = [str(p.pattern) for p in urls.urlpatterns]
        assert any(
            p.startswith("attributes") or "attributes/" in p
            for p in patterns
            if "attribute-groups" not in p and "attribute-options" not in p
        )

    def test_attribute_options_route_registered(self):
        from apps.attributes import urls

        patterns = [str(p.pattern) for p in urls.urlpatterns]
        assert any("attribute-options" in p for p in patterns)

    def test_uses_default_router(self):
        from apps.attributes import urls

        assert hasattr(urls, "router")

    def test_router_has_registered_viewsets(self):
        from apps.attributes import urls

        registered = [r[0] for r in urls.router.registry]
        assert "attribute-groups" in registered
        assert "attributes" in registered
        assert "attribute-options" in registered


# ═══════════════════════════════════════════════════════════════════════
# 10. Admin Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestAttributeGroupAdminConfig:
    """Test AttributeGroupAdmin configuration."""

    def test_registered(self):
        from django.contrib import admin

        from apps.attributes.models import AttributeGroup

        assert admin.site.is_registered(AttributeGroup)

    def test_list_display(self):
        from apps.attributes.admin import AttributeGroupAdmin

        assert "name" in AttributeGroupAdmin.list_display
        assert "slug" in AttributeGroupAdmin.list_display
        assert "display_order" in AttributeGroupAdmin.list_display
        assert "is_active" in AttributeGroupAdmin.list_display
        assert "attribute_count" in AttributeGroupAdmin.list_display
        assert "created_on" in AttributeGroupAdmin.list_display

    def test_list_filter(self):
        from apps.attributes.admin import AttributeGroupAdmin

        assert "is_active" in AttributeGroupAdmin.list_filter
        assert "created_on" in AttributeGroupAdmin.list_filter

    def test_search_fields(self):
        from apps.attributes.admin import AttributeGroupAdmin

        assert "name" in AttributeGroupAdmin.search_fields
        assert "description" in AttributeGroupAdmin.search_fields

    def test_prepopulated_fields(self):
        from apps.attributes.admin import AttributeGroupAdmin

        assert AttributeGroupAdmin.prepopulated_fields == {"slug": ("name",)}

    def test_attribute_count_method(self):
        from apps.attributes.admin import AttributeGroupAdmin

        admin_instance = AttributeGroupAdmin(MagicMock(), MagicMock())
        obj = MagicMock()
        obj.attributes.count.return_value = 3
        assert admin_instance.attribute_count(obj) == 3

    def test_readonly_fields(self):
        from apps.attributes.admin import AttributeGroupAdmin

        assert "created_on" in AttributeGroupAdmin.readonly_fields
        assert "updated_on" in AttributeGroupAdmin.readonly_fields


class TestAttributeAdminConfig:
    """Test AttributeAdmin configuration."""

    def test_registered(self):
        from django.contrib import admin

        from apps.attributes.models import Attribute

        assert admin.site.is_registered(Attribute)

    def test_list_display(self):
        from apps.attributes.admin import AttributeAdmin

        assert "name" in AttributeAdmin.list_display
        assert "group" in AttributeAdmin.list_display
        assert "attribute_type" in AttributeAdmin.list_display
        assert "is_required" in AttributeAdmin.list_display
        assert "is_filterable" in AttributeAdmin.list_display
        assert "is_visible_on_product" in AttributeAdmin.list_display
        assert "display_order" in AttributeAdmin.list_display
        assert "option_count" in AttributeAdmin.list_display

    def test_list_filter(self):
        from apps.attributes.admin import AttributeAdmin

        assert "attribute_type" in AttributeAdmin.list_filter
        assert "is_required" in AttributeAdmin.list_filter
        assert "is_filterable" in AttributeAdmin.list_filter
        assert "is_searchable" in AttributeAdmin.list_filter
        assert "is_comparable" in AttributeAdmin.list_filter
        assert "is_visible_on_product" in AttributeAdmin.list_filter

    def test_filter_horizontal(self):
        from apps.attributes.admin import AttributeAdmin

        assert "categories" in AttributeAdmin.filter_horizontal

    def test_has_inlines(self):
        from apps.attributes.admin import AttributeAdmin, AttributeOptionInline

        assert AttributeOptionInline in AttributeAdmin.inlines

    def test_prepopulated_fields(self):
        from apps.attributes.admin import AttributeAdmin

        assert AttributeAdmin.prepopulated_fields == {"slug": ("name",)}

    def test_option_count_method(self):
        from apps.attributes.admin import AttributeAdmin

        admin_instance = AttributeAdmin(MagicMock(), MagicMock())
        obj = MagicMock()
        obj.options.count.return_value = 7
        assert admin_instance.option_count(obj) == 7

    def test_fieldsets_defined(self):
        from apps.attributes.admin import AttributeAdmin

        assert AttributeAdmin.fieldsets is not None
        assert len(AttributeAdmin.fieldsets) >= 4

    def test_fieldsets_has_basic_info(self):
        from apps.attributes.admin import AttributeAdmin

        section_names = [fs[0] for fs in AttributeAdmin.fieldsets]
        assert "Basic Information" in section_names

    def test_fieldsets_has_display_settings(self):
        from apps.attributes.admin import AttributeAdmin

        section_names = [fs[0] for fs in AttributeAdmin.fieldsets]
        assert "Display Settings" in section_names

    def test_fieldsets_has_validation_rules(self):
        from apps.attributes.admin import AttributeAdmin

        section_names = [fs[0] for fs in AttributeAdmin.fieldsets]
        assert "Validation Rules" in section_names

    def test_fieldsets_has_categories(self):
        from apps.attributes.admin import AttributeAdmin

        section_names = [fs[0] for fs in AttributeAdmin.fieldsets]
        assert "Categories" in section_names

    def test_readonly_fields(self):
        from apps.attributes.admin import AttributeAdmin

        assert "created_on" in AttributeAdmin.readonly_fields
        assert "updated_on" in AttributeAdmin.readonly_fields


class TestAttributeOptionAdminConfig:
    """Test AttributeOptionAdmin configuration."""

    def test_registered(self):
        from django.contrib import admin

        from apps.attributes.models import AttributeOption

        assert admin.site.is_registered(AttributeOption)

    def test_list_display(self):
        from apps.attributes.admin import AttributeOptionAdmin

        assert "label" in AttributeOptionAdmin.list_display
        assert "value" in AttributeOptionAdmin.list_display
        assert "attribute" in AttributeOptionAdmin.list_display
        assert "color_code" in AttributeOptionAdmin.list_display
        assert "display_order" in AttributeOptionAdmin.list_display
        assert "is_default" in AttributeOptionAdmin.list_display
        assert "is_active" in AttributeOptionAdmin.list_display

    def test_list_filter(self):
        from apps.attributes.admin import AttributeOptionAdmin

        assert "is_default" in AttributeOptionAdmin.list_filter
        assert "is_active" in AttributeOptionAdmin.list_filter


class TestAttributeOptionInlineConfig:
    """Test AttributeOptionInline configuration."""

    def test_model(self):
        from apps.attributes.admin import AttributeOptionInline
        from apps.attributes.models import AttributeOption

        assert AttributeOptionInline.model is AttributeOption

    def test_extra(self):
        from apps.attributes.admin import AttributeOptionInline

        assert AttributeOptionInline.extra == 3

    def test_fields(self):
        from apps.attributes.admin import AttributeOptionInline

        assert "value" in AttributeOptionInline.fields
        assert "label" in AttributeOptionInline.fields
        assert "color_code" in AttributeOptionInline.fields
        assert "display_order" in AttributeOptionInline.fields
        assert "is_default" in AttributeOptionInline.fields

    def test_is_tabular_inline(self):
        from django.contrib import admin
        from apps.attributes.admin import AttributeOptionInline

        assert issubclass(AttributeOptionInline, admin.TabularInline)

    def test_ordering(self):
        from apps.attributes.admin import AttributeOptionInline

        assert AttributeOptionInline.ordering == ["display_order", "label"]
