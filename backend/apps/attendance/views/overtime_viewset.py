"""Overtime Request ViewSet with approve/reject actions."""

import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.attendance.filters import OvertimeRequestFilter
from apps.attendance.models import OvertimeRequest
from apps.attendance.serializers import (
    OvertimeRequestListSerializer,
    OvertimeRequestSerializer,
)
from apps.attendance.services.overtime_service import OvertimeService

logger = logging.getLogger(__name__)


class OvertimeRequestViewSet(ModelViewSet):
    """ViewSet for Overtime Request CRUD with approval workflow."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OvertimeRequestFilter
    search_fields = ["employee__first_name", "employee__last_name", "reason"]
    ordering_fields = ["date", "planned_hours", "status", "created_on"]
    ordering = ["-date"]

    def get_queryset(self):
        return (
            OvertimeRequest.objects.filter(is_deleted=False)
            .select_related("employee", "attendance_record", "approved_by")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OvertimeRequestListSerializer
        return OvertimeRequestSerializer

    def perform_destroy(self, instance):
        """Soft delete."""
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    # ── Custom Actions ──────────────────────────────────────────

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve an overtime request."""
        ot_request = self.get_object()
        if ot_request.status != "pending":
            return Response(
                {"detail": "Only pending requests can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        OvertimeService.approve_request(ot_request, request.user)
        ot_request.refresh_from_db()
        return Response(OvertimeRequestSerializer(ot_request).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject an overtime request."""
        ot_request = self.get_object()
        if ot_request.status != "pending":
            return Response(
                {"detail": "Only pending requests can be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rejection_reason = request.data.get("rejection_reason", "")
        OvertimeService.reject_request(ot_request, request.user, rejection_reason)
        ot_request.refresh_from_db()
        return Response(OvertimeRequestSerializer(ot_request).data)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """List all pending overtime requests."""
        qs = self.get_queryset().filter(status="pending")
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = OvertimeRequestListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = OvertimeRequestListSerializer(qs, many=True)
        return Response(serializer.data)
