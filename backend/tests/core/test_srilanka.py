"""
Comprehensive tests for Sri Lanka utilities module.

Covers: currency, phone, NIC, provinces/districts.
Target: 150+ test cases (expanded via parametrize).
No database access required.
"""

import pytest
from datetime import date
from decimal import Decimal

from apps.core.srilanka import (
    # Currency
    format_lkr,
    parse_lkr,
    convert_currency,
    # Phone
    validate_sl_phone,
    format_sl_phone,
    normalize_sl_phone,
    # NIC
    validate_nic,
    parse_nic_dob,
    # Administrative
    PROVINCES,
    DISTRICTS,
    get_province_by_code,
    get_province_choices,
    get_districts_by_province,
    get_district_by_code,
    get_district_choices,
)
from apps.core.srilanka.currency import format_lkr as currency_format_lkr
from apps.core.srilanka.phone import validate_sl_phone as phone_validate
from apps.core.srilanka.nic import validate_nic as nic_validate
from apps.core.srilanka.provinces import PROVINCES as prov_list


# ─────────────────────────────────────────────────────────
# TestFormatLKR (~20 tests)
# ─────────────────────────────────────────────────────────

class TestFormatLKR:
    """Tests for format_lkr()."""

    @pytest.mark.parametrize("amount, expected", [
        (0, "Rs. 0.00"),
        (1, "Rs. 1.00"),
        (100, "Rs. 100.00"),
        (999, "Rs. 999.00"),
        (1000, "Rs. 1,000.00"),
        (1500, "Rs. 1,500.00"),
        (9999, "Rs. 9,999.00"),
        (10000, "Rs. 10,000.00"),
        (99999, "Rs. 99,999.00"),
        (100000, "Rs. 100,000.00"),
        (1500000, "Rs. 1,500,000.00"),
        (10000000, "Rs. 10,000,000.00"),
        (999999999, "Rs. 999,999,999.00"),
    ])
    def test_format_integer_amounts(self, amount, expected):
        assert format_lkr(amount) == expected

    @pytest.mark.parametrize("amount, expected", [
        (99.99, "Rs. 99.99"),
        (1500.50, "Rs. 1,500.50"),
        (0.01, "Rs. 0.01"),
        (0.10, "Rs. 0.10"),
        (1234.56, "Rs. 1,234.56"),
        (999999.99, "Rs. 999,999.99"),
    ])
    def test_format_float_amounts(self, amount, expected):
        assert format_lkr(amount) == expected

    @pytest.mark.parametrize("amount, expected", [
        (-500, "Rs. -500.00"),
        (-1500.50, "Rs. -1,500.50"),
        (-0.01, "Rs. -0.01"),
        (-999999, "Rs. -999,999.00"),
    ])
    def test_format_negative_amounts(self, amount, expected):
        assert format_lkr(amount) == expected

    def test_format_decimal_type(self):
        assert format_lkr(Decimal("1500.50")) == "Rs. 1,500.50"

    def test_format_decimal_precise(self):
        assert format_lkr(Decimal("0.10")) == "Rs. 0.10"

    def test_format_string_amount(self):
        assert format_lkr("1500") == "Rs. 1,500.00"

    def test_format_string_decimal_amount(self):
        assert format_lkr("1500.75") == "Rs. 1,500.75"

    @pytest.mark.parametrize("amount, expected", [
        (1500, "1,500.00"),
        (0, "0.00"),
        (99.99, "99.99"),
        (-500, "-500.00"),
        (1500000, "1,500,000.00"),
    ])
    def test_format_without_symbol(self, amount, expected):
        assert format_lkr(amount, show_symbol=False) == expected

    def test_format_large_amount(self):
        assert format_lkr(1000000000) == "Rs. 1,000,000,000.00"

    def test_format_very_small_decimal(self):
        assert format_lkr(Decimal("0.005")) == "Rs. 0.00"  # banker's rounding


# ─────────────────────────────────────────────────────────
# TestParseLKR (~20 tests)
# ─────────────────────────────────────────────────────────

class TestParseLKR:
    """Tests for parse_lkr()."""

    @pytest.mark.parametrize("value, expected", [
        ("Rs. 1,500.00", Decimal("1500.00")),
        ("Rs. 0.00", Decimal("0.00")),
        ("Rs. 100.00", Decimal("100.00")),
        ("Rs. 1,500,000.00", Decimal("1500000.00")),
        ("Rs. 99.99", Decimal("99.99")),
        ("Rs. -500.00", Decimal("-500.00")),
    ])
    def test_parse_with_rs_symbol(self, value, expected):
        assert parse_lkr(value) == expected

    @pytest.mark.parametrize("value, expected", [
        ("1,500", Decimal("1500")),
        ("1500", Decimal("1500")),
        ("1500.00", Decimal("1500.00")),
        ("0", Decimal("0")),
        ("0.01", Decimal("0.01")),
        ("999,999.99", Decimal("999999.99")),
    ])
    def test_parse_without_symbol(self, value, expected):
        assert parse_lkr(value) == expected

    def test_parse_sinhala_symbol(self):
        result = parse_lkr("රු 1,500.00")
        assert result == Decimal("1500.00")

    def test_parse_integer(self):
        assert parse_lkr(1500) == Decimal("1500")

    def test_parse_float(self):
        assert parse_lkr(1500.50) == Decimal("1500.5")

    def test_parse_decimal_passthrough(self):
        val = Decimal("1500.00")
        assert parse_lkr(val) is val

    def test_parse_negative_string(self):
        assert parse_lkr("-1500") == Decimal("-1500")

    def test_parse_invalid_string_raises(self):
        with pytest.raises(ValueError):
            parse_lkr("invalid")

    def test_parse_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse_lkr("")

    def test_parse_only_symbol_raises(self):
        with pytest.raises(ValueError):
            parse_lkr("Rs.")

    def test_parse_none_raises(self):
        with pytest.raises(ValueError):
            parse_lkr(None)

    def test_parse_list_raises(self):
        with pytest.raises(ValueError):
            parse_lkr([1500])

    @pytest.mark.parametrize("amount", [
        0, 1, 100, 1500, 99999, 1500000, Decimal("1234.56"),
    ])
    def test_roundtrip_format_parse(self, amount):
        """format then parse should return the same value (2 dp)."""
        formatted = format_lkr(amount, show_symbol=True)
        parsed = parse_lkr(formatted)
        assert parsed == Decimal(str(amount)).quantize(Decimal("0.01"))

    def test_parse_whitespace_padding(self):
        assert parse_lkr("  1500  ") == Decimal("1500")

    def test_parse_rs_with_extra_spaces(self):
        assert parse_lkr("Rs.  1,500.00") == Decimal("1500.00")


# ─────────────────────────────────────────────────────────
# TestConvertCurrency (~12 tests)
# ─────────────────────────────────────────────────────────

class TestConvertCurrency:
    """Tests for convert_currency()."""

    def test_basic_conversion(self):
        result = convert_currency(300, 'LKR', 'USD', exchange_rate=0.0033)
        assert result == Decimal("300") * Decimal("0.0033")

    def test_no_rate_raises(self):
        with pytest.raises(ValueError, match="Exchange rate required"):
            convert_currency(300, 'LKR', 'USD')

    def test_zero_amount(self):
        result = convert_currency(0, 'LKR', 'USD', exchange_rate=0.0033)
        assert result == Decimal("0")

    def test_decimal_input(self):
        result = convert_currency(Decimal("1000"), 'LKR', 'USD', exchange_rate=Decimal("0.0033"))
        assert result == Decimal("1000") * Decimal("0.0033")

    def test_float_input(self):
        result = convert_currency(1000.50, 'LKR', 'USD', exchange_rate=0.0033)
        assert result == Decimal("1000.50") * Decimal("0.0033")

    def test_string_amount(self):
        result = convert_currency("500", 'LKR', 'USD', exchange_rate="0.0033")
        assert result == Decimal("500") * Decimal("0.0033")

    def test_usd_to_lkr(self):
        result = convert_currency(10, 'USD', 'LKR', exchange_rate=300)
        assert result == Decimal("3000")

    def test_same_currency(self):
        result = convert_currency(1000, 'LKR', 'LKR', exchange_rate=1)
        assert result == Decimal("1000")

    def test_negative_amount(self):
        result = convert_currency(-100, 'LKR', 'USD', exchange_rate=0.0033)
        assert result == Decimal("-100") * Decimal("0.0033")

    def test_very_small_rate(self):
        result = convert_currency(1000000, 'LKR', 'BTC', exchange_rate="0.0000001")
        assert result == Decimal("1000000") * Decimal("0.0000001")

    def test_large_amount(self):
        result = convert_currency(1000000000, 'LKR', 'USD', exchange_rate=0.0033)
        assert result == Decimal("1000000000") * Decimal("0.0033")

    def test_rate_of_one(self):
        result = convert_currency(1500, 'LKR', 'XXX', exchange_rate=1)
        assert result == Decimal("1500")


# ─────────────────────────────────────────────────────────
# TestValidateSLPhone (~30 tests)
# ─────────────────────────────────────────────────────────

class TestValidateSLPhone:
    """Tests for validate_sl_phone()."""

    @pytest.mark.parametrize("phone", [
        "+94 71 234 5678",
        "+94712345678",
        "0712345678",
        "712345678",
        "+94 71 234 5678",
        "+94-71-234-5678",
        "(071) 234 5678",
    ])
    def test_valid_71_prefix(self, phone):
        assert validate_sl_phone(phone) is True

    @pytest.mark.parametrize("prefix", [
        "70", "71", "72", "74", "75", "76", "77", "78",
    ])
    def test_all_valid_prefixes_with_0(self, prefix):
        phone = f"0{prefix}1234567"
        assert validate_sl_phone(phone) is True

    @pytest.mark.parametrize("prefix", [
        "70", "71", "72", "74", "75", "76", "77", "78",
    ])
    def test_all_valid_prefixes_with_94(self, prefix):
        phone = f"+94{prefix}1234567"
        assert validate_sl_phone(phone) is True

    @pytest.mark.parametrize("prefix", [
        "70", "71", "72", "74", "75", "76", "77", "78",
    ])
    def test_all_valid_prefixes_bare(self, prefix):
        phone = f"{prefix}1234567"
        assert validate_sl_phone(phone) is True

    @pytest.mark.parametrize("phone", [
        "0732345678",   # 73 is not valid
        "0792345678",   # 79 is not valid
    ])
    def test_invalid_prefixes(self, phone):
        assert validate_sl_phone(phone) is False

    @pytest.mark.parametrize("phone", [
        "123456",               # too short
        "12345678901234",       # too long
        "",                     # empty
        "+1 555 123 4567",      # US number
        "+44 20 7946 0958",     # UK number
        "0612345678",           # invalid prefix 61
        "abc1234567",           # letters
        "071234567",            # 9 digits with 0 (too short - only 7 after prefix)
        "07123456789",          # too long with 0 prefix
    ])
    def test_invalid_numbers(self, phone):
        assert validate_sl_phone(phone) is False

    def test_none_returns_false(self):
        assert validate_sl_phone(None) is False

    def test_integer_returns_false(self):
        assert validate_sl_phone(712345678) is False

    def test_list_returns_false(self):
        assert validate_sl_phone(["0712345678"]) is False

    def test_valid_with_spaces_and_dashes(self):
        assert validate_sl_phone("+94 77 123 4567") is True
        assert validate_sl_phone("+94-77-123-4567") is True

    def test_valid_minimum_digits(self):
        # 9 digits starting with valid prefix
        assert validate_sl_phone("700000000") is True

    def test_valid_maximum_digits(self):
        # 9 digits all 9s with valid prefix
        assert validate_sl_phone("789999999") is True


# ─────────────────────────────────────────────────────────
# TestFormatSLPhone (~12 tests)
# ─────────────────────────────────────────────────────────

class TestFormatSLPhone:
    """Tests for format_sl_phone()."""

    @pytest.mark.parametrize("phone, expected", [
        ("0712345678", "+94 71 234 5678"),
        ("+94712345678", "+94 71 234 5678"),
        ("712345678", "+94 71 234 5678"),
        ("+94 71 234 5678", "+94 71 234 5678"),
        ("+94-71-234-5678", "+94 71 234 5678"),
        ("0771234567", "+94 77 123 4567"),
        ("0701234567", "+94 70 123 4567"),
        ("0781234567", "+94 78 123 4567"),
        ("0751234567", "+94 75 123 4567"),
        ("0741234567", "+94 74 123 4567"),
    ])
    def test_format_valid_numbers(self, phone, expected):
        assert format_sl_phone(phone) == expected

    def test_format_invalid_raises(self):
        with pytest.raises(ValueError):
            format_sl_phone("invalid")

    def test_format_empty_raises(self):
        with pytest.raises(ValueError):
            format_sl_phone("")

    def test_format_us_number_raises(self):
        with pytest.raises(ValueError):
            format_sl_phone("+1 555 123 4567")


# ─────────────────────────────────────────────────────────
# TestNormalizeSLPhone (~12 tests)
# ─────────────────────────────────────────────────────────

class TestNormalizeSLPhone:
    """Tests for normalize_sl_phone()."""

    @pytest.mark.parametrize("phone, expected", [
        ("0712345678", "+94712345678"),
        ("+94 71 234 5678", "+94712345678"),
        ("712345678", "+94712345678"),
        ("+94712345678", "+94712345678"),
        ("+94-71-234-5678", "+94712345678"),
        ("0771234567", "+94771234567"),
        ("0701234567", "+94701234567"),
        ("0781234567", "+94781234567"),
    ])
    def test_normalize_valid_numbers(self, phone, expected):
        assert normalize_sl_phone(phone) == expected

    def test_normalize_invalid_raises(self):
        with pytest.raises(ValueError):
            normalize_sl_phone("invalid")

    def test_normalize_empty_raises(self):
        with pytest.raises(ValueError):
            normalize_sl_phone("")

    def test_normalize_none_raises(self):
        with pytest.raises(ValueError):
            normalize_sl_phone(None)

    def test_normalize_idempotent(self):
        """Normalizing an already normalized number returns the same."""
        normalized = normalize_sl_phone("0712345678")
        assert normalize_sl_phone(normalized) == normalized


# ─────────────────────────────────────────────────────────
# TestValidateNIC (~30 tests)
# ─────────────────────────────────────────────────────────

class TestValidateNIC:
    """Tests for validate_nic()."""

    @pytest.mark.parametrize("nic", [
        "881234567V",   # male, day 123
        "886234567X",   # female, day 623 (623-500=123)
        "900011234V",   # day 001 (Jan 1)
        "903661234V",   # day 366 (Dec 31 leap year)
        "905011234X",   # female day 001 (501 = 1 + 500)
        "908661234X",   # female day 366 (866 = 366 + 500)
        "501001234V",   # year 50, day 100
        "993001234V",   # year 99, day 300
        "010011234V",   # year 01, day 001
        "881001234V",   # day 100
        "882001234V",   # day 200
        "883001234V",   # day 300
    ])
    def test_valid_old_format(self, nic):
        assert validate_nic(nic) is True

    @pytest.mark.parametrize("nic", [
        "198812345678",   # standard new format
        "200001112345",   # year 2000
        "199001100001",   # year 1990
        "210001100001",   # year 2100
        "190001100001",   # year 1900
        "200050100001",   # female new format (501)
        "200086600001",   # female day 366 (866)
    ])
    def test_valid_new_format(self, nic):
        assert validate_nic(nic) is True

    @pytest.mark.parametrize("nic", [
        "880001234V",   # day 000 (invalid)
        "883671234V",   # day 367 (invalid male, between 367-500)
        "884001234V",   # day 400 (invalid, between 367-500)
        "885001234V",   # day 500 (invalid, between 367-500)
        "888671234V",   # day 867 (invalid female)
        "889001234V",   # day 900 (way too high)
    ])
    def test_invalid_old_format_day_range(self, nic):
        assert validate_nic(nic) is False

    @pytest.mark.parametrize("nic", [
        "130012345678",   # year 1300 (too old)
        "210112345678",   # year 2101 (too far in future)
        "189912345678",   # year 1899 (below 1900)
        "300012345678",   # year 3000
    ])
    def test_invalid_new_format_year_range(self, nic):
        assert validate_nic(nic) is False

    @pytest.mark.parametrize("nic", [
        "200000012345",   # day 000 in new format
        "200036712345",   # day 367 in new format (invalid)
        "200040012345",   # day 400 in new format (invalid)
        "200086712345",   # day 867 in new format (invalid)
    ])
    def test_invalid_new_format_day_range(self, nic):
        assert validate_nic(nic) is False

    @pytest.mark.parametrize("nic", [
        "123456789",      # 9 digits, no suffix
        "ABCDEFGHIJ",     # non-numeric
        "",               # empty
        "12345678901",    # 11 chars
        "1234567890123",  # 13 digits
        "88123456VV",     # double suffix
        "88123456A",      # wrong suffix letter
    ])
    def test_invalid_format(self, nic):
        assert validate_nic(nic) is False

    def test_none_returns_false(self):
        assert validate_nic(None) is False

    def test_integer_returns_false(self):
        assert validate_nic(881234567) is False

    def test_list_returns_false(self):
        assert validate_nic(["881234567V"]) is False

    def test_lowercase_v_accepted(self):
        assert validate_nic("881234567v") is True

    def test_lowercase_x_accepted(self):
        assert validate_nic("886234567x") is True

    def test_whitespace_stripped(self):
        assert validate_nic("  881234567V  ") is True


# ─────────────────────────────────────────────────────────
# TestParseNICDob (~22 tests)
# ─────────────────────────────────────────────────────────

class TestParseNICDob:
    """Tests for parse_nic_dob()."""

    def test_old_male_basic(self):
        # 881234567V: year=88 → 1988, day=123, male
        dob, gender = parse_nic_dob("881234567V")
        assert gender == 'M'
        assert dob.year == 1988
        # Day 123 of 1988 = May 3, 1988 (1988 is a leap year)
        assert dob == date(1988, 5, 2)  # day 1 = Jan 1, day 123 = May 2

    def test_old_female_basic(self):
        # 886234567X: year=88 → 1988, day=623 → 623-500=123, female
        dob, gender = parse_nic_dob("886234567X")
        assert gender == 'F'
        assert dob.year == 1988
        assert dob == date(1988, 5, 2)

    def test_old_format_year_ge_50_is_1900s(self):
        # 503651234V: year=50 → 1950
        dob, gender = parse_nic_dob("503651234V")
        assert dob.year == 1950
        assert gender == 'M'

    def test_old_format_year_lt_50_is_2000s(self):
        # 103651234V: year=10 → 2010
        dob, gender = parse_nic_dob("103651234V")
        assert dob.year == 2010
        assert gender == 'M'

    def test_old_format_year_49_is_2000s(self):
        # 491001234V: year=49 → 2049
        dob, gender = parse_nic_dob("491001234V")
        assert dob.year == 2049
        assert gender == 'M'

    def test_old_format_year_00_is_2000(self):
        # 001001234V: year=00 → 2000
        dob, gender = parse_nic_dob("001001234V")
        assert dob.year == 2000
        assert gender == 'M'

    def test_old_format_day_001_is_jan_1(self):
        # 900011234V: year=90 → 1990, day=001 → Jan 1
        dob, gender = parse_nic_dob("900011234V")
        assert dob == date(1990, 1, 1)
        assert gender == 'M'

    def test_old_format_day_365_non_leap(self):
        # 910011234V but day=365, year=91 (1991, not a leap year)
        # "913651234V" — day 365 of 1991 = Dec 31
        dob, gender = parse_nic_dob("913651234V")
        assert dob == date(1991, 12, 31)
        assert gender == 'M'

    def test_old_format_day_366_leap_year(self):
        # 923661234V: year=92 → 1992 (leap year), day=366 → Dec 31
        dob, gender = parse_nic_dob("923661234V")
        assert dob == date(1992, 12, 31)
        assert gender == 'M'

    def test_new_male_basic(self):
        # 199801512345: year=1998, day=015, male
        dob, gender = parse_nic_dob("199801512345")
        assert gender == 'M'
        assert dob.year == 1998
        assert dob == date(1998, 1, 15)

    def test_new_female_basic(self):
        # 199851512345: year=1998, day=515 → 515-500=15, female
        dob, gender = parse_nic_dob("199851512345")
        assert gender == 'F'
        assert dob.year == 1998
        assert dob == date(1998, 1, 15)

    def test_new_format_year_2000(self):
        dob, gender = parse_nic_dob("200000112345")
        assert dob == date(2000, 1, 1)
        assert gender == 'M'

    def test_new_format_dec_31_leap(self):
        # 200036612345: year=2000 (leap), day=366 → Dec 31
        dob, gender = parse_nic_dob("200036612345")
        assert dob == date(2000, 12, 31)
        assert gender == 'M'

    def test_new_format_female_day_501_is_jan1(self):
        # 200050112345: day=501 → 501-500=1 → Jan 1, female
        dob, gender = parse_nic_dob("200050112345")
        assert dob == date(2000, 1, 1)
        assert gender == 'F'

    def test_invalid_nic_raises(self):
        with pytest.raises(ValueError, match="Invalid NIC"):
            parse_nic_dob("invalid")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            parse_nic_dob("")

    def test_none_raises(self):
        with pytest.raises(ValueError):
            parse_nic_dob(None)

    @pytest.mark.parametrize("nic, expected_gender", [
        ("881001234V", "M"),
        ("885011234X", "F"),
        ("886001234X", "F"),
        ("881001234V", "M"),
    ])
    def test_gender_detection(self, nic, expected_gender):
        _, gender = parse_nic_dob(nic)
        assert gender == expected_gender

    def test_old_and_new_same_person(self):
        """Old and new format for same person should give same DOB."""
        dob_old, gender_old = parse_nic_dob("881234567V")
        # New format: 1988, day 123
        dob_new, gender_new = parse_nic_dob("198812312345")
        assert dob_old == dob_new
        assert gender_old == gender_new

    def test_lowercasev_parsed(self):
        dob, gender = parse_nic_dob("881234567v")
        assert gender == 'M'
        assert dob.year == 1988

    def test_whitespace_stripped_parse(self):
        dob, gender = parse_nic_dob("  881234567V  ")
        assert gender == 'M'
        assert dob.year == 1988


# ─────────────────────────────────────────────────────────
# TestProvinces (~18 tests)
# ─────────────────────────────────────────────────────────

class TestProvinces:
    """Tests for province utilities."""

    def test_province_count(self):
        assert len(PROVINCES) == 9

    def test_all_province_codes_unique(self):
        codes = [p['code'] for p in PROVINCES]
        assert len(codes) == len(set(codes))

    def test_all_provinces_have_required_keys(self):
        for p in PROVINCES:
            assert 'code' in p
            assert 'name' in p
            assert 'sinhala' in p

    @pytest.mark.parametrize("code, name", [
        ("WP", "Western Province"),
        ("CP", "Central Province"),
        ("SP", "Southern Province"),
        ("NP", "Northern Province"),
        ("EP", "Eastern Province"),
        ("NWP", "North Western Province"),
        ("NCP", "North Central Province"),
        ("UP", "Uva Province"),
        ("SG", "Sabaragamuwa Province"),
    ])
    def test_get_province_by_code(self, code, name):
        province = get_province_by_code(code)
        assert province is not None
        assert province['name'] == name

    def test_get_province_by_code_invalid(self):
        assert get_province_by_code("INVALID") is None

    def test_get_province_by_code_empty(self):
        assert get_province_by_code("") is None

    def test_get_province_by_code_lowercase(self):
        province = get_province_by_code("wp")
        assert province is not None
        assert province['code'] == "WP"

    def test_get_province_choices(self):
        choices = get_province_choices()
        assert len(choices) == 9
        assert all(isinstance(c, tuple) and len(c) == 2 for c in choices)

    def test_get_province_choices_first(self):
        choices = get_province_choices()
        assert choices[0] == ("WP", "Western Province")

    def test_all_province_names_non_empty(self):
        for p in PROVINCES:
            assert len(p['name']) > 0
            assert len(p['sinhala']) > 0

    def test_province_sinhala_is_string(self):
        for p in PROVINCES:
            assert isinstance(p['sinhala'], str)


# ─────────────────────────────────────────────────────────
# TestDistricts (~25 tests)
# ─────────────────────────────────────────────────────────

class TestDistricts:
    """Tests for district utilities."""

    def test_district_count(self):
        assert len(DISTRICTS) == 25

    def test_all_district_codes_unique(self):
        codes = [d['code'] for d in DISTRICTS]
        assert len(codes) == len(set(codes))

    def test_all_districts_have_required_keys(self):
        for d in DISTRICTS:
            assert 'code' in d
            assert 'name' in d
            assert 'sinhala' in d
            assert 'province' in d

    def test_all_districts_have_valid_province(self):
        province_codes = {p['code'] for p in PROVINCES}
        for d in DISTRICTS:
            assert d['province'] in province_codes, f"District {d['name']} has invalid province {d['province']}"

    @pytest.mark.parametrize("province_code, count", [
        ("WP", 3),     # Colombo, Gampaha, Kalutara
        ("CP", 3),     # Kandy, Matale, Nuwara Eliya
        ("SP", 3),     # Galle, Matara, Hambantota
        ("NP", 5),     # Jaffna, Kilinochchi, Mannar, Mullaitivu, Vavuniya
        ("EP", 3),     # Ampara, Batticaloa, Trincomalee
        ("NWP", 2),    # Kurunegala, Puttalam
        ("NCP", 2),    # Anuradhapura, Polonnaruwa
        ("UP", 2),     # Badulla, Monaragala
        ("SG", 2),     # Kegalle, Ratnapura
    ])
    def test_districts_by_province_count(self, province_code, count):
        districts = get_districts_by_province(province_code)
        assert len(districts) == count

    def test_districts_by_province_western(self):
        districts = get_districts_by_province("WP")
        names = [d['name'] for d in districts]
        assert "Colombo" in names
        assert "Gampaha" in names
        assert "Kalutara" in names

    def test_districts_by_province_northern(self):
        districts = get_districts_by_province("NP")
        names = [d['name'] for d in districts]
        assert "Jaffna" in names
        assert "Kilinochchi" in names
        assert "Mannar" in names
        assert "Mullaitivu" in names
        assert "Vavuniya" in names

    def test_districts_by_province_lowercase(self):
        districts = get_districts_by_province("wp")
        assert len(districts) == 3

    def test_districts_by_province_invalid(self):
        districts = get_districts_by_province("INVALID")
        assert len(districts) == 0

    @pytest.mark.parametrize("code, name", [
        ("CO", "Colombo"),
        ("GM", "Gampaha"),
        ("KT", "Kalutara"),
        ("KY", "Kandy"),
        ("GL", "Galle"),
        ("JA", "Jaffna"),
        ("KR", "Kurunegala"),
        ("AD", "Anuradhapura"),
        ("BA", "Badulla"),
        ("KG", "Kegalle"),
        ("RP", "Ratnapura"),
    ])
    def test_get_district_by_code(self, code, name):
        district = get_district_by_code(code)
        assert district is not None
        assert district['name'] == name

    def test_get_district_by_code_invalid(self):
        assert get_district_by_code("INVALID") is None

    def test_get_district_by_code_empty(self):
        assert get_district_by_code("") is None

    def test_get_district_by_code_lowercase(self):
        district = get_district_by_code("co")
        assert district is not None
        assert district['name'] == "Colombo"

    def test_get_district_choices_all(self):
        choices = get_district_choices()
        assert len(choices) == 25
        assert all(isinstance(c, tuple) and len(c) == 2 for c in choices)

    def test_get_district_choices_filtered(self):
        choices = get_district_choices("WP")
        assert len(choices) == 3

    def test_get_district_choices_filtered_northern(self):
        choices = get_district_choices("NP")
        assert len(choices) == 5

    def test_get_district_choices_filtered_none(self):
        choices = get_district_choices("INVALID")
        assert len(choices) == 0

    def test_get_district_choices_contains_colombo(self):
        choices = get_district_choices()
        assert ("CO", "Colombo") in choices

    def test_all_district_names_non_empty(self):
        for d in DISTRICTS:
            assert len(d['name']) > 0
            assert len(d['sinhala']) > 0

    def test_total_districts_sum_to_25(self):
        total = sum(
            len(get_districts_by_province(p['code']))
            for p in PROVINCES
        )
        assert total == 25


# ─────────────────────────────────────────────────────────
# TestImports (~12 tests)
# ─────────────────────────────────────────────────────────

class TestImports:
    """Tests for package imports and __all__."""

    def test_import_format_lkr(self):
        from apps.core.srilanka import format_lkr as f
        assert callable(f)

    def test_import_parse_lkr(self):
        from apps.core.srilanka import parse_lkr as f
        assert callable(f)

    def test_import_convert_currency(self):
        from apps.core.srilanka import convert_currency as f
        assert callable(f)

    def test_import_validate_sl_phone(self):
        from apps.core.srilanka import validate_sl_phone as f
        assert callable(f)

    def test_import_format_sl_phone(self):
        from apps.core.srilanka import format_sl_phone as f
        assert callable(f)

    def test_import_normalize_sl_phone(self):
        from apps.core.srilanka import normalize_sl_phone as f
        assert callable(f)

    def test_import_validate_nic(self):
        from apps.core.srilanka import validate_nic as f
        assert callable(f)

    def test_import_parse_nic_dob(self):
        from apps.core.srilanka import parse_nic_dob as f
        assert callable(f)

    def test_import_provinces(self):
        from apps.core.srilanka import PROVINCES as p
        assert isinstance(p, list)

    def test_import_districts(self):
        from apps.core.srilanka import DISTRICTS as d
        assert isinstance(d, list)

    def test_version(self):
        import apps.core.srilanka as pkg
        assert pkg.__version__ == '1.0.0'

    def test_all_contains_expected(self):
        import apps.core.srilanka as pkg
        expected = [
            'format_lkr', 'parse_lkr', 'convert_currency',
            'validate_sl_phone', 'format_sl_phone', 'normalize_sl_phone',
            'validate_nic', 'parse_nic_dob',
            'PROVINCES', 'DISTRICTS',
            'get_province_by_code', 'get_province_choices',
            'get_districts_by_province', 'get_district_by_code',
            'get_district_choices',
        ]
        for name in expected:
            assert name in pkg.__all__, f"{name} missing from __all__"

    def test_submodule_import_currency(self):
        assert callable(currency_format_lkr)

    def test_submodule_import_phone(self):
        assert callable(phone_validate)

    def test_submodule_import_nic(self):
        assert callable(nic_validate)

    def test_submodule_import_provinces(self):
        assert isinstance(prov_list, list)
