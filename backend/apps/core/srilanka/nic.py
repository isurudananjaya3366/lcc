"""
Sri Lankan National Identity Card (NIC) validation and parsing.

Old format: 9 digits + V/X (e.g., 881234567V)
    - First 2 digits: Birth year (last 2 digits)
    - Next 3 digits: Day of year (+500 for females)
    - Last 4 digits: Serial number
    - Suffix: V (voter/male) or X (female)

New format: 12 digits (e.g., 198812345678)
    - First 4 digits: Birth year (full)
    - Next 3 digits: Day of year (+500 for females)
    - Last 5 digits: Serial number
"""

import re
from datetime import datetime, timedelta


def validate_nic(nic):
    """
    Validate Sri Lankan NIC (old or new format).

    Old: 9 digits + V/X (e.g., 881234567V)
    New: 12 digits (e.g., 198812345678)

    Args:
        nic: NIC number string

    Returns:
        bool: True if valid NIC

    Examples:
        >>> validate_nic("881234567V")
        True
        >>> validate_nic("198812345678")
        True
        >>> validate_nic("invalid")
        False
    """
    if not isinstance(nic, str):
        return False

    nic = nic.strip().upper()

    # Old format: 9 digits + V/X
    old_pattern = r'^\d{9}[VX]$'
    if re.match(old_pattern, nic):
        return _validate_old_nic(nic)

    # New format: 12 digits
    new_pattern = r'^\d{12}$'
    if re.match(new_pattern, nic):
        return _validate_new_nic(nic)

    return False


def _validate_old_nic(nic):
    """Validate old NIC format (9 digits + V/X)."""
    days = int(nic[2:5])

    # Days should be 1-366 or 501-866 (for females)
    if days == 0 or days > 866:
        return False
    if 367 <= days <= 500:
        return False

    return True


def _validate_new_nic(nic):
    """Validate new NIC format (12 digits)."""
    year = int(nic[0:4])
    days = int(nic[4:7])

    # Year should be reasonable (1900-2100)
    if year < 1900 or year > 2100:
        return False

    # Days should be 1-366 or 501-866 (for females)
    if days == 0 or days > 866:
        return False
    if 367 <= days <= 500:
        return False

    return True


def parse_nic_dob(nic):
    """
    Extract date of birth and gender from NIC.

    Args:
        nic: Valid NIC number string

    Returns:
        tuple: (date, str) - Date of birth and gender ('M' or 'F')

    Raises:
        ValueError: If NIC is invalid

    Examples:
        >>> dob, gender = parse_nic_dob("881234567V")
        >>> # dob = date for day 123 of 1988
        >>> # gender = 'M' (V suffix or days <= 366)

        >>> dob, gender = parse_nic_dob("886234567X")
        >>> # gender = 'F' (days > 500)
    """
    if not validate_nic(nic):
        raise ValueError(f"Invalid NIC number: {nic}")

    nic = nic.strip().upper()

    if len(nic) == 10:  # Old format
        year = int(nic[0:2])
        # Assume 1900s for year >= 50, 2000s otherwise
        year = 1900 + year if year >= 50 else 2000 + year
        days = int(nic[2:5])
    else:  # New format (12 digits)
        year = int(nic[0:4])
        days = int(nic[4:7])

    # Determine gender
    if days > 500:
        gender = 'F'
        days -= 500
    else:
        gender = 'M'

    # Calculate date of birth from year and day-of-year
    date_of_birth = datetime(year, 1, 1) + timedelta(days=days - 1)

    return date_of_birth.date(), gender
