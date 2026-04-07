"""Vendor export service for CSV-based data exports."""

import io
import csv


class VendorExportService:
    """Service class for exporting vendor data to CSV."""

    @staticmethod
    def export_vendors_to_csv(queryset=None, fields=None):
        """Export vendors to a CSV StringIO object.

        Args:
            queryset: Optional vendor queryset (defaults to all active vendors).
            fields: Optional list of field names to export.

        Returns:
            A StringIO object containing the CSV data.
        """
        from apps.vendors.models import Vendor

        if queryset is None:
            queryset = Vendor.objects.filter(is_deleted=False)

        if fields is None:
            fields = VendorExportService.get_default_export_fields()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(fields)

        for vendor in queryset.iterator():
            row = []
            for field in fields:
                value = getattr(vendor, field, "")
                if value is None:
                    value = ""
                row.append(str(value))
            writer.writerow(row)

        output.seek(0)
        return output

    @staticmethod
    def get_default_export_fields():
        """Return the default list of fields for vendor CSV export."""
        return [
            "vendor_code",
            "company_name",
            "vendor_type",
            "business_registration",
            "tax_id",
            "primary_email",
            "primary_phone",
            "address_line_1",
            "city",
            "district",
            "province",
            "payment_terms_days",
            "credit_limit",
            "rating",
            "total_orders",
            "total_spend",
            "status",
            "created_on",
        ]
