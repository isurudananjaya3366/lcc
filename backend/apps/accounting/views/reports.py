"""
Report API views.

Provides ViewSet with actions for generating and exporting
all financial reports (Trial Balance, P&L, Balance Sheet,
Cash Flow, General Ledger).
"""

import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounting.models.report_config import ReportConfig
from apps.accounting.reports.enums import DetailLevel, ReportType
from apps.accounting.reports.exporters.excel_exporter import ExcelReportExporter
from apps.accounting.reports.exporters.pdf_exporter import PDFReportExporter
from apps.accounting.reports.generators import (
    BalanceSheetGenerator,
    CashFlowGenerator,
    GeneralLedgerGenerator,
    ProfitLossGenerator,
    TrialBalanceGenerator,
)
from apps.accounting.serializers.report import (
    BalanceSheetQuerySerializer,
    CashFlowQuerySerializer,
    GeneralLedgerQuerySerializer,
    ProfitLossQuerySerializer,
    TrialBalanceQuerySerializer,
)

logger = logging.getLogger(__name__)


class ReportViewSet(viewsets.ViewSet):
    """ViewSet for financial report generation and export."""

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """GET /reports/ — List available report types."""
        reports = [
            {"type": rt.value, "name": rt.label}
            for rt in ReportType
        ]
        return Response({"reports": reports})

    # ── Report Actions ──────────────────────────────────────────────

    @action(detail=False, methods=["get"], url_path="trial-balance")
    def trial_balance(self, request):
        """GET /reports/trial-balance/"""
        serializer = TrialBalanceQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        config = self._build_config(ReportType.TRIAL_BALANCE, params, request.user)
        generator = TrialBalanceGenerator(config)
        return self._generate_response(generator, request)

    @action(detail=False, methods=["get"], url_path="profit-loss")
    def profit_loss(self, request):
        """GET /reports/profit-loss/"""
        serializer = ProfitLossQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        config = self._build_config(ReportType.PROFIT_LOSS, params, request.user)
        generator = ProfitLossGenerator(config)
        return self._generate_response(generator, request)

    @action(detail=False, methods=["get"], url_path="balance-sheet")
    def balance_sheet(self, request):
        """GET /reports/balance-sheet/"""
        serializer = BalanceSheetQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        config = self._build_config(ReportType.BALANCE_SHEET, params, request.user)
        generator = BalanceSheetGenerator(config)
        return self._generate_response(generator, request)

    @action(detail=False, methods=["get"], url_path="cash-flow")
    def cash_flow(self, request):
        """GET /reports/cash-flow/"""
        serializer = CashFlowQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        config = self._build_config(ReportType.CASH_FLOW, params, request.user)
        generator = CashFlowGenerator(config)
        return self._generate_response(generator, request)

    @action(detail=False, methods=["get"], url_path="general-ledger")
    def general_ledger(self, request):
        """GET /reports/general-ledger/"""
        serializer = GeneralLedgerQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        config = self._build_config(ReportType.GENERAL_LEDGER, params, request.user)
        generator = GeneralLedgerGenerator(
            config,
            account_code=params.get("account_code"),
            code_from=params.get("code_from"),
            code_to=params.get("code_to"),
        )
        return self._generate_response(generator, request)

    # ── Helpers ──────────────────────────────────────────────────────

    def _build_config(self, report_type, params, user):
        """Create an unsaved ReportConfig from query params."""
        config = ReportConfig(
            name=f"{report_type} Report",
            report_type=report_type,
            start_date=params.get("start_date"),
            end_date=params.get("end_date"),
            as_of_date=params.get("as_of_date"),
            detail_level=params.get("detail_level", DetailLevel.SUMMARY),
            include_comparison=params.get("include_comparison", False),
            include_zero_balances=params.get("include_zero_balances", False),
            comparison_start_date=params.get("comparison_start_date"),
            comparison_end_date=params.get("comparison_end_date"),
            comparison_as_of_date=params.get("comparison_as_of_date"),
            created_by=user,
        )
        return config

    def _generate_response(self, generator, request=None):
        """Execute generator and return JSON, PDF, or Excel response."""
        result = generator.generate()

        if not result.is_success:
            return Response(
                {
                    "status": "error",
                    "message": result.error_message,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check requested output format
        output_format = "json"
        if request:
            output_format = request.query_params.get("format", "json").lower()

        if output_format == "pdf":
            exporter = PDFReportExporter()
            return exporter.to_pdf_response(
                result.report_type, result.report_data,
            )

        if output_format == "excel":
            exporter = ExcelReportExporter(
                result.report_type, result.report_data,
            )
            filename = f"{result.report_type}_report.xlsx"
            return exporter.to_excel_response(filename=filename)

        return Response(
            {
                "status": "success",
                "report_type": result.report_type,
                "data": result.report_data,
                "metadata": result.report_metadata,
            }
        )
