"""
Reconciliation report service.

Generates structured reconciliation reports with matched items,
unmatched items, adjustments, summary totals, and optional PDF export.
"""

import logging
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from apps.accounting.models.enums import (
    JournalEntryStatus,
    MatchStatus,
    MatchType,
    ReconciliationStatus,
)

logger = logging.getLogger(__name__)


class ReconciliationReportService:
    """
    Generates comprehensive reconciliation reports.

    Usage::

        svc = ReconciliationReportService(reconciliation)
        report = svc.generate_report()
        pdf_bytes = svc.export_to_pdf(return_bytes=True)
    """

    def __init__(self, reconciliation):
        self.reconciliation = reconciliation

    # ── Main report ────────────────────────────────────────────────

    def generate_report(self):
        """Generate the complete reconciliation report as a dict."""
        return {
            "header": self._get_report_header(),
            "summary": self.calculate_summary_totals(),
            "matched_items": self.get_matched_items(),
            "unmatched_items": self.get_unmatched_items(),
            "adjustments": self.get_adjustments(),
        }

    # ── Header ─────────────────────────────────────────────────────

    def _get_report_header(self):
        recon = self.reconciliation
        ba = recon.bank_account
        return {
            "account_name": ba.account_name,
            "account_number": ba.account_number,
            "bank_name": ba.bank_name,
            "period_start": recon.start_date.isoformat(),
            "period_end": recon.end_date.isoformat(),
            "period_description": recon.period_description,
            "status": recon.get_status_display(),
            "reconciled_by": (
                str(recon.completed_by) if recon.completed_by else None
            ),
            "completed_at": (
                recon.completed_at.isoformat() if recon.completed_at else None
            ),
            "report_generated": timezone.now().isoformat(),
        }

    # ── Matched items ──────────────────────────────────────────────

    def get_matched_items(self):
        from apps.accounting.models.reconciliation_item import ReconciliationItem

        items_qs = ReconciliationItem.objects.filter(
            reconciliation=self.reconciliation,
        ).select_related("statement_line", "journal_entry").order_by("matched_at")

        items = []
        total_amount = Decimal("0.00")
        auto_count = 0
        manual_count = 0

        for item in items_qs:
            line = item.statement_line
            entry = item.journal_entry
            amount = line.credit_amount - line.debit_amount
            total_amount += amount

            if item.match_type == MatchType.AUTO:
                auto_count += 1
            else:
                manual_count += 1

            items.append({
                "match_id": str(item.pk),
                "date": line.transaction_date.isoformat(),
                "statement_description": line.description or "",
                "statement_amount": float(amount),
                "statement_reference": line.reference or "",
                "journal_reference": entry.reference or "",
                "journal_description": entry.description or "",
                "match_type": item.get_match_type_display(),
                "matched_at": item.matched_at.isoformat() if item.matched_at else None,
                "matched_by": str(item.matched_by) if item.matched_by else None,
                "notes": item.notes,
            })

        return {
            "total_count": len(items),
            "total_amount": float(total_amount),
            "auto_count": auto_count,
            "manual_count": manual_count,
            "items": items,
        }

    # ── Unmatched items ────────────────────────────────────────────

    def get_unmatched_items(self):
        return {
            "book_items": self._get_unmatched_book_items(),
            "statement_items": self._get_unmatched_statement_items(),
        }

    def _get_unmatched_book_items(self):
        from apps.accounting.models.journal_entry import JournalEntry

        recon = self.reconciliation
        gl_account = recon.bank_account.gl_account

        entries = (
            JournalEntry.objects.filter(
                entry_status=JournalEntryStatus.POSTED,
                lines__account=gl_account,
                entry_date__range=[recon.start_date, recon.end_date],
            )
            .distinct()
            .exclude(reconciliation_items__reconciliation=recon)
            .order_by("entry_date")
        )

        today = date.today()
        items = []
        total = Decimal("0.00")

        for entry in entries:
            amount = entry.total_debit - entry.total_credit
            total += amount
            age_days = (today - entry.entry_date).days

            items.append({
                "date": entry.entry_date.isoformat(),
                "reference": entry.reference or "",
                "description": entry.description or "",
                "amount": float(amount),
                "age_days": age_days,
                "age_category": self._age_category(age_days),
            })

        return {
            "count": len(items),
            "total_amount": float(total),
            "items": items,
        }

    def _get_unmatched_statement_items(self):
        from apps.accounting.models.statement_line import StatementLine

        recon = self.reconciliation
        qs = StatementLine.objects.filter(
            statement__bank_account=recon.bank_account,
            match_status=MatchStatus.UNMATCHED,
        )
        if recon.bank_statement_id:
            qs = qs.filter(statement_id=recon.bank_statement_id)

        items = []
        total = Decimal("0.00")

        for line in qs.order_by("transaction_date"):
            amount = line.credit_amount - line.debit_amount
            total += amount
            items.append({
                "date": line.transaction_date.isoformat(),
                "reference": line.reference or "",
                "description": line.description or "",
                "amount": float(amount),
            })

        return {
            "count": len(items),
            "total_amount": float(total),
            "items": items,
        }

    @staticmethod
    def _age_category(days):
        if days <= 30:
            return "current"
        if days <= 60:
            return "30_plus"
        if days <= 90:
            return "60_plus"
        return "90_plus"

    # ── Adjustments ────────────────────────────────────────────────

    def get_adjustments(self):
        from apps.accounting.models.reconciliation_adjustment import (
            ReconciliationAdjustment,
        )

        adj_qs = ReconciliationAdjustment.objects.filter(
            reconciliation=self.reconciliation,
        ).select_related("journal_entry").order_by("created_at")

        items = []
        net = Decimal("0.00")
        for adj in adj_qs:
            signed = (
                adj.adjustment_amount
                if adj.adjustment_type == "DEBIT"
                else -adj.adjustment_amount
            )
            net += signed
            items.append({
                "date": adj.created_at.isoformat(),
                "type": adj.adjustment_type,
                "amount": float(adj.adjustment_amount),
                "reason": adj.adjustment_reason,
                "journal_entry": (
                    str(adj.journal_entry.entry_number)
                    if adj.journal_entry
                    else None
                ),
                "created_by": str(adj.created_by) if adj.created_by else None,
            })

        return {
            "total_count": len(items),
            "net_adjustment": float(net),
            "items": items,
        }

    # ── Summary totals ─────────────────────────────────────────────

    def calculate_summary_totals(self):
        recon = self.reconciliation
        matched = self.get_matched_items()
        unmatched = self.get_unmatched_items()
        adjustments = self.get_adjustments()

        return {
            "balances": {
                "statement_balance": float(recon.statement_balance),
                "book_balance": float(recon.book_balance),
                "difference": float(recon.difference),
            },
            "reconciliation": {
                "matched_items_count": matched["total_count"],
                "matched_items_amount": matched["total_amount"],
                "unmatched_book_count": unmatched["book_items"]["count"],
                "unmatched_book_amount": unmatched["book_items"]["total_amount"],
                "unmatched_statement_count": unmatched["statement_items"]["count"],
                "unmatched_statement_amount": unmatched["statement_items"]["total_amount"],
                "adjustments_count": adjustments["total_count"],
                "adjustments_net": adjustments["net_adjustment"],
            },
            "status": {
                "is_reconciled": recon.status == ReconciliationStatus.COMPLETED,
                "variance_resolved": recon.difference == Decimal("0.00"),
            },
        }

    # ── PDF export ─────────────────────────────────────────────────

    def export_to_pdf(self, return_bytes=False, output_path=None):
        """
        Export reconciliation report to PDF.

        Requires ``weasyprint`` to be installed.
        """
        from django.template.loader import render_to_string

        report_data = self.generate_report()
        html_string = render_to_string(
            "accounting/reconciliation_report.html",
            {"report": report_data},
        )

        try:
            from weasyprint import CSS, HTML
        except ImportError:
            raise ImportError(
                "weasyprint is required for PDF export. "
                "Install it with: pip install weasyprint"
            )

        css = CSS(string=self._get_pdf_css())
        pdf_bytes = HTML(string=html_string).write_pdf(stylesheets=[css])

        if return_bytes:
            return pdf_bytes

        if not output_path:
            ba = self.reconciliation.bank_account
            period = self.reconciliation.end_date.strftime("%b%Y")
            output_path = f"Reconciliation_Report_{ba.account_name}_{period}.pdf"

        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        return output_path

    @staticmethod
    def _get_pdf_css():
        return """
            @page { size: A4; margin: 2cm 1.5cm; }
            body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; }
            h1 { font-size: 16pt; margin-bottom: 4pt; }
            h2 { font-size: 13pt; border-bottom: 1px solid #ccc; padding-bottom: 4pt; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 12pt; }
            th, td { border: 1px solid #ddd; padding: 4pt 6pt; text-align: left; }
            th { background-color: #f5f5f5; font-weight: bold; }
            tr:nth-child(even) { background-color: #fafafa; }
            .amount { text-align: right; font-family: monospace; }
            .status-completed { color: #2e7d32; }
            .status-cancelled { color: #c62828; }
        """
