"""
Brand model for LankaCommerce Cloud.

Represents product brands or manufacturers. Brands help organize products
and provide trust signals for customers.

Each brand is tenant-specific and can have:
- Name and unique slug
- Logo image
- Description and website
- Active/inactive status (inherited from BaseModel)
"""

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel


class Brand(BaseModel):
    """
    Represents a product brand or manufacturer.

    Brands help organize products and provide filtering options
    for customers. Each brand can have a logo, description, and
    website link.

    Examples: Apple, Samsung, Nike, Coca-Cola

    Relationships:
        - Products: Many products can belong to one brand

    Tenant Isolation: Each tenant has separate brands via
    django-tenants schema isolation.
    """

    # ── Core Fields ─────────────────────────────────────────────────
    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("Brand Name"),
        help_text=_("Name of the brand or manufacturer (e.g., Apple, Samsung)."),
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name=_("URL Slug"),
        help_text=_(
            "URL-friendly identifier (auto-generated from name if left blank)."
        ),
    )

    # ── Branding ────────────────────────────────────────────────────
    logo = models.ImageField(
        upload_to="brands/logos/",
        blank=True,
        null=True,
        verbose_name=_("Brand Logo"),
        help_text=_(
            "Brand logo image (recommended: 500x500px, square aspect ratio)."
        ),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
        help_text=_("Brand description for webstore display (supports HTML formatting)."),
    )
    website = models.URLField(
        max_length=200,
        blank=True,
        default="",
        verbose_name=_("Official Website"),
        help_text=_("Brand's official website URL (e.g., https://www.apple.com)."),
    )

    class Meta:
        db_table = "products_brand"
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
