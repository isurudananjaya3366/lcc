"""
Barcode validators for POS system.

Supports EAN-13, EAN-8, UPC-A, Code-128, and weight-embedded barcodes.
"""

import re
from typing import Optional

from apps.pos.constants import (
    BARCODE_FORMAT_CODE128,
    BARCODE_FORMAT_EAN8,
    BARCODE_FORMAT_EAN13,
    BARCODE_FORMAT_UPC_A,
    BARCODE_FORMAT_WEIGHT,
    WEIGHT_BARCODE_PREFIX,
    WEIGHT_BARCODE_PRODUCT_DIGITS,
    WEIGHT_BARCODE_WEIGHT_DIGITS,
)


def _calculate_ean_check_digit(digits: str) -> int:
    """Calculate EAN/UPC check digit using modulo-10 algorithm."""
    total = 0
    for i, d in enumerate(digits):
        weight = 1 if i % 2 == 0 else 3
        total += int(d) * weight
    return (10 - (total % 10)) % 10


def validate_ean13(barcode: str) -> bool:
    """Validate an EAN-13 barcode (13 digits with valid check digit)."""
    if not barcode or len(barcode) != 13 or not barcode.isdigit():
        return False
    return _calculate_ean_check_digit(barcode[:12]) == int(barcode[12])


def validate_ean8(barcode: str) -> bool:
    """Validate an EAN-8 barcode (8 digits with valid check digit)."""
    if not barcode or len(barcode) != 8 or not barcode.isdigit():
        return False
    return _calculate_ean_check_digit(barcode[:7]) == int(barcode[7])


def validate_upc_a(barcode: str) -> bool:
    """Validate a UPC-A barcode (12 digits with valid check digit)."""
    if not barcode or len(barcode) != 12 or not barcode.isdigit():
        return False
    return _calculate_ean_check_digit(barcode[:11]) == int(barcode[11])


def validate_code128(barcode: str) -> bool:
    """Validate a Code-128 barcode (6-20 alphanumeric characters)."""
    if not barcode or len(barcode) < 6 or len(barcode) > 20:
        return False
    return bool(re.match(r"^[A-Za-z0-9\-_]+$", barcode))


def detect_barcode_format(barcode: str) -> Optional[str]:
    """
    Detect the barcode format from the raw string.

    Returns the format constant or None if unrecognized.
    """
    if not barcode:
        return None

    barcode = barcode.strip()

    if barcode.isdigit():
        if len(barcode) == 13:
            if barcode.startswith(WEIGHT_BARCODE_PREFIX) and validate_ean13(barcode):
                return BARCODE_FORMAT_WEIGHT
            if validate_ean13(barcode):
                return BARCODE_FORMAT_EAN13
        elif len(barcode) == 8 and validate_ean8(barcode):
            return BARCODE_FORMAT_EAN8
        elif len(barcode) == 12 and validate_upc_a(barcode):
            return BARCODE_FORMAT_UPC_A

    if validate_code128(barcode):
        return BARCODE_FORMAT_CODE128

    return None


def parse_weight_barcode(barcode: str) -> Optional[dict]:
    """
    Parse a weight-embedded barcode (prefix '2').

    Format: 2PPPPPWWWWWC (13 digits)
    - P: 5-digit product code
    - W: 5-digit weight in grams
    - C: check digit

    Returns dict with 'product_code' (str) and 'weight_kg' (Decimal) or None.
    """
    if not barcode or len(barcode) != 13 or not barcode.isdigit():
        return None
    if not barcode.startswith(WEIGHT_BARCODE_PREFIX):
        return None
    if not validate_ean13(barcode):
        return None

    from decimal import Decimal

    start = 1
    product_code = barcode[start : start + WEIGHT_BARCODE_PRODUCT_DIGITS]
    weight_start = start + WEIGHT_BARCODE_PRODUCT_DIGITS
    weight_grams = barcode[weight_start : weight_start + WEIGHT_BARCODE_WEIGHT_DIGITS]
    weight_kg = Decimal(weight_grams) / Decimal("1000")

    return {
        "product_code": product_code,
        "weight_kg": weight_kg,
    }


def validate_barcode(barcode: str, barcode_format: Optional[str] = None) -> dict:
    """
    Unified barcode validation.

    If barcode_format is provided, validates against that specific format.
    Otherwise, detects the format automatically and validates.

    Returns dict with keys: valid (bool), format (str|None), message (str).
    """
    if not barcode or not barcode.strip():
        return {"valid": False, "format": None, "message": "Barcode is empty"}

    barcode = barcode.strip()

    format_validators = {
        BARCODE_FORMAT_EAN13: (validate_ean13, "EAN-13"),
        BARCODE_FORMAT_EAN8: (validate_ean8, "EAN-8"),
        BARCODE_FORMAT_UPC_A: (validate_upc_a, "UPC-A"),
        BARCODE_FORMAT_CODE128: (validate_code128, "Code-128"),
    }

    if barcode_format:
        if barcode_format not in format_validators:
            return {
                "valid": False,
                "format": barcode_format,
                "message": f"Unknown barcode format: {barcode_format}",
            }
        validator_fn, label = format_validators[barcode_format]
        is_valid = validator_fn(barcode)
        return {
            "valid": is_valid,
            "format": barcode_format if is_valid else None,
            "message": f"Valid {label} barcode" if is_valid else f"Invalid {label} barcode",
        }

    # Auto-detect
    detected = detect_barcode_format(barcode)
    if detected:
        return {
            "valid": True,
            "format": detected,
            "message": f"Valid barcode (detected: {detected})",
        }

    return {"valid": False, "format": None, "message": "Unrecognized barcode format"}


def is_weight_barcode(barcode: str) -> bool:
    """Check if a barcode is a weight-embedded barcode."""
    if not barcode or len(barcode) != 13 or not barcode.isdigit():
        return False
    return barcode.startswith(WEIGHT_BARCODE_PREFIX) and validate_ean13(barcode)


def generate_weight_barcode(product_code: str, weight_grams: int) -> Optional[str]:
    """
    Generate a weight-embedded EAN-13 barcode.

    Args:
        product_code: 5-digit product code
        weight_grams: Weight in grams (0-99999)

    Returns:
        13-digit barcode string or None if inputs are invalid.
    """
    if not product_code or len(product_code) != WEIGHT_BARCODE_PRODUCT_DIGITS:
        return None
    if not product_code.isdigit():
        return None
    if weight_grams < 0 or weight_grams > 99999:
        return None

    body = f"{WEIGHT_BARCODE_PREFIX}{product_code}{weight_grams:05d}"
    check_digit = _calculate_ean_check_digit(body)
    return f"{body}{check_digit}"
