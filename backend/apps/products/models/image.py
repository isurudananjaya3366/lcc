"""
ProductImage model for the products application.

Defines the ProductImage model which allows multiple images
per product with gallery ordering, primary image designation,
metadata for SEO/accessibility, and automatic dimension/file-size tracking.
"""

from django.db import models
from django.db.models import Q

from apps.core.mixins import TimestampMixin, UUIDMixin
from apps.products.media.managers import ProductImageManager
from apps.products.media.utils import product_image_upload_path
from apps.products.media.validators import (
    validate_image_dimensions,
    validate_image_file_size,
    validate_image_file_type,
)


class ProductImage(UUIDMixin, TimestampMixin, models.Model):
    """
    Product image model supporting multiple images per product.

    Each product can have multiple images with a display order.
    One image per product should be marked as the primary image
    for display on listing pages.

    Fields:
        product: FK to Product model.
        image: The image file.
        display_order: Gallery ordering (lower first).
        is_primary: Whether this is the main product image.
        alt_text: Alternative text for accessibility (screen readers).
        title: Image title (displayed on hover).
        caption: Longer descriptive text for image context.
        width/height: Image dimensions (auto-populated via signal).
        file_size: File size in bytes (auto-populated via signal).
        original_filename: Original filename before UUID rename.
        processing_status: Status of image variant generation.
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Product",
        help_text="The product this image belongs to.",
    )
    image = models.ImageField(
        upload_to=product_image_upload_path,
        max_length=500,
        verbose_name="Image",
        help_text="Product image file (JPEG, PNG, WebP, or GIF).",
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
        help_text="Designate as the main product image.",
    )

    # SEO & Accessibility metadata
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Alt Text",
        help_text="Alternative text for accessibility (screen readers).",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Title",
        help_text="Image title (displayed on hover).",
    )
    caption = models.TextField(
        blank=True,
        default="",
        verbose_name="Caption",
        help_text="Image caption or description.",
    )

    # Auto-populated dimension fields
    width = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        help_text="Image width in pixels (auto-populated).",
    )
    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        help_text="Image height in pixels (auto-populated).",
    )

    # Auto-populated file size
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        editable=False,
        help_text="File size in bytes (auto-populated).",
    )

    # Original filename preserved before UUID rename
    original_filename = models.CharField(
        max_length=255,
        blank=True,
        default="",
        editable=False,
        help_text="Original filename when uploaded.",
    )

    # Processing status for async variant generation
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
        help_text="Status of image variant processing.",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        help_text="Error details when processing fails.",
    )

    # Generated image variant paths
    thumbnail_path = models.CharField(
        max_length=500, blank=True, default="", editable=False
    )
    medium_path = models.CharField(
        max_length=500, blank=True, default="", editable=False
    )
    large_path = models.CharField(
        max_length=500, blank=True, default="", editable=False
    )

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

    objects = ProductImageManager()

    class Meta:
        app_label = "products"
        db_table = "products_productimage"
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ["display_order", "id"]
        indexes = [
            models.Index(
                fields=["product", "is_primary"],
                name="idx_prodimg_product_primary",
            ),
            models.Index(
                fields=["product", "display_order"],
                name="idx_prodimg_product_order",
            ),
            models.Index(
                fields=["created_on"],
                name="idx_prodimg_created_on",
            ),
        ]
        constraints = [
            # Only one image per product can be is_primary=True
            models.UniqueConstraint(
                fields=["product", "is_primary"],
                condition=Q(is_primary=True),
                name="unique_primary_per_product",
            ),
        ]
        permissions = [
            ("can_upload_images", "Can upload product images"),
            ("can_delete_images", "Can delete product images"),
            ("can_set_primary", "Can set primary product image"),
        ]

    def __str__(self):
        """Return image description."""
        primary = " (primary)" if self.is_primary else ""
        return f"Image for {self.product_id}{primary}"

    def clean(self):
        """Validate display_order uniqueness within the product gallery."""
        super().clean()
        if self.product_id:
            from apps.products.media.validators import validate_unique_display_order

            existing = validate_unique_display_order(
                ProductImage, "product", self.product, exclude_pk=self.pk
            )
            if self.display_order in existing:
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    {"display_order": "Another image already uses this display order."}
                )

    # ── Dimension Properties ────────────────────────────────────────

    @property
    def aspect_ratio(self):
        """Calculate aspect ratio (width / height), rounded to 2 decimals."""
        if self.width and self.height:
            return round(self.width / self.height, 2)
        return None

    @property
    def is_landscape(self):
        """Return True if width > height."""
        if self.width is not None and self.height is not None:
            return self.width > self.height
        return None

    @property
    def is_portrait(self):
        """Return True if height > width."""
        if self.width is not None and self.height is not None:
            return self.height > self.width
        return None

    @property
    def is_square(self):
        """Return True if width == height."""
        if self.width is not None and self.height is not None:
            return self.width == self.height
        return None

    @property
    def file_size_human(self):
        """Return human-readable file size string."""
        if self.file_size is None:
            return "N/A"
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        return f"{self.file_size / (1024 * 1024):.1f} MB"

    @property
    def file_size_kb(self):
        """Return file size in kilobytes, rounded to 1 decimal."""
        if self.file_size is None:
            return None
        return round(self.file_size / 1024, 1)

    @property
    def file_size_mb(self):
        """Return file size in megabytes, rounded to 2 decimals."""
        if self.file_size is None:
            return None
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def is_large_file(self):
        """Return True if file size exceeds 2 MB."""
        if self.file_size is None:
            return False
        return self.file_size > 2 * 1024 * 1024

    @property
    def dimensions_display(self):
        """Return formatted dimensions string."""
        if self.width and self.height:
            return f"{self.width} × {self.height}"
        return "N/A"

    @property
    def is_ready(self):
        """Return True if image processing is completed."""
        return self.processing_status == "completed"

    # ── Instance Methods ────────────────────────────────────────────

    def set_as_primary(self):
        """Set this image as primary, unsetting others for the same product."""
        ProductImage.objects.set_primary_image(self.product, self.pk)

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
