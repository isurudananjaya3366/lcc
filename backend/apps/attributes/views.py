"""DRF ViewSets for the attributes app."""

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.products.models import Category

from .models import Attribute, AttributeGroup, AttributeOption
from .serializers import (
    AttributeDetailSerializer,
    AttributeGroupSerializer,
    AttributeListSerializer,
    AttributeOptionSerializer,
    AttributeSerializer,
)


class AttributeGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for AttributeGroup CRUD operations."""

    serializer_class = AttributeGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["display_order", "name", "created_on"]
    ordering = ["display_order", "name"]

    def get_queryset(self):
        return (
            AttributeGroup.objects.all()
            .prefetch_related("attributes")
        )


class AttributeViewSet(viewsets.ModelViewSet):
    """ViewSet for Attribute CRUD with custom actions."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["attribute_type", "is_required", "is_filterable", "group"]
    search_fields = ["name"]
    ordering_fields = ["display_order", "name", "created_on"]
    ordering = ["group__display_order", "display_order", "name"]

    def get_serializer_class(self):
        if self.action == "list":
            return AttributeListSerializer
        if self.action == "retrieve":
            return AttributeDetailSerializer
        return AttributeSerializer

    def get_queryset(self):
        return (
            Attribute.objects.all()
            .select_related("group")
            .prefetch_related("options", "categories")
        )

    @action(detail=False, methods=["get"], url_path="by-category")
    def by_category(self, request):
        """Return attributes for a category including inherited from parents."""
        category_id = request.query_params.get("category_id")
        if not category_id:
            return Response(
                {"error": "category_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        category = get_object_or_404(Category, pk=category_id)

        # Collect category + all ancestors
        category_ids = []
        current = category
        while current is not None:
            category_ids.append(current.pk)
            current = current.parent

        attributes = (
            self.get_queryset()
            .filter(categories__id__in=category_ids)
            .distinct()
        )
        serializer = AttributeDetailSerializer(attributes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="filterable")
    def filterable(self, request):
        """Return filterable attributes for webstore faceted search."""
        queryset = self.get_queryset().filter(is_filterable=True)

        category_id = request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(categories__id=category_id).distinct()

        serializer = AttributeDetailSerializer(queryset, many=True)
        return Response(serializer.data)


class AttributeOptionViewSet(viewsets.ModelViewSet):
    """ViewSet for AttributeOption CRUD operations."""

    serializer_class = AttributeOptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["attribute", "is_default"]
    ordering_fields = ["display_order", "label"]
    ordering = ["display_order", "label"]

    def get_queryset(self):
        return (
            AttributeOption.objects.all()
            .select_related("attribute")
        )
