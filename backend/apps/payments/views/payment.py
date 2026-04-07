"""Payment ViewSet — full CRUD + custom actions."""

import logging

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.payments.exceptions import PaymentError
from apps.payments.filters import PaymentFilter
from apps.payments.models import Payment
from apps.payments.serializers import (
    PaymentCreateSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentSerializer,
)

logger = logging.getLogger(__name__)


class PaymentViewSet(ModelViewSet):
    """
    ViewSet for Payments.

    Endpoints
    ---------
    GET    /payments/                  — list
    POST   /payments/                  — create
    GET    /payments/{id}/             — retrieve
    PUT    /payments/{id}/             — update
    PATCH  /payments/{id}/             — partial update
    DELETE /payments/{id}/             — soft delete
    POST   /payments/{id}/complete/    — complete payment
    POST   /payments/{id}/cancel/      — cancel payment
    GET    /payments/{id}/receipt/     — download receipt PDF
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PaymentFilter
    search_fields = [
        "payment_number",
        "reference_number",
        "transaction_id",
    ]
    ordering_fields = [
        "created_on",
        "payment_date",
        "amount",
        "payment_number",
        "status",
    ]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            Payment.objects.select_related(
                "customer", "invoice", "order", "received_by", "approved_by"
            )
            .prefetch_related("allocations", "history", "refunds")
            .filter(is_deleted=False)
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "create":
            return PaymentCreateSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        """Create payment via service layer."""
        from apps.payments.services.payment_service import PaymentService

        data = serializer.validated_data

        # Look up related instances from IDs
        invoice = None
        if data.get("invoice_id"):
            from apps.invoices.models import Invoice
            invoice = Invoice.objects.get(id=data["invoice_id"])

        order = None
        if data.get("order_id"):
            from apps.orders.models import Order
            order = Order.objects.get(id=data["order_id"])

        customer = None
        if data.get("customer_id"):
            from apps.customers.models import Customer
            customer = Customer.objects.get(id=data["customer_id"])

        payment = PaymentService.create_payment(
            method=data["method"],
            amount=data["amount"],
            invoice=invoice,
            order=order,
            customer=customer,
            payment_date=data.get("payment_date"),
            reference_number=data.get("reference_number", ""),
            transaction_id=data.get("transaction_id", ""),
            currency=data.get("currency", "LKR"),
            exchange_rate=data.get("exchange_rate"),
            method_details=data.get("method_details"),
            notes=data.get("notes", ""),
            user=self.request.user,
        )
        self._created_payment = payment

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except PaymentError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        response_serializer = PaymentSerializer(self._created_payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """Soft delete."""
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted", "updated_on"])

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Complete a pending payment."""
        from apps.payments.services.payment_service import PaymentService

        payment = self.get_object()
        try:
            PaymentService.complete_payment(payment, user=request.user)
        except PaymentError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a pending payment."""
        from apps.payments.services.payment_service import PaymentService

        payment = self.get_object()
        reason = request.data.get("reason", "")
        try:
            PaymentService.cancel_payment(payment, reason=reason, user=request.user)
        except PaymentError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=["get"])
    def receipt(self, request, pk=None):
        """Download receipt PDF."""
        from apps.payments.services.receipt_pdf_service import ReceiptPDFService
        from apps.payments.services.receipt_service import ReceiptService

        payment = self.get_object()
        receipt_obj = ReceiptService.get_receipt_by_payment(payment)
        if not receipt_obj:
            return Response(
                {"detail": "No receipt found for this payment."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not receipt_obj.has_pdf():
            ReceiptPDFService.generate_receipt_pdf(receipt_obj)
            receipt_obj.refresh_from_db()

        if not receipt_obj.pdf_file:
            return Response(
                {"detail": "PDF generation failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = HttpResponse(
            receipt_obj.pdf_file.read(), content_type="application/pdf"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{receipt_obj.receipt_number}.pdf"'
        )
        return response
