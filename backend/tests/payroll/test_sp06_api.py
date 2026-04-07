"""Tests for SP06 Payroll API endpoints."""

import pytest
from decimal import Decimal
from datetime import date

from rest_framework.test import APIClient
from rest_framework import status

from apps.payroll.constants import PayrollStatus

pytestmark = pytest.mark.django_db

TENANT_DOMAIN = "payroll.testserver"


@pytest.fixture
def api_client(user):
    """Authenticated API client with tenant header."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def staff_api_client(staff_user):
    """Authenticated staff API client with tenant header (has approval perms)."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=staff_user)
    return client


@pytest.fixture
def approver_api_client(approver_user):
    """Authenticated approver API client (different user for self-approval prevention)."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=approver_user)
    return client


# ──────────────────────────────────────────────────────────────
# PayrollPeriod API Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollPeriodAPI:
    """Tests for PayrollPeriod API endpoints."""

    def test_list_periods(self, api_client, payroll_period):
        response = api_client.get("/api/v1/payroll/periods/")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_period(self, api_client, payroll_period):
        response = api_client.get(f"/api/v1/payroll/periods/{payroll_period.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "January 2024"

    def test_create_period(self, api_client, tenant_context):
        data = {
            "period_month": 2,
            "period_year": 2024,
            "name": "February 2024",
            "start_date": "2024-02-01",
            "end_date": "2024-02-29",
            "pay_date": "2024-02-25",
            "total_working_days": 21,
        }
        response = api_client.post("/api/v1/payroll/periods/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "February 2024"

    def test_lock_period(self, api_client, payroll_period):
        response = api_client.post(
            f"/api/v1/payroll/periods/{payroll_period.pk}/lock/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_locked"] is True

    def test_lock_already_locked(self, api_client, payroll_period):
        api_client.post(f"/api/v1/payroll/periods/{payroll_period.pk}/lock/")
        response = api_client.post(
            f"/api/v1/payroll/periods/{payroll_period.pk}/lock/"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unlock_period(self, api_client, payroll_period):
        api_client.post(f"/api/v1/payroll/periods/{payroll_period.pk}/lock/")
        response = api_client.post(
            f"/api/v1/payroll/periods/{payroll_period.pk}/unlock/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_locked"] is False

    def test_unlock_not_locked(self, api_client, payroll_period):
        response = api_client.post(
            f"/api/v1/payroll/periods/{payroll_period.pk}/unlock/"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_access(self, payroll_period):
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        response = client.get("/api/v1/payroll/periods/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ──────────────────────────────────────────────────────────────
# PayrollRun API Tests
# ──────────────────────────────────────────────────────────────


class TestPayrollRunAPI:
    """Tests for PayrollRun API endpoints."""

    def test_list_runs(self, api_client, payroll_run):
        response = api_client.get("/api/v1/payroll/runs/")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_run(self, api_client, payroll_run):
        response = api_client.get(f"/api/v1/payroll/runs/{payroll_run.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["run_number"] == 1

    def test_create_run(self, api_client, payroll_period):
        data = {
            "payroll_period": str(payroll_period.pk),
            "run_number": 3,
            "notes": "Test run",
        }
        response = api_client.post("/api/v1/payroll/runs/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_submit_for_approval(self, staff_api_client, processed_run):
        response = staff_api_client.post(
            f"/api/v1/payroll/runs/{processed_run.pk}/submit-for-approval/"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_submit_draft_fails(self, api_client, payroll_run):
        response = api_client.post(
            f"/api/v1/payroll/runs/{payroll_run.pk}/submit-for-approval/"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_approve_run(self, staff_api_client, approver_api_client, processed_run):
        staff_api_client.post(
            f"/api/v1/payroll/runs/{processed_run.pk}/submit-for-approval/"
        )
        response = approver_api_client.post(
            f"/api/v1/payroll/runs/{processed_run.pk}/approve/",
            {"notes": "LGTM"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_reject_run_requires_reason(self, staff_api_client, processed_run):
        staff_api_client.post(
            f"/api/v1/payroll/runs/{processed_run.pk}/submit-for-approval/"
        )
        response = staff_api_client.post(
            f"/api/v1/payroll/runs/{processed_run.pk}/reject/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reject_run_with_reason(self, staff_api_client, processed_run):
        staff_api_client.post(
            f"/api/v1/payroll/runs/{processed_run.pk}/submit-for-approval/"
        )
        response = staff_api_client.post(
            f"/api/v1/payroll/runs/{processed_run.pk}/reject/",
            {"reason": "Incorrect calculations"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_employees_endpoint(self, api_client, payroll_run, employee_payroll_record):
        response = api_client.get(
            f"/api/v1/payroll/runs/{payroll_run.pk}/employees/"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_history_endpoint(self, api_client, payroll_run):
        response = api_client.get(
            f"/api/v1/payroll/runs/{payroll_run.pk}/history/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_pending_approvals_endpoint(self, api_client, tenant_context):
        response = api_client.get("/api/v1/payroll/runs/pending-approvals/")
        assert response.status_code == status.HTTP_200_OK

    def test_reverse_requires_reason(self, api_client, processed_run):
        response = api_client.post(
            f"/api/v1/payroll/runs/{processed_run.pk}/reverse/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_epf_return_endpoint(self, api_client, processed_run):
        response = api_client.get(
            f"/api/v1/payroll/runs/{processed_run.pk}/epf-return/"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_etf_return_endpoint(self, api_client, processed_run):
        response = api_client.get(
            f"/api/v1/payroll/runs/{processed_run.pk}/etf-return/"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_paye_return_endpoint(self, api_client, processed_run):
        response = api_client.get(
            f"/api/v1/payroll/runs/{processed_run.pk}/paye-return/"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_access(self, payroll_run):
        client = APIClient(HTTP_HOST=TENANT_DOMAIN)
        response = client.get("/api/v1/payroll/runs/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
