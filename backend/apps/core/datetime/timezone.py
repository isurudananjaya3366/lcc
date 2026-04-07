"""
Timezone utilities for Sri Lankan context.

Timezone: Asia/Colombo (UTC+5:30)
No daylight saving time changes
"""

import pytz
from datetime import datetime
from django.utils import timezone as django_tz

# Sri Lankan timezone constant
SL_TIMEZONE = pytz.timezone('Asia/Colombo')


def get_local_now():
    """
    Get current date/time in Sri Lankan timezone.

    Returns:
        datetime: Current datetime in Asia/Colombo timezone

    Example:
        >>> local_now = get_local_now()
        >>> print(local_now)
        2026-01-23 14:30:00+05:30
    """
    return django_tz.now().astimezone(SL_TIMEZONE)


def convert_to_utc(local_datetime):
    """
    Convert Sri Lankan local datetime to UTC.

    Use for: Database storage (always store in UTC)

    Args:
        local_datetime: Datetime in Asia/Colombo or naive

    Returns:
        datetime: Timezone-aware datetime in UTC

    Example:
        >>> sl_time = datetime(2026, 1, 23, 14, 30)
        >>> utc_time = convert_to_utc(sl_time)
        >>> print(utc_time)
        2026-01-23 09:00:00+00:00
    """
    if local_datetime.tzinfo is None:
        # Naive datetime, assume Sri Lankan time
        local_datetime = SL_TIMEZONE.localize(local_datetime)

    return local_datetime.astimezone(pytz.UTC)


def convert_to_local(utc_datetime):
    """
    Convert UTC datetime to Sri Lankan local time.

    Use for: Displaying dates/times to users

    Args:
        utc_datetime: Datetime in UTC or naive (assumed UTC)

    Returns:
        datetime: Timezone-aware datetime in Asia/Colombo

    Example:
        >>> utc_time = datetime(2026, 1, 23, 9, 0, tzinfo=pytz.UTC)
        >>> local_time = convert_to_local(utc_time)
        >>> print(local_time)
        2026-01-23 14:30:00+05:30
    """
    if utc_datetime.tzinfo is None:
        # Naive datetime, assume UTC
        utc_datetime = pytz.UTC.localize(utc_datetime)

    return utc_datetime.astimezone(SL_TIMEZONE)
