"""Statutory report generation service for EPF, ETF, and PAYE returns."""

import csv
import io
import logging
from decimal import Decimal

from django.utils import timezone

from apps.payroll.models.epf_contribution import EPFContribution
from apps.payroll.models.etf_contribution import ETFContribution
from apps.payroll.models.paye_calculation import PAYECalculation

logger = logging.getLogger(__name__)


class StatutoryReportService:
    """Generates statutory return reports for EPF, ETF, and PAYE."""

    def generate_epf_return(self, payroll_run, fmt="csv"):
        """Generate EPF return report (Form C) for a payroll run.

        Args:
            payroll_run: PayrollRun instance.
            fmt: Output format ('csv').

        Returns:
            dict with 'content' (file bytes), 'filename', and 'content_type'.
        """
        contributions = EPFContribution.objects.filter(
            employee_payroll__payroll_run=payroll_run,
        ).select_related(
            "employee_payroll__employee",
        ).order_by("employee_payroll__employee__first_name")

        period = payroll_run.payroll_period
        report_date = timezone.now().date()

        rows = []
        total_epf_base = Decimal("0.00")
        total_employee = Decimal("0.00")
        total_employer = Decimal("0.00")
        total_combined = Decimal("0.00")

        for c in contributions:
            emp = c.employee_payroll.employee
            emp_name = f"{getattr(emp, 'first_name', '')} {getattr(emp, 'last_name', '')}".strip()
            rows.append({
                "epf_number": c.epf_number,
                "employee_name": emp_name,
                "nic": getattr(emp, "nic_number", ""),
                "epf_base": c.epf_base,
                "employee_amount": c.employee_amount,
                "employer_amount": c.employer_amount,
                "total_amount": c.total_amount,
            })
            total_epf_base += c.epf_base
            total_employee += c.employee_amount
            total_employer += c.employer_amount
            total_combined += c.total_amount

        summary = {
            "period": f"{period.period_year}-{period.period_month:02d}",
            "report_date": str(report_date),
            "total_employees": len(rows),
            "total_epf_base": str(total_epf_base),
            "total_employee_contribution": str(total_employee),
            "total_employer_contribution": str(total_employer),
            "total_contribution": str(total_combined),
        }

        if fmt == "csv":
            return self._build_epf_csv(rows, summary, period)

        return {"rows": rows, "summary": summary}

    def _build_epf_csv(self, rows, summary, period):
        """Build CSV file content for EPF return."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["EPF Return Report"])
        writer.writerow(["Period", summary["period"]])
        writer.writerow(["Generated", summary["report_date"]])
        writer.writerow([])
        writer.writerow([
            "EPF Number", "Employee Name", "NIC",
            "EPF Base (LKR)", "Employee (LKR)", "Employer (LKR)", "Total (LKR)",
        ])

        for row in rows:
            writer.writerow([
                row["epf_number"],
                row["employee_name"],
                row["nic"],
                row["epf_base"],
                row["employee_amount"],
                row["employer_amount"],
                row["total_amount"],
            ])

        writer.writerow([])
        writer.writerow([
            "", "TOTALS", "",
            summary["total_epf_base"],
            summary["total_employee_contribution"],
            summary["total_employer_contribution"],
            summary["total_contribution"],
        ])

        filename = f"EPF_Return_{period.period_year}_{period.period_month:02d}.csv"
        return {
            "content": output.getvalue().encode("utf-8"),
            "filename": filename,
            "content_type": "text/csv",
        }

    def generate_etf_return(self, payroll_run, fmt="csv"):
        """Generate ETF return report for Central Bank submission.

        Args:
            payroll_run: PayrollRun instance.
            fmt: Output format ('csv').

        Returns:
            dict with 'content' (file bytes), 'filename', and 'content_type'.
        """
        contributions = ETFContribution.objects.filter(
            employee_payroll__payroll_run=payroll_run,
        ).select_related(
            "employee_payroll__employee",
        ).order_by("employee_payroll__employee__first_name")

        period = payroll_run.payroll_period
        report_date = timezone.now().date()

        rows = []
        total_etf_base = Decimal("0.00")
        total_employer = Decimal("0.00")

        for c in contributions:
            emp = c.employee_payroll.employee
            emp_name = f"{getattr(emp, 'first_name', '')} {getattr(emp, 'last_name', '')}".strip()
            rows.append({
                "employee_name": emp_name,
                "nic": getattr(emp, "nic_number", ""),
                "etf_base": c.etf_base,
                "employer_amount": c.employer_amount,
            })
            total_etf_base += c.etf_base
            total_employer += c.employer_amount

        summary = {
            "period": f"{period.period_year}-{period.period_month:02d}",
            "report_date": str(report_date),
            "total_employees": len(rows),
            "total_etf_base": str(total_etf_base),
            "total_employer_contribution": str(total_employer),
        }

        if fmt == "csv":
            return self._build_etf_csv(rows, summary, period)

        return {"rows": rows, "summary": summary}

    def _build_etf_csv(self, rows, summary, period):
        """Build CSV file content for ETF return."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["ETF Return Report"])
        writer.writerow(["Period", summary["period"]])
        writer.writerow(["Generated", summary["report_date"]])
        writer.writerow([])
        writer.writerow([
            "Employee Name", "NIC", "ETF Base (LKR)", "Employer Contribution (LKR)",
        ])

        for row in rows:
            writer.writerow([
                row["employee_name"],
                row["nic"],
                row["etf_base"],
                row["employer_amount"],
            ])

        writer.writerow([])
        writer.writerow([
            "TOTALS", "",
            summary["total_etf_base"],
            summary["total_employer_contribution"],
        ])

        filename = f"ETF_Return_{period.period_year}_{period.period_month:02d}.csv"
        return {
            "content": output.getvalue().encode("utf-8"),
            "filename": filename,
            "content_type": "text/csv",
        }

    def generate_paye_return(self, payroll_run, fmt="csv"):
        """Generate PAYE return report for IRD submission.

        Args:
            payroll_run: PayrollRun instance.
            fmt: Output format ('csv').

        Returns:
            dict with 'content' (file bytes), 'filename', and 'content_type'.
        """
        calculations = PAYECalculation.objects.filter(
            employee_payroll__payroll_run=payroll_run,
        ).select_related(
            "employee_payroll__employee",
        ).order_by("employee_payroll__employee__first_name")

        period = payroll_run.payroll_period
        report_date = timezone.now().date()

        rows = []
        total_gross = Decimal("0.00")
        total_taxable = Decimal("0.00")
        total_tax = Decimal("0.00")

        for c in calculations:
            emp = c.employee_payroll.employee
            emp_name = f"{getattr(emp, 'first_name', '')} {getattr(emp, 'last_name', '')}".strip()
            rows.append({
                "employee_name": emp_name,
                "nic": getattr(emp, "nic_number", ""),
                "gross_income": c.gross_income,
                "taxable_income": c.taxable_income,
                "monthly_tax": c.monthly_tax,
            })
            total_gross += c.gross_income
            total_taxable += c.taxable_income
            total_tax += c.monthly_tax

        summary = {
            "period": f"{period.period_year}-{period.period_month:02d}",
            "report_date": str(report_date),
            "total_employees": len(rows),
            "total_gross_income": str(total_gross),
            "total_taxable_income": str(total_taxable),
            "total_tax_withheld": str(total_tax),
        }

        if fmt == "csv":
            return self._build_paye_csv(rows, summary, period)

        return {"rows": rows, "summary": summary}

    def _build_paye_csv(self, rows, summary, period):
        """Build CSV file content for PAYE return."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["PAYE Return Report"])
        writer.writerow(["Period", summary["period"]])
        writer.writerow(["Generated", summary["report_date"]])
        writer.writerow([])
        writer.writerow([
            "Employee Name", "NIC",
            "Gross Income (LKR)", "Taxable Income (LKR)", "Monthly Tax (LKR)",
        ])

        for row in rows:
            writer.writerow([
                row["employee_name"],
                row["nic"],
                row["gross_income"],
                row["taxable_income"],
                row["monthly_tax"],
            ])

        writer.writerow([])
        writer.writerow([
            "TOTALS", "",
            summary["total_gross_income"],
            summary["total_taxable_income"],
            summary["total_tax_withheld"],
        ])

        filename = f"PAYE_Return_{period.period_year}_{period.period_month:02d}.csv"
        return {
            "content": output.getvalue().encode("utf-8"),
            "filename": filename,
            "content_type": "text/csv",
        }

    # ── Excel Format Support ─────────────────────────────────

    def _build_excel_report(self, headers, rows, title, period, report_type):
        """Build an Excel report from headers and rows.

        Falls back to CSV if openpyxl is not available.
        """
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = title
            ws.append([title])
            ws.append(["Period", f"{period.period_year}-{period.period_month:02d}"])
            ws.append([])
            ws.append(headers)
            for row in rows:
                ws.append(row)

            output = io.BytesIO()
            wb.save(output)
            filename = f"{report_type}_{period.period_year}_{period.period_month:02d}.xlsx"
            return {
                "content": output.getvalue(),
                "filename": filename,
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        except ImportError:
            # Fall back to CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow([title])
            writer.writerow(["Period", f"{period.period_year}-{period.period_month:02d}"])
            writer.writerow([])
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)
            filename = f"{report_type}_{period.period_year}_{period.period_month:02d}.csv"
            return {
                "content": output.getvalue().encode("utf-8"),
                "filename": filename,
                "content_type": "text/csv",
            }

    # ── Payroll Summary Report ───────────────────────────────

    def generate_payroll_summary(self, payroll_run, fmt="csv"):
        """Generate a comprehensive payroll summary report.

        Args:
            payroll_run: PayrollRun instance.
            fmt: Output format ('csv' or 'excel').

        Returns:
            dict with 'content', 'filename', and 'content_type'.
        """
        from apps.payroll.models import EmployeePayroll

        employees = EmployeePayroll.objects.filter(
            payroll_run=payroll_run,
        ).select_related("employee").order_by("employee__first_name")

        period = payroll_run.payroll_period
        headers = [
            "Employee Name", "Basic Salary", "Overtime", "Gross Salary",
            "EPF (Employee)", "PAYE Tax", "Total Deductions", "Net Salary",
            "Payment Status",
        ]
        rows = []

        for ep in employees:
            emp_name = f"{getattr(ep.employee, 'first_name', '')} {getattr(ep.employee, 'last_name', '')}".strip()
            rows.append([
                emp_name,
                str(ep.basic_salary),
                str(ep.overtime_amount),
                str(ep.gross_salary),
                str(ep.epf_employee),
                str(ep.paye_tax),
                str(ep.total_deductions),
                str(ep.net_salary),
                ep.payment_status,
            ])

        # Summary row
        rows.append([])
        rows.append([
            "TOTALS",
            str(payroll_run.total_gross),
            "",
            str(payroll_run.total_gross),
            str(payroll_run.total_epf_employee),
            str(payroll_run.total_paye),
            str(payroll_run.total_deductions),
            str(payroll_run.total_net),
            "",
        ])

        if fmt == "excel":
            return self._build_excel_report(
                headers, rows, "Payroll Summary Report", period, "Payroll_Summary"
            )

        # Default CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Payroll Summary Report"])
        writer.writerow(["Period", f"{period.period_year}-{period.period_month:02d}"])
        writer.writerow(["Run #", payroll_run.run_number])
        writer.writerow([])
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
        filename = f"Payroll_Summary_{period.period_year}_{period.period_month:02d}.csv"
        return {
            "content": output.getvalue().encode("utf-8"),
            "filename": filename,
            "content_type": "text/csv",
        }
