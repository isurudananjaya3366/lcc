"""PAYE (Pay As You Earn) tax calculator service for Sri Lanka."""

import logging
from decimal import ROUND_HALF_UP, Decimal

from apps.payroll.constants import ComponentType
from apps.payroll.models.employee_salary_component import EmployeeSalaryComponent
from apps.payroll.models.paye_slab import PAYETaxSlab
from apps.payroll.models.tax_exemption import TaxExemption

logger = logging.getLogger(__name__)


class PAYECalculator:
    """Calculates PAYE income tax using progressive tax slabs."""

    @staticmethod
    def get_taxable_income(employee_salary):
        """Calculate monthly taxable income from taxable earning components."""
        components = EmployeeSalaryComponent.objects.filter(
            employee_salary=employee_salary,
            component__component_type=ComponentType.EARNING,
            component__is_taxable=True,
        ).select_related("component")

        return sum(c.amount for c in components)

    @staticmethod
    def get_monthly_exemptions():
        """Get total monthly tax exemption amount."""
        exemptions = TaxExemption.objects.filter(is_active=True)
        return sum(e.monthly_amount for e in exemptions)

    @staticmethod
    def calculate_annual_tax(annual_taxable_income, tax_year=None):
        """Calculate annual tax using progressive slab rates."""
        if tax_year is None:
            from django.utils import timezone
            tax_year = timezone.now().year

        slabs = PAYETaxSlab.objects.filter(
            tax_year=tax_year, is_active=True
        ).order_by("from_amount")

        if not slabs.exists():
            return Decimal("0")

        total_tax = Decimal("0")
        remaining_income = annual_taxable_income

        for slab in slabs:
            if remaining_income <= 0:
                break

            if slab.to_amount is not None:
                slab_range = slab.to_amount - slab.from_amount
                taxable_in_slab = min(remaining_income, slab_range)
            else:
                taxable_in_slab = remaining_income

            slab_tax = (
                taxable_in_slab * slab.rate / Decimal("100")
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            total_tax += slab_tax
            remaining_income -= taxable_in_slab

        return total_tax

    @staticmethod
    def calculate(employee_salary, tax_year=None):
        """Calculate monthly PAYE tax for an employee salary.

        Returns dict with monthly_taxable, annual_projection, annual_tax, monthly_tax.
        """
        monthly_taxable = PAYECalculator.get_taxable_income(employee_salary)
        monthly_exemptions = PAYECalculator.get_monthly_exemptions()

        net_monthly_taxable = max(monthly_taxable - monthly_exemptions, Decimal("0"))
        annual_projection = net_monthly_taxable * 12

        annual_tax = PAYECalculator.calculate_annual_tax(annual_projection, tax_year)
        monthly_tax = (annual_tax / 12).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return {
            "monthly_taxable_income": monthly_taxable,
            "monthly_exemptions": monthly_exemptions,
            "net_monthly_taxable": net_monthly_taxable,
            "annual_projection": annual_projection,
            "annual_tax": annual_tax,
            "monthly_tax": monthly_tax,
        }

    @staticmethod
    def get_tax_slab(annual_income, tax_year=None):
        """Find the applicable tax slab for a given annual income."""
        if tax_year is None:
            from django.utils import timezone
            tax_year = timezone.now().year

        return PAYETaxSlab.objects.filter(
            tax_year=tax_year,
            is_active=True,
            from_amount__lte=annual_income,
        ).order_by("-from_amount").first()

    @staticmethod
    def project_annual_tax(monthly_income, current_month=None, ytd_income=None, tax_year=None):
        """Project annual tax from monthly income with YTD adjustment.

        Handles mid-year starts and YTD income already earned.
        """
        if tax_year is None:
            from django.utils import timezone
            tax_year = timezone.now().year

        if current_month is None:
            from django.utils import timezone
            current_month = timezone.now().month

        remaining_months = 12 - current_month + 1

        if ytd_income is not None:
            projected_annual = ytd_income + (monthly_income * remaining_months)
        else:
            projected_annual = monthly_income * 12

        annual_tax = PAYECalculator.calculate_annual_tax(projected_annual, tax_year)

        if remaining_months > 0:
            monthly_tax = (annual_tax / remaining_months).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            monthly_tax = Decimal("0")

        return {
            "projected_annual_income": projected_annual,
            "projected_annual_tax": annual_tax,
            "adjusted_monthly_tax": monthly_tax,
            "remaining_months": remaining_months,
            "current_month": current_month,
        }

    @staticmethod
    def get_effective_rate(total_income, tax_year=None):
        """Calculate the effective tax rate for a given total income."""
        annual_tax = PAYECalculator.calculate_annual_tax(total_income, tax_year)
        if total_income and total_income > 0:
            return (annual_tax / total_income * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        return Decimal("0")
