"""Standalone Report Views for Payroll statutory returns.

Provides dedicated endpoints for generating EPF, ETF, PAYE returns,
payroll summaries, and bank file downloads.
"""

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payroll.models import PayrollPeriod, PayrollRun
from apps.payroll.services.statutory_reports import StatutoryReportService

logger = logging.getLogger(__name__)


class PayrollReportView(APIView):
    """Base class for payroll report views."""

    permission_classes = [IsAuthenticated]

    def _get_period(self, request):
        """Resolve period from query params."""
        period_id = request.query_params.get("period_id")
        if not period_id:
            return None, Response(
                {"detail": "period_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            period = PayrollPeriod.objects.get(pk=period_id)
            return period, None
        except PayrollPeriod.DoesNotExist:
            return None, Response(
                {"detail": "Payroll period not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def _get_run(self, request):
        """Resolve run from query params."""
        run_id = request.query_params.get("run_id")
        if not run_id:
            return None, Response(
                {"detail": "run_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            run = PayrollRun.objects.get(pk=run_id)
            return run, None
        except PayrollRun.DoesNotExist:
            return None, Response(
                {"detail": "Payroll run not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class EPFReportView(PayrollReportView):
    """Generate EPF return report.

    GET /reports/epf/?period_id={id}&format=excel
    """

    def get(self, request):
        run, error = self._get_run(request)
        if error:
            return error
        service = StatutoryReportService()
        try:
            result = service.generate_epf_return(run)
            return Response(result)
        except (ValueError, Exception) as e:
            logger.exception("EPF report generation failed")
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class ETFReportView(PayrollReportView):
    """Generate ETF return report.

    GET /reports/etf/?period_id={id}&format=excel
    """

    def get(self, request):
        run, error = self._get_run(request)
        if error:
            return error
        service = StatutoryReportService()
        try:
            result = service.generate_etf_return(run)
            return Response(result)
        except (ValueError, Exception) as e:
            logger.exception("ETF report generation failed")
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class PAYEReportView(PayrollReportView):
    """Generate PAYE return report.

    GET /reports/paye/?period_id={id}&format=pdf
    """

    def get(self, request):
        run, error = self._get_run(request)
        if error:
            return error
        service = StatutoryReportService()
        try:
            result = service.generate_paye_return(run)
            return Response(result)
        except (ValueError, Exception) as e:
            logger.exception("PAYE report generation failed")
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class PayrollSummaryView(PayrollReportView):
    """Generate payroll summary report.

    GET /reports/summary/?run_id={id}
    """

    def get(self, request):
        run, error = self._get_run(request)
        if error:
            return error
        service = StatutoryReportService()
        try:
            result = service.generate_payroll_summary(run)
            return Response(result)
        except (ValueError, Exception) as e:
            logger.exception("Payroll summary generation failed")
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class BankFileView(PayrollReportView):
    """Generate bank payment file.

    GET /reports/bank-file/?run_id={id}&bank_code=CSV
    """

    def get(self, request):
        from apps.payroll.services.finalization_service import PayrollFinalizationService

        run, error = self._get_run(request)
        if error:
            return error
        bank_code = request.query_params.get("bank_code", "CSV")
        service = PayrollFinalizationService()
        try:
            result = service.generate_bank_file(
                run.pk, bank_code=bank_code, generated_by=request.user
            )
            return Response(result)
        except (ValueError, Exception) as e:
            logger.exception("Bank file generation failed")
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class ReportListView(PayrollReportView):
    """List available reports for a period.

    GET /reports/list/?period_id={id}
    """

    def get(self, request):
        period, error = self._get_period(request)
        if error:
            return error
        reports = [
            {
                "name": "EPF Return",
                "url": f"/api/v1/payroll/reports/epf/?period_id={period.pk}",
                "formats": ["excel", "csv", "pdf"],
            },
            {
                "name": "ETF Return",
                "url": f"/api/v1/payroll/reports/etf/?period_id={period.pk}",
                "formats": ["excel", "csv", "pdf"],
            },
            {
                "name": "PAYE Return",
                "url": f"/api/v1/payroll/reports/paye/?period_id={period.pk}",
                "formats": ["excel", "csv", "pdf"],
            },
            {
                "name": "Payroll Summary",
                "description": "Comprehensive payroll run summary",
                "formats": ["excel", "csv", "json"],
            },
            {
                "name": "Bank File",
                "description": "Bank transfer payment file",
                "formats": ["SLIPS", "BOC", "ComBank", "CSV"],
            },
        ]
        return Response({"period": str(period), "reports": reports})
