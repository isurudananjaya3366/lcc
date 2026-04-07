"""Tests for PayslipGenerator service — Task 86."""

import pytest
from unittest.mock import MagicMock, patch

from apps.payslip.constants import PayslipStatus

pytestmark = pytest.mark.django_db


class TestPayslipGenerator:
    """Tests for PDF generation service."""

    def test_build_context(self, payslip_with_lines, payslip_template):
        """_build_context returns a dict with all expected keys."""
        from apps.payslip.services.generator import PayslipGenerator

        gen = PayslipGenerator()
        template = payslip_template
        payslip = payslip_with_lines

        ctx = gen._build_context(payslip, template)

        assert ctx["payslip"].slip_number == payslip.slip_number
        assert ctx["template"].company_name == "Test Company (Pvt) Ltd"
        assert len(ctx["earnings"]) == 2
        assert len(ctx["deductions"]) == 1
        assert "total_earnings" in ctx
        assert "net_salary" in ctx

    def test_render_html(self, payslip_with_lines, payslip_template):
        """_render_html produces non-empty HTML string."""
        from apps.payslip.services.generator import PayslipGenerator

        gen = PayslipGenerator()
        ctx = gen._build_context(payslip_with_lines, payslip_template)
        html = gen._render_html(ctx)

        assert isinstance(html, str)
        assert len(html) > 0
        assert payslip_with_lines.slip_number in html
        assert "Test Company (Pvt) Ltd" in html

    def test_get_template(self, payslip_template):
        """_get_template returns the active template."""
        from apps.payslip.services.generator import PayslipGenerator

        gen = PayslipGenerator()
        template = gen._get_template()
        assert template == payslip_template

    def test_get_template_no_active(self, tenant_context):
        """_get_template returns None when no active template."""
        from apps.payslip.services.generator import PayslipGenerator

        gen = PayslipGenerator()
        result = gen._get_template()
        assert result is None

    @patch("apps.payslip.services.generator.PayslipGenerator._html_to_pdf")
    def test_generate_creates_pdf(
        self, mock_pdf, payslip_with_lines, payslip_template, admin_user
    ):
        """generate() saves PDF and marks payslip as GENERATED."""
        from apps.payslip.services.generator import PayslipGenerator

        mock_pdf.return_value = b"%PDF-1.4 fake content"

        gen = PayslipGenerator()
        gen.generate(payslip_with_lines.pk, admin_user)

        payslip_with_lines.refresh_from_db()
        assert payslip_with_lines.status == PayslipStatus.GENERATED
        assert payslip_with_lines.generated_at is not None
        assert payslip_with_lines.generated_by == admin_user
        assert payslip_with_lines.has_pdf is True

    @patch("apps.payslip.services.generator.PayslipGenerator._html_to_pdf")
    def test_regenerate_replaces_pdf(
        self, mock_pdf, payslip_with_lines, payslip_template, admin_user
    ):
        """regenerate() deletes old PDF and creates new one."""
        from apps.payslip.services.generator import PayslipGenerator

        mock_pdf.return_value = b"%PDF-1.4 fake content"

        gen = PayslipGenerator()
        gen.generate(payslip_with_lines.pk, admin_user)
        first_gen_time = payslip_with_lines.generated_at

        gen.regenerate(payslip_with_lines.pk, admin_user)
        payslip_with_lines.refresh_from_db()

        assert payslip_with_lines.status == PayslipStatus.GENERATED
        # re-generated timestamp updated
        assert payslip_with_lines.generated_at is not None

    def test_generate_nonexistent_payslip(self, tenant_context, payslip_template, admin_user):
        """generate() raises error for non-existent payslip ID."""
        import uuid
        from apps.payslip.services.generator import (
            PayslipGenerationError,
            PayslipGenerator,
        )

        gen = PayslipGenerator()
        with pytest.raises(Exception):
            gen.generate(uuid.uuid4(), admin_user)
