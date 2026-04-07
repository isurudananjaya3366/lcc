"""
Customer search service.

Provides full-text search via PostgreSQL ``SearchVector`` and
convenience lookup methods for phone, email, and customer code.
"""

from __future__ import annotations

import logging
import re

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Q, QuerySet

logger = logging.getLogger(__name__)

# Pattern to detect a customer code like CUST-00001
_CODE_PATTERN = re.compile(r"^[A-Z]{2,10}-\d+$", re.IGNORECASE)

# Pattern to detect a phone-number-like input (starts with + or 0, digits)
_PHONE_PATTERN = re.compile(r"^[\+0]\d[\d\s\-]{5,}$")


class CustomerSearchService:
    """
    Search and lookup operations for customers.

    ``search()`` uses PostgreSQL full-text search on the
    ``search_vector`` field (GIN-indexed).

    ``quick_search()`` dispatches to the appropriate method based
    on the input pattern (code, phone, or free-text).
    """

    # ── Full-text search ────────────────────────────────────────────

    @classmethod
    def search(
        cls,
        query_text: str,
        *,
        active_only: bool = True,
        limit: int = 50,
    ) -> QuerySet:
        """
        Full-text search on the ``search_vector`` field.

        Falls back to ``icontains`` on key text fields when the
        ``search_vector`` column is not yet populated.
        """
        from apps.customers.models import Customer

        qs = Customer.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)

        if not query_text or not query_text.strip():
            return qs.none()

        query_text = query_text.strip()

        # Try SearchVector-based search first
        try:
            search_query = SearchQuery(query_text, search_type="plain")
            results = (
                qs.filter(search_vector=search_query)
                .annotate(rank=SearchRank("search_vector", search_query))
                .order_by("-rank")[:limit]
            )
            # Force evaluation to detect if search_vector works
            if results.exists() or len(query_text) > 2:
                return results
        except Exception:
            logger.debug("search_vector not available, falling back to icontains")

        # Fallback: icontains on multiple fields
        return (
            qs.filter(
                Q(first_name__icontains=query_text)
                | Q(last_name__icontains=query_text)
                | Q(display_name__icontains=query_text)
                | Q(business_name__icontains=query_text)
                | Q(email__icontains=query_text)
                | Q(phone__icontains=query_text)
                | Q(customer_code__icontains=query_text)
            )
            .distinct()[:limit]
        )

    # ── Quick search (auto-detect input type) ───────────────────────

    @classmethod
    def quick_search(
        cls,
        query_text: str,
        *,
        active_only: bool = True,
        limit: int = 20,
    ) -> QuerySet:
        """
        Smart search that detects input type and dispatches:

        - Customer code pattern (CUST-00001) → code lookup
        - Phone pattern (+94… / 07…) → phone lookup
        - Otherwise → full-text search
        """
        if not query_text or not query_text.strip():
            from apps.customers.models import Customer
            return Customer.objects.none()

        query_text = query_text.strip()

        if _CODE_PATTERN.match(query_text):
            return cls._lookup_by_code(query_text, active_only=active_only)

        if _PHONE_PATTERN.match(query_text):
            return cls.lookup_by_phone(query_text, active_only=active_only, limit=limit)

        return cls.search(query_text, active_only=active_only, limit=limit)

    # ── Lookup by phone ─────────────────────────────────────────────

    @classmethod
    def lookup_by_phone(
        cls,
        phone: str,
        *,
        active_only: bool = True,
        limit: int = 20,
    ) -> QuerySet:
        """
        Find customers by phone number.

        Searches both ``Customer.phone`` / ``Customer.mobile`` and
        related ``CustomerPhone`` records. Normalises the input by
        stripping spaces and dashes.
        """
        from apps.customers.models import Customer

        normalised = re.sub(r"[\s\-]", "", phone)

        qs = Customer.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)

        return (
            qs.filter(
                Q(phone__icontains=normalised)
                | Q(mobile__icontains=normalised)
                | Q(phone_numbers__phone_number__icontains=normalised)
            )
            .distinct()[:limit]
        )

    # ── Lookup by email ─────────────────────────────────────────────

    @classmethod
    def lookup_by_email(
        cls,
        email: str,
        *,
        active_only: bool = True,
    ) -> QuerySet:
        """
        Find customers by email (case-insensitive exact match).
        """
        from apps.customers.models import Customer

        qs = Customer.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)

        return qs.filter(email__iexact=email.strip())

    # ── Lookup by code ──────────────────────────────────────────────

    @classmethod
    def _lookup_by_code(
        cls,
        code: str,
        *,
        active_only: bool = True,
    ) -> QuerySet:
        """
        Find a customer by their customer code.
        """
        from apps.customers.models import Customer

        qs = Customer.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)

        return qs.filter(customer_code__iexact=code.strip())
