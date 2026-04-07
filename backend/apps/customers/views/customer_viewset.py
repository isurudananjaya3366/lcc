"""
Customer ViewSet — full CRUD plus custom actions.

Provides all customer API endpoints including search, import/export,
statistics, tagging, duplicate detection, and merge.
"""

import logging

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

from apps.customers.filters import CustomerFilter
from apps.customers.models import (
    Customer,
    CustomerAddress,
    CustomerCommunication,
    CustomerImport,
    CustomerPhone,
    CustomerTag,
)
from apps.customers.serializers import (
    CustomerAddressSerializer,
    CustomerCreateUpdateSerializer,
    CustomerListSerializer,
    CustomerPhoneSerializer,
    CustomerSerializer,
    CustomerTagSerializer,
)
from apps.customers.services import (
    CommunicationService,
    CustomerActivityService,
    CustomerExportService,
    CustomerImportService,
    CustomerSearchService,
    CustomerTagService,
    DuplicateDetectionService,
    PurchaseHistoryService,
)

logger = logging.getLogger(__name__)


class CustomerPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class CustomerViewSet(ModelViewSet):
    """
    ViewSet for Customer CRUD and custom actions.

    Standard endpoints:
        GET    /customers/             — list
        POST   /customers/             — create
        GET    /customers/{id}/        — retrieve
        PUT    /customers/{id}/        — update
        PATCH  /customers/{id}/        — partial_update
        DELETE /customers/{id}/        — destroy (soft-delete)

    Custom endpoints — see individual @action methods.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomerPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CustomerFilter
    search_fields = [
        "customer_code",
        "first_name",
        "last_name",
        "display_name",
        "business_name",
        "email",
        "phone",
    ]
    ordering_fields = [
        "customer_code",
        "display_name",
        "created_on",
        "total_purchases",
        "outstanding_balance",
    ]
    ordering = ["display_name"]

    def get_queryset(self):
        return Customer.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.action == "list":
            return CustomerListSerializer
        if self.action in ("create", "update", "partial_update"):
            return CustomerCreateUpdateSerializer
        return CustomerSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        """Soft-delete."""
        instance.is_deleted = True
        instance.deleted_on = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_on", "updated_on"])

    # ── Search ───────────────────────────────────────────────────────

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Full-text search.
        Query params: q (search term)
        """
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        results = CustomerSearchService.search(query)
        page = self.paginate_queryset(results)
        serializer = CustomerListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    # ── Addresses ────────────────────────────────────────────────────

    @action(detail=True, methods=["get", "post"])
    def addresses(self, request, pk=None):
        customer = self.get_object()
        if request.method == "GET":
            qs = CustomerAddress.objects.filter(customer=customer)
            serializer = CustomerAddressSerializer(qs, many=True)
            return Response(serializer.data)
        # POST
        serializer = CustomerAddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ── Phones ───────────────────────────────────────────────────────

    @action(detail=True, methods=["get", "post"])
    def phones(self, request, pk=None):
        customer = self.get_object()
        if request.method == "GET":
            qs = CustomerPhone.objects.filter(customer=customer)
            serializer = CustomerPhoneSerializer(qs, many=True)
            return Response(serializer.data)
        # POST
        serializer = CustomerPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ── Communications ───────────────────────────────────────────────

    @action(detail=True, methods=["get", "post"])
    def communications(self, request, pk=None):
        customer = self.get_object()
        if request.method == "GET":
            timeline = CommunicationService.get_communication_timeline(
                customer_id=customer.pk,
                communication_type=request.query_params.get("type"),
            )
            page = self.paginate_queryset(list(timeline))
            return self.get_paginated_response(
                [
                    {
                        "id": str(c.pk),
                        "type": c.communication_type,
                        "subject": c.subject,
                        "content": c.content,
                        "date": c.communication_date.isoformat(),
                    }
                    for c in page
                ]
            )
        # POST
        CommunicationService.log_communication(
            customer_id=customer.pk,
            communication_type=request.data.get("communication_type", "NOTE"),
            subject=request.data.get("subject", ""),
            content=request.data.get("content", ""),
            contacted_by=request.user,
        )
        return Response({"detail": "Communication logged."}, status=status.HTTP_201_CREATED)

    # ── History ──────────────────────────────────────────────────────

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        customer = self.get_object()
        summary = PurchaseHistoryService.get_purchase_summary(customer.pk)
        return Response(summary)

    # ── Statistics ───────────────────────────────────────────────────

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        customer = self.get_object()
        stats = PurchaseHistoryService.get_customer_statistics(customer.pk)
        return Response(stats)

    # ── Activity Feed ────────────────────────────────────────────────

    @action(detail=True, methods=["get"])
    def activity(self, request, pk=None):
        customer = self.get_object()
        page_num = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        feed = CustomerActivityService.get_activity_feed(
            customer_id=customer.pk,
            page=page_num,
            page_size=page_size,
        )
        return Response(feed)

    # ── Tags ─────────────────────────────────────────────────────────

    @action(detail=True, methods=["get", "post"], url_path="tags")
    def tags(self, request, pk=None):
        customer = self.get_object()
        if request.method == "GET":
            tags_qs = CustomerTagService.get_customer_tags(customer.pk)
            serializer = CustomerTagSerializer(tags_qs, many=True)
            return Response(serializer.data)
        # POST — assign tag
        tag_id = request.data.get("tag_id")
        if not tag_id:
            return Response(
                {"detail": "tag_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        CustomerTagService.assign_tag(
            customer_id=customer.pk,
            tag_id=tag_id,
            assigned_by=request.user,
        )
        return Response({"detail": "Tag assigned."}, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["delete"],
        url_path="tags/(?P<tag_id>[^/.]+)",
    )
    def remove_tag(self, request, pk=None, tag_id=None):
        customer = self.get_object()
        removed = CustomerTagService.remove_tag(customer.pk, tag_id)
        if removed:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Tag not found on customer."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # ── Import ───────────────────────────────────────────────────────

    @action(
        detail=False,
        methods=["post"],
        url_path="import",
        parser_classes=[MultiPartParser, FormParser],
    )
    def import_csv(self, request):
        """Import customers from an uploaded CSV file."""
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response(
                {"detail": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create progress record
        import_record = CustomerImport.objects.create(
            filename=csv_file.name,
            status="PROCESSING",
            uploaded_by=request.user,
        )

        try:
            summary = CustomerImportService.import_from_csv(
                csv_file,
                uploaded_by=request.user,
                import_record=import_record,
            )
            return Response(summary, status=status.HTTP_201_CREATED)
        except ValueError as exc:
            import_record.status = "FAILED"
            import_record.save(update_fields=["status"])
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # ── Export ───────────────────────────────────────────────────────

    @action(detail=False, methods=["get"])
    def export(self, request):
        """Export filtered customers to CSV."""
        qs = self.filter_queryset(self.get_queryset())
        columns = request.query_params.get("columns")
        column_list = columns.split(",") if columns else None

        csv_content = CustomerExportService.export_to_csv(
            qs, columns=column_list
        )
        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="customers_export_{timezone.now():%Y%m%d}.csv"'
        )
        return response

    # ── Duplicates ───────────────────────────────────────────────────

    @action(detail=True, methods=["get"])
    def duplicates(self, request, pk=None):
        """Find potential duplicates for a customer."""
        customer = self.get_object()
        min_score = int(request.query_params.get("min_score", 50))
        matches = DuplicateDetectionService.find_duplicates(
            customer, min_score=min_score
        )
        return Response(
            [
                {
                    "customer_id": m.customer_id,
                    "display_name": m.display_name,
                    "score": m.score,
                    "confidence": m.confidence,
                    "matched_fields": m.matched_fields,
                }
                for m in matches
            ]
        )

    # ── Merge ────────────────────────────────────────────────────────

    @action(detail=False, methods=["post"])
    def merge(self, request):
        """
        Merge two customers.
        Body: { "primary_id": "...", "duplicate_id": "...", "reason": "..." }
        """
        primary_id = request.data.get("primary_id")
        duplicate_id = request.data.get("duplicate_id")
        if not primary_id or not duplicate_id:
            return Response(
                {"detail": "primary_id and duplicate_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            primary = Customer.objects.get(pk=primary_id, is_deleted=False)
            duplicate = Customer.objects.get(pk=duplicate_id, is_deleted=False)
        except Customer.DoesNotExist:
            return Response(
                {"detail": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        merge_record = DuplicateDetectionService.merge_customers(
            primary,
            duplicate,
            merged_by=request.user,
            merge_reason=request.data.get("reason", ""),
        )
        return Response(
            {
                "merge_id": str(merge_record.pk),
                "primary_id": str(primary.pk),
                "duplicate_id": str(duplicate.pk),
                "orders_transferred": merge_record.orders_transferred,
                "invoices_transferred": merge_record.invoices_transferred,
                "payments_transferred": merge_record.payments_transferred,
            },
            status=status.HTTP_200_OK,
        )
