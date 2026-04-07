"""Org-Chart API view."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organization.services.orgchart_service import OrgChartService


class OrgChartView(APIView):
    """GET /api/v1/organization/org-chart/?type=department|employee"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        chart_type = request.query_params.get("type", "department")
        if chart_type not in ("department", "employee"):
            chart_type = "department"

        data = OrgChartService.generate_orgchart_json(chart_type=chart_type)
        return Response(data)
