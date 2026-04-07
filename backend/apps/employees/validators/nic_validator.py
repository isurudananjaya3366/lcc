"""Sri Lanka NIC (National Identity Card) validator."""

import calendar
import re
from datetime import date

from django.core.exceptions import ValidationError


# Old format: 9 digits + V or X (e.g., 912345678V)
OLD_NIC_PATTERN = re.compile(r"^(\d{9})[VvXx]$")

# New format: 12 digits (e.g., 199112345678)
NEW_NIC_PATTERN = re.compile(r"^(\d{12})$")


def is_leap_year(year):
    """Return True if the given year is a leap year."""
    return calendar.isleap(year)


def is_valid_day_of_year(day_of_year, year=None):
    """
    Validate whether a day-of-year value is valid.

    Args:
        day_of_year: The day number (1-366 for male, 501-866 for female).
        year: Optional year for leap year validation.

    Returns:
        True if valid, False otherwise.
    """
    # Adjust for female offset
    adjusted = day_of_year
    if adjusted >= 500:
        adjusted -= 500

    if adjusted < 1:
        return False

    max_day = 366 if (year and is_leap_year(year)) else 365
    return adjusted <= max_day


def extract_nic_components(nic_value):
    """
    Extract all components from a NIC number.

    Returns:
        dict with keys: format, year, day_of_year, gender, sequence
        or None if invalid.
    """
    if not nic_value:
        return None

    nic_value = nic_value.strip()
    old_match = OLD_NIC_PATTERN.match(nic_value)
    new_match = NEW_NIC_PATTERN.match(nic_value)

    if old_match:
        digits = old_match.group(1)
        year = 1900 + int(digits[:2])
        day_of_year = int(digits[2:5])
        sequence = digits[5:]
        gender = "female" if day_of_year >= 500 else "male"
        return {
            "format": "old",
            "year": year,
            "day_of_year": day_of_year,
            "gender": gender,
            "sequence": sequence,
        }
    elif new_match:
        digits = new_match.group(1)
        year = int(digits[:4])
        day_of_year = int(digits[4:7])
        sequence = digits[7:]
        gender = "female" if day_of_year >= 500 else "male"
        return {
            "format": "new",
            "year": year,
            "day_of_year": day_of_year,
            "gender": gender,
            "sequence": sequence,
        }

    return None


def validate_nic(value):
    """
    Validate Sri Lanka NIC number.

    Supports both old format (9 digits + V/X) and new format (12 digits).

    Old format: YYDDDNNNNV/X
        - YY: Year of birth (2 digits)
        - DDD: Day of year (001-366 male, 501-866 female)
        - NNNN: Sequence number
        - V or X: Suffix

    New format: YYYYDDDNNNNN
        - YYYY: Year of birth (4 digits)
        - DDD: Day of year (001-366 male, 501-866 female)
        - NNNNN: Sequence number
    """
    if not value or not value.strip():
        raise ValidationError(
            "NIC number is required.",
            code="required",
        )

    value = value.strip()

    old_match = OLD_NIC_PATTERN.match(value)
    new_match = NEW_NIC_PATTERN.match(value)

    if not old_match and not new_match:
        raise ValidationError(
            "Invalid NIC format. Use old format (e.g., 912345678V) "
            "or new format (e.g., 199112345678).",
            code="invalid_nic_format",
        )

    components = extract_nic_components(value)
    if not components:
        raise ValidationError(
            "Could not parse NIC number.",
            code="invalid_nic",
        )

    # Validate year is not in the future
    current_year = date.today().year
    if components["year"] > current_year:
        raise ValidationError(
            f"NIC birth year ({components['year']}) cannot be in the future.",
            code="invalid_nic_year",
        )

    # Validate day of year
    day_of_year = components["day_of_year"]
    if day_of_year >= 500:
        day_of_year -= 500

    if day_of_year < 1 or day_of_year > 366:
        raise ValidationError(
            "Invalid NIC: day of year out of range.",
            code="invalid_nic_day",
        )


def extract_birth_year_from_nic(nic_value):
    """Extract birth year from NIC number."""
    if not nic_value:
        return None

    nic_value = nic_value.strip()
    old_match = OLD_NIC_PATTERN.match(nic_value)
    new_match = NEW_NIC_PATTERN.match(nic_value)

    if old_match:
        year_part = int(old_match.group(1)[:2])
        return 1900 + year_part
    elif new_match:
        return int(new_match.group(1)[:4])
    return None


def extract_gender_from_nic(nic_value):
    """Extract gender from NIC number (male if day <= 366, female if day > 500)."""
    if not nic_value:
        return None

    nic_value = nic_value.strip()
    old_match = OLD_NIC_PATTERN.match(nic_value)
    new_match = NEW_NIC_PATTERN.match(nic_value)

    if old_match:
        day_of_year = int(old_match.group(1)[2:5])
    elif new_match:
        day_of_year = int(new_match.group(1)[4:7])
    else:
        return None

    return "female" if day_of_year >= 500 else "male"
