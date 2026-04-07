"""Designation ViewSet with CRUD and custom actions."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.organization.constants import (
    DESIGNATION_LEVEL_CHOICES,
    DESIGNATION_LEVEL_ORDER,
)
from apps.organization.filters import DesignationFilter
from apps.organization.models import Designation
from apps.organization.serializers import (
    DesignationListSerializer,
    DesignationSerializer,
)
from apps.organization.services.designation_service import DesignationService


class DesignationViewSet(ModelViewSet):
    """ViewSet for Designation CRUD and utility actions."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DesignationFilter
    search_fields = ["title", "code", "description"]
    ordering_fields = ["title", "code", "level", "created_on"]
    ordering = ["title"]

    def get_queryset(self):
        return (
            Designation.objects.filter(is_deleted=False)
            .select_related("department", "reports_to")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return DesignationListSerializer
        return DesignationSerializer

    def perform_create(self, serializer):
        instance = DesignationService.create(serializer.validated_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        instance = DesignationService.update(self.get_object(), serializer.validated_data)
        serializer.instance = instance

    # ── Custom Actions ──────────────────────────────────────────────

    @action(detail=True, methods=["get"])
    def employees(self, request, pk=None):
        """List employees holding this designation."""
        designation = self.get_object()
        from apps.employees.serializers import EmployeeListSerializer

        qs = designation.employees.filter(is_deleted=False)
        serializer = EmployeeListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="salary-range")
    def salary_range(self, request, pk=None):
        """Return salary range information for this designation."""
        designation = self.get_object()
        return Response(
            {
                "title": designation.title,
                "min_salary": str(designation.min_salary) if designation.min_salary else None,
                "max_salary": str(designation.max_salary) if designation.max_salary else None,
                "currency": designation.currency,
            }
        )

    @action(detail=False, methods=["get"], url_path="level-hierarchy")
    def level_hierarchy(self, request):
        """Return the designation level hierarchy with counts."""
        from django.db.models import Count

        level_counts = (
            Designation.objects.filter(is_deleted=False)
            .values("level")
            .annotate(count=Count("id"))
            .order_by()
        )

        level_map = {lc["level"]: lc["count"] for lc in level_counts}

        hierarchy = []
        for value, label in DESIGNATION_LEVEL_CHOICES:
            hierarchy.append(
                {
                    "level": value,
                    "label": label,
                    "rank": DESIGNATION_LEVEL_ORDER.get(value, 0),
                    "count": level_map.get(value, 0),
                }
            )

        return Response(hierarchy)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate_designation(self, request, pk=None):
        """Re-activate this designation."""
        designation = self.get_object()
        designation = DesignationService.activate(designation)
        serializer = self.get_serializer(designation)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate_designation(self, request, pk=None):
        """Deactivate this designation."""
        designation = self.get_object()
        designation = DesignationService.deactivate(designation)
        serializer = self.get_serializer(designation)
        return Response(serializer.data)
