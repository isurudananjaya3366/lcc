"""
Variant managers and querysets for ProductVariant.

Custom QuerySet and Manager providing chainable filter methods
and lookup utilities for variant operations.

QuerySet methods (all chainable):
    - ``active()``       — Active, non-deleted variants
    - ``inactive()``     — Inactive variants
    - ``in_stock()``     — Variants with stock (placeholder)
    - ``for_product()``  — Filter by parent product
    - ``by_option()``    — Filter by option value(s)
    - ``with_prices()``  — Prefetch price data
    - ``with_stock()``   — Prefetch stock data
    - ``with_options()`` — Prefetch option values and types

Manager-only methods:
    - ``get_by_options(product, options)`` — Find exact variant match

Usage::

    ProductVariant.objects.active().for_product(product_id)
    ProductVariant.objects.active().by_option(size_medium)
    ProductVariant.objects.get_by_options(product, {'Size': 'M'})
"""

import logging

from django.db import models
from django.db.models import Count

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# VariantQuerySet
# ════════════════════════════════════════════════════════════════════════


class VariantQuerySet(models.QuerySet):
    """
    Custom QuerySet for ProductVariant with chainable filter methods.

    Provides reusable, chainable query methods for common variant
    filtering and prefetch optimisation patterns.

    All methods return a QuerySet instance, enabling chaining::

        ProductVariant.objects.active().for_product(pid).with_options()
    """

    # ── Filtering ───────────────────────────────────────────────────

    def active(self):
        """
        Return only active, non-deleted variants.

        Returns:
            VariantQuerySet: Filtered to ``is_active=True`` and
            ``is_deleted=False``.

        Example::

            ProductVariant.objects.active()
        """
        return self.filter(is_active=True, is_deleted=False)

    def inactive(self):
        """
        Return only inactive variants.

        Returns:
            VariantQuerySet: Filtered to ``is_active=False``.

        Example::

            ProductVariant.objects.inactive()
        """
        return self.filter(is_active=False)

    def in_stock(self):
        """
        Return variants with available stock.

        .. note::
            Placeholder implementation — returns ``active()`` until
            the inventory / VariantStock module is ready (Phase-05).

        Future implementation will annotate ``stock_qty`` from the
        ``VariantStock`` model and filter ``stock_qty__gt=0``.

        Returns:
            VariantQuerySet: Variants in stock (currently all active).

        Example::

            ProductVariant.objects.active().in_stock()
        """
        # Placeholder — inventory integration in Phase-05
        return self.active()

    def for_product(self, product):
        """
        Return variants belonging to a specific product.

        Args:
            product: Product instance or product ID (UUID).

        Returns:
            VariantQuerySet: Variants belonging to the product.

        Example::

            ProductVariant.objects.active().for_product(product)
            ProductVariant.objects.for_product(product_id)
        """
        if hasattr(product, "pk"):
            product = product.pk
        return self.filter(product_id=product)

    def by_option(self, option_value):
        """
        Return variants with specific option value(s).

        Supports a single ``VariantOptionValue`` instance or a list.
        When a list is provided, **AND** logic is applied — the
        variant must have *all* specified option values.

        Args:
            option_value: Single ``VariantOptionValue`` or list of
                values.

        Returns:
            VariantQuerySet: Variants matching the option criteria.

        Examples::

            # Single option
            ProductVariant.objects.by_option(size_medium)

            # Multiple options (AND)
            ProductVariant.objects.by_option([size_medium, color_red])
        """
        if isinstance(option_value, (list, tuple)):
            qs = self
            for val in option_value:
                qs = qs.filter(option_values=val)
            return qs
        return self.filter(option_values=option_value)

    # ── Prefetch Optimisation ───────────────────────────────────────

    def with_prices(self):
        """
        Prefetch price-related data for query optimisation.

        .. note::
            Placeholder — ``VariantPrice`` model does not exist yet.
            Currently prefetches option values and selects the parent
            product as a useful baseline.

        Returns:
            VariantQuerySet: QuerySet with related data prefetched.

        Example::

            variants = ProductVariant.objects.active().with_prices()
        """
        return self.select_related("product").prefetch_related(
            "option_values",
            "option_values__option_type",
        )

    def with_stock(self):
        """
        Prefetch stock-related data for query optimisation.

        .. note::
            Placeholder — ``VariantStock`` model does not exist yet.
            Currently prefetches option values and selects the parent
            product as a useful baseline.

        Returns:
            VariantQuerySet: QuerySet with related data prefetched.

        Example::

            variants = ProductVariant.objects.active().with_stock()
        """
        return self.select_related("product").prefetch_related(
            "option_values",
            "option_values__option_type",
        )

    def with_options(self):
        """
        Prefetch option values and their types for display.

        Optimises the common pattern of iterating variants and
        accessing their option value labels/types.

        Returns:
            VariantQuerySet: QuerySet with option data prefetched.

        Example::

            variants = ProductVariant.objects.for_product(pid).with_options()
            for v in variants:
                for ov in v.option_values.all():  # No extra query
                    print(ov.option_type.name, ov.value)
        """
        return self.prefetch_related(
            "option_values",
            "option_values__option_type",
            "variant_options",
        )


# ════════════════════════════════════════════════════════════════════════
# VariantManager
# ════════════════════════════════════════════════════════════════════════


class VariantManager(models.Manager):
    """
    Custom manager for ProductVariant.

    Uses :class:`VariantQuerySet` for chainable filter methods and
    provides additional manager-level lookup methods.

    QuerySet methods (via proxy):
        ``active()``, ``inactive()``, ``in_stock()``,
        ``for_product()``, ``by_option()``, ``with_prices()``,
        ``with_stock()``, ``with_options()``

    Manager-only methods:
        ``get_by_options(product, options)``

    Usage::

        ProductVariant.objects.active()
        ProductVariant.objects.active().for_product(product_id)
        ProductVariant.objects.get_by_options(product, {'Size': 'M'})
    """

    def get_queryset(self):
        """Return :class:`VariantQuerySet` as base queryset."""
        return VariantQuerySet(self.model, using=self._db)

    # ------------------------------------------------------------------
    # Proxy QuerySet methods so they are available on the manager
    # ------------------------------------------------------------------

    def active(self):
        """Proxy to :meth:`VariantQuerySet.active`."""
        return self.get_queryset().active()

    def inactive(self):
        """Proxy to :meth:`VariantQuerySet.inactive`."""
        return self.get_queryset().inactive()

    def in_stock(self):
        """Proxy to :meth:`VariantQuerySet.in_stock`."""
        return self.get_queryset().in_stock()

    def for_product(self, product):
        """Proxy to :meth:`VariantQuerySet.for_product`."""
        return self.get_queryset().for_product(product)

    def by_option(self, option_value):
        """Proxy to :meth:`VariantQuerySet.by_option`."""
        return self.get_queryset().by_option(option_value)

    def with_prices(self):
        """Proxy to :meth:`VariantQuerySet.with_prices`."""
        return self.get_queryset().with_prices()

    def with_stock(self):
        """Proxy to :meth:`VariantQuerySet.with_stock`."""
        return self.get_queryset().with_stock()

    def with_options(self):
        """Proxy to :meth:`VariantQuerySet.with_options`."""
        return self.get_queryset().with_options()

    # ------------------------------------------------------------------
    # Manager-only methods
    # ------------------------------------------------------------------

    def get_by_options(self, product, options):
        """
        Get variant by exact option combination.

        Finds the variant for the given product that matches
        **exactly** the specified option values — no more, no fewer.

        Args:
            product: Product instance or product ID.
            options: List of ``VariantOptionValue`` instances, **or**
                dict mapping option type names to values, e.g.
                ``{'Size': 'Medium', 'Color': 'Red'}``.

        Returns:
            ProductVariant or None: Matching variant, or ``None`` if
            no exact match is found.

        Examples::

            # By option value instances
            variant = ProductVariant.objects.get_by_options(
                product, [size_m, color_red]
            )

            # By dict
            variant = ProductVariant.objects.get_by_options(
                product, {'Size': 'Medium', 'Color': 'Red'}
            )
        """
        from apps.products.models.variant_option import VariantOptionValue

        # ── Resolve dict to option value instances ──────────────────
        if isinstance(options, dict):
            option_values = []
            for type_name, value in options.items():
                try:
                    ov = VariantOptionValue.objects.get(
                        option_type__name=type_name,
                        value=value,
                    )
                    option_values.append(ov)
                except VariantOptionValue.DoesNotExist:
                    logger.debug(
                        "Option value not found: %s=%s",
                        type_name,
                        value,
                    )
                    return None
            options = option_values

        if not options:
            return None

        # ── Step 1: Find variants with ALL specified option values ──
        qs = self.get_queryset().for_product(product)
        for opt_val in options:
            qs = qs.filter(option_values=opt_val)

        candidate_ids = list(qs.values_list("pk", flat=True))
        if not candidate_ids:
            return None

        # ── Step 2: Ensure exact match (no extra option values) ─────
        # Use a clean queryset to avoid count inflation from the
        # multiple M2M JOINs created in step 1.
        exact_qs = (
            self.get_queryset()
            .filter(pk__in=candidate_ids)
            .annotate(num_options=Count("variant_options"))
            .filter(num_options=len(options))
        )

        return exact_qs.first()
