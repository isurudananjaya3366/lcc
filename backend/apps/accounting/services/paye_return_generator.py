"""
PAYE return generator service.

Generates PAYE returns by fetching payroll data, applying Sri Lankan
tax brackets, building employee schedules, and producing exports.
"""

import csv
import io
from datetime import date
from decimal import Decimal

from django.template.loader import render_to_string

from apps.accounting.models.paye_return import PAYEReturn
from apps.accounting.models.tax_period import TaxPeriodRecord

# Sri Lanka PAYE monthly tax brackets (2024-2026)
MONTHLY_TAX_BRACKETS = [
    (Decimal("100000"), Decimal("0")),       # First 100,000: 0%
    (Decimal("41667"), Decimal("6")),         # Next 41,667: 6%
    (Decimal("41666"), Decimal("12")),        # Next 41,666: 12%
    (Decimal("41667"), Decimal("18")),        # Next 41,667: 18%
    (Decimal("41667"), Decimal("24")),        # Next 41,667: 24%
    (Decimal("41667"), Decimal("30")),        # Next 41,667: 30%
    (None, Decimal("36")),                    # Balance: 36%
]


class PAYEReturnGenerator:
    """Generates PAYE returns from payroll data for a given period."""

    def __init__(self, period: TaxPeriodRecord):
        self.period = period

    def generate(self) -> PAYEReturn:
        """Generate a complete PAYE return for the period."""
        payroll_data = self._get_payroll_data()
        enriched = self._calculate_tax_brackets(payroll_data)
        schedule = self._build_employee_schedule(enriched)

        total_employees = len(enriched)
        total_remuneration = sum(e["gross_salary"] for e in enriched)
        total_paye = sum(e["paye_calculated"] for e in enriched)

        paye_return = PAYEReturn(
            period=self.period,
            total_employees=total_employees,
            total_remuneration=total_remuneration,
            total_paye_deducted=total_paye,
            employee_details=schedule,
        )
        paye_return.save()
        return paye_return

    def _get_payroll_data(self) -> list:
        """Fetch payroll data for the period from journal entries."""
        from apps.accounting.models import JournalEntry

        employees = []
        entries = JournalEntry.objects.filter(
            entry_date__gte=self.period.start_date,
            entry_date__lte=self.period.end_date,
            entry_source="PAYROLL",
            entry_status="POSTED",
        )

        for entry in entries:
            salary_lines = entry.lines.filter(
                account__code__startswith="5-1",  # Salary expense accounts
            )
            paye_lines = entry.lines.filter(
                account__code__startswith="2-3",  # PAYE liability accounts
            )

            gross = sum(l.debit_amount for l in salary_lines)
            paye_deducted = sum(l.credit_amount for l in paye_lines)
            epf_employee = gross * Decimal("0.08")
            taxable = gross - epf_employee

            if gross > 0:
                employees.append({
                    "entry_number": entry.entry_number,
                    "name": entry.description if hasattr(entry, "description") else f"Employee-{entry.entry_number}",
                    "nic": "",
                    "basic_salary": gross,
                    "allowances": Decimal("0"),
                    "gross_salary": gross,
                    "epf_employee": epf_employee,
                    "taxable_income": taxable,
                    "paye_deducted": paye_deducted,
                })

        return employees

    def _calculate_tax_brackets(self, payroll_data: list) -> list:
        """Apply Sri Lanka progressive tax brackets to each employee."""
        for employee in payroll_data:
            taxable = employee["taxable_income"]
            total_tax = Decimal("0")
            remaining = taxable
            bracket_details = []

            for slab_amount, rate in MONTHLY_TAX_BRACKETS:
                if remaining <= 0:
                    break

                if slab_amount is None:
                    taxable_in_slab = remaining
                else:
                    taxable_in_slab = min(remaining, slab_amount)

                tax_in_slab = (taxable_in_slab * rate / 100).quantize(Decimal("0.01"))
                total_tax += tax_in_slab
                remaining -= taxable_in_slab

                bracket_details.append({
                    "rate": str(rate),
                    "taxable_amount": str(taxable_in_slab),
                    "tax_amount": str(tax_in_slab),
                })

            employee["paye_calculated"] = total_tax
            employee["bracket_details"] = bracket_details

        return payroll_data

    def _build_employee_schedule(self, enriched_data: list) -> dict:
        """Build employee schedule JSON for the return."""
        sorted_data = sorted(enriched_data, key=lambda e: e.get("name", ""))

        employees = []
        for idx, emp in enumerate(sorted_data, 1):
            employees.append({
                "no": idx,
                "name": emp.get("name", ""),
                "nic": emp.get("nic", ""),
                "basic_salary": str(emp["basic_salary"]),
                "allowances": str(emp.get("allowances", Decimal("0"))),
                "gross_salary": str(emp["gross_salary"]),
                "epf_employee": str(emp["epf_employee"]),
                "taxable_income": str(emp["taxable_income"]),
                "paye_deducted": str(emp["paye_calculated"]),
            })

        totals = {
            "total_basic": str(sum(e["basic_salary"] for e in enriched_data)),
            "total_gross": str(sum(e["gross_salary"] for e in enriched_data)),
            "total_taxable": str(sum(e["taxable_income"] for e in enriched_data)),
            "total_paye": str(sum(e["paye_calculated"] for e in enriched_data)),
        }

        return {
            "employees": employees,
            "totals": totals,
            "metadata": {
                "period": f"{self.period.year}-{self.period.period_number:02d}",
                "employee_count": len(employees),
                "generated_date": date.today().isoformat(),
            },
        }

    def get_summary_by_bracket(self, paye_return: PAYEReturn) -> dict:
        """Aggregate PAYE data by tax bracket."""
        employees = paye_return.employee_details.get("employees", [])
        bracket_summary = {}

        for emp in employees:
            taxable = Decimal(emp.get("taxable_income", "0"))
            paye = Decimal(emp.get("paye_deducted", "0"))

            # Determine highest bracket
            bracket = self._get_bracket_label(taxable)
            if bracket not in bracket_summary:
                bracket_summary[bracket] = {
                    "count": 0,
                    "total_income": Decimal("0"),
                    "total_paye": Decimal("0"),
                }
            bracket_summary[bracket]["count"] += 1
            bracket_summary[bracket]["total_income"] += taxable
            bracket_summary[bracket]["total_paye"] += paye

        result = []
        for bracket, data in sorted(bracket_summary.items()):
            avg_rate = (data["total_paye"] / data["total_income"] * 100).quantize(Decimal("0.01")) if data["total_income"] else Decimal("0")
            result.append({
                "bracket": bracket,
                "employee_count": data["count"],
                "total_income": str(data["total_income"]),
                "total_paye": str(data["total_paye"]),
                "average_effective_rate": str(avg_rate),
            })

        return {"brackets": result}

    def _get_bracket_label(self, monthly_taxable: Decimal) -> str:
        if monthly_taxable <= 100000:
            return "0% (up to 100K)"
        elif monthly_taxable <= 141667:
            return "6% (100K-141K)"
        elif monthly_taxable <= 183333:
            return "12% (141K-183K)"
        elif monthly_taxable <= 225000:
            return "18% (183K-225K)"
        elif monthly_taxable <= 266667:
            return "24% (225K-267K)"
        elif monthly_taxable <= 308334:
            return "30% (267K-308K)"
        else:
            return "36% (308K+)"

    def get_ytd_summary(self, year: int) -> dict:
        """Get year-to-date PAYE summary across all months."""
        ytd_returns = PAYEReturn.objects.filter(
            period__year=year,
            period__tax_type="paye",
            is_active=True,
        ).order_by("period__period_number")

        months = []
        ytd_remuneration = Decimal("0")
        ytd_paye = Decimal("0")

        for ret in ytd_returns:
            ytd_remuneration += ret.total_remuneration
            ytd_paye += ret.total_paye_deducted
            months.append({
                "month": ret.period.period_number,
                "employees": ret.total_employees,
                "remuneration": str(ret.total_remuneration),
                "paye": str(ret.total_paye_deducted),
                "ytd_remuneration": str(ytd_remuneration),
                "ytd_paye": str(ytd_paye),
            })

        return {
            "year": year,
            "months": months,
            "ytd_totals": {
                "total_remuneration": str(ytd_remuneration),
                "total_paye": str(ytd_paye),
                "effective_rate": str(
                    (ytd_paye / ytd_remuneration * 100).quantize(Decimal("0.01"))
                    if ytd_remuneration else Decimal("0")
                ),
            },
        }

    def export_csv(self, paye_return: PAYEReturn) -> str:
        """Export PAYE return as CSV for IRD submission."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\r\n")

        writer.writerow(["PAYE RETURN - T-10 FORM"])
        writer.writerow(["Period", f"{paye_return.period.year}-{paye_return.period.period_number:02d}"])
        writer.writerow(["Reference", paye_return.reference_number])
        writer.writerow([])

        writer.writerow(["No", "Name", "NIC", "Gross Salary", "Taxable Income", "PAYE Deducted"])

        for emp in paye_return.employee_details.get("employees", []):
            writer.writerow([
                emp.get("no", ""),
                emp.get("name", ""),
                emp.get("nic", ""),
                emp.get("gross_salary", "0"),
                emp.get("taxable_income", "0"),
                emp.get("paye_deducted", "0"),
            ])

        writer.writerow([])
        writer.writerow(["TOTALS"])
        writer.writerow(["Total Employees", paye_return.total_employees])
        writer.writerow(["Total Remuneration", str(paye_return.total_remuneration)])
        writer.writerow(["Total PAYE Deducted", str(paye_return.total_paye_deducted)])

        return output.getvalue()

    def render_pdf_html(self, paye_return: PAYEReturn) -> str:
        """Render PAYE return as HTML for PDF generation."""
        context = {
            "paye_return": paye_return,
            "period": self.period,
            "employees": paye_return.employee_details.get("employees", []),
            "totals": paye_return.employee_details.get("totals", {}),
            "generated_date": date.today().isoformat(),
        }
        return render_to_string("tax/paye_return.html", context)
