"""Vendor Payment ViewSet."""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.vendor_bills.models.vendor_payment import VendorPayment
from apps.vendor_bills.serializers.bill_serializer import (
    VendorPaymentCreateSerializer,
    VendorPaymentDetailSerializer,
    VendorPaymentListSerializer,
)
from apps.vendor_bills.services.payment_service import PaymentService


class VendorPaymentViewSet(ModelViewSet):
    """ViewSet for Vendor Payments with CRUD and lifecycle actions."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "vendor", "payment_method", "is_advance"]
    search_fields = ["payment_number", "reference", "vendor__company_name"]
    ordering_fields = ["payment_number", "payment_date", "amount", "created_on"]
    ordering = ["-payment_date", "-created_on"]

    def get_queryset(self):
        return VendorPayment.objects.select_related(
            "vendor", "vendor_bill", "created_by"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return VendorPaymentListSerializer
        if self.action == "create":
            return VendorPaymentCreateSerializer
        return VendorPaymentDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response(
            VendorPaymentDetailSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="void")
    def void_payment(self, request, pk=None):
        """Void / reverse a completed payment."""
        reason = request.data.get("reason", "")
        try:
            payment = PaymentService.void_payment(pk, request.user, reason)
            return Response(VendorPaymentDetailSerializer(payment).data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        """Payment summary stats (total paid, count, average)."""
        from apps.vendor_bills.services.report_service import PaymentHistoryService

        vendor_id = request.query_params.get("vendor")
        start = request.query_params.get("start_date")
        end = request.query_params.get("end_date")
        data = PaymentHistoryService.get_payment_summary(
            vendor_id=vendor_id, start_date=start, end_date=end
        )
        return Response(data)

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        """Dashboard widget data for AP overview."""
        from apps.vendor_bills.services.report_service import ReportService

        data = ReportService.dashboard_widgets()
        return Response(data)
