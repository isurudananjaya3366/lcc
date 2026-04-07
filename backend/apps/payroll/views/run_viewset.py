"""PayrollRun ViewSet."""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.payroll.filters import EmployeePayrollFilter, PayrollRunFilter
from apps.payroll.models import EmployeePayroll, PayrollHistory, PayrollRun
from apps.payroll.serializers.employee_payroll_serializer import (
    EmployeePayrollListSerializer,
    EmployeePayrollSerializer,
)
from apps.payroll.serializers.history_serializer import PayrollHistorySerializer
from apps.payroll.serializers.run_serializer import (
    PayrollRunListSerializer,
    PayrollRunSerializer,
)
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.payroll.services.approval_service import PayrollApprovalService
from apps.payroll.services.finalization_service import PayrollFinalizationService
from apps.payroll.services.payroll_processor import PayrollProcessor
from apps.payroll.services.reversal_service import PayrollReversalService
from apps.payroll.services.statutory_reports import StatutoryReportService

logger = logging.getLogger(__name__)


class PayrollRunViewSet(ModelViewSet):
    """ViewSet for PayrollRun CRUD and payroll processing actions.

    Endpoints:
        GET    /runs/                            - List runs
        POST   /runs/                            - Create run
        GET    /runs/{id}/                       - Retrieve run
        PUT    /runs/{id}/                       - Update run
        DELETE /runs/{id}/                       - Delete run
        POST   /runs/{id}/process/               - Process payroll
        POST   /runs/{id}/submit-for-approval/   - Submit for approval
        POST   /runs/{id}/approve/               - Approve run
        POST   /runs/{id}/reject/                - Reject run
        POST   /runs/{id}/finalize/              - Finalize run
        POST   /runs/{id}/generate-bank-file/    - Generate bank file
        POST   /runs/{id}/mark-as-paid/          - Mark as paid
        POST   /runs/{id}/reverse/               - Reverse run
        GET    /runs/{id}/employees/             - List employee payrolls
        GET    /runs/{id}/employees/{emp_id}/    - Get employee payroll detail
        GET    /runs/{id}/history/               - Audit trail
        GET    /runs/{id}/epf-return/            - Generate EPF return
        GET    /runs/{id}/etf-return/            - Generate ETF return
        GET    /runs/{id}/paye-return/           - Generate PAYE return
        GET    /runs/pending-approvals/          - List pending approvals
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PayrollRunFilter
    search_fields = ["notes"]
    ordering_fields = ["run_number", "status", "total_employees", "total_net", "created_on"]
    ordering = ["-created_on"]

    def get_queryset(self):
        return PayrollRun.objects.select_related(
            "payroll_period", "processed_by", "approved_by"
        ).all()

    def get_serializer_class(self):
        if self.action == "list":
            return PayrollRunListSerializer
        return PayrollRunSerializer

    # ── Processing ────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="process")
    def process(self, request, pk=None):
        """Process payroll for all eligible employees in this run."""
        payroll_run = self.get_object()
        try:
            processor = PayrollProcessor(payroll_run)
            result = processor.process_batch()
            return Response(result)
        except Exception:
            logger.exception("Payroll processing failed for run %s", pk)
            return Response(
                {"detail": "Payroll processing failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ── Approval workflow ─────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="submit-for-approval")
    def submit_for_approval(self, request, pk=None):
        """Submit this payroll run for approval."""
        self.get_object()
        service = PayrollApprovalService()
        try:
            run = service.submit_for_approval(pk, submitted_by=request.user)
            serializer = self.get_serializer(run)
            return Response(serializer.data)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """Approve this payroll run."""
        self.get_object()
        notes = request.data.get("notes", "")
        service = PayrollApprovalService()
        try:
            run = service.approve(pk, approved_by=request.user, notes=notes)
            serializer = self.get_serializer(run)
            return Response(serializer.data)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """Reject this payroll run."""
        self.get_object()
        reason = request.data.get("reason", "")
        if not reason:
            return Response(
                {"detail": "Reason is required for rejection."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = PayrollApprovalService()
        try:
            run = service.reject(pk, rejected_by=request.user, reason=reason)
            serializer = self.get_serializer(run)
            return Response(serializer.data)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"], url_path="pending-approvals")
    def pending_approvals(self, request):
        """List all payroll runs pending approval."""
        service = PayrollApprovalService()
        pending = service.get_pending_approvals()
        serializer = PayrollRunListSerializer(pending, many=True)
        return Response(serializer.data)

    # ── Finalization ──────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="finalize")
    def finalize(self, request, pk=None):
        """Finalize this payroll run."""
        self.get_object()
        service = PayrollFinalizationService()
        try:
            run = service.finalize(pk, finalized_by=request.user)
            serializer = self.get_serializer(run)
            return Response(serializer.data)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="generate-bank-file")
    def generate_bank_file(self, request, pk=None):
        """Generate bank payment file for this run."""
        self.get_object()
        bank_code = request.data.get("bank_code", "CSV")
        service = PayrollFinalizationService()
        try:
            result = service.generate_bank_file(
                pk, bank_code=bank_code, generated_by=request.user
            )
            return Response(result)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="mark-as-paid")
    def mark_as_paid(self, request, pk=None):
        """Mark this payroll run as paid."""
        self.get_object()
        payment_reference = request.data.get("payment_reference", "")
        payment_date = request.data.get("payment_date")
        if not payment_reference:
            return Response(
                {"detail": "Payment reference is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = PayrollFinalizationService()
        try:
            run = service.mark_as_paid(
                pk,
                payment_reference=payment_reference,
                payment_date=payment_date,
                marked_by=request.user,
            )
            serializer = self.get_serializer(run)
            return Response(serializer.data)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    # ── Reversal ──────────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="reverse")
    def reverse(self, request, pk=None):
        """Reverse this payroll run."""
        self.get_object()
        reason = request.data.get("reason", "")
        if not reason:
            return Response(
                {"detail": "Reason is required for reversal."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = PayrollReversalService()
        try:
            run = service.reverse(pk, reversed_by=request.user, reason=reason)
            serializer = self.get_serializer(run)
            return Response(serializer.data)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    # ── Employee payrolls for a run ───────────────────────────

    @action(detail=True, methods=["get"], url_path="employees")
    def employees(self, request, pk=None):
        """List employee payroll records for this run."""
        self.get_object()
        queryset = EmployeePayroll.objects.filter(
            payroll_run_id=pk
        ).select_related("employee", "employee_salary").prefetch_related(
            "line_items", "line_items__component"
        )

        # Apply filtering
        employee_filter = EmployeePayrollFilter(request.query_params, queryset=queryset)
        filtered_qs = employee_filter.qs

        # Use detail serializer if single employee requested via query param
        employee_id = request.query_params.get("employee_id")
        if employee_id:
            try:
                record = filtered_qs.get(employee_id=employee_id)
                serializer = EmployeePayrollSerializer(record)
                return Response(serializer.data)
            except EmployeePayroll.DoesNotExist:
                return Response(
                    {"detail": "Employee payroll record not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = EmployeePayrollListSerializer(filtered_qs, many=True)
        return Response(serializer.data)

    # ── History / Audit trail ─────────────────────────────────

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Get audit trail for this payroll run."""
        self.get_object()
        queryset = PayrollHistory.objects.filter(
            payroll_run_id=pk
        ).select_related("performed_by")
        serializer = PayrollHistorySerializer(queryset, many=True)
        return Response(serializer.data)

    # ── Statutory returns ─────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="epf-return")
    def epf_return(self, request, pk=None):
        """Generate EPF return report for this run."""
        payroll_run = self.get_object()
        service = StatutoryReportService()
        try:
            result = service.generate_epf_return(payroll_run)
            return Response(result)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["get"], url_path="etf-return")
    def etf_return(self, request, pk=None):
        """Generate ETF return report for this run."""
        payroll_run = self.get_object()
        service = StatutoryReportService()
        try:
            result = service.generate_etf_return(payroll_run)
            return Response(result)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["get"], url_path="paye-return")
    def paye_return(self, request, pk=None):
        """Generate PAYE return report for this run."""
        payroll_run = self.get_object()
        service = StatutoryReportService()
        try:
            result = service.generate_paye_return(payroll_run)
            return Response(result)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    # ── Summary ───────────────────────────────────────────────

    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        """Generate a comprehensive payroll summary for this run."""
        payroll_run = self.get_object()
        service = StatutoryReportService()
        try:
            result = service.generate_payroll_summary(payroll_run)
            return Response(result)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="reprocess")
    def reprocess(self, request, pk=None):
        """Reprocess a rejected payroll run."""
        self.get_object()
        service = PayrollApprovalService()
        try:
            run = service.reprocess(pk, reprocessed_by=request.user)
            serializer = self.get_serializer(run)
            return Response(serializer.data)
        except (ValueError, DjangoValidationError) as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
