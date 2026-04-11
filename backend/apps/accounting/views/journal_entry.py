"""
Journal entry ViewSet with custom workflow actions.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounting.models import JournalEntry
from apps.accounting.serializers.journal_entry import JournalEntrySerializer
from apps.accounting.services.approval_service import ApprovalService
from apps.accounting.services.journal_service import (
    EntryNotPostableError,
    EntryNotVoidableError,
    JournalEntryService,
)


class JournalEntryViewSet(viewsets.ModelViewSet):
    """
    CRUD + workflow actions for journal entries.

    Custom actions:
        POST /entries/{id}/post/    — Post a draft/approved entry.
        POST /entries/{id}/void/    — Void a posted entry (creates reversal).
        POST /entries/{id}/approve/ — Approve a pending entry.
    """

    queryset = JournalEntry.objects.prefetch_related("lines", "lines__account").all()
    serializer_class = JournalEntrySerializer
    filterset_fields = ["entry_status", "entry_type", "entry_source"]
    search_fields = ["entry_number", "reference", "description"]
    ordering_fields = ["entry_date", "entry_number", "total_debit"]
    ordering = ["-entry_date", "-entry_number"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        if not instance.is_editable:
            return Response(
                {"detail": "Only draft entries can be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.delete()

    # ── Custom Actions ──────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="post")
    def post_entry(self, request, pk=None):
        """Post a draft or approved entry."""
        entry = self.get_object()
        try:
            JournalEntryService.post_entry(entry, posted_by=request.user)
        except (EntryNotPostableError, Exception) as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(entry)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        """Void a posted entry by creating a reversal."""
        entry = self.get_object()
        reason = request.data.get("reason", "")
        try:
            voided, reversal = JournalEntryService.void_entry(
                entry, voided_by=request.user, reason=reason
            )
        except (EntryNotVoidableError, Exception) as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "voided_entry": self.get_serializer(voided).data,
                "reversal_entry": self.get_serializer(reversal).data,
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a pending entry."""
        entry = self.get_object()
        service = ApprovalService()
        try:
            service.approve_entry(entry, approved_by=request.user)
        except Exception as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(entry)
        return Response(serializer.data)
