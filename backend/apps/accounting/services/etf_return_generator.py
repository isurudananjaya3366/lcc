"""
ETF return generator service.

Generates ETF returns by calculating 3% employer-only contributions
from payroll data, and producing PDF/CSV exports.
"""

import csv
import io
from datetime import date
from decimal import Decimal

from django.template.loader import render_to_string

from apps.accounting.models.etf_return import ETFReturn
from apps.accounting.models.tax_configuration import TaxConfiguration
from apps.accounting.models.tax_period import TaxPeriodRecord


class ETFReturnGenerator:
    """Generates ETF returns from payroll data."""

    ETF_RATE = Decimal("0.03")

    def __init__(self, period: TaxPeriodRecord):
        self.period = period
        self.tax_config = TaxConfiguration.objects.filter(is_active=True).first()

    def generate(self) -> ETFReturn:
        """Generate a complete ETF return for the period."""
        etf_data = self._get_etf_data()

        etf_return = ETFReturn(
            period=self.period,
            total_contribution=etf_data["total_contribution"],
            total_gross_salary=etf_data["total_gross"],
            total_employees=etf_data["total_employees"],
            employee_schedule=etf_data["schedule"],
        )
        etf_return.save()
        return etf_return

    def _get_etf_data(self) -> dict:
        """Fetch payroll data and calculate ETF contributions."""
        from apps.accounting.models import JournalEntry

        employees = []
        total_contribution = Decimal("0")
        total_gross = Decimal("0")

        entries = JournalEntry.objects.filter(
            entry_date__gte=self.period.start_date,
            entry_date__lte=self.period.end_date,
            entry_source="PAYROLL",
            entry_status="POSTED",
        )

        for entry in entries:
            salary_lines = entry.lines.filter(
                account__code__startswith="5-1",
            )
            gross = sum(l.debit_amount for l in salary_lines)

            if gross > 0:
                contrib = (gross * self.ETF_RATE).quantize(Decimal("0.01"))
                employees.append({
                    "name": entry.description if hasattr(entry, "description") else f"Employee-{entry.entry_number}",
                    "nic": "",
                    "gross_salary": str(gross),
                    "etf_contribution": str(contrib),
                })
                total_contribution += contrib
                total_gross += gross

        return {
            "total_contribution": total_contribution,
            "total_gross": total_gross,
            "total_employees": len(employees),
            "schedule": {
                "employees": employees,
                "summary": {
                    "total_employees": len(employees),
                    "total_gross_salary": str(total_gross),
                    "total_contribution": str(total_contribution),
                    "calculation_date": date.today().isoformat(),
                },
            },
        }

    def export_csv(self, etf_return: ETFReturn) -> str:
        """Export ETF return as CSV for ETF Board submission."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\r\n")

        etf_no = self.tax_config.etf_registration_no if self.tax_config else "N/A"

        writer.writerow(["ETF RETURN"])
        writer.writerow(["Employer ETF No", etf_no])
        writer.writerow(["Period", f"{etf_return.period.year}-{etf_return.period.period_number:02d}"])
        writer.writerow(["Reference", etf_return.reference_number])
        writer.writerow([])

        writer.writerow(["Name", "NIC", "Gross Salary", "ETF Contribution (3%)"])

        for emp in etf_return.employee_schedule.get("employees", []):
            writer.writerow([
                emp.get("name", ""),
                emp.get("nic", ""),
                emp.get("gross_salary", "0"),
                emp.get("etf_contribution", "0"),
            ])

        writer.writerow([])
        writer.writerow(["TOTALS", "", str(etf_return.total_gross_salary), str(etf_return.total_contribution)])

        return output.getvalue()

    def render_pdf_html(self, etf_return: ETFReturn) -> str:
        """Render ETF return as HTML for PDF generation."""
        context = {
            "etf_return": etf_return,
            "tax_config": self.tax_config,
            "period": self.period,
            "employees": etf_return.employee_schedule.get("employees", []),
            "summary": etf_return.employee_schedule.get("summary", {}),
            "generated_date": date.today().isoformat(),
        }
        return render_to_string("tax/etf_return.html", context)
