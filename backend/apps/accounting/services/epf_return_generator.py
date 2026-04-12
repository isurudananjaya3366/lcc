"""
EPF return generator service.

Generates EPF C-Form returns by calculating 8% employee and 12% employer
contributions from payroll data, and producing PDF/CSV exports.
"""

import csv
import io
from datetime import date
from decimal import Decimal

from django.template.loader import render_to_string

from apps.accounting.models.epf_return import EPFReturn
from apps.accounting.models.tax_configuration import TaxConfiguration
from apps.accounting.models.tax_period import TaxPeriodRecord


class EPFReturnGenerator:
    """Generates EPF C-Form returns from payroll data."""

    EMPLOYEE_RATE = Decimal("0.08")
    EMPLOYER_RATE = Decimal("0.12")

    def __init__(self, period: TaxPeriodRecord):
        self.period = period
        self.tax_config = TaxConfiguration.objects.filter(is_active=True).first()

    def generate(self) -> EPFReturn:
        """Generate a complete EPF return for the period."""
        epf_data = self._get_epf_data()

        epf_return = EPFReturn(
            period=self.period,
            total_employee_contribution=epf_data["total_employee"],
            total_employer_contribution=epf_data["total_employer"],
            total_employees=epf_data["total_employees"],
            employee_schedule=epf_data["schedule"],
        )
        epf_return.save()
        return epf_return

    def _get_epf_data(self) -> dict:
        """Fetch payroll data and calculate EPF contributions."""
        from apps.accounting.models import JournalEntry

        schedule = []
        total_employee = Decimal("0")
        total_employer = Decimal("0")

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
                emp_contrib = (gross * self.EMPLOYEE_RATE).quantize(Decimal("0.01"))
                er_contrib = (gross * self.EMPLOYER_RATE).quantize(Decimal("0.01"))

                schedule.append({
                    "employee_name": entry.description if hasattr(entry, "description") else f"Employee-{entry.entry_number}",
                    "nic": "",
                    "gross_salary": str(gross),
                    "employee_contribution": str(emp_contrib),
                    "employer_contribution": str(er_contrib),
                    "total_contribution": str(emp_contrib + er_contrib),
                })
                total_employee += emp_contrib
                total_employer += er_contrib

        return {
            "total_employee": total_employee,
            "total_employer": total_employer,
            "total_employees": len(schedule),
            "schedule": schedule,
        }

    def export_csv(self, epf_return: EPFReturn) -> str:
        """Export EPF C-Form as CSV for CBSL online submission."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\r\n")

        epf_no = self.tax_config.epf_registration_no if self.tax_config else "N/A"

        writer.writerow(["EPF C-FORM"])
        writer.writerow(["Employer EPF No", epf_no])
        writer.writerow(["Period", f"{epf_return.period.year}-{epf_return.period.period_number:02d}"])
        writer.writerow(["Reference", epf_return.reference_number])
        writer.writerow(["Total Members", epf_return.total_employees])
        writer.writerow([])

        writer.writerow(["Name", "NIC", "Gross Salary", "Employee (8%)", "Employer (12%)", "Total (20%)"])

        for emp in epf_return.employee_schedule:
            writer.writerow([
                emp.get("employee_name", ""),
                emp.get("nic", ""),
                emp.get("gross_salary", "0"),
                emp.get("employee_contribution", "0"),
                emp.get("employer_contribution", "0"),
                emp.get("total_contribution", "0"),
            ])

        writer.writerow([])
        writer.writerow([
            "TOTALS", "",
            "", str(epf_return.total_employee_contribution),
            str(epf_return.total_employer_contribution),
            str(epf_return.total_contribution),
        ])

        return output.getvalue()

    def render_pdf_html(self, epf_return: EPFReturn) -> str:
        """Render EPF C-Form as HTML for PDF generation."""
        context = {
            "epf_return": epf_return,
            "tax_config": self.tax_config,
            "period": self.period,
            "schedule": epf_return.employee_schedule,
            "generated_date": date.today().isoformat(),
        }
        return render_to_string("tax/c_form.html", context)
