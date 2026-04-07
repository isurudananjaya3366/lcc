import csv
import io
import json
import logging

from django.utils import timezone

logger = logging.getLogger(__name__)


class AttendanceExportService:
    """Service for exporting attendance reports to CSV, Excel, and JSON."""

    @classmethod
    def export_daily_csv(cls, date, department=None):
        """Export daily attendance report as CSV string."""
        from apps.attendance.services.report_service import AttendanceReportService

        data = AttendanceReportService.daily_summary(date, department=department)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Employee ID", "Name", "Status", "Clock In", "Clock Out", "Work Hours", "Late Minutes"])
        for emp in data.get("employees", []):
            writer.writerow([
                emp.get("employee_id", ""),
                emp.get("name", ""),
                emp.get("status", ""),
                emp.get("clock_in", ""),
                emp.get("clock_out", ""),
                emp.get("work_hours", 0),
                emp.get("late_minutes", 0),
            ])

        return output.getvalue()

    @classmethod
    def export_monthly_csv(cls, year, month, department=None):
        """Export monthly payroll integration data as CSV."""
        from apps.attendance.services.report_service import AttendanceReportService

        data = AttendanceReportService.payroll_integration_data(year, month, department=department)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Employee ID", "Name", "Present Days", "Absent Days", "Half Days",
            "Total Work Hours", "Total OT Hours", "Total Late Minutes",
        ])
        for emp in data.get("employees", []):
            writer.writerow([
                emp.get("employee_id", ""),
                emp.get("employee_name", ""),
                emp.get("present_days", 0),
                emp.get("absent_days", 0),
                emp.get("half_days", 0),
                emp.get("total_work_hours", 0),
                emp.get("total_overtime_hours", 0),
                emp.get("total_late_minutes", 0),
            ])

        return output.getvalue()

    @classmethod
    def export_late_arrivals_csv(cls, start_date, end_date, department=None):
        """Export late arrivals report as CSV."""
        from apps.attendance.services.report_service import AttendanceReportService

        data = AttendanceReportService.late_arrivals_report(start_date, end_date, department=department)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Date", "Employee ID", "Name", "Shift Start", "Clock In", "Late Minutes"])
        for rec in data.get("records", []):
            writer.writerow([
                rec.get("date", ""),
                rec.get("employee_id", ""),
                rec.get("employee_name", ""),
                rec.get("shift_start", ""),
                rec.get("clock_in", ""),
                rec.get("late_minutes", 0),
            ])

        return output.getvalue()

    @classmethod
    def export_daily_excel(cls, date, department=None):
        """Export daily attendance report as Excel bytes (xlsx)."""
        try:
            from openpyxl import Workbook
        except ImportError:
            logger.warning("openpyxl not installed, falling back to CSV")
            return cls.export_daily_csv(date, department=department).encode()

        from apps.attendance.services.report_service import AttendanceReportService

        data = AttendanceReportService.daily_summary(date, department=department)
        wb = Workbook()
        ws = wb.active
        ws.title = f"Attendance {date}"

        headers = ["Employee ID", "Name", "Status", "Clock In", "Clock Out", "Work Hours", "Late Minutes"]
        ws.append(headers)

        for emp in data.get("employees", []):
            ws.append([
                emp.get("employee_id", ""),
                emp.get("name", ""),
                emp.get("status", ""),
                emp.get("clock_in", ""),
                emp.get("clock_out", ""),
                emp.get("work_hours", 0),
                emp.get("late_minutes", 0),
            ])

        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    @classmethod
    def export_monthly_excel(cls, year, month, department=None):
        """Export monthly payroll data as Excel bytes (xlsx)."""
        try:
            from openpyxl import Workbook
        except ImportError:
            logger.warning("openpyxl not installed, falling back to CSV")
            return cls.export_monthly_csv(year, month, department=department).encode()

        from apps.attendance.services.report_service import AttendanceReportService

        data = AttendanceReportService.payroll_integration_data(year, month, department=department)
        wb = Workbook()
        ws = wb.active
        ws.title = f"Payroll {year}-{month:02d}"

        headers = [
            "Employee ID", "Name", "Present Days", "Absent Days", "Half Days",
            "Total Work Hours", "Total OT Hours", "Total Late Minutes",
        ]
        ws.append(headers)

        for emp in data.get("employees", []):
            ws.append([
                emp.get("employee_id", ""),
                emp.get("employee_name", ""),
                emp.get("present_days", 0),
                emp.get("absent_days", 0),
                emp.get("half_days", 0),
                emp.get("total_work_hours", 0),
                emp.get("total_overtime_hours", 0),
                emp.get("total_late_minutes", 0),
            ])

        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    @classmethod
    def export_daily_json(cls, date, department=None):
        """Export daily attendance report as JSON string."""
        from apps.attendance.services.report_service import AttendanceReportService

        data = AttendanceReportService.daily_summary(date, department=department)
        return json.dumps(data, indent=2, default=str)

    @classmethod
    def export_monthly_json(cls, year, month, department=None):
        """Export monthly payroll data as JSON string."""
        from apps.attendance.services.report_service import AttendanceReportService

        data = AttendanceReportService.payroll_integration_data(year, month, department=department)
        return json.dumps(data, indent=2, default=str)

    # ── PDF Exports ─────────────────────────────────────────

    @classmethod
    def export_daily_pdf(cls, date, department=None):
        """Export daily attendance report as PDF bytes.

        Falls back to CSV bytes if reportlab is not available.
        """
        from apps.attendance.services.report_service import AttendanceReportService

        data = AttendanceReportService.daily_summary(date, department=department)

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors

            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = [Paragraph(f"Daily Attendance Report – {date}", styles["Title"])]

            table_data = [["Employee ID", "Name", "Status", "Clock In", "Clock Out", "Work Hours"]]
            for emp in data.get("employees", []):
                table_data.append([
                    str(emp.get("employee_id", "")),
                    str(emp.get("name", "")),
                    str(emp.get("status", "")),
                    str(emp.get("clock_in", "")),
                    str(emp.get("clock_out", "")),
                    str(emp.get("work_hours", 0)),
                ])

            table = Table(table_data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)
            doc.build(elements)
            return output.getvalue()
        except ImportError:
            logger.warning("reportlab not installed, falling back to CSV bytes")
            return cls.export_daily_csv(date, department=department).encode()

    @classmethod
    def export_monthly_pdf(cls, year, month, department=None):
        """Export monthly payroll data as PDF bytes.

        Falls back to CSV bytes if reportlab is not available.
        """
        from apps.attendance.services.report_service import AttendanceReportService

        data = AttendanceReportService.payroll_integration_data(year, month, department=department)

        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors

            output = io.BytesIO()
            doc = SimpleDocTemplate(output, pagesize=landscape(A4))
            styles = getSampleStyleSheet()
            elements = [Paragraph(f"Monthly Payroll Report – {year}-{month:02d}", styles["Title"])]

            table_data = [[
                "Employee ID", "Name", "Present", "Absent", "Half Days",
                "Work Hours", "OT Hours", "Late Min",
            ]]
            for emp in data.get("employees", []):
                table_data.append([
                    str(emp.get("employee_id", "")),
                    str(emp.get("employee_name", "")),
                    str(emp.get("present_days", 0)),
                    str(emp.get("absent_days", 0)),
                    str(emp.get("half_days", 0)),
                    str(emp.get("total_work_hours", 0)),
                    str(emp.get("total_overtime_hours", 0)),
                    str(emp.get("total_late_minutes", 0)),
                ])

            table = Table(table_data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)
            doc.build(elements)
            return output.getvalue()
        except ImportError:
            logger.warning("reportlab not installed, falling back to CSV bytes")
            return cls.export_monthly_csv(year, month, department=department).encode()

    # ── Async wrapper (Celery) ──────────────────────────────

    @classmethod
    def export_async(cls, export_format, export_type, **kwargs):
        """Queue an export job for background processing via Celery.

        Args:
            export_format: 'csv', 'excel', 'json', or 'pdf'
            export_type: 'daily' or 'monthly'
            **kwargs: Parameters passed to the underlying export method.

        Returns:
            dict with task_id or the export result if Celery is unavailable.
        """
        method_map = {
            ("csv", "daily"): cls.export_daily_csv,
            ("csv", "monthly"): cls.export_monthly_csv,
            ("excel", "daily"): cls.export_daily_excel,
            ("excel", "monthly"): cls.export_monthly_excel,
            ("json", "daily"): cls.export_daily_json,
            ("json", "monthly"): cls.export_monthly_json,
            ("pdf", "daily"): cls.export_daily_pdf,
            ("pdf", "monthly"): cls.export_monthly_pdf,
        }

        method = method_map.get((export_format, export_type))
        if not method:
            raise ValueError(f"Unsupported export: format={export_format}, type={export_type}")

        try:
            from apps.attendance.tasks import run_export_task
            task = run_export_task.delay(export_format, export_type, kwargs)
            return {"task_id": str(task.id), "status": "queued"}
        except Exception:
            logger.info("Celery unavailable, running export synchronously")
            return method(**kwargs)
