"""
Validators for the customers application.

Includes Sri Lanka-specific validators for district-province mapping
and phone number format validation.
"""

import re

from django.core.exceptions import ValidationError


# Sri Lanka district-to-province mapping
DISTRICT_PROVINCE_MAP = {
    "Colombo": "Western Province",
    "Gampaha": "Western Province",
    "Kalutara": "Western Province",
    "Kandy": "Central Province",
    "Matale": "Central Province",
    "Nuwara Eliya": "Central Province",
    "Galle": "Southern Province",
    "Matara": "Southern Province",
    "Hambantota": "Southern Province",
    "Jaffna": "Northern Province",
    "Kilinochchi": "Northern Province",
    "Mannar": "Northern Province",
    "Mullaitivu": "Northern Province",
    "Vavuniya": "Northern Province",
    "Batticaloa": "Eastern Province",
    "Ampara": "Eastern Province",
    "Trincomalee": "Eastern Province",
    "Kurunegala": "North Western Province",
    "Puttalam": "North Western Province",
    "Anuradhapura": "North Central Province",
    "Polonnaruwa": "North Central Province",
    "Badulla": "Uva Province",
    "Monaragala": "Uva Province",
    "Ratnapura": "Sabaragamuwa Province",
    "Kegalle": "Sabaragamuwa Province",
}


def validate_district_province(district, province):
    """
    Validate that a district belongs to the specified province.

    Args:
        district: District name (with or without "District" suffix).
        province: Province name.

    Raises:
        ValidationError: If the district does not belong to the province.
    """
    # Normalize district name (remove "District" suffix if present)
    clean_district = district.replace(" District", "").strip()

    if clean_district in DISTRICT_PROVINCE_MAP:
        expected_province = DISTRICT_PROVINCE_MAP[clean_district]
        if expected_province != province:
            raise ValidationError(
                f"{district} belongs to {expected_province}, "
                f"not {province}."
            )


# Sri Lanka phone number patterns
SL_MOBILE_PATTERN = re.compile(
    r"^(\+94\s?|0)7[0-8]\s?\d{3}\s?\d{4}$"
)
SL_LANDLINE_PATTERN = re.compile(
    r"^(\+94\s?|0)\d{2}\s?\d{3}\s?\d{4}$"
)


def validate_phone_number(phone_number):
    """
    Validate Sri Lanka phone number format.

    Accepts both +94 and 0-prefixed formats for mobile and landline.

    Args:
        phone_number: Phone number string.

    Raises:
        ValidationError: If the format is invalid.
    """
    cleaned = phone_number.strip()
    if not cleaned:
        return

    if SL_MOBILE_PATTERN.match(cleaned) or SL_LANDLINE_PATTERN.match(cleaned):
        return

    # Allow international numbers starting with +
    if cleaned.startswith("+") and len(cleaned) >= 8:
        return

    raise ValidationError(
        f"Invalid phone number format: {phone_number}. "
        "Expected Sri Lanka format: +94 77 123 4567 or 0771234567."
    )
