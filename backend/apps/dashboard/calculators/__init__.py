"""Dashboard calculators package."""

from apps.dashboard.calculators.base import BaseKPICalculator
from apps.dashboard.calculators.financial import FinancialKPICalculator
from apps.dashboard.calculators.hr import HRKPICalculator
from apps.dashboard.calculators.inventory import InventoryKPICalculator
from apps.dashboard.calculators.sales import SalesKPICalculator

__all__ = [
    "BaseKPICalculator",
    "FinancialKPICalculator",
    "HRKPICalculator",
    "InventoryKPICalculator",
    "SalesKPICalculator",
]
