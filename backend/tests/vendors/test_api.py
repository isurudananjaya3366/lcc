"""Tests for vendor API endpoints."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestVendorAPI:
    """Test vendor CRUD endpoints."""

    def test_list_vendors(self, api_client, vendor):
        response = api_client.get("/api/v1/vendors/")
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_create_vendor(self, api_client, tenant_context):
        data = {
            "company_name": "API Created Vendor",
            "vendor_type": "distributor",
        }
        response = api_client.post("/api/v1/vendors/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["company_name"] == "API Created Vendor"

    def test_retrieve_vendor(self, api_client, vendor):
        response = api_client.get(f"/api/v1/vendors/{vendor.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["company_name"] == "Test Vendor Co"

    def test_update_vendor(self, api_client, vendor):
        data = {"company_name": "Updated API Vendor", "vendor_type": "manufacturer"}
        response = api_client.put(f"/api/v1/vendors/{vendor.pk}/", data)
        assert response.status_code == status.HTTP_200_OK

    def test_partial_update_vendor(self, api_client, vendor):
        response = api_client.patch(
            f"/api/v1/vendors/{vendor.pk}/",
            {"company_name": "Patched Vendor"},
        )
        assert response.status_code == status.HTTP_200_OK

    def test_delete_vendor(self, api_client, vendor):
        response = api_client.delete(f"/api/v1/vendors/{vendor.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_unauthenticated_access(self, vendor):
        client = APIClient(HTTP_HOST="vendors.testserver")
        response = client.get("/api/v1/vendors/")
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )


class TestVendorContactsAPI:
    """Test vendor contacts endpoint."""

    def test_list_contacts(self, api_client, vendor, vendor_contact):
        response = api_client.get(
            f"/api/v1/vendors/{vendor.pk}/contacts/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_contact(self, api_client, vendor):
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@test.com",
            "role": "accounts",
        }
        response = api_client.post(
            f"/api/v1/vendors/{vendor.pk}/contacts/", data
        )
        assert response.status_code == status.HTTP_201_CREATED


class TestVendorAddressesAPI:
    """Test vendor addresses endpoint."""

    def test_list_addresses(self, api_client, vendor, vendor_address):
        response = api_client.get(
            f"/api/v1/vendors/{vendor.pk}/addresses/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_create_address(self, api_client, vendor):
        data = {
            "address_type": "shipping",
            "address_line_1": "99 Harbor Rd",
            "city": "Galle",
        }
        response = api_client.post(
            f"/api/v1/vendors/{vendor.pk}/addresses/", data
        )
        assert response.status_code == status.HTTP_201_CREATED


class TestVendorBankAccountsAPI:
    """Test vendor bank accounts endpoint."""

    def test_list_bank_accounts(self, api_client, vendor, vendor_bank):
        response = api_client.get(
            f"/api/v1/vendors/{vendor.pk}/bank-accounts/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


class TestVendorFilteringAPI:
    """Test vendor filtering."""

    def test_filter_by_status(self, api_client, vendor):
        response = api_client.get("/api/v1/vendors/?status=active")
        assert response.status_code == status.HTTP_200_OK

    def test_filter_by_vendor_type(self, api_client, vendor):
        response = api_client.get(
            "/api/v1/vendors/?vendor_type=manufacturer"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_search(self, api_client, vendor):
        response = api_client.get("/api/v1/vendors/?search=Test")
        assert response.status_code == status.HTTP_200_OK

    def test_ordering(self, api_client, vendor):
        response = api_client.get("/api/v1/vendors/?ordering=-rating")
        assert response.status_code == status.HTTP_200_OK


class TestVendorExportAPI:
    """Test vendor export endpoint."""

    def test_export_csv(self, api_client, vendor):
        response = api_client.get("/api/v1/vendors/export/")
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "text/csv"


class TestVendorSearchAPI:
    """Test vendor search endpoint."""

    def test_search_vendors(self, api_client, vendor):
        response = api_client.get("/api/v1/vendors/search/?q=Test")
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_search_requires_query(self, api_client, vendor):
        response = api_client.get("/api/v1/vendors/search/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
