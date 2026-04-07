"""
Integration tests for core utilities.

Verifies all utility modules work together correctly.
SubPhase-12, Group F, Task 93.

These tests do NOT require database access — mocks are used where needed.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock

import pytz


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SL_TZ = pytz.timezone("Asia/Colombo")
UTC = pytz.UTC


# ===========================================================================
# 1. Cross-Module Import Tests
# ===========================================================================


class TestCrossModuleImports:
    """Verify every public symbol can be imported from all 5 modules."""

    # -- Pagination --

    def test_import_standard_pagination(self):
        from apps.core.pagination import StandardPagination

        assert StandardPagination is not None

    def test_import_cursor_pagination(self):
        from apps.core.pagination import LCCCursorPagination

        assert LCCCursorPagination is not None

    def test_import_limit_offset_pagination(self):
        from apps.core.pagination import LCCLimitOffsetPagination

        assert LCCLimitOffsetPagination is not None

    def test_import_no_pagination(self):
        from apps.core.pagination import NoPagination

        assert NoPagination is not None

    # -- Filters --

    def test_import_all_filter_backends(self):
        from apps.core.filters import (
            TenantFilterBackend,
            DateRangeFilterBackend,
            LCCSearchFilter,
            LCCOrderingFilter,
            IsActiveFilterBackend,
            CreatedByFilterBackend,
            ModifiedAtFilterBackend,
        )

        for cls in (
            TenantFilterBackend,
            DateRangeFilterBackend,
            LCCSearchFilter,
            LCCOrderingFilter,
            IsActiveFilterBackend,
            CreatedByFilterBackend,
            ModifiedAtFilterBackend,
        ):
            assert cls is not None

    def test_import_base_filterset(self):
        from apps.core.filters import BaseFilterSet

        assert BaseFilterSet is not None

    # -- Validators --

    def test_import_all_validators(self):
        from apps.core.validators import (
            LCCEmailValidator,
            LCCURLValidator,
            LCCSlugValidator,
            PositiveNumberValidator,
            DecimalValidator,
            PercentageValidator,
            FileSizeValidator,
            ImageDimensionValidator,
            FileExtensionValidator,
            JSONValidator,
            NoHTMLValidator,
            UniqueForTenantValidator,
        )

        for cls in (
            LCCEmailValidator,
            LCCURLValidator,
            LCCSlugValidator,
            PositiveNumberValidator,
            DecimalValidator,
            PercentageValidator,
            FileSizeValidator,
            ImageDimensionValidator,
            FileExtensionValidator,
            JSONValidator,
            NoHTMLValidator,
            UniqueForTenantValidator,
        ):
            assert cls is not None

    # -- DateTime --

    def test_import_all_datetime(self):
        from apps.core.datetime import (
            SL_TIMEZONE,
            get_local_now,
            convert_to_utc,
            convert_to_local,
            get_date_range,
            get_month_range,
            get_year_range,
            format_date,
            format_datetime,
        )

        assert SL_TIMEZONE is not None

    # -- Sri Lanka --

    def test_import_all_srilanka(self):
        from apps.core.srilanka import (
            format_lkr,
            parse_lkr,
            convert_currency,
            validate_sl_phone,
            format_sl_phone,
            normalize_sl_phone,
            validate_nic,
            parse_nic_dob,
            PROVINCES,
            DISTRICTS,
            get_province_by_code,
            get_province_choices,
            get_districts_by_province,
            get_district_by_code,
            get_district_choices,
        )

        assert len(PROVINCES) == 9
        assert len(DISTRICTS) == 25

    # -- __all__ completeness --

    def test_pagination_all_list(self):
        import apps.core.pagination as mod

        expected = {
            "StandardPagination",
            "LCCCursorPagination",
            "LCCLimitOffsetPagination",
            "NoPagination",
        }
        assert expected.issubset(set(mod.__all__))

    def test_filters_all_list(self):
        import apps.core.filters as mod

        expected = {
            "TenantFilterBackend",
            "DateRangeFilterBackend",
            "LCCSearchFilter",
            "LCCOrderingFilter",
            "IsActiveFilterBackend",
            "CreatedByFilterBackend",
            "ModifiedAtFilterBackend",
            "BaseFilterSet",
        }
        assert expected.issubset(set(mod.__all__))

    def test_validators_all_list(self):
        import apps.core.validators as mod

        expected = {
            "LCCEmailValidator",
            "LCCURLValidator",
            "LCCSlugValidator",
            "PositiveNumberValidator",
            "DecimalValidator",
            "PercentageValidator",
            "FileSizeValidator",
            "ImageDimensionValidator",
            "FileExtensionValidator",
            "JSONValidator",
            "NoHTMLValidator",
            "UniqueForTenantValidator",
        }
        assert expected.issubset(set(mod.__all__))

    def test_datetime_all_list(self):
        import apps.core.datetime as mod

        expected = {
            "SL_TIMEZONE",
            "get_local_now",
            "convert_to_utc",
            "convert_to_local",
            "get_date_range",
            "get_month_range",
            "get_year_range",
            "format_date",
            "format_datetime",
        }
        assert expected.issubset(set(mod.__all__))

    def test_srilanka_all_list(self):
        import apps.core.srilanka as mod

        expected = {
            "format_lkr",
            "parse_lkr",
            "convert_currency",
            "validate_sl_phone",
            "format_sl_phone",
            "normalize_sl_phone",
            "validate_nic",
            "parse_nic_dob",
            "PROVINCES",
            "DISTRICTS",
            "get_province_by_code",
            "get_province_choices",
            "get_districts_by_province",
            "get_district_by_code",
            "get_district_choices",
        }
        assert expected.issubset(set(mod.__all__))

    # -- Version attributes --

    def test_pagination_version(self):
        import apps.core.pagination as mod

        assert hasattr(mod, "__version__")
        assert mod.__version__ == "1.0.0"

    def test_filters_version(self):
        import apps.core.filters as mod

        assert hasattr(mod, "__version__")
        assert mod.__version__ == "1.0.0"

    def test_validators_version(self):
        import apps.core.validators as mod

        assert hasattr(mod, "__version__")
        assert mod.__version__ == "1.0.0"

    def test_datetime_version(self):
        import apps.core.datetime as mod

        assert hasattr(mod, "__version__")
        assert mod.__version__ == "1.0.0"

    def test_srilanka_version(self):
        import apps.core.srilanka as mod

        assert hasattr(mod, "__version__")
        assert mod.__version__ == "1.0.0"


# ===========================================================================
# 2. Currency + DateTime Integration
# ===========================================================================


class TestCurrencyDateTimeIntegration:
    """Test currency and datetime modules working together."""

    def test_format_lkr_for_daily_sales(self):
        """Simulate formatting daily sales with date context."""
        from apps.core.srilanka import format_lkr
        from apps.core.datetime import format_date

        sale_date = date(2026, 3, 11)
        amount = Decimal("15750.50")

        formatted_amount = format_lkr(amount)
        formatted_date = format_date(sale_date)

        assert formatted_amount == "Rs. 15,750.50"
        assert formatted_date == "11/03/2026"

    def test_monthly_sales_report(self):
        """Get month range and format currency totals."""
        from apps.core.srilanka import format_lkr
        from apps.core.datetime import get_month_range, format_date

        start, end = get_month_range(2026, 1)
        total = Decimal("2500000.00")

        report_start = format_date(start)
        report_end = format_date(end)
        report_total = format_lkr(total)

        assert report_start == "01/01/2026"
        assert report_end == "31/01/2026"
        assert report_total == "Rs. 2,500,000.00"

    def test_fiscal_year_report(self):
        """Fiscal year range with formatted dates and amounts."""
        from apps.core.srilanka import format_lkr
        from apps.core.datetime import get_year_range, format_date

        start, end = get_year_range(2025, fiscal=True)
        revenue = Decimal("125000000.00")

        assert format_date(start) == "01/04/2025"
        assert format_date(end) == "31/03/2026"
        assert format_lkr(revenue) == "Rs. 125,000,000.00"

    def test_currency_roundtrip_with_datetime(self):
        """Format, parse back, and combine with a date."""
        from apps.core.srilanka import format_lkr, parse_lkr
        from apps.core.datetime import format_datetime

        original = Decimal("42350.75")
        formatted = format_lkr(original)
        parsed = parse_lkr(formatted)
        assert parsed == original

        dt = datetime(2026, 3, 11, 14, 30)
        assert format_datetime(dt) == "11/03/2026 14:30"

    def test_get_date_range_and_format_both_bounds(self):
        """Get date range boundaries and format them as strings."""
        from apps.core.datetime import get_date_range, format_datetime

        start, end = get_date_range(date(2026, 6, 15))

        start_str = format_datetime(start)
        end_str = format_datetime(end)

        assert start_str == "15/06/2026 00:00"
        assert end_str == "15/06/2026 23:59"

    def test_format_lkr_zero_and_negative(self):
        """Currency formatting edge cases with date context."""
        from apps.core.srilanka import format_lkr
        from apps.core.datetime import format_date

        assert format_lkr(0) == "Rs. 0.00"
        assert format_lkr(-1500) == "Rs. -1,500.00"
        assert format_date(date(2026, 12, 31)) == "31/12/2026"

    def test_convert_currency_with_formatted_result(self):
        """Convert LKR to USD and format both."""
        from apps.core.srilanka import format_lkr, convert_currency

        lkr_amount = Decimal("30000")
        usd_amount = convert_currency(lkr_amount, "LKR", "USD", exchange_rate=0.0033)

        assert format_lkr(lkr_amount) == "Rs. 30,000.00"
        assert usd_amount == Decimal("99.0000")

    def test_parse_lkr_from_numeric(self):
        """Parse currency from numeric types."""
        from apps.core.srilanka import parse_lkr

        assert parse_lkr(1500) == Decimal("1500")
        assert parse_lkr(99.99) == Decimal("99.99")
        assert parse_lkr(Decimal("1234.56")) == Decimal("1234.56")


# ===========================================================================
# 3. Phone + NIC Integration
# ===========================================================================


class TestPhoneNICIntegration:
    """Test phone and NIC validation together — user registration workflow."""

    def test_validate_phone_and_nic_together(self):
        """Simulate user registration validating both phone and NIC."""
        from apps.core.srilanka import validate_sl_phone, validate_nic

        phone = "0712345678"
        nic = "881234567V"

        assert validate_sl_phone(phone) is True
        assert validate_nic(nic) is True

    def test_parse_nic_dob_and_format_date(self):
        """Parse DOB from NIC and format using datetime module."""
        from apps.core.srilanka import parse_nic_dob
        from apps.core.datetime import format_date

        dob, gender = parse_nic_dob("881234567V")
        formatted = format_date(dob)

        assert isinstance(dob, date)
        assert isinstance(formatted, str)
        assert "/" in formatted  # DD/MM/YYYY
        assert gender in ("M", "F")

    def test_normalize_phone_and_validate_nic_workflow(self):
        """Normalize phone + validate NIC in same workflow."""
        from apps.core.srilanka import normalize_sl_phone, validate_nic

        normalized = normalize_sl_phone("0771234567")
        assert normalized == "+94771234567"

        assert validate_nic("200012345678") is True

    def test_format_phone_and_parse_nic(self):
        """Format phone and parse NIC in registration context."""
        from apps.core.srilanka import format_sl_phone, parse_nic_dob

        phone = format_sl_phone("0751234567")
        assert phone == "+94 75 123 4567"

        dob, gender = parse_nic_dob("198812345678")
        assert isinstance(dob, date)
        assert gender in ("M", "F")

    def test_invalid_phone_with_valid_nic(self):
        """One valid, one invalid — partial registration failure."""
        from apps.core.srilanka import validate_sl_phone, validate_nic

        assert validate_sl_phone("1234") is False
        assert validate_nic("881234567V") is True

    def test_female_nic_and_phone(self):
        """Validate a female NIC (days > 500) with phone."""
        from apps.core.srilanka import validate_nic, parse_nic_dob, validate_sl_phone

        nic = "886234567V"
        assert validate_nic(nic) is True

        dob, gender = parse_nic_dob(nic)
        assert gender == "F"

        assert validate_sl_phone("0781234567") is True


# ===========================================================================
# 4. Provinces & Districts Integration
# ===========================================================================


class TestProvincesDistrictsIntegration:
    """Test province-district relationship integrity."""

    def test_get_province_then_districts(self):
        """Look up province, then get its districts."""
        from apps.core.srilanka import get_province_by_code, get_districts_by_province

        province = get_province_by_code("WP")
        assert province is not None
        assert province["name"] == "Western Province"

        districts = get_districts_by_province("WP")
        assert len(districts) == 3
        names = {d["name"] for d in districts}
        assert names == {"Colombo", "Gampaha", "Kalutara"}

    def test_all_districts_link_to_valid_provinces(self):
        """Every district's province code matches a valid province."""
        from apps.core.srilanka import PROVINCES, DISTRICTS, get_province_by_code

        province_codes = {p["code"] for p in PROVINCES}
        for district in DISTRICTS:
            assert district["province"] in province_codes, (
                f"District {district['name']} has unknown province {district['province']}"
            )

    def test_district_choices_for_all_provinces(self):
        """Get district choices for each of the 9 provinces."""
        from apps.core.srilanka import PROVINCES, get_district_choices

        for province in PROVINCES:
            choices = get_district_choices(province["code"])
            assert len(choices) >= 2, (
                f"Province {province['name']} should have at least 2 districts"
            )
            for code, name in choices:
                assert isinstance(code, str)
                assert isinstance(name, str)

    def test_province_choices_returns_tuples(self):
        """Province choices suitable for Django model/form field."""
        from apps.core.srilanka import get_province_choices

        choices = get_province_choices()
        assert len(choices) == 9
        for code, name in choices:
            assert isinstance(code, str)
            assert "Province" in name or code in ("UP", "SG")

    def test_district_by_code_lookup(self):
        """Look up specific districts by code."""
        from apps.core.srilanka import get_district_by_code

        colombo = get_district_by_code("CO")
        assert colombo is not None
        assert colombo["name"] == "Colombo"
        assert colombo["province"] == "WP"
        assert "sinhala" in colombo

    def test_all_districts_total_25(self):
        """Confirm all 25 districts are present."""
        from apps.core.srilanka import get_district_choices

        all_districts = get_district_choices()
        assert len(all_districts) == 25


# ===========================================================================
# 5. DateTime Formatting Integration
# ===========================================================================


class TestDateTimeFormattingIntegration:
    """Test datetime functions chained together."""

    @patch("apps.core.datetime.timezone.django_tz")
    def test_get_local_now_and_format(self, mock_django_tz):
        """get_local_now → format_date → DD/MM/YYYY."""
        from apps.core.datetime import get_local_now, format_date

        fixed_utc = datetime(2026, 3, 11, 9, 0, tzinfo=UTC)
        mock_django_tz.now.return_value = fixed_utc

        local_now = get_local_now()
        formatted = format_date(local_now)

        assert formatted == "11/03/2026"

    def test_utc_to_local_roundtrip(self):
        """convert_to_utc → convert_to_local gives equivalent time."""
        from apps.core.datetime import convert_to_utc, convert_to_local

        original = SL_TZ.localize(datetime(2026, 6, 15, 10, 30))
        utc = convert_to_utc(original)
        back = convert_to_local(utc)

        assert back.year == 2026
        assert back.month == 6
        assert back.day == 15
        assert back.hour == 10
        assert back.minute == 30

    def test_date_range_format_start_end(self):
        """get_date_range → format both start and end."""
        from apps.core.datetime import get_date_range, format_date

        start, end = get_date_range(date(2026, 1, 15))
        assert format_date(start) == "15/01/2026"
        assert format_date(end) == "15/01/2026"

    def test_month_range_format(self):
        """get_month_range → format boundary dates."""
        from apps.core.datetime import get_month_range, format_date

        start, end = get_month_range(2026, 2)
        assert format_date(start) == "01/02/2026"
        assert format_date(end) == "28/02/2026"

    def test_fiscal_year_starts_april(self):
        """get_year_range(fiscal=True) → April start."""
        from apps.core.datetime import get_year_range, format_date

        start, end = get_year_range(2025, fiscal=True)
        assert format_date(start) == "01/04/2025"
        assert format_date(end) == "31/03/2026"

    def test_calendar_year_range(self):
        """get_year_range → Jan-Dec."""
        from apps.core.datetime import get_year_range, format_date

        start, end = get_year_range(2026)
        assert format_date(start) == "01/01/2026"
        assert format_date(end) == "31/12/2026"

    def test_format_datetime_with_seconds(self):
        """format_datetime with show_seconds=True."""
        from apps.core.datetime import format_datetime

        dt = datetime(2026, 7, 4, 15, 30, 45)
        assert format_datetime(dt, show_seconds=True) == "04/07/2026 15:30:45"

    def test_naive_datetime_handling(self):
        """Naive datetimes are assumed SL for to_utc, UTC for to_local."""
        from apps.core.datetime import convert_to_utc, convert_to_local

        naive_sl = datetime(2026, 1, 1, 12, 0, 0)
        utc_result = convert_to_utc(naive_sl)
        assert utc_result.tzinfo is not None
        assert utc_result.hour == 6  # 12:00 SL = 06:30 UTC
        assert utc_result.minute == 30

        naive_utc = datetime(2026, 1, 1, 6, 30, 0)
        local_result = convert_to_local(naive_utc)
        assert local_result.tzinfo is not None
        assert local_result.hour == 12
        assert local_result.minute == 0


# ===========================================================================
# 6. Validator Integration
# ===========================================================================


class TestValidatorIntegration:
    """Test validators with other modules."""

    def test_validate_email_phone_nic_together(self):
        """Full contact validation — email + phone + NIC."""
        from apps.core.validators import LCCEmailValidator
        from apps.core.srilanka import validate_sl_phone, validate_nic

        email_validator = LCCEmailValidator()
        email_validator("user@example.com")  # Should not raise

        assert validate_sl_phone("0712345678") is True
        assert validate_nic("881234567V") is True

    def test_positive_number_as_currency(self):
        """Validate positive number then format as LKR."""
        from apps.core.validators import PositiveNumberValidator
        from apps.core.srilanka import format_lkr

        validator = PositiveNumberValidator()
        validator(1500)  # Should not raise

        assert format_lkr(1500) == "Rs. 1,500.00"

    def test_decimal_validator_with_lkr(self):
        """Validate decimal precision then format."""
        from apps.core.validators import DecimalValidator
        from apps.core.srilanka import format_lkr

        validator = DecimalValidator(max_digits=10, decimal_places=2)
        validator("12345.67")  # Should not raise

        assert format_lkr(Decimal("12345.67")) == "Rs. 12,345.67"

    def test_percentage_validator_for_discount(self):
        """Validate percentage then compute discount on LKR amount."""
        from apps.core.validators import PercentageValidator
        from apps.core.srilanka import format_lkr

        validator = PercentageValidator()
        validator(15)  # 15% discount, should not raise

        price = Decimal("10000")
        discount = price * Decimal("15") / Decimal("100")
        final = price - discount

        assert format_lkr(final) == "Rs. 8,500.00"

    def test_slug_validator_with_province_codes(self):
        """Slug-style strings derived from province data."""
        from apps.core.validators import LCCSlugValidator
        from apps.core.srilanka import PROVINCES

        validator = LCCSlugValidator()

        # Province-based slugs
        for province in PROVINCES:
            slug = province["name"].lower().replace(" ", "-")
            if len(slug) >= 3:
                validator(slug)  # Should not raise

    def test_json_validator_with_product_data(self):
        """Validate a JSON string representing product metadata."""
        import json
        from apps.core.validators import JSONValidator
        from apps.core.srilanka import format_lkr

        validator = JSONValidator()
        product_json = json.dumps({
            "name": "Laptop",
            "price": "150000.00",
            "currency": "LKR",
        })
        validator(product_json)  # Should not raise

        data = json.loads(product_json)
        assert format_lkr(Decimal(data["price"])) == "Rs. 150,000.00"


# ===========================================================================
# 7. End-to-End Workflows
# ===========================================================================


class TestEndToEndWorkflows:
    """Realistic multi-module workflows."""

    def test_user_registration_workflow(self):
        """
        Workflow: Validate phone → Validate NIC → Parse DOB →
                  Format DOB → Get province.
        """
        from apps.core.srilanka import (
            validate_sl_phone,
            normalize_sl_phone,
            validate_nic,
            parse_nic_dob,
            get_province_by_code,
        )
        from apps.core.datetime import format_date

        # Step 1: Validate and normalize phone
        phone = "0771234567"
        assert validate_sl_phone(phone) is True
        normalized = normalize_sl_phone(phone)
        assert normalized == "+94771234567"

        # Step 2: Validate NIC
        nic = "881234567V"
        assert validate_nic(nic) is True

        # Step 3: Parse DOB from NIC
        dob, gender = parse_nic_dob(nic)
        assert isinstance(dob, date)
        assert gender in ("M", "F")

        # Step 4: Format DOB
        formatted_dob = format_date(dob)
        assert "/" in formatted_dob

        # Step 5: Look up province
        province = get_province_by_code("WP")
        assert province["name"] == "Western Province"

    def test_invoice_workflow(self):
        """
        Workflow: Format amounts → Format date → Get month range.
        """
        from apps.core.srilanka import format_lkr
        from apps.core.datetime import format_date, get_month_range

        # Line items
        items = [
            Decimal("2500.00"),
            Decimal("7500.00"),
            Decimal("15000.00"),
        ]
        subtotal = sum(items)
        tax = subtotal * Decimal("0.08")
        total = subtotal + tax

        assert format_lkr(subtotal) == "Rs. 25,000.00"
        assert format_lkr(tax) == "Rs. 2,000.00"
        assert format_lkr(total) == "Rs. 27,000.00"

        # Invoice date
        invoice_date = date(2026, 3, 11)
        assert format_date(invoice_date) == "11/03/2026"

        # Reporting period
        start, end = get_month_range(2026, 3)
        assert format_date(start) == "01/03/2026"
        assert format_date(end) == "31/03/2026"

    def test_product_creation_workflow(self):
        """
        Workflow: Validate slug → Validate price → Format LKR.
        """
        from apps.core.validators import (
            LCCSlugValidator,
            PositiveNumberValidator,
            DecimalValidator,
        )
        from apps.core.srilanka import format_lkr

        slug_val = LCCSlugValidator()
        positive_val = PositiveNumberValidator()
        decimal_val = DecimalValidator(max_digits=10, decimal_places=2)

        # Product data
        slug = "premium-laptop-15"
        price = Decimal("285000.00")

        slug_val(slug)          # Valid slug
        positive_val(price)     # Positive
        decimal_val(str(price)) # Correct decimal precision

        assert format_lkr(price) == "Rs. 285,000.00"

    def test_financial_report_workflow(self):
        """
        Workflow: Fiscal year range → Format dates → Format currency totals.
        """
        from apps.core.datetime import get_year_range, format_date
        from apps.core.srilanka import format_lkr

        start, end = get_year_range(2025, fiscal=True)
        assert format_date(start) == "01/04/2025"
        assert format_date(end) == "31/03/2026"

        monthly_totals = [Decimal(f"{i * 100000}") for i in range(1, 13)]
        grand_total = sum(monthly_totals)

        formatted = format_lkr(grand_total)
        assert "Rs." in formatted
        assert grand_total == Decimal("7800000")

    def test_customer_lookup_workflow(self):
        """
        Workflow: Search customer by phone → Get district info.
        """
        from apps.core.srilanka import (
            validate_sl_phone,
            format_sl_phone,
            get_district_by_code,
            get_province_by_code,
        )

        phone = "0712345678"
        assert validate_sl_phone(phone) is True
        formatted = format_sl_phone(phone)
        assert formatted == "+94 71 234 5678"

        district = get_district_by_code("CO")
        assert district["name"] == "Colombo"

        province = get_province_by_code(district["province"])
        assert province["name"] == "Western Province"

    def test_date_boundary_report(self):
        """
        Workflow: Get today's range → monthly → yearly → format all.
        """
        from apps.core.datetime import (
            get_date_range,
            get_month_range,
            get_year_range,
            format_date,
        )

        target = date(2026, 6, 15)

        day_start, day_end = get_date_range(target)
        month_start, month_end = get_month_range(2026, 6)
        year_start, year_end = get_year_range(2026)

        assert format_date(day_start) == "15/06/2026"
        assert format_date(month_start) == "01/06/2026"
        assert format_date(month_end) == "30/06/2026"
        assert format_date(year_start) == "01/01/2026"
        assert format_date(year_end) == "31/12/2026"

    def test_multi_currency_comparison(self):
        """
        Workflow: Format LKR → Convert to USD → Compare.
        """
        from apps.core.srilanka import format_lkr, convert_currency

        lkr = Decimal("50000")
        usd = convert_currency(lkr, "LKR", "USD", exchange_rate=Decimal("0.003"))

        assert format_lkr(lkr) == "Rs. 50,000.00"
        assert usd == Decimal("150.000")

    def test_complete_order_summary(self):
        """
        Workflow: Validate customer phone → Validate product data →
                  Calculate totals → Format with date → Get province.
        """
        from apps.core.srilanka import (
            validate_sl_phone,
            format_lkr,
            get_province_by_code,
            get_districts_by_province,
        )
        from apps.core.datetime import format_date, format_datetime
        from apps.core.validators import PositiveNumberValidator

        # Customer
        assert validate_sl_phone("0761234567") is True

        # Product prices
        pos_val = PositiveNumberValidator()
        prices = [Decimal("5000"), Decimal("12000"), Decimal("3500")]
        for p in prices:
            pos_val(p)

        total = sum(prices)
        assert format_lkr(total) == "Rs. 20,500.00"

        # Date/time
        order_dt = datetime(2026, 3, 11, 14, 45)
        assert format_date(order_dt) == "11/03/2026"
        assert format_datetime(order_dt) == "11/03/2026 14:45"

        # Delivery province
        province = get_province_by_code("SP")
        assert province["name"] == "Southern Province"
        districts = get_districts_by_province("SP")
        assert len(districts) == 3
