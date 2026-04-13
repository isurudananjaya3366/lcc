"""
Base report generator.

Abstract base class for all analytics report generators.
"""

import time
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from django.db.models import QuerySet
from django.utils import timezone


class BaseReportGenerator(ABC):
    """
    Abstract base class for analytics report generators.

    Subclasses must implement ``get_base_queryset`` and ``generate``.
    """

    REPORT_TYPE: str = ""

    def __init__(
        self,
        filter_parameters: dict[str, Any] | None = None,
        user: Any | None = None,
    ):
        self.filter_parameters = filter_parameters or {}
        self.user = user
        self._start_time: float | None = None

    # ── Abstract Methods ──────────────────────────────────────────

    @abstractmethod
    def get_base_queryset(self) -> QuerySet:
        """Return the base queryset for this report."""

    @abstractmethod
    def generate(self) -> dict[str, Any]:
        """Generate the report data and return standardised structure."""

    # ── Common Utility Methods ────────────────────────────────────

    def get_filter_value(self, key: str, default: Any = None) -> Any:
        """Safely extract a value from filter_parameters."""
        return self.filter_parameters.get(key, default)

    def apply_date_filter(
        self,
        queryset: QuerySet,
        date_field: str = "created_on",
    ) -> QuerySet:
        """
        Apply date range filter from ``filter_parameters['date_range']``.

        Expects ``{'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'}``.
        """
        date_range = self.get_filter_value("date_range")
        if not date_range:
            return queryset
        start = date_range.get("start_date")
        end = date_range.get("end_date")
        if start:
            queryset = queryset.filter(**{f"{date_field}__gte": start})
        if end:
            queryset = queryset.filter(**{f"{date_field}__lte": end})
        return queryset

    def get_report_title(self) -> str:
        """Generate a human-readable report title."""
        date_range = self.get_filter_value("date_range", {})
        start = date_range.get("start_date", "")
        end = date_range.get("end_date", "")
        period_str = f" ({start} to {end})" if start and end else ""
        return f"{self.REPORT_TYPE.replace('_', ' ').title()}{period_str}"

    def calculate_totals(
        self, data: list[dict[str, Any]], numeric_keys: list[str] | None = None
    ) -> dict[str, Any]:
        """Sum numeric columns from data rows."""
        totals: dict[str, Any] = {"row_count": len(data)}
        if not data:
            return totals
        if numeric_keys is None:
            numeric_keys = [
                k
                for k, v in data[0].items()
                if isinstance(v, (int, float, Decimal))
                and k not in ("rank", "percentage")
            ]
        for key in numeric_keys:
            totals[key] = sum(row.get(key, 0) or 0 for row in data)
        return totals

    def build_response(
        self,
        data: list[dict[str, Any]],
        totals: dict[str, Any] | None = None,
        chart_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build the standardised report response structure."""
        if totals is None:
            totals = self.calculate_totals(data)
        generation_time = (
            time.time() - self._start_time if self._start_time else 0
        )
        result: dict[str, Any] = {
            "report_type": self.REPORT_TYPE,
            "report_title": self.get_report_title(),
            "generated_at": timezone.now().isoformat(),
            "period": self._get_period_string(),
            "filters": self.filter_parameters,
            "data": data,
            "totals": totals,
            "row_count": len(data),
            "metadata": {
                "generation_time_seconds": round(generation_time, 2),
            },
        }
        if chart_data:
            result["metadata"]["chart_data"] = chart_data
        return result

    def start_timer(self) -> None:
        """Mark the start of report generation."""
        self._start_time = time.time()

    # ── Export Methods ────────────────────────────────────────────

    def to_csv(
        self, data: dict[str, Any] | None = None, delimiter: str = ","
    ) -> str:
        """Export report data to CSV string."""
        import csv
        import io

        if data is None:
            data = self.generate()
        rows = data.get("data", [])
        if not rows:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=rows[0].keys(), delimiter=delimiter
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {k: str(v) if isinstance(v, Decimal) else v for k, v in row.items()}
            )
        return output.getvalue()

    def get_export_filename(self, extension: str) -> str:
        """Generate a report filename."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        code = self.REPORT_TYPE.lower()
        return f"{code}_{ts}{extension}"

    # ── Private Helpers ───────────────────────────────────────────

    def _get_period_string(self) -> str:
        date_range = self.get_filter_value("date_range", {})
        start = date_range.get("start_date", "")
        end = date_range.get("end_date", "")
        if start and end:
            return f"{start} to {end}"
        return "All time"
