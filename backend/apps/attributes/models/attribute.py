"""
Attribute model for defining product attributes with type-based validation.

Attributes support multiple data types (text, number, select, multiselect,
boolean, date) and can be assigned to categories for category-specific
product specifications.
"""

from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel

from ..constants import ATTRIBUTE_TYPES
from .attribute_group import AttributeGroup


class AttributeQuerySet(models.QuerySet):
    """Custom QuerySet for Attribute with chainable filter methods."""

    def active(self):
        """Return only active attributes."""
        return self.filter(is_active=True)

    def filterable(self):
        """Return attributes that are filterable in webstore."""
        return self.filter(is_filterable=True)

    def searchable(self):
        """Return attributes that are searchable."""
        return self.filter(is_searchable=True)

    def required(self):
        """Return required attributes."""
        return self.filter(is_required=True)

    def by_type(self, attribute_type):
        """Return attributes of a specific type."""
        return self.filter(attribute_type=attribute_type)

    def for_category(self, category):
        """Return attributes assigned to a specific category."""
        return self.filter(categories=category)


class AttributeManager(models.Manager):
    """Custom manager for Attribute providing optimized query methods."""

    def get_queryset(self):
        return AttributeQuerySet(self.model, using=self._db)

    def active(self):
        """Return only active attributes."""
        return self.get_queryset().active()

    def filterable(self):
        """Return filterable attributes."""
        return self.get_queryset().filterable()

    def searchable(self):
        """Return searchable attributes."""
        return self.get_queryset().searchable()

    def by_type(self, attribute_type):
        """Return attributes of a specific type."""
        return self.get_queryset().by_type(attribute_type)

    def for_category(self, category):
        """Return attributes for a specific category."""
        return self.get_queryset().for_category(category)


class Attribute(BaseModel):
    """
    Model for defining product attributes with type-based validation.

    Supports multiple attribute types: TEXT, NUMBER, SELECT,
    MULTISELECT, BOOLEAN, DATE. Attributes are organized into groups
    and assigned to categories for category-specific product forms.

    Inherits from BaseModel:
    - id (UUID v4 primary key)
    - created_on, updated_on (timestamps)
    - created_by, updated_by (audit)
    - is_active, deactivated_on (status)
    - is_deleted, deleted_on (soft delete)
    """

    # ── Basic identification fields ─────────────────────────────────
    name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Name of the attribute (e.g., Color, Weight, Size)",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly identifier (auto-generated from name)",
    )

    # ── Organizational fields ───────────────────────────────────────
    group = models.ForeignKey(
        AttributeGroup,
        on_delete=models.SET_NULL,
        related_name="attributes",
        blank=True,
        null=True,
        help_text="Optional group for organizing attributes",
    )
    attribute_type = models.CharField(
        max_length=20,
        choices=ATTRIBUTE_TYPES,
        db_index=True,
        help_text="Type of attribute (text, number, select, multiselect, boolean, date)",
    )
    unit = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Unit of measure (e.g., kg, cm, GB, LKR) — for NUMBER type",
    )

    # ── Requirement and display flags ───────────────────────────────
    is_required = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this attribute must have a value when creating products",
    )
    is_filterable = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Include in webstore faceted search filters",
    )
    is_searchable = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Include attribute values in search indexing",
    )
    is_comparable = models.BooleanField(
        default=False,
        help_text="Show in product comparison tables",
    )
    is_visible_on_product = models.BooleanField(
        default=True,
        help_text="Display this attribute on product detail pages",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Order in which attribute is displayed (lower numbers first)",
    )

    # ── Validation fields ───────────────────────────────────────────
    validation_regex = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Regex pattern for validating TEXT attributes (e.g., '^[A-Z0-9-]+$')",
    )
    min_value = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="Minimum allowed value for NUMBER attributes",
    )
    max_value = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="Maximum allowed value for NUMBER attributes",
    )

    # ── Category assignment (M2M) ──────────────────────────────────
    categories = models.ManyToManyField(
        "products.Category",
        related_name="attributes",
        blank=True,
        help_text="Categories this attribute applies to",
    )

    objects = AttributeManager()
    all_with_deleted = models.Manager()

    class Meta(BaseModel.Meta):
        ordering = ["group__display_order", "display_order", "name"]
        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        indexes = [
            models.Index(
                fields=["attribute_type"],
                name="attrs_attr_type_idx",
            ),
            models.Index(
                fields=["is_filterable"],
                name="attrs_attr_filterable_idx",
            ),
            models.Index(
                fields=["group", "display_order"],
                name="attrs_attr_grp_order_idx",
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        """Validate min_value <= max_value for NUMBER attributes."""
        super().clean()
        if (
            self.min_value is not None
            and self.max_value is not None
            and self.min_value > self.max_value
        ):
            from django.core.exceptions import ValidationError
            raise ValidationError(
                "Minimum value cannot be greater than maximum value."
            )
