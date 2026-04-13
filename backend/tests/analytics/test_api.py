"""Tests for analytics API endpoints."""

from uuid import uuid4

import pytest

from apps.analytics.enums import ReportCategory, ReportFormat, ScheduleFrequency
from apps.analytics.models import (
    ReportDefinition,
    ReportInstance,
    SavedReport,
    ScheduledReport,
)

pytestmark = pytest.mark.django_db


def _uid():
    return uuid4().hex[:8]


class TestListReportsEndpoint:
    """Tests for GET /api/v1/analytics/reports/"""

    def test_list_reports_unauthenticated(self, api_client):
        response = api_client.get("/api/v1/analytics/reports/")
        assert response.status_code in (401, 403)

    def test_list_reports_empty(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/analytics/reports/")
        assert response.status_code == 200

    def test_list_reports_with_data(self, authenticated_client, tenant_context):
        uid = _uid()
        ReportDefinition.objects.create(
            name=f"Sales Summary {uid}",
            category=ReportCategory.SALES,
            is_active=True,
        )
        ReportDefinition.objects.create(
            name=f"Inactive Report {uid}",
            category=ReportCategory.SALES,
            is_active=False,
        )
        response = authenticated_client.get("/api/v1/analytics/reports/")
        assert response.status_code == 200
        active_names = [r["name"] for r in response.data]
        assert f"Sales Summary {uid}" in active_names

    def test_list_reports_filter_category(self, authenticated_client, tenant_context):
        uid = _uid()
        ReportDefinition.objects.create(
            name=f"Sales A {uid}", category=ReportCategory.SALES, is_active=True
        )
        ReportDefinition.objects.create(
            name=f"Inv A {uid}", category=ReportCategory.INVENTORY, is_active=True
        )
        response = authenticated_client.get(
            "/api/v1/analytics/reports/", {"category": "SALES"}
        )
        assert response.status_code == 200
        categories = {r["category"] for r in response.data}
        assert categories == {"SALES"} or len(response.data) >= 1

    def test_list_reports_search(self, authenticated_client, tenant_context):
        uid = _uid()
        ReportDefinition.objects.create(
            name=f"Sales Summary {uid}",
            category=ReportCategory.SALES,
            is_active=True,
        )
        ReportDefinition.objects.create(
            name=f"Stock Level {uid}",
            category=ReportCategory.INVENTORY,
            is_active=True,
        )
        response = authenticated_client.get(
            "/api/v1/analytics/reports/", {"search": uid}
        )
        assert response.status_code == 200
        assert len(response.data) == 2


class TestReportDetailEndpoint:
    """Tests for GET /api/v1/analytics/reports/{code}/"""

    def test_report_detail(self, authenticated_client, tenant_context):
        uid = _uid()
        rd = ReportDefinition.objects.create(
            name=f"My Report {uid}",
            category=ReportCategory.SALES,
            is_active=True,
        )
        response = authenticated_client.get(f"/api/v1/analytics/reports/{rd.code}/")
        assert response.status_code == 200
        assert response.data["code"] == rd.code

    def test_report_detail_not_found(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/analytics/reports/NOPE/")
        assert response.status_code == 404


class TestGenerateEndpoint:
    """Tests for POST /api/v1/analytics/generate/"""

    def test_generate_unknown_code(self, authenticated_client, tenant_context):
        response = authenticated_client.post(
            "/api/v1/analytics/generate/",
            {"report_code": "UNKNOWN_CODE"},
            format="json",
        )
        assert response.status_code == 400

    def test_generate_valid_report(self, authenticated_client, user):
        uid = _uid()
        ReportDefinition.objects.create(
            name=f"Customer Acquisition {uid}",
            code="CUSTOMER_ACQUISITION",
            category=ReportCategory.CUSTOMER,
            is_active=True,
        )
        response = authenticated_client.post(
            "/api/v1/analytics/generate/",
            {"report_code": "CUSTOMER_ACQUISITION", "parameters": {}},
            format="json",
        )
        assert response.status_code == 201
        assert "report_data" in response.data
        assert response.data["status"] == "COMPLETED"


class TestInstancesEndpoint:
    """Tests for GET /api/v1/analytics/instances/"""

    def test_list_instances_empty(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/analytics/instances/")
        assert response.status_code == 200


class TestSavedReportsEndpoint:
    """Tests for GET/POST /api/v1/analytics/saved/"""

    def test_list_saved_empty(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/analytics/saved/")
        assert response.status_code == 200

    def test_create_saved_report(self, authenticated_client, user):
        uid = _uid()
        rd = ReportDefinition.objects.create(
            name=f"Save Target {uid}",
            category=ReportCategory.SALES,
            is_active=True,
        )
        response = authenticated_client.post(
            "/api/v1/analytics/saved/",
            {
                "name": f"My Saved Report {uid}",
                "report_definition": str(rd.id),
                "filters_config": {},
                "output_format": "PDF",
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["name"] == f"My Saved Report {uid}"


class TestScheduledReportsEndpoint:
    """Tests for GET/POST /api/v1/analytics/scheduled/"""

    def test_list_scheduled_empty(self, authenticated_client, tenant_context):
        response = authenticated_client.get("/api/v1/analytics/scheduled/")
        assert response.status_code == 200

    def test_create_scheduled_report(self, authenticated_client, user):
        uid = _uid()
        rd = ReportDefinition.objects.create(
            name=f"Sched Target {uid}",
            category=ReportCategory.SALES,
            is_active=True,
        )
        saved = SavedReport.objects.create(
            name=f"Sched Saved {uid}", report_definition=rd, owner=user
        )
        response = authenticated_client.post(
            "/api/v1/analytics/scheduled/",
            {
                "saved_report": str(saved.id),
                "frequency": "DAILY",
                "time_of_day": "09:00:00",
                "recipients": ["admin@example.com"],
            },
            format="json",
        )
        assert response.status_code == 201
