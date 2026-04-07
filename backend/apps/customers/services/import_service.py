"""
Customer CSV Import Service.

Handles parsing, validating, column-mapping, and batch-creating
customers from uploaded CSV files. Supports progress tracking via
a CustomerImport record.
"""

import csv
import io
import logging
import time
from typing import Any, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.customers.constants import (
    CUSTOMER_STATUS_CHOICES,
    CUSTOMER_TYPE_CHOICES,
    DEFAULT_CUSTOMER_STATUS,
)
from apps.customers.validators import validate_phone_number, validate_district_province

logger = logging.getLogger(__name__)

# ── Default column mapping ──────────────────────────────────────────
DEFAULT_COLUMN_MAP: dict[str, str] = {
    "first_name": "first_name",
    "firstname": "first_name",
    "given_name": "first_name",
    "last_name": "last_name",
    "lastname": "last_name",
    "surname": "last_name",
    "company_name": "business_name",
    "company": "business_name",
    "business_name": "business_name",
    "email": "email",
    "email_address": "email",
    "contact_email": "email",
    "phone": "phone",
    "phone_number": "phone",
    "mobile": "mobile",
    "contact": "phone",
    "address": "billing_address_line_1",
    "street": "billing_address_line_1",
    "address1": "billing_address_line_1",
    "address_line_1": "billing_address_line_1",
    "city": "billing_city",
    "town": "billing_city",
    "district": "billing_state_province",
    "province": "billing_state_province",
    "state": "billing_state_province",
    "postal_code": "billing_postal_code",
    "zip": "billing_postal_code",
    "zip_code": "billing_postal_code",
    "tax_id": "tax_id",
    "tin": "tax_id",
    "vat_number": "vat_number",
    "customer_type": "customer_type",
    "type": "customer_type",
    "status": "status",
    "notes": "notes",
    "display_name": "display_name",
}

VALID_STATUSES = {c[0] for c in CUSTOMER_STATUS_CHOICES}
VALID_TYPES = {c[0] for c in CUSTOMER_TYPE_CHOICES}

BATCH_SIZE = 100

# ── Import modes ────────────────────────────────────────────────────
MODE_STRICT = "strict"
MODE_SKIP_INVALID = "skip_invalid"
MODE_SKIP_DUPLICATE = "skip_duplicate"


class CustomerImportService:
    """Import customers from CSV data."""

    # ── Column Mapping ──────────────────────────────────────────────

    @staticmethod
    def auto_detect_mapping(headers: list[str]) -> dict[str, str]:
        """
        Given CSV headers, return {csv_col: model_field} mapping.
        Uses the DEFAULT_COLUMN_MAP lookup table.
        """
        mapping: dict[str, str] = {}
        for header in headers:
            normalized = header.strip().lower().replace(" ", "_").replace("-", "_")
            model_field = DEFAULT_COLUMN_MAP.get(normalized)
            if model_field:
                mapping[header] = model_field
        return mapping

    # ── Row Validation ──────────────────────────────────────────────

    @classmethod
    def validate_row(
        cls,
        row_data: dict[str, Any],
        row_number: int,
    ) -> dict:
        """
        Validate a single mapped row.
        Returns {"valid": bool, "errors": [...], "row": int}.
        """
        errors: list[dict] = []

        # Customer type
        ctype = row_data.get("customer_type", "").lower()
        if ctype and ctype not in VALID_TYPES:
            errors.append(
                {
                    "field": "customer_type",
                    "message": f"Invalid customer type: {ctype}",
                    "value": ctype,
                }
            )

        # Status
        status_val = row_data.get("status", "").lower()
        if status_val and status_val not in VALID_STATUSES:
            errors.append(
                {
                    "field": "status",
                    "message": f"Invalid status: {status_val}",
                    "value": status_val,
                }
            )

        # Email basic check
        email = (row_data.get("email") or "").strip()
        if email and "@" not in email:
            errors.append(
                {
                    "field": "email",
                    "message": "Invalid email format",
                    "value": email,
                }
            )

        # Phone validation (Sri Lanka)
        phone = (row_data.get("phone") or "").strip()
        if phone:
            try:
                validate_phone_number(phone)
            except Exception:
                errors.append(
                    {
                        "field": "phone",
                        "message": "Invalid Sri Lanka phone number",
                        "value": phone,
                    }
                )

        # District-province consistency
        district = (row_data.get("district") or "").strip()
        province = (row_data.get("province") or "").strip()
        if district and province:
            try:
                validate_district_province(district, province)
            except Exception as exc:
                errors.append(
                    {
                        "field": "district",
                        "message": str(exc).strip("[]'\""),
                        "value": f"{district} / {province}",
                    }
                )

        # Tax ID basic format validation
        tax_id = (row_data.get("tax_id") or "").strip()
        if tax_id and len(tax_id) < 5:
            errors.append(
                {
                    "field": "tax_id",
                    "message": "Tax ID too short (minimum 5 characters)",
                    "value": tax_id,
                }
            )

        return {
            "row": row_number,
            "valid": len(errors) == 0,
            "errors": errors,
        }

    # ── Core Import ─────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def import_from_csv(
        cls,
        csv_file,
        *,
        column_mapping: Optional[dict[str, str]] = None,
        mode: str = MODE_SKIP_INVALID,
        uploaded_by=None,
        import_record=None,
    ) -> dict:
        """
        Parse a CSV file and bulk-create customers.

        Args:
            csv_file: File-like object (text or binary).
            column_mapping: {csv_col: model_field}. Auto-detected if None.
            mode: 'strict', 'skip_invalid', or 'skip_duplicate'.
            uploaded_by: User who triggered the import.
            import_record: Optional CustomerImport instance for progress.

        Returns:
            Import summary dict.
        """
        from apps.customers.models import Customer

        start_time = time.monotonic()
        # Read file content
        if hasattr(csv_file, "read"):
            raw = csv_file.read()
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8-sig")
        else:
            raw = str(csv_file)

        reader = csv.DictReader(io.StringIO(raw))
        headers = reader.fieldnames or []

        if column_mapping is None:
            column_mapping = cls.auto_detect_mapping(headers)

        total_rows = 0
        successful = 0
        failed = 0
        skipped = 0
        error_log: list[dict] = []
        batch: list[Customer] = []

        for row_num, csv_row in enumerate(reader, start=1):
            total_rows += 1
            # Map columns
            mapped = {}
            for csv_col, model_field in column_mapping.items():
                val = csv_row.get(csv_col, "")
                if val:
                    mapped[model_field] = val.strip()

            # Validate
            validation = cls.validate_row(mapped, row_num)
            if not validation["valid"]:
                if mode == MODE_STRICT:
                    raise ValueError(
                        f"Validation failed at row {row_num}: "
                        f"{validation['errors']}"
                    )
                error_log.extend(
                    [
                        {"row": row_num, "error": e["message"], "data": {e["field"]: e["value"]}}
                        for e in validation["errors"]
                    ]
                )
                failed += 1
                continue

            # Duplicate check (by email)
            email = mapped.get("email")
            if email and mode == MODE_SKIP_DUPLICATE:
                if Customer.objects.filter(email__iexact=email, is_deleted=False).exists():
                    skipped += 1
                    continue

            # Normalise type / status
            if "customer_type" in mapped:
                mapped["customer_type"] = mapped["customer_type"].lower()
            if "status" not in mapped:
                mapped["status"] = DEFAULT_CUSTOMER_STATUS

            # Build Customer object (code is auto-generated on save)
            customer = Customer(**mapped)
            if uploaded_by:
                customer.created_by = uploaded_by
            batch.append(customer)

            # Flush batch
            if len(batch) >= BATCH_SIZE:
                _save_batch(batch)
                successful += len(batch)
                batch = []
                # Update progress
                if import_record:
                    cls._update_progress(
                        import_record, total_rows, successful, failed, skipped, error_log
                    )

        # Final batch
        if batch:
            _save_batch(batch)
            successful += len(batch)

        duration = round(time.monotonic() - start_time, 2)

        summary = {
            "total_rows": total_rows,
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "errors": error_log,
            "duration_seconds": duration,
        }

        # Final progress update
        if import_record:
            cls._finalise_import(import_record, summary)

        return summary

    # ── Progress helpers ────────────────────────────────────────────

    @staticmethod
    def _update_progress(record, total, success, fail, skip, errors):
        record.total_rows = total
        record.processed_rows = success + fail + skip
        record.successful_rows = success
        record.failed_rows = fail
        record.skipped_rows = skip
        record.error_log = errors
        record.save(
            update_fields=[
                "total_rows",
                "processed_rows",
                "successful_rows",
                "failed_rows",
                "skipped_rows",
                "error_log",
            ]
        )

    @staticmethod
    def _finalise_import(record, summary):
        record.status = "COMPLETED" if summary["failed"] == 0 else "COMPLETED_WITH_ERRORS"
        record.total_rows = summary["total_rows"]
        record.processed_rows = summary["total_rows"]
        record.successful_rows = summary["successful"]
        record.failed_rows = summary["failed"]
        record.skipped_rows = summary["skipped"]
        record.error_log = summary["errors"]
        record.completed_at = timezone.now()
        record.save()


def _save_batch(customers: list):
    """
    Save a batch of customer objects. Uses individual saves rather
    than bulk_create so that the auto-generated customer_code
    logic in save() is triggered.
    """
    for customer in customers:
        customer.save()
