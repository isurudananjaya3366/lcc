"""Tests for employee API endpoints."""

import pytest
from datetime import date
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

TENANT_DOMAIN = "testserver"


@pytest.fixture
def api_client(user):
    """Authenticated API client with tenant HTTP_HOST."""
    client = APIClient(HTTP_HOST=TENANT_DOMAIN)
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def unauth_client():
    """Unauthenticated API client with tenant HTTP_HOST."""
    return APIClient(HTTP_HOST=TENANT_DOMAIN)


class TestEmployeeListEndpoint:
    """Tests for GET /api/v1/employees/"""

    def test_list_returns_200(self, api_client, employee):
        response = api_client.get("/api/v1/employees/")
        assert response.status_code == 200

    def test_list_returns_employees(self, api_client, employee):
        response = api_client.get("/api/v1/employees/")
        assert response.data["count"] >= 1

    def test_list_pagination(self, api_client, employee):
        response = api_client.get("/api/v1/employees/")
        data = response.data
        assert "count" in data
        assert "results" in data

    def test_list_unauthenticated(self, unauth_client):
        response = unauth_client.get("/api/v1/employees/")
        assert response.status_code == 401

    def test_list_search_by_name(self, api_client, employee):
        response = api_client.get("/api/v1/employees/?search=John")
        assert response.status_code == 200

    def test_list_filter_by_status(self, api_client, employee):
        response = api_client.get("/api/v1/employees/?status=active")
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_list_filter_by_employment_type(self, api_client, employee):
        response = api_client.get("/api/v1/employees/?employment_type=full_time")
        assert response.status_code == 200

    def test_list_ordering(self, api_client, employee):
        response = api_client.get("/api/v1/employees/?ordering=-hire_date")
        assert response.status_code == 200

    def test_list_excludes_soft_deleted(self, api_client, employee):
        employee.is_deleted = True
        employee.save(update_fields=["is_deleted"])
        response = api_client.get("/api/v1/employees/")
        ids = [e["id"] for e in response.data["results"]]
        assert str(employee.id) not in ids


class TestEmployeeCreateEndpoint:
    """Tests for POST /api/v1/employees/"""

    def test_create_employee(self, api_client, tenant_context):
        data = {
            "first_name": "Test",
            "last_name": "Creating",
            "nic_number": "199823456789",
            "email": "create.test@example.com",
            "mobile": "+94712349999",
            "date_of_birth": "1998-01-15",
            "gender": "male",
            "employment_type": "full_time",
            "hire_date": "2024-06-01",
        }
        response = api_client.post("/api/v1/employees/", data, format="json")
        assert response.status_code == 201
        assert response.data["first_name"] == "Test"

    def test_create_missing_required_field(self, api_client, tenant_context):
        data = {"first_name": "Only"}
        response = api_client.post("/api/v1/employees/", data, format="json")
        assert response.status_code == 400


class TestEmployeeRetrieveEndpoint:
    """Tests for GET /api/v1/employees/{id}/"""

    def test_retrieve_employee(self, api_client, employee):
        response = api_client.get(f"/api/v1/employees/{employee.id}/")
        assert response.status_code == 200
        assert response.data["first_name"] == "John"

    def test_retrieve_nonexistent(self, api_client, tenant_context):
        import uuid
        response = api_client.get(f"/api/v1/employees/{uuid.uuid4()}/")
        assert response.status_code == 404


class TestEmployeeUpdateEndpoint:
    """Tests for PUT/PATCH /api/v1/employees/{id}/"""

    def test_partial_update(self, api_client, employee):
        response = api_client.patch(
            f"/api/v1/employees/{employee.id}/",
            {"first_name": "Updated"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["first_name"] == "Updated"


class TestEmployeeDeleteEndpoint:
    """Tests for DELETE /api/v1/employees/{id}/ (soft delete)"""

    def test_soft_delete_employee(self, api_client, employee):
        response = api_client.delete(f"/api/v1/employees/{employee.id}/")
        assert response.status_code == 204
        employee.refresh_from_db()
        assert employee.is_deleted is True
        assert employee.deleted_on is not None


class TestEmployeeLifecycleActions:
    """Tests for employee lifecycle action endpoints."""

    def test_activate(self, api_client, employee):
        employee.status = "inactive"
        employee.save(update_fields=["status"])
        response = api_client.post(f"/api/v1/employees/{employee.id}/activate/")
        assert response.status_code == 200
        assert response.data["status"] == "active"

    def test_deactivate(self, api_client, employee):
        response = api_client.post(
            f"/api/v1/employees/{employee.id}/deactivate/",
            {"reason": "leave of absence"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == "inactive"

    def test_terminate(self, api_client, employee):
        response = api_client.post(
            f"/api/v1/employees/{employee.id}/terminate/",
            {"termination_date": str(date.today()), "reason": "performance"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == "terminated"

    def test_resign(self, api_client, employee):
        response = api_client.post(
            f"/api/v1/employees/{employee.id}/resign/",
            {"resignation_date": str(date.today()), "reason": "personal"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["status"] == "resigned"


class TestEmployeeLinkUser:
    """Tests for POST /api/v1/employees/{id}/link-user/"""

    def test_link_user_success(self, api_client, employee, user):
        response = api_client.post(
            f"/api/v1/employees/{employee.id}/link-user/",
            {"email": user.email},
            format="json",
        )
        assert response.status_code == 200

    def test_link_user_missing_email(self, api_client, employee):
        response = api_client.post(
            f"/api/v1/employees/{employee.id}/link-user/",
            {},
            format="json",
        )
        assert response.status_code == 400

    def test_link_user_nonexistent_email(self, api_client, employee):
        response = api_client.post(
            f"/api/v1/employees/{employee.id}/link-user/",
            {"email": "nope@example.com"},
            format="json",
        )
        assert response.status_code == 404


class TestEmployeeNestedResources:
    """Tests for nested resource actions."""

    def test_list_addresses(self, api_client, employee, employee_address):
        response = api_client.get(f"/api/v1/employees/{employee.id}/addresses/")
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_create_address(self, api_client, employee):
        response = api_client.post(
            f"/api/v1/employees/{employee.id}/addresses/",
            {
                "address_type": "temporary",
                "line1": "456 Test Ave",
                "city": "Kandy",
                "province": "central",
                "postal_code": "20000",
            },
            format="json",
        )
        assert response.status_code == 201

    def test_list_emergency_contacts(self, api_client, employee, emergency_contact):
        response = api_client.get(f"/api/v1/employees/{employee.id}/emergency-contacts/")
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_list_bank_accounts(self, api_client, employee, employee_bank_account):
        response = api_client.get(f"/api/v1/employees/{employee.id}/bank-accounts/")
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_list_history(self, api_client, employee):
        response = api_client.get(f"/api/v1/employees/{employee.id}/history/")
        assert response.status_code == 200
