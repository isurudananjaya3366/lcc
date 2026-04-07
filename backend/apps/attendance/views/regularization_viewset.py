"""Regularization ViewSet with approve/reject actions."""

import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.attendance.filters import RegularizationFilter
from apps.attendance.models import AttendanceRegularization
from apps.attendance.serializers import (
    RegularizationListSerializer,
    RegularizationSerializer,
)
from apps.attendance.services.regularization_service import RegularizationService

logger = logging.getLogger(__name__)


class RegularizationViewSet(ModelViewSet):
    """ViewSet for Attendance Regularization CRUD with approval workflow."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RegularizationFilter
    search_fields = ["employee__first_name", "employee__last_name", "reason"]
    ordering_fields = ["created_on", "status"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            AttendanceRegularization.objects.filter(is_deleted=False)
            .select_related("employee", "attendance_record", "approved_by")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return RegularizationListSerializer
        return RegularizationSerializer

    def perform_create(self, serializer):
        """Set original values from the attendance record on creation."""
        record = serializer.validated_data["attendance_record"]
        serializer.save(
            original_clock_in=record.clock_in,
            original_clock_out=record.clock_out,
        )

    def perform_destroy(self, instance):
        """Soft delete."""
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    # ── Custom Actions ──────────────────────────────────────────

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a regularization request."""
        regularization = self.get_object()
        if not regularization.is_pending:
            return Response(
                {"detail": "Only pending requests can be approved."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        RegularizationService.approve(regularization, request.user)
        regularization.refresh_from_db()
        return Response(RegularizationSerializer(regularization).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a regularization request."""
        regularization = self.get_object()
        if not regularization.is_pending:
            return Response(
                {"detail": "Only pending requests can be rejected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rejection_reason = request.data.get("rejection_reason", "")
        RegularizationService.reject(regularization, request.user, rejection_reason)
        regularization.refresh_from_db()
        return Response(RegularizationSerializer(regularization).data)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """List all pending regularization requests."""
        qs = self.get_queryset().filter(status="pending")
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = RegularizationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RegularizationListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="bulk-approve")
    def bulk_approve(self, request):
        """Approve multiple regularization requests at once."""
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"detail": "No IDs provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        approved = RegularizationService.bulk_approve(ids, request.user)
        return Response({
            "status": "success",
            "approved_count": len(approved),
            "approved_ids": [str(r.pk) for r in approved],
        })

    @action(detail=False, methods=["post"], url_path="bulk-reject")
    def bulk_reject(self, request):
        """Reject multiple regularization requests at once."""
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"detail": "No IDs provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rejection_reason = request.data.get("rejection_reason", "")
        rejected = RegularizationService.bulk_reject(ids, request.user, rejection_reason)
        return Response({
            "status": "success",
            "rejected_count": len(rejected),
            "rejected_ids": [str(r.pk) for r in rejected],
        })
