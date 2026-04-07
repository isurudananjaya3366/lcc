"""
Date and time utilities for LankaCommerce Cloud.

Sri Lankan timezone: Asia/Colombo (UTC+5:30)
No daylight saving time

Utilities:
    - Timezone conversion (UTC ↔ Asia/Colombo)
    - Date range helpers
    - Date formatting (DD/MM/YYYY)
    - Fiscal year helpers (April-March)
"""

__version__ = '1.0.0'

from .timezone import (
    SL_TIMEZONE,
    get_local_now,
    convert_to_utc,
    convert_to_local,
)

from .date_utils import (
    get_date_range,
    get_month_range,
    get_year_range,
    format_date,
    format_datetime,
)

__all__ = [
    'SL_TIMEZONE',
    'get_local_now',
    'convert_to_utc',
    'convert_to_local',
    'get_date_range',
    'get_month_range',
    'get_year_range',
    'format_date',
    'format_datetime',
]
