"""Invoice API endpoint tests."""

import pytest
from decimal import Decimal

from rest_framework.test import APIClient

from apps.invoices.constants import InvoiceStatus, InvoiceType
from apps.invoices.models import Invoice, InvoiceLineItem

pytestmark = pytest.mark.django_db

TENANT_HOST = "invoices.testserver"


@pytest.fixture
def api_client(user):
    """Return an authenticated API client with tenant host."""
    client = APIClient(HTTP_HOST=TENANT_HOST)
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def draft_invoice(tenant_context, invoice_data, user):
    """Create a draft invoice with a line item."""
    invoice = Invoice.objects.create(**invoice_data, created_by=user)
    InvoiceLineItem.objects.create(
        invoice=invoice,
        position=1,
        description="Test Product",
        sku="TST-001",
        quantity=Decimal("2"),
        unit_price=Decimal("1000.00"),
        tax_rate=Decimal("12.00"),
        is_taxable=True,
    )
    return invoice


class TestInvoiceListEndpoint:
    """Tests for GET /api/v1/invoices/"""

    def test_list_invoices(self, api_client, draft_invoice):
        response = api_client.get("/api/v1/invoices/")
        assert response.status_code == 200
        assert len(response.data["results"]) >= 1

    def test_list_filter_by_status(self, api_client, draft_invoice):
        response = api_client.get("/api/v1/invoices/", {"status": "DRAFT"})
        assert response.status_code == 200
        assert all(
            inv["status"] == "DRAFT" for inv in response.data["results"]
        )

    def test_list_filter_by_type(self, api_client, draft_invoice):
        response = api_client.get("/api/v1/invoices/", {"type": "STANDARD"})
        assert response.status_code == 200
        assert all(
            inv["type"] == "STANDARD" for inv in response.data["results"]
        )

    def test_list_unauthenticated(self, tenant_context):
        client = APIClient(HTTP_HOST=TENANT_HOST)
        response = client.get("/api/v1/invoices/")
        assert response.status_code in (401, 403)


class TestInvoiceCreateEndpoint:
    """Tests for POST /api/v1/invoices/"""

    def test_create_invoice(self, api_client, tenant_context):
        data = {
            "type": "STANDARD",
            "currency": "LKR",
        }
        response = api_client.post("/api/v1/invoices/", data, format="json")
        assert response.status_code == 201
        assert response.data["status"] == "DRAFT"

    def test_create_invoice_with_notes(self, api_client, tenant_context):
        data = {
            "type": "STANDARD",
            "currency": "LKR",
            "notes": "Test invoice notes",
        }
        response = api_client.post("/api/v1/invoices/", data, format="json")
        assert response.status_code == 201


class TestInvoiceRetrieveEndpoint:
    """Tests for GET /api/v1/invoices/{id}/"""

    def test_retrieve_invoice(self, api_client, draft_invoice):
        response = api_client.get(f"/api/v1/invoices/{draft_invoice.id}/")
        assert response.status_code == 200
        assert response.data["id"] == str(draft_invoice.id)

    def test_retrieve_nonexistent(self, api_client, tenant_context):
        import uuid
        response = api_client.get(f"/api/v1/invoices/{uuid.uuid4()}/")
        assert response.status_code == 404


class TestInvoiceActionEndpoints:
    """Tests for custom action endpoints."""

    def test_issue_invoice(self, api_client, draft_invoice):
        response = api_client.post(
            f"/api/v1/invoices/{draft_invoice.id}/issue/"
        )
        assert response.status_code == 200
        assert response.data["status"] == "ISSUED"

    def test_issue_already_issued(self, api_client, draft_invoice):
        api_client.post(f"/api/v1/invoices/{draft_invoice.id}/issue/")
        response = api_client.post(
            f"/api/v1/invoices/{draft_invoice.id}/issue/"
        )
        assert response.status_code == 400

    def test_cancel_draft(self, api_client, draft_invoice):
        response = api_client.post(
            f"/api/v1/invoices/{draft_invoice.id}/cancel/",
            {"notes": "Test cancel"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == "CANCELLED"

    def test_void_issued_invoice(self, api_client, draft_invoice):
        api_client.post(f"/api/v1/invoices/{draft_invoice.id}/issue/")
        response = api_client.post(
            f"/api/v1/invoices/{draft_invoice.id}/void/",
            {"notes": "Test void"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == "VOID"

    def test_mark_paid(self, api_client, draft_invoice):
        api_client.post(f"/api/v1/invoices/{draft_invoice.id}/issue/")
        response = api_client.post(
            f"/api/v1/invoices/{draft_invoice.id}/mark-paid/",
            format="json",
        )
        assert response.status_code == 200

    def test_duplicate_invoice(self, api_client, draft_invoice):
        response = api_client.post(
            f"/api/v1/invoices/{draft_invoice.id}/duplicate/"
        )
        assert response.status_code == 201
        assert response.data["status"] == "DRAFT"
        assert response.data["id"] != str(draft_invoice.id)


class TestAgingReportEndpoint:
    """Tests for GET /api/v1/invoices/reports/aging/"""

    def test_aging_report(self, api_client, tenant_context):
        response = api_client.get("/api/v1/invoices/reports/aging/")
        assert response.status_code == 200
        assert "current" in response.data
        assert "30_days" in response.data
        assert "60_days" in response.data
        assert "90_days" in response.data
        assert "90_plus" in response.data
        assert "total" in response.data
