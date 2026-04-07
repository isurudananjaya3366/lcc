"""Vendor Bill ViewSet."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.vendor_bills.models.vendor_bill import VendorBill
from apps.vendor_bills.serializers.bill_serializer import (
    VendorBillCreateSerializer,
    VendorBillDetailSerializer,
    VendorBillListSerializer,
    VendorBillUpdateSerializer,
)
from apps.vendor_bills.services.bill_service import BillService


class VendorBillViewSet(ModelViewSet):
    """ViewSet for Vendor Bills with full CRUD and lifecycle actions."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "vendor", "payment_terms", "is_matched"]
    search_fields = ["bill_number", "vendor_invoice_number", "vendor__company_name"]
    ordering_fields = ["bill_number", "bill_date", "due_date", "total", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return VendorBill.objects.select_related(
            "vendor", "created_by", "purchase_order"
        ).prefetch_related("line_items")

    def get_serializer_class(self):
        if self.action == "list":
            return VendorBillListSerializer
        if self.action == "create":
            return VendorBillCreateSerializer
        if self.action in ("update", "partial_update"):
            return VendorBillUpdateSerializer
        return VendorBillDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bill = serializer.save()
        return Response(
            VendorBillDetailSerializer(bill).data,
            status=status.HTTP_201_CREATED,
        )

    # ------------------------------------------------------------------
    # Custom lifecycle actions
    # ------------------------------------------------------------------

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        """Submit bill for approval (DRAFT -> PENDING)."""
        try:
            bill = BillService.submit_bill(pk, request.user)
            return Response(VendorBillDetailSerializer(bill).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """Approve a bill (PENDING -> APPROVED)."""
        notes = request.data.get("approval_notes", "")
        try:
            bill = BillService.approve_bill(pk, request.user, notes)
            return Response(VendorBillDetailSerializer(bill).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="dispute")
    def dispute(self, request, pk=None):
        """Dispute a bill."""
        reason = request.data.get("reason", "")
        try:
            bill = BillService.dispute_bill(pk, request.user, reason)
            return Response(VendorBillDetailSerializer(bill).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancel a bill."""
        reason = request.data.get("reason", "")
        try:
            bill = BillService.cancel_bill(pk, request.user, reason)
            return Response(VendorBillDetailSerializer(bill).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        """Duplicate a bill as a new DRAFT."""
        try:
            bill = BillService.duplicate_bill(pk, request.user)
            return Response(
                VendorBillDetailSerializer(bill).data,
                status=status.HTTP_201_CREATED,
            )
        except VendorBill.DoesNotExist:
            return Response(
                {"detail": "Bill not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["post"], url_path="match")
    def match(self, request, pk=None):
        """Run 3-way matching on this bill."""
        from apps.vendor_bills.services.matching_service import MatchingService

        bill = self.get_object()
        try:
            results = MatchingService.perform_3way_match(bill)
            return Response(results)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Get change history for a bill."""
        from apps.vendor_bills.models.bill_history import BillHistory

        bill = self.get_object()
        entries = BillHistory.objects.filter(vendor_bill=bill).order_by("-created_on")
        data = [
            {
                "id": str(e.pk),
                "change_type": e.change_type,
                "description": e.description,
                "old_status": e.old_status,
                "new_status": e.new_status,
                "changed_by": str(e.changed_by_id) if e.changed_by_id else None,
                "created_on": e.created_on.isoformat(),
            }
            for e in entries
        ]
        return Response(data)
