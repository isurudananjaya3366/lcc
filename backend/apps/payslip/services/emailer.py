"""PayslipEmailer service for sending payslip emails to employees."""

import logging
from decimal import Decimal

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from apps.payslip.models.payslip import Payslip
from apps.payslip.models.payslip_template import PayslipTemplate

logger = logging.getLogger(__name__)


class PayslipEmailError(Exception):
    """Raised when payslip email sending fails."""


class PayslipEmailer:
    """Sends payslip PDF emails to employees.

    Renders an HTML email body, attaches the PDF file,
    and sends via Django's email backend.
    """

    EMAIL_TEMPLATE = "payslip/email_template.html"
    DEFAULT_SUBJECT = "Your Payslip for {period_name}"

    def send(self, payslip):
        """Send a payslip email to the employee.

        Args:
            payslip: Payslip instance with pdf_file attached.

        Raises:
            PayslipEmailError: If email sending fails.
        """
        if not payslip.has_pdf:
            raise PayslipEmailError(
                f"Payslip {payslip.slip_number} has no PDF attached."
            )

        employee = payslip.employee
        recipient_email = self._get_recipient_email(employee)
        if not recipient_email:
            raise PayslipEmailError(
                f"No email address for employee {employee}."
            )

        template = PayslipTemplate.objects.filter(is_active=True).first()
        context = self._build_email_context(payslip, template)
        subject = self._build_subject(payslip, template)
        html_body = render_to_string(self.EMAIL_TEMPLATE, context)

        try:
            email = EmailMessage(
                subject=subject,
                body=html_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            email.content_subtype = "html"

            # Attach PDF
            pdf_bytes = payslip.pdf_file.read()
            payslip.pdf_file.seek(0)
            email.attach(
                filename=f"{payslip.slip_number}.pdf",
                content=pdf_bytes,
                mimetype="application/pdf",
            )

            email.send(fail_silently=False)
        except Exception as exc:
            raise PayslipEmailError(
                f"Failed to send email for {payslip.slip_number}: {exc}"
            ) from exc

        # Update payslip record
        payslip.mark_sent(recipient_email)

        logger.info(
            "Payslip email sent: %s → %s",
            payslip.slip_number,
            recipient_email,
        )

    def _get_recipient_email(self, employee):
        """Get the best email address for the employee."""
        # Try employee email first, then personal, then linked user
        email = getattr(employee, "email", None) or ""
        if not email:
            email = getattr(employee, "personal_email", None) or ""
        if not email and hasattr(employee, "user") and employee.user:
            email = employee.user.email or ""
        return email.strip() if email else None

    def _build_email_context(self, payslip, template):
        """Build template context for the email body."""
        employee = payslip.employee
        period = payslip.payroll_period
        total_earnings = sum(
            (e.amount for e in payslip.earnings.all()), Decimal("0")
        )
        total_deductions = sum(
            (d.amount for d in payslip.deductions.all()), Decimal("0")
        )
        net_salary = total_earnings - total_deductions

        return {
            "employee_name": str(employee),
            "company_name": template.company_name if template else "",
            "period_name": getattr(period, "name", str(period)) if period else "",
            "slip_number": payslip.slip_number,
            "net_salary": f"{net_salary:,.2f}",
            "disclaimer": (
                template.disclaimer_text
                if template and template.show_disclaimer
                else ""
            ),
        }

    def _build_subject(self, payslip, template):
        """Build the email subject line."""
        period = payslip.payroll_period
        period_name = getattr(period, "name", str(period)) if period else ""
        return self.DEFAULT_SUBJECT.format(period_name=period_name)
