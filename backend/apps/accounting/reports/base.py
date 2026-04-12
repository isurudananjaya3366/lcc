"""
Base report generator.

Provides the abstract base class for all financial report generators,
implementing the Template Method pattern for consistent report
generation flow.
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounting.reports.enums import DetailLevel, ReportType

logger = logging.getLogger(__name__)


class BaseReportGenerator(ABC):
    """
    Abstract base class for financial report generators.

    Subclasses must implement:
        - get_data() -> Dict[str, Any]
        - format_output(data) -> Dict[str, Any]

    Usage:
        generator = TrialBalanceGenerator(config)
        result = generator.generate()
    """

    report_type: ReportType = None  # Override in subclass

    def __init__(self, config):
        """
        Initialize the report generator.

        Args:
            config: ReportConfig instance with report parameters.
        """
        self._config = config
        self._errors = []

    # ── Properties ──────────────────────────────────────────────────

    @property
    def config(self):
        return self._config

    # ── Public Methods ──────────────────────────────────────────────

    def generate(self, force_refresh: bool = False) -> "ReportResult":
        """
        Generate the financial report.

        Orchestrates the report generation flow: validation → data
        retrieval → comparison (if enabled) → formatting → result.

        Args:
            force_refresh: Skip cache and regenerate.

        Returns:
            ReportResult instance with report data.
        """
        from apps.accounting.models.report_result import ReportResult

        start_time = time.monotonic()

        # 1. Validate configuration
        if not self.validate_config():
            result = ReportResult(
                config=self._config,
                report_type=self._config.report_type,
                is_success=False,
                error_message="; ".join(self._errors),
            )
            return result

        # 2. Check cache
        if not force_refresh:
            cached = self._get_cached_result()
            if cached:
                return cached

        try:
            # 3. Retrieve current period data
            data = self.get_data()

            # 4. Comparison data (if enabled)
            if self._config.include_comparison:
                comparison_data = self._get_comparison_data()
                if comparison_data:
                    data["comparison"] = comparison_data
                    data["variances"] = self._calculate_variances(
                        data, comparison_data
                    )

            # 5. Format output
            formatted = self.format_output(data)

            # 6. Ensure JSON-safe (convert Decimals, dates, etc.)
            formatted = self._make_json_safe(formatted)

            # 6. Create result
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            result = ReportResult(
                config=self._config,
                report_type=self._config.report_type,
                report_data=formatted,
                report_metadata={
                    "generated_at": timezone.now().isoformat(),
                    "report_type": self._config.report_type,
                    "detail_level": self._config.detail_level,
                    "include_comparison": self._config.include_comparison,
                },
                generation_time_ms=elapsed_ms,
                is_success=True,
                is_cached=False,
            )
            result.save()
            return result

        except Exception as e:
            logger.exception("Report generation failed: %s", e)
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            result = ReportResult(
                config=self._config,
                report_type=self._config.report_type,
                is_success=False,
                error_message=str(e),
                generation_time_ms=elapsed_ms,
            )
            return result

    def validate_config(self) -> bool:
        """Validate the report configuration."""
        self._errors = []

        if not self._config:
            self._errors.append("Report configuration is required.")
            return False

        if (
            self.report_type
            and self._config.report_type != self.report_type
        ):
            self._errors.append(
                f"Invalid report type: expected {self.report_type}, "
                f"got {self._config.report_type}."
            )
            return False

        try:
            self._config.clean()
        except ValidationError as e:
            self._errors.extend(
                e.message_dict.values()
                if hasattr(e, "message_dict")
                else e.messages
            )
            return False

        return True

    # ── Abstract Methods ────────────────────────────────────────────

    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """
        Retrieve raw financial data for the report.

        Returns:
            Dictionary with report data.
        """

    @abstractmethod
    def format_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw data into the final report structure.

        Args:
            data: Raw data from get_data().

        Returns:
            Formatted report dictionary.
        """

    # ── Protected Helper Methods ────────────────────────────────────

    def _get_date_range(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Return (start_date, end_date) from config."""
        return self._config.start_date, self._config.end_date

    def _get_comparison_range(self) -> Tuple[Optional[Any], Optional[Any]]:
        """Return comparison (start_date, end_date) from config."""
        return (
            self._config.comparison_start_date,
            self._config.comparison_end_date,
        )

    def _should_include_account(self, account) -> bool:
        """Check if an account should be included in the report."""
        if not self._config.include_zero_balances:
            balance = getattr(account, "current_balance", Decimal("0"))
            if balance == Decimal("0"):
                return False
        return True

    # Materiality thresholds for variance analysis
    MATERIALITY_PERCENTAGE = Decimal("10.0")
    MATERIALITY_ABSOLUTE = Decimal("100000.00")

    def _calculate_variance(
        self, current: Decimal, prior: Decimal,
        account_type: str = "",
    ) -> Dict[str, Any]:
        """Calculate amount and percentage variance with classification."""
        amount = current - prior
        if prior and prior != Decimal("0"):
            percentage = (amount / abs(prior)) * Decimal("100")
        else:
            percentage = Decimal("0")

        # Classify variance direction
        if amount > Decimal("0"):
            direction = "increase"
        elif amount < Decimal("0"):
            direction = "decrease"
        else:
            direction = "no_change"

        # Classify as favorable/unfavorable
        classification = self._classify_variance(
            direction, account_type,
        )

        # Check materiality
        is_material = (
            abs(percentage) >= self.MATERIALITY_PERCENTAGE
            or abs(amount) >= self.MATERIALITY_ABSOLUTE
        )

        return {
            "amount": amount,
            "percentage": round(percentage, 2),
            "direction": direction,
            "classification": classification,
            "is_material": is_material,
        }

    @staticmethod
    def _classify_variance(direction: str, account_type: str) -> str:
        """Classify variance as favorable, unfavorable, or neutral."""
        if direction == "no_change":
            return "neutral"

        from apps.accounting.constants import (
            ACCOUNT_TYPE_ASSET,
            ACCOUNT_TYPE_EQUITY,
            ACCOUNT_TYPE_EXPENSE,
            ACCOUNT_TYPE_LIABILITY,
            ACCOUNT_TYPE_REVENUE,
        )

        # Favorable: asset increase, liability decrease, equity increase,
        #            revenue increase, expense decrease
        favorable_increase = {
            ACCOUNT_TYPE_ASSET, ACCOUNT_TYPE_EQUITY, ACCOUNT_TYPE_REVENUE,
        }
        favorable_decrease = {
            ACCOUNT_TYPE_LIABILITY, ACCOUNT_TYPE_EXPENSE,
        }

        if direction == "increase":
            if account_type in favorable_increase:
                return "favorable"
            if account_type in favorable_decrease:
                return "unfavorable"
        elif direction == "decrease":
            if account_type in favorable_decrease:
                return "favorable"
            if account_type in favorable_increase:
                return "unfavorable"

        return "neutral"

    def _calculate_variances(
        self, current_data: Dict, comparison_data: Dict
    ) -> Dict[str, Any]:
        """Calculate variances between current and comparison data."""
        return {}  # Subclasses override for specific variance logic

    def _get_comparison_data(self) -> Optional[Dict[str, Any]]:
        """Retrieve comparison period data. Override in subclasses."""
        return None

    def _get_cached_result(self):
        """Check for a cached report result."""
        from apps.accounting.models.report_result import ReportResult

        try:
            return ReportResult.objects.filter(
                config=self._config,
                report_type=self._config.report_type,
                is_success=True,
                is_cached=True,
            ).first()
        except Exception:
            return None

    @staticmethod
    def _make_json_safe(obj):
        """Recursively convert Decimals and dates to JSON-safe types."""

        class _Encoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, Decimal):
                    return float(o)
                if hasattr(o, "isoformat"):
                    return o.isoformat()
                return super().default(o)

        return json.loads(json.dumps(obj, cls=_Encoder))
