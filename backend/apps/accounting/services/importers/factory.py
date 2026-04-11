"""
Statement parser factory.

Provides format detection and parser selection for bank
statement imports.
"""

from apps.accounting.models.enums import StatementFormat
from apps.accounting.services.importers.base import BaseImporter
from apps.accounting.services.importers.csv_importer import CSVImporter
from apps.accounting.services.importers.ofx_importer import OFXImporter


class StatementParserFactory:
    """Factory for creating format-specific statement parsers."""

    _parsers = {
        StatementFormat.CSV: CSVImporter,
        StatementFormat.OFX: OFXImporter,
    }

    @classmethod
    def get_parser(cls, statement_format: str, **kwargs) -> BaseImporter:
        """Get a parser instance for the specified format."""
        parser_class = cls._parsers.get(statement_format)
        if not parser_class:
            raise ValueError(f"Unsupported statement format: {statement_format}")
        return parser_class(**kwargs)

    @classmethod
    def detect_and_parse(cls, file_content: str, **kwargs):
        """Auto-detect format and parse the statement."""
        for fmt, parser_class in cls._parsers.items():
            parser = parser_class()
            if parser.detect_format(file_content):
                return parser.parse(file_content, **kwargs)
        raise ValueError("Unable to detect statement format.")
