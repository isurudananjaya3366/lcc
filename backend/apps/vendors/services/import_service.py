"""Vendor import service for CSV-based bulk imports."""

import io
import csv
from decimal import Decimal, InvalidOperation

from django.db import transaction


class VendorImportService:
    """Service class for importing vendors from CSV files."""

    @staticmethod
    def import_vendors_from_csv(csv_file, update_existing=False):
        """Import vendors from a CSV file.

        Returns a dict with total, created, updated, failed, and errors.
        """
        from apps.vendors.models import Vendor
        from apps.vendors.constants import VENDOR_TYPE_CHOICES

        result = {"total": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

        if isinstance(csv_file, bytes):
            csv_file = io.StringIO(csv_file.decode("utf-8"))
        elif hasattr(csv_file, "read"):
            content = csv_file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            csv_file = io.StringIO(content)

        reader = csv.DictReader(csv_file)
        column_mapping = VendorImportService._get_column_mapping(reader.fieldnames or [])

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                result["total"] += 1

                row_data = {}
                for csv_col, model_field in column_mapping.items():
                    if csv_col in row:
                        row_data[model_field] = row[csv_col].strip() if row[csv_col] else ""

                errors = VendorImportService._validate_row(row_data, row_num)
                if errors:
                    result["failed"] += 1
                    result["errors"].extend(errors)
                    continue

                # Convert numeric fields
                if "payment_terms_days" in row_data and row_data["payment_terms_days"]:
                    try:
                        row_data["payment_terms_days"] = int(row_data["payment_terms_days"])
                    except (ValueError, TypeError):
                        row_data.pop("payment_terms_days", None)

                if "credit_limit" in row_data and row_data["credit_limit"]:
                    try:
                        row_data["credit_limit"] = Decimal(row_data["credit_limit"])
                    except (InvalidOperation, ValueError):
                        row_data.pop("credit_limit", None)

                try:
                    if update_existing:
                        vendor, created = Vendor.objects.update_or_create(
                            company_name=row_data.pop("company_name"),
                            defaults=row_data,
                        )
                        if created:
                            result["created"] += 1
                        else:
                            result["updated"] += 1
                    else:
                        Vendor.objects.create(**row_data)
                        result["created"] += 1
                except Exception as e:
                    result["failed"] += 1
                    result["errors"].append(f"Row {row_num}: {str(e)}")

        return result

    @staticmethod
    def _get_column_mapping(headers):
        """Map CSV headers to model field names (case-insensitive)."""
        mapping = {}
        header_map = {
            "company_name": "company_name",
            "company name": "company_name",
            "vendor_type": "vendor_type",
            "vendor type": "vendor_type",
            "type": "vendor_type",
            "business_registration": "business_registration",
            "business registration": "business_registration",
            "tax_id": "tax_id",
            "tax id": "tax_id",
            "email": "primary_email",
            "primary_email": "primary_email",
            "primary email": "primary_email",
            "phone": "primary_phone",
            "primary_phone": "primary_phone",
            "primary phone": "primary_phone",
            "address": "address_line_1",
            "address_line_1": "address_line_1",
            "address line 1": "address_line_1",
            "city": "city",
            "district": "district",
            "province": "province",
            "payment_terms": "payment_terms_days",
            "payment terms": "payment_terms_days",
            "payment_terms_days": "payment_terms_days",
            "payment terms days": "payment_terms_days",
            "credit_limit": "credit_limit",
            "credit limit": "credit_limit",
        }

        for header in headers:
            normalized = header.strip().lower()
            if normalized in header_map:
                mapping[header] = header_map[normalized]

        return mapping

    @staticmethod
    def _validate_row(row_data, row_num):
        """Validate a row of import data. Returns a list of error strings."""
        from apps.vendors.constants import VENDOR_TYPE_CHOICES

        errors = []
        if not row_data.get("company_name"):
            errors.append(f"Row {row_num}: company_name is required.")

        vendor_type = row_data.get("vendor_type")
        if not vendor_type:
            errors.append(f"Row {row_num}: vendor_type is required.")
        else:
            valid_types = [choice[0] for choice in VENDOR_TYPE_CHOICES]
            if vendor_type not in valid_types:
                errors.append(
                    f"Row {row_num}: Invalid vendor_type '{vendor_type}'. "
                    f"Valid types: {', '.join(valid_types)}"
                )

        return errors
