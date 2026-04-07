"""
Comprehensive tests for apps.core.datetime module.

Tests cover:
    - Timezone constants and conversions
    - Date range helpers
    - Month range helpers
    - Year range (calendar and fiscal) helpers
    - Date/datetime formatting (DD/MM/YYYY)
    - Import validation

Target: 80+ tests
"""

import pytest
import pytz
from datetime import datetime, date, time, timedelta
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Timezone tests
# ---------------------------------------------------------------------------

class TestSLTimezone:
    """Tests for the SL_TIMEZONE constant."""

    def test_sl_timezone_name(self):
        from apps.core.datetime.timezone import SL_TIMEZONE
        assert SL_TIMEZONE.zone == 'Asia/Colombo'

    def test_sl_timezone_is_pytz_timezone(self):
        from apps.core.datetime.timezone import SL_TIMEZONE
        assert isinstance(SL_TIMEZONE, pytz.tzinfo.BaseTzInfo)

    def test_utc_offset_is_530(self):
        from apps.core.datetime.timezone import SL_TIMEZONE
        dt = datetime(2026, 6, 15, 12, 0, 0)
        localized = SL_TIMEZONE.localize(dt)
        offset = localized.utcoffset()
        assert offset == timedelta(hours=5, minutes=30)

    def test_utc_offset_same_in_january(self):
        """No DST — offset is the same in January."""
        from apps.core.datetime.timezone import SL_TIMEZONE
        dt = datetime(2026, 1, 15, 12, 0, 0)
        localized = SL_TIMEZONE.localize(dt)
        offset = localized.utcoffset()
        assert offset == timedelta(hours=5, minutes=30)

    def test_utc_offset_same_in_july(self):
        """No DST — offset is the same in July."""
        from apps.core.datetime.timezone import SL_TIMEZONE
        dt = datetime(2026, 7, 15, 12, 0, 0)
        localized = SL_TIMEZONE.localize(dt)
        offset = localized.utcoffset()
        assert offset == timedelta(hours=5, minutes=30)


class TestGetLocalNow:
    """Tests for get_local_now()."""

    def test_get_local_now_returns_datetime(self):
        from apps.core.datetime.timezone import get_local_now
        result = get_local_now()
        assert isinstance(result, datetime)

    def test_get_local_now_has_timezone(self):
        from apps.core.datetime.timezone import get_local_now
        result = get_local_now()
        assert result.tzinfo is not None

    def test_get_local_now_is_sl_timezone(self):
        from apps.core.datetime.timezone import get_local_now, SL_TIMEZONE
        result = get_local_now()
        # The tzname should match Asia/Colombo's tzname
        expected_offset = timedelta(hours=5, minutes=30)
        assert result.utcoffset() == expected_offset

    @patch('apps.core.datetime.timezone.django_tz')
    def test_get_local_now_calls_django_now(self, mock_tz):
        from apps.core.datetime.timezone import get_local_now, SL_TIMEZONE
        fixed_utc = pytz.UTC.localize(datetime(2026, 1, 23, 9, 0, 0))
        mock_tz.now.return_value = fixed_utc
        result = get_local_now()
        mock_tz.now.assert_called_once()
        assert result.hour == 14
        assert result.minute == 30

    @patch('apps.core.datetime.timezone.django_tz')
    def test_get_local_now_specific_date(self, mock_tz):
        from apps.core.datetime.timezone import get_local_now
        fixed_utc = pytz.UTC.localize(datetime(2026, 6, 15, 0, 0, 0))
        mock_tz.now.return_value = fixed_utc
        result = get_local_now()
        assert result.day == 15
        assert result.month == 6
        assert result.hour == 5
        assert result.minute == 30


class TestConvertToUTC:
    """Tests for convert_to_utc()."""

    def test_convert_to_utc_naive_datetime(self):
        from apps.core.datetime.timezone import convert_to_utc
        naive = datetime(2026, 1, 23, 14, 30, 0)
        result = convert_to_utc(naive)
        assert result.tzinfo is not None
        assert result.utcoffset() == timedelta(0)
        assert result.hour == 9
        assert result.minute == 0

    def test_convert_to_utc_aware_datetime(self):
        from apps.core.datetime.timezone import convert_to_utc, SL_TIMEZONE
        aware = SL_TIMEZONE.localize(datetime(2026, 1, 23, 14, 30, 0))
        result = convert_to_utc(aware)
        assert result.utcoffset() == timedelta(0)
        assert result.hour == 9
        assert result.minute == 0

    def test_convert_to_utc_already_utc(self):
        from apps.core.datetime.timezone import convert_to_utc
        utc_dt = pytz.UTC.localize(datetime(2026, 1, 23, 9, 0, 0))
        result = convert_to_utc(utc_dt)
        assert result.hour == 9
        assert result.minute == 0

    def test_convert_to_utc_specific_values(self):
        from apps.core.datetime.timezone import convert_to_utc
        naive = datetime(2026, 1, 23, 14, 30, 0)
        result = convert_to_utc(naive)
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 23
        assert result.hour == 9
        assert result.minute == 0

    def test_convert_to_utc_midnight(self):
        """Midnight SL → 18:30 previous day UTC."""
        from apps.core.datetime.timezone import convert_to_utc
        naive = datetime(2026, 1, 23, 0, 0, 0)
        result = convert_to_utc(naive)
        assert result.day == 22
        assert result.hour == 18
        assert result.minute == 30

    def test_convert_to_utc_end_of_day(self):
        from apps.core.datetime.timezone import convert_to_utc
        naive = datetime(2026, 1, 23, 23, 59, 59)
        result = convert_to_utc(naive)
        assert result.day == 23
        assert result.hour == 18
        assert result.minute == 29

    def test_convert_to_utc_preserves_date_for_afternoon(self):
        from apps.core.datetime.timezone import convert_to_utc
        naive = datetime(2026, 6, 15, 12, 0, 0)
        result = convert_to_utc(naive)
        assert result.day == 15
        assert result.hour == 6
        assert result.minute == 30

    @pytest.mark.parametrize(
        "sl_hour,sl_min,utc_hour,utc_min,utc_day_offset",
        [
            (0, 0, 18, 30, -1),
            (5, 30, 0, 0, 0),
            (12, 0, 6, 30, 0),
            (14, 30, 9, 0, 0),
            (18, 0, 12, 30, 0),
            (23, 59, 18, 29, 0),
        ],
    )
    def test_convert_to_utc_various(self, sl_hour, sl_min, utc_hour, utc_min, utc_day_offset):
        from apps.core.datetime.timezone import convert_to_utc
        naive = datetime(2026, 1, 15, sl_hour, sl_min, 0)
        result = convert_to_utc(naive)
        assert result.hour == utc_hour
        assert result.minute == utc_min
        expected_day = 15 + utc_day_offset
        assert result.day == expected_day


class TestConvertToLocal:
    """Tests for convert_to_local()."""

    def test_convert_to_local_naive_datetime(self):
        """Naive datetime assumed UTC, adds +5:30."""
        from apps.core.datetime.timezone import convert_to_local
        naive = datetime(2026, 1, 23, 9, 0, 0)
        result = convert_to_local(naive)
        assert result.utcoffset() == timedelta(hours=5, minutes=30)
        assert result.hour == 14
        assert result.minute == 30

    def test_convert_to_local_aware_utc(self):
        from apps.core.datetime.timezone import convert_to_local
        utc_dt = pytz.UTC.localize(datetime(2026, 1, 23, 9, 0, 0))
        result = convert_to_local(utc_dt)
        assert result.hour == 14
        assert result.minute == 30

    def test_convert_to_local_already_local(self):
        from apps.core.datetime.timezone import convert_to_local, SL_TIMEZONE
        sl_dt = SL_TIMEZONE.localize(datetime(2026, 1, 23, 14, 30, 0))
        result = convert_to_local(sl_dt)
        assert result.hour == 14
        assert result.minute == 30

    def test_convert_to_local_specific_values(self):
        from apps.core.datetime.timezone import convert_to_local
        utc_dt = pytz.UTC.localize(datetime(2026, 1, 23, 9, 0, 0))
        result = convert_to_local(utc_dt)
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 23
        assert result.hour == 14
        assert result.minute == 30

    def test_convert_to_local_midnight(self):
        """Midnight UTC → 05:30 SL."""
        from apps.core.datetime.timezone import convert_to_local
        utc_dt = pytz.UTC.localize(datetime(2026, 1, 23, 0, 0, 0))
        result = convert_to_local(utc_dt)
        assert result.hour == 5
        assert result.minute == 30

    def test_convert_to_local_crosses_day(self):
        """UTC 20:00 → SL 01:30 next day."""
        from apps.core.datetime.timezone import convert_to_local
        utc_dt = pytz.UTC.localize(datetime(2026, 1, 23, 20, 0, 0))
        result = convert_to_local(utc_dt)
        assert result.day == 24
        assert result.hour == 1
        assert result.minute == 30

    def test_convert_to_local_has_correct_offset(self):
        from apps.core.datetime.timezone import convert_to_local
        utc_dt = pytz.UTC.localize(datetime(2026, 1, 23, 12, 0, 0))
        result = convert_to_local(utc_dt)
        assert result.utcoffset() == timedelta(hours=5, minutes=30)

    @pytest.mark.parametrize(
        "utc_hour,utc_min,sl_hour,sl_min,sl_day_offset",
        [
            (0, 0, 5, 30, 0),
            (6, 30, 12, 0, 0),
            (9, 0, 14, 30, 0),
            (12, 30, 18, 0, 0),
            (18, 30, 0, 0, 1),
            (20, 0, 1, 30, 1),
        ],
    )
    def test_convert_to_local_various(self, utc_hour, utc_min, sl_hour, sl_min, sl_day_offset):
        from apps.core.datetime.timezone import convert_to_local
        utc_dt = pytz.UTC.localize(datetime(2026, 1, 15, utc_hour, utc_min, 0))
        result = convert_to_local(utc_dt)
        assert result.hour == sl_hour
        assert result.minute == sl_min
        expected_day = 15 + sl_day_offset
        assert result.day == expected_day


class TestRoundtrip:
    """Tests for UTC ↔ local roundtrip conversions."""

    def test_utc_to_local_roundtrip(self):
        from apps.core.datetime.timezone import convert_to_utc, convert_to_local
        original = pytz.UTC.localize(datetime(2026, 1, 23, 9, 0, 0))
        local = convert_to_local(original)
        back_to_utc = convert_to_utc(local)
        assert back_to_utc.hour == original.hour
        assert back_to_utc.minute == original.minute
        assert back_to_utc.day == original.day

    def test_local_to_utc_roundtrip(self):
        from apps.core.datetime.timezone import convert_to_utc, convert_to_local, SL_TIMEZONE
        original = SL_TIMEZONE.localize(datetime(2026, 1, 23, 14, 30, 0))
        utc = convert_to_utc(original)
        back_to_local = convert_to_local(utc)
        assert back_to_local.hour == original.hour
        assert back_to_local.minute == original.minute
        assert back_to_local.day == original.day

    def test_roundtrip_preserves_timestamp(self):
        from apps.core.datetime.timezone import convert_to_utc, convert_to_local
        original = pytz.UTC.localize(datetime(2026, 7, 4, 15, 45, 30))
        local = convert_to_local(original)
        back = convert_to_utc(local)
        # Timestamps should be identical
        assert abs((back - original).total_seconds()) < 1

    def test_roundtrip_naive_sl(self):
        """Naive SL → UTC → local should keep same hour/minute."""
        from apps.core.datetime.timezone import convert_to_utc, convert_to_local
        naive_sl = datetime(2026, 3, 10, 8, 15, 0)
        utc = convert_to_utc(naive_sl)  # assumes SL
        local = convert_to_local(utc)
        assert local.hour == 8
        assert local.minute == 15


# ---------------------------------------------------------------------------
# Date range tests
# ---------------------------------------------------------------------------

class TestGetDateRange:
    """Tests for get_date_range()."""

    def test_get_date_range_specific_date(self):
        from apps.core.datetime.date_utils import get_date_range
        start, end = get_date_range(date(2026, 1, 23))
        assert start.date() == date(2026, 1, 23)
        assert end.date() == date(2026, 1, 23)

    def test_get_date_range_start_is_midnight(self):
        from apps.core.datetime.date_utils import get_date_range
        start, _ = get_date_range(date(2026, 1, 23))
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0
        assert start.microsecond == 0

    def test_get_date_range_end_is_end_of_day(self):
        from apps.core.datetime.date_utils import get_date_range
        _, end = get_date_range(date(2026, 1, 23))
        assert end.hour == 23
        assert end.minute == 59
        assert end.second == 59
        assert end.microsecond == 999999

    def test_get_date_range_has_timezone(self):
        from apps.core.datetime.date_utils import get_date_range
        start, end = get_date_range(date(2026, 1, 23))
        assert start.tzinfo is not None
        assert end.tzinfo is not None

    def test_get_date_range_timezone_is_sl(self):
        from apps.core.datetime.date_utils import get_date_range
        start, end = get_date_range(date(2026, 1, 23))
        assert start.utcoffset() == timedelta(hours=5, minutes=30)
        assert end.utcoffset() == timedelta(hours=5, minutes=30)

    @patch('apps.core.datetime.date_utils.get_local_now')
    def test_get_date_range_default_today(self, mock_now):
        from apps.core.datetime.date_utils import get_date_range
        from apps.core.datetime.timezone import SL_TIMEZONE
        mock_now.return_value = SL_TIMEZONE.localize(datetime(2026, 3, 15, 10, 0, 0))
        start, end = get_date_range()
        assert start.date() == date(2026, 3, 15)
        assert end.date() == date(2026, 3, 15)

    def test_get_date_range_leap_day(self):
        from apps.core.datetime.date_utils import get_date_range
        start, end = get_date_range(date(2024, 2, 29))
        assert start.date() == date(2024, 2, 29)
        assert end.date() == date(2024, 2, 29)

    def test_get_date_range_first_day_of_year(self):
        from apps.core.datetime.date_utils import get_date_range
        start, end = get_date_range(date(2026, 1, 1))
        assert start.date() == date(2026, 1, 1)

    def test_get_date_range_last_day_of_year(self):
        from apps.core.datetime.date_utils import get_date_range
        start, end = get_date_range(date(2026, 12, 31))
        assert end.date() == date(2026, 12, 31)


# ---------------------------------------------------------------------------
# Month range tests
# ---------------------------------------------------------------------------

class TestGetMonthRange:
    """Tests for get_month_range()."""

    def test_get_month_range_january(self):
        from apps.core.datetime.date_utils import get_month_range
        start, end = get_month_range(2026, 1)
        assert start.date() == date(2026, 1, 1)
        assert end.date() == date(2026, 1, 31)

    def test_get_month_range_february_regular(self):
        from apps.core.datetime.date_utils import get_month_range
        start, end = get_month_range(2026, 2)
        assert start.date() == date(2026, 2, 1)
        assert end.date() == date(2026, 2, 28)

    def test_get_month_range_february_leap(self):
        from apps.core.datetime.date_utils import get_month_range
        start, end = get_month_range(2024, 2)
        assert start.date() == date(2024, 2, 1)
        assert end.date() == date(2024, 2, 29)

    def test_get_month_range_april_30days(self):
        from apps.core.datetime.date_utils import get_month_range
        start, end = get_month_range(2026, 4)
        assert start.date() == date(2026, 4, 1)
        assert end.date() == date(2026, 4, 30)

    def test_get_month_range_december(self):
        from apps.core.datetime.date_utils import get_month_range
        start, end = get_month_range(2026, 12)
        assert start.date() == date(2026, 12, 1)
        assert end.date() == date(2026, 12, 31)

    def test_get_month_range_has_timezone(self):
        from apps.core.datetime.date_utils import get_month_range
        start, end = get_month_range(2026, 5)
        assert start.tzinfo is not None
        assert end.tzinfo is not None

    def test_get_month_range_start_is_midnight(self):
        from apps.core.datetime.date_utils import get_month_range
        start, _ = get_month_range(2026, 6)
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0

    def test_get_month_range_end_is_end_of_day(self):
        from apps.core.datetime.date_utils import get_month_range
        _, end = get_month_range(2026, 6)
        assert end.hour == 23
        assert end.minute == 59
        assert end.second == 59
        assert end.microsecond == 999999

    @pytest.mark.parametrize(
        "month,last_day",
        [
            (1, 31),
            (2, 28),
            (3, 31),
            (4, 30),
            (5, 31),
            (6, 30),
            (7, 31),
            (8, 31),
            (9, 30),
            (10, 31),
            (11, 30),
            (12, 31),
        ],
    )
    def test_get_month_range_all_months(self, month, last_day):
        from apps.core.datetime.date_utils import get_month_range
        start, end = get_month_range(2026, month)
        assert start.day == 1
        assert end.day == last_day


# ---------------------------------------------------------------------------
# Year range tests
# ---------------------------------------------------------------------------

class TestGetYearRange:
    """Tests for get_year_range()."""

    def test_get_year_range_calendar(self):
        from apps.core.datetime.date_utils import get_year_range
        start, end = get_year_range(2026)
        assert start.date() == date(2026, 1, 1)
        assert end.date() == date(2026, 12, 31)

    def test_get_year_range_fiscal(self):
        from apps.core.datetime.date_utils import get_year_range
        start, end = get_year_range(2026, fiscal=True)
        assert start.date() == date(2026, 4, 1)
        assert end.date() == date(2027, 3, 31)

    def test_get_year_range_calendar_has_timezone(self):
        from apps.core.datetime.date_utils import get_year_range
        start, end = get_year_range(2026)
        assert start.tzinfo is not None
        assert end.tzinfo is not None

    def test_get_year_range_fiscal_has_timezone(self):
        from apps.core.datetime.date_utils import get_year_range
        start, end = get_year_range(2026, fiscal=True)
        assert start.tzinfo is not None
        assert end.tzinfo is not None

    def test_get_year_range_calendar_start(self):
        from apps.core.datetime.date_utils import get_year_range
        start, _ = get_year_range(2026)
        assert start.month == 1
        assert start.day == 1
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0

    def test_get_year_range_calendar_end(self):
        from apps.core.datetime.date_utils import get_year_range
        _, end = get_year_range(2026)
        assert end.month == 12
        assert end.day == 31
        assert end.hour == 23
        assert end.minute == 59
        assert end.second == 59
        assert end.microsecond == 999999

    def test_get_year_range_fiscal_start(self):
        from apps.core.datetime.date_utils import get_year_range
        start, _ = get_year_range(2026, fiscal=True)
        assert start.month == 4
        assert start.day == 1
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0

    def test_get_year_range_fiscal_end(self):
        from apps.core.datetime.date_utils import get_year_range
        _, end = get_year_range(2026, fiscal=True)
        assert end.year == 2027
        assert end.month == 3
        assert end.day == 31
        assert end.hour == 23
        assert end.minute == 59
        assert end.second == 59
        assert end.microsecond == 999999

    def test_get_year_range_leap_year(self):
        from apps.core.datetime.date_utils import get_year_range
        start, end = get_year_range(2024)
        assert start.date() == date(2024, 1, 1)
        assert end.date() == date(2024, 12, 31)
        # 2024 is a leap year — 366 days
        delta = end.date() - start.date()
        assert delta.days == 365  # Dec 31 - Jan 1 = 365, meaning 366 days inclusive

    def test_get_year_range_fiscal_different_year(self):
        from apps.core.datetime.date_utils import get_year_range
        start, end = get_year_range(2025, fiscal=True)
        assert start.date() == date(2025, 4, 1)
        assert end.date() == date(2026, 3, 31)

    def test_get_year_range_calendar_offset_is_sl(self):
        from apps.core.datetime.date_utils import get_year_range
        start, end = get_year_range(2026)
        assert start.utcoffset() == timedelta(hours=5, minutes=30)
        assert end.utcoffset() == timedelta(hours=5, minutes=30)


# ---------------------------------------------------------------------------
# Format date tests
# ---------------------------------------------------------------------------

class TestFormatDate:
    """Tests for format_date()."""

    def test_format_date_basic(self):
        from apps.core.datetime.date_utils import format_date
        assert format_date(date(2026, 1, 23)) == '23/01/2026'

    def test_format_date_with_datetime(self):
        from apps.core.datetime.date_utils import format_date
        assert format_date(datetime(2026, 1, 23, 14, 30)) == '23/01/2026'

    def test_format_date_single_digit_day(self):
        from apps.core.datetime.date_utils import format_date
        assert format_date(date(2026, 1, 5)) == '05/01/2026'

    def test_format_date_single_digit_month(self):
        from apps.core.datetime.date_utils import format_date
        assert format_date(date(2026, 3, 15)) == '15/03/2026'

    def test_format_date_december(self):
        from apps.core.datetime.date_utils import format_date
        assert format_date(date(2026, 12, 25)) == '25/12/2026'

    def test_format_date_leap_day(self):
        from apps.core.datetime.date_utils import format_date
        assert format_date(date(2024, 2, 29)) == '29/02/2024'

    def test_format_date_first_day_of_year(self):
        from apps.core.datetime.date_utils import format_date
        assert format_date(date(2026, 1, 1)) == '01/01/2026'

    def test_format_date_last_day_of_year(self):
        from apps.core.datetime.date_utils import format_date
        assert format_date(date(2026, 12, 31)) == '31/12/2026'

    @pytest.mark.parametrize(
        "dt,expected",
        [
            (date(2026, 1, 1), '01/01/2026'),
            (date(2026, 2, 14), '14/02/2026'),
            (date(2026, 4, 14), '14/04/2026'),  # Sinhala/Tamil New Year
            (date(2026, 5, 1), '01/05/2026'),
            (date(2026, 10, 31), '31/10/2026'),
            (date(2026, 11, 9), '09/11/2026'),
            (date(2026, 12, 25), '25/12/2026'),
        ],
    )
    def test_format_date_various(self, dt, expected):
        from apps.core.datetime.date_utils import format_date
        assert format_date(dt) == expected


# ---------------------------------------------------------------------------
# Format datetime tests
# ---------------------------------------------------------------------------

class TestFormatDatetime:
    """Tests for format_datetime()."""

    def test_format_datetime_basic(self):
        from apps.core.datetime.date_utils import format_datetime
        dt = datetime(2026, 1, 23, 14, 30)
        assert format_datetime(dt) == '23/01/2026 14:30'

    def test_format_datetime_with_seconds(self):
        from apps.core.datetime.date_utils import format_datetime
        dt = datetime(2026, 1, 23, 14, 30, 0)
        assert format_datetime(dt, show_seconds=True) == '23/01/2026 14:30:00'

    def test_format_datetime_midnight(self):
        from apps.core.datetime.date_utils import format_datetime
        dt = datetime(2026, 1, 23, 0, 0)
        assert format_datetime(dt) == '23/01/2026 00:00'

    def test_format_datetime_midnight_with_seconds(self):
        from apps.core.datetime.date_utils import format_datetime
        dt = datetime(2026, 1, 23, 0, 0, 0)
        assert format_datetime(dt, show_seconds=True) == '23/01/2026 00:00:00'

    def test_format_datetime_end_of_day(self):
        from apps.core.datetime.date_utils import format_datetime
        dt = datetime(2026, 1, 23, 23, 59)
        assert format_datetime(dt) == '23/01/2026 23:59'

    def test_format_datetime_end_of_day_with_seconds(self):
        from apps.core.datetime.date_utils import format_datetime
        dt = datetime(2026, 1, 23, 23, 59, 59)
        assert format_datetime(dt, show_seconds=True) == '23/01/2026 23:59:59'

    def test_format_datetime_noon(self):
        from apps.core.datetime.date_utils import format_datetime
        dt = datetime(2026, 6, 15, 12, 0, 0)
        assert format_datetime(dt) == '15/06/2026 12:00'

    def test_format_datetime_single_digit_hour(self):
        from apps.core.datetime.date_utils import format_datetime
        dt = datetime(2026, 1, 5, 8, 5, 0)
        assert format_datetime(dt) == '05/01/2026 08:05'

    @pytest.mark.parametrize(
        "dt,show_seconds,expected",
        [
            (datetime(2026, 1, 1, 0, 0, 0), False, '01/01/2026 00:00'),
            (datetime(2026, 1, 1, 0, 0, 0), True, '01/01/2026 00:00:00'),
            (datetime(2026, 6, 15, 9, 15, 30), False, '15/06/2026 09:15'),
            (datetime(2026, 6, 15, 9, 15, 30), True, '15/06/2026 09:15:30'),
            (datetime(2026, 12, 31, 23, 59, 59), False, '31/12/2026 23:59'),
            (datetime(2026, 12, 31, 23, 59, 59), True, '31/12/2026 23:59:59'),
            (datetime(2026, 4, 14, 6, 0, 0), False, '14/04/2026 06:00'),
        ],
    )
    def test_format_datetime_various(self, dt, show_seconds, expected):
        from apps.core.datetime.date_utils import format_datetime
        assert format_datetime(dt, show_seconds=show_seconds) == expected


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------

class TestImports:
    """Tests for package-level imports and __all__."""

    def test_imports_from_package_sl_timezone(self):
        from apps.core.datetime import SL_TIMEZONE
        assert SL_TIMEZONE is not None

    def test_imports_from_package_get_local_now(self):
        from apps.core.datetime import get_local_now
        assert callable(get_local_now)

    def test_imports_from_package_convert_to_utc(self):
        from apps.core.datetime import convert_to_utc
        assert callable(convert_to_utc)

    def test_imports_from_package_convert_to_local(self):
        from apps.core.datetime import convert_to_local
        assert callable(convert_to_local)

    def test_imports_from_package_get_date_range(self):
        from apps.core.datetime import get_date_range
        assert callable(get_date_range)

    def test_imports_from_package_get_month_range(self):
        from apps.core.datetime import get_month_range
        assert callable(get_month_range)

    def test_imports_from_package_get_year_range(self):
        from apps.core.datetime import get_year_range
        assert callable(get_year_range)

    def test_imports_from_package_format_date(self):
        from apps.core.datetime import format_date
        assert callable(format_date)

    def test_imports_from_package_format_datetime(self):
        from apps.core.datetime import format_datetime
        assert callable(format_datetime)

    def test_all_exports(self):
        import apps.core.datetime as dt_module
        expected = [
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
        for name in expected:
            assert name in dt_module.__all__, f"{name} not found in __all__"

    def test_all_exports_length(self):
        import apps.core.datetime as dt_module
        assert len(dt_module.__all__) == 9

    def test_version(self):
        import apps.core.datetime as dt_module
        assert dt_module.__version__ == '1.0.0'
