"""
Reusable FilterSet classes for LankaCommerce Cloud.

The ``BaseFilterSet`` provides common filter fields that appear on most
tenant-schema models (``is_active``, ``created_on``, ``updated_on``).
App-specific FilterSets should inherit from ``BaseFilterSet`` and add
model-specific filters.

Field naming follows the project convention:
    * ``created_on`` — creation timestamp  (NOT ``created_at``)
    * ``updated_on`` — modification timestamp  (NOT ``updated_at``)
"""

from __future__ import annotations

import django_filters
from django_filters import BooleanFilter, DateFilter, FilterSet


class BaseFilterSet(FilterSet):
    """
    Base FilterSet with common filter fields for LankaCommerce Cloud models.

    Inherit from this class in app-specific FilterSets to get automatic
    support for the common query parameters listed below.

    Common query parameters:
        ``?is_active=true``           — active/inactive records
        ``?created_after=YYYY-MM-DD`` — records created on or after date
        ``?created_before=YYYY-MM-DD``— records created on or before date
        ``?modified_after=YYYY-MM-DD``— records modified on or after date
        ``?modified_before=YYYY-MM-DD``— records modified on or before date

    Usage::

        class ProductFilter(BaseFilterSet):
            class Meta:
                model = Product
                fields = ['category', 'price']
    """

    # ── Boolean active filter ──────────────────────────────────────────
    is_active = BooleanFilter(
        field_name="is_active",
        label="Active status",
        help_text="Filter by active status (true/false).",
    )

    # ── Creation date range ────────────────────────────────────────────
    created_after = DateFilter(
        field_name="created_on",
        lookup_expr="gte",
        label="Created after",
        help_text="Records created on or after this date (YYYY-MM-DD).",
    )
    created_before = DateFilter(
        field_name="created_on",
        lookup_expr="lte",
        label="Created before",
        help_text="Records created on or before this date (YYYY-MM-DD).",
    )

    # ── Modification date range ────────────────────────────────────────
    modified_after = DateFilter(
        field_name="updated_on",
        lookup_expr="gte",
        label="Modified after",
        help_text="Records modified on or after this date (YYYY-MM-DD).",
    )
    modified_before = DateFilter(
        field_name="updated_on",
        lookup_expr="lte",
        label="Modified before",
        help_text="Records modified on or before this date (YYYY-MM-DD).",
    )

    class Meta:
        # No model — this is abstract. Subclasses MUST define model and
        # fields in their own Meta.
        abstract = True
        fields: list[str] = []
