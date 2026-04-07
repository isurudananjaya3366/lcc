"""Tests for SP06 Payroll Processing services."""

import pytest
from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError

from apps.payroll.constants import PayrollStatus, PaymentStatus, HistoryAction

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────────────────────
# PayrollApprovalService Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollApprovalService:
    """Tests for the PayrollApprovalService."""

    def test_submit_for_approval(self, processed_run, user, tenant_context):
        from apps.payroll.services.approval_service import PayrollApprovalService

        service = PayrollApprovalService()
        result = service.submit_for_approval(processed_run.pk, submitted_by=user)
        assert result.status == PayrollStatus.PENDING_APPROVAL

    def test_submit_draft_run_fails(self, payroll_run, user, tenant_context):
        from apps.payroll.services.approval_service import PayrollApprovalService

        service = PayrollApprovalService()
        with pytest.raises(ValidationError):
            service.submit_for_approval(payroll_run.pk, submitted_by=user)

    def test_approve_run(self, processed_run, staff_user, approver_user, tenant_context):
        from apps.payroll.services.approval_service import PayrollApprovalService

        service = PayrollApprovalService()
        service.submit_for_approval(processed_run.pk, submitted_by=staff_user)
        result = service.approve(processed_run.pk, approved_by=approver_user, notes="Approved")
        assert result.status == PayrollStatus.APPROVED

    def test_reject_run(self, processed_run, staff_user, tenant_context):
        from apps.payroll.services.approval_service import PayrollApprovalService

        service = PayrollApprovalService()
        service.submit_for_approval(processed_run.pk, submitted_by=staff_user)
        result = service.reject(
            processed_run.pk, rejected_by=staff_user, reason="Incorrect values"
        )
        assert result.status == PayrollStatus.REJECTED

    def test_approve_without_permission_fails(self, processed_run, user, tenant_context):
        from apps.payroll.services.approval_service import PayrollApprovalService

        service = PayrollApprovalService()
        service.submit_for_approval(processed_run.pk, submitted_by=user)
        with pytest.raises(PermissionDenied):
            service.approve(processed_run.pk, approved_by=user)

    def test_get_pending_approvals(self, processed_run, user, tenant_context):
        from apps.payroll.services.approval_service import PayrollApprovalService

        service = PayrollApprovalService()
        service.submit_for_approval(processed_run.pk, submitted_by=user)
        pending = service.get_pending_approvals()
        assert pending.count() >= 1

    def test_get_approval_history(self, processed_run, user, tenant_context):
        from apps.payroll.services.approval_service import PayrollApprovalService

        service = PayrollApprovalService()
        service.submit_for_approval(processed_run.pk, submitted_by=user)
        history = service.get_approval_history(processed_run.pk)
        assert len(history) >= 1


# ──────────────────────────────────────────────────────────────
# PayrollFinalizationService Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollFinalizationService:
    """Tests for the PayrollFinalizationService."""

    def _make_approved_run(self, processed_run, staff_user, approver_user):
        from apps.payroll.services.approval_service import PayrollApprovalService

        service = PayrollApprovalService()
        service.submit_for_approval(processed_run.pk, submitted_by=staff_user)
        service.approve(processed_run.pk, approved_by=approver_user)

    def test_finalize_run(self, processed_run, staff_user, approver_user, tenant_context):
        from apps.payroll.services.finalization_service import PayrollFinalizationService

        self._make_approved_run(processed_run, staff_user, approver_user)
        service = PayrollFinalizationService()
        result = service.finalize(processed_run.pk, finalized_by=staff_user)
        assert result.status == PayrollStatus.FINALIZED

    def test_finalize_non_approved_fails(self, processed_run, staff_user, tenant_context):
        from apps.payroll.services.finalization_service import PayrollFinalizationService

        service = PayrollFinalizationService()
        with pytest.raises(ValidationError):
            service.finalize(processed_run.pk, finalized_by=staff_user)

    def test_get_bank_file_formats(self, tenant_context):
        from apps.payroll.services.finalization_service import PayrollFinalizationService

        service = PayrollFinalizationService()
        formats = service.get_bank_file_formats()
        assert isinstance(formats, dict)
        assert len(formats) > 0

    def test_get_finalization_status(self, processed_run, staff_user, approver_user, tenant_context):
        from apps.payroll.services.finalization_service import PayrollFinalizationService

        self._make_approved_run(processed_run, staff_user, approver_user)
        service = PayrollFinalizationService()
        service.finalize(processed_run.pk, finalized_by=staff_user)
        status_info = service.get_finalization_status(processed_run.pk)
        assert status_info is not None


# ──────────────────────────────────────────────────────────────
# PayrollReversalService Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollReversalService:
    """Tests for the PayrollReversalService."""

    def _make_finalized_run(self, processed_run, staff_user, approver_user):
        from apps.payroll.services.approval_service import PayrollApprovalService
        from apps.payroll.services.finalization_service import PayrollFinalizationService

        approval_svc = PayrollApprovalService()
        approval_svc.submit_for_approval(processed_run.pk, submitted_by=staff_user)
        approval_svc.approve(processed_run.pk, approved_by=approver_user)

        fin_svc = PayrollFinalizationService()
        fin_svc.finalize(processed_run.pk, finalized_by=staff_user)

    def test_reverse_run(self, processed_run, staff_user, approver_user, tenant_context):
        from apps.payroll.services.reversal_service import PayrollReversalService

        self._make_finalized_run(processed_run, staff_user, approver_user)
        service = PayrollReversalService()
        result = service.reverse(
            processed_run.pk, reversed_by=staff_user, reason="Error found"
        )
        assert result.status == PayrollStatus.REVERSED

    def test_reverse_non_finalized_fails(self, processed_run, staff_user, tenant_context):
        from apps.payroll.services.reversal_service import PayrollReversalService

        service = PayrollReversalService()
        with pytest.raises((ValidationError, PermissionDenied)):
            service.reverse(
                processed_run.pk, reversed_by=staff_user, reason="Test"
            )

    def test_reverse_without_permission_fails(self, processed_run, user, tenant_context):
        from apps.payroll.services.reversal_service import PayrollReversalService

        service = PayrollReversalService()
        with pytest.raises(PermissionDenied):
            service.reverse(
                processed_run.pk, reversed_by=user, reason="Test"
            )


# ──────────────────────────────────────────────────────────────
# StatutoryReportService Tests
# ──────────────────────────────────────────────────────────────


class TestStatutoryReportService:
    """Tests for the StatutoryReportService."""

    def test_generate_epf_return(self, processed_run, tenant_context):
        from apps.payroll.services.statutory_reports import StatutoryReportService

        service = StatutoryReportService()
        result = service.generate_epf_return(processed_run)
        assert isinstance(result, dict)

    def test_generate_etf_return(self, processed_run, tenant_context):
        from apps.payroll.services.statutory_reports import StatutoryReportService

        service = StatutoryReportService()
        result = service.generate_etf_return(processed_run)
        assert isinstance(result, dict)

    def test_generate_paye_return(self, processed_run, tenant_context):
        from apps.payroll.services.statutory_reports import StatutoryReportService

        service = StatutoryReportService()
        result = service.generate_paye_return(processed_run)
        assert isinstance(result, dict)
