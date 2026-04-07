"""
AttributeOption model for predefined choices in SELECT and MULTISELECT attributes.

Options enable dropdown selection, color swatches, and visual product
variant selection for attributes that require predefined choices.
"""

from django.db import models

from apps.core.models import BaseModel

from .attribute import Attribute


class OptionQuerySet(models.QuerySet):
    """Custom QuerySet for AttributeOption with chainable filter methods."""

    def for_attribute(self, attribute):
        """Return options for a specific attribute."""
        return self.filter(attribute=attribute)

    def with_images(self):
        """Return options that have images."""
        return self.exclude(image="")

    def defaults(self):
        """Return default options."""
        return self.filter(is_default=True)


class OptionManager(models.Manager):
    """Custom manager for AttributeOption."""

    def get_queryset(self):
        return OptionQuerySet(self.model, using=self._db)

    def for_attribute(self, attribute):
        """Return options for a specific attribute."""
        return self.get_queryset().for_attribute(attribute)

    def with_images(self):
        """Return options that have images."""
        return self.get_queryset().with_images()

    def defaults(self):
        """Return default options."""
        return self.get_queryset().defaults()


class AttributeOption(BaseModel):
    """
    Model for storing predefined options for SELECT and MULTISELECT attributes.

    Used for color swatches, size selections, feature lists, and other
    predefined choices. Supports visual representation through color codes
    and thumbnail images.

    Only used for SELECT and MULTISELECT attribute types.

    Inherits from BaseModel:
    - id (UUID v4 primary key)
    - created_on, updated_on (timestamps)
    - created_by, updated_by (audit)
    - is_active, deactivated_on (status)
    - is_deleted, deleted_on (soft delete)
    """

    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name="options",
        help_text="Attribute this option belongs to",
    )
    value = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Internal value (e.g., 'red', 'large', 'cotton')",
    )
    label = models.CharField(
        max_length=100,
        help_text="Display label (e.g., 'Bright Red', 'Extra Large')",
    )
    color_code = models.CharField(
        max_length=7,
        blank=True,
        default="",
        help_text="Hex color code for swatches (e.g., #FF0000)",
    )
    image = models.ImageField(
        upload_to="attributes/options/",
        blank=True,
        null=True,
        help_text="Optional image for visual selection (e.g., fabric textures)",
    )
    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        help_text="Order in which option is displayed (lower numbers first)",
    )
    is_default = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this is the default selected option",
    )

    objects = OptionManager()
    all_with_deleted = models.Manager()

    class Meta(BaseModel.Meta):
        ordering = ["display_order", "label"]
        verbose_name = "Attribute Option"
        verbose_name_plural = "Attribute Options"
        unique_together = [("attribute", "value")]
        indexes = [
            models.Index(
                fields=["attribute", "display_order"],
                name="attrs_opt_attr_order_idx",
            ),
        ]

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        """Ensure only one default option per attribute."""
        if self.is_default:
            AttributeOption.objects.filter(
                attribute=self.attribute,
                is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
