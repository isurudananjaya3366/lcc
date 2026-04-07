"""
Pagination classes for LankaCommerce Cloud API.

Provides reusable, configurable pagination classes extending
Django REST Framework's built-in pagination.

Exports:
    - StandardPagination: Page number pagination (default 20, max 100)
    - LCCCursorPagination: Cursor-based pagination for real-time data
    - LCCLimitOffsetPagination: SQL-style limit/offset pagination
    - NoPagination: Disables pagination for small datasets
"""

__version__ = "1.0.0"

from .cursor import LCCCursorPagination
from .limit_offset import LCCLimitOffsetPagination
from .none import NoPagination
from .standard import StandardPagination

__all__ = [
    "StandardPagination",
    "LCCCursorPagination",
    "LCCLimitOffsetPagination",
    "NoPagination",
]
