"""Tests for purchases API endpoints."""

import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

TENANT_DOMAIN = "purchases.testserver"


@pytest.fixture
def api_client(user):
    """Authenticated API client for tenant."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    return client


class TestPOAPI:
    """Tests for PurchaseOrder API."""

    def test_list_pos(self, api_client, purchase_order):
        response = api_client.get("/api/v1/purchase-orders/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_po(self, api_client, vendor):
        data = {
            "vendor": str(vendor.pk),
            "order_date": "2025-01-01",
        }
        response = api_client.post("/api/v1/purchase-orders/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["po_number"].startswith("PO-")

    def test_retrieve_po(self, api_client, purchase_order):
        response = api_client.get(f"/api/v1/purchase-orders/{purchase_order.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["po_number"] == purchase_order.po_number

    def test_send_po(self, api_client, po_with_lines):
        response = api_client.post(
            f"/api/v1/purchase-orders/{po_with_lines.pk}/send/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "sent"

    def test_cancel_po(self, api_client, po_with_lines):
        response = api_client.post(
            f"/api/v1/purchase-orders/{po_with_lines.pk}/cancel/",
            {"reason": "Testing"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "cancelled"

    def test_duplicate_po(self, api_client, po_with_lines):
        response = api_client.post(
            f"/api/v1/purchase-orders/{po_with_lines.pk}/duplicate/"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["po_number"] != po_with_lines.po_number


class TestGRNAPI:
    """Tests for GoodsReceipt API."""

    def test_list_grns(self, api_client, purchase_order):
        response = api_client.get("/api/v1/goods-receipts/")
        assert response.status_code == status.HTTP_200_OK
