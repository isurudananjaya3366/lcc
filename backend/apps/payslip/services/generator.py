"""PayslipGenerator service for rendering HTML and converting to PDF."""

import logging
from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from apps.payslip.constants import PayslipStatus
from apps.payslip.models.payslip import Payslip
from apps.payslip.models.payslip_template import PayslipTemplate

logger = logging.getLogger(__name__)


class PayslipGenerationError(Exception):
    """Base exception for payslip generation failures."""


class PayslipGenerator:
    """Orchestrates payslip PDF generation using WeasyPrint.

    Builds a template context from payslip data, renders HTML,
    converts to PDF, and saves the file to the payslip record.
    """

    TEMPLATE_NAME = "payslip/payslip_template.html"

    def __init__(self):
        self._template_cache = None

    # ── Public Methods ───────────────────────────────────────

    def generate(self, payslip_id, user=None):
        """Generate PDF for a single payslip and save to storage.

        Args:
            payslip_id: UUID of the Payslip record.
            user: User who triggered generation (for audit).

        Returns:
            Payslip instance with PDF attached.

        Raises:
            PayslipGenerationError: If generation fails.
        """
        try:
            payslip = (
                Payslip.objects.select_related(
                    "employee",
                    "payroll_period",
                    "employee_payroll",
                )
                .prefetch_related(
                    "earnings",
                    "deductions",
                    "employer_contributions",
                )
                .get(pk=payslip_id)
            )
        except Payslip.DoesNotExist:
            raise PayslipGenerationError(
                f"Payslip {payslip_id} not found."
            )

        logger.info("Generating PDF for payslip %s", payslip.slip_number)

        template = self._get_template()
        context = self._build_context(payslip, template)
        html_content = self._render_html(context)
        pdf_bytes = self._html_to_pdf(html_content)

        self._save_pdf(payslip, pdf_bytes, user)

        logger.info(
            "PDF generated for %s (%d bytes)",
            payslip.slip_number,
            len(pdf_bytes),
        )
        return payslip

    def regenerate(self, payslip_id, user=None):
        """Regenerate PDF for an existing payslip.

        Deletes the old PDF file (if any) and generates a new one.

        Args:
            payslip_id: UUID of the Payslip record.
            user: User who triggered regeneration.

        Returns:
            Payslip instance with new PDF.
        """
        payslip = Payslip.objects.get(pk=payslip_id)

        # Delete old file if exists
        if payslip.pdf_file:
            payslip.pdf_file.delete(save=False)
            logger.info(
                "Deleted old PDF for %s", payslip.slip_number
            )

        # Reset status to draft so generate() flow works cleanly
        payslip.status = PayslipStatus.DRAFT
        payslip.generated_at = None
        payslip.generated_by = None
        payslip.save(
            update_fields=["status", "generated_at", "generated_by"]
        )

        return self.generate(payslip_id, user=user)

    # ── Private Methods ──────────────────────────────────────

    def _get_template(self):
        """Retrieve the active PayslipTemplate (or None for defaults)."""
        if self._template_cache is not None:
            return self._template_cache
        self._template_cache = (
            PayslipTemplate.objects.filter(is_active=True).first()
        )
        return self._template_cache

    def _build_context(self, payslip, template):
        """Build the full template rendering context."""
        employee = payslip.employee
        period = payslip.payroll_period
        ep = payslip.employee_payroll

        earnings = list(payslip.earnings.order_by("display_order"))
        deductions = list(payslip.deductions.order_by("display_order"))
        employer_contributions = list(
            payslip.employer_contributions.order_by("display_order")
        )

        total_earnings = sum(
            (e.amount for e in earnings), Decimal("0")
        )
        total_deductions = sum(
            (d.amount for d in deductions), Decimal("0")
        )
        total_employer = sum(
            (c.amount for c in employer_contributions), Decimal("0")
        )
        net_salary = total_earnings - total_deductions

        ytd_total_earnings = sum(
            (e.ytd_amount for e in earnings), Decimal("0")
        )
        ytd_total_deductions = sum(
            (d.ytd_amount for d in deductions), Decimal("0")
        )
        ytd_total_employer = sum(
            (c.ytd_amount for c in employer_contributions), Decimal("0")
        )

        # Show flags from template or defaults
        show_ytd = template.show_ytd if template else True
        show_employer = (
            template.show_employer_contributions if template else False
        )
        show_bank = template.show_bank_details if template else True
        paper_size = template.paper_size if template else "A4"
        primary_color = (
            template.primary_color if template else "#2C3E50"
        )
        secondary_color = (
            template.secondary_color if template else "#7F8C8D"
        )

        # Employee details - safe attribute access
        employee_name = str(employee) if employee else ""
        employee_code = getattr(employee, "employee_code", "") or getattr(
            employee, "employee_id", ""
        ) or ""
        department = getattr(employee, "department", "") or ""
        designation = getattr(employee, "designation", "") or ""

        # Bank details
        bank_name = ""
        bank_account = ""
        if show_bank:
            bank_name = getattr(employee, "bank_name", "") or ""
            bank_account = getattr(employee, "bank_account_number", "") or ""

        # Period details
        period_name = getattr(period, "name", str(period)) if period else ""
        period_start = (
            period.start_date.strftime("%d %b %Y") if period and hasattr(period, "start_date") else ""
        )
        period_end = (
            period.end_date.strftime("%d %b %Y") if period and hasattr(period, "end_date") else ""
        )
        pay_date = (
            period.end_date.strftime("%d %b %Y") if period and hasattr(period, "end_date") else ""
        )
        working_days = getattr(ep, "working_days", "") or ""

        return {
            "payslip": payslip,
            "template": template,
            "employee_name": employee_name,
            "employee_code": employee_code,
            "department": department,
            "designation": designation,
            "bank_name": bank_name,
            "bank_account": bank_account,
            "period_name": period_name,
            "period_start": period_start,
            "period_end": period_end,
            "pay_date": pay_date,
            "working_days": working_days,
            "earnings": earnings,
            "deductions": deductions,
            "employer_contributions": employer_contributions,
            "total_earnings": total_earnings,
            "total_deductions": total_deductions,
            "net_salary": net_salary,
            "total_employer_contributions": total_employer,
            "ytd_total_earnings": ytd_total_earnings,
            "ytd_total_deductions": ytd_total_deductions,
            "ytd_total_employer_contributions": ytd_total_employer,
            "show_ytd": show_ytd,
            "show_employer_contributions": show_employer,
            "show_bank_details": show_bank,
            "paper_size": paper_size,
            "primary_color": primary_color,
            "secondary_color": secondary_color,
            "generated_at": timezone.now().strftime("%d %b %Y %H:%M"),
        }

    def _render_html(self, context):
        """Render the payslip HTML template."""
        try:
            return render_to_string(self.TEMPLATE_NAME, context)
        except Exception as exc:
            raise PayslipGenerationError(
                f"Failed to render HTML template: {exc}"
            ) from exc

    def _html_to_pdf(self, html_content):
        """Convert HTML string to PDF bytes using WeasyPrint."""
        try:
            from weasyprint import HTML

            pdf_file = BytesIO()
            HTML(string=html_content).write_pdf(pdf_file)
            pdf_bytes = pdf_file.getvalue()
            if not pdf_bytes:
                raise PayslipGenerationError("PDF generation returned empty content.")
            return pdf_bytes
        except ImportError:
            raise PayslipGenerationError(
                "WeasyPrint is not installed. Install with: pip install weasyprint"
            )
        except PayslipGenerationError:
            raise
        except Exception as exc:
            raise PayslipGenerationError(
                f"PDF conversion failed: {exc}"
            ) from exc

    @transaction.atomic
    def _save_pdf(self, payslip, pdf_bytes, user=None):
        """Save PDF bytes to the payslip FileField and update status."""
        filename = f"{payslip.slip_number}.pdf"
        payslip.pdf_file.save(
            name=filename,
            content=ContentFile(pdf_bytes),
            save=False,
        )
        payslip.status = PayslipStatus.GENERATED
        payslip.generated_at = timezone.now()
        payslip.generated_by = user
        payslip.save(
            update_fields=[
                "pdf_file",
                "status",
                "generated_at",
                "generated_by",
            ]
        )
