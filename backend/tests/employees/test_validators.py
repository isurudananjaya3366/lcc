"""Tests for employee validators."""

import pytest
from django.core.exceptions import ValidationError

from apps.employees.validators.nic_validator import (
    extract_birth_year_from_nic,
    extract_gender_from_nic,
    extract_nic_components,
    is_leap_year,
    is_valid_day_of_year,
    validate_nic,
)
from apps.employees.validators.phone_validator import (
    SriLankaPhoneValidator,
    validate_sl_phone,
)

pytestmark = pytest.mark.django_db


class TestNICValidator:
    """Tests for Sri Lankan NIC validation."""

    # --- Valid NIC formats ---

    def test_valid_old_format_male(self):
        validate_nic("912345678V")

    def test_valid_old_format_female(self):
        validate_nic("916345678V")

    def test_valid_old_format_lowercase_v(self):
        validate_nic("912345678v")

    def test_valid_old_format_x_suffix(self):
        validate_nic("912345678X")

    def test_valid_new_format_male(self):
        validate_nic("199123456789")

    def test_valid_new_format_female(self):
        validate_nic("199563456789")

    # --- Invalid NIC formats ---

    def test_invalid_too_short(self):
        with pytest.raises(ValidationError):
            validate_nic("123")

    def test_invalid_too_long(self):
        with pytest.raises(ValidationError):
            validate_nic("1234567890123")

    def test_invalid_old_format_wrong_suffix(self):
        with pytest.raises(ValidationError):
            validate_nic("912345678Z")

    def test_invalid_empty(self):
        with pytest.raises(ValidationError):
            validate_nic("")

    def test_invalid_non_numeric(self):
        with pytest.raises(ValidationError):
            validate_nic("abcdefghij")

    def test_invalid_old_format_day_of_year_zero(self):
        with pytest.raises(ValidationError):
            validate_nic("910005678V")

    def test_invalid_old_format_day_of_year_too_high(self):
        with pytest.raises(ValidationError):
            validate_nic("919995678V")  # Day 999 invalid

    # --- extract_birth_year_from_nic ---

    def test_extract_birth_year_old_format(self):
        assert extract_birth_year_from_nic("912345678V") == 1991

    def test_extract_birth_year_new_format(self):
        assert extract_birth_year_from_nic("199123456789") == 1991

    def test_extract_birth_year_invalid_returns_none(self):
        assert extract_birth_year_from_nic("invalid") is None

    # --- extract_gender_from_nic ---

    def test_extract_gender_male_old_format(self):
        assert extract_gender_from_nic("912345678V") == "male"

    def test_extract_gender_female_old_format(self):
        assert extract_gender_from_nic("916345678V") == "female"

    def test_extract_gender_male_new_format(self):
        assert extract_gender_from_nic("199123456789") == "male"

    def test_extract_gender_female_new_format(self):
        assert extract_gender_from_nic("199563456789") == "female"

    def test_extract_gender_invalid_returns_none(self):
        assert extract_gender_from_nic("invalid") is None

    # --- extract_nic_components ---

    def test_extract_components_old_format(self):
        result = extract_nic_components("912345678V")
        assert result is not None
        assert result["year"] == 1991
        assert result["gender"] == "male"
        assert result["format"] == "old"

    def test_extract_components_new_format(self):
        result = extract_nic_components("199123456789")
        assert result is not None
        assert result["year"] == 1991
        assert result["gender"] == "male"
        assert result["format"] == "new"

    def test_extract_components_invalid(self):
        assert extract_nic_components("invalid") is None

    # --- is_leap_year ---

    def test_leap_year_2000(self):
        assert is_leap_year(2000) is True

    def test_leap_year_2024(self):
        assert is_leap_year(2024) is True

    def test_not_leap_year_1900(self):
        assert is_leap_year(1900) is False

    def test_not_leap_year_2023(self):
        assert is_leap_year(2023) is False

    # --- is_valid_day_of_year ---

    def test_valid_day_of_year(self):
        assert is_valid_day_of_year(1) is True
        assert is_valid_day_of_year(365) is True
        assert is_valid_day_of_year(366, 2024) is True  # 2024 is a leap year

    def test_invalid_day_of_year(self):
        assert is_valid_day_of_year(0) is False
        assert is_valid_day_of_year(366, 2023) is False  # 2023 is not a leap year
        assert is_valid_day_of_year(367, 2024) is False


class TestPhoneValidator:
    """Tests for Sri Lankan phone number validation."""

    def test_valid_mobile_with_country_code(self):
        validate_sl_phone("+94712345678")

    def test_valid_mobile_local(self):
        validate_sl_phone("0712345678")

    def test_valid_landline_with_country_code(self):
        validate_sl_phone("+94112345678")

    def test_valid_landline_local(self):
        validate_sl_phone("0112345678")

    def test_invalid_prefix(self):
        with pytest.raises(ValidationError):
            validate_sl_phone("+94992345678")

    def test_invalid_too_short(self):
        with pytest.raises(ValidationError):
            validate_sl_phone("+9471234")

    def test_invalid_too_long(self):
        with pytest.raises(ValidationError):
            validate_sl_phone("+947123456789999")

    def test_invalid_non_numeric(self):
        with pytest.raises(ValidationError):
            validate_sl_phone("phone123")


class TestSriLankaPhoneValidatorClass:
    """Tests for SriLankaPhoneValidator class."""

    def test_validator_creation(self):
        v = SriLankaPhoneValidator()
        assert v is not None

    def test_validator_call_valid(self):
        v = SriLankaPhoneValidator()
        v("+94712345678")  # Should not raise

    def test_validator_call_invalid(self):
        v = SriLankaPhoneValidator()
        with pytest.raises(ValidationError):
            v("invalid")

    def test_validator_deconstruct(self):
        v = SriLankaPhoneValidator()
        path, args, kwargs = v.deconstruct()
        assert "SriLankaPhoneValidator" in path

    def test_validator_equality(self):
        v1 = SriLankaPhoneValidator()
        v2 = SriLankaPhoneValidator()
        assert v1 == v2
