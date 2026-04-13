"""
Analytics ViewSet — report listing, generation, download, saved & scheduled.
"""

import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.analytics.api.serializers import (
    ReportDefinitionListSerializer,
    ReportDefinitionSerializer,
    ReportGenerationSerializer,
    ReportInstanceSerializer,
    SavedReportSerializer,
    ScheduledReportCreateSerializer,
    ScheduledReportSerializer,
    ScheduleHistorySerializer,
)
from apps.analytics.models import (
    ReportDefinition,
    ReportInstance,
    SavedReport,
    ScheduledReport,
    ScheduleHistory,
)
from apps.analytics.services.scheduler import ReportSchedulerService

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ViewSet):
    """Unified analytics API for reports, instances, and schedules."""

    permission_classes = [IsAuthenticated]

    # ── Report Definitions ────────────────────────────────────────

    def list(self, request):
        """List active report definitions."""
        return self.list_reports(request)

    @action(detail=False, methods=["get"], url_path="reports")
    def list_reports(self, request):
        """GET /api/v1/analytics/reports/ — List available report types."""
        qs = ReportDefinition.objects.filter(is_active=True)
        category = request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)
        serializer = ReportDefinitionListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="reports/(?P<code>[^/.]+)")
    def report_detail(self, request, code=None):
        """GET /api/v1/analytics/reports/{code}/ — Report definition detail."""
        try:
            report_def = ReportDefinition.objects.get(code=code, is_active=True)
        except ReportDefinition.DoesNotExist:
            return Response(
                {"detail": "Report definition not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ReportDefinitionSerializer(report_def)
        return Response(serializer.data)

    # ── Generate ──────────────────────────────────────────────────

    @action(detail=False, methods=["post"], url_path="generate")
    def generate_report(self, request):
        """POST /api/v1/analytics/generate/ — Generate a report."""
        ser = ReportGenerationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        report_code = ser.validated_data["report_code"]
        parameters = ser.validated_data.get("parameters", {})

        try:
            generator_cls = ReportSchedulerService.get_generator_class(report_code)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report_def = ReportDefinition.objects.get(code=report_code)
        instance = ReportInstance.objects.create(
            report_definition=report_def,
            user=request.user,
            filter_parameters=parameters,
            output_format=ser.validated_data.get("format", "JSON"),
        )

        try:
            generator = generator_cls(
                filter_parameters=parameters, user=request.user
            )
            result = generator.generate()
            instance.mark_completed(file_path="", file_size=0)
        except Exception as exc:
            instance.mark_failed(str(exc))
            logger.exception("Report generation failed: %s", exc)
            return Response(
                {"detail": "Report generation failed.", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_data = ReportInstanceSerializer(instance).data
        response_data["report_data"] = result
        return Response(response_data, status=status.HTTP_201_CREATED)

    # ── Instances ─────────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="instances")
    def list_instances(self, request):
        """GET /api/v1/analytics/instances/ — User's generated reports."""
        qs = ReportInstance.objects.filter(user=request.user).select_related(
            "report_definition"
        )
        serializer = ReportInstanceSerializer(qs[:50], many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="download/(?P<pk>[^/.]+)")
    def download_report(self, request, pk=None):
        """GET /api/v1/analytics/download/{id}/ — Download report file."""
        try:
            instance = ReportInstance.objects.get(pk=pk, user=request.user)
        except ReportInstance.DoesNotExist:
            return Response(
                {"detail": "Report instance not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not instance.output_file:
            return Response(
                {"detail": "No file available for this report."},
                status=status.HTTP_404_NOT_FOUND,
            )
        from django.http import FileResponse

        return FileResponse(
            instance.output_file.open("rb"),
            as_attachment=True,
            filename=instance.output_file.name.split("/")[-1],
        )

    # ── Saved Reports ─────────────────────────────────────────────

    @action(detail=False, methods=["get", "post"], url_path="saved")
    def saved_reports(self, request):
        """GET/POST /api/v1/analytics/saved/ — Manage saved reports."""
        if request.method == "POST":
            ser = SavedReportSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            ser.save(owner=request.user)
            return Response(ser.data, status=status.HTTP_201_CREATED)

        qs = SavedReport.objects.filter(
            owner=request.user
        ).select_related("report_definition", "owner") | SavedReport.objects.filter(
            is_public=True
        ).select_related(
            "report_definition", "owner"
        )
        serializer = SavedReportSerializer(qs.distinct(), many=True)
        return Response(serializer.data)

    # ── Scheduled Reports ─────────────────────────────────────────

    @action(detail=False, methods=["get", "post"], url_path="scheduled")
    def scheduled_reports(self, request):
        """GET/POST /api/v1/analytics/scheduled/ — Manage schedules."""
        if request.method == "POST":
            ser = ScheduledReportCreateSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            ser.save(created_by=request.user)
            return Response(
                ScheduledReportSerializer(ser.instance).data,
                status=status.HTTP_201_CREATED,
            )

        qs = ScheduledReport.objects.filter(
            created_by=request.user
        ).select_related("saved_report")
        serializer = ScheduledReportSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="scheduled/(?P<pk>[^/.]+)/history")
    def schedule_history(self, request, pk=None):
        """GET /api/v1/analytics/scheduled/{id}/history/ — Schedule run history."""
        qs = ScheduleHistory.objects.filter(
            scheduled_report_id=pk,
            scheduled_report__created_by=request.user,
        )
        serializer = ScheduleHistorySerializer(qs[:50], many=True)
        return Response(serializer.data)
