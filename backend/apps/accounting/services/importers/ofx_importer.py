"""
OFX bank statement importer.

Provides basic OFX format parsing. Full OFX support requires
the ofxparse library; this implementation handles simple cases.
"""

from decimal import Decimal

from apps.accounting.services.importers.base import (
    BaseImporter,
    ParsedLine,
    ParseResult,
)


class OFXImporter(BaseImporter):
    """
    OFX (Open Financial Exchange) statement parser.

    Handles OFX/QFX format bank statements. For full production
    use, install the `ofxparse` library.
    """

    def detect_format(self, file_content: str) -> bool:
        """Check if content is OFX format."""
        return "<OFX>" in file_content.upper() or "OFXHEADER" in file_content.upper()

    def parse(self, file_content: str, **kwargs) -> ParseResult:
        """Parse OFX content. Requires ofxparse library for full support."""
        try:
            import ofxparse
        except ImportError:
            return ParseResult(
                success=False,
                error=(
                    "OFX parsing requires the 'ofxparse' library. "
                    "Install it with: pip install ofxparse"
                ),
            )

        try:
            import io

            ofx = ofxparse.OfxParser.parse(io.BytesIO(file_content.encode()))
            account = ofx.account
            statement = account.statement

            lines = []
            for idx, txn in enumerate(statement.transactions, 1):
                amount = Decimal(str(txn.amount))
                lines.append(
                    ParsedLine(
                        line_number=idx,
                        transaction_date=txn.date.strftime("%Y-%m-%d"),
                        description=txn.memo or txn.payee or "",
                        debit_amount=abs(amount) if amount < 0 else Decimal("0"),
                        credit_amount=amount if amount > 0 else Decimal("0"),
                        reference=txn.id or None,
                    )
                )

            dates = [l.transaction_date for l in lines] if lines else []
            return ParseResult(
                success=True,
                lines=lines,
                opening_balance=Decimal(str(statement.balance)) if hasattr(statement, "balance") else Decimal("0"),
                closing_balance=Decimal(str(statement.balance)) if hasattr(statement, "balance") else Decimal("0"),
                start_date=min(dates) if dates else None,
                end_date=max(dates) if dates else None,
            )
        except Exception as exc:
            return ParseResult(success=False, error=f"OFX parse error: {exc}")
