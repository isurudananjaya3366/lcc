"""
Base importer interface for bank statement parsers.
"""

import abc
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class ParsedLine:
    """A single parsed transaction line from a bank statement."""

    line_number: int
    transaction_date: str  # ISO format YYYY-MM-DD
    description: str
    debit_amount: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")
    running_balance: Decimal | None = None
    reference: str | None = None
    value_date: str | None = None


@dataclass
class ParseResult:
    """Result of parsing a bank statement file."""

    success: bool
    lines: list[ParsedLine] = field(default_factory=list)
    opening_balance: Decimal = Decimal("0")
    closing_balance: Decimal = Decimal("0")
    start_date: str | None = None
    end_date: str | None = None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def line_count(self):
        return len(self.lines)


class BaseImporter(abc.ABC):
    """Abstract base class for statement importers."""

    @abc.abstractmethod
    def parse(self, file_content: str, **kwargs) -> ParseResult:
        """Parse file content and return structured result."""

    @abc.abstractmethod
    def detect_format(self, file_content: str) -> bool:
        """Return True if this importer can handle the given content."""
