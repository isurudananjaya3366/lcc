"""
Customer CSV Export Service.

Generates CSV output from customer querysets with configurable
column selection and filtering.
"""

import csv
import io
import logging
from typing import Optional

from django.db.models import QuerySet

logger = logging.getLogger(__name__)

# ── Default export columns ──────────────────────────────────────────
DEFAULT_EXPORT_COLUMNS: list[tuple[str, str]] = [
    ("customer_code", "Customer Code"),
    ("first_name", "First Name"),
    ("last_name", "Last Name"),
    ("display_name", "Display Name"),
    ("business_name", "Business Name"),
    ("email", "Email"),
    ("phone", "Phone"),
    ("mobile", "Mobile"),
    ("customer_type", "Customer Type"),
    ("status", "Status"),
    ("total_purchases", "Total Purchases"),
    ("outstanding_balance", "Outstanding Balance"),
    ("created_on", "Created Date"),
]

OPTIONAL_COLUMNS: list[tuple[str, str]] = [
    ("billing_address_line_1", "Address"),
    ("billing_city", "City"),
    ("billing_state_province", "Province"),
    ("billing_postal_code", "Postal Code"),
    ("tax_id", "Tax ID"),
    ("vat_number", "VAT Number"),
    ("credit_limit", "Credit Limit"),
    ("order_count", "Order Count"),
    ("last_purchase_date", "Last Purchase Date"),
    ("notes", "Notes"),
]


class CustomerExportService:
    """Export customers to CSV format."""

    @classmethod
    def export_to_csv(
        cls,
        queryset: QuerySet,
        *,
        columns: Optional[list[str]] = None,
        include_headers: bool = True,
    ) -> str:
        """
        Export queryset to a CSV string.

        Args:
            queryset: Customer queryset (may be pre-filtered).
            columns: List of field names to include. Uses defaults if None.
            include_headers: Whether to include header row.

        Returns:
            CSV content as a string.
        """
        col_map = dict(DEFAULT_EXPORT_COLUMNS + OPTIONAL_COLUMNS)

        if columns:
            selected = [(c, col_map.get(c, c)) for c in columns if c in col_map]
        else:
            selected = list(DEFAULT_EXPORT_COLUMNS)

        field_names = [c[0] for c in selected]
        header_names = [c[1] for c in selected]

        output = io.StringIO()
        writer = csv.writer(output)

        if include_headers:
            writer.writerow(header_names)

        for customer in queryset.only(*field_names).iterator(chunk_size=500):
            row = []
            for field in field_names:
                val = getattr(customer, field, "")
                if val is None:
                    val = ""
                row.append(str(val))
            writer.writerow(row)

        return output.getvalue()

    @classmethod
    def get_available_columns(cls) -> list[dict]:
        """Return list of available export columns."""
        result = []
        for field, label in DEFAULT_EXPORT_COLUMNS:
            result.append({"field": field, "label": label, "default": True})
        for field, label in OPTIONAL_COLUMNS:
            result.append({"field": field, "label": label, "default": False})
        return result
