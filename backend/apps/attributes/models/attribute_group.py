"""
AttributeGroup model for organizing related product attributes into logical groups.

Groups help categorize attributes in the UI
(e.g., "Dimensions", "Technical Specifications", "Materials").
"""

from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel


class GroupQuerySet(models.QuerySet):
    """Custom QuerySet for AttributeGroup with chainable filter methods."""

    def active(self):
        """Return only active attribute groups."""
        return self.filter(is_active=True)

    def with_attributes(self):
        """Prefetch related attributes for performance optimization."""
        return self.prefetch_related("attributes")


class GroupManager(models.Manager):
    """Custom manager for AttributeGroup providing optimized query methods."""

    def get_queryset(self):
        return GroupQuerySet(self.model, using=self._db)

    def active(self):
        """Return only active attribute groups."""
        return self.get_queryset().active()

    def with_attributes(self):
        """Prefetch related attributes."""
        return self.get_queryset().with_attributes()


class AttributeGroup(BaseModel):
    """
    Model for organizing related attributes into logical groups.

    Attribute groups categorize product specifications for better
    organization and display in the UI. For example:
    - "Technical Specifications" (processor, RAM, storage)
    - "Dimensions" (height, width, depth, weight)
    - "Materials" (fabric composition, care instructions)

    Inherits from BaseModel:
    - id (UUID v4 primary key)
    - created_on, updated_on (timestamps)
    - created_by, updated_by (audit)
    - is_active, deactivated_on (status — used instead of separate field)
    - is_deleted, deleted_on (soft delete)
    """

    name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Name of the attribute group (e.g., 'Technical Specifications')",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly identifier (auto-generated from name)",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Optional description of this attribute group",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Order in which groups are displayed (lower numbers first)",
    )

    objects = GroupManager()
    all_with_deleted = models.Manager()

    class Meta(BaseModel.Meta):
        ordering = ["display_order", "name"]
        verbose_name = "Attribute Group"
        verbose_name_plural = "Attribute Groups"
        indexes = [
            models.Index(
                fields=["is_active", "display_order"],
                name="attrs_grp_active_order_idx",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
