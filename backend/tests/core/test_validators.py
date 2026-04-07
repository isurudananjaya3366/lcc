"""
LankaCommerce Cloud – Validator Tests (SP12 Task 48).

Comprehensive tests for all validators in ``apps.core.validators``.

Coverage targets:
    * Every validator's ``__call__`` with valid input (no exception)
    * Every validator's ``__call__`` with invalid input (``ValidationError``)
    * Edge cases: empty strings, ``None``, boundary values
    * Parameterised validators with different configurations
    * ``UniqueForTenantValidator`` with mocked tenant connection
    * Error messages contain useful information
"""

from __future__ import annotations

import json
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from django.core.exceptions import ValidationError

from apps.core.validators import (
    DecimalValidator,
    FileExtensionValidator,
    FileSizeValidator,
    ImageDimensionValidator,
    JSONValidator,
    LCCEmailValidator,
    LCCSlugValidator,
    LCCURLValidator,
    NoHTMLValidator,
    PercentageValidator,
    PositiveNumberValidator,
    UniqueForTenantValidator,
)


# ════════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════════


def _make_file(name: str, size: int = 1024) -> SimpleNamespace:
    """Create a lightweight file-like object for testing."""
    return SimpleNamespace(name=name, size=size)


# ════════════════════════════════════════════════════════════════════════════
# Import Smoke Tests
# ════════════════════════════════════════════════════════════════════════════


class TestImports:
    """Verify all validators are importable from the package."""

    def test_import_lcc_email_validator(self):
        from apps.core.validators import LCCEmailValidator  # noqa: F811

        assert LCCEmailValidator is not None

    def test_import_lcc_url_validator(self):
        from apps.core.validators import LCCURLValidator  # noqa: F811

        assert LCCURLValidator is not None

    def test_import_lcc_slug_validator(self):
        from apps.core.validators import LCCSlugValidator  # noqa: F811

        assert LCCSlugValidator is not None

    def test_import_positive_number_validator(self):
        from apps.core.validators import PositiveNumberValidator  # noqa: F811

        assert PositiveNumberValidator is not None

    def test_import_decimal_validator(self):
        from apps.core.validators import DecimalValidator  # noqa: F811

        assert DecimalValidator is not None

    def test_import_percentage_validator(self):
        from apps.core.validators import PercentageValidator  # noqa: F811

        assert PercentageValidator is not None

    def test_import_file_size_validator(self):
        from apps.core.validators import FileSizeValidator  # noqa: F811

        assert FileSizeValidator is not None

    def test_import_image_dimension_validator(self):
        from apps.core.validators import ImageDimensionValidator  # noqa: F811

        assert ImageDimensionValidator is not None

    def test_import_file_extension_validator(self):
        from apps.core.validators import FileExtensionValidator  # noqa: F811

        assert FileExtensionValidator is not None

    def test_import_json_validator(self):
        from apps.core.validators import JSONValidator  # noqa: F811

        assert JSONValidator is not None

    def test_import_no_html_validator(self):
        from apps.core.validators import NoHTMLValidator  # noqa: F811

        assert NoHTMLValidator is not None

    def test_import_unique_for_tenant_validator(self):
        from apps.core.validators import UniqueForTenantValidator  # noqa: F811

        assert UniqueForTenantValidator is not None

    def test_package_version(self):
        from apps.core.validators import __version__

        assert __version__ == "1.0.0"


# ════════════════════════════════════════════════════════════════════════════
# LCCEmailValidator
# ════════════════════════════════════════════════════════════════════════════


class TestLCCEmailValidator:
    """Tests for the stricter email validator."""

    @pytest.fixture()
    def validator(self):
        return LCCEmailValidator()

    # ── Valid ──

    @pytest.mark.parametrize(
        "email",
        [
            "user@example.com",
            "admin@company.lk",
            "test.user+tag@domain.co.uk",
            "firstname.lastname@subdomain.example.org",
        ],
    )
    def test_valid_emails(self, validator, email):
        validator(email)  # should not raise

    # ── Invalid format ──

    @pytest.mark.parametrize(
        "email",
        [
            "",
            "plainaddress",
            "@no-local.com",
            "user@",
            "user@.com",
            "user@@double.com",
            "user@domain",  # no dot in domain
        ],
    )
    def test_invalid_format(self, validator, email):
        with pytest.raises(ValidationError):
            validator(email)

    def test_none_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(None)

    def test_non_string_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(12345)

    def test_too_long_email(self, validator):
        long_email = "a" * 246 + "@test.com"  # > 254 chars
        with pytest.raises(ValidationError) as exc_info:
            validator(long_email)
        assert "254" in str(exc_info.value)

    # ── Disposable domains ──

    @pytest.mark.parametrize(
        "domain",
        [
            "tempmail.com",
            "guerrillamail.com",
            "mailinator.com",
            "yopmail.com",
        ],
    )
    def test_disposable_domain_rejected(self, validator, domain):
        with pytest.raises(ValidationError) as exc_info:
            validator(f"test@{domain}")
        assert "disposable" in str(exc_info.value).lower() or "Disposable" in str(
            exc_info.value
        )

    def test_domain_without_dot_rejected(self, validator):
        with pytest.raises(ValidationError):
            validator("user@localhost")

    # ── Error message quality ──

    def test_error_message_is_descriptive(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator("")
        assert "email" in str(exc_info.value).lower()


# ════════════════════════════════════════════════════════════════════════════
# LCCURLValidator
# ════════════════════════════════════════════════════════════════════════════


class TestLCCURLValidator:
    """Tests for the HTTP/HTTPS URL validator."""

    @pytest.fixture()
    def validator(self):
        return LCCURLValidator()

    # ── Valid ──

    @pytest.mark.parametrize(
        "url",
        [
            "http://example.com",
            "https://example.com",
            "https://www.example.com/path?q=1",
            "http://localhost:8000/api/",
            "https://sub.domain.example.com/a/b/c",
        ],
    )
    def test_valid_urls(self, validator, url):
        validator(url)  # should not raise

    # ── Invalid ──

    @pytest.mark.parametrize(
        "url",
        [
            "",
            "not-a-url",
            "ftp://files.example.com",
            "example.com",  # no scheme
            "://missing-scheme.com",
        ],
    )
    def test_invalid_urls(self, validator, url):
        with pytest.raises(ValidationError):
            validator(url)

    def test_none_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(None)

    def test_non_string_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(12345)

    def test_error_message_mentions_url(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator("")
        assert "url" in str(exc_info.value).lower() or "URL" in str(exc_info.value)


# ════════════════════════════════════════════════════════════════════════════
# LCCSlugValidator
# ════════════════════════════════════════════════════════════════════════════


class TestLCCSlugValidator:
    """Tests for the slug format validator."""

    @pytest.fixture()
    def validator(self):
        return LCCSlugValidator()

    # ── Valid ──

    @pytest.mark.parametrize(
        "slug",
        [
            "abc",
            "product-name",
            "category-123",
            "my-long-slug-with-numbers-42",
            "a1b",
            "a" * 50,  # exactly max length
        ],
    )
    def test_valid_slugs(self, validator, slug):
        validator(slug)  # should not raise

    # ── Invalid ──

    @pytest.mark.parametrize(
        "slug",
        [
            "",
            "ab",  # too short (< 3)
            "a" * 51,  # too long (> 50)
            "Product-Name",  # uppercase
            "-leading-hyphen",
            "trailing-hyphen-",
            "double--hyphen",
            "has spaces",
            "special_chars!",
            "under_score",
        ],
    )
    def test_invalid_slugs(self, validator, slug):
        with pytest.raises(ValidationError):
            validator(slug)

    def test_none_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(None)

    def test_non_string_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(123)

    def test_slug_min_length_boundary(self, validator):
        validator("abc")  # exactly 3 — OK
        with pytest.raises(ValidationError):
            validator("ab")  # 2 — too short

    def test_slug_max_length_boundary(self, validator):
        validator("a" * 50)  # exactly 50 — OK
        with pytest.raises(ValidationError):
            validator("a" * 51)  # 51 — too long


# ════════════════════════════════════════════════════════════════════════════
# PositiveNumberValidator
# ════════════════════════════════════════════════════════════════════════════


class TestPositiveNumberValidator:
    """Tests for the positive-number validator."""

    @pytest.fixture()
    def validator(self):
        return PositiveNumberValidator()

    @pytest.fixture()
    def validator_allow_zero(self):
        return PositiveNumberValidator(allow_zero=True)

    # ── Valid (strict) ──

    @pytest.mark.parametrize("value", [1, 0.5, Decimal("100"), "99.99", 1e10])
    def test_valid_positive(self, validator, value):
        validator(value)  # should not raise

    # ── Invalid (strict) ──

    @pytest.mark.parametrize("value", [0, -1, -0.5, Decimal("-10"), "-5"])
    def test_invalid_non_positive(self, validator, value):
        with pytest.raises(ValidationError):
            validator(value)

    # ── allow_zero ──

    def test_zero_allowed(self, validator_allow_zero):
        validator_allow_zero(0)  # should not raise

    def test_negative_not_allowed_with_zero(self, validator_allow_zero):
        with pytest.raises(ValidationError):
            validator_allow_zero(-1)

    def test_positive_allowed_with_zero(self, validator_allow_zero):
        validator_allow_zero(10)  # OK

    # ── Edge cases ──

    def test_non_numeric_raises(self, validator):
        with pytest.raises(ValidationError):
            validator("not-a-number")

    def test_none_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(None)

    def test_empty_string_raises(self, validator):
        with pytest.raises(ValidationError):
            validator("")

    def test_error_message_positive(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator(-1)
        assert "positive" in str(exc_info.value).lower()


# ════════════════════════════════════════════════════════════════════════════
# DecimalValidator
# ════════════════════════════════════════════════════════════════════════════


class TestDecimalValidator:
    """Tests for decimal precision validation."""

    @pytest.fixture()
    def validator(self):
        return DecimalValidator(max_digits=10, decimal_places=2)

    @pytest.fixture()
    def strict_validator(self):
        return DecimalValidator(max_digits=5, decimal_places=2)

    # ── Valid ──

    @pytest.mark.parametrize(
        "value",
        [
            "123.45",
            "0.01",
            "99999999.99",
            0,
            1,
            Decimal("500.50"),
            "100",
        ],
    )
    def test_valid_decimals(self, validator, value):
        validator(value)  # should not raise

    # ── Invalid ──

    def test_too_many_decimal_places(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator("123.456")
        assert "decimal" in str(exc_info.value).lower()

    def test_too_many_total_digits(self, validator):
        with pytest.raises(ValidationError):
            validator("12345678901")  # 11 digits

    def test_too_many_whole_digits(self, strict_validator):
        with pytest.raises(ValidationError):
            strict_validator("1234.12")  # 4 whole digits > max_digits(5) - decimal_places(2) = 3

    def test_non_numeric_raises(self, validator):
        with pytest.raises(ValidationError):
            validator("abc")

    def test_none_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(None)

    def test_nan_raises(self, validator):
        with pytest.raises(ValidationError):
            validator("NaN")

    def test_infinity_raises(self, validator):
        with pytest.raises(ValidationError):
            validator("Infinity")

    # ── Different configurations ──

    def test_three_decimal_places(self):
        v = DecimalValidator(max_digits=10, decimal_places=3)
        v("123.456")  # OK
        with pytest.raises(ValidationError):
            v("123.4567")

    def test_zero_decimal_places(self):
        v = DecimalValidator(max_digits=5, decimal_places=0)
        v("12345")  # OK
        with pytest.raises(ValidationError):
            v("123.1")

    def test_equality(self):
        a = DecimalValidator(10, 2)
        b = DecimalValidator(10, 2)
        c = DecimalValidator(5, 2)
        assert a == b
        assert a != c


# ════════════════════════════════════════════════════════════════════════════
# PercentageValidator
# ════════════════════════════════════════════════════════════════════════════


class TestPercentageValidator:
    """Tests for percentage (0–100) validation."""

    @pytest.fixture()
    def validator(self):
        return PercentageValidator()

    # ── Valid ──

    @pytest.mark.parametrize(
        "value", [0, 50, 100, 0.0, 99.99, Decimal("50.5"), "75"]
    )
    def test_valid_percentages(self, validator, value):
        validator(value)  # should not raise

    # ── Invalid ──

    @pytest.mark.parametrize("value", [-1, -0.01, 100.01, 200, "-5", "150"])
    def test_invalid_percentages(self, validator, value):
        with pytest.raises(ValidationError):
            validator(value)

    def test_non_numeric_raises(self, validator):
        with pytest.raises(ValidationError):
            validator("abc")

    def test_none_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(None)

    def test_boundary_zero(self, validator):
        validator(0)  # exactly 0 — OK

    def test_boundary_hundred(self, validator):
        validator(100)  # exactly 100 — OK

    def test_error_message_mentions_percentage(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator(101)
        assert "percentage" in str(exc_info.value).lower() or "100" in str(
            exc_info.value
        )


# ════════════════════════════════════════════════════════════════════════════
# FileSizeValidator
# ════════════════════════════════════════════════════════════════════════════


class TestFileSizeValidator:
    """Tests for file-size limit validation."""

    @pytest.fixture()
    def validator(self):
        return FileSizeValidator()  # default 5 MB

    @pytest.fixture()
    def small_validator(self):
        return FileSizeValidator(max_size=1024)  # 1 KB

    # ── Valid ──

    def test_small_file_passes(self, validator):
        f = _make_file("doc.pdf", size=1024)
        validator(f)  # 1 KB < 5 MB

    def test_exact_limit_passes(self, validator):
        f = _make_file("doc.pdf", size=5 * 1024 * 1024)
        validator(f)  # exactly 5 MB

    def test_int_size_accepted(self, validator):
        validator(1024)  # plain int

    # ── Invalid ──

    def test_file_too_large(self, validator):
        f = _make_file("big.zip", size=6 * 1024 * 1024)
        with pytest.raises(ValidationError) as exc_info:
            validator(f)
        assert "size" in str(exc_info.value).lower() or "large" in str(
            exc_info.value
        ).lower()

    def test_small_limit_exceeded(self, small_validator):
        f = _make_file("tiny.txt", size=2048)
        with pytest.raises(ValidationError):
            small_validator(f)

    def test_zero_size_passes(self, validator):
        f = _make_file("empty.txt", size=0)
        validator(f)

    # ── Different configurations ──

    def test_custom_10mb(self):
        v = FileSizeValidator(max_size=10 * 1024 * 1024)
        f = _make_file("medium.zip", size=9 * 1024 * 1024)
        v(f)  # OK

    def test_equality(self):
        a = FileSizeValidator(1024)
        b = FileSizeValidator(1024)
        c = FileSizeValidator(2048)
        assert a == b
        assert a != c


# ════════════════════════════════════════════════════════════════════════════
# ImageDimensionValidator
# ════════════════════════════════════════════════════════════════════════════


class TestImageDimensionValidator:
    """Tests for image width/height validation (using tuple shortcut)."""

    @pytest.fixture()
    def validator(self):
        return ImageDimensionValidator(
            min_width=100, min_height=100, max_width=2000, max_height=2000
        )

    # ── Valid ──

    def test_valid_dimensions(self, validator):
        validator((800, 600))  # within range

    def test_exact_minimum(self, validator):
        validator((100, 100))

    def test_exact_maximum(self, validator):
        validator((2000, 2000))

    # ── Invalid ──

    def test_width_too_small(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator((50, 200))
        assert "width" in str(exc_info.value).lower()

    def test_height_too_small(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator((200, 50))
        assert "height" in str(exc_info.value).lower()

    def test_width_too_large(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator((3000, 500))
        assert "width" in str(exc_info.value).lower()

    def test_height_too_large(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator((500, 3000))
        assert "height" in str(exc_info.value).lower()

    def test_both_too_small(self, validator):
        with pytest.raises(ValidationError):
            validator((10, 10))

    def test_both_too_large(self, validator):
        with pytest.raises(ValidationError):
            validator((5000, 5000))

    # ── Partial constraints ──

    def test_only_max_width(self):
        v = ImageDimensionValidator(max_width=1000)
        v((999, 5000))  # height unconstrained
        with pytest.raises(ValidationError):
            v((1001, 500))

    def test_only_min_height(self):
        v = ImageDimensionValidator(min_height=200)
        v((50, 200))
        with pytest.raises(ValidationError):
            v((50, 100))

    def test_no_constraints_passes(self):
        v = ImageDimensionValidator()
        v((9999, 9999))

    def test_equality(self):
        a = ImageDimensionValidator(100, 100, 2000, 2000)
        b = ImageDimensionValidator(100, 100, 2000, 2000)
        c = ImageDimensionValidator(200, 200, 3000, 3000)
        assert a == b
        assert a != c


# ════════════════════════════════════════════════════════════════════════════
# FileExtensionValidator
# ════════════════════════════════════════════════════════════════════════════


class TestFileExtensionValidator:
    """Tests for file-extension whitelisting."""

    @pytest.fixture()
    def validator(self):
        return FileExtensionValidator(["pdf", "docx", "jpg"])

    # ── Valid ──

    @pytest.mark.parametrize("name", ["report.pdf", "doc.docx", "photo.jpg"])
    def test_valid_extensions(self, validator, name):
        f = _make_file(name)
        validator(f)

    def test_case_insensitive(self, validator):
        f = _make_file("REPORT.PDF")
        validator(f)

    def test_string_filename(self, validator):
        validator("document.pdf")  # plain string

    # ── Invalid ──

    def test_disallowed_extension(self, validator):
        f = _make_file("script.exe")
        with pytest.raises(ValidationError) as exc_info:
            validator(f)
        assert "exe" in str(exc_info.value).lower()

    def test_no_extension(self, validator):
        f = _make_file("README")
        with pytest.raises(ValidationError):
            validator(f)

    def test_double_extension_uses_last(self, validator):
        f = _make_file("archive.tar.gz")
        with pytest.raises(ValidationError):
            validator(f)  # .gz not allowed

    # ── Different configurations ──

    def test_image_set(self):
        v = FileExtensionValidator(["jpg", "jpeg", "png", "gif", "webp"])
        v(_make_file("pic.png"))
        with pytest.raises(ValidationError):
            v(_make_file("doc.pdf"))

    def test_with_leading_dots(self):
        v = FileExtensionValidator([".pdf", ".docx"])
        v(_make_file("report.pdf"))  # should work

    def test_equality(self):
        a = FileExtensionValidator(["pdf", "jpg"])
        b = FileExtensionValidator(["jpg", "pdf"])
        c = FileExtensionValidator(["png"])
        assert a == b
        assert a != c


# ════════════════════════════════════════════════════════════════════════════
# JSONValidator
# ════════════════════════════════════════════════════════════════════════════


class TestJSONValidator:
    """Tests for JSON syntax validation."""

    @pytest.fixture()
    def validator(self):
        return JSONValidator()

    # ── Valid ──

    @pytest.mark.parametrize(
        "value",
        [
            '{"key": "value"}',
            "[]",
            "[1, 2, 3]",
            '"just a string"',
            "null",
            "true",
            "42",
            '{"nested": {"a": [1, 2]}}',
        ],
    )
    def test_valid_json_strings(self, validator, value):
        validator(value)

    def test_dict_input_accepted(self, validator):
        validator({"key": "value"})

    def test_list_input_accepted(self, validator):
        validator([1, 2, 3])

    # ── Invalid ──

    @pytest.mark.parametrize(
        "value",
        [
            "{bad json}",
            "{'single_quotes': 'not json'}",
            "{key: value}",
            "",
        ],
    )
    def test_invalid_json_strings(self, validator, value):
        with pytest.raises(ValidationError):
            validator(value)

    def test_none_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(None)

    def test_non_string_non_collection_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(object())

    def test_empty_string_raises(self, validator):
        with pytest.raises(ValidationError):
            validator("")

    def test_whitespace_only_raises(self, validator):
        with pytest.raises(ValidationError):
            validator("   ")

    def test_error_message_mentions_json(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator("{bad}")
        error_str = str(exc_info.value).lower()
        assert "json" in error_str

    def test_equality(self):
        assert JSONValidator() == JSONValidator()


# ════════════════════════════════════════════════════════════════════════════
# NoHTMLValidator
# ════════════════════════════════════════════════════════════════════════════


class TestNoHTMLValidator:
    """Tests for HTML-tag rejection."""

    @pytest.fixture()
    def validator(self):
        return NoHTMLValidator()

    # ── Valid (no HTML) ──

    @pytest.mark.parametrize(
        "value",
        [
            "Hello world",
            "Price: $10 < $20",  # less-than but not a tag
            "2 > 1",
            "plain text with numbers 123",
            "email@example.com",
            "",  # empty is technically no HTML — but let's test
        ],
    )
    def test_plain_text_passes(self, validator, value):
        # empty string is fine for NoHTML (it's the field's job to require non-empty)
        if value == "":
            # empty string is valid plain text for this validator
            validator(value)
        else:
            validator(value)

    # ── Invalid (contains HTML) ──

    @pytest.mark.parametrize(
        "value",
        [
            "<b>bold</b>",
            "<script>alert(1)</script>",
            "<div class='cls'>content</div>",
            "<img src='x' onerror='alert(1)'>",
            "Hello <br> world",
            "text <a href='#'>link</a> text",
            "<p>paragraph</p>",
            "<!-- comment -->",
        ],
    )
    def test_html_rejected(self, validator, value):
        with pytest.raises(ValidationError):
            validator(value)

    def test_none_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(None)

    def test_non_string_raises(self, validator):
        with pytest.raises(ValidationError):
            validator(12345)

    def test_script_tag_rejected(self, validator):
        with pytest.raises(ValidationError) as exc_info:
            validator("<script>document.cookie</script>")
        assert "html" in str(exc_info.value).lower() or "HTML" in str(exc_info.value)

    def test_self_closing_tag_rejected(self, validator):
        with pytest.raises(ValidationError):
            validator("Hello <br/> world")

    def test_equality(self):
        assert NoHTMLValidator() == NoHTMLValidator()


# ════════════════════════════════════════════════════════════════════════════
# UniqueForTenantValidator
# ════════════════════════════════════════════════════════════════════════════


class TestUniqueForTenantValidator:
    """Tests for tenant-scoped uniqueness validation (mocked)."""

    def _mock_model(self, exists: bool = False):
        """Create a mock model class with a mocked queryset."""
        qs = MagicMock()
        qs.filter.return_value = qs
        qs.exclude.return_value = qs
        qs.exists.return_value = exists
        model = MagicMock()
        model.objects.filter.return_value = qs
        # Model does NOT have a 'tenant' attribute by default.
        if hasattr(model, "tenant"):
            del model.tenant
        return model, qs

    # ── No duplicate ──

    def test_unique_value_passes(self):
        model, qs = self._mock_model(exists=False)
        validator = UniqueForTenantValidator(model=model, field_name="sku")
        validator("SKU-001")  # should not raise

    def test_unique_value_with_tenant_attribute(self):
        model, qs = self._mock_model(exists=False)
        model.tenant = True  # mark model as having tenant FK
        validator = UniqueForTenantValidator(model=model, field_name="sku")

        with patch("django.db.connection") as mock_conn:
            mock_conn.tenant = MagicMock()
            validator("SKU-001")

    # ── Duplicate found ──

    def test_duplicate_raises(self):
        model, qs = self._mock_model(exists=True)
        validator = UniqueForTenantValidator(model=model, field_name="sku")
        with pytest.raises(ValidationError) as exc_info:
            validator("SKU-001")
        assert "unique" in str(exc_info.value).lower()

    def test_duplicate_with_custom_message(self):
        model, qs = self._mock_model(exists=True)
        validator = UniqueForTenantValidator(
            model=model,
            field_name="email",
            message="This email is already taken.",
        )
        with pytest.raises(ValidationError) as exc_info:
            validator("user@example.com")
        assert "already taken" in str(exc_info.value).lower()

    # ── Update scenario (exclude current instance) ──

    def test_update_excludes_current_instance(self):
        model, qs = self._mock_model(exists=False)
        validator = UniqueForTenantValidator(model=model, field_name="sku")
        instance = MagicMock()
        instance.pk = 42
        validator("SKU-001", instance=instance)
        qs.exclude.assert_called_once_with(pk=42)

    def test_update_duplicate_on_other_record(self):
        model, qs = self._mock_model(exists=True)
        validator = UniqueForTenantValidator(model=model, field_name="sku")
        instance = MagicMock()
        instance.pk = 42
        with pytest.raises(ValidationError):
            validator("SKU-001", instance=instance)

    # ── New instance (no pk) ──

    def test_new_instance_no_exclude(self):
        model, qs = self._mock_model(exists=False)
        validator = UniqueForTenantValidator(model=model, field_name="sku")
        instance = MagicMock()
        instance.pk = None
        validator("SKU-001", instance=instance)
        qs.exclude.assert_not_called()

    # ── Tenant FK safety filter ──

    def test_tenant_fk_filter_applied_when_model_has_tenant(self):
        model, qs = self._mock_model(exists=False)
        # Simulate model having a tenant field.
        model.tenant = True

        with patch("django.db.connection") as mock_conn:
            tenant_mock = MagicMock()
            mock_conn.tenant = tenant_mock
            validator = UniqueForTenantValidator(model=model, field_name="sku")
            validator("SKU-001")

        # The queryset should have been filtered with tenant=<tenant>.
        model.objects.filter.assert_called_once_with(sku="SKU-001")
        qs.filter.assert_called_once_with(tenant=tenant_mock)

    def test_no_tenant_fk_no_extra_filter(self):
        model, qs = self._mock_model(exists=False)
        # Ensure no 'tenant' attr on model spec.
        spec_model = MagicMock(spec=[])
        spec_model.objects = model.objects
        # Remove tenant attribute
        validator = UniqueForTenantValidator(model=model, field_name="sku")

        with patch("django.db.connection") as mock_conn:
            mock_conn.tenant = MagicMock()
            # model doesn't have 'tenant' attr since we deleted it in _mock_model
            validator("SKU-001")

        # Only the initial filter should be called, no qs.filter for tenant
        qs.filter.assert_not_called()

    # ── Equality ──

    def test_equality(self):
        model = MagicMock()
        a = UniqueForTenantValidator(model=model, field_name="sku")
        b = UniqueForTenantValidator(model=model, field_name="sku")
        c = UniqueForTenantValidator(model=model, field_name="name")
        assert a == b
        assert a != c

    # ── Error message quality ──

    def test_default_error_message_mentions_unique(self):
        model, qs = self._mock_model(exists=True)
        validator = UniqueForTenantValidator(model=model, field_name="sku")
        with pytest.raises(ValidationError) as exc_info:
            validator("SKU-001")
        assert "unique" in str(exc_info.value).lower()
