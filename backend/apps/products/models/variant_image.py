"""
VariantImage model for variant-specific product images.

Allows product variants to have their own images, separate from
the parent product's gallery. Supports inheritance fallback to
product images when a variant has no dedicated images.
"""

from django.db import models
from django.db.models import Q

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.products.media.managers.variant_image_manager import VariantImageManager
from apps.products.media.utils import variant_image_upload_path
from apps.products.media.validators import (
    validate_image_dimensions,
    validate_image_file_size,
    validate_image_file_type,
)


class VariantImage(UUIDMixin, TimestampMixin, models.Model):
    """
    Image associated with a specific ProductVariant.

    Mirrors ``ProductImage`` but links to a variant instead of a product.
    Variants without their own images fall back to the parent product's
    gallery via the ``get_images`` helper on this model.
    """

    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Variant",
        help_text="The product variant this image belongs to.",
    )
    image = models.ImageField(
        upload_to=variant_image_upload_path,
        max_length=500,
        verbose_name="Image",
        help_text="Variant image file (JPEG, PNG, WebP, or GIF).",
        validators=[
            validate_image_file_type,
            validate_image_file_size,
            validate_image_dimensions,
        ],
    )
    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="Display Order",
        help_text="Order of image in gallery (lower numbers first).",
    )
    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Primary Image",
        help_text="Designate as the main variant image.",
    )

    # SEO / accessibility
    alt_text = models.CharField(max_length=255, blank=True, default="")
    title = models.CharField(max_length=255, blank=True, default="")
    caption = models.TextField(blank=True, default="")

    # Auto-populated via signal
    width = models.PositiveIntegerField(null=True, blank=True, editable=False)
    height = models.PositiveIntegerField(null=True, blank=True, editable=False)
    file_size = models.PositiveIntegerField(null=True, blank=True, editable=False)
    original_filename = models.CharField(
        max_length=255, blank=True, default="", editable=False
    )

    # Processing
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Error details when processing fails.",
    )
    thumbnail_path = models.CharField(max_length=500, blank=True, default="", editable=False)
    medium_path = models.CharField(max_length=500, blank=True, default="", editable=False)
    large_path = models.CharField(max_length=500, blank=True, default="", editable=False)

    # WebP variant paths
    webp_thumbnail_path = models.CharField(
        max_length=500,
        blank=True,
        default="",
        editable=False,
        help_text="Path to 150×150 WebP thumbnail.",
    )
    webp_medium_path = models.CharField(
        max_length=500,
        blank=True,
        default="",
        editable=False,
        help_text="Path to 500×500 WebP medium image.",
    )
    webp_large_path = models.CharField(
        max_length=500,
        blank=True,
        default="",
        editable=False,
        help_text="Path to 1000×1000 WebP large image.",
    )

    # Low Quality Image Placeholder (base64 data URI)
    placeholder_data_uri = models.TextField(
        blank=True,
        default="",
        editable=False,
        help_text="Base64-encoded LQIP for progressive loading.",
    )

    objects = VariantImageManager()

    class Meta:
        app_label = "products"
        db_table = "products_variant_images"
        verbose_name = "Variant Image"
        verbose_name_plural = "Variant Images"
        ordering = ["display_order", "id"]
        indexes = [
            models.Index(
                fields=["variant", "display_order"],
                name="idx_varimg_variant_order",
            ),
            models.Index(
                fields=["variant", "is_primary"],
                name="idx_varimg_variant_primary",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["variant", "is_primary"],
                condition=Q(is_primary=True),
                name="unique_primary_per_variant",
            ),
        ]

    def __str__(self):
        primary = " (primary)" if self.is_primary else ""
        webp_count = sum(
            1
            for p in (self.webp_thumbnail_path, self.webp_medium_path, self.webp_large_path)
            if p
        )
        webp_info = f" ({webp_count} WebP)" if webp_count else ""
        return f"Variant Image for {self.variant_id}{primary}{webp_info}"

    def clean(self):
        """Validate display_order uniqueness within the variant gallery."""
        super().clean()
        if self.variant_id:
            from apps.products.media.validators import validate_unique_display_order

            existing = validate_unique_display_order(
                VariantImage, "variant", self.variant, exclude_pk=self.pk
            )
            if self.display_order in existing:
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    {"display_order": "Another image already uses this display order."}
                )

    # ── Display helper ──────────────────────────────────────────────

    def get_display_name(self) -> str:
        """Return best available display text: alt_text -> title -> filename."""
        return self.alt_text or self.title or self.original_filename or str(self.pk)

    @property
    def is_ready(self):
        """Return True if image processing is completed."""
        return self.processing_status == "completed"

    # ── WebP helpers ────────────────────────────────────────────────

    def get_webp_path(self, size: str) -> str:
        """Return the WebP path for *size* ('thumbnail', 'medium', 'large')."""
        return getattr(self, f"webp_{size}_path", "") or ""

    def has_webp(self, size: str | None = None) -> bool:
        """Return True if a WebP variant exists for *size* (or any size)."""
        if size:
            return bool(self.get_webp_path(size))
        return bool(
            self.webp_thumbnail_path
            or self.webp_medium_path
            or self.webp_large_path
        )

    def get_all_webp_paths(self) -> dict[str, str]:
        """Return a dict of all non-empty WebP variant paths."""
        paths: dict[str, str] = {}
        for size in ("thumbnail", "medium", "large"):
            path = self.get_webp_path(size)
            if path:
                paths[size] = path
        return paths

    # ── Image inheritance helpers (static) ──────────────────────────

    @staticmethod
    def has_own_images(variant) -> bool:
        """Return True if the variant has at least one dedicated image."""
        return variant.images.exists()

    @staticmethod
    def get_images(variant):
        """
        Return the variant's own images, or fall back to the parent product's
        images if the variant has none.
        """
        if variant.images.exists():
            return variant.images.all().order_by("display_order")
        return variant.product.images.all().order_by("display_order")

    @staticmethod
    def get_primary_image(variant):
        """
        Return the variant's primary image, or fall back to the product's
        primary image.
        """
        own = variant.images.filter(is_primary=True).first()
        if own:
            return own
        return variant.product.images.filter(is_primary=True).first()

    @staticmethod
    def uses_inherited_images(variant) -> bool:
        """Return True if the variant is using the product's images."""
        return not variant.images.exists()

    @staticmethod
    def get_image_count(variant) -> int:
        """Return effective image count (own or inherited)."""
        own = variant.images.count()
        if own:
            return own
        return variant.product.images.count()
