"""LeaveType ViewSet with CRUD and custom actions."""

import logging

from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from apps.leave.constants import LeaveRequestStatus
from apps.leave.filters import LeaveTypeFilter
from apps.leave.models import LeaveType
from apps.leave.serializers import LeaveTypeListSerializer, LeaveTypeSerializer

logger = logging.getLogger(__name__)


class LeaveTypeViewSet(ModelViewSet):
    """ViewSet for LeaveType CRUD and management actions.

    Endpoints:
        GET    /types/                  - List leave types
        POST   /types/                  - Create leave type
        GET    /types/{id}/             - Retrieve leave type
        PUT    /types/{id}/             - Update leave type
        PATCH  /types/{id}/             - Partial update
        DELETE /types/{id}/             - Soft delete (deactivate)
        POST   /types/{id}/activate/    - Activate
        POST   /types/{id}/deactivate/  - Deactivate
        GET    /types/{id}/usage/        - Usage statistics
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LeaveTypeFilter
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "category", "created_on"]
    ordering = ["category", "name"]

    def get_queryset(self):
        return LeaveType.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.action == "list":
            return LeaveTypeListSerializer
        return LeaveTypeSerializer

    def perform_destroy(self, instance):
        """Soft delete — deactivate instead of hard delete."""
        instance.is_active = False
        instance.is_deleted = True
        instance.save(update_fields=["is_active", "is_deleted"])

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a deactivated leave type."""
        leave_type = self.get_object()
        leave_type.is_active = True
        leave_type.save(update_fields=["is_active"])
        serializer = LeaveTypeSerializer(leave_type)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a leave type."""
        leave_type = self.get_object()
        leave_type.is_active = False
        leave_type.save(update_fields=["is_active"])
        serializer = LeaveTypeSerializer(leave_type)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="usage")
    def usage_stats(self, request, pk=None):
        """Get usage statistics for a leave type."""
        leave_type = self.get_object()

        from apps.leave.models import LeaveRequest

        requests = LeaveRequest.objects.filter(
            leave_type=leave_type,
            is_deleted=False,
        )

        stats = requests.aggregate(
            total_requests=Count("id"),
        )

        by_status = {}
        for s in LeaveRequestStatus:
            by_status[s.value.lower()] = requests.filter(status=s.value).count()

        return Response({
            "leave_type_id": str(leave_type.id),
            "leave_type_name": leave_type.name,
            "statistics": {
                "total_requests": stats["total_requests"],
                **by_status,
            },
        })
