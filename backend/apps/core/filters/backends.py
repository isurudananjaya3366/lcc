"""
Custom DRF filter backends for LankaCommerce Cloud.

All backends inherit from ``rest_framework.filters.BaseFilterBackend``
(or an existing DRF filter) and implement ``filter_queryset``.

Naming conventions
------------------
- Model timestamp fields: ``created_on`` / ``updated_on``
  (project convention — NOT ``created_at`` / ``updated_at``).
- Audit user field: ``created_by`` (FK to AUTH_USER_MODEL).
- Active flag: ``is_active`` (from StatusMixin).
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import TYPE_CHECKING

from django.db import connection
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import BaseFilterBackend
from rest_framework.filters import OrderingFilter as DRFOrderingFilter
from rest_framework.filters import SearchFilter as DRFSearchFilter

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.views import APIView

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# Tenant Isolation
# ════════════════════════════════════════════════════════════════════════


class TenantFilterBackend(BaseFilterBackend):
    """
    Automatically filters querysets to the current tenant's data.

    This is the **critical security filter** for multi-tenant isolation.
    It must be listed **first** in a view's ``filter_backends`` so that
    subsequent filters operate only on tenant-scoped data.

    The current tenant is resolved from ``django.db.connection.tenant``
    which is set by the django-tenants middleware
    (``LCCTenantMiddleware``).

    Behaviour:
        * If the model has a ``tenant`` or ``tenant_id`` field the
          queryset is filtered by ``tenant=<current_tenant>``.
        * If the view has ``tenant_filter_field`` the specified field
          name is used instead.
        * If no tenant is found on the connection the backend returns
          an empty queryset (fail-secure) and logs a warning.

    Usage::

        class ProductListView(ListAPIView):
            queryset = Product.objects.all()
            filter_backends = [
                TenantFilterBackend,   # MUST be first
                LCCSearchFilter,
                LCCOrderingFilter,
            ]
    """

    # Attribute views can set to override the FK field name.
    tenant_field_name: str = "tenant"

    def filter_queryset(
        self,
        request: Request,
        queryset: QuerySet,
        view: APIView,
    ) -> QuerySet:
        tenant = getattr(connection, "tenant", None)

        if tenant is None:
            logger.warning(
                "TenantFilterBackend: No tenant found on connection. "
                "Returning empty queryset for security."
            )
            return queryset.none()

        # Allow views to override the tenant FK field name.
        field_name: str = getattr(
            view, "tenant_filter_field", self.tenant_field_name
        )

        # Only filter if the model actually has the tenant field.
        model = queryset.model
        try:
            model._meta.get_field(field_name)
        except Exception:  # noqa: BLE001
            # Model has no tenant FK (e.g. a shared-schema model).
            return queryset

        return queryset.filter(**{field_name: tenant})


# ════════════════════════════════════════════════════════════════════════
# Date Range Filtering
# ════════════════════════════════════════════════════════════════════════


class DateRangeFilterBackend(BaseFilterBackend):
    """
    Filter a queryset by date range using query parameters.

    Query parameters:
        ``date_from``  — ISO date (YYYY-MM-DD). Records on or after.
        ``date_to``    — ISO date (YYYY-MM-DD). Records on or before.

    The target model field defaults to ``created_on``.  Views can
    override this by setting ``date_filter_field``::

        class OrderListView(ListAPIView):
            date_filter_field = "order_date"

    Both, either, or neither parameter may be supplied.
    Invalid date strings are silently ignored.
    """

    date_from_param: str = "date_from"
    date_to_param: str = "date_to"
    default_field: str = "created_on"

    def filter_queryset(
        self,
        request: Request,
        queryset: QuerySet,
        view: APIView,
    ) -> QuerySet:
        field_name: str = getattr(view, "date_filter_field", self.default_field)

        date_from = self._parse_date(
            request.query_params.get(self.date_from_param)
        )
        date_to = self._parse_date(
            request.query_params.get(self.date_to_param)
        )

        if date_from is not None:
            # Make timezone-aware start of day.
            start_dt = timezone.make_aware(
                datetime.combine(date_from, datetime.min.time())
            ) if timezone.is_naive(
                datetime.combine(date_from, datetime.min.time())
            ) else datetime.combine(date_from, datetime.min.time())
            queryset = queryset.filter(**{f"{field_name}__gte": start_dt})

        if date_to is not None:
            # Make timezone-aware end of day.
            end_dt = timezone.make_aware(
                datetime.combine(date_to, datetime.max.time())
            ) if timezone.is_naive(
                datetime.combine(date_to, datetime.max.time())
            ) else datetime.combine(date_to, datetime.max.time())
            queryset = queryset.filter(**{f"{field_name}__lte": end_dt})

        return queryset

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        """Parse an ISO-8601 date string (YYYY-MM-DD).  Returns *None* on failure."""
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            return None


# ════════════════════════════════════════════════════════════════════════
# Search
# ════════════════════════════════════════════════════════════════════════


class LCCSearchFilter(DRFSearchFilter):
    """
    Enhanced search filter for LankaCommerce Cloud.

    Extends DRF's built-in ``SearchFilter`` — all standard search
    operators are available:

    ========  ============================
    Prefix    Behaviour
    ========  ============================
    *(none)*  Case-insensitive ``icontains``
    ``^``     ``istartswith``
    ``=``     Exact match
    ``@``     Full-text search (PostgreSQL)
    ``$``     Regex search
    ========  ============================

    Query parameter: ``?search=<term>``

    Views must define ``search_fields``::

        class ProductListView(ListAPIView):
            search_fields = ['^name', 'description', '=sku']

    PostgreSQL full-text search (``@`` operator) supports Sinhala and
    Tamil scripts when the database text-search configuration is set
    accordingly.
    """

    search_param = "search"


# ════════════════════════════════════════════════════════════════════════
# Ordering
# ════════════════════════════════════════════════════════════════════════


class LCCOrderingFilter(DRFOrderingFilter):
    """
    Enhanced ordering filter for LankaCommerce Cloud.

    Extends DRF's built-in ``OrderingFilter``.

    Query parameter: ``?ordering=<field>``

    Syntax:
        * ``?ordering=name``           → ascending
        * ``?ordering=-created_on``    → descending
        * ``?ordering=category,-price`` → multiple fields

    Views must define ``ordering_fields`` (list or ``'__all__'``) and
    may define a default ``ordering``::

        class ProductListView(ListAPIView):
            ordering_fields = ['name', 'price', 'created_on']
            ordering = ['-created_on']
    """

    ordering_param = "ordering"


# ════════════════════════════════════════════════════════════════════════
# Boolean Active Filter
# ════════════════════════════════════════════════════════════════════════

# Canonical truthy / falsy string values.
_TRUTHY = frozenset({"true", "1", "yes"})
_FALSY = frozenset({"false", "0", "no"})


class IsActiveFilterBackend(BaseFilterBackend):
    """
    Filter records by the ``is_active`` boolean field.

    Query parameter: ``?is_active=true`` or ``?is_active=false``

    Accepted truthy values : ``true``, ``1``, ``yes`` (case-insensitive)
    Accepted falsy values  : ``false``, ``0``, ``no``  (case-insensitive)

    If the parameter is absent or unrecognised the queryset is returned
    unfiltered.  If the model has no ``is_active`` field the filter is
    silently skipped.
    """

    def filter_queryset(
        self,
        request: Request,
        queryset: QuerySet,
        view: APIView,
    ) -> QuerySet:
        raw = request.query_params.get("is_active")
        if raw is None:
            return queryset

        lower = raw.strip().lower()
        if lower in _TRUTHY:
            is_active = True
        elif lower in _FALSY:
            is_active = False
        else:
            # Unrecognised value — skip filtering.
            return queryset

        if not hasattr(queryset.model, "is_active"):
            return queryset

        return queryset.filter(is_active=is_active)


# ════════════════════════════════════════════════════════════════════════
# Created-By Filter
# ════════════════════════════════════════════════════════════════════════


class CreatedByFilterBackend(BaseFilterBackend):
    """
    Filter records by the ``created_by`` user field.

    Query parameters:
        ``?created_by=me``   — items created by the current user
        ``?created_by=<id>`` — items created by the user with the given PK

    The special value ``me`` requires an authenticated request; for
    anonymous users it returns an empty queryset.

    If the model has no ``created_by`` field the filter is silently
    skipped.

    Usage::

        class TaskListView(ListAPIView):
            filter_backends = [CreatedByFilterBackend]
    """

    def filter_queryset(
        self,
        request: Request,
        queryset: QuerySet,
        view: APIView,
    ) -> QuerySet:
        created_by = request.query_params.get("created_by")
        if not created_by:
            return queryset

        if not hasattr(queryset.model, "created_by"):
            return queryset

        if created_by.strip().lower() == "me":
            if request.user and request.user.is_authenticated:
                return queryset.filter(created_by=request.user)
            return queryset.none()

        # Attempt to filter by user PK (integer or UUID).
        try:
            user_pk = int(created_by)
        except (ValueError, TypeError):
            # Could be a UUID string — pass through as-is.
            user_pk = created_by

        return queryset.filter(created_by_id=user_pk)


# ════════════════════════════════════════════════════════════════════════
# Modified-At Filter  (uses ``updated_on`` field)
# ════════════════════════════════════════════════════════════════════════


class ModifiedAtFilterBackend(BaseFilterBackend):
    """
    Filter records by the ``updated_on`` modification timestamp.

    Query parameters:
        ``modified_after``  — ISO date (YYYY-MM-DD). Records updated on or after.
        ``modified_before`` — ISO date (YYYY-MM-DD). Records updated on or before.

    This is useful for sync operations ("give me everything modified
    since my last sync") and audit / change-monitoring dashboards.

    The default model field is ``updated_on``.  Views may override this
    by setting ``modified_filter_field``.
    """

    modified_after_param: str = "modified_after"
    modified_before_param: str = "modified_before"
    default_field: str = "updated_on"

    def filter_queryset(
        self,
        request: Request,
        queryset: QuerySet,
        view: APIView,
    ) -> QuerySet:
        field_name: str = getattr(
            view, "modified_filter_field", self.default_field
        )

        after = self._parse_date(
            request.query_params.get(self.modified_after_param)
        )
        before = self._parse_date(
            request.query_params.get(self.modified_before_param)
        )

        if after is not None:
            start_dt = timezone.make_aware(
                datetime.combine(after, datetime.min.time())
            ) if timezone.is_naive(
                datetime.combine(after, datetime.min.time())
            ) else datetime.combine(after, datetime.min.time())
            queryset = queryset.filter(**{f"{field_name}__gte": start_dt})

        if before is not None:
            end_dt = timezone.make_aware(
                datetime.combine(before, datetime.max.time())
            ) if timezone.is_naive(
                datetime.combine(before, datetime.max.time())
            ) else datetime.combine(before, datetime.max.time())
            queryset = queryset.filter(**{f"{field_name}__lte": end_dt})

        return queryset

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        """Parse an ISO-8601 date string.  Returns *None* on failure."""
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            return None
