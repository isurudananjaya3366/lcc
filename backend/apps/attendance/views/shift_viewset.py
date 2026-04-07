"""Shift ViewSet with CRUD and custom actions."""

import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.attendance.filters import ShiftFilter
from apps.attendance.models import Shift
from apps.attendance.serializers import ShiftListSerializer, ShiftSerializer

logger = logging.getLogger(__name__)


class ShiftViewSet(ModelViewSet):
    """ViewSet for Shift CRUD and related operations."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ShiftFilter
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "start_time", "work_hours", "created_on"]
    ordering = ["name"]

    def get_queryset(self):
        return (
            Shift.objects.filter(is_deleted=False)
            .select_related()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ShiftListSerializer
        return ShiftSerializer

    def perform_destroy(self, instance):
        """Soft delete."""
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    # ── Custom Actions ──────────────────────────────────────────

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a shift."""
        shift = self.get_object()
        shift.status = "active"
        shift.save(update_fields=["status"])
        return Response(ShiftSerializer(shift).data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a shift."""
        shift = self.get_object()
        shift.status = "inactive"
        shift.save(update_fields=["status"])
        return Response(ShiftSerializer(shift).data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """List only active shifts."""
        qs = self.get_queryset().filter(status="active")
        serializer = ShiftListSerializer(qs, many=True)
        return Response(serializer.data)
