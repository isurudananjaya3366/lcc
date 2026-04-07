"""
Invoice ViewSet — full CRUD + status actions.
"""

import logging

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.invoices.exceptions import (
    CreditLimitExceededError,
    InvoiceError,
    InvoiceLockedError,
    InvalidTransitionError,
)
from apps.invoices.filters import InvoiceFilter
from apps.invoices.models import Invoice
from apps.invoices.serializers import (
    CreditNoteCreateSerializer,
    DebitNoteCreateSerializer,
    InvoiceCreateSerializer,
    InvoiceHistorySerializer,
    InvoiceLineItemSerializer,
    InvoiceListSerializer,
    InvoiceSerializer,
    InvoiceStatusActionSerializer,
)

logger = logging.getLogger(__name__)


class InvoiceViewSet(ModelViewSet):
    """
    ViewSet for Invoices.

    Endpoints
    ---------
    GET    /invoices/                         — list
    POST   /invoices/                         — create
    GET    /invoices/{id}/                     — retrieve
    PUT    /invoices/{id}/                     — update
    PATCH  /invoices/{id}/                     — partial update
    DELETE /invoices/{id}/                     — soft delete (draft only)
    POST   /invoices/{id}/issue/              — issue invoice
    POST   /invoices/{id}/send/               — send via email
    POST   /invoices/{id}/mark_paid/          — record payment
    POST   /invoices/{id}/cancel/             — cancel invoice
    POST   /invoices/{id}/void/               — void invoice
    POST   /invoices/{id}/duplicate/          — duplicate invoice
    GET    /invoices/{id}/pdf/                — download PDF
    GET    /invoices/{id}/preview/            — HTML preview
    GET    /invoices/{id}/history/            — audit history
    GET    /invoices/{id}/line_items/         — list line items
    POST   /invoices/{id}/line_items/         — add line item
    POST   /invoices/create_credit_note/      — create credit note
    POST   /invoices/create_debit_note/       — create debit note
    GET    /invoices/aging_report/            — aging report
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InvoiceFilter
    search_fields = [
        "invoice_number",
        "customer_name",
        "customer_email",
        "notes",
        "external_reference",
    ]
    ordering_fields = [
        "created_on",
        "issue_date",
        "due_date",
        "total",
        "balance_due",
        "invoice_number",
        "status",
    ]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            Invoice.objects.select_related("customer", "order", "related_invoice", "created_by")
            .prefetch_related("line_items")
            .filter(is_deleted=False)
        )

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        if self.action == "create":
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def perform_create(self, serializer):
        """Create invoice via service layer."""
        from apps.invoices.services.invoice_service import InvoiceService

        data = serializer.validated_data
        order_id = data.get("order_id")
        if order_id:
            invoice = InvoiceService.create_from_order(
                order_id=order_id, user=self.request.user
            )
        else:
            invoice = InvoiceService.create_invoice(
                data={
                    "type": data.get("type", "STANDARD"),
                    "notes": data.get("notes", ""),
                    "currency": data.get("currency", "LKR"),
                    "customer_id": data.get("customer_id"),
                },
                user=self.request.user,
            )
        # Return the created invoice
        self.created_invoice = invoice

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = InvoiceSerializer(self.created_invoice)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        if instance.status != "DRAFT":
            return Response(
                {"detail": "Only draft invoices can be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.is_deleted = True
        from django.utils import timezone
        instance.deleted_on = timezone.now()
        instance.save(update_fields=["is_deleted", "deleted_on"])

    # ── Status Actions ──────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="issue")
    def issue(self, request, pk=None):
        """Issue the invoice."""
        from apps.invoices.services.invoice_service import InvoiceService

        serializer = InvoiceStatusActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invoice = InvoiceService.issue_invoice(pk, user=request.user)
            return Response(InvoiceSerializer(invoice).data)
        except (InvalidTransitionError, InvoiceError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="send")
    def send_email(self, request, pk=None):
        """Send invoice via email."""
        from apps.invoices.services.invoice_service import InvoiceService
        try:
            invoice = InvoiceService.send_invoice(pk, user=request.user)
            return Response(InvoiceSerializer(invoice).data)
        except (InvalidTransitionError, InvoiceError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        """Record payment for the invoice."""
        from apps.invoices.services.invoice_service import InvoiceService

        serializer = InvoiceStatusActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            amount = serializer.validated_data.get("amount")
            invoice = InvoiceService.mark_paid(pk, user=request.user, amount=amount)
            return Response(InvoiceSerializer(invoice).data)
        except (InvalidTransitionError, InvoiceError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Cancel the invoice."""
        from apps.invoices.services.invoice_service import InvoiceService

        serializer = InvoiceStatusActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invoice = InvoiceService.cancel_invoice(
                pk, user=request.user, reason=serializer.validated_data.get("notes", "")
            )
            return Response(InvoiceSerializer(invoice).data)
        except (InvalidTransitionError, InvoiceError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="void")
    def void(self, request, pk=None):
        """Void the invoice."""
        from apps.invoices.services.invoice_service import InvoiceService

        serializer = InvoiceStatusActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            invoice = InvoiceService.void_invoice(
                pk, user=request.user, reason=serializer.validated_data.get("notes", "")
            )
            return Response(InvoiceSerializer(invoice).data)
        except (InvalidTransitionError, InvoiceError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="duplicate")
    def duplicate(self, request, pk=None):
        """Duplicate an existing invoice."""
        from apps.invoices.services.invoice_service import InvoiceService
        try:
            invoice = InvoiceService.duplicate_invoice(pk, user=request.user)
            return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)
        except InvoiceError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ── PDF / Preview ────────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        """Download the invoice PDF."""
        from apps.invoices.services.pdf_generator import InvoicePDFGenerator

        pdf_bytes = InvoicePDFGenerator.generate_pdf(pk)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        invoice = self.get_object()
        filename = f"{invoice.invoice_number or invoice.id}.pdf"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        """HTML preview of the invoice."""
        from apps.invoices.services.pdf_generator import InvoicePDFGenerator

        html = InvoicePDFGenerator.render_preview(pk)
        return HttpResponse(html, content_type="text/html")

    # ── History ──────────────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Get audit history for the invoice."""
        invoice = self.get_object()
        history = invoice.history.all().order_by("-created_on")
        serializer = InvoiceHistorySerializer(history, many=True)
        return Response(serializer.data)

    # ── Line Items ───────────────────────────────────────────────

    @action(detail=True, methods=["get", "post"], url_path="line-items")
    def line_items(self, request, pk=None):
        """List or add line items."""
        invoice = self.get_object()
        if request.method == "GET":
            from apps.invoices.serializers.line_item import InvoiceLineItemListSerializer
            items = invoice.line_items.all().order_by("position")
            serializer = InvoiceLineItemListSerializer(items, many=True)
            return Response(serializer.data)
        # POST
        if not invoice.is_editable:
            return Response(
                {"detail": "Invoice is not editable."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = InvoiceLineItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(invoice=invoice)
        from apps.invoices.services.calculation_service import InvoiceCalculationService
        InvoiceCalculationService.recalculate_invoice(invoice.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ── Credit / Debit Notes ─────────────────────────────────────

    @action(detail=False, methods=["post"], url_path="credit-note")
    def create_credit_note(self, request):
        """Create a credit note for an existing invoice."""
        from apps.invoices.services.credit_note_service import CreditNoteService

        serializer = CreditNoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cn = CreditNoteService.create_credit_note(
                original_invoice_id=serializer.validated_data["original_invoice_id"],
                reason=serializer.validated_data["reason"],
                line_items_data=serializer.validated_data.get("line_items"),
                notes=serializer.validated_data.get("notes", ""),
                user=request.user,
            )
            return Response(InvoiceSerializer(cn).data, status=status.HTTP_201_CREATED)
        except (InvoiceError, CreditLimitExceededError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="debit-note")
    def create_debit_note(self, request):
        """Create a debit note for an existing invoice."""
        from apps.invoices.services.debit_note_service import DebitNoteService

        serializer = DebitNoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            dn = DebitNoteService.create_debit_note(
                original_invoice_id=serializer.validated_data["original_invoice_id"],
                reason=serializer.validated_data["reason"],
                line_items_data=serializer.validated_data.get("line_items"),
                notes=serializer.validated_data.get("notes", ""),
                user=request.user,
            )
            return Response(InvoiceSerializer(dn).data, status=status.HTTP_201_CREATED)
        except InvoiceError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ── Reports ──────────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="reports/aging")
    def aging_report(self, request):
        """Get accounts receivable aging report."""
        from apps.invoices.services.invoice_service import InvoiceService

        report = InvoiceService.get_aging_report()
        return Response(report)
