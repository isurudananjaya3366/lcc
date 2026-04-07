"""
Bulk order import service (Task 40).

Handles CSV/Excel file validation, parsing, and batch order creation.
"""

import csv
import io
import logging
from decimal import Decimal, InvalidOperation

from django.db import transaction

logger = logging.getLogger(__name__)

MAX_IMPORT_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class ImportService:
    """
    Handles bulk import of orders from CSV/Excel files.

    Validates file format, parses rows, groups by order number,
    and creates orders via OrderService.
    """

    REQUIRED_COLUMNS = {"product_sku", "quantity", "unit_price"}
    CUSTOMER_COLUMNS = {"customer_id", "customer_email"}
    OPTIONAL_COLUMNS = {
        "order_number",
        "shipping_address",
        "billing_address",
        "notes",
        "discount_percent",
    }

    @classmethod
    def validate_file(cls, file):
        """
        Validate the uploaded file format and size.

        Returns:
            str: File type ('CSV' or 'EXCEL').
        Raises:
            ValueError: If the file is unsupported or too large.
        """
        name = getattr(file, "name", "")
        if not name:
            raise ValueError("File has no name.")

        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext == "csv":
            file_type = "CSV"
        elif ext in ("xlsx", "xls"):
            file_type = "EXCEL"
        else:
            raise ValueError(
                f"Unsupported file format: .{ext}. Use .csv, .xlsx, or .xls"
            )

        # Check file size
        size = getattr(file, "size", None)
        if size and size > MAX_IMPORT_FILE_SIZE:
            raise ValueError(
                f"File too large ({size} bytes). Maximum is {MAX_IMPORT_FILE_SIZE} bytes."
            )

        return file_type

    @classmethod
    def parse_file(cls, file, file_type):
        """
        Parse the uploaded file into a list of row dicts.

        Returns:
            list[dict]: Parsed rows.
        """
        if file_type == "CSV":
            return cls._parse_csv(file)
        elif file_type == "EXCEL":
            return cls._parse_excel(file)
        raise ValueError(f"Unsupported file type: {file_type}")

    @classmethod
    def _parse_csv(cls, file):
        """Parse a CSV file into row dicts."""
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))
        return [row for row in reader]

    @classmethod
    def _parse_excel(cls, file):
        """Parse an Excel file into row dicts using openpyxl."""
        try:
            import openpyxl
        except ImportError:
            raise ValueError(
                "openpyxl is required for Excel import. "
                "Install with: pip install openpyxl"
            )

        wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []

        headers = [str(h).strip().lower() if h else "" for h in rows[0]]
        result = []
        for row in rows[1:]:
            row_dict = {}
            for i, val in enumerate(row):
                if i < len(headers) and headers[i]:
                    row_dict[headers[i]] = val
            result.append(row_dict)
        wb.close()
        return result

    @classmethod
    def validate_columns(cls, rows):
        """
        Validate that required columns are present.

        Returns:
            list[dict]: Validated rows.
        Raises:
            ValueError: If required columns are missing.
        """
        if not rows:
            raise ValueError("File is empty or has no data rows.")

        headers = set(k.lower().strip() for k in rows[0].keys())

        missing_required = cls.REQUIRED_COLUMNS - headers
        has_customer = bool(cls.CUSTOMER_COLUMNS & headers)

        if missing_required:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing_required))}"
            )
        if not has_customer:
            raise ValueError(
                "At least one customer column required: customer_id or customer_email"
            )

        return rows

    @classmethod
    def validate_row(cls, row, row_number):
        """
        Validate a single data row.

        Returns:
            tuple: (is_valid: bool, errors: list[str])
        """
        errors = []

        # Customer check
        customer_id = row.get("customer_id", "")
        customer_email = row.get("customer_email", "")
        if not customer_id and not customer_email:
            errors.append(f"Row {row_number}: Missing customer_id or customer_email")

        # Product SKU
        sku = row.get("product_sku", "")
        if not sku:
            errors.append(f"Row {row_number}: Missing product_sku")

        # Quantity
        try:
            qty = int(row.get("quantity", 0))
            if qty <= 0:
                errors.append(f"Row {row_number}: Quantity must be positive")
        except (ValueError, TypeError):
            errors.append(f"Row {row_number}: Invalid quantity")

        # Unit price
        try:
            price = Decimal(str(row.get("unit_price", 0)))
            if price < 0:
                errors.append(f"Row {row_number}: Unit price must be non-negative")
        except (InvalidOperation, TypeError, ValueError):
            errors.append(f"Row {row_number}: Invalid unit_price")

        return (len(errors) == 0, errors)

    @classmethod
    def group_orders(cls, rows):
        """
        Group rows by order_number. If no order_number, each row is a separate order.

        Returns:
            list[list[dict]]: Groups of rows, each group becomes one order.
        """
        groups = {}
        ungrouped = []
        for row in rows:
            order_num = row.get("order_number", "").strip()
            if order_num:
                groups.setdefault(order_num, []).append(row)
            else:
                ungrouped.append([row])

        return list(groups.values()) + ungrouped

    @classmethod
    def execute_import(cls, file, user):
        """
        Execute the full import pipeline.

        Returns:
            dict: Results with success, failed, and summary sections.
        """
        file_type = cls.validate_file(file)
        rows = cls.parse_file(file, file_type)
        rows = cls.validate_columns(rows)

        success = []
        failed = []
        total_items = 0

        # Validate all rows first
        valid_rows = []
        for idx, row in enumerate(rows, start=2):  # Row 1 is header
            is_valid, errors = cls.validate_row(row, idx)
            if is_valid:
                valid_rows.append((idx, row))
            else:
                failed.append(
                    {
                        "row_number": idx,
                        "errors": errors,
                        "data": {k: str(v) for k, v in row.items()},
                    }
                )

        # Group valid rows into orders
        valid_row_dicts = [r for _, r in valid_rows]
        row_numbers_map = {}
        for idx, row in valid_rows:
            key = row.get("order_number", "").strip() or f"_auto_{idx}"
            row_numbers_map.setdefault(key, []).append(idx)

        order_groups = cls.group_orders(valid_row_dicts)

        for group in order_groups:
            try:
                order = cls._create_order_from_group(group, user)
                group_key = group[0].get("order_number", "").strip()
                row_nums = row_numbers_map.get(
                    group_key, [f"auto_{i}" for i in range(len(group))]
                )
                success.append(
                    {
                        "order_number": order.order_number,
                        "order_id": str(order.id),
                        "row_numbers": row_nums,
                    }
                )
                total_items += len(group)
            except Exception as exc:
                logger.exception("Failed to create order from import group")
                failed.append(
                    {
                        "row_number": "group",
                        "errors": [str(exc)],
                        "data": {
                            "first_sku": group[0].get("product_sku", ""),
                        },
                    }
                )

        return {
            "success": success,
            "failed": failed,
            "summary": {
                "total_rows": len(rows),
                "successful_orders": len(success),
                "failed_rows": len(failed),
                "total_items_imported": total_items,
            },
        }

    @classmethod
    @transaction.atomic
    def _create_order_from_group(cls, group, user):
        """Create a single order from a group of import rows."""
        from apps.orders.constants import OrderSource
        from apps.orders.services.order_service import OrderService

        first_row = group[0]

        # Build order data
        data = {
            "source": OrderSource.IMPORT,
            "customer_email": first_row.get("customer_email", ""),
            "customer_name": first_row.get("customer_email", ""),
            "notes": first_row.get("notes", ""),
            "shipping_address": cls._parse_address(
                first_row.get("shipping_address", "")
            ),
            "billing_address": cls._parse_address(
                first_row.get("billing_address", "")
            ),
        }

        # Resolve customer
        customer_id = first_row.get("customer_id", "")
        if customer_id:
            data["customer"] = customer_id

        # Build items data
        items_data = []
        for row in group:
            discount_pct = Decimal(str(row.get("discount_percent", 0) or 0))
            unit_price = Decimal(str(row.get("unit_price", 0)))
            discount_value = (unit_price * discount_pct / 100) if discount_pct else 0

            items_data.append(
                {
                    "item_sku": row.get("product_sku", ""),
                    "item_name": row.get("product_sku", ""),
                    "quantity_ordered": int(row.get("quantity", 1)),
                    "unit_price": unit_price,
                    "discount_type": "percentage" if discount_pct else "",
                    "discount_value": discount_value,
                }
            )

        order = OrderService.create_order(data, items_data, user=user)
        return order

    @staticmethod
    def _parse_address(address_str):
        """Parse an address string into a dict."""
        if not address_str:
            return {}
        if isinstance(address_str, dict):
            return address_str
        return {"raw": str(address_str)}
