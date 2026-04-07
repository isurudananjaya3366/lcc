"""Production-level API tests for payslip endpoints — Task 86-88.

Uses real Docker PostgreSQL database, tenant isolation, and
DRF APIClient with HTTP_HOST for django-tenants resolution.
"""

import pytest
from decimal import Decimal

from rest_framework import status as http_status

pytestmark = pytest.mark.django_db


# ──────────────────────────────────────────────────────────────
# Employee Self-Service Endpoints
# ──────────────────────────────────────────────────────────────


class TestEmployeePayslipListAPI:
    """GET /api/v1/payslips/my/ — employee self-service list."""

    def test_unauthenticated_returns_401_or_403(self, api_client, tenant_context):
        response = api_client.get("/api/v1/payslips/my/")
        assert response.status_code in (
            http_status.HTTP_401_UNAUTHORIZED,
            http_status.HTTP_403_FORBIDDEN,
        )

    def test_employee_sees_own_payslips(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/payslips/my/")
        assert response.status_code == http_status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["slip_number"] == payslip_with_lines.slip_number

    def test_employee_cannot_see_others_payslips(
        self, api_client, tenant_context, admin_user, payslip_with_lines
    ):
        """Admin is not linked to any employee — should see zero payslips."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/payslips/my/")
        assert response.status_code == http_status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) == 0

    def test_list_contains_expected_fields(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/payslips/my/")
        results = response.data.get("results", response.data)
        item = results[0]
        for field in [
            "id", "slip_number", "employee_name", "period_name",
            "status", "email_sent", "view_count", "download_count",
            "generated_at", "pdf_available",
        ]:
            assert field in item, f"Missing field: {field}"


class TestEmployeePayslipDetailAPI:
    """GET /api/v1/payslips/my/{id}/ — retrieve + view tracking."""

    def test_retrieve_increments_view_count(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        assert payslip_with_lines.view_count == 0

        response = api_client.get(f"/api/v1/payslips/my/{payslip_with_lines.pk}/")
        assert response.status_code == http_status.HTTP_200_OK

        payslip_with_lines.refresh_from_db()
        assert payslip_with_lines.view_count == 1
        assert payslip_with_lines.first_viewed_at is not None

    def test_detail_contains_nested_earnings(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/payslips/my/{payslip_with_lines.pk}/")
        data = response.data
        assert "earnings" in data
        assert len(data["earnings"]) == 2
        assert "deductions" in data
        assert len(data["deductions"]) == 1

    def test_detail_has_summary(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/payslips/my/{payslip_with_lines.pk}/")
        summary = response.data["summary"]
        assert Decimal(summary["total_earnings"]) == Decimal("55000.00")
        assert Decimal(summary["total_deductions"]) == Decimal("4000.00")
        assert Decimal(summary["net_pay"]) == Decimal("51000.00")


class TestEmployeePayslipDownloadAPI:
    """GET /api/v1/payslips/my/{id}/download/ — PDF download."""

    def test_download_no_pdf_returns_404(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.get(
            f"/api/v1/payslips/my/{payslip_with_lines.pk}/download/"
        )
        assert response.status_code == http_status.HTTP_404_NOT_FOUND

    def test_unauthenticated_download_returns_401_or_403(self, api_client, tenant_context):
        response = api_client.get("/api/v1/payslips/my/some-id/download/")
        assert response.status_code in (
            http_status.HTTP_401_UNAUTHORIZED,
            http_status.HTTP_403_FORBIDDEN,
            http_status.HTTP_404_NOT_FOUND,  # tenant middleware may 404
        )


# ──────────────────────────────────────────────────────────────
# Admin Payslip Endpoints
# ──────────────────────────────────────────────────────────────


class TestAdminPayslipListAPI:
    """GET /api/v1/payslips/admin/payslips/ — admin list."""

    def test_admin_can_list_all_payslips(self, api_client, admin_user, payslip_with_lines):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/payslips/admin/payslips/")
        assert response.status_code == http_status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) >= 1

    def test_non_admin_gets_403(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/payslips/admin/payslips/")
        assert response.status_code == http_status.HTTP_403_FORBIDDEN


class TestAdminPayslipRetrieveAPI:
    """GET /api/v1/payslips/admin/payslips/{id}/ — admin detail."""

    def test_admin_retrieve_payslip(self, api_client, admin_user, payslip_with_lines):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(
            f"/api/v1/payslips/admin/payslips/{payslip_with_lines.pk}/"
        )
        assert response.status_code == http_status.HTTP_200_OK
        assert response.data["slip_number"] == payslip_with_lines.slip_number
        assert "earnings" in response.data
        assert "summary" in response.data


class TestAdminGenerateAPI:
    """POST /api/v1/payslips/admin/payslips/{id}/generate/ — single PDF gen."""

    def test_non_admin_cannot_generate(self, api_client, user, payslip_with_lines, payslip_template):
        api_client.force_authenticate(user=user)
        response = api_client.post(
            f"/api/v1/payslips/admin/payslips/{payslip_with_lines.pk}/generate/"
        )
        assert response.status_code == http_status.HTTP_403_FORBIDDEN


class TestAdminSendEmailAPI:
    """POST /api/v1/payslips/admin/payslips/{id}/send-email/ — email action."""

    def test_send_email_on_draft_returns_400(
        self, api_client, admin_user, payslip_with_lines, payslip_template
    ):
        """Cannot send email for a payslip that has no PDF."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(
            f"/api/v1/payslips/admin/payslips/{payslip_with_lines.pk}/send-email/"
        )
        assert response.status_code == http_status.HTTP_400_BAD_REQUEST

    def test_non_admin_cannot_send_email(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.post(
            f"/api/v1/payslips/admin/payslips/{payslip_with_lines.pk}/send-email/"
        )
        assert response.status_code == http_status.HTTP_403_FORBIDDEN


# ──────────────────────────────────────────────────────────────
# Admin Batch Endpoints
# ──────────────────────────────────────────────────────────────


class TestPayslipBatchAPI:
    """Batch management endpoints."""

    def test_list_batches_admin(self, api_client, admin_user, tenant_context):
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/v1/payslips/admin/batches/")
        assert response.status_code == http_status.HTTP_200_OK

    def test_list_batches_non_admin_403(self, api_client, user, tenant_context):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/payslips/admin/batches/")
        assert response.status_code == http_status.HTTP_403_FORBIDDEN

    def test_batch_status_action(self, api_client, admin_user, payroll_period, tenant_context):
        from apps.payslip.models import PayslipBatch

        batch = PayslipBatch.objects.create(
            payroll_period=payroll_period,
            initiated_by=admin_user,
            batch_type="GENERATION",
            status="PENDING",
            total_count=5,
        )
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(
            f"/api/v1/payslips/admin/batches/{batch.pk}/status/"
        )
        assert response.status_code == http_status.HTTP_200_OK
        data = response.data
        assert data["batch_type"] == "GENERATION"
        assert data["status"] == "PENDING"
        assert data["progress"]["total"] == 5
        assert data["progress"]["percent"] is not None


# ──────────────────────────────────────────────────────────────
# Serializer Output Verification
# ──────────────────────────────────────────────────────────────


class TestSerializerOutput:
    """Verify serializer field coverage and data correctness."""

    def test_list_serializer_fields(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/payslips/my/")
        item = response.data.get("results", response.data)[0]
        assert item["pdf_available"] is False
        assert item["email_sent"] is False
        assert item["view_count"] == 0
        assert item["status"] == "DRAFT"

    def test_detail_serializer_earnings_structure(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/payslips/my/{payslip_with_lines.pk}/")
        earning = response.data["earnings"][0]
        for field in ["component_code", "component_name", "amount", "ytd_amount", "display_order"]:
            assert field in earning, f"Earning missing field: {field}"

    def test_detail_serializer_deductions_structure(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        response = api_client.get(f"/api/v1/payslips/my/{payslip_with_lines.pk}/")
        deduction = response.data["deductions"][0]
        assert deduction["component_code"] == "EPF_EE"
        assert Decimal(deduction["amount"]) == Decimal("4000.00")

    def test_multiple_views_increment_counter(self, api_client, user, payslip_with_lines):
        api_client.force_authenticate(user=user)
        api_client.get(f"/api/v1/payslips/my/{payslip_with_lines.pk}/")
        api_client.get(f"/api/v1/payslips/my/{payslip_with_lines.pk}/")
        api_client.get(f"/api/v1/payslips/my/{payslip_with_lines.pk}/")
        payslip_with_lines.refresh_from_db()
        assert payslip_with_lines.view_count == 3
