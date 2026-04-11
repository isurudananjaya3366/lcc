"""
CSV bank statement importer.

Parses CSV-format bank statements with configurable column mapping,
auto-detection of delimiters and date formats, and support for
Sri Lankan bank CSV formats (BOC, Commercial Bank, Sampath).
"""

import csv
import io
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from apps.accounting.services.importers.base import (
    BaseImporter,
    ParsedLine,
    ParseResult,
)

# Default column mappings (0-indexed)
DEFAULT_COLUMN_MAP = {
    "date": 0,
    "description": 1,
    "debit": 2,
    "credit": 3,
    "balance": 4,
    "reference": None,
    "value_date": None,
}

# Common date format patterns to try
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%m/%d/%Y",
    "%d %b %Y",
    "%d-%b-%Y",
    "%d-%b-%y",
    "%Y/%m/%d",
]


class CSVImporter(BaseImporter):
    """
    CSV bank statement parser.

    Supports flexible column mapping, multiple date formats,
    and various amount formatting conventions.
    """

    def __init__(self, column_map=None, date_format=None, skip_rows=0, delimiter=None):
        self.column_map = column_map or DEFAULT_COLUMN_MAP.copy()
        self.date_format = date_format
        self.skip_rows = skip_rows
        self.delimiter = delimiter

    def detect_format(self, file_content: str) -> bool:
        """Check if content looks like CSV."""
        try:
            dialect = csv.Sniffer().sniff(file_content[:2048])
            return dialect is not None
        except csv.Error:
            return "," in file_content or "\t" in file_content

    def parse(self, file_content: str, **kwargs) -> ParseResult:
        """Parse CSV content into structured statement data."""
        column_map = kwargs.get("column_map", self.column_map)
        date_format = kwargs.get("date_format", self.date_format)
        skip_rows = kwargs.get("skip_rows", self.skip_rows)
        delimiter = kwargs.get("delimiter", self.delimiter)

        try:
            if not delimiter:
                delimiter = self._detect_delimiter(file_content)

            reader = csv.reader(io.StringIO(file_content), delimiter=delimiter)
            rows = list(reader)

            # Skip header rows
            data_rows = rows[skip_rows:]
            if not data_rows:
                return ParseResult(success=False, error="No data rows found.")

            # Auto-detect date format if not specified
            if not date_format:
                date_format = self._detect_date_format(data_rows, column_map)

            lines = []
            warnings = []
            line_number = 0

            for row_idx, row in enumerate(data_rows):
                if not row or all(cell.strip() == "" for cell in row):
                    continue

                line_number += 1
                try:
                    parsed = self._parse_row(
                        row, line_number, column_map, date_format
                    )
                    if parsed:
                        lines.append(parsed)
                except (ValueError, IndexError) as exc:
                    warnings.append(
                        f"Row {row_idx + skip_rows + 1}: {exc}"
                    )

            if not lines:
                return ParseResult(
                    success=False,
                    error="No valid transaction lines parsed.",
                    warnings=warnings,
                )

            # Determine date range
            dates = [l.transaction_date for l in lines]
            start_date = min(dates)
            end_date = max(dates)

            # Determine balances
            opening_balance = Decimal("0")
            closing_balance = Decimal("0")
            if lines[0].running_balance is not None:
                # Opening = first balance - first transaction net
                first = lines[0]
                net = first.credit_amount - first.debit_amount
                opening_balance = first.running_balance - net
            if lines[-1].running_balance is not None:
                closing_balance = lines[-1].running_balance

            return ParseResult(
                success=True,
                lines=lines,
                opening_balance=opening_balance,
                closing_balance=closing_balance,
                start_date=start_date,
                end_date=end_date,
                warnings=warnings,
                metadata={"delimiter": delimiter, "date_format": date_format},
            )

        except Exception as exc:
            return ParseResult(success=False, error=str(exc))

    def _detect_delimiter(self, content: str) -> str:
        """Auto-detect CSV delimiter."""
        try:
            dialect = csv.Sniffer().sniff(content[:4096])
            return dialect.delimiter
        except csv.Error:
            # Count occurrences on first data line
            first_line = content.split("\n")[0]
            counts = {
                ",": first_line.count(","),
                "\t": first_line.count("\t"),
                ";": first_line.count(";"),
                "|": first_line.count("|"),
            }
            return max(counts, key=counts.get)

    def _detect_date_format(self, rows, column_map):
        """Try to detect date format from first few data rows."""
        date_col = column_map.get("date", 0)
        for row in rows[:5]:
            if len(row) <= date_col:
                continue
            date_str = row[date_col].strip()
            if not date_str:
                continue
            for fmt in DATE_FORMATS:
                try:
                    datetime.strptime(date_str, fmt)
                    return fmt
                except ValueError:
                    continue
        return "%d/%m/%Y"  # Default for Sri Lankan banks

    def _parse_row(self, row, line_number, column_map, date_format):
        """Parse a single CSV row into a ParsedLine."""
        date_col = column_map.get("date", 0)
        desc_col = column_map.get("description", 1)
        debit_col = column_map.get("debit", 2)
        credit_col = column_map.get("credit", 3)
        balance_col = column_map.get("balance")
        ref_col = column_map.get("reference")
        value_date_col = column_map.get("value_date")

        # Parse date
        date_str = row[date_col].strip()
        if not date_str:
            return None
        transaction_date = datetime.strptime(date_str, date_format).strftime(
            "%Y-%m-%d"
        )

        # Parse description
        description = row[desc_col].strip() if len(row) > desc_col else ""

        # Parse amounts
        debit = self._parse_amount(
            row[debit_col] if len(row) > debit_col else ""
        )
        credit = self._parse_amount(
            row[credit_col] if len(row) > credit_col else ""
        )

        # Parse balance
        running_balance = None
        if balance_col is not None and len(row) > balance_col:
            running_balance = self._parse_amount(row[balance_col])

        # Parse reference
        reference = None
        if ref_col is not None and len(row) > ref_col:
            reference = row[ref_col].strip() or None

        # Parse value date
        value_date = None
        if value_date_col is not None and len(row) > value_date_col:
            vd_str = row[value_date_col].strip()
            if vd_str:
                try:
                    value_date = datetime.strptime(vd_str, date_format).strftime(
                        "%Y-%m-%d"
                    )
                except ValueError:
                    pass

        return ParsedLine(
            line_number=line_number,
            transaction_date=transaction_date,
            description=description,
            debit_amount=debit,
            credit_amount=credit,
            running_balance=running_balance,
            reference=reference,
            value_date=value_date,
        )

    @staticmethod
    def _parse_amount(value: str) -> Decimal:
        """Parse amount string handling various formats."""
        if not value:
            return Decimal("0")

        cleaned = value.strip()
        if not cleaned or cleaned == "-":
            return Decimal("0")

        # Remove currency symbols and whitespace
        cleaned = re.sub(r"[A-Za-z$€£¥₹\s]", "", cleaned)

        # Handle parentheses as negative (accounting format)
        is_negative = False
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = cleaned[1:-1]
            is_negative = True
        elif cleaned.startswith("-"):
            cleaned = cleaned[1:]
            is_negative = True

        # Handle thousand separators
        # If last separator is comma and has 2 digits after: European format
        if re.match(r"^[\d.]+,\d{2}$", cleaned):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")

        try:
            amount = Decimal(cleaned)
            return -amount if is_negative else amount
        except InvalidOperation:
            return Decimal("0")
