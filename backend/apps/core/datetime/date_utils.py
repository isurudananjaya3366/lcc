"""
Date utilities for LankaCommerce Cloud.

Sri Lankan date format: DD/MM/YYYY
Fiscal year: April to March
"""

from datetime import datetime, timedelta, date
from calendar import monthrange

from .timezone import SL_TIMEZONE, get_local_now, convert_to_local


def get_date_range(target_date=None):
    """
    Get start and end datetime for a specific date.

    Args:
        target_date: date object (default: today in SL timezone)

    Returns:
        tuple: (start_datetime, end_datetime) in SL timezone

    Example:
        >>> start, end = get_date_range(date(2026, 1, 23))
        >>> # Returns: 2026-01-23 00:00:00+05:30, 2026-01-23 23:59:59.999999+05:30

    Use for:
        - Daily reports
        - "Today's sales"
        - Filter by specific date
    """
    if target_date is None:
        target_date = get_local_now().date()

    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())

    start = SL_TIMEZONE.localize(start)
    end = SL_TIMEZONE.localize(end)

    return start, end


def get_month_range(year, month):
    """
    Get start and end datetime for a specific month.

    Args:
        year: Year (int)
        month: Month (1-12)

    Returns:
        tuple: (start_datetime, end_datetime) in SL timezone

    Example:
        >>> start, end = get_month_range(2026, 1)
        >>> # Returns: 2026-01-01 00:00:00+05:30, 2026-01-31 23:59:59.999999+05:30

    Use for:
        - Monthly reports
        - "This month's sales"
        - Month-based analytics
    """
    first_day = date(year, month, 1)
    last_day_num = monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)

    start = datetime.combine(first_day, datetime.min.time())
    end = datetime.combine(last_day, datetime.max.time())

    start = SL_TIMEZONE.localize(start)
    end = SL_TIMEZONE.localize(end)

    return start, end


def get_year_range(year, fiscal=False):
    """
    Get start and end datetime for a specific year.

    Args:
        year: Year (int)
        fiscal: If True, use fiscal year (April-March)

    Returns:
        tuple: (start_datetime, end_datetime) in SL timezone

    Sri Lankan Fiscal Year: April 1 to March 31

    Examples:
        >>> # Calendar year
        >>> start, end = get_year_range(2026)
        >>> # Returns: 2026-01-01 to 2026-12-31

        >>> # Fiscal year
        >>> start, end = get_year_range(2026, fiscal=True)
        >>> # Returns: 2026-04-01 to 2027-03-31
    """
    if fiscal:
        # Fiscal year: April to March
        start_date = date(year, 4, 1)
        end_date = date(year + 1, 3, 31)
    else:
        # Calendar year: January to December
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    start = datetime.combine(start_date, datetime.min.time())
    end = datetime.combine(end_date, datetime.max.time())

    start = SL_TIMEZONE.localize(start)
    end = SL_TIMEZONE.localize(end)

    return start, end


def format_date(dt):
    """
    Format date in Sri Lankan format (DD/MM/YYYY).

    Args:
        dt: date or datetime object

    Returns:
        str: Formatted date string

    Example:
        >>> dt = date(2026, 1, 23)
        >>> format_date(dt)
        '23/01/2026'
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    return dt.strftime('%d/%m/%Y')


def format_datetime(dt, show_seconds=False):
    """
    Format datetime in Sri Lankan format.

    Args:
        dt: datetime object
        show_seconds: Include seconds (default False)

    Returns:
        str: Formatted datetime string

    Examples:
        >>> dt = datetime(2026, 1, 23, 14, 30)
        >>> format_datetime(dt)
        '23/01/2026 14:30'

        >>> format_datetime(dt, show_seconds=True)
        '23/01/2026 14:30:00'
    """
    if show_seconds:
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    return dt.strftime('%d/%m/%Y %H:%M')
