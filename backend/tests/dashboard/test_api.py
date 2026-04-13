"""Tests for dashboard API endpoints."""

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestDashboardAPI:
    """Tests for DashboardViewSet endpoints."""

    def test_unauthenticated_access_denied(self, api_client, tenant_context):
        response = api_client.get("/api/v1/dashboard/sales/")
        assert response.status_code in (
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        )

    def test_sales_endpoint(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/dashboard/sales/")
        assert response.status_code == status.HTTP_200_OK, response.data
        assert isinstance(response.data, dict)

    def test_inventory_endpoint(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/dashboard/inventory/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)

    def test_financial_endpoint(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/dashboard/financial/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)

    def test_hr_endpoint(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/dashboard/hr/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)

    def test_all_kpis_endpoint(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/dashboard/all/")
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert "sales" in data
        assert "inventory" in data
        assert "financial" in data
        assert "hr" in data
        assert "alerts" in data

    def test_alerts_endpoint(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/dashboard/alerts/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_period_query_param(self, authenticated_client, tenant_context):
        response = authenticated_client.get(
            "/api/v1/dashboard/sales/", {"period": "week"}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_refresh_query_param(self, authenticated_client, tenant_context):
        response = authenticated_client.get(
            "/api/v1/dashboard/sales/", {"refresh": "true"}
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDashboardLayoutAPI:
    """Tests for layout management endpoints."""

    def test_get_layout_default(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/dashboard/layout/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_default"] is True

    def test_save_layout(self, authenticated_client, tenant_context):
        data = {
            "name": "Custom Layout",
            "widgets": {
                "widgets": [
                    {
                        "kpi_code": "SALES_TODAY",
                        "position": {"x": 0, "y": 0, "w": 3, "h": 1},
                    }
                ]
            },
        }
        response = authenticated_client.put(
            "/api/v1/dashboard/layout/",
            data=data,
            format="json",
        )
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
        )
        assert response.data["name"] == "Custom Layout"

    def test_update_existing_layout(self, authenticated_client, user, tenant_context):
        from apps.dashboard.models import DashboardLayout

        DashboardLayout.objects.create(
            user=user,
            name="Old Layout",
            widgets={"widgets": []},
            is_default=True,
        )

        data = {
            "name": "Updated Layout",
            "widgets": {"widgets": [{"kpi_code": "REVENUE"}]},
        }
        response = authenticated_client.put(
            "/api/v1/dashboard/layout/",
            data=data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Layout"

    def test_reset_layout(self, authenticated_client, user, tenant_context):
        from apps.dashboard.models import DashboardLayout

        DashboardLayout.objects.create(
            user=user,
            name="Custom",
            widgets={"widgets": [{"kpi_code": "X"}]},
            is_default=True,
        )
        response = authenticated_client.get(
            "/api/v1/dashboard/layout/", {"reset": "true"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_default"] is True
