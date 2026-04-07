"""
LankaCommerce Cloud – Common Validators (SP12 Tasks 35-40).

Basic and numeric validators used across all LankaCommerce Cloud applications.

Validators:
    LCCEmailValidator       — Stricter email validation with domain checks
    LCCURLValidator         — URL validation for HTTP/HTTPS schemes
    LCCSlugValidator        — Slug format (lowercase, hyphens, 3-50 chars)
    PositiveNumberValidator — Ensures value > 0 (optionally >= 0)
    DecimalValidator        — Validates decimal precision (max_digits, decimal_places)
    PercentageValidator     — Validates 0-100 inclusive range
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator as DjangoEmailValidator
from django.core.validators import URLValidator as DjangoURLValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


# ════════════════════════════════════════════════════════════════════════
# Email Validator
# ════════════════════════════════════════════════════════════════════════

# Common disposable / temporary email domains to block.
_DISPOSABLE_DOMAINS: frozenset[str] = frozenset(
    {
        "tempmail.com",
        "guerrillamail.com",
        "guerrillamail.net",
        "guerrillamail.org",
        "throwaway.email",
        "mailinator.com",
        "yopmail.com",
        "sharklasers.com",
        "guerrillamailblock.com",
        "grr.la",
        "dispostable.com",
        "trashmail.com",
        "trashmail.net",
        "trashmail.org",
        "10minutemail.com",
        "tempail.com",
        "fakeinbox.com",
        "temp-mail.org",
        "maildrop.cc",
    }
)


@deconstructible
class LCCEmailValidator(DjangoEmailValidator):
    """
    Stricter email validator for LankaCommerce Cloud.

    Extends Django's built-in ``EmailValidator`` with:

    * RFC 5322 format compliance (inherited)
    * Maximum length of 254 characters
    * Rejection of disposable / temporary email domains
    * Basic domain validation (must contain at least one dot)

    Usage::

        validator = LCCEmailValidator()
        validator("user@example.com")  # OK
        validator("bad@@example")      # raises ValidationError
    """

    message = _("Enter a valid email address.")
    code = "invalid_email"

    def __call__(self, value: str) -> None:  # type: ignore[override]
        # --- basic type / emptiness guard ---
        if not isinstance(value, str) or not value:
            raise ValidationError(
                _("Enter a valid email address."),
                code=self.code,
            )

        # --- length check (RFC 5321) ---
        if len(value) > 254:
            raise ValidationError(
                _("Email address must be at most 254 characters."),
                code=self.code,
            )

        # --- parent format validation ---
        super().__call__(value)

        # --- domain-level checks ---
        try:
            _local, domain = value.rsplit("@", 1)
        except ValueError:
            raise ValidationError(self.message, code=self.code)

        domain_lower = domain.lower()

        # Must contain at least one dot (simple MX-like heuristic)
        if "." not in domain_lower:
            raise ValidationError(
                _("Email domain '%(domain)s' is not valid."),
                code=self.code,
                params={"domain": domain},
            )

        # Block disposable email providers
        if domain_lower in _DISPOSABLE_DOMAINS:
            raise ValidationError(
                _(
                    "Disposable email addresses are not allowed. "
                    "Please use a permanent email address."
                ),
                code="disposable_email",
            )


# ════════════════════════════════════════════════════════════════════════
# URL Validator
# ════════════════════════════════════════════════════════════════════════


@deconstructible
class LCCURLValidator(DjangoURLValidator):
    """
    URL validator restricted to HTTP and HTTPS schemes.

    Extends Django's ``URLValidator`` and locks ``schemes`` to
    ``['http', 'https']``.  Localhost URLs are accepted for development
    convenience.

    Usage::

        validator = LCCURLValidator()
        validator("https://example.com")  # OK
        validator("ftp://files.example.com")  # raises ValidationError
    """

    schemes = ["http", "https"]
    message = _("Enter a valid URL (http or https).")
    code = "invalid_url"

    def __call__(self, value: str) -> None:  # type: ignore[override]
        if not isinstance(value, str) or not value:
            raise ValidationError(self.message, code=self.code)
        super().__call__(value)


# ════════════════════════════════════════════════════════════════════════
# Slug Validator
# ════════════════════════════════════════════════════════════════════════

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

_SLUG_MIN_LENGTH = 3
_SLUG_MAX_LENGTH = 50


@deconstructible
class LCCSlugValidator:
    """
    Validate URL-friendly slug strings.

    Rules:
        * Lowercase letters, digits, and hyphens only
        * Must start and end with an alphanumeric character
        * No consecutive hyphens
        * Length between 3 and 50 characters (inclusive)

    Valid: ``"product-name"``, ``"category-123"``
    Invalid: ``"-product"``, ``"product--name"``, ``"AB"``, ``"Product Name"``

    Usage::

        validator = LCCSlugValidator()
        validator("my-product")  # OK
    """

    message = _(
        "Enter a valid slug: lowercase letters, numbers, and single hyphens only "
        "(%(min)d–%(max)d characters)."
    )
    code = "invalid_slug"

    def __call__(self, value: str) -> None:
        if not isinstance(value, str) or not value:
            raise ValidationError(
                self.message,
                code=self.code,
                params={"min": _SLUG_MIN_LENGTH, "max": _SLUG_MAX_LENGTH},
            )

        if len(value) < _SLUG_MIN_LENGTH:
            raise ValidationError(
                _("Slug must be at least %(min)d characters."),
                code=self.code,
                params={"min": _SLUG_MIN_LENGTH},
            )

        if len(value) > _SLUG_MAX_LENGTH:
            raise ValidationError(
                _("Slug must be at most %(max)d characters."),
                code=self.code,
                params={"max": _SLUG_MAX_LENGTH},
            )

        if not _SLUG_RE.match(value):
            raise ValidationError(
                self.message,
                code=self.code,
                params={"min": _SLUG_MIN_LENGTH, "max": _SLUG_MAX_LENGTH},
            )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LCCSlugValidator)


# ════════════════════════════════════════════════════════════════════════
# Positive Number Validator
# ════════════════════════════════════════════════════════════════════════


@deconstructible
class PositiveNumberValidator:
    """
    Validate that a numeric value is strictly positive (> 0).

    Set ``allow_zero=True`` to accept zero as valid (>= 0).

    Supports ``int``, ``float``, ``Decimal``, and string representations
    convertible to ``Decimal``.

    Use cases:
        * Prices
        * Quantities
        * Stock levels

    Usage::

        validator = PositiveNumberValidator()
        validator(10)    # OK
        validator(0)     # raises ValidationError
        validator(-5)    # raises ValidationError

        validator_z = PositiveNumberValidator(allow_zero=True)
        validator_z(0)   # OK
    """

    code = "invalid_positive_number"

    def __init__(self, allow_zero: bool = False) -> None:
        self.allow_zero = allow_zero
        if allow_zero:
            self.message = _("Value must be zero or positive.")
        else:
            self.message = _("Value must be a positive number.")

    def __call__(self, value: int | float | Decimal | str) -> None:
        try:
            num = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(
                _("Invalid number format."),
                code=self.code,
            )

        if self.allow_zero:
            if num < 0:
                raise ValidationError(self.message, code=self.code)
        else:
            if num <= 0:
                raise ValidationError(self.message, code=self.code)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PositiveNumberValidator) and self.allow_zero == other.allow_zero


# ════════════════════════════════════════════════════════════════════════
# Decimal Validator
# ════════════════════════════════════════════════════════════════════════


@deconstructible
class DecimalValidator:
    """
    Validate decimal precision (total digits and decimal places).

    Parameters:
        max_digits:     Maximum total number of digits (default ``10``)
        decimal_places: Maximum number of digits after the decimal point (default ``2``)

    Use cases:
        * Prices:      ``DecimalValidator(10, 2)`` → ``99999999.99``
        * Rates:       ``DecimalValidator(5, 2)``  → ``999.99``
        * Quantities:  ``DecimalValidator(10, 3)`` → ``9999999.999``

    Usage::

        validator = DecimalValidator(max_digits=10, decimal_places=2)
        validator("123.45")   # OK
        validator("123.456")  # raises ValidationError (too many decimal places)
    """

    code = "invalid_decimal"

    def __init__(self, max_digits: int = 10, decimal_places: int = 2) -> None:
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def __call__(self, value: int | float | Decimal | str) -> None:
        try:
            d = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(
                _("Invalid decimal format."),
                code=self.code,
            )

        if d.is_nan() or d.is_infinite():
            raise ValidationError(
                _("Value must be a finite number."),
                code=self.code,
            )

        # Normalize to remove trailing zeros for consistent counting.
        sign, digits, exponent = d.as_tuple()
        num_digits = len(digits)

        # Number of digits after decimal point.
        if exponent < 0:
            decimals = abs(exponent)
        else:
            decimals = 0

        # Total significant digits (whole + decimal).
        whole_digits = num_digits + exponent if exponent < 0 else num_digits + exponent
        # More robust: total digits = max(num_digits, whole_digits + decimals)
        # Use tuple math directly:
        if exponent >= 0:
            # e.g. Decimal("1E+2") → digits=(1,), exp=2 → 100, total_digits=1, decimals=0
            total_digits = num_digits + exponent
            decimals = 0
        else:
            # e.g. Decimal("123.45") → digits=(1,2,3,4,5), exp=-2
            decimals = abs(exponent)
            whole_count = max(num_digits - decimals, 0)
            total_digits = whole_count + decimals

        if decimals > self.decimal_places:
            raise ValidationError(
                _(
                    "Ensure that there are no more than %(decimal_places)d decimal places."
                ),
                code=self.code,
                params={"decimal_places": self.decimal_places},
            )

        if total_digits > self.max_digits:
            raise ValidationError(
                _(
                    "Ensure that there are no more than %(max_digits)d digits in total."
                ),
                code=self.code,
                params={"max_digits": self.max_digits},
            )

        max_whole = self.max_digits - self.decimal_places
        whole = total_digits - decimals
        if whole > max_whole:
            raise ValidationError(
                _(
                    "Ensure that there are no more than %(max_whole)d digits before "
                    "the decimal point."
                ),
                code=self.code,
                params={"max_whole": max_whole},
            )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, DecimalValidator)
            and self.max_digits == other.max_digits
            and self.decimal_places == other.decimal_places
        )


# ════════════════════════════════════════════════════════════════════════
# Percentage Validator
# ════════════════════════════════════════════════════════════════════════


@deconstructible
class PercentageValidator:
    """
    Validate that a value is a percentage in the range 0–100 (inclusive).

    Decimals are allowed (e.g. ``99.5``).

    Use cases:
        * Discount percentages
        * Tax rates
        * Completion indicators

    Usage::

        validator = PercentageValidator()
        validator(50)    # OK
        validator(100)   # OK
        validator(100.1) # raises ValidationError
    """

    message = _("Percentage must be between 0 and 100.")
    code = "invalid_percentage"

    def __call__(self, value: int | float | Decimal | str) -> None:
        try:
            num = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(
                _("Invalid percentage format."),
                code=self.code,
            )

        if num < 0 or num > 100:
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PercentageValidator)
