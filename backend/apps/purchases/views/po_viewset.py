"""
Purchase Order ViewSet.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.purchases.models.purchase_order import PurchaseOrder
from apps.purchases.serializers.po_serializer import (
    POCreateSerializer,
    PODetailSerializer,
    POListSerializer,
    POUpdateSerializer,
)
from apps.purchases.services.po_service import POService


class POViewSet(ModelViewSet):
    """ViewSet for Purchase Orders with full CRUD and lifecycle actions."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "vendor", "payment_status"]
    search_fields = ["po_number", "vendor__company_name", "vendor_reference"]
    ordering_fields = ["po_number", "order_date", "total", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return PurchaseOrder.objects.select_related(
            "vendor", "created_by", "receiving_warehouse"
        ).prefetch_related("line_items")

    def get_serializer_class(self):
        if self.action == "list":
            return POListSerializer
        if self.action in ("create",):
            return POCreateSerializer
        if self.action in ("partial_update", "update"):
            return POUpdateSerializer
        return PODetailSerializer

    def create(self, request, *args, **kwargs):
        """Create PO and return detail representation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        po = serializer.save()
        return Response(
            PODetailSerializer(po).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="send")
    def send_po(self, request, pk=None):
        """Send PO to vendor (DRAFT -> SENT)."""
        try:
            po = POService.send_po(pk, request.user)
            return Response(PODetailSerializer(po).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="acknowledge")
    def acknowledge(self, request, pk=None):
        """Record vendor acknowledgement (SENT -> ACKNOWLEDGED)."""
        vendor_ref = request.data.get("vendor_reference")
        try:
            po = POService.acknowledge_po(pk, request.user, vendor_ref)
            return Response(PODetailSerializer(po).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancel a PO."""
        reason = request.data.get("reason", "")
        try:
            po = POService.cancel_po(pk, request.user, reason)
            return Response(PODetailSerializer(po).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        """Duplicate a PO as a new DRAFT."""
        try:
            po = POService.duplicate_po(pk, user=request.user)
            return Response(
                PODetailSerializer(po).data, status=status.HTTP_201_CREATED
            )
        except PurchaseOrder.DoesNotExist:
            return Response(
                {"detail": "PO not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["post"], url_path="receive")
    def receive(self, request, pk=None):
        """Receive items on a PO."""
        from apps.purchases.serializers.grn_serializer import GRNDetailSerializer
        from apps.purchases.services.receiving_service import ReceivingService

        line_data = request.data.get("line_data", [])
        try:
            if line_data:
                grn = ReceivingService.receive_partial(pk, request.user, line_data)
            else:
                grn = ReceivingService.receive_full(pk, request.user)
            return Response(
                GRNDetailSerializer(grn).data, status=status.HTTP_201_CREATED
            )
        except (ValueError, PurchaseOrder.DoesNotExist) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """Approve a PO (PENDING_APPROVAL -> APPROVED)."""
        notes = request.data.get("approval_notes", "")
        try:
            po = POService.approve_po(pk, request.user, notes)
            return Response(PODetailSerializer(po).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """Reject a PO (PENDING_APPROVAL -> DRAFT)."""
        reason = request.data.get("rejection_reason", "")
        try:
            po = POService.reject_po(pk, request.user, reason)
            return Response(PODetailSerializer(po).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Get the change history for a PO."""
        from apps.purchases.models.po_history import POHistory

        po = self.get_object()
        entries = POHistory.objects.filter(purchase_order=po).order_by("-created_on")
        data = [
            {
                "id": str(entry.pk),
                "change_type": entry.change_type,
                "change_description": entry.change_description,
                "changed_by": str(entry.changed_by_id) if entry.changed_by_id else None,
                "data_snapshot": entry.data_snapshot,
                "created_on": entry.created_on.isoformat(),
            }
            for entry in entries
        ]
        return Response(data)

    @action(detail=True, methods=["get"], url_path="download-pdf")
    def download_pdf(self, request, pk=None):
        """Download a generated PDF for the PO."""
        from apps.purchases.services.pdf_generator import POPDFGenerator
        from apps.purchases.models.po_template import POTemplate

        po = self.get_object()
        template = POTemplate.objects.filter(is_default=True).first()
        pdf_content = POPDFGenerator.generate_pdf(po, template)

        response = HttpResponse(pdf_content, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{po.po_number}.pdf"'
        return response
