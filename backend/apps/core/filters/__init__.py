"""
Filter backends and FilterSet classes for LankaCommerce Cloud API.

Provides reusable DRF filter backends and a BaseFilterSet for declarative
filtering across all tenant-scoped API endpoints.

Filter Backends:
    TenantFilterBackend      — Automatic tenant isolation (must be first)
    DateRangeFilterBackend   — Filter by created_on date range
    LCCSearchFilter          — Enhanced search with search_fields
    LCCOrderingFilter        — Enhanced ordering with ordering_fields
    IsActiveFilterBackend    — Boolean is_active filtering
    CreatedByFilterBackend   — Filter by created_by user
    ModifiedAtFilterBackend  — Filter by updated_on date range

FilterSets:
    BaseFilterSet            — Reusable base with common filter fields
"""

__version__ = "1.0.0"

from .backends import (
    CreatedByFilterBackend,
    DateRangeFilterBackend,
    IsActiveFilterBackend,
    LCCOrderingFilter,
    LCCSearchFilter,
    ModifiedAtFilterBackend,
    TenantFilterBackend,
)
from .filtersets import BaseFilterSet

__all__ = [
    # Filter Backends
    "TenantFilterBackend",
    "DateRangeFilterBackend",
    "LCCSearchFilter",
    "LCCOrderingFilter",
    "IsActiveFilterBackend",
    "CreatedByFilterBackend",
    "ModifiedAtFilterBackend",
    # FilterSets
    "BaseFilterSet",
]
