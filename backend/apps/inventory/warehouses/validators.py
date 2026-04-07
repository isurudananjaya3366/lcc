"""
Custom validators for the warehouse module.

Provides validation for Sri Lankan phone numbers and postal codes.
"""

import re

from django.core.exceptions import ValidationError


def validate_sri_lankan_phone(value):
    """
    Validate Sri Lankan phone number format.

    Accepted formats:
        +94XXXXXXXXX  (11 digits after +)
        0XXXXXXXXX    (10 digits starting with 0)
    """
    if not value:
        return
    pattern = r"^(\+94\d{9}|0\d{9})$"
    cleaned = re.sub(r"[\s\-()]", "", value)
    if not re.match(pattern, cleaned):
        raise ValidationError(
            "Enter a valid Sri Lankan phone number "
            "(e.g., +94 77 123 4567 or 077 123 4567)."
        )
