"""
Variant API unit tests.

Tests for serializer Meta configurations, ViewSet attributes,
URL routing, and custom action endpoints.
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()


# ═══════════════════════════════════════════════════════════════════════
# VariantOptionTypeSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestVariantOptionTypeSerializer:
    """Test VariantOptionTypeSerializer meta configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import (
            VariantOptionTypeSerializer,
        )
        from apps.products.models import VariantOptionType

        assert VariantOptionTypeSerializer.Meta.model is VariantOptionType

    def test_meta_fields(self):
        from apps.products.api.serializers import (
            VariantOptionTypeSerializer,
        )

        expected = [
            "id",
            "name",
            "slug",
            "display_order",
            "is_color_swatch",
            "is_image_swatch",
            "is_active",
            "value_count",
            "created_on",
            "updated_on",
        ]
        assert VariantOptionTypeSerializer.Meta.fields == expected

    def test_meta_read_only_fields(self):
        from apps.products.api.serializers import (
            VariantOptionTypeSerializer,
        )

        ro = VariantOptionTypeSerializer.Meta.read_only_fields
        assert "id" in ro
        assert "slug" in ro
        assert "created_on" in ro
        assert "updated_on" in ro

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import (
            VariantOptionTypeSerializer,
        )

        assert issubclass(
            VariantOptionTypeSerializer, drf_serializers.ModelSerializer
        )

    def test_has_value_count_method_field(self):
        from apps.products.api.serializers import (
            VariantOptionTypeSerializer,
        )

        fields = VariantOptionTypeSerializer().fields
        assert "value_count" in fields


# ═══════════════════════════════════════════════════════════════════════
# VariantOptionValueSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestVariantOptionValueSerializer:
    """Test VariantOptionValueSerializer meta configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import (
            VariantOptionValueSerializer,
        )
        from apps.products.models import VariantOptionValue

        assert (
            VariantOptionValueSerializer.Meta.model is VariantOptionValue
        )

    def test_meta_fields(self):
        from apps.products.api.serializers import (
            VariantOptionValueSerializer,
        )

        expected = [
            "id",
            "option_type",
            "option_type_name",
            "value",
            "label",
            "color_code",
            "image",
            "display_order",
            "is_active",
            "swatch_preview",
            "created_on",
            "updated_on",
        ]
        assert VariantOptionValueSerializer.Meta.fields == expected

    def test_meta_read_only_fields(self):
        from apps.products.api.serializers import (
            VariantOptionValueSerializer,
        )

        ro = VariantOptionValueSerializer.Meta.read_only_fields
        assert "id" in ro
        assert "created_on" in ro

    def test_has_swatch_preview(self):
        from apps.products.api.serializers import (
            VariantOptionValueSerializer,
        )

        fields = VariantOptionValueSerializer().fields
        assert "swatch_preview" in fields


# ═══════════════════════════════════════════════════════════════════════
# ProductVariantOptionSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestProductVariantOptionSerializer:
    """Test ProductVariantOptionSerializer meta configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import (
            ProductVariantOptionSerializer,
        )
        from apps.products.models import ProductVariantOption

        assert (
            ProductVariantOptionSerializer.Meta.model
            is ProductVariantOption
        )

    def test_meta_fields(self):
        from apps.products.api.serializers import (
            ProductVariantOptionSerializer,
        )

        expected = ["id", "option_value", "option_value_id", "display_order"]
        assert ProductVariantOptionSerializer.Meta.fields == expected

    def test_has_write_only_option_value_id(self):
        from apps.products.api.serializers import (
            ProductVariantOptionSerializer,
        )

        fields = ProductVariantOptionSerializer().fields
        assert "option_value_id" in fields
        assert fields["option_value_id"].write_only is True


# ═══════════════════════════════════════════════════════════════════════
# ProductVariantListSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestProductVariantListSerializer:
    """Test ProductVariantListSerializer meta configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import (
            ProductVariantListSerializer,
        )
        from apps.products.models import ProductVariant

        assert ProductVariantListSerializer.Meta.model is ProductVariant

    def test_meta_fields(self):
        from apps.products.api.serializers import (
            ProductVariantListSerializer,
        )

        expected = [
            "id",
            "product",
            "product_name",
            "sku",
            "name",
            "option_summary",
            "sort_order",
            "is_active",
            "created_on",
        ]
        assert ProductVariantListSerializer.Meta.fields == expected

    def test_has_option_summary(self):
        from apps.products.api.serializers import (
            ProductVariantListSerializer,
        )

        fields = ProductVariantListSerializer().fields
        assert "option_summary" in fields

    def test_product_name_read_only(self):
        from apps.products.api.serializers import (
            ProductVariantListSerializer,
        )

        fields = ProductVariantListSerializer().fields
        assert fields["product_name"].read_only is True


# ═══════════════════════════════════════════════════════════════════════
# ProductVariantDetailSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestProductVariantDetailSerializer:
    """Test ProductVariantDetailSerializer meta configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import (
            ProductVariantDetailSerializer,
        )
        from apps.products.models import ProductVariant

        assert ProductVariantDetailSerializer.Meta.model is ProductVariant

    def test_meta_fields_include_overrides(self):
        from apps.products.api.serializers import (
            ProductVariantDetailSerializer,
        )

        fields = ProductVariantDetailSerializer.Meta.fields
        assert "weight_override" in fields
        assert "length_override" in fields
        assert "width_override" in fields
        assert "height_override" in fields
        assert "barcode" in fields
        assert "options" in fields

    def test_meta_fields_include_timestamps(self):
        from apps.products.api.serializers import (
            ProductVariantDetailSerializer,
        )

        fields = ProductVariantDetailSerializer.Meta.fields
        assert "created_on" in fields
        assert "updated_on" in fields


# ═══════════════════════════════════════════════════════════════════════
# ProductVariantCreateSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestProductVariantCreateSerializer:
    """Test ProductVariantCreateSerializer meta configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import (
            ProductVariantCreateSerializer,
        )
        from apps.products.models import ProductVariant

        assert ProductVariantCreateSerializer.Meta.model is ProductVariant

    def test_meta_fields(self):
        from apps.products.api.serializers import (
            ProductVariantCreateSerializer,
        )

        fields = ProductVariantCreateSerializer.Meta.fields
        assert "product" in fields
        assert "sku" in fields
        assert "option_value_ids" in fields

    def test_option_value_ids_write_only(self):
        from apps.products.api.serializers import (
            ProductVariantCreateSerializer,
        )

        fields = ProductVariantCreateSerializer().fields
        assert "option_value_ids" in fields
        assert fields["option_value_ids"].write_only is True


# ═══════════════════════════════════════════════════════════════════════
# BulkVariantCreateSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestBulkVariantCreateSerializer:
    """Test BulkVariantCreateSerializer fields."""

    def test_inherits_serializer(self):
        from apps.products.api.serializers import (
            BulkVariantCreateSerializer,
        )

        assert issubclass(
            BulkVariantCreateSerializer, drf_serializers.Serializer
        )

    def test_has_product_id_field(self):
        from apps.products.api.serializers import (
            BulkVariantCreateSerializer,
        )

        fields = BulkVariantCreateSerializer().fields
        assert "product_id" in fields


# ═══════════════════════════════════════════════════════════════════════
# ProductOptionConfigSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestProductOptionConfigSerializer:
    """Test ProductOptionConfigSerializer meta configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import (
            ProductOptionConfigSerializer,
        )
        from apps.products.models import ProductOptionConfig

        assert (
            ProductOptionConfigSerializer.Meta.model is ProductOptionConfig
        )

    def test_meta_fields(self):
        from apps.products.api.serializers import (
            ProductOptionConfigSerializer,
        )

        expected = [
            "id",
            "product",
            "option_type",
            "option_type_name",
            "display_order",
            "is_active",
            "created_on",
            "updated_on",
        ]
        assert ProductOptionConfigSerializer.Meta.fields == expected

    def test_meta_read_only_fields(self):
        from apps.products.api.serializers import (
            ProductOptionConfigSerializer,
        )

        ro = ProductOptionConfigSerializer.Meta.read_only_fields
        assert "id" in ro
        assert "created_on" in ro


# ═══════════════════════════════════════════════════════════════════════
# VariantOptionTypeViewSet
# ═══════════════════════════════════════════════════════════════════════


class TestVariantOptionTypeViewSet:
    """Test VariantOptionTypeViewSet configuration."""

    def test_serializer_class(self):
        from apps.products.api.serializers import (
            VariantOptionTypeSerializer,
        )
        from apps.products.api.views import VariantOptionTypeViewSet

        assert (
            VariantOptionTypeViewSet.serializer_class
            is VariantOptionTypeSerializer
        )

    def test_permission_classes(self):
        from apps.products.api.views import VariantOptionTypeViewSet

        assert IsAuthenticated in VariantOptionTypeViewSet.permission_classes

    def test_search_fields(self):
        from apps.products.api.views import VariantOptionTypeViewSet

        assert "name" in VariantOptionTypeViewSet.search_fields

    def test_ordering_fields(self):
        from apps.products.api.views import VariantOptionTypeViewSet

        assert "name" in VariantOptionTypeViewSet.ordering_fields
        assert "display_order" in VariantOptionTypeViewSet.ordering_fields

    def test_filterset_fields(self):
        from apps.products.api.views import VariantOptionTypeViewSet

        assert "is_active" in VariantOptionTypeViewSet.filterset_fields

    def test_filter_backends(self):
        from django_filters.rest_framework import DjangoFilterBackend

        from apps.products.api.views import VariantOptionTypeViewSet

        backends = VariantOptionTypeViewSet.filter_backends
        assert DjangoFilterBackend in backends
        assert SearchFilter in backends
        assert OrderingFilter in backends


# ═══════════════════════════════════════════════════════════════════════
# VariantOptionValueViewSet
# ═══════════════════════════════════════════════════════════════════════


class TestVariantOptionValueViewSet:
    """Test VariantOptionValueViewSet configuration."""

    def test_serializer_class(self):
        from apps.products.api.serializers import (
            VariantOptionValueSerializer,
        )
        from apps.products.api.views import VariantOptionValueViewSet

        assert (
            VariantOptionValueViewSet.serializer_class
            is VariantOptionValueSerializer
        )

    def test_permission_classes(self):
        from apps.products.api.views import VariantOptionValueViewSet

        assert (
            IsAuthenticated
            in VariantOptionValueViewSet.permission_classes
        )

    def test_filterset_fields(self):
        from apps.products.api.views import VariantOptionValueViewSet

        fields = VariantOptionValueViewSet.filterset_fields
        assert "option_type" in fields
        assert "is_active" in fields

    def test_search_fields(self):
        from apps.products.api.views import VariantOptionValueViewSet

        assert "value" in VariantOptionValueViewSet.search_fields
        assert "label" in VariantOptionValueViewSet.search_fields

    def test_has_by_type_action(self):
        from apps.products.api.views import VariantOptionValueViewSet

        assert hasattr(VariantOptionValueViewSet, "by_type")


# ═══════════════════════════════════════════════════════════════════════
# ProductVariantViewSet
# ═══════════════════════════════════════════════════════════════════════


class TestProductVariantViewSet:
    """Test ProductVariantViewSet configuration."""

    def test_permission_classes(self):
        from apps.products.api.views import ProductVariantViewSet

        assert IsAuthenticated in ProductVariantViewSet.permission_classes

    def test_filterset_fields(self):
        from apps.products.api.views import ProductVariantViewSet

        fields = ProductVariantViewSet.filterset_fields
        assert "product" in fields
        assert "is_active" in fields

    def test_search_fields(self):
        from apps.products.api.views import ProductVariantViewSet

        fields = ProductVariantViewSet.search_fields
        assert "sku" in fields
        assert "name" in fields

    def test_ordering_fields(self):
        from apps.products.api.views import ProductVariantViewSet

        fields = ProductVariantViewSet.ordering_fields
        assert "sku" in fields
        assert "sort_order" in fields

    def test_has_by_options_action(self):
        from apps.products.api.views import ProductVariantViewSet

        assert hasattr(ProductVariantViewSet, "by_options")

    def test_has_generate_variants_action(self):
        from apps.products.api.views import ProductVariantViewSet

        assert hasattr(ProductVariantViewSet, "generate_variants")

    def test_get_serializer_class_list(self):
        from apps.products.api.serializers import (
            ProductVariantListSerializer,
        )
        from apps.products.api.views import ProductVariantViewSet

        view = ProductVariantViewSet()
        view.action = "list"
        assert view.get_serializer_class() is ProductVariantListSerializer

    def test_get_serializer_class_retrieve(self):
        from apps.products.api.serializers import (
            ProductVariantDetailSerializer,
        )
        from apps.products.api.views import ProductVariantViewSet

        view = ProductVariantViewSet()
        view.action = "retrieve"
        assert (
            view.get_serializer_class() is ProductVariantDetailSerializer
        )

    def test_get_serializer_class_create(self):
        from apps.products.api.serializers import (
            ProductVariantCreateSerializer,
        )
        from apps.products.api.views import ProductVariantViewSet

        view = ProductVariantViewSet()
        view.action = "create"
        assert (
            view.get_serializer_class()
            is ProductVariantCreateSerializer
        )

    def test_get_serializer_class_generate(self):
        from apps.products.api.serializers import (
            BulkVariantCreateSerializer,
        )
        from apps.products.api.views import ProductVariantViewSet

        view = ProductVariantViewSet()
        view.action = "generate_variants"
        assert (
            view.get_serializer_class() is BulkVariantCreateSerializer
        )


# ═══════════════════════════════════════════════════════════════════════
# ProductOptionConfigViewSet
# ═══════════════════════════════════════════════════════════════════════


class TestProductOptionConfigViewSet:
    """Test ProductOptionConfigViewSet configuration."""

    def test_serializer_class(self):
        from apps.products.api.serializers import (
            ProductOptionConfigSerializer,
        )
        from apps.products.api.views import ProductOptionConfigViewSet

        assert (
            ProductOptionConfigViewSet.serializer_class
            is ProductOptionConfigSerializer
        )

    def test_permission_classes(self):
        from apps.products.api.views import ProductOptionConfigViewSet

        assert (
            IsAuthenticated
            in ProductOptionConfigViewSet.permission_classes
        )

    def test_filterset_fields(self):
        from apps.products.api.views import ProductOptionConfigViewSet

        fields = ProductOptionConfigViewSet.filterset_fields
        assert "product" in fields
        assert "option_type" in fields


# ═══════════════════════════════════════════════════════════════════════
# URL Routing
# ═══════════════════════════════════════════════════════════════════════


class TestVariantURLRouting:
    """Test variant API URL registration."""

    def test_variant_option_type_registered(self):
        from apps.products.api.urls import router

        names = [r[0] for r in router.registry]
        assert "variant-option-types" in names

    def test_variant_option_value_registered(self):
        from apps.products.api.urls import router

        names = [r[0] for r in router.registry]
        assert "variant-option-values" in names

    def test_product_variant_registered(self):
        from apps.products.api.urls import router

        names = [r[0] for r in router.registry]
        assert "product-variants" in names

    def test_product_option_config_registered(self):
        from apps.products.api.urls import router

        names = [r[0] for r in router.registry]
        assert "product-option-configs" in names

    def test_variant_list_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "product-variant-list" in url_names

    def test_variant_detail_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "product-variant-detail" in url_names

    def test_option_type_list_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "variant-option-type-list" in url_names

    def test_option_value_list_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "variant-option-value-list" in url_names

    def test_option_config_list_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "product-option-config-list" in url_names
