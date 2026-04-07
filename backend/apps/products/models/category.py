"""
Category model for the products application.

Defines the Category model which supports hierarchical product
categorization using MPTT (Modified Preorder Tree Traversal).
Categories are tenant-specific — each tenant has its own
independent category tree managed via django-tenants schema
isolation.

MPTT provides efficient tree queries (ancestors, descendants,
siblings) without recursive SQL. The tree structure is maintained
via four auto-managed fields: lft, rght, tree_id, level.
"""

from django.db import models
from django.utils.text import slugify
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from apps.core.mixins import UUIDMixin, TimestampMixin
from apps.products.models.managers import CategoryManager


def category_image_upload_path(instance, filename):
    """Generate upload path for category images."""
    return f"categories/{instance.slug}/{filename}"


class Category(UUIDMixin, TimestampMixin, MPTTModel):
    """
    Product category with MPTT-powered hierarchical support.

    Uses django-mptt for efficient tree operations. The tree
    structure is maintained via auto-managed fields (lft, rght,
    tree_id, level). Root categories have parent=None.

    Each category has a unique slug within its tenant schema
    (django-tenants provides schema isolation).

    Fields:
        name: Display name of the category (max 255 chars).
        slug: URL-friendly identifier, unique per tenant schema.
        parent: TreeForeignKey for MPTT-managed category hierarchy.
            Null for root categories.
        description: Optional rich-text description.
        image: Optional category image for branding/display.
        icon: Optional CSS icon class for UI rendering.
        is_active: Controls category visibility. Inactive categories
            and their products are hidden from the storefront but
            remain accessible in the admin.
        display_order: Integer for controlling display order within
            the same tree level.
        seo_title: Meta title for search engine optimization.
        seo_description: Meta description for search results.
        seo_keywords: Comma-separated keywords (legacy SEO).

    MPTT auto-managed fields (do not set manually):
        level: Depth in the tree (0 for root).
        lft: Left value for nested-set traversal.
        rght: Right value for nested-set traversal.
        tree_id: Identifier grouping nodes in the same tree.
    """

    # ── Core Fields ─────────────────────────────────────────────────
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Category Name",
        help_text="Display name of the category.",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug",
        help_text="URL-friendly identifier. Unique per tenant schema.",
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="Description",
        help_text="Optional description for the category.",
    )

    # ── Hierarchy (MPTT) ────────────────────────────────────────────
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Parent Category",
        help_text="Parent category. Null for root categories.",
    )

    # ── Branding ────────────────────────────────────────────────────
    image = models.ImageField(
        upload_to=category_image_upload_path,
        null=True,
        blank=True,
        verbose_name="Category Image",
        help_text="Optional image for category branding.",
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Icon Class",
        help_text="CSS icon class (e.g., 'fas fa-mobile-alt').",
    )

    # ── Visibility & Ordering ───────────────────────────────────────
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Controls category visibility on the storefront.",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Display Order",
        help_text="Controls display order. Lower values appear first.",
    )

    # ── SEO Fields ──────────────────────────────────────────────────
    seo_title = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="SEO Title",
        help_text="Meta title for search engines (60 chars optimal).",
    )
    seo_description = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="SEO Description",
        help_text="Meta description for search results (155 chars optimal).",
    )
    seo_keywords = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="SEO Keywords",
        help_text="Comma-separated keywords (optional, legacy SEO).",
    )

    objects = CategoryManager()

    class MPTTMeta:
        order_insertion_by = ["display_order", "name"]

    class Meta:
        app_label = "products"
        db_table = "products_category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["tree_id", "lft"]
        indexes = [
            models.Index(
                fields=["is_active", "display_order"],
                name="idx_category_active_order",
            ),
            models.Index(
                fields=["tree_id", "lft"],
                name="idx_category_tree_lft",
            ),
            models.Index(
                fields=["slug"],
                name="idx_category_slug",
            ),
        ]

    def __str__(self):
        """Return the category name."""
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_root(self):
        """Return True if this is a root category (no parent)."""
        return self.is_root_node()

    def get_full_path(self, separator=" > "):
        """
        Return the full ancestor path as a string.

        Example: "Electronics > Phones > Smartphones"

        Uses MPTT's ``get_ancestors()`` for an efficient single query
        instead of recursive parent traversal.
        """
        ancestors = self.get_ancestors(include_self=True)
        return separator.join(a.name for a in ancestors)

    @property
    def is_leaf(self):
        """Return True if this category has no children (leaf node)."""
        return self.is_leaf_node()

    @property
    def children_count(self):
        """Return the number of direct children."""
        return self.get_children().count()

    @property
    def descendants_count(self):
        """Return the total number of descendants at all levels."""
        return self.get_descendants().count()
