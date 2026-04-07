"""
Product API unit tests.

Tests for Brand/TaxClass/UoM/Product serializers, ViewSets, filters, and URL routing.
All tests are database-free.
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, PropertyMock, patch, call

import pytest
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()


# ═══════════════════════════════════════════════════════════════════════
# BrandSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestBrandSerializer:
    """Test BrandSerializer field configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import BrandSerializer
        from apps.products.models import Brand

        assert BrandSerializer.Meta.model is Brand

    def test_meta_fields(self):
        from apps.products.api.serializers import BrandSerializer

        expected = [
            "id",
            "name",
            "slug",
            "logo",
            "description",
            "website",
            "is_active",
        ]
        assert BrandSerializer.Meta.fields == expected

    def test_meta_read_only_fields(self):
        from apps.products.api.serializers import BrandSerializer

        assert BrandSerializer.Meta.read_only_fields == ["id", "slug"]

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import BrandSerializer

        assert issubclass(BrandSerializer, drf_serializers.ModelSerializer)

    def test_fields_count(self):
        from apps.products.api.serializers import BrandSerializer

        assert len(BrandSerializer.Meta.fields) == 7

    def test_id_in_fields(self):
        from apps.products.api.serializers import BrandSerializer

        assert "id" in BrandSerializer.Meta.fields

    def test_logo_in_fields(self):
        from apps.products.api.serializers import BrandSerializer

        assert "logo" in BrandSerializer.Meta.fields

    def test_website_in_fields(self):
        from apps.products.api.serializers import BrandSerializer

        assert "website" in BrandSerializer.Meta.fields

    def test_slug_is_read_only(self):
        from apps.products.api.serializers import BrandSerializer

        assert "slug" in BrandSerializer.Meta.read_only_fields


# ═══════════════════════════════════════════════════════════════════════
# TaxClassSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestTaxClassSerializer:
    """Test TaxClassSerializer field configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import TaxClassSerializer
        from apps.products.models import TaxClass

        assert TaxClassSerializer.Meta.model is TaxClass

    def test_meta_fields(self):
        from apps.products.api.serializers import TaxClassSerializer

        expected = [
            "id",
            "name",
            "rate",
            "description",
            "is_default",
            "is_active",
        ]
        assert TaxClassSerializer.Meta.fields == expected

    def test_meta_read_only_fields(self):
        from apps.products.api.serializers import TaxClassSerializer

        assert TaxClassSerializer.Meta.read_only_fields == ["id"]

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import TaxClassSerializer

        assert issubclass(TaxClassSerializer, drf_serializers.ModelSerializer)

    def test_fields_count(self):
        from apps.products.api.serializers import TaxClassSerializer

        assert len(TaxClassSerializer.Meta.fields) == 6

    def test_rate_in_fields(self):
        from apps.products.api.serializers import TaxClassSerializer

        assert "rate" in TaxClassSerializer.Meta.fields

    def test_is_default_in_fields(self):
        from apps.products.api.serializers import TaxClassSerializer

        assert "is_default" in TaxClassSerializer.Meta.fields


# ═══════════════════════════════════════════════════════════════════════
# UnitOfMeasureSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestUnitOfMeasureSerializer:
    """Test UnitOfMeasureSerializer field configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import UnitOfMeasureSerializer
        from apps.products.models import UnitOfMeasure

        assert UnitOfMeasureSerializer.Meta.model is UnitOfMeasure

    def test_meta_fields(self):
        from apps.products.api.serializers import UnitOfMeasureSerializer

        expected = [
            "id",
            "name",
            "symbol",
            "description",
            "conversion_factor",
            "is_base_unit",
            "is_active",
        ]
        assert UnitOfMeasureSerializer.Meta.fields == expected

    def test_meta_read_only_fields(self):
        from apps.products.api.serializers import UnitOfMeasureSerializer

        assert UnitOfMeasureSerializer.Meta.read_only_fields == ["id"]

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import UnitOfMeasureSerializer

        assert issubclass(UnitOfMeasureSerializer, drf_serializers.ModelSerializer)

    def test_fields_count(self):
        from apps.products.api.serializers import UnitOfMeasureSerializer

        assert len(UnitOfMeasureSerializer.Meta.fields) == 7

    def test_symbol_in_fields(self):
        from apps.products.api.serializers import UnitOfMeasureSerializer

        assert "symbol" in UnitOfMeasureSerializer.Meta.fields

    def test_conversion_factor_in_fields(self):
        from apps.products.api.serializers import UnitOfMeasureSerializer

        assert "conversion_factor" in UnitOfMeasureSerializer.Meta.fields

    def test_is_base_unit_in_fields(self):
        from apps.products.api.serializers import UnitOfMeasureSerializer

        assert "is_base_unit" in UnitOfMeasureSerializer.Meta.fields


# ═══════════════════════════════════════════════════════════════════════
# ProductListSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestProductListSerializer:
    """Test ProductListSerializer field configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import ProductListSerializer
        from apps.products.models import Product

        assert ProductListSerializer.Meta.model is Product

    def test_meta_fields(self):
        from apps.products.api.serializers import ProductListSerializer

        expected = [
            "id",
            "name",
            "slug",
            "sku",
            "barcode",
            "category",
            "category_name",
            "brand",
            "brand_name",
            "product_type",
            "product_type_display",
            "status",
            "status_display",
            "cost_price",
            "selling_price",
            "is_webstore_visible",
            "is_pos_visible",
            "featured",
            "created_on",
            "updated_on",
        ]
        assert ProductListSerializer.Meta.fields == expected

    def test_meta_read_only_fields(self):
        from apps.products.api.serializers import ProductListSerializer

        assert ProductListSerializer.Meta.read_only_fields == [
            "id",
            "slug",
            "created_on",
            "updated_on",
        ]

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import ProductListSerializer

        assert issubclass(ProductListSerializer, drf_serializers.ModelSerializer)

    def test_category_name_in_fields(self):
        from apps.products.api.serializers import ProductListSerializer

        assert "category_name" in ProductListSerializer.Meta.fields

    def test_brand_name_in_fields(self):
        from apps.products.api.serializers import ProductListSerializer

        assert "brand_name" in ProductListSerializer.Meta.fields

    def test_product_type_display_in_fields(self):
        from apps.products.api.serializers import ProductListSerializer

        assert "product_type_display" in ProductListSerializer.Meta.fields

    def test_status_display_in_fields(self):
        from apps.products.api.serializers import ProductListSerializer

        assert "status_display" in ProductListSerializer.Meta.fields

    def test_category_name_source(self):
        from apps.products.api.serializers import ProductListSerializer

        serializer = ProductListSerializer()
        field = serializer.fields["category_name"]
        assert field.source == "category.name"

    def test_brand_name_source(self):
        from apps.products.api.serializers import ProductListSerializer

        serializer = ProductListSerializer()
        field = serializer.fields["brand_name"]
        assert field.source == "brand.name"

    def test_product_type_display_source(self):
        from apps.products.api.serializers import ProductListSerializer

        serializer = ProductListSerializer()
        field = serializer.fields["product_type_display"]
        assert field.source == "get_product_type_display"

    def test_status_display_source(self):
        from apps.products.api.serializers import ProductListSerializer

        serializer = ProductListSerializer()
        field = serializer.fields["status_display"]
        assert field.source == "get_status_display"

    def test_fields_count(self):
        from apps.products.api.serializers import ProductListSerializer

        assert len(ProductListSerializer.Meta.fields) == 20


# ═══════════════════════════════════════════════════════════════════════
# ProductDetailSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestProductDetailSerializer:
    """Test ProductDetailSerializer configuration."""

    def test_meta_model(self):
        from apps.products.api.serializers import ProductDetailSerializer
        from apps.products.models import Product

        assert ProductDetailSerializer.Meta.model is Product

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import ProductDetailSerializer

        assert issubclass(ProductDetailSerializer, drf_serializers.ModelSerializer)

    def test_category_is_nested_serializer(self):
        from apps.products.api.serializers import (
            CategorySerializer,
            ProductDetailSerializer,
        )

        serializer = ProductDetailSerializer()
        cat_field = serializer.fields["category"]
        assert isinstance(cat_field, CategorySerializer)

    def test_brand_is_nested_serializer(self):
        from apps.products.api.serializers import (
            BrandSerializer,
            ProductDetailSerializer,
        )

        serializer = ProductDetailSerializer()
        brand_field = serializer.fields["brand"]
        assert isinstance(brand_field, BrandSerializer)

    def test_tax_class_is_nested_serializer(self):
        from apps.products.api.serializers import (
            ProductDetailSerializer,
            TaxClassSerializer,
        )

        serializer = ProductDetailSerializer()
        field = serializer.fields["tax_class"]
        assert isinstance(field, TaxClassSerializer)

    def test_unit_of_measure_is_nested_serializer(self):
        from apps.products.api.serializers import (
            ProductDetailSerializer,
            UnitOfMeasureSerializer,
        )

        serializer = ProductDetailSerializer()
        field = serializer.fields["unit_of_measure"]
        assert isinstance(field, UnitOfMeasureSerializer)

    def test_category_field_is_read_only(self):
        from apps.products.api.serializers import ProductDetailSerializer

        serializer = ProductDetailSerializer()
        assert serializer.fields["category"].read_only is True

    def test_brand_field_is_read_only(self):
        from apps.products.api.serializers import ProductDetailSerializer

        serializer = ProductDetailSerializer()
        assert serializer.fields["brand"].read_only is True

    def test_description_in_fields(self):
        from apps.products.api.serializers import ProductDetailSerializer

        assert "description" in ProductDetailSerializer.Meta.fields

    def test_short_description_in_fields(self):
        from apps.products.api.serializers import ProductDetailSerializer

        assert "short_description" in ProductDetailSerializer.Meta.fields

    def test_seo_title_in_fields(self):
        from apps.products.api.serializers import ProductDetailSerializer

        assert "seo_title" in ProductDetailSerializer.Meta.fields

    def test_seo_description_in_fields(self):
        from apps.products.api.serializers import ProductDetailSerializer

        assert "seo_description" in ProductDetailSerializer.Meta.fields

    def test_weight_in_fields(self):
        from apps.products.api.serializers import ProductDetailSerializer

        assert "weight" in ProductDetailSerializer.Meta.fields

    def test_mrp_in_fields(self):
        from apps.products.api.serializers import ProductDetailSerializer

        assert "mrp" in ProductDetailSerializer.Meta.fields

    def test_wholesale_price_in_fields(self):
        from apps.products.api.serializers import ProductDetailSerializer

        assert "wholesale_price" in ProductDetailSerializer.Meta.fields

    def test_read_only_fields(self):
        from apps.products.api.serializers import ProductDetailSerializer

        assert ProductDetailSerializer.Meta.read_only_fields == [
            "id",
            "slug",
            "created_on",
            "updated_on",
        ]

    def test_detail_has_more_fields_than_list(self):
        from apps.products.api.serializers import (
            ProductDetailSerializer,
            ProductListSerializer,
        )

        assert len(ProductDetailSerializer.Meta.fields) > len(
            ProductListSerializer.Meta.fields
        )


# ═══════════════════════════════════════════════════════════════════════
# ProductCreateSerializer
# ═══════════════════════════════════════════════════════════════════════


class TestProductCreateSerializer:
    """Test ProductCreateSerializer configuration and methods."""

    def test_meta_model(self):
        from apps.products.api.serializers import ProductCreateSerializer
        from apps.products.models import Product

        assert ProductCreateSerializer.Meta.model is Product

    def test_inherits_model_serializer(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert issubclass(ProductCreateSerializer, drf_serializers.ModelSerializer)

    def test_sku_not_required(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert (
            ProductCreateSerializer.Meta.extra_kwargs["sku"]["required"] is False
        )

    def test_sku_allow_blank(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert (
            ProductCreateSerializer.Meta.extra_kwargs["sku"]["allow_blank"] is True
        )

    def test_slug_not_required(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert (
            ProductCreateSerializer.Meta.extra_kwargs["slug"]["required"] is False
        )

    def test_slug_allow_blank(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert (
            ProductCreateSerializer.Meta.extra_kwargs["slug"]["allow_blank"] is True
        )

    def test_brand_not_required(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert (
            ProductCreateSerializer.Meta.extra_kwargs["brand"]["required"] is False
        )

    def test_brand_allow_null(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert (
            ProductCreateSerializer.Meta.extra_kwargs["brand"]["allow_null"] is True
        )

    def test_has_validate_sku_method(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert hasattr(ProductCreateSerializer, "validate_sku")

    def test_has_validate_barcode_method(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert hasattr(ProductCreateSerializer, "validate_barcode")

    def test_has_generate_sku_method(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert hasattr(ProductCreateSerializer, "_generate_sku")

    def test_has_generate_unique_slug_method(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert hasattr(ProductCreateSerializer, "_generate_unique_slug")

    def test_has_create_method(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert hasattr(ProductCreateSerializer, "create")

    def test_has_update_method(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert hasattr(ProductCreateSerializer, "update")

    def test_name_in_fields(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert "name" in ProductCreateSerializer.Meta.fields

    def test_category_in_fields(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert "category" in ProductCreateSerializer.Meta.fields

    def test_id_not_in_fields(self):
        from apps.products.api.serializers import ProductCreateSerializer

        assert "id" not in ProductCreateSerializer.Meta.fields

    @patch("apps.products.api.serializers.Product.objects")
    def test_generate_sku_format(self, mock_objects):
        from apps.products.api.serializers import ProductCreateSerializer

        mock_objects.filter.return_value.order_by.return_value.first.return_value = None
        category = MagicMock()
        category.slug = "electronics"

        serializer = ProductCreateSerializer()
        sku = serializer._generate_sku(category)
        assert sku.startswith("PRD-ELEC-")
        assert sku == "PRD-ELEC-00001"

    @patch("apps.products.api.serializers.Product.objects")
    def test_generate_unique_slug_simple(self, mock_objects):
        from apps.products.api.serializers import ProductCreateSerializer

        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = False

        serializer = ProductCreateSerializer()
        serializer.instance = None

        result = serializer._generate_unique_slug("Test Phone")
        assert result == "test-phone"

    @patch("apps.products.api.serializers.Product.objects")
    def test_generate_unique_slug_collision(self, mock_objects):
        from apps.products.api.serializers import ProductCreateSerializer

        mock_qs = MagicMock()
        mock_objects.all.return_value = mock_qs
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.side_effect = [True, False]

        serializer = ProductCreateSerializer()
        serializer.instance = None

        result = serializer._generate_unique_slug("Test Phone")
        assert result == "test-phone-2"

    def test_create_autogenerates_slug_and_sku(self):
        from apps.products.api.serializers import ProductCreateSerializer

        serializer = ProductCreateSerializer()
        serializer._generate_unique_slug = MagicMock(return_value="test-phone")
        serializer._generate_sku = MagicMock(return_value="PRD-ELEC-00001")

        category_mock = MagicMock()

        with patch.object(
            drf_serializers.ModelSerializer, "create", return_value=MagicMock()
        ) as mock_super_create:
            serializer.create(
                {"name": "Test Phone", "slug": "", "sku": "", "category": category_mock}
            )
            args = mock_super_create.call_args[0][0]
            assert args["slug"] == "test-phone"
            assert args["sku"] == "PRD-ELEC-00001"

    def test_create_keeps_provided_slug_and_sku(self):
        from apps.products.api.serializers import ProductCreateSerializer

        serializer = ProductCreateSerializer()
        serializer._generate_unique_slug = MagicMock()
        serializer._generate_sku = MagicMock()

        category_mock = MagicMock()

        with patch.object(
            drf_serializers.ModelSerializer, "create", return_value=MagicMock()
        ) as mock_super_create:
            serializer.create(
                {
                    "name": "Test Phone",
                    "slug": "custom-slug",
                    "sku": "CUSTOM-SKU",
                    "category": category_mock,
                }
            )
            args = mock_super_create.call_args[0][0]
            assert args["slug"] == "custom-slug"
            assert args["sku"] == "CUSTOM-SKU"
            serializer._generate_unique_slug.assert_not_called()
            serializer._generate_sku.assert_not_called()

    @patch("apps.products.api.serializers.Product.objects")
    def test_validate_sku_empty_passes(self, mock_objects):
        from apps.products.api.serializers import ProductCreateSerializer

        serializer = ProductCreateSerializer()
        result = serializer.validate_sku("")
        assert result == ""

    @patch("apps.products.api.serializers.Product.objects")
    def test_validate_sku_unique_passes(self, mock_objects):
        from apps.products.api.serializers import ProductCreateSerializer

        mock_objects.filter.return_value.exists.return_value = False

        serializer = ProductCreateSerializer()
        serializer.instance = None

        result = serializer.validate_sku("PRD-ELEC-00001")
        assert result == "PRD-ELEC-00001"

    @patch("apps.products.api.serializers.Product.objects")
    def test_validate_sku_duplicate_raises(self, mock_objects):
        from apps.products.api.serializers import ProductCreateSerializer

        mock_objects.filter.return_value.exists.return_value = True

        serializer = ProductCreateSerializer()
        serializer.instance = None

        with pytest.raises(drf_serializers.ValidationError, match="SKU already exists"):
            serializer.validate_sku("PRD-ELEC-00001")


# ═══════════════════════════════════════════════════════════════════════
# BrandViewSet Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestBrandViewSetConfiguration:
    """Test BrandViewSet configuration."""

    def test_permission_classes(self):
        from apps.products.api.views import BrandViewSet

        assert BrandViewSet.permission_classes == [IsAuthenticated]

    def test_serializer_class(self):
        from apps.products.api.serializers import BrandSerializer
        from apps.products.api.views import BrandViewSet

        assert BrandViewSet.serializer_class is BrandSerializer

    def test_filter_backends(self):
        from django_filters.rest_framework import DjangoFilterBackend

        from apps.products.api.views import BrandViewSet

        assert BrandViewSet.filter_backends == [DjangoFilterBackend, SearchFilter]

    def test_filterset_fields(self):
        from apps.products.api.views import BrandViewSet

        assert BrandViewSet.filterset_fields == ["is_active"]

    def test_search_fields(self):
        from apps.products.api.views import BrandViewSet

        assert BrandViewSet.search_fields == ["name"]

    def test_inherits_model_viewset(self):
        from apps.products.api.views import BrandViewSet
        from rest_framework.viewsets import ModelViewSet

        assert issubclass(BrandViewSet, ModelViewSet)


# ═══════════════════════════════════════════════════════════════════════
# TaxClassViewSet Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestTaxClassViewSetConfiguration:
    """Test TaxClassViewSet configuration."""

    def test_permission_classes(self):
        from apps.products.api.views import TaxClassViewSet

        assert TaxClassViewSet.permission_classes == [IsAuthenticated]

    def test_serializer_class(self):
        from apps.products.api.serializers import TaxClassSerializer
        from apps.products.api.views import TaxClassViewSet

        assert TaxClassViewSet.serializer_class is TaxClassSerializer

    def test_filter_backends(self):
        from django_filters.rest_framework import DjangoFilterBackend

        from apps.products.api.views import TaxClassViewSet

        assert TaxClassViewSet.filter_backends == [DjangoFilterBackend]

    def test_filterset_fields(self):
        from apps.products.api.views import TaxClassViewSet

        assert TaxClassViewSet.filterset_fields == ["is_default"]

    def test_inherits_model_viewset(self):
        from apps.products.api.views import TaxClassViewSet
        from rest_framework.viewsets import ModelViewSet

        assert issubclass(TaxClassViewSet, ModelViewSet)


# ═══════════════════════════════════════════════════════════════════════
# ProductViewSet Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestProductViewSetConfiguration:
    """Test ProductViewSet configuration."""

    def test_permission_classes(self):
        from apps.products.api.views import ProductViewSet

        assert ProductViewSet.permission_classes == [IsAuthenticated]

    def test_filter_backends_include_ordering(self):
        from apps.products.api.views import ProductViewSet

        assert OrderingFilter in ProductViewSet.filter_backends

    def test_filter_backends_include_search(self):
        from apps.products.api.views import ProductViewSet

        assert SearchFilter in ProductViewSet.filter_backends

    def test_filter_backends_include_django_filter(self):
        from django_filters.rest_framework import DjangoFilterBackend

        from apps.products.api.views import ProductViewSet

        assert DjangoFilterBackend in ProductViewSet.filter_backends

    def test_filterset_class(self):
        from apps.products.api.filters import ProductFilter
        from apps.products.api.views import ProductViewSet

        assert ProductViewSet.filterset_class is ProductFilter

    def test_search_fields(self):
        from apps.products.api.views import ProductViewSet

        assert ProductViewSet.search_fields == [
            "name",
            "sku",
            "barcode",
            "description",
        ]

    def test_ordering_fields(self):
        from apps.products.api.views import ProductViewSet

        assert ProductViewSet.ordering_fields == [
            "name",
            "created_on",
            "updated_on",
            "selling_price",
        ]

    def test_ordering_default(self):
        from apps.products.api.views import ProductViewSet

        assert ProductViewSet.ordering == ["-created_on"]

    def test_inherits_model_viewset(self):
        from apps.products.api.views import ProductViewSet
        from rest_framework.viewsets import ModelViewSet

        assert issubclass(ProductViewSet, ModelViewSet)

    def test_get_serializer_class_list(self):
        from apps.products.api.serializers import ProductListSerializer
        from apps.products.api.views import ProductViewSet

        view = ProductViewSet()
        view.action = "list"
        assert view.get_serializer_class() is ProductListSerializer

    def test_get_serializer_class_retrieve(self):
        from apps.products.api.serializers import ProductDetailSerializer
        from apps.products.api.views import ProductViewSet

        view = ProductViewSet()
        view.action = "retrieve"
        assert view.get_serializer_class() is ProductDetailSerializer

    def test_get_serializer_class_create(self):
        from apps.products.api.serializers import ProductCreateSerializer
        from apps.products.api.views import ProductViewSet

        view = ProductViewSet()
        view.action = "create"
        assert view.get_serializer_class() is ProductCreateSerializer

    def test_get_serializer_class_update(self):
        from apps.products.api.serializers import ProductCreateSerializer
        from apps.products.api.views import ProductViewSet

        view = ProductViewSet()
        view.action = "update"
        assert view.get_serializer_class() is ProductCreateSerializer

    def test_get_serializer_class_partial_update(self):
        from apps.products.api.serializers import ProductCreateSerializer
        from apps.products.api.views import ProductViewSet

        view = ProductViewSet()
        view.action = "partial_update"
        assert view.get_serializer_class() is ProductCreateSerializer

    def test_has_get_queryset_method(self):
        from apps.products.api.views import ProductViewSet

        assert hasattr(ProductViewSet, "get_queryset")

    @patch("apps.products.api.views.Product.objects")
    def test_get_queryset_uses_select_related(self, mock_objects):
        from apps.products.api.views import ProductViewSet

        mock_qs = MagicMock()
        mock_objects.select_related.return_value = mock_qs

        view = ProductViewSet()
        view.request = MagicMock()
        view.kwargs = {}
        view.format_kwarg = None
        view.get_queryset()

        mock_objects.select_related.assert_called_once_with(
            "category", "brand", "tax_class", "unit_of_measure"
        )


# ═══════════════════════════════════════════════════════════════════════
# ProductViewSet Custom Actions
# ═══════════════════════════════════════════════════════════════════════


class TestProductViewSetCustomActions:
    """Test custom actions on ProductViewSet."""

    def test_published_action_exists(self):
        from apps.products.api.views import ProductViewSet

        assert hasattr(ProductViewSet, "published")

    def test_featured_action_exists(self):
        from apps.products.api.views import ProductViewSet

        assert hasattr(ProductViewSet, "featured")

    def test_published_action_methods(self):
        from apps.products.api.views import ProductViewSet

        action = getattr(ProductViewSet, "published")
        # DRF decorates actions with .mapping or .kwargs
        assert hasattr(action, "mapping") or hasattr(action, "kwargs")

    def test_featured_action_methods(self):
        from apps.products.api.views import ProductViewSet

        action = getattr(ProductViewSet, "featured")
        assert hasattr(action, "mapping") or hasattr(action, "kwargs")

    def test_published_url_path(self):
        from apps.products.api.views import ProductViewSet

        action = getattr(ProductViewSet, "published")
        assert action.url_path == "published"

    def test_featured_url_path(self):
        from apps.products.api.views import ProductViewSet

        action = getattr(ProductViewSet, "featured")
        assert action.url_path == "featured"


# ═══════════════════════════════════════════════════════════════════════
# ProductFilter
# ═══════════════════════════════════════════════════════════════════════


class TestProductFilter:
    """Test ProductFilter FilterSet configuration."""

    def test_meta_model(self):
        from apps.products.api.filters import ProductFilter
        from apps.products.models import Product

        assert ProductFilter.Meta.model is Product

    def test_meta_fields(self):
        from apps.products.api.filters import ProductFilter

        expected = [
            "category",
            "brand",
            "product_type",
            "status",
            "is_webstore_visible",
            "is_pos_visible",
            "featured",
        ]
        assert ProductFilter.Meta.fields == expected

    def test_category_is_uuid_filter(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert isinstance(
            ProductFilter.declared_filters["category"], django_filters.UUIDFilter
        )

    def test_brand_is_uuid_filter(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert isinstance(
            ProductFilter.declared_filters["brand"], django_filters.UUIDFilter
        )

    def test_product_type_is_choice_filter(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert isinstance(
            ProductFilter.declared_filters["product_type"],
            django_filters.ChoiceFilter,
        )

    def test_status_is_choice_filter(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert isinstance(
            ProductFilter.declared_filters["status"], django_filters.ChoiceFilter
        )

    def test_is_webstore_visible_is_boolean_filter(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert isinstance(
            ProductFilter.declared_filters["is_webstore_visible"],
            django_filters.BooleanFilter,
        )

    def test_is_pos_visible_is_boolean_filter(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert isinstance(
            ProductFilter.declared_filters["is_pos_visible"],
            django_filters.BooleanFilter,
        )

    def test_featured_is_boolean_filter(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert isinstance(
            ProductFilter.declared_filters["featured"], django_filters.BooleanFilter
        )

    def test_min_price_is_number_filter(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert isinstance(
            ProductFilter.declared_filters["min_price"], django_filters.NumberFilter
        )

    def test_max_price_is_number_filter(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert isinstance(
            ProductFilter.declared_filters["max_price"], django_filters.NumberFilter
        )

    def test_min_price_field_name(self):
        from apps.products.api.filters import ProductFilter

        f = ProductFilter.declared_filters["min_price"]
        assert f.field_name == "selling_price"

    def test_max_price_field_name(self):
        from apps.products.api.filters import ProductFilter

        f = ProductFilter.declared_filters["max_price"]
        assert f.field_name == "selling_price"

    def test_min_price_lookup_expr(self):
        from apps.products.api.filters import ProductFilter

        f = ProductFilter.declared_filters["min_price"]
        assert f.lookup_expr == "gte"

    def test_max_price_lookup_expr(self):
        from apps.products.api.filters import ProductFilter

        f = ProductFilter.declared_filters["max_price"]
        assert f.lookup_expr == "lte"

    def test_inherits_filterset(self):
        import django_filters

        from apps.products.api.filters import ProductFilter

        assert issubclass(ProductFilter, django_filters.FilterSet)


# ═══════════════════════════════════════════════════════════════════════
# URL Configuration
# ═══════════════════════════════════════════════════════════════════════


class TestProductURLConfiguration:
    """Test URL routing configuration for product-related endpoints."""

    def test_router_has_brands(self):
        from apps.products.api.urls import router

        names = [r[0] for r in router.registry]
        assert "brands" in names

    def test_router_has_tax_classes(self):
        from apps.products.api.urls import router

        names = [r[0] for r in router.registry]
        assert "tax-classes" in names

    def test_router_has_products(self):
        from apps.products.api.urls import router

        names = [r[0] for r in router.registry]
        assert "products" in names

    def test_router_has_categories(self):
        from apps.products.api.urls import router

        names = [r[0] for r in router.registry]
        assert "categories" in names

    def test_router_registry_count(self):
        from apps.products.api.urls import router

        # 8 viewsets registered: categories, brands, tax-classes, products,
        # variant-option-types, variant-option-values, product-variants,
        # product-option-configs
        assert len(router.registry) == 8

    def test_brand_list_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "brand-list" in url_names

    def test_brand_detail_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "brand-detail" in url_names

    def test_taxclass_list_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "taxclass-list" in url_names

    def test_taxclass_detail_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "taxclass-detail" in url_names

    def test_product_list_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "product-list" in url_names

    def test_product_detail_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "product-detail" in url_names

    def test_product_published_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "product-published" in url_names

    def test_product_featured_url_name_exists(self):
        from apps.products.api.urls import urlpatterns

        url_names = [p.name for p in urlpatterns if hasattr(p, "name")]
        assert "product-featured" in url_names

    def test_urlpatterns_not_empty(self):
        from apps.products.api.urls import urlpatterns

        assert len(urlpatterns) > 0

    def test_urlpatterns_equals_router_urls(self):
        from apps.products.api.urls import router, urlpatterns

        assert urlpatterns is router.urls
