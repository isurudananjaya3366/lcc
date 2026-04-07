"""
Customer API endpoint tests.

Tests for CustomerViewSet including CRUD operations,
custom actions, filtering, and pagination.
"""

import io

import pytest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.customers.models import (
    Customer,
    CustomerAddress,
    CustomerPhone,
    CustomerTag,
)

pytestmark = pytest.mark.django_db


# api_client fixture is provided by conftest.py (tenant-aware)


@pytest.fixture
def sample_customer():
    return Customer.objects.create(
        first_name="John",
        last_name="Perera",
        email="john@example.com",
        phone="+94712345678",
        customer_type="individual",
        status="active",
    )


# ═══════════════════════════════════════════════════════════════════
# CRUD Tests
# ═══════════════════════════════════════════════════════════════════


class TestCustomerCRUD:

    def test_list_customers(self, api_client, sample_customer):
        response = api_client.get("/api/v1/customers/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_create_customer(self, api_client):
        data = {
            "first_name": "Jane",
            "last_name": "Silva",
            "customer_type": "individual",
            "email": "jane@example.com",
        }
        response = api_client.post("/api/v1/customers/", data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve_customer(self, api_client, sample_customer):
        response = api_client.get(f"/api/v1/customers/{sample_customer.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["customer_code"] == sample_customer.customer_code

    def test_update_customer(self, api_client, sample_customer):
        data = {"first_name": "Updated"}
        response = api_client.patch(
            f"/api/v1/customers/{sample_customer.pk}/", data
        )
        assert response.status_code == status.HTTP_200_OK

    def test_delete_customer_soft(self, api_client, sample_customer):
        response = api_client.delete(f"/api/v1/customers/{sample_customer.pk}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        sample_customer.refresh_from_db()
        assert sample_customer.is_deleted is True

    def test_unauthenticated_access(self, sample_customer):
        client = APIClient(HTTP_HOST="customers.testserver")
        response = client.get("/api/v1/customers/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ═══════════════════════════════════════════════════════════════════
# Search
# ═══════════════════════════════════════════════════════════════════


class TestCustomerSearch:

    def test_search_endpoint(self, api_client, sample_customer):
        response = api_client.get("/api/v1/customers/search/?q=John")
        assert response.status_code == status.HTTP_200_OK

    def test_search_requires_query(self, api_client):
        response = api_client.get("/api/v1/customers/search/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ═══════════════════════════════════════════════════════════════════
# Addresses
# ═══════════════════════════════════════════════════════════════════


class TestCustomerAddresses:

    def test_list_addresses(self, api_client, sample_customer):
        CustomerAddress.objects.create(
            customer=sample_customer,
            address_type="billing",
            address_line_1="123 Main St",
        )
        response = api_client.get(
            f"/api/v1/customers/{sample_customer.pk}/addresses/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_add_address(self, api_client, sample_customer):
        data = {
            "address_type": "shipping",
            "address_line_1": "456 Side St",
            "city": "Colombo",
        }
        response = api_client.post(
            f"/api/v1/customers/{sample_customer.pk}/addresses/", data
        )
        assert response.status_code == status.HTTP_201_CREATED


# ═══════════════════════════════════════════════════════════════════
# Phones
# ═══════════════════════════════════════════════════════════════════


class TestCustomerPhones:

    def test_list_phones(self, api_client, sample_customer):
        CustomerPhone.objects.create(
            customer=sample_customer,
            phone_type="mobile",
            phone_number="+94771234567",
        )
        response = api_client.get(
            f"/api/v1/customers/{sample_customer.pk}/phones/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


# ═══════════════════════════════════════════════════════════════════
# Tags
# ═══════════════════════════════════════════════════════════════════


class TestCustomerTags:

    def test_assign_tag(self, api_client, sample_customer):
        tag = CustomerTag.objects.create(name="VIP")
        response = api_client.post(
            f"/api/v1/customers/{sample_customer.pk}/tags/",
            {"tag_id": str(tag.pk)},
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_tags(self, api_client, sample_customer):
        response = api_client.get(
            f"/api/v1/customers/{sample_customer.pk}/tags/"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_remove_tag(self, api_client, sample_customer):
        tag = CustomerTag.objects.create(name="Removable")
        from apps.customers.services import CustomerTagService

        CustomerTagService.assign_tag(sample_customer.pk, tag.pk)
        response = api_client.delete(
            f"/api/v1/customers/{sample_customer.pk}/tags/{tag.pk}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


# ═══════════════════════════════════════════════════════════════════
# Statistics & Activity
# ═══════════════════════════════════════════════════════════════════


class TestCustomerStats:

    def test_statistics_endpoint(self, api_client, sample_customer):
        response = api_client.get(
            f"/api/v1/customers/{sample_customer.pk}/statistics/"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_history_endpoint(self, api_client, sample_customer):
        response = api_client.get(
            f"/api/v1/customers/{sample_customer.pk}/history/"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_activity_endpoint(self, api_client, sample_customer):
        response = api_client.get(
            f"/api/v1/customers/{sample_customer.pk}/activity/"
        )
        assert response.status_code == status.HTTP_200_OK


# ═══════════════════════════════════════════════════════════════════
# Filtering
# ═══════════════════════════════════════════════════════════════════


class TestCustomerFiltering:

    def test_filter_by_status(self, api_client, sample_customer):
        response = api_client.get("/api/v1/customers/?status=active")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_filter_by_type(self, api_client, sample_customer):
        response = api_client.get("/api/v1/customers/?customer_type=individual")
        assert response.status_code == status.HTTP_200_OK

    def test_filter_search(self, api_client, sample_customer):
        response = api_client.get("/api/v1/customers/?search=John")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_filter_has_outstanding(self, api_client):
        Customer.objects.create(
            first_name="Owe", last_name="Me",
            outstanding_balance=5000,
        )
        response = api_client.get("/api/v1/customers/?has_outstanding=true")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1


# ═══════════════════════════════════════════════════════════════════
# Import / Export
# ═══════════════════════════════════════════════════════════════════


class TestCustomerImportExport:

    def test_export_csv(self, api_client, sample_customer):
        response = api_client.get("/api/v1/customers/export/")
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "text/csv"
        assert "Customer Code" in response.content.decode()

    def test_import_csv(self, api_client):
        csv_content = b"first_name,last_name,email\nImport,Test,imp@test.com\n"
        csv_file = io.BytesIO(csv_content)
        csv_file.name = "test_import.csv"
        response = api_client.post(
            "/api/v1/customers/import/",
            {"file": csv_file},
            format="multipart",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["successful"] >= 1

    def test_import_no_file(self, api_client):
        response = api_client.post("/api/v1/customers/import/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ═══════════════════════════════════════════════════════════════════
# Merge
# ═══════════════════════════════════════════════════════════════════


class TestCustomerMerge:

    def test_merge_endpoint(self, api_client):
        primary = Customer.objects.create(
            first_name="Primary", last_name="M",
            total_purchases=10000, order_count=5,
        )
        duplicate = Customer.objects.create(
            first_name="Dup", last_name="M",
            total_purchases=3000, order_count=2,
        )
        response = api_client.post(
            "/api/v1/customers/merge/",
            {
                "primary_id": str(primary.pk),
                "duplicate_id": str(duplicate.pk),
                "reason": "Duplicates",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert "merge_id" in response.data

    def test_merge_missing_params(self, api_client):
        response = api_client.post("/api/v1/customers/merge/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ═══════════════════════════════════════════════════════════════════
# Duplicates
# ═══════════════════════════════════════════════════════════════════


class TestCustomerDuplicates:

    def test_duplicates_endpoint(self, api_client, sample_customer):
        response = api_client.get(
            f"/api/v1/customers/{sample_customer.pk}/duplicates/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)


# ═══════════════════════════════════════════════════════════════════
# Pagination
# ═══════════════════════════════════════════════════════════════════


class TestPagination:

    def test_pagination_default(self, api_client, sample_customer):
        response = api_client.get("/api/v1/customers/")
        assert "count" in response.data
        assert "results" in response.data

    def test_pagination_page_size(self, api_client, sample_customer):
        response = api_client.get("/api/v1/customers/?page_size=10")
        assert response.status_code == status.HTTP_200_OK
