"""
PDF receipt generator service.

Tasks 53-59: PDF template rendering, tenant branding, PDF generation,
metadata, A4 invoice style, thermal style, and PDF storage.
"""

import hashlib
import logging
import os
from datetime import datetime
from io import BytesIO

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)

# Template paths (relative to templates/)
_TEMPLATES = {
    "default": "receipts/pdf/base_receipt.html",
    "a4_invoice": "receipts/pdf/a4_invoice.html",
    "thermal": "receipts/pdf/thermal_style.html",
}


class PDFGeneratorService:
    """
    Generates PDF receipts from receipt_data JSON.

    Supports multiple layout styles (thermal, A4 invoice) and
    tenant branding (logo, colours, fonts).

    Uses Django template rendering → HTML → (optional) WeasyPrint.
    Falls back to raw HTML when WeasyPrint is not installed.
    """

    def __init__(self, receipt=None, receipt_data: dict | None = None,
                 style: str = "default"):
        self.receipt = receipt
        self.data = receipt_data or (receipt.receipt_data if receipt else {})
        self.style = style if style in _TEMPLATES else "default"

    # ── Public API ────────────────────────────────────────

    def generate_pdf(self) -> bytes:
        """Render receipt data to PDF bytes with metadata."""
        html = self._render_html()
        metadata = self.get_metadata()
        return self._html_to_pdf(html, metadata=metadata)

    def generate_html(self) -> str:
        """Render receipt data to HTML string (for preview)."""
        return self._render_html()

    def save_pdf(self, receipt) -> str | None:
        """
        Generate PDF and save to media storage.

        Returns:
            Relative file path or None on failure.
        """
        try:
            pdf_bytes = self.generate_pdf()
            path = self._build_storage_path(receipt)
            full_path = os.path.join(settings.MEDIA_ROOT, path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(pdf_bytes)

            logger.info("Saved PDF: %s (%d bytes)", path, len(pdf_bytes))
            return path
        except Exception:
            logger.exception("Failed to save PDF for receipt %s",
                             getattr(receipt, "receipt_number", "?"))
            return None

    # ── HTML rendering ────────────────────────────────────

    def _render_html(self) -> str:
        template_name = _TEMPLATES[self.style]
        context = self._build_context()
        return render_to_string(template_name, context)

    def _build_context(self) -> dict:
        """Build template context from receipt_data + optional branding."""
        ctx = {
            "receipt_number": self.data.get("transaction", {}).get(
                "receipt_number", ""
            ),
            "header": self.data.get("header", {}),
            "transaction": self.data.get("transaction", {}),
            "items": self.data.get("items", []),
            "totals": self.data.get("totals", {}),
            "payments": self.data.get("payments", {}),
            "footer": self.data.get("footer", {}),
            "qr_code": self.data.get("qr_code", {}),
            "is_duplicate": self.data.get("is_duplicate", False),
            "watermark": self.data.get("header", {}).get("duplicate_text"),
        }

        branding = self._get_branding()
        ctx.update(branding)

        # Receipt-level watermark
        if self.receipt and hasattr(self.receipt, "get_watermark_text"):
            wm = self.receipt.get_watermark_text()
            if wm:
                ctx["watermark"] = wm

        return ctx

    def _get_branding(self) -> dict:
        """Extract tenant branding from connection schema or fallback."""
        branding = {
            "primary_color": "#2c3e50",
            "secondary_color": "#34495e",
            "accent_color": "#3498db",
            "font_family": "Arial, Helvetica, sans-serif",
            "logo_url": None,
        }
        try:
            from django.db import connection

            tenant = getattr(connection, "tenant", None)
            if tenant:
                branding["primary_color"] = getattr(
                    tenant, "primary_color", branding["primary_color"]
                ) or branding["primary_color"]
                branding["logo_url"] = getattr(tenant, "logo_url", None)
                branding["font_family"] = getattr(
                    tenant, "font_family", branding["font_family"]
                ) or branding["font_family"]
        except Exception:
            pass
        return branding

    # ── PDF conversion ────────────────────────────────────

    @staticmethod
    def _html_to_pdf(html: str, metadata: dict | None = None) -> bytes:
        """
        Convert HTML to PDF bytes.

        Tries WeasyPrint first; falls back to returning HTML bytes
        when the library is unavailable (CI / Docker slim images).
        """
        try:
            from weasyprint import HTML  # type: ignore[import-untyped]
            buf = BytesIO()
            doc = HTML(string=html).render()
            if metadata:
                doc.metadata.title = metadata.get("title", "")
                doc.metadata.authors = (
                    [metadata["author"]] if metadata.get("author") else []
                )
                doc.metadata.description = metadata.get("subject", "")
                doc.metadata.keywords = metadata.get("keywords", "")
                doc.metadata.generator = metadata.get("creator", "")
                doc.metadata.created = metadata.get("created")
            doc.write_pdf(buf)
            return buf.getvalue()
        except ImportError:
            logger.warning(
                "WeasyPrint not installed — returning HTML instead of PDF"
            )
            return html.encode("utf-8")

    # ── Task 56: PDF metadata ─────────────────────────────

    def get_metadata(self) -> dict:
        biz = self.data.get("header", {}).get("business_name", "Business")
        receipt_num = self.data.get("transaction", {}).get("receipt_number", "")
        return {
            "title": f"Receipt {receipt_num}",
            "author": biz,
            "subject": "Sales Receipt",
            "creator": "LankaCommerce Cloud",
            "producer": "LCC Receipt Generator",
            "keywords": f"receipt,{receipt_num},{biz}",
            "created": timezone.now().isoformat(),
        }

    # ── Task 55: QR code generation + currency helper ────

    @staticmethod
    def generate_qr_code(data: str, size: int = 200) -> str | None:
        """Generate QR code as base64-encoded PNG for embedding in PDF."""
        try:
            import qrcode  # type: ignore[import-untyped]
            import base64

            qr = qrcode.make(data, box_size=size // 30, border=2)
            buf = BytesIO()
            qr.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode()
        except ImportError:
            logger.debug("qrcode library not installed — skipping QR")
            return None

    @staticmethod
    def format_currency(amount, symbol: str = "Rs.") -> str:
        """Format a numeric amount as currency string."""
        from decimal import Decimal

        d = Decimal(str(amount))
        return f"{symbol} {d:,.2f}"

    # ── Task 59: Storage path ─────────────────────────────

    @staticmethod
    def _build_storage_path(receipt) -> str:
        """Build media-relative path for storing a PDF."""
        from django.utils import timezone

        now = timezone.now()
        receipt_num = getattr(receipt, "receipt_number", "unknown")
        return os.path.join(
            "receipts",
            str(now.year),
            f"{now.month:02d}",
            f"{receipt_num}.pdf",
        )

    @staticmethod
    def get_cache_key(receipt_id: str, version: int = 1) -> str:
        raw = f"receipt_pdf:{receipt_id}:v{version}"
        return hashlib.md5(raw.encode()).hexdigest()
