"""
Task 81 (API): Receipt API Endpoint Tests.

Tests for receipt and template API endpoints including
list, retrieve, generate, print, email, PDF, search, and export.
"""

import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


# ── Receipt List & Retrieve ───────────────────────────────────


class TestReceiptListAPI:
    """Tests for GET /api/v1/pos/receipts/"""

    def test_list_unauthenticated(self, api_client):
        url = reverse("pos:receipt-list")
        resp = api_client.get(url)
        assert resp.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )

    def test_list_authenticated(self, authenticated_client, receipt):
        url = reverse("pos:receipt-list")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    def test_list_contains_receipt(self, authenticated_client, receipt):
        url = reverse("pos:receipt-list")
        resp = authenticated_client.get(url)
        data = resp.json()
        results = data.get("results", data)
        receipt_numbers = [r["receipt_number"] for r in results]
        assert receipt.receipt_number in receipt_numbers


class TestReceiptRetrieveAPI:
    """Tests for GET /api/v1/pos/receipts/{id}/"""

    def test_retrieve_receipt(self, authenticated_client, receipt):
        url = reverse("pos:receipt-detail", kwargs={"pk": receipt.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["receipt_number"] == receipt.receipt_number

    def test_retrieve_not_found(self, authenticated_client):
        import uuid

        url = reverse(
            "pos:receipt-detail", kwargs={"pk": uuid.uuid4()}
        )
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND


# ── Receipt Generate ──────────────────────────────────────────


class TestReceiptGenerateAPI:
    """Tests for POST /api/v1/pos/receipts/generate/"""

    def test_generate_receipt(
        self, authenticated_client, completed_cart, receipt_template
    ):
        url = reverse("pos:receipt-generate")
        data = {
            "cart": str(completed_cart.pk),
            "receipt_type": "SALE",
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert "receipt_number" in resp.json()

    def test_generate_with_template(
        self, authenticated_client, completed_cart, receipt_template
    ):
        url = reverse("pos:receipt-generate")
        data = {
            "cart": str(completed_cart.pk),
            "receipt_type": "SALE",
            "template": str(receipt_template.pk),
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED

    def test_generate_invalid_cart(
        self, authenticated_client, receipt_template
    ):
        import uuid

        url = reverse("pos:receipt-generate")
        data = {
            "cart": str(uuid.uuid4()),
            "receipt_type": "SALE",
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_generate_active_cart_fails(
        self, authenticated_client, cart, receipt_template
    ):
        """Cannot generate receipt for non-completed cart."""
        url = reverse("pos:receipt-generate")
        data = {
            "cart": str(cart.pk),
            "receipt_type": "SALE",
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── Receipt PDF Download ──────────────────────────────────────


class TestReceiptPDFAPI:
    """Tests for GET /api/v1/pos/receipts/{id}/pdf/"""

    def test_download_pdf(self, authenticated_client, receipt):
        url = reverse("pos:receipt-pdf", kwargs={"pk": receipt.pk})
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert "application/pdf" in resp["Content-Type"]

    def test_download_pdf_unauthenticated(self, api_client, receipt):
        url = reverse("pos:receipt-pdf", kwargs={"pk": receipt.pk})
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# ── Receipt Email ─────────────────────────────────────────────


class TestReceiptEmailAPI:
    """Tests for POST /api/v1/pos/receipts/{id}/email/"""

    def test_email_requires_email_field(
        self, authenticated_client, receipt
    ):
        url = reverse(
            "pos:receipt-email", kwargs={"pk": receipt.pk}
        )
        resp = authenticated_client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_email_invalid_address(
        self, authenticated_client, receipt
    ):
        url = reverse(
            "pos:receipt-email", kwargs={"pk": receipt.pk}
        )
        data = {"email": "not-an-email"}
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── Receipt Duplicate ─────────────────────────────────────────


class TestReceiptDuplicateAPI:
    """Tests for POST /api/v1/pos/receipts/{id}/duplicate/"""

    def test_create_duplicate(self, authenticated_client, receipt):
        url = reverse(
            "pos:receipt-duplicate", kwargs={"pk": receipt.pk}
        )
        resp = authenticated_client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["receipt_type"] == "DUPLICATE"


# ── Receipt Search ────────────────────────────────────────────


class TestReceiptSearchAPI:
    """Tests for GET /api/v1/pos/receipts/search/"""

    def test_search_by_number(self, authenticated_client, receipt):
        url = reverse("pos:receipt-search")
        resp = authenticated_client.get(
            url, {"query": receipt.receipt_number}
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_search_by_type(self, authenticated_client, receipt):
        url = reverse("pos:receipt-search")
        resp = authenticated_client.get(
            url, {"receipt_type": "SALE"}
        )
        assert resp.status_code == status.HTTP_200_OK

    def test_search_with_date_range(self, authenticated_client, receipt):
        url = reverse("pos:receipt-search")
        resp = authenticated_client.get(
            url,
            {
                "date_from": "2020-01-01",
                "date_to": "2099-12-31",
            },
        )
        assert resp.status_code == status.HTTP_200_OK


# ── Receipt Export ────────────────────────────────────────────


class TestReceiptExportAPI:
    """Tests for GET /api/v1/pos/receipts/export/"""

    def test_export_csv(self, authenticated_client, receipt):
        url = reverse("pos:receipt-export")
        resp = authenticated_client.get(url, {"format": "csv"})
        assert resp.status_code == status.HTTP_200_OK
        assert "text/csv" in resp["Content-Type"]

    def test_export_json(self, authenticated_client, receipt):
        url = reverse("pos:receipt-export")
        resp = authenticated_client.get(url, {"format": "json"})
        assert resp.status_code == status.HTTP_200_OK
        assert "application/json" in resp["Content-Type"]

    def test_export_with_date_filter(
        self, authenticated_client, receipt
    ):
        url = reverse("pos:receipt-export")
        resp = authenticated_client.get(
            url,
            {
                "format": "csv",
                "date_from": "2020-01-01",
                "date_to": "2099-12-31",
            },
        )
        assert resp.status_code == status.HTTP_200_OK


# ── Template API ──────────────────────────────────────────────


class TestReceiptTemplateListAPI:
    """Tests for GET /api/v1/pos/receipt-templates/"""

    def test_list_unauthenticated(self, api_client):
        url = reverse("pos:receipt-template-list")
        resp = api_client.get(url)
        assert resp.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND,
        )

    def test_list_authenticated(
        self, authenticated_client, receipt_template
    ):
        url = reverse("pos:receipt-template-list")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK


class TestReceiptTemplateCreateAPI:
    """Tests for POST /api/v1/pos/receipt-templates/"""

    def test_create_template(self, authenticated_client):
        url = reverse("pos:receipt-template-list")
        data = {
            "name": "New Template",
            "paper_size": "80mm",
            "description": "A new template",
        }
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED


class TestReceiptTemplateActionsAPI:
    """Tests for template custom actions."""

    def test_set_default(
        self, authenticated_client, receipt_template
    ):
        url = reverse(
            "pos:receipt-template-set-default",
            kwargs={"pk": receipt_template.pk},
        )
        resp = authenticated_client.post(url, {}, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json()["is_default"] is True

    def test_clone_template(
        self, authenticated_client, receipt_template
    ):
        url = reverse(
            "pos:receipt-template-clone",
            kwargs={"pk": receipt_template.pk},
        )
        data = {"new_name": "Cloned Template via API"}
        resp = authenticated_client.post(url, data, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json()["name"] == "Cloned Template via API"

    def test_usage_stats(
        self, authenticated_client, receipt_template
    ):
        url = reverse(
            "pos:receipt-template-usage",
            kwargs={"pk": receipt_template.pk},
        )
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert "total_receipts" in resp.json()
