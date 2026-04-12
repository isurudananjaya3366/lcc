"""
PDF report exporter.

Renders report HTML templates to PDF using Django's template engine.
Falls back to HTML response if WeasyPrint is not available.
"""

import logging
from io import BytesIO
from typing import Any, Dict

from django.http import HttpResponse
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class PDFReportExporter:
    """Export reports as PDF via HTML template rendering."""

    TEMPLATE_MAP = {
        "TRIAL_BALANCE": "reports/trial_balance.html",
        "PROFIT_LOSS": "reports/profit_loss.html",
        "BALANCE_SHEET": "reports/balance_sheet.html",
        "CASH_FLOW": "reports/cash_flow.html",
        "GENERAL_LEDGER": "reports/general_ledger.html",
    }

    def __init__(self, report_type: str, data: Dict[str, Any]):
        self.report_type = report_type
        self.data = data

    def render_html(self) -> str:
        """Render report data to an HTML string."""
        template = self.TEMPLATE_MAP.get(self.report_type)
        if not template:
            raise ValueError(f"No template for report type: {self.report_type}")
        return render_to_string(template, self.data)

    def to_pdf_response(self, filename: str = "report.pdf") -> HttpResponse:
        """Generate PDF response. Falls back to HTML if WeasyPrint unavailable."""
        html = self.render_html()

        try:
            from weasyprint import HTML as WeasyHTML

            pdf_bytes = WeasyHTML(string=html).write_pdf()
            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except ImportError:
            logger.warning("WeasyPrint not installed; returning HTML response.")
            response = HttpResponse(html, content_type="text/html")
            response["Content-Disposition"] = f'inline; filename="{filename}.html"'
            return response

    def to_html_response(self, filename: str = "report.html") -> HttpResponse:
        """Generate an HTML response."""
        html = self.render_html()
        response = HttpResponse(html, content_type="text/html")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
