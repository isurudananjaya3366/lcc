"""
Sri Lankan phone number validation and formatting.

International format: +94 XX XXX XXXX
Valid mobile prefixes: 70, 71, 72, 74, 75, 76, 77, 78
"""

import re


def validate_sl_phone(phone):
    """
    Validate Sri Lankan phone number.

    Accepted formats:
        - +94 XX XXX XXXX
        - +94XXXXXXXXX
        - 0XXXXXXXXX
        - XXXXXXXXX (9 digits starting with 7)

    Valid mobile prefixes: 70, 71, 72, 74, 75, 76, 77, 78

    Args:
        phone: Phone number string

    Returns:
        bool: True if valid Sri Lankan mobile number

    Examples:
        >>> validate_sl_phone("+94 71 234 5678")
        True
        >>> validate_sl_phone("0712345678")
        True
        >>> validate_sl_phone("712345678")
        True
    """
    if not isinstance(phone, str):
        return False

    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)

    # Pattern: optional +94 or 0, then mobile prefix (70-78, not 73/79), then 7 digits
    pattern = r'^(\+94|0)?(7[01245678])\d{7}$'

    return bool(re.match(pattern, cleaned))


def format_sl_phone(phone):
    """
    Format phone number in standard format: +94 XX XXX XXXX

    Args:
        phone: Phone number string

    Returns:
        str: Formatted phone number

    Raises:
        ValueError: If phone number is invalid

    Example:
        >>> format_sl_phone("0712345678")
        '+94 71 234 5678'
    """
    if not validate_sl_phone(phone):
        raise ValueError(f"Invalid Sri Lankan phone number: {phone}")

    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d]', '', phone)

    # Remove country code prefix
    if cleaned.startswith('94'):
        cleaned = cleaned[2:]
    elif cleaned.startswith('0'):
        cleaned = cleaned[1:]

    # Format as +94 XX XXX XXXX
    return f"+94 {cleaned[:2]} {cleaned[2:5]} {cleaned[5:]}"


def normalize_sl_phone(phone):
    """
    Normalize phone number to storage format: +94XXXXXXXXX

    Args:
        phone: Phone number string

    Returns:
        str: Normalized phone number

    Raises:
        ValueError: If phone number is invalid

    Example:
        >>> normalize_sl_phone("0712345678")
        '+94712345678'
    """
    if not validate_sl_phone(phone):
        raise ValueError(f"Invalid Sri Lankan phone number: {phone}")

    # Remove all non-digit characters
    cleaned = re.sub(r'[^\d]', '', phone)

    # Remove country code prefix if present
    if cleaned.startswith('94'):
        cleaned = cleaned[2:]
    elif cleaned.startswith('0'):
        cleaned = cleaned[1:]

    return f"+94{cleaned}"
