"""Salary data export service for reporting."""

import csv
import io
import logging
from decimal import Decimal

from apps.payroll.constants import ComponentType
from apps.payroll.models.employee_salary import EmployeeSalary
from apps.payroll.services.epf_calculator import EPFCalculator
from apps.payroll.services.etf_calculator import ETFCalculator
from apps.payroll.services.paye_calculator import PAYECalculator

logger = logging.getLogger(__name__)


class SalaryExportService:
    """Exports salary data for reports and external systems."""

    @staticmethod
    def export_current_salaries(queryset=None, output_format="csv"):
        """Export current employee salaries to CSV with statutory deductions."""
        if queryset is None:
            queryset = EmployeeSalary.objects.filter(
                is_current=True
            ).select_related("employee", "template")

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Employee ID",
            "Employee Name",
            "Department",
            "Basic Salary",
            "Allowances",
            "Gross Salary",
            "EPF Employee",
            "PAYE",
            "Total Deductions",
            "Net Salary",
            "EPF Employer",
            "ETF",
            "Employer Cost",
        ])

        totals = {k: Decimal("0") for k in [
            "basic", "allowances", "gross", "epf_ee", "paye",
            "total_ded", "net", "epf_er", "etf", "employer_cost",
        ]}

        for salary in queryset:
            epf = EPFCalculator.calculate(salary)
            etf = ETFCalculator.calculate(salary)
            paye = PAYECalculator.calculate(salary)

            allowances = salary.gross_salary - salary.basic_salary
            epf_ee = epf["employee_contribution"]
            epf_er = epf["employer_contribution"]
            etf_amt = etf["employer_contribution"]
            paye_amt = paye["monthly_tax"]
            total_ded = epf_ee + paye_amt
            net = salary.gross_salary - total_ded
            employer_cost = salary.gross_salary + epf_er + etf_amt

            dept = ""
            if hasattr(salary.employee, "department") and salary.employee.department:
                dept = str(salary.employee.department)

            writer.writerow([
                str(salary.employee.employee_id) if hasattr(salary.employee, "employee_id") else str(salary.employee_id),
                str(salary.employee),
                dept,
                str(salary.basic_salary),
                str(allowances),
                str(salary.gross_salary),
                str(epf_ee),
                str(paye_amt),
                str(total_ded),
                str(net),
                str(epf_er),
                str(etf_amt),
                str(employer_cost),
            ])

            totals["basic"] += salary.basic_salary
            totals["allowances"] += allowances
            totals["gross"] += salary.gross_salary
            totals["epf_ee"] += epf_ee
            totals["paye"] += paye_amt
            totals["total_ded"] += total_ded
            totals["net"] += net
            totals["epf_er"] += epf_er
            totals["etf"] += etf_amt
            totals["employer_cost"] += employer_cost

        writer.writerow([
            "", "TOTALS", "",
            str(totals["basic"]),
            str(totals["allowances"]),
            str(totals["gross"]),
            str(totals["epf_ee"]),
            str(totals["paye"]),
            str(totals["total_ded"]),
            str(totals["net"]),
            str(totals["epf_er"]),
            str(totals["etf"]),
            str(totals["employer_cost"]),
        ])

        return output.getvalue()

    @staticmethod
    def export_salary_breakdown(employee_salary):
        """Export detailed salary breakdown for a single employee."""
        components = employee_salary.salary_components.select_related(
            "component"
        ).order_by("component__display_order")

        earnings = []
        deductions = []
        contributions = []

        for esc in components:
            entry = {
                "name": esc.component.name,
                "code": esc.component.code,
                "amount": str(esc.amount),
            }
            if esc.component.component_type == ComponentType.EARNING:
                earnings.append(entry)
            elif esc.component.component_type == ComponentType.DEDUCTION:
                deductions.append(entry)
            else:
                contributions.append(entry)

        return {
            "employee": str(employee_salary.employee),
            "basic_salary": str(employee_salary.basic_salary),
            "gross_salary": str(employee_salary.gross_salary),
            "effective_from": str(employee_salary.effective_from),
            "earnings": earnings,
            "deductions": deductions,
            "employer_contributions": contributions,
        }
