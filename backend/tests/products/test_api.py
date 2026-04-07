"""
Category API tests.

Tests for Category serializers, ViewSet, and URL routing.
All tests are database-free — they use mocks and plain Python objects
so they can run in the *unit* test suite.
"""

import uuid
from unittest.mock import MagicMock, PropertyMock, patch, call

import pytest
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_category(**kwargs):
    """Return a MagicMock that looks like a Category instance."""
    defaults = {
        "pk": uuid.uuid4(),
        "id": uuid.uuid4(),
        "name": "Electronics",
        "slug": "electronics",
        "icon": "fas fa-laptop",
        "parent": None,
        "is_active": True,
        "display_order": 0,
        "level": 0,
        "description": "Electronic devices",
        "image": None,
        "seo_title": "",
        "seo_description": "",
        "seo_keywords": "",
    }
    defaults.update(kwargs)
    mock = MagicMock(**defaults)
    mock.pk = defaults["pk"]
    mock.id = defaults["id"]
    return mock


# ═══════════════════════════════════════════════════════════════════════
# CategoryListSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryListSerializer:
    """Test CategoryListSerializer field configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import CategoryListSerializer
        from apps.products.models import Category

        assert CategoryListSerializer.Meta.model is Category

    def test_meta_fields(self):
        from apps.products.api.serializers import CategoryListSerializer

        expected = [
            "id",
            "name",
            "slug",
            "icon",
            "parent",
            "is_active",
            "display_order",
            "level",
        ]
        assert CategoryListSerializer.Meta.fields == expected

    def test_meta_read_only_fields(self):
        from apps.products.api.serializers import CategoryListSerializer

        assert CategoryListSerializer.Meta.read_only_fields == ["id"]

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import CategoryListSerializer

        assert issubclass(CategoryListSerializer, drf_serializers.ModelSerializer)

    def test_fields_count(self):
        from apps.products.api.serializers import CategoryListSerializer

        assert len(CategoryListSerializer.Meta.fields) == 8

    def test_id_in_fields(self):
        from apps.products.api.serializers import CategoryListSerializer

        assert "id" in CategoryListSerializer.Meta.fields

    def test_level_in_fields(self):
        from apps.products.api.serializers import CategoryListSerializer

        assert "level" in CategoryListSerializer.Meta.fields

    def test_parent_in_fields(self):
        from apps.products.api.serializers import CategoryListSerializer

        assert "parent" in CategoryListSerializer.Meta.fields


# ═══════════════════════════════════════════════════════════════════════
# CategorySerializer (base)
# ═══════════════════════════════════════════════════════════════════════


class TestCategorySerializer:
    """Test CategorySerializer (base) configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import CategorySerializer
        from apps.products.models import Category

        assert CategorySerializer.Meta.model is Category

    def test_fields_include_parent_name(self):
        from apps.products.api.serializers import CategorySerializer

        assert "parent_name" in CategorySerializer.Meta.fields

    def test_fields_include_children_count(self):
        from apps.products.api.serializers import CategorySerializer

        assert "children_count" in CategorySerializer.Meta.fields

    def test_fields_include_timestamps(self):
        from apps.products.api.serializers import CategorySerializer

        assert "created_on" in CategorySerializer.Meta.fields
        assert "updated_on" in CategorySerializer.Meta.fields

    def test_read_only_fields(self):
        from apps.products.api.serializers import CategorySerializer

        assert CategorySerializer.Meta.read_only_fields == [
            "id",
            "created_on",
            "updated_on",
        ]

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import CategorySerializer

        assert issubclass(CategorySerializer, drf_serializers.ModelSerializer)

    def test_parent_name_field_is_declared(self):
        from apps.products.api.serializers import CategorySerializer

        serializer = CategorySerializer()
        assert "parent_name" in serializer.fields

    def test_children_count_field_is_declared(self):
        from apps.products.api.serializers import CategorySerializer

        serializer = CategorySerializer()
        assert "children_count" in serializer.fields

    def test_parent_name_source(self):
        from apps.products.api.serializers import CategorySerializer

        field = CategorySerializer().fields["parent_name"]
        assert field.source == "parent.name"

    def test_parent_name_is_read_only(self):
        from apps.products.api.serializers import CategorySerializer

        field = CategorySerializer().fields["parent_name"]
        assert field.read_only is True

    def test_children_count_is_read_only(self):
        from apps.products.api.serializers import CategorySerializer

        field = CategorySerializer().fields["children_count"]
        assert field.read_only is True

    def test_description_in_fields(self):
        from apps.products.api.serializers import CategorySerializer

        assert "description" in CategorySerializer.Meta.fields

    def test_image_in_fields(self):
        from apps.products.api.serializers import CategorySerializer

        assert "image" in CategorySerializer.Meta.fields

    def test_icon_in_fields(self):
        from apps.products.api.serializers import CategorySerializer

        assert "icon" in CategorySerializer.Meta.fields

    def test_fields_count(self):
        from apps.products.api.serializers import CategorySerializer

        assert len(CategorySerializer.Meta.fields) == 13


# ═══════════════════════════════════════════════════════════════════════
# CategoryDetailSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryDetailSerializer:
    """Test CategoryDetailSerializer configuration."""

    def test_inherits_category_serializer(self):
        from apps.products.api.serializers import (
            CategoryDetailSerializer,
            CategorySerializer,
        )

        assert issubclass(CategoryDetailSerializer, CategorySerializer)

    def test_seo_title_in_fields(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        assert "seo_title" in CategoryDetailSerializer.Meta.fields

    def test_seo_description_in_fields(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        assert "seo_description" in CategoryDetailSerializer.Meta.fields

    def test_seo_keywords_in_fields(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        assert "seo_keywords" in CategoryDetailSerializer.Meta.fields

    def test_is_root_in_fields(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        assert "is_root" in CategoryDetailSerializer.Meta.fields

    def test_is_leaf_in_fields(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        assert "is_leaf" in CategoryDetailSerializer.Meta.fields

    def test_descendants_count_in_fields(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        assert "descendants_count" in CategoryDetailSerializer.Meta.fields

    def test_full_path_in_fields(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        assert "full_path" in CategoryDetailSerializer.Meta.fields

    def test_children_in_fields(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        assert "children" in CategoryDetailSerializer.Meta.fields

    def test_meta_extends_parent_fields(self):
        from apps.products.api.serializers import (
            CategoryDetailSerializer,
            CategorySerializer,
        )

        # Detail fields should be a superset of base fields
        for field in CategorySerializer.Meta.fields:
            assert field in CategoryDetailSerializer.Meta.fields

    def test_get_full_path_calls_obj_method(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        obj = MagicMock()
        obj.get_full_path.return_value = "Electronics > Phones"
        serializer = CategoryDetailSerializer()
        result = serializer.get_full_path(obj)
        obj.get_full_path.assert_called_once()
        assert result == "Electronics > Phones"

    def test_is_root_field_is_read_only(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        serializer = CategoryDetailSerializer()
        assert serializer.fields["is_root"].read_only is True

    def test_is_leaf_field_is_read_only(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        serializer = CategoryDetailSerializer()
        assert serializer.fields["is_leaf"].read_only is True

    def test_descendants_count_field_is_read_only(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        serializer = CategoryDetailSerializer()
        assert serializer.fields["descendants_count"].read_only is True

    def test_children_field_is_read_only(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        serializer = CategoryDetailSerializer()
        assert serializer.fields["children"].read_only is True

    def test_children_field_is_many(self):
        from apps.products.api.serializers import CategoryDetailSerializer

        serializer = CategoryDetailSerializer()
        assert serializer.fields["children"].many is True

    def test_detail_has_more_fields_than_base(self):
        from apps.products.api.serializers import (
            CategoryDetailSerializer,
            CategorySerializer,
        )

        assert len(CategoryDetailSerializer.Meta.fields) > len(
            CategorySerializer.Meta.fields
        )


# ═══════════════════════════════════════════════════════════════════════
# CategoryTreeSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryTreeSerializer:
    """Test CategoryTreeSerializer recursive structure."""

    def test_meta_model(self):
        from apps.products.api.serializers import CategoryTreeSerializer
        from apps.products.models import Category

        assert CategoryTreeSerializer.Meta.model is Category

    def test_meta_fields(self):
        from apps.products.api.serializers import CategoryTreeSerializer

        expected = [
            "id",
            "name",
            "slug",
            "icon",
            "is_active",
            "display_order",
            "level",
            "children",
        ]
        assert CategoryTreeSerializer.Meta.fields == expected

    def test_children_is_serializer_method_field(self):
        from apps.products.api.serializers import CategoryTreeSerializer

        serializer = CategoryTreeSerializer()
        assert isinstance(
            serializer.fields["children"],
            drf_serializers.SerializerMethodField,
        )

    def test_get_children_calls_get_children(self):
        from apps.products.api.serializers import CategoryTreeSerializer

        obj = MagicMock()
        children_qs = MagicMock()
        obj.get_children.return_value = children_qs
        children_qs.filter.return_value = []

        serializer = CategoryTreeSerializer()
        serializer.get_children(obj)
        obj.get_children.assert_called_once()

    def test_get_children_filters_active(self):
        from apps.products.api.serializers import CategoryTreeSerializer

        obj = MagicMock()
        children_qs = MagicMock()
        obj.get_children.return_value = children_qs
        children_qs.filter.return_value = MagicMock(data=[])

        serializer = CategoryTreeSerializer()
        serializer.get_children(obj)
        children_qs.filter.assert_called_once_with(is_active=True)

    def test_fields_count(self):
        from apps.products.api.serializers import CategoryTreeSerializer

        assert len(CategoryTreeSerializer.Meta.fields) == 8

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import CategoryTreeSerializer

        assert issubclass(CategoryTreeSerializer, drf_serializers.ModelSerializer)

    def test_no_parent_in_fields(self):
        from apps.products.api.serializers import CategoryTreeSerializer

        assert "parent" not in CategoryTreeSerializer.Meta.fields


# ═══════════════════════════════════════════════════════════════════════
# CategoryCreateUpdateSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryCreateUpdateSerializer:
    """Test CategoryCreateUpdateSerializer validation."""

    def test_meta_model(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer
        from apps.products.models import Category

        assert CategoryCreateUpdateSerializer.Meta.model is Category

    def test_meta_fields(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        expected = [
            "name",
            "slug",
            "parent",
            "description",
            "image",
            "icon",
            "is_active",
            "display_order",
            "seo_title",
            "seo_description",
            "seo_keywords",
        ]
        assert CategoryCreateUpdateSerializer.Meta.fields == expected

    def test_slug_not_required(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        assert (
            CategoryCreateUpdateSerializer.Meta.extra_kwargs["slug"]["required"]
            is False
        )

    def test_slug_allow_blank(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        assert (
            CategoryCreateUpdateSerializer.Meta.extra_kwargs["slug"]["allow_blank"]
            is True
        )

    def test_validate_parent_self_reference_raises(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        cat_pk = uuid.uuid4()
        parent_mock = MagicMock()
        parent_mock.pk = cat_pk

        instance_mock = MagicMock()
        instance_mock.pk = cat_pk

        serializer = CategoryCreateUpdateSerializer()
        serializer.instance = instance_mock

        with pytest.raises(drf_serializers.ValidationError, match="own parent"):
            serializer.validate_parent(parent_mock)

    def test_validate_parent_descendant_raises(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        parent_mock = MagicMock()
        parent_mock.pk = uuid.uuid4()

        instance_mock = MagicMock()
        instance_mock.pk = uuid.uuid4()
        instance_mock.is_ancestor_of.return_value = True

        serializer = CategoryCreateUpdateSerializer()
        serializer.instance = instance_mock

        with pytest.raises(drf_serializers.ValidationError, match="descendant"):
            serializer.validate_parent(parent_mock)

    def test_validate_parent_valid_returns_value(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        parent_mock = MagicMock()
        parent_mock.pk = uuid.uuid4()

        instance_mock = MagicMock()
        instance_mock.pk = uuid.uuid4()
        instance_mock.is_ancestor_of.return_value = False

        serializer = CategoryCreateUpdateSerializer()
        serializer.instance = instance_mock

        result = serializer.validate_parent(parent_mock)
        assert result is parent_mock

    def test_validate_parent_none_is_ok(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        serializer = CategoryCreateUpdateSerializer()
        serializer.instance = MagicMock()

        result = serializer.validate_parent(None)
        assert result is None

    def test_validate_parent_no_instance_is_ok(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        parent_mock = MagicMock()
        parent_mock.pk = uuid.uuid4()

        serializer = CategoryCreateUpdateSerializer()
        serializer.instance = None

        result = serializer.validate_parent(parent_mock)
        assert result is parent_mock

    def test_validate_name_strips_whitespace(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        serializer = CategoryCreateUpdateSerializer()
        result = serializer.validate_name("  Electronics  ")
        assert result == "Electronics"

    def test_validate_name_blank_raises(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        serializer = CategoryCreateUpdateSerializer()
        with pytest.raises(drf_serializers.ValidationError, match="blank"):
            serializer.validate_name("   ")

    def test_validate_name_empty_raises(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        serializer = CategoryCreateUpdateSerializer()
        with pytest.raises(drf_serializers.ValidationError, match="blank"):
            serializer.validate_name("")

    @patch("apps.products.api.serializers.Category.objects")
    def test_generate_unique_slug_simple(self, mock_objects):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = False

        serializer = CategoryCreateUpdateSerializer()
        serializer.instance = None

        result = serializer._generate_unique_slug("Electronics")
        assert result == "electronics"

    @patch("apps.products.api.serializers.Category.objects")
    def test_generate_unique_slug_collision(self, mock_objects):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        # First call: slug exists; second call: unique
        mock_qs.exists.side_effect = [True, False]

        serializer = CategoryCreateUpdateSerializer()
        serializer.instance = None

        result = serializer._generate_unique_slug("Electronics")
        assert result == "electronics-2"

    @patch("apps.products.api.serializers.Category.objects")
    def test_generate_unique_slug_excludes_instance(self, mock_objects):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.exclude.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = False

        instance = MagicMock()
        instance.pk = uuid.uuid4()

        serializer = CategoryCreateUpdateSerializer()
        serializer.instance = instance

        serializer._generate_unique_slug("Electronics")
        mock_qs.exclude.assert_called_once_with(pk=instance.pk)

    @patch("apps.products.api.serializers.Category.objects")
    def test_generate_unique_slug_empty_name_falls_back(self, mock_objects):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = False

        serializer = CategoryCreateUpdateSerializer()
        serializer.instance = None

        # slugify("!!!") returns ""
        result = serializer._generate_unique_slug("!!!")
        assert result == "category"

    def test_create_autogenerates_slug(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        serializer = CategoryCreateUpdateSerializer()
        serializer._generate_unique_slug = MagicMock(return_value="electronics")

        with patch.object(
            drf_serializers.ModelSerializer, "create", return_value=MagicMock()
        ) as mock_super_create:
            serializer.create({"name": "Electronics", "slug": ""})
            # slug should now be auto-generated
            args = mock_super_create.call_args[0][0]
            assert args["slug"] == "electronics"

    def test_create_keeps_provided_slug(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        serializer = CategoryCreateUpdateSerializer()
        serializer._generate_unique_slug = MagicMock()

        with patch.object(
            drf_serializers.ModelSerializer, "create", return_value=MagicMock()
        ) as mock_super_create:
            serializer.create({"name": "Electronics", "slug": "custom-slug"})
            args = mock_super_create.call_args[0][0]
            assert args["slug"] == "custom-slug"
            serializer._generate_unique_slug.assert_not_called()

    def test_update_regenerates_slug_when_name_changed(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        instance = MagicMock()
        instance.name = "Old Name"

        serializer = CategoryCreateUpdateSerializer()
        serializer._generate_unique_slug = MagicMock(return_value="new-name")

        with patch.object(
            drf_serializers.ModelSerializer, "update", return_value=MagicMock()
        ) as mock_super_update:
            serializer.update(instance, {"name": "New Name", "slug": ""})
            args = mock_super_update.call_args[0][1]
            assert args["slug"] == "new-name"

    def test_update_keeps_slug_when_name_unchanged(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        instance = MagicMock()
        instance.name = "Electronics"

        serializer = CategoryCreateUpdateSerializer()
        serializer._generate_unique_slug = MagicMock()

        with patch.object(
            drf_serializers.ModelSerializer, "update", return_value=MagicMock()
        ):
            serializer.update(instance, {"name": "Electronics", "slug": ""})
            serializer._generate_unique_slug.assert_not_called()

    def test_update_keeps_provided_slug(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        instance = MagicMock()
        instance.name = "Old Name"

        serializer = CategoryCreateUpdateSerializer()
        serializer._generate_unique_slug = MagicMock()

        with patch.object(
            drf_serializers.ModelSerializer, "update", return_value=MagicMock()
        ) as mock_super_update:
            serializer.update(
                instance, {"name": "New Name", "slug": "explicit-slug"}
            )
            args = mock_super_update.call_args[0][1]
            assert args["slug"] == "explicit-slug"
            serializer._generate_unique_slug.assert_not_called()

    def test_id_not_in_fields(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        assert "id" not in CategoryCreateUpdateSerializer.Meta.fields

    def test_fields_count(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        assert len(CategoryCreateUpdateSerializer.Meta.fields) == 11


# ═══════════════════════════════════════════════════════════════════════
# CategoryViewSet — Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryViewSetConfiguration:
    """Test CategoryViewSet configuration."""

    def test_permission_classes(self):
        from apps.products.api.views import CategoryViewSet

        assert CategoryViewSet.permission_classes == [IsAuthenticated]

    def test_filter_backends(self):
        from django_filters.rest_framework import DjangoFilterBackend

        from apps.products.api.views import CategoryViewSet

        assert CategoryViewSet.filter_backends == [
            DjangoFilterBackend,
            SearchFilter,
            OrderingFilter,
        ]

    def test_search_fields(self):
        from apps.products.api.views import CategoryViewSet

        assert CategoryViewSet.search_fields == ["name", "description"]

    def test_ordering_fields(self):
        from apps.products.api.views import CategoryViewSet

        assert CategoryViewSet.ordering_fields == [
            "name",
            "display_order",
            "created_on",
        ]

    def test_ordering_default(self):
        from apps.products.api.views import CategoryViewSet

        assert CategoryViewSet.ordering == ["display_order", "name"]

    def test_inherits_model_viewset(self):
        from apps.products.api.views import CategoryViewSet
        from rest_framework.viewsets import ModelViewSet

        assert issubclass(CategoryViewSet, ModelViewSet)


# ═══════════════════════════════════════════════════════════════════════
# CategoryViewSet — Serializer Selection
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryViewSetSerializerSelection:
    """Test get_serializer_class returns correct serializer."""

    def test_list_returns_list_serializer(self):
        from apps.products.api.serializers import CategoryListSerializer
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.action = "list"
        assert view.get_serializer_class() is CategoryListSerializer

    def test_retrieve_returns_detail_serializer(self):
        from apps.products.api.serializers import CategoryDetailSerializer
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.action = "retrieve"
        assert view.get_serializer_class() is CategoryDetailSerializer

    def test_create_returns_create_update_serializer(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.action = "create"
        assert view.get_serializer_class() is CategoryCreateUpdateSerializer

    def test_update_returns_create_update_serializer(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.action = "update"
        assert view.get_serializer_class() is CategoryCreateUpdateSerializer

    def test_partial_update_returns_create_update_serializer(self):
        from apps.products.api.serializers import CategoryCreateUpdateSerializer
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.action = "partial_update"
        assert view.get_serializer_class() is CategoryCreateUpdateSerializer

    def test_tree_returns_tree_serializer(self):
        from apps.products.api.serializers import CategoryTreeSerializer
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.action = "tree"
        assert view.get_serializer_class() is CategoryTreeSerializer

    def test_destroy_returns_list_serializer_as_default(self):
        from apps.products.api.serializers import CategoryListSerializer
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.action = "destroy"
        assert view.get_serializer_class() is CategoryListSerializer

    def test_unknown_action_returns_list_serializer(self):
        from apps.products.api.serializers import CategoryListSerializer
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.action = "unknown_custom_action"
        assert view.get_serializer_class() is CategoryListSerializer


# ═══════════════════════════════════════════════════════════════════════
# CategoryViewSet — QuerySet filtering
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryViewSetQuerySet:
    """Test get_queryset and filterset configuration."""

    def _make_view(self, query_params=None):
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.request = MagicMock()
        view.request.query_params = query_params or {}
        view.kwargs = {}
        view.format_kwarg = None
        return view

    @patch("apps.products.api.views.Category.objects")
    def test_basic_queryset_selects_related_parent(self, mock_objects):
        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs

        view = self._make_view()
        view.get_queryset()
        mock_qs.select_related.assert_called_once_with("parent")

    def test_filterset_fields_include_parent(self):
        from apps.products.api.views import CategoryViewSet

        assert "parent" in CategoryViewSet.filterset_fields

    def test_filterset_fields_include_is_active(self):
        from apps.products.api.views import CategoryViewSet

        assert "is_active" in CategoryViewSet.filterset_fields

    @patch("apps.products.api.views.Category.objects")
    def test_queryset_starts_from_all(self, mock_objects):
        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs

        view = self._make_view()
        view.get_queryset()
        mock_objects.all.assert_called_once()

    @patch("apps.products.api.views.Category.objects")
    def test_no_manual_filter_calls_in_get_queryset(self, mock_objects):
        """Filtering is handled by DjangoFilterBackend, not manually."""
        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs

        view = self._make_view(query_params={"is_active": "true", "parent": ""})
        result = view.get_queryset()
        mock_qs.filter.assert_not_called()

    def test_django_filter_backend_in_filter_backends(self):
        from django_filters.rest_framework import DjangoFilterBackend

        from apps.products.api.views import CategoryViewSet

        assert DjangoFilterBackend in CategoryViewSet.filter_backends

    @patch("apps.products.api.views.Category.objects")
    def test_no_params_no_extra_filters(self, mock_objects):
        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.select_related.return_value = mock_qs

        view = self._make_view(query_params={})
        view.get_queryset()
        mock_qs.filter.assert_not_called()


# ═══════════════════════════════════════════════════════════════════════
# CategoryViewSet — Tree Action
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryTreeAction:
    """Test custom tree action."""

    @patch("apps.products.api.views.CategoryTreeSerializer")
    @patch("apps.products.api.views.Category.objects")
    def test_tree_default_active_only(self, mock_objects, mock_serializer):
        from apps.products.api.views import CategoryViewSet

        mock_qs = MagicMock()
        mock_objects.get_tree.return_value = mock_qs
        mock_serializer.return_value.data = []

        request = MagicMock()
        request.query_params = {}

        view = CategoryViewSet()
        view.request = request
        view.format_kwarg = None
        view.kwargs = {}

        response = view.tree(request)
        mock_objects.get_tree.assert_called_once_with(active_only=True)
        assert response.status_code == 200

    @patch("apps.products.api.views.CategoryTreeSerializer")
    @patch("apps.products.api.views.Category.objects")
    def test_tree_active_only_false(self, mock_objects, mock_serializer):
        from apps.products.api.views import CategoryViewSet

        mock_qs = MagicMock()
        mock_objects.get_tree.return_value = mock_qs
        mock_serializer.return_value.data = []

        request = MagicMock()
        request.query_params = {"active_only": "false"}

        view = CategoryViewSet()
        view.request = request
        view.format_kwarg = None
        view.kwargs = {}

        view.tree(request)
        mock_objects.get_tree.assert_called_once_with(active_only=False)

    @patch("apps.products.api.views.CategoryTreeSerializer")
    @patch("apps.products.api.views.Category.objects")
    def test_tree_active_only_zero(self, mock_objects, mock_serializer):
        from apps.products.api.views import CategoryViewSet

        mock_qs = MagicMock()
        mock_objects.get_tree.return_value = mock_qs
        mock_serializer.return_value.data = []

        request = MagicMock()
        request.query_params = {"active_only": "0"}

        view = CategoryViewSet()
        view.request = request
        view.format_kwarg = None
        view.kwargs = {}

        view.tree(request)
        mock_objects.get_tree.assert_called_once_with(active_only=False)

    @patch("apps.products.api.views.CategoryTreeSerializer")
    @patch("apps.products.api.views.Category.objects")
    def test_tree_returns_serialized_data(self, mock_objects, mock_serializer):
        from apps.products.api.views import CategoryViewSet

        mock_qs = MagicMock()
        mock_objects.get_tree.return_value = mock_qs
        mock_serializer.return_value.data = [{"id": "abc", "name": "Root"}]

        request = MagicMock()
        request.query_params = {}

        view = CategoryViewSet()
        view.request = request
        view.format_kwarg = None
        view.kwargs = {}

        response = view.tree(request)
        assert response.data == [{"id": "abc", "name": "Root"}]


# ═══════════════════════════════════════════════════════════════════════
# CategoryViewSet — Move Action
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryMoveAction:
    """Test custom move action."""

    def _make_view_and_request(self, data=None):
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.request = MagicMock()
        view.request.data = data or {}
        view.format_kwarg = None
        view.kwargs = {"pk": str(uuid.uuid4())}
        return view

    @patch("apps.products.api.views.Category.objects")
    def test_invalid_position_returns_400(self, mock_objects):
        view = self._make_view_and_request(
            {"target": None, "position": "invalid-pos"}
        )
        view.get_object = MagicMock(return_value=MagicMock())

        response = view.move(view.request, pk=view.kwargs["pk"])
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid position" in response.data["detail"]

    @patch("apps.products.api.views.Category.objects")
    def test_target_not_found_returns_404(self, mock_objects):
        from apps.products.models import Category

        mock_objects.get.side_effect = Category.DoesNotExist

        view = self._make_view_and_request(
            {"target": str(uuid.uuid4()), "position": "last-child"}
        )
        view.get_object = MagicMock(return_value=MagicMock())

        response = view.move(view.request, pk=view.kwargs["pk"])
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.data["detail"]

    @patch("apps.products.api.views.CategoryDetailSerializer")
    @patch("apps.products.api.views.Category.objects")
    def test_move_node_value_error_returns_400(
        self, mock_objects, mock_serializer
    ):
        target_mock = MagicMock()
        mock_objects.get.return_value = target_mock
        mock_objects.move_node.side_effect = ValueError("Cannot move node")

        view = self._make_view_and_request(
            {"target": str(uuid.uuid4()), "position": "last-child"}
        )
        view.get_object = MagicMock(return_value=MagicMock())

        response = view.move(view.request, pk=view.kwargs["pk"])
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot move node" in response.data["detail"]

    @patch("apps.products.api.views.CategoryDetailSerializer")
    @patch("apps.products.api.views.Category.objects")
    def test_successful_move_returns_200(self, mock_objects, mock_serializer):
        target_mock = MagicMock()
        mock_objects.get.return_value = target_mock
        mock_serializer.return_value.data = {"id": "abc", "name": "Moved"}

        view = self._make_view_and_request(
            {"target": str(uuid.uuid4()), "position": "first-child"}
        )
        view.get_object = MagicMock(return_value=MagicMock())

        response = view.move(view.request, pk=view.kwargs["pk"])
        assert response.status_code == 200

    @patch("apps.products.api.views.CategoryDetailSerializer")
    @patch("apps.products.api.views.Category.objects")
    def test_successful_move_returns_detail_serializer_data(
        self, mock_objects, mock_serializer
    ):
        target_mock = MagicMock()
        mock_objects.get.return_value = target_mock
        mock_serializer.return_value.data = {"id": "abc", "name": "Moved"}

        view = self._make_view_and_request(
            {"target": str(uuid.uuid4()), "position": "left"}
        )
        category = MagicMock()
        view.get_object = MagicMock(return_value=category)

        response = view.move(view.request, pk=view.kwargs["pk"])
        mock_serializer.assert_called_once_with(category)
        assert response.data == {"id": "abc", "name": "Moved"}

    @patch("apps.products.api.views.CategoryDetailSerializer")
    @patch("apps.products.api.views.Category.objects")
    def test_move_with_null_target_makes_root(
        self, mock_objects, mock_serializer
    ):
        mock_serializer.return_value.data = {"id": "abc"}

        view = self._make_view_and_request(
            {"target": None, "position": "last-child"}
        )
        category = MagicMock()
        view.get_object = MagicMock(return_value=category)

        response = view.move(view.request, pk=view.kwargs["pk"])
        mock_objects.move_node.assert_called_once_with(
            category, None, position="last-child"
        )
        assert response.status_code == 200

    def test_default_position_is_last_child(self):
        """When position is not provided, it defaults to 'last-child'."""
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        request = MagicMock()
        request.data = {"target": None}  # no position key
        view.request = request
        view.format_kwarg = None
        view.kwargs = {"pk": str(uuid.uuid4())}
        view.get_object = MagicMock(return_value=MagicMock())

        with patch("apps.products.api.views.Category.objects") as mock_obj:
            with patch("apps.products.api.views.CategoryDetailSerializer") as mock_ser:
                mock_ser.return_value.data = {}
                view.move(request, pk=view.kwargs["pk"])
                mock_obj.move_node.assert_called_once()
                call_kwargs = mock_obj.move_node.call_args
                assert call_kwargs[1]["position"] == "last-child"

    @patch("apps.products.api.views.Category.objects")
    def test_position_right_is_valid(self, mock_objects):
        """'right' is an accepted position value."""
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        request = MagicMock()
        request.data = {"target": None, "position": "right"}
        view.request = request
        view.format_kwarg = None
        view.kwargs = {"pk": str(uuid.uuid4())}
        view.get_object = MagicMock(return_value=MagicMock())

        with patch("apps.products.api.views.CategoryDetailSerializer") as mock_ser:
            mock_ser.return_value.data = {}
            response = view.move(request, pk=view.kwargs["pk"])
            assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════
# URL Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryURLConfiguration:
    """Test URL routing configuration."""

    def test_app_name(self):
        from apps.products.api import urls

        assert urls.app_name == "products"

    def test_router_is_default_router(self):
        from rest_framework.routers import DefaultRouter

        from apps.products.api.urls import router

        assert isinstance(router, DefaultRouter)

    def test_router_has_category_viewset(self):
        from apps.products.api.urls import router

        names = [r[0] for r in router.registry]
        assert "categories" in names

    def test_router_basename(self):
        from apps.products.api.urls import router

        basenames = [r[2] for r in router.registry]
        assert "category" in basenames

    def test_router_viewset_class(self):
        from apps.products.api.urls import router
        from apps.products.api.views import CategoryViewSet

        viewset_classes = [r[1] for r in router.registry]
        assert CategoryViewSet in viewset_classes

    def test_urlpatterns_equals_router_urls(self):
        from apps.products.api.urls import router, urlpatterns

        assert urlpatterns is router.urls

    def test_urlpatterns_not_empty(self):
        from apps.products.api.urls import urlpatterns

        assert len(urlpatterns) > 0

    def test_category_list_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "category-list" in url_names

    def test_category_detail_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "category-detail" in url_names

    def test_category_tree_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "category-tree" in url_names

    def test_category_move_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "category-move" in url_names


# ═══════════════════════════════════════════════════════════════════════
# Tenant Isolation (conceptual, mock-based)
# ═══════════════════════════════════════════════════════════════════════


class TestCategoryTenantIsolation:
    """Test tenant isolation concepts (mock-based)."""

    def test_viewset_uses_model_objects(self):
        """Queryset starts from Category.objects, which respects tenant schema."""
        from apps.products.api.views import CategoryViewSet

        view = CategoryViewSet()
        view.request = MagicMock()
        view.request.query_params = {}
        view.kwargs = {}
        view.format_kwarg = None

        with patch("apps.products.api.views.Category.objects") as mock_objects:
            mock_qs = MagicMock()
            mock_objects.all.return_value = mock_qs
            mock_qs.select_related.return_value = mock_qs
            view.get_queryset()
            mock_objects.all.assert_called_once()

    def test_tree_action_uses_model_objects(self):
        """Tree action also starts from Category.objects (tenant-aware)."""
        from apps.products.api.views import CategoryViewSet

        with patch("apps.products.api.views.Category.objects") as mock_objects:
            with patch("apps.products.api.views.CategoryTreeSerializer") as mock_ser:
                mock_qs = MagicMock()
                mock_objects.get_tree.return_value = mock_qs
                mock_ser.return_value.data = []

                request = MagicMock()
                request.query_params = {}
                view = CategoryViewSet()
                view.request = request
                view.format_kwarg = None
                view.kwargs = {}

                view.tree(request)
                mock_objects.get_tree.assert_called_once()

    def test_create_update_serializer_uses_model_objects(self):
        """Slug generation queries Category.objects (tenant-scoped)."""
        from apps.products.api.serializers import CategoryCreateUpdateSerializer

        with patch("apps.products.api.serializers.Category.objects") as mock_objects:
            mock_qs = MagicMock()
            mock_objects.all.return_value = mock_qs
            mock_qs.filter.return_value = mock_qs
            mock_qs.exists.return_value = False

            serializer = CategoryCreateUpdateSerializer()
            serializer.instance = None
            serializer._generate_unique_slug("Test")
            mock_objects.all.assert_called_once()

    def test_move_action_queries_model_objects(self):
        """Move action target lookup uses Category.objects (tenant-scoped)."""
        from apps.products.api.views import CategoryViewSet

        with patch("apps.products.api.views.Category.objects") as mock_objects:
            with patch(
                "apps.products.api.views.CategoryDetailSerializer"
            ) as mock_ser:
                target_id = str(uuid.uuid4())
                mock_objects.get.return_value = MagicMock()
                mock_ser.return_value.data = {}

                request = MagicMock()
                request.data = {"target": target_id, "position": "last-child"}

                view = CategoryViewSet()
                view.request = request
                view.format_kwarg = None
                view.kwargs = {"pk": str(uuid.uuid4())}
                view.get_object = MagicMock(return_value=MagicMock())

                view.move(request, pk=view.kwargs["pk"])
                mock_objects.get.assert_called_once_with(pk=target_id)
