"""Category and Product managers and querysets.

Custom managers and querysets for the Category and Product models
providing chainable filter methods and domain-specific operations.

Category managers are built on top of django-mptt's TreeManager and
TreeQuerySet for full MPTT compatibility.

Product managers provide chainable query methods for common product
filtering:
- active(): Products with status=ACTIVE
- published(): Active and webstore-visible
- in_stock(): Products with available inventory
- by_category(): Filter by category (includes descendants)
- by_brand(): Filter by brand
- Product type filters: simple_products(), variable_products()
- featured(): Featured products only
- for_pos(): POS-visible products
- for_webstore(): Webstore-visible products
- by_status(): Filter by status value

Usage::

    Product.objects.active().by_category(category_id)
    Product.objects.published().featured()
    Product.objects.search("laptop")
"""

from django.db import models
from django.db.models import Q
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet

from apps.products.constants import PRODUCT_STATUS, PRODUCT_TYPES


class CategoryQuerySet(TreeQuerySet):
    """
    Custom queryset for Category model.

    Provides chainable methods for common category queries.
    Inherits from TreeQuerySet for MPTT compatibility.

    Usage::

        Category.objects.active().root_nodes()
        Category.objects.active().root_nodes().with_children()
    """

    def active(self):
        """
        Filter active categories only.

        Returns:
            CategoryQuerySet: Filtered to is_active=True.

        Example::

            Category.objects.active()
        """
        return self.filter(is_active=True)

    def inactive(self):
        """
        Filter inactive categories only.

        Returns:
            CategoryQuerySet: Filtered to is_active=False.
        """
        return self.filter(is_active=False)

    def root_nodes(self):
        """
        Filter root categories (no parent).

        Returns:
            CategoryQuerySet: Root categories only (level=0).

        Example::

            Category.objects.root_nodes()
        """
        return self.filter(parent__isnull=True)

    def with_children(self):
        """
        Prefetch direct children to prevent N+1 queries.

        Returns:
            CategoryQuerySet: Queryset with children prefetched.

        Example::

            roots = Category.objects.root_nodes().with_children()
            for cat in roots:
                for child in cat.children.all():  # No extra query
                    print(child.name)
        """
        return self.prefetch_related("children")

    def with_products(self):
        """
        Prefetch products relationship.

        The Product model defines ``category = ForeignKey(Category,
        related_name='products')``, so this prefetches that reverse
        relation.

        Returns:
            CategoryQuerySet: Queryset with products prefetched.

        Example::

            categories = Category.objects.active().with_products()
        """
        return self.prefetch_related("products")


class CategoryManager(TreeManager):
    """
    Custom manager for the Category model.

    Provides tree-specific operations on top of django-mptt's
    TreeManager while exposing CategoryQuerySet methods for
    chainable filters.
    """

    def get_queryset(self):
        """Return CategoryQuerySet for chainable custom methods."""
        return CategoryQuerySet(self.model, using=self._db)

    def get_tree(self, active_only=True):
        """
        Get complete category tree starting from root nodes.

        Args:
            active_only: If True, include only active categories.

        Returns:
            CategoryQuerySet: Root categories with children prefetched.

        Example::

            tree = Category.objects.get_tree()
        """
        qs = self.get_queryset()
        if active_only:
            qs = qs.active()
        return qs.root_nodes().with_children()

    def get_breadcrumbs(self, category, include_self=True):
        """
        Get breadcrumb path for a category (root → current).

        Args:
            category: Category instance.
            include_self: Include the category itself in the trail.

        Returns:
            QuerySet: Ancestors ordered root-first, optionally
            including *category* itself.

        Example::

            crumbs = Category.objects.get_breadcrumbs(smartphone)
            # [Electronics, Mobile Phones, Smartphones]
        """
        return category.get_ancestors(include_self=include_self)

    def get_descendants_ids(self, category, include_self=True):
        """
        Get flat list of descendant category IDs.

        Useful for filtering products across a whole sub-tree::

            ids = Category.objects.get_descendants_ids(electronics)
            Product.objects.filter(category_id__in=ids)

        Args:
            category: Category instance.
            include_self: Include the category's own ID.

        Returns:
            list[uuid.UUID]: Descendant (and optionally self) IDs.
        """
        descendants = category.get_descendants(include_self=include_self)
        return list(descendants.values_list("id", flat=True))

    def move_node(self, category, target, position="last-child"):
        """
        Move a category to a new position in the tree.

        Args:
            category: Category instance to move.
            target: Target parent category, or ``None`` to make root.
            position: MPTT position string — one of ``'first-child'``,
                ``'last-child'``, ``'left'``, ``'right'``.

        Returns:
            Category: The refreshed category instance.

        Raises:
            ValueError: If *category* is an ancestor of *target*
                (would create a cycle).

        Example::

            Category.objects.move_node(smartphone, electronics)
        """
        if target is not None and category.is_ancestor_of(target):
            raise ValueError(
                "Cannot move a category to its own descendant."
            )
        category.move_to(target, position=position)
        category.refresh_from_db()
        return category


# ════════════════════════════════════════════════════════════════════════
# Product QuerySet & Manager
# ════════════════════════════════════════════════════════════════════════


class ProductQuerySet(models.QuerySet):
    """
    Custom QuerySet for Product model with chainable filter methods.

    All methods return a QuerySet for chaining.

    Usage::

        Product.objects.active()
        Product.objects.published().featured()
        Product.objects.active().by_category(cat).by_brand(brand)
    """

    def active(self):
        """
        Filter products with status=ACTIVE, is_active=True, and not deleted.

        Returns:
            ProductQuerySet: Active products only.

        Example::

            Product.objects.active()
        """
        return self.filter(
            status=PRODUCT_STATUS.ACTIVE,
            is_active=True,
            is_deleted=False,
        )

    def published(self):
        """
        Filter products published in webstore.

        Returns products that are:
        - Status: ACTIVE
        - is_active: True
        - is_deleted: False
        - Webstore visible: True

        Returns:
            ProductQuerySet: Published products.

        Example::

            Product.objects.published()
        """
        return self.filter(
            status=PRODUCT_STATUS.ACTIVE,
            is_active=True,
            is_deleted=False,
            is_webstore_visible=True,
        )

    def in_stock(self):
        """
        Filter products with available inventory.

        TODO: Implement when inventory module is ready.
        Currently returns active products as placeholder.

        Future: Will filter products where stock quantity > 0.

        Returns:
            ProductQuerySet: Products in stock (currently all active).

        Example::

            Product.objects.in_stock()
        """
        # Placeholder — inventory integration in Phase-05
        return self.active()

    def by_category(self, category):
        """
        Filter products by category.

        Supports both a Category model instance and a raw ID/UUID.

        Args:
            category: Category object or category ID.

        Returns:
            ProductQuerySet: Products in the specified category.

        TODO: Include child categories when MPTT descendant
              filtering is fully integrated.

        Example::

            Product.objects.active().by_category(electronics)
            Product.objects.active().by_category(category_id)
        """
        if hasattr(category, "pk"):
            category_id = category.pk
        else:
            category_id = category

        return self.filter(category_id=category_id)

    def by_brand(self, brand):
        """
        Filter products by brand.

        Supports both a Brand model instance and a raw ID/UUID.

        Args:
            brand: Brand object or brand ID.

        Returns:
            ProductQuerySet: Products with the specified brand.

        Example::

            Product.objects.active().by_brand(apple)
            Product.objects.active().by_brand(brand_id)
        """
        if hasattr(brand, "pk"):
            brand_id = brand.pk
        else:
            brand_id = brand

        return self.filter(brand_id=brand_id)

    def simple_products(self):
        """
        Filter products with type=SIMPLE.

        Returns:
            ProductQuerySet: Simple products only.

        Example::

            Product.objects.active().simple_products()
        """
        return self.filter(product_type=PRODUCT_TYPES.SIMPLE)

    def variable_products(self):
        """
        Filter products with type=VARIABLE (products with variants).

        Returns:
            ProductQuerySet: Variable products only.

        Example::

            Product.objects.active().variable_products()
        """
        return self.filter(product_type=PRODUCT_TYPES.VARIABLE)

    def featured(self):
        """
        Filter featured products only.

        Returns:
            ProductQuerySet: Featured products.

        Example::

            Product.objects.published().featured()
        """
        return self.filter(featured=True)

    def for_pos(self):
        """
        Filter products visible in the POS system.

        Combines active status with POS visibility flag.

        Returns:
            ProductQuerySet: POS-visible active products.

        Example::

            Product.objects.for_pos()
        """
        return self.active().filter(is_pos_visible=True)

    def for_webstore(self):
        """
        Filter products visible in the webstore.

        Alias for :meth:`published`.

        Returns:
            ProductQuerySet: Webstore-visible active products.

        Example::

            Product.objects.for_webstore()
        """
        return self.published()

    def by_status(self, status):
        """
        Filter products by a given status value.

        Args:
            status: One of :class:`~apps.products.constants.PRODUCT_STATUS`
                values (e.g., ``PRODUCT_STATUS.DRAFT``).

        Returns:
            ProductQuerySet: Products with the specified status.

        Example::

            Product.objects.by_status(PRODUCT_STATUS.DRAFT)
        """
        return self.filter(status=status)


class ProductManager(models.Manager):
    """
    Custom manager for the Product model.

    Uses :class:`ProductQuerySet` to provide chainable filter methods
    directly on the manager (``Product.objects.active()``, etc.).

    Available QuerySet methods:
    - ``active()`` — Active products
    - ``published()`` — Published in webstore
    - ``in_stock()`` — Products with inventory (placeholder)
    - ``by_category(category)`` — Filter by category
    - ``by_brand(brand)`` — Filter by brand
    - ``simple_products()`` / ``variable_products()``
    - ``featured()`` — Featured products
    - ``for_pos()`` — POS-visible products
    - ``for_webstore()`` — Webstore-visible products
    - ``by_status(status)`` — Filter by status

    Manager-only methods:
    - ``search(query)`` — Full-text search across name, SKU, barcode,
      and description.

    Usage::

        Product.objects.active()
        Product.objects.published().featured()
        Product.objects.search("laptop")
    """

    def get_queryset(self):
        """Return :class:`ProductQuerySet` as base queryset."""
        return ProductQuerySet(self.model, using=self._db)

    # ------------------------------------------------------------------
    # Proxy QuerySet methods so they are available on the manager
    # ------------------------------------------------------------------

    def active(self):
        """Proxy to :meth:`ProductQuerySet.active`."""
        return self.get_queryset().active()

    def published(self):
        """Proxy to :meth:`ProductQuerySet.published`."""
        return self.get_queryset().published()

    def in_stock(self):
        """Proxy to :meth:`ProductQuerySet.in_stock`."""
        return self.get_queryset().in_stock()

    def by_category(self, category):
        """Proxy to :meth:`ProductQuerySet.by_category`."""
        return self.get_queryset().by_category(category)

    def by_brand(self, brand):
        """Proxy to :meth:`ProductQuerySet.by_brand`."""
        return self.get_queryset().by_brand(brand)

    def simple_products(self):
        """Proxy to :meth:`ProductQuerySet.simple_products`."""
        return self.get_queryset().simple_products()

    def variable_products(self):
        """Proxy to :meth:`ProductQuerySet.variable_products`."""
        return self.get_queryset().variable_products()

    def featured(self):
        """Proxy to :meth:`ProductQuerySet.featured`."""
        return self.get_queryset().featured()

    def for_pos(self):
        """Proxy to :meth:`ProductQuerySet.for_pos`."""
        return self.get_queryset().for_pos()

    def for_webstore(self):
        """Proxy to :meth:`ProductQuerySet.for_webstore`."""
        return self.get_queryset().for_webstore()

    def by_status(self, status):
        """Proxy to :meth:`ProductQuerySet.by_status`."""
        return self.get_queryset().by_status(status)

    # ------------------------------------------------------------------
    # Manager-only methods
    # ------------------------------------------------------------------

    def search(self, query):
        """
        Full-text search on products.

        Searches name, SKU, barcode, and description with weighted
        relevance.  Uses PostgreSQL full-text search when available,
        falling back to simple ``icontains`` lookups otherwise.

        Args:
            query (str): Search query string.

        Returns:
            QuerySet: Products ordered by relevance.

        Usage::

            Product.objects.search("apple iphone")
            Product.objects.search("PRD-ELEC-001")
        """
        if not query:
            return self.get_queryset()

        # Try PostgreSQL full-text search
        try:
            from django.contrib.postgres.search import (
                SearchQuery,
                SearchRank,
                SearchVector,
            )

            search_vector = (
                SearchVector("name", weight="A")
                + SearchVector("sku", weight="A")
                + SearchVector("barcode", weight="A")
                + SearchVector("description", weight="B")
            )
            search_query = SearchQuery(query)

            return (
                self.get_queryset()
                .annotate(rank=SearchRank(search_vector, search_query))
                .filter(rank__gte=0.1)
                .order_by("-rank")
            )

        except Exception:
            # Fallback for non-PostgreSQL databases (e.g. SQLite in tests)
            return self.get_queryset().filter(
                Q(name__icontains=query)
                | Q(sku__icontains=query)
                | Q(barcode__icontains=query)
                | Q(description__icontains=query)
            )


# ══════════════════════════════════════════════════════════════════════
# Bundle QuerySet & Manager
# ══════════════════════════════════════════════════════════════════════


class BundleQuerySet(models.QuerySet):
    """
    Custom QuerySet for ProductBundle model.

    Provides chainable filter methods for common bundle queries.
    """

    def active(self):
        """Return only active bundles."""
        return self.filter(is_active=True, is_deleted=False)

    def with_items(self):
        """Prefetch bundle items with related products and variants."""
        return self.prefetch_related(
            "items",
            "items__product",
            "items__variant",
        ).select_related("product")

    def by_type(self, bundle_type):
        """Filter bundles by pricing type (fixed/dynamic)."""
        return self.filter(bundle_type=bundle_type)

    def available(self):
        """Return active bundles that have at least one required item with stock."""
        from apps.products.services import BundleStockService

        active_bundles = self.active()
        available_ids = []
        for bundle in active_bundles.prefetch_related("items", "items__product", "items__variant"):
            service = BundleStockService(bundle)
            if service.get_available_stock() > 0:
                available_ids.append(bundle.pk)
        return self.filter(pk__in=available_ids)


class BundleManager(models.Manager):
    """
    Custom manager for ProductBundle model.

    Provides convenience methods for common bundle queries.
    """

    def get_queryset(self):
        return BundleQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def with_items(self):
        return self.get_queryset().with_items()

    def by_type(self, bundle_type):
        return self.get_queryset().by_type(bundle_type)

    def available(self):
        return self.get_queryset().available()
