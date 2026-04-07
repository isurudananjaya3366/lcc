"""Admin payslip management viewset and endpoints."""

import logging

from django.utils import timezone
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.payslip.constants import PayslipStatus
from apps.payslip.models import Payslip, PayslipBatch
from apps.payslip.serializers.payslip import (
    PayslipDetailSerializer,
    PayslipListSerializer,
)

logger = logging.getLogger(__name__)


# ── Batch Serializers (used only by admin endpoints) ─────────

class PayslipBatchSerializer(drf_serializers.ModelSerializer):
    progress_percent = drf_serializers.ReadOnlyField()
    duration_seconds = drf_serializers.ReadOnlyField()

    class Meta:
        model = PayslipBatch
        fields = [
            "id",
            "payroll_period",
            "initiated_by",
            "batch_type",
            "status",
            "total_count",
            "success_count",
            "failed_count",
            "error_log",
            "started_at",
            "completed_at",
            "progress_percent",
            "duration_seconds",
            "created_on",
        ]
        read_only_fields = fields


class BulkActionRequestSerializer(drf_serializers.Serializer):
    period_id = drf_serializers.UUIDField(help_text="Payroll period UUID.")


# ── Admin Payslip ViewSet ────────────────────────────────────

class AdminPayslipViewSet(ModelViewSet):
    """Admin ViewSet for full payslip management.

    Endpoints:
        GET    /payslips/                  - List all payslips
        POST   /payslips/                  - Create payslip
        GET    /payslips/{id}/             - Retrieve payslip
        PUT    /payslips/{id}/             - Update payslip
        DELETE /payslips/{id}/             - Delete payslip
        POST   /payslips/{id}/generate/    - Generate single PDF
        POST   /payslips/{id}/send-email/  - Send email
        POST   /generate-bulk/             - Bulk generate
        POST   /send-bulk/                 - Bulk send emails
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["slip_number", "employee__first_name", "employee__last_name"]
    ordering_fields = ["slip_number", "generated_at", "status", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return (
            Payslip.objects.all()
            .select_related("employee", "payroll_period", "employee_payroll", "generated_by")
            .prefetch_related("earnings", "deductions", "employer_contributions")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PayslipListSerializer
        return PayslipDetailSerializer

    # ── Task 80: Generate Single ─────────────────────────────

    @action(detail=True, methods=["post"], url_path="generate")
    def generate(self, request, pk=None):
        """Generate PDF for a single payslip."""
        from apps.payslip.services.generator import PayslipGenerationError, PayslipGenerator

        payslip = self.get_object()
        generator = PayslipGenerator()
        try:
            generator.generate(payslip.pk, request.user)
        except PayslipGenerationError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payslip.refresh_from_db()
        return Response({
            "success": True,
            "payslip_id": str(payslip.pk),
            "slip_number": payslip.slip_number,
            "pdf_url": payslip.pdf_url,
            "generated_at": payslip.generated_at,
        })

    # ── Task 81: Bulk Generate ───────────────────────────────

    @action(detail=False, methods=["post"], url_path="generate-bulk")
    def generate_bulk(self, request):
        """Start bulk PDF generation for a payroll period."""
        ser = BulkActionRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        period_id = ser.validated_data["period_id"]

        from apps.payroll.models import PayrollPeriod
        try:
            period = PayrollPeriod.objects.get(pk=period_id)
        except PayrollPeriod.DoesNotExist:
            return Response(
                {"detail": "Payroll period not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        total = Payslip.objects.filter(
            payroll_period=period, status=PayslipStatus.DRAFT,
        ).count()
        if total == 0:
            return Response(
                {"detail": "No DRAFT payslips for this period."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        batch = PayslipBatch.objects.create(
            payroll_period=period,
            initiated_by=request.user,
            batch_type="GENERATION",
            status="PENDING",
            total_count=total,
        )

        from apps.payslip.tasks import bulk_generate_payslips
        bulk_generate_payslips.delay(str(batch.pk))

        return Response({
            "batch_id": str(batch.pk),
            "total_count": total,
            "status": "PROCESSING",
            "message": "Bulk generation started.",
        }, status=status.HTTP_202_ACCEPTED)

    # ── Task 82: Send Email ──────────────────────────────────

    @action(detail=True, methods=["post"], url_path="send-email")
    def send_email(self, request, pk=None):
        """Send email for a single payslip."""
        from apps.payslip.services.emailer import PayslipEmailer, PayslipEmailError

        payslip = self.get_object()
        emailer = PayslipEmailer()
        try:
            emailer.send(payslip)
        except PayslipEmailError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payslip.refresh_from_db()
        return Response({
            "success": True,
            "payslip_id": str(payslip.pk),
            "sent_to": payslip.sent_to,
            "sent_at": payslip.sent_at,
        })

    # ── Task 83: Bulk Send Email ─────────────────────────────

    @action(detail=False, methods=["post"], url_path="send-bulk")
    def send_bulk(self, request):
        """Start bulk email distribution for a payroll period."""
        ser = BulkActionRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        period_id = ser.validated_data["period_id"]

        from apps.payroll.models import PayrollPeriod
        try:
            period = PayrollPeriod.objects.get(pk=period_id)
        except PayrollPeriod.DoesNotExist:
            return Response(
                {"detail": "Payroll period not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        total = Payslip.objects.filter(
            payroll_period=period,
            status=PayslipStatus.GENERATED,
            email_sent=False,
        ).count()
        if total == 0:
            return Response(
                {"detail": "No unsent GENERATED payslips for this period."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        batch = PayslipBatch.objects.create(
            payroll_period=period,
            initiated_by=request.user,
            batch_type="EMAIL",
            status="PENDING",
            total_count=total,
        )

        from apps.payslip.tasks import bulk_send_payslip_emails
        bulk_send_payslip_emails.delay(str(batch.pk))

        return Response({
            "batch_id": str(batch.pk),
            "total_count": total,
            "status": "PROCESSING",
            "message": "Bulk email distribution started.",
        }, status=status.HTTP_202_ACCEPTED)


# ── Task 84: Batch Status ViewSet ────────────────────────────

class PayslipBatchViewSet(ReadOnlyModelViewSet):
    """Read-only viewset for payslip batch progress tracking."""

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = PayslipBatchSerializer
    ordering = ["-created_on"]

    def get_queryset(self):
        return PayslipBatch.objects.select_related(
            "payroll_period", "initiated_by",
        ).all()

    @action(detail=True, methods=["get"], url_path="status")
    def batch_status(self, request, pk=None):
        """Get current batch processing status."""
        batch = self.get_object()
        return Response({
            "batch_id": str(batch.pk),
            "batch_type": batch.batch_type,
            "status": batch.status,
            "progress": {
                "total": batch.total_count,
                "processed": batch.success_count + batch.failed_count,
                "success": batch.success_count,
                "failed": batch.failed_count,
                "percent": batch.progress_percent,
            },
            "started_at": batch.started_at,
            "completed_at": batch.completed_at,
            "duration_seconds": batch.duration_seconds,
        })
