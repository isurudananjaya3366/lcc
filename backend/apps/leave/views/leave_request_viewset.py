"""LeaveRequest ViewSet with full workflow actions."""

import logging
from datetime import date

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from apps.leave.constants import LeaveRequestStatus
from apps.leave.filters import LeaveRequestFilter
from apps.leave.models import LeaveRequest
from apps.leave.serializers import (
    LeaveRequestCreateSerializer,
    LeaveRequestListSerializer,
    LeaveRequestSerializer,
    WorkflowActionSerializer,
)

logger = logging.getLogger(__name__)


class LeaveRequestViewSet(ModelViewSet):
    """ViewSet for LeaveRequest CRUD and workflow actions.

    Standard endpoints:
        GET    /requests/                   - List requests
        POST   /requests/                   - Create request
        GET    /requests/{id}/              - Retrieve request
        PUT    /requests/{id}/              - Update (DRAFT only)
        PATCH  /requests/{id}/              - Partial update
        DELETE /requests/{id}/              - Delete (DRAFT only)

    Workflow actions:
        POST   /requests/{id}/submit/       - Submit for approval
        POST   /requests/{id}/approve/      - Approve request
        POST   /requests/{id}/reject/       - Reject request
        POST   /requests/{id}/cancel/       - Cancel request
        POST   /requests/{id}/recall/       - Recall approved request

    Query actions:
        GET    /requests/pending/           - Pending approvals
        GET    /requests/team/              - Team requests
        GET    /requests/calendar/          - Calendar view
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LeaveRequestFilter
    search_fields = [
        "employee__first_name",
        "employee__last_name",
        "employee__employee_id",
        "reason",
    ]
    ordering_fields = [
        "start_date",
        "end_date",
        "total_days",
        "status",
        "submitted_at",
        "created_on",
    ]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            LeaveRequest.objects.filter(is_deleted=False)
            .select_related("employee", "leave_type", "approved_by")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return LeaveRequestCreateSerializer
        if self.action in ("update", "partial_update"):
            return LeaveRequestCreateSerializer
        if self.action == "list":
            return LeaveRequestListSerializer
        return LeaveRequestSerializer

    def perform_destroy(self, instance):
        """Soft delete — only allowed for DRAFT requests."""
        if instance.status != LeaveRequestStatus.DRAFT:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only DRAFT requests can be deleted.")
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])

    # ── Workflow Actions ─────────────────────────────────────

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Submit a draft leave request for approval."""
        leave_request = self.get_object()

        from apps.leave.services.request_service import LeaveRequestService
        service = LeaveRequestService()

        try:
            service.submit(leave_request)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a pending leave request."""
        leave_request = self.get_object()

        from apps.leave.services.request_service import LeaveRequestService
        service = LeaveRequestService()

        try:
            service.approve(leave_request, approved_by=request.user)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a pending leave request."""
        leave_request = self.get_object()
        reason = request.data.get("reason", "")

        from apps.leave.services.request_service import LeaveRequestService
        service = LeaveRequestService()

        try:
            service.reject(leave_request, rejected_by=request.user, reason=reason)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a pending or approved request."""
        leave_request = self.get_object()
        reason = request.data.get("reason", "")

        from apps.leave.services.request_service import LeaveRequestService
        service = LeaveRequestService()

        try:
            service.cancel(leave_request, reason=reason)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def recall(self, request, pk=None):
        """Recall an approved request."""
        leave_request = self.get_object()
        reason = request.data.get("reason", "")

        from apps.leave.services.request_service import LeaveRequestService
        service = LeaveRequestService()

        try:
            service.recall(leave_request, reason=reason)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data)

    # ── Query Actions ────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="pending")
    def pending_approvals(self, request):
        """List pending requests requiring approval."""
        qs = self.get_queryset().filter(status=LeaveRequestStatus.PENDING)
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = LeaveRequestListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = LeaveRequestListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="team")
    def team_requests(self, request):
        """List team member leave requests."""
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = LeaveRequestListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = LeaveRequestListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="calendar")
    def calendar(self, request):
        """Return calendar view of leave requests."""
        year = request.query_params.get("year", date.today().year)
        month = request.query_params.get("month")

        qs = self.get_queryset().filter(
            status__in=[LeaveRequestStatus.APPROVED, LeaveRequestStatus.PENDING],
        )

        try:
            year = int(year)
            qs = qs.filter(start_date__year__lte=year, end_date__year__gte=year)
        except (ValueError, TypeError):
            pass

        if month:
            try:
                month = int(month)
                qs = qs.filter(start_date__month__lte=month, end_date__month__gte=month)
            except (ValueError, TypeError):
                pass

        requests = [
            {
                "employee": f"{lr.employee.first_name} {lr.employee.last_name}" if lr.employee else "",
                "start_date": lr.start_date.isoformat(),
                "end_date": lr.end_date.isoformat(),
                "leave_type": lr.leave_type.name if lr.leave_type else "",
                "leave_type_color": lr.leave_type.color if lr.leave_type else "#999",
                "status": lr.status,
                "total_days": str(lr.total_days),
            }
            for lr in qs.select_related("employee", "leave_type")
        ]

        return Response({
            "year": year,
            "month": month,
            "requests": requests,
        })

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Return workflow history for a request."""
        leave_request = self.get_object()

        history_entries = []

        history_entries.append({
            "timestamp": leave_request.created_on.isoformat() if leave_request.created_on else None,
            "action": "CREATED",
            "status": LeaveRequestStatus.DRAFT,
        })

        if leave_request.submitted_at:
            history_entries.append({
                "timestamp": leave_request.submitted_at.isoformat(),
                "action": "SUBMITTED",
                "status": LeaveRequestStatus.PENDING,
            })

        if leave_request.status == LeaveRequestStatus.APPROVED and leave_request.approved_at:
            history_entries.append({
                "timestamp": leave_request.approved_at.isoformat(),
                "action": "APPROVED",
                "status": LeaveRequestStatus.APPROVED,
                "by": str(leave_request.approved_by) if leave_request.approved_by else None,
            })

        if leave_request.status == LeaveRequestStatus.REJECTED and leave_request.rejection_reason:
            history_entries.append({
                "action": "REJECTED",
                "status": LeaveRequestStatus.REJECTED,
                "reason": leave_request.rejection_reason,
            })

        if leave_request.status == LeaveRequestStatus.CANCELLED:
            history_entries.append({
                "action": "CANCELLED",
                "status": LeaveRequestStatus.CANCELLED,
            })

        if leave_request.recalled_at:
            history_entries.append({
                "timestamp": leave_request.recalled_at.isoformat(),
                "action": "RECALLED",
                "status": LeaveRequestStatus.RECALLED,
                "reason": leave_request.recalled_reason,
            })

        return Response({
            "request_id": str(leave_request.id),
            "history": history_entries,
        })
