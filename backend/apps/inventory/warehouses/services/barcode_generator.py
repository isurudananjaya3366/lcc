"""
Service for generating and validating location barcodes.

Barcodes follow format: LOC-{TENANT_PREFIX}-{WAREHOUSE_CODE}-{LOCATION_CODE}-{CHECK_DIGIT}
Example: LOC-ABC-WHCMB01-A03R02S01B05-7
"""

import logging

from apps.inventory.warehouses.constants import (
    BARCODE_LOCATION_CODE_LENGTH,
    BARCODE_PREFIX_LOCATION,
    BARCODE_SEPARATOR,
    BARCODE_TENANT_PREFIX_LENGTH,
    BARCODE_WAREHOUSE_CODE_LENGTH,
    CHECK_DIGIT_LENGTH,
)

logger = logging.getLogger(__name__)


class BarcodeGenerator:
    """
    Service for generating location barcodes with Luhn check digit validation.

    Barcodes follow the format:
    LOC-{TENANT_PREFIX}-{WAREHOUSE_CODE}-{LOCATION_CODE}-{CHECK_DIGIT}
    """

    def __init__(self):
        self.prefix = BARCODE_PREFIX_LOCATION
        self.separator = BARCODE_SEPARATOR

    # ── Tenant / code helpers ─────────────────────────────────────────

    def get_tenant_prefix(self, tenant):
        """
        Extract 3-letter prefix from tenant.

        Uses tenant.code first, then tenant.name, padded with 'X' if short.
        """
        name = getattr(tenant, "code", None) or getattr(tenant, "name", "TEN")
        cleaned = "".join(c for c in str(name) if c.isalnum())
        return cleaned[:BARCODE_TENANT_PREFIX_LENGTH].upper().ljust(
            BARCODE_TENANT_PREFIX_LENGTH, "X"
        )

    def normalize_code(self, code):
        """Remove hyphens/spaces and uppercase an alphanumeric code."""
        if not code:
            return ""
        return "".join(c for c in code.replace("-", "").replace(" ", "").upper() if c.isalnum())

    # ── Luhn check digit ──────────────────────────────────────────────

    def _to_numeric_string(self, text):
        """Convert alphanumeric text to numeric string (A=10 … Z=35)."""
        result = []
        for char in text.upper():
            if char.isdigit():
                result.append(char)
            elif char.isalpha():
                result.append(str(ord(char) - ord("A") + 10))
        return "".join(result)

    def calculate_check_digit(self, barcode_base):
        """Calculate Luhn check digit for *barcode_base* (without check digit)."""
        numeric = self._to_numeric_string(barcode_base)
        total = 0
        is_second = False
        for digit in reversed(numeric):
            n = int(digit)
            if is_second:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
            is_second = not is_second
        return str((10 - (total % 10)) % 10)

    # ── Generation ────────────────────────────────────────────────────

    def generate_location_barcode(self, location):
        """
        Generate a complete barcode for a StorageLocation instance.

        Raises ValueError when required fields are missing.
        """
        if not location.warehouse:
            raise ValueError("Location must have a warehouse assigned")
        if not location.code:
            raise ValueError("Location must have a code assigned")

        # Try to get tenant from connection (django-tenants stores it there)
        from django.db import connection

        tenant = getattr(connection, "tenant", None)
        tenant_prefix = self.get_tenant_prefix(tenant) if tenant else "TEN"

        warehouse_code = self.normalize_code(location.warehouse.code)[
            :BARCODE_WAREHOUSE_CODE_LENGTH
        ]
        location_code = self.normalize_code(location.code)[
            :BARCODE_LOCATION_CODE_LENGTH
        ]

        barcode_base = self.separator.join(
            [self.prefix, tenant_prefix, warehouse_code, location_code]
        )
        check_digit = self.calculate_check_digit(barcode_base)
        barcode = f"{barcode_base}{self.separator}{check_digit}"

        if not self.validate_barcode_format(barcode):
            raise ValueError(f"Generated barcode has invalid format: {barcode}")

        if self._barcode_exists(barcode, location):
            barcode = self._make_unique(barcode, location)

        return barcode

    def _barcode_exists(self, barcode, exclude_location=None):
        from apps.inventory.warehouses.models import StorageLocation

        qs = StorageLocation.objects.filter(barcode=barcode)
        if exclude_location and exclude_location.pk:
            qs = qs.exclude(pk=exclude_location.pk)
        return qs.exists()

    def _make_unique(self, barcode, location):
        base = barcode.rsplit(self.separator, 1)[0]
        for i in range(1, 100):
            candidate = f"{base}{self.separator}{i:02d}"
            if not self._barcode_exists(candidate, location):
                return candidate
        raise ValueError("Could not generate unique barcode")

    # ── Validation ────────────────────────────────────────────────────

    def validate_barcode_format(self, barcode):
        """Return True if *barcode* has the expected 5-part structure."""
        if not barcode or not barcode.startswith(self.prefix):
            return False
        parts = barcode.split(self.separator)
        if len(parts) != 5:
            return False
        prefix, tenant, _warehouse, _location, check = parts
        if prefix != self.prefix:
            return False
        if len(tenant) != BARCODE_TENANT_PREFIX_LENGTH:
            return False
        if len(check) != CHECK_DIGIT_LENGTH or not check.isdigit():
            return False
        return True

    def validate_barcode(self, barcode):
        """Validate format **and** Luhn check digit."""
        if not self.validate_barcode_format(barcode):
            return False
        parts = barcode.split(self.separator)
        barcode_base = self.separator.join(parts[:-1])
        return parts[-1] == self.calculate_check_digit(barcode_base)

    def validate_barcode_detailed(self, barcode):
        """Return ``(is_valid, error_messages)`` with detailed diagnostics."""
        errors = []
        if not barcode:
            return False, ["Barcode is empty"]
        if not barcode.startswith(self.prefix):
            errors.append(f"Barcode must start with {self.prefix}")

        parts = barcode.split(self.separator)
        if len(parts) != 5:
            errors.append(
                f"Barcode must have 5 components separated by '{self.separator}'"
            )
            return False, errors

        prefix, tenant, _warehouse, _location, check = parts
        if prefix != self.prefix:
            errors.append(f"Invalid prefix: {prefix}")
        if len(tenant) != BARCODE_TENANT_PREFIX_LENGTH:
            errors.append(
                f"Tenant prefix must be {BARCODE_TENANT_PREFIX_LENGTH} characters"
            )
        if not check.isdigit():
            errors.append("Check digit must be a number")
        else:
            barcode_base = self.separator.join(parts[:-1])
            expected = self.calculate_check_digit(barcode_base)
            if check != expected:
                errors.append(
                    f"Invalid check digit: expected {expected}, got {check}"
                )

        return len(errors) == 0, errors

    def parse_barcode(self, barcode):
        """Parse a valid barcode into its component dict, or return None."""
        if not self.validate_barcode(barcode):
            return None
        parts = barcode.split(self.separator)
        return {
            "prefix": parts[0],
            "tenant_prefix": parts[1],
            "warehouse_code": parts[2],
            "location_code": parts[3],
            "check_digit": parts[4],
            "is_valid": True,
        }
