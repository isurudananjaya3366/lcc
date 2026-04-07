"""Sri Lanka phone number validator."""

import re

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator


# +94 followed by 9 digits, or 0 followed by 9 digits
SL_PHONE_PATTERN = re.compile(r"^(\+94|0)\d{9}$")

# Sri Lanka mobile phone prefixes (after 0 or +94)
MOBILE_PREFIXES = [
    "70", "71", "72", "74", "75", "76", "77", "78",
]

# Sri Lanka landline area codes (major)
AREA_CODES = [
    "11",   # Colombo
    "21",   # Jaffna
    "23",   # Trincomalee
    "24",   # Vavuniya
    "25",   # Anuradhapura
    "26",   # Batticaloa
    "27",   # Polonnaruwa
    "31",   # Negombo/Chilaw
    "32",   # Puttalam
    "33",   # Gampaha
    "34",   # Kalutara
    "35",   # Kegalle
    "36",   # Avissawella
    "37",   # Kurunegala
    "38",   # Panadura
    "41",   # Matara
    "45",   # Ratnapura
    "47",   # Hambantota
    "51",   # Hatton
    "52",   # Nuwara Eliya
    "54",   # Nawalapitiya
    "55",   # Badulla
    "57",   # Bandarawela
    "63",   # Ampara
    "65",   # Monaragala
    "66",   # Matale
    "67",   # Dambulla
    "81",   # Kandy
    "91",   # Galle
]


class SriLankaPhoneValidator:
    """
    Validates Sri Lanka phone numbers.

    Accepts formats:
    - +94XXXXXXXXX (international)
    - 0XXXXXXXXX (local)
    """

    def __init__(self, allow_mobile=True, allow_landline=True):
        self.allow_mobile = allow_mobile
        self.allow_landline = allow_landline

    def __call__(self, value):
        if not value:
            return
        validate_sl_phone(value)

    def __eq__(self, other):
        return (
            isinstance(other, SriLankaPhoneValidator)
            and self.allow_mobile == other.allow_mobile
            and self.allow_landline == other.allow_landline
        )

    def deconstruct(self):
        return (
            f"{self.__class__.__module__}.{self.__class__.__qualname__}",
            [],
            {
                "allow_mobile": self.allow_mobile,
                "allow_landline": self.allow_landline,
            },
        )


def validate_sl_phone(value):
    """
    Validate Sri Lanka phone number format.

    Accepts: +94XXXXXXXXX or 0XXXXXXXXX (10-12 chars total).
    Validates prefix against known mobile and landline prefixes.
    """
    if not value:
        return

    cleaned = re.sub(r"[\s\-()]", "", value)

    if not SL_PHONE_PATTERN.match(cleaned):
        raise ValidationError(
            "Invalid phone number format. Use +94XXXXXXXXX or 0XXXXXXXXX.",
            code="invalid_phone_format",
        )

    # Extract prefix (2 digits after country code or leading 0)
    if cleaned.startswith("+94"):
        prefix = cleaned[3:5]
    else:
        prefix = cleaned[1:3]

    all_valid_prefixes = MOBILE_PREFIXES + AREA_CODES
    if prefix not in all_valid_prefixes:
        raise ValidationError(
            f"Invalid phone prefix '{prefix}'. Not a recognized Sri Lankan mobile or landline prefix.",
            code="invalid_phone_prefix",
        )
