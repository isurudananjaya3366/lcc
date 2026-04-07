"""
Variant option models for the products app.

Provides VariantOptionType (Size, Color, Material) and VariantOptionValue
(S, M, L, Red, Blue) for building product variant combinations.
"""

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class VariantOptionType(BaseModel):
    """
    Defines a type of variant option such as Size, Color, or Material.

    Each option type can contain multiple option values. The swatch flags
    control how values are rendered in the storefront (color picker, image
    picker, or plain text).

    Examples:
        - Size → [S, M, L, XL]
        - Color → [Red, Blue, Green]  (color swatch)
        - Material → [Cotton, Polyester]
    """

    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("Option Type Name"),
        help_text=_(
            "Name of the variant option type "
            "(e.g., Size, Color, Material)"
        ),
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name=_("URL Slug"),
        help_text=_("URL-friendly identifier (auto-generated from name)"),
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_(
            "Order in which this option type appears "
            "(lower numbers first)"
        ),
    )
    is_color_swatch = models.BooleanField(
        default=False,
        verbose_name=_("Display as Color Swatch"),
        help_text=_(
            "If True, option values will display as color swatches"
        ),
    )
    is_image_swatch = models.BooleanField(
        default=False,
        verbose_name=_("Display as Image Swatch"),
        help_text=_(
            "If True, option values will display as image swatches"
        ),
    )

    class Meta(BaseModel.Meta):
        db_table = "products_variantoptiontype"
        verbose_name = _("Variant Option Type")
        verbose_name_plural = _("Variant Option Types")
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["slug"], name="varopttype_slug_idx"),
            models.Index(
                fields=["display_order", "name"],
                name="varopttype_order_name_idx",
            ),
            models.Index(
                fields=["is_active"], name="varopttype_active_idx"
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_variantoptiontype_name",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate that swatch flags are mutually exclusive."""
        super().clean()
        if self.is_color_swatch and self.is_image_swatch:
            raise ValidationError(
                _(
                    "Option type cannot be both color swatch "
                    "and image swatch."
                )
            )

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class VariantOptionValue(BaseModel):
    """
    A specific value for a variant option type.

    For example, if the option type is "Size", values might be
    S, M, L, XL. If the option type is "Color", values might be
    Red, Blue, Green with associated hex color codes.

    When the parent option type is a color swatch, ``color_code``
    is required. When it is an image swatch, ``image`` is required.
    """

    option_type = models.ForeignKey(
        VariantOptionType,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name=_("Option Type"),
        help_text=_("The variant option type this value belongs to"),
    )
    value = models.CharField(
        max_length=100,
        verbose_name=_("Value"),
        help_text=_(
            "Internal value identifier (e.g., 's', 'red', '8gb')"
        ),
    )
    label = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name=_("Display Label"),
        help_text=_(
            "Display label for this value "
            "(e.g., 'Small', 'Red', '8GB RAM')"
        ),
    )
    color_code = models.CharField(
        max_length=7,
        blank=True,
        default="",
        verbose_name=_("Color Code"),
        help_text=_(
            "Hex color code (e.g., #FF0000 for red). "
            "Required if option type is color swatch"
        ),
    )
    image = models.ImageField(
        upload_to="variant_option_swatches/",
        blank=True,
        null=True,
        verbose_name=_("Swatch Image"),
        help_text=_(
            "Swatch image for visual selection. "
            "Required if option type uses image swatches"
        ),
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_(
            "Order in which this value appears "
            "(lower numbers first)"
        ),
    )

    class Meta(BaseModel.Meta):
        db_table = "products_variantoptionvalue"
        verbose_name = _("Variant Option Value")
        verbose_name_plural = _("Variant Option Values")
        ordering = ["option_type", "display_order", "value"]
        unique_together = [["option_type", "value"]]
        indexes = [
            models.Index(
                fields=["option_type", "display_order"],
                name="varoptval_type_order_idx",
            ),
            models.Index(fields=["value"], name="varoptval_value_idx"),
        ]

    def __str__(self):
        return f"{self.option_type.name}: {self.label or self.value}"

    def clean(self):
        """Validate swatch requirements based on option type."""
        super().clean()
        # Validate hex color code format
        if self.color_code:
            if not re.match(r"^#[0-9A-Fa-f]{6}$", self.color_code):
                raise ValidationError(
                    {
                        "color_code": _(
                            "Invalid hex color code. "
                            "Must be in #RRGGBB format (e.g., #FF0000)."
                        )
                    }
                )

        # Color swatch requires color_code
        if (
            hasattr(self, "option_type")
            and self.option_type_id
            and self.option_type.is_color_swatch
            and not self.color_code
        ):
            raise ValidationError(
                {
                    "color_code": _(
                        "Color code is required for color swatch "
                        "option types."
                    )
                }
            )

        # Image swatch requires image
        if (
            hasattr(self, "option_type")
            and self.option_type_id
            and self.option_type.is_image_swatch
            and not self.image
        ):
            raise ValidationError(
                {
                    "image": _(
                        "Image is required for image swatch "
                        "option types."
                    )
                }
            )

    def save(self, *args, **kwargs):
        """Auto-generate label from value if not provided."""
        if not self.label:
            self.label = (
                self.value.replace("-", " ")
                .replace("_", " ")
                .title()
            )
        super().save(*args, **kwargs)

    # ── Properties ──────────────────────────────────────────────────

    @property
    def is_color_swatch(self):
        """Return True if the parent option type uses color swatches."""
        return self.option_type.is_color_swatch

    @property
    def is_image_swatch(self):
        """Return True if the parent option type uses image swatches."""
        return self.option_type.is_image_swatch

    @property
    def get_display_html(self):
        """Return an HTML snippet for swatch rendering."""
        if self.option_type.is_color_swatch and self.color_code:
            return (
                f'<div style="background-color: {self.color_code}; '
                f'width: 24px; height: 24px; border-radius: 50%;" '
                f'title="{self.label}"></div>'
            )
        if self.option_type.is_image_swatch and self.image:
            return (
                f'<img src="{self.image.url}" alt="{self.label}" '
                f'width="24" height="24">'
            )
        return f"<span>{self.label}</span>"
