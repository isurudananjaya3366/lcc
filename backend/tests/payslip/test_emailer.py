"""Tests for PayslipEmailer service — Task 87."""

import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile

from apps.payslip.constants import PayslipStatus

pytestmark = pytest.mark.django_db


class TestPayslipEmailer:
    """Tests for email distribution service."""

    @pytest.fixture
    def payslip_with_pdf(self, payslip_with_lines):
        """Payslip with a fake PDF attached and GENERATED status."""
        payslip = payslip_with_lines
        payslip.pdf_file.save(
            f"{payslip.slip_number}.pdf",
            ContentFile(b"%PDF-1.4 test content"),
            save=False,
        )
        payslip.status = PayslipStatus.GENERATED
        payslip.save(update_fields=["pdf_file", "status"])
        return payslip

    def test_send_no_pdf_raises(self, payslip_with_lines):
        """send() raises error when no PDF attached."""
        from apps.payslip.services.emailer import PayslipEmailer, PayslipEmailError

        emailer = PayslipEmailer()
        with pytest.raises(PayslipEmailError, match="no PDF"):
            emailer.send(payslip_with_lines)

    @patch("apps.payslip.services.emailer.EmailMessage")
    def test_send_success(self, MockEmail, payslip_with_pdf, payslip_template):
        """send() sends email and marks payslip as SENT."""
        from apps.payslip.services.emailer import PayslipEmailer

        mock_instance = MockEmail.return_value
        mock_instance.send.return_value = 1

        emailer = PayslipEmailer()
        emailer.send(payslip_with_pdf)

        payslip_with_pdf.refresh_from_db()
        assert payslip_with_pdf.email_sent is True
        assert payslip_with_pdf.status == PayslipStatus.SENT
        assert payslip_with_pdf.sent_to == "kamal@example.com"
        mock_instance.send.assert_called_once()

    @patch("apps.payslip.services.emailer.EmailMessage")
    def test_send_attaches_pdf(self, MockEmail, payslip_with_pdf, payslip_template):
        """send() attaches PDF to the email."""
        from apps.payslip.services.emailer import PayslipEmailer

        mock_instance = MockEmail.return_value
        mock_instance.send.return_value = 1

        emailer = PayslipEmailer()
        emailer.send(payslip_with_pdf)

        mock_instance.attach.assert_called_once()
        call_args = mock_instance.attach.call_args
        assert call_args[1]["filename"].endswith(".pdf")
        assert call_args[1]["mimetype"] == "application/pdf"

    @patch("apps.payslip.services.emailer.EmailMessage")
    def test_send_failure_raises(self, MockEmail, payslip_with_pdf, payslip_template):
        """send() raises PayslipEmailError on send failure."""
        from apps.payslip.services.emailer import PayslipEmailer, PayslipEmailError

        mock_instance = MockEmail.return_value
        mock_instance.send.side_effect = Exception("SMTP error")

        emailer = PayslipEmailer()
        with pytest.raises(PayslipEmailError, match="SMTP error"):
            emailer.send(payslip_with_pdf)

    def test_build_email_context(self, payslip_with_pdf, payslip_template):
        """_build_email_context returns expected keys."""
        from apps.payslip.services.emailer import PayslipEmailer

        emailer = PayslipEmailer()
        ctx = emailer._build_email_context(payslip_with_pdf, payslip_template)

        assert "employee_name" in ctx
        assert "company_name" in ctx
        assert "slip_number" in ctx
        assert "net_salary" in ctx
        assert ctx["company_name"] == "Test Company (Pvt) Ltd"

    def test_build_subject(self, payslip_with_pdf, payslip_template):
        """_build_subject includes period name."""
        from apps.payslip.services.emailer import PayslipEmailer

        emailer = PayslipEmailer()
        subject = emailer._build_subject(payslip_with_pdf, payslip_template)

        assert "January 2026" in subject

    def test_get_recipient_email_from_employee(self, payslip_with_pdf):
        """_get_recipient_email gets employee.email first."""
        from apps.payslip.services.emailer import PayslipEmailer

        emailer = PayslipEmailer()
        email = emailer._get_recipient_email(payslip_with_pdf.employee)
        assert email == "kamal@example.com"

    def test_no_recipient_email_raises(self, tenant_context, payslip_with_lines, payslip_template):
        """send() raises when employee has no email."""
        from apps.payslip.services.emailer import PayslipEmailer, PayslipEmailError
        from django.core.files.base import ContentFile

        payslip = payslip_with_lines
        # Remove email from employee
        emp = payslip.employee
        emp.email = ""
        emp.save(update_fields=["email"])

        # Add PDF
        payslip.pdf_file.save(
            f"{payslip.slip_number}.pdf",
            ContentFile(b"%PDF-1.4 test"),
            save=False,
        )
        payslip.status = PayslipStatus.GENERATED
        payslip.save(update_fields=["pdf_file", "status"])

        emailer = PayslipEmailer()
        # The employee's linked user still has an email, so it falls through
        # Let's also remove user link
        emp.user = None
        emp.save(update_fields=["user"])

        with pytest.raises(PayslipEmailError, match="No email"):
            emailer.send(payslip)
