"""Tests for organization API endpoints — ViewSets and OrgChartView."""

import pytest
from datetime import date
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db

TENANT_DOMAIN = "testserver"


@pytest.fixture
def auth_client(user):
    """Return an authenticated API client."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# =====================================================================
# Department API Tests
# =====================================================================


class TestDepartmentAPI:
    """Tests for Department ViewSet endpoints."""

    def test_list_departments(self, auth_client, department):
        response = auth_client.get(
            "/api/v1/organization/departments/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_department(self, auth_client, department):
        response = auth_client.get(
            f"/api/v1/organization/departments/{department.pk}/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Engineering"
        assert response.data["code"] == "DEPT-ENG"

    def test_create_department(self, auth_client, tenant_context):
        response = auth_client.post(
            "/api/v1/organization/departments/",
            {"name": "Finance", "code": "DEPT-FIN"},
            format="json",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_department(self, auth_client, department):
        response = auth_client.patch(
            f"/api/v1/organization/departments/{department.pk}/",
            {"description": "Updated description"},
            format="json",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_delete_department(self, auth_client, department):
        response = auth_client.delete(
            f"/api/v1/organization/departments/{department.pk}/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_tree_action(self, auth_client, department, child_department):
        response = auth_client.get(
            "/api/v1/organization/departments/tree/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_children_action(self, auth_client, department, child_department):
        response = auth_client.get(
            f"/api/v1/organization/departments/{department.pk}/children/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_path_action(self, auth_client, child_department):
        response = auth_client.get(
            f"/api/v1/organization/departments/{child_department.pk}/path/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "path" in response.data
        assert "path_string" in response.data
        names = [p["name"] for p in response.data["path"]]
        assert "Engineering" in names

    def test_stats_action(self, auth_client, department):
        response = auth_client.get(
            f"/api/v1/organization/departments/{department.pk}/stats/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "total_employees" in response.data

    def test_move_action(self, auth_client, department, second_department):
        response = auth_client.post(
            f"/api/v1/organization/departments/{department.pk}/move/",
            {"new_parent_id": str(second_department.pk)},
            format="json",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_merge_action(self, auth_client, department, second_department):
        response = auth_client.post(
            f"/api/v1/organization/departments/{department.pk}/merge/",
            {"target_id": str(second_department.pk)},
            format="json",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_employees_action(self, auth_client, department, employee):
        employee.department = department
        employee.save()
        response = auth_client.get(
            f"/api/v1/organization/departments/{department.pk}/employees/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_unauthenticated_access(self, department):
        client = APIClient()
        response = client.get(
            "/api/v1/organization/departments/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_filter_by_status(self, auth_client, department, second_department):
        second_department.status = "inactive"
        second_department.save()
        response = auth_client.get(
            "/api/v1/organization/departments/?status=active",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_search_departments(self, auth_client, department):
        response = auth_client.get(
            "/api/v1/organization/departments/?search=Eng",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK


# =====================================================================
# Designation API Tests
# =====================================================================


class TestDesignationAPI:
    """Tests for Designation ViewSet endpoints."""

    def test_list_designations(self, auth_client, designation):
        response = auth_client.get(
            "/api/v1/organization/designations/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_designation(self, auth_client, designation):
        response = auth_client.get(
            f"/api/v1/organization/designations/{designation.pk}/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Software Engineer"

    def test_create_designation(self, auth_client, tenant_context):
        response = auth_client.post(
            "/api/v1/organization/designations/",
            {"title": "DevOps Engineer", "code": "DOE", "level": "mid"},
            format="json",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_update_designation(self, auth_client, designation):
        response = auth_client.patch(
            f"/api/v1/organization/designations/{designation.pk}/",
            {"description": "Updated"},
            format="json",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_delete_designation(self, auth_client, designation):
        response = auth_client.delete(
            f"/api/v1/organization/designations/{designation.pk}/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_employees_action(self, auth_client, designation, employee):
        employee.designation = designation
        employee.save()
        response = auth_client.get(
            f"/api/v1/organization/designations/{designation.pk}/employees/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_salary_range_action(self, auth_client, designation):
        response = auth_client.get(
            f"/api/v1/organization/designations/{designation.pk}/salary-range/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["currency"] == "LKR"

    def test_level_hierarchy_action(self, auth_client, designation, manager_designation):
        response = auth_client.get(
            "/api/v1/organization/designations/level-hierarchy/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        levels = [item["level"] for item in response.data]
        assert "mid" in levels
        assert "manager" in levels

    def test_filter_by_level(self, auth_client, designation, manager_designation):
        response = auth_client.get(
            "/api/v1/organization/designations/?level=manager",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_filter_is_manager(self, auth_client, designation, manager_designation):
        response = auth_client.get(
            "/api/v1/organization/designations/?is_manager=true",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK

    def test_search_designations(self, auth_client, designation):
        response = auth_client.get(
            "/api/v1/organization/designations/?search=Software",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK


# =====================================================================
# OrgChart API Tests
# =====================================================================


class TestOrgChartAPI:
    """Tests for OrgChart view."""

    def test_orgchart_department(self, auth_client, department):
        response = auth_client.get(
            "/api/v1/organization/org-chart/?type=department",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "department"

    def test_orgchart_employee(self, auth_client, employee):
        response = auth_client.get(
            "/api/v1/organization/org-chart/?type=employee",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "employee"

    def test_orgchart_default_type(self, auth_client, department):
        response = auth_client.get(
            "/api/v1/organization/org-chart/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "department"

    def test_orgchart_invalid_type_defaults(self, auth_client, department):
        response = auth_client.get(
            "/api/v1/organization/org-chart/?type=invalid",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["type"] == "department"

    def test_orgchart_unauthenticated(self, department):
        client = APIClient()
        response = client.get(
            "/api/v1/organization/org-chart/",
            HTTP_HOST=TENANT_DOMAIN,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
