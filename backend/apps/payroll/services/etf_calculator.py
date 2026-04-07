"""ETF (Employees' Trust Fund) calculator service."""

import logging
from decimal import ROUND_HALF_UP, Decimal

from apps.payroll.models.etf_settings import ETFSettings
from apps.payroll.services.epf_calculator import EPFCalculator

logger = logging.getLogger(__name__)


class ETFCalculator:
    """Calculates ETF employer contribution (same base as EPF)."""

    @staticmethod
    def calculate(employee_salary, settings=None):
        """Calculate ETF employer contribution.

        Returns dict with etf_base and employer_contribution.
        """
        if settings is None:
            settings = ETFSettings.objects.filter(is_active=True).first()

        if not settings:
            return {
                "etf_base": Decimal("0"),
                "employer_contribution": Decimal("0"),
            }

        # ETF uses same base as EPF
        etf_base = EPFCalculator.get_epf_base(employee_salary)

        employer_contribution = (
            etf_base * settings.employer_rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "etf_base": etf_base,
            "employer_contribution": employer_contribution,
        }
