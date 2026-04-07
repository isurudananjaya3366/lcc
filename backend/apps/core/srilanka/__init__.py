"""
Sri Lanka-specific utilities for LankaCommerce Cloud.

Utilities:
    - Currency: LKR formatting and conversion
    - Phone: Sri Lankan phone number validation
    - NIC: National Identity Card validation
    - Administrative: Provinces and districts
"""

__version__ = '1.0.0'

# Currency utilities
from .currency import (
    format_lkr,
    parse_lkr,
    convert_currency,
)

# Phone utilities
from .phone import (
    validate_sl_phone,
    format_sl_phone,
    normalize_sl_phone,
)

# NIC utilities
from .nic import (
    validate_nic,
    parse_nic_dob,
)

# Administrative divisions
from .provinces import (
    PROVINCES,
    DISTRICTS,
    get_province_by_code,
    get_province_choices,
    get_districts_by_province,
    get_district_by_code,
    get_district_choices,
)

__all__ = [
    # Currency
    'format_lkr',
    'parse_lkr',
    'convert_currency',
    # Phone
    'validate_sl_phone',
    'format_sl_phone',
    'normalize_sl_phone',
    # NIC
    'validate_nic',
    'parse_nic_dob',
    # Administrative
    'PROVINCES',
    'DISTRICTS',
    'get_province_by_code',
    'get_province_choices',
    'get_districts_by_province',
    'get_district_by_code',
    'get_district_choices',
]
