"""EPF (Employees' Provident Fund) calculator service."""

import logging
from decimal import ROUND_HALF_UP, Decimal

from apps.payroll.constants import ComponentType
from apps.payroll.models.employee_salary_component import EmployeeSalaryComponent
from apps.payroll.models.epf_settings import EPFSettings

logger = logging.getLogger(__name__)


class EPFCalculator:
    """Calculates EPF contributions based on EPF-applicable earnings."""

    @staticmethod
    def get_epf_base(employee_salary):
        """Calculate the EPF base from EPF-applicable earning components."""
        components = EmployeeSalaryComponent.objects.filter(
            employee_salary=employee_salary,
            component__component_type=ComponentType.EARNING,
            component__is_epf_applicable=True,
        ).select_related("component")

        return sum(c.amount for c in components)

    @staticmethod
    def calculate(employee_salary, settings=None):
        """Calculate EPF contributions (employee and employer).

        Returns dict with employee_contribution, employer_contribution, epf_base.
        """
        if settings is None:
            settings = EPFSettings.objects.filter(is_active=True).first()

        if not settings:
            return {
                "epf_base": Decimal("0"),
                "employee_contribution": Decimal("0"),
                "employer_contribution": Decimal("0"),
            }

        epf_base = EPFCalculator.get_epf_base(employee_salary)

        employee_contribution = (
            epf_base * settings.employee_rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        employer_contribution = (
            epf_base * settings.employer_rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Apply ceiling if configured
        if settings.max_contribution_ceiling:
            employee_contribution = min(employee_contribution, settings.max_contribution_ceiling)
            employer_contribution = min(employer_contribution, settings.max_contribution_ceiling)

        return {
            "epf_base": epf_base,
            "employee_contribution": employee_contribution,
            "employer_contribution": employer_contribution,
        }

    @staticmethod
    def calculate_employee_epf(epf_base, settings=None):
        """Calculate employee EPF contribution from a given base."""
        if settings is None:
            settings = EPFSettings.objects.filter(is_active=True).first()
        if not settings:
            return Decimal("0")
        return (
            epf_base * settings.employee_rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_employer_epf(epf_base, settings=None):
        """Calculate employer EPF contribution from a given base."""
        if settings is None:
            settings = EPFSettings.objects.filter(is_active=True).first()
        if not settings:
            return Decimal("0")
        return (
            epf_base * settings.employer_rate / Decimal("100")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_total_epf(epf_base, settings=None):
        """Calculate total (employee + employer) EPF contribution."""
        employee = EPFCalculator.calculate_employee_epf(epf_base, settings)
        employer = EPFCalculator.calculate_employer_epf(epf_base, settings)
        return employee + employer
