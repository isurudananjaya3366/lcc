"""Vendor ViewSet for CRUD and custom actions."""

import logging

from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.vendors.filters import VendorFilter
from apps.vendors.models import (
    Vendor,
    VendorAddress,
    VendorBankAccount,
    VendorContact,
    VendorCommunication,
    VendorDocument,
    VendorProduct,
)
from apps.vendors.serializers import (
    VendorAddressSerializer,
    VendorBankAccountSerializer,
    VendorContactSerializer,
    VendorCreateUpdateSerializer,
    VendorListSerializer,
    VendorPerformanceSerializer,
    VendorProductSerializer,
    VendorSerializer,
)
from apps.vendors.services.communication_service import CommunicationService
from apps.vendors.services.document_service import DocumentService
from apps.vendors.services.export_service import VendorExportService
from apps.vendors.services.import_service import VendorImportService

logger = logging.getLogger(__name__)


class VendorPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class VendorViewSet(ModelViewSet):
    """
    ViewSet for Vendor CRUD and custom actions.

    Standard endpoints:
        GET    /vendors/             - list
        POST   /vendors/             - create
        GET    /vendors/{id}/        - retrieve
        PUT    /vendors/{id}/        - update
        PATCH  /vendors/{id}/        - partial_update
        DELETE /vendors/{id}/        - destroy (soft-delete)
    """

    permission_classes = [IsAuthenticated]
    pagination_class = VendorPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VendorFilter
    search_fields = [
        "vendor_code", "company_name", "display_name",
        "primary_email", "primary_phone",
    ]
    ordering_fields = [
        "vendor_code", "company_name", "rating",
        "total_orders", "total_spend", "created_on",
    ]
    ordering = ["company_name"]

    def get_queryset(self):
        return Vendor.objects.filter(is_deleted=False).select_related(
            "created_by", "updated_by",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return VendorListSerializer
        if self.action in ("create", "update", "partial_update"):
            return VendorCreateUpdateSerializer
        return VendorSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        """Soft-delete."""
        instance.is_deleted = True
        instance.deleted_on = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_on", "updated_on"])

    # ── Custom Actions ─────────────────────────

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search vendors. Query param: q"""
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = self.get_queryset().filter(
            Q(company_name__icontains=query)
            | Q(vendor_code__icontains=query)
            | Q(primary_email__icontains=query)
        )
        page = self.paginate_queryset(qs)
        serializer = VendorListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def contacts(self, request, pk=None):
        vendor = self.get_object()
        if request.method == "GET":
            qs = VendorContact.objects.filter(vendor=vendor)
            serializer = VendorContactSerializer(qs, many=True)
            return Response(serializer.data)
        serializer = VendorContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendor=vendor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"])
    def addresses(self, request, pk=None):
        vendor = self.get_object()
        if request.method == "GET":
            qs = VendorAddress.objects.filter(vendor=vendor)
            serializer = VendorAddressSerializer(qs, many=True)
            return Response(serializer.data)
        serializer = VendorAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendor=vendor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="bank-accounts")
    def bank_accounts(self, request, pk=None):
        vendor = self.get_object()
        if request.method == "GET":
            qs = VendorBankAccount.objects.filter(vendor=vendor)
            serializer = VendorBankAccountSerializer(qs, many=True)
            return Response(serializer.data)
        serializer = VendorBankAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendor=vendor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"])
    def products(self, request, pk=None):
        vendor = self.get_object()
        if request.method == "GET":
            qs = VendorProduct.objects.filter(vendor=vendor).select_related("product")
            serializer = VendorProductSerializer(qs, many=True)
            return Response(serializer.data)
        serializer = VendorProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(vendor=vendor)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def performance(self, request, pk=None):
        vendor = self.get_object()
        qs = vendor.performance_records.all()
        serializer = VendorPerformanceSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def communications(self, request, pk=None):
        vendor = self.get_object()
        if request.method == "GET":
            timeline = CommunicationService.get_communication_timeline(vendor.pk)
            page = self.paginate_queryset(list(timeline))
            return self.get_paginated_response(
                [
                    {
                        "id": str(c.pk),
                        "type": c.communication_type,
                        "subject": c.subject,
                        "content": c.content,
                        "date": c.contact_date.isoformat(),
                        "follow_up_date": c.follow_up_date.isoformat() if c.follow_up_date else None,
                    }
                    for c in page
                ]
            )
        CommunicationService.log_communication(
            vendor_id=vendor.pk,
            data={
                "communication_type": request.data.get("communication_type", "email"),
                "subject": request.data.get("subject", ""),
                "content": request.data.get("content", ""),
                "contacted_by": request.user,
                "contact_date": timezone.now(),
            },
        )
        return Response({"detail": "Communication logged."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], parser_classes=[MultiPartParser, FormParser])
    def documents(self, request, pk=None):
        vendor = self.get_object()
        if request.method == "GET":
            qs = VendorDocument.objects.filter(vendor=vendor).select_related("uploaded_by")
            return Response(
                [
                    {
                        "id": str(d.pk),
                        "name": d.name,
                        "document_type": d.document_type,
                        "file": request.build_absolute_uri(d.file.url) if d.file else None,
                        "expiry_date": d.expiry_date.isoformat() if d.expiry_date else None,
                        "created_on": d.created_on.isoformat(),
                    }
                    for d in qs
                ]
            )
        try:
            doc = DocumentService.upload_document(
                vendor_id=vendor.pk,
                document_type=request.data.get("document_type", "other"),
                name=request.data.get("name", ""),
                file=request.FILES.get("file"),
                uploaded_by=request.user,
                expiry_date=request.data.get("expiry_date"),
                notes=request.data.get("notes", ""),
            )
            return Response(
                {"id": str(doc.pk), "name": doc.name, "detail": "Document uploaded."},
                status=status.HTTP_201_CREATED,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        vendor = self.get_object()
        from apps.vendors.services.history_service import VendorHistoryService
        records = VendorHistoryService.get_vendor_history(vendor.pk)
        return Response(
            [
                {
                    "id": str(h.pk),
                    "field_name": h.field_name,
                    "old_value": h.old_value,
                    "new_value": h.new_value,
                    "change_type": h.change_type,
                    "changed_at": h.changed_at.isoformat(),
                }
                for h in records
            ]
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="import",
        parser_classes=[MultiPartParser, FormParser],
    )
    def import_csv(self, request):
        """Import vendors from CSV."""
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response(
                {"detail": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            summary = VendorImportService.import_vendors_from_csv(csv_file)
            return Response(summary, status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="export")
    def export_csv(self, request):
        """Export vendors to CSV."""
        qs = self.filter_queryset(self.get_queryset())
        csv_output = VendorExportService.export_vendors_to_csv(queryset=qs)
        response = HttpResponse(csv_output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="vendors_export.csv"'
        return response

    @action(detail=False, methods=["post"], url_path="bulk-activate")
    def bulk_activate(self, request):
        """Activate multiple vendors by ID."""
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"detail": "No vendor IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        updated = Vendor.objects.filter(pk__in=ids, is_deleted=False).update(status="active")
        return Response({"detail": f"{updated} vendor(s) activated."})

    @action(detail=False, methods=["post"], url_path="bulk-deactivate")
    def bulk_deactivate(self, request):
        """Deactivate multiple vendors by ID."""
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"detail": "No vendor IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        updated = Vendor.objects.filter(pk__in=ids, is_deleted=False).update(status="inactive")
        return Response({"detail": f"{updated} vendor(s) deactivated."})
