"""
LankaCommerce Cloud – Validators Package (SP12 Tasks 33-48).

Reusable validators for data validation across all LankaCommerce Cloud
applications.  All validators are callable classes that raise
``django.core.exceptions.ValidationError`` on invalid input.

Categories:
    **Basic:**   Email, URL, Slug, Positive Number
    **Numeric:** Decimal, Percentage
    **Files:**   File Size, Image Dimensions, File Extensions
    **Content:** JSON, No-HTML
    **Tenant:**  Unique-for-Tenant

Usage::

    from apps.core.validators import LCCEmailValidator, DecimalValidator

    validator = LCCEmailValidator()
    validator("user@example.com")  # OK

    decimal_validator = DecimalValidator(max_digits=10, decimal_places=2)
    decimal_validator("123.45")  # OK
"""

__version__ = "1.0.0"

from .common import (
    DecimalValidator,
    LCCEmailValidator,
    LCCSlugValidator,
    LCCURLValidator,
    PercentageValidator,
    PositiveNumberValidator,
)
from .content import (
    JSONValidator,
    NoHTMLValidator,
    UniqueForTenantValidator,
)
from .file_validators import (
    FileExtensionValidator,
    FileSizeValidator,
    ImageDimensionValidator,
)

__all__ = [
    # Basic Validators
    "LCCEmailValidator",
    "LCCURLValidator",
    "LCCSlugValidator",
    "PositiveNumberValidator",
    # Numeric Validators
    "DecimalValidator",
    "PercentageValidator",
    # File Validators
    "FileSizeValidator",
    "ImageDimensionValidator",
    "FileExtensionValidator",
    # Content Validators
    "JSONValidator",
    "NoHTMLValidator",
    # Tenant Validators
    "UniqueForTenantValidator",
]
