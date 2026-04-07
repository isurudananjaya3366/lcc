"""
Django admin configuration for the Products application.

Provides tree-based admin interface for Category model using
MPTTModelAdmin with drag-drop reordering, search, filters,
and organized fieldsets.
"""

from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin

from apps.products.models import (
    Brand,
    Category,
    Product,
    ProductImage,
    ProductOptionConfig,
    ProductVariant,
    ProductVariantOption,
    TaxClass,
    UnitOfMeasure,
    VariantImage,
    VariantOptionType,
    VariantOptionValue,
)


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    """
    Admin configuration for Category model with MPTT tree display.

    Features:
        - Hierarchical tree display with indentation
        - Drag-drop reordering via MPTTModelAdmin
        - Auto-populated slug from name
        - Organized fieldsets (Basic Info, Display, SEO, Timestamps)
        - Sidebar filters for quick category filtering
        - Full-text search across name, slug, and description
    """

    # ── List View Configuration ─────────────────────────────────────
    list_display = [
        "name",
        "slug",
        "parent",
        "is_active",
        "display_order",
        "children_count",
        "created_on",
    ]
    list_display_links = ["name"]
    list_editable = ["is_active", "display_order"]
    list_filter = [
        "is_active",
        "level",
        "parent",
        "created_on",
        "updated_on",
    ]
    list_per_page = 50

    # ── Search ──────────────────────────────────────────────────────
    search_fields = ["name", "slug", "description"]

    # ── Auto-populate slug from name ────────────────────────────────
    prepopulated_fields = {"slug": ("name",)}

    # ── Ordering (tree_id, lft for proper MPTT tree order) ──────────
    ordering = ["tree_id", "lft"]

    # ── Read-only timestamp fields ──────────────────────────────────
    readonly_fields = ["created_on", "updated_on"]

    # ── MPTT-specific: pixel indentation per tree level ─────────────
    mptt_level_indent = 20

    # ── Fieldsets for organized form layout ─────────────────────────
    fieldsets = (
        (
            "Basic Info",
            {
                "fields": ("name", "slug", "parent", "description"),
            },
        ),
        (
            "Display",
            {
                "fields": ("image", "icon", "is_active", "display_order"),
            },
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("seo_title", "seo_description", "seo_keywords"),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    # ── Custom list columns ─────────────────────────────────────────

    @admin.display(description="Children", ordering="lft")
    def children_count(self, obj):
        """Return the number of direct children for the list view."""
        return obj.get_children().count()


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Admin configuration for Brand model.

    Features:
        - Logo preview in detail view
        - Auto-populated slug from name
        - Organized fieldsets
    """

    list_display = ["name", "logo_preview", "is_active", "created_on"]
    list_filter = ["is_active", "created_on"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["logo_preview", "created_on", "updated_on"]

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": ("name", "slug", "description"),
            },
        ),
        (
            "Branding",
            {
                "fields": ("logo", "logo_preview", "website"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    @admin.display(description="Logo Preview")
    def logo_preview(self, obj):
        """Show a small logo thumbnail if the brand has a logo."""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.logo.url,
            )
        return "-"


@admin.register(TaxClass)
class TaxClassAdmin(admin.ModelAdmin):
    """
    Admin configuration for TaxClass model.

    Features:
        - Rate display with percentage symbol
        - Default tax class indicator
    """

    list_display = ["name", "rate_display", "is_default", "created_on"]
    list_filter = ["is_default", "created_on"]
    search_fields = ["name"]
    readonly_fields = ["created_on", "updated_on"]

    fieldsets = (
        (
            "Tax Info",
            {
                "fields": ("name", "rate", "description", "is_default"),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    @admin.display(description="Rate", ordering="rate")
    def rate_display(self, obj):
        """Display rate with percentage symbol."""
        return f"{obj.rate}%"


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    """
    Admin configuration for UnitOfMeasure model.

    Features:
        - Conversion factor display
        - Base unit indicator
    """

    list_display = [
        "name",
        "symbol",
        "conversion_factor",
        "is_base_unit",
        "is_active",
    ]
    list_filter = ["is_base_unit", "is_active"]
    search_fields = ["name", "symbol"]
    readonly_fields = ["created_on", "updated_on"]

    fieldsets = (
        (
            "Unit Info",
            {
                "fields": ("name", "symbol", "description"),
            },
        ),
        (
            "Conversion",
            {
                "fields": ("conversion_factor", "is_base_unit"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )


class ProductVariantTabInline(admin.TabularInline):
    """Inline display of variants within the Product admin."""

    model = ProductVariant
    extra = 0
    fields = ["sku", "name", "sort_order", "is_active"]
    readonly_fields = ["sku", "name"]
    show_change_link = True
    classes = ["collapse"]
    verbose_name = "Variant"
    verbose_name_plural = "Variants"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for Product model.

    Features:
        - Colored status badge
        - Auto-generated SKU (readonly)
        - Autocomplete for related models
        - Organized fieldsets with collapsible sections
    """

    list_display = [
        "sku",
        "name",
        "product_type",
        "status_badge",
        "category",
        "brand",
        "selling_price",
        "featured",
        "created_on",
    ]
    list_filter = [
        "product_type",
        "status",
        "is_webstore_visible",
        "is_pos_visible",
        "featured",
        "category",
        "brand",
        "created_on",
    ]
    search_fields = [
        "name",
        "sku",
        "barcode",
        "description",
        "short_description",
    ]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["sku", "created_on", "updated_on"]
    autocomplete_fields = ["category", "brand", "tax_class", "unit_of_measure"]
    inlines = [ProductVariantTabInline]
    list_per_page = 25

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "name",
                    "slug",
                    "sku",
                    "barcode",
                    "short_description",
                    "description",
                ),
            },
        ),
        (
            "Classification",
            {
                "fields": ("category", "brand", "product_type", "status"),
            },
        ),
        (
            "Visibility",
            {
                "fields": (
                    "is_webstore_visible",
                    "is_pos_visible",
                    "featured",
                ),
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "cost_price",
                    "selling_price",
                    "mrp",
                    "wholesale_price",
                    "tax_class",
                    "unit_of_measure",
                ),
            },
        ),
        (
            "Physical Attributes",
            {
                "classes": ("collapse",),
                "fields": ("weight", "length", "width", "height"),
            },
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("seo_title", "seo_description"),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        """Display a colored HTML badge based on product status."""
        colors = {
            "draft": "#999",
            "active": "#28a745",
            "archived": "#ffc107",
            "discontinued": "#dc3545",
        }
        color = colors.get(obj.status, "#999")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    def get_queryset(self, request):
        """Optimize queryset with select_related for list view."""
        return (
            super()
            .get_queryset(request)
            .select_related("category", "brand", "tax_class", "unit_of_measure")
        )


# ── Variant Option Admin ────────────────────────────────────────────


class VariantOptionValueInline(admin.TabularInline):
    """Inline admin for managing option values within an option type."""

    model = VariantOptionValue
    extra = 1
    fields = [
        "value",
        "label",
        "color_code",
        "image",
        "display_order",
        "is_active",
    ]
    ordering = ["display_order", "value"]


@admin.register(VariantOptionType)
class VariantOptionTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for VariantOptionType model.

    Features:
        - Inline editing of option values
        - Auto-populated slug from name
        - Swatch type indicators
    """

    list_display = [
        "name",
        "slug",
        "display_order",
        "is_color_swatch",
        "is_image_swatch",
        "is_active",
        "values_count",
        "created_on",
    ]
    list_filter = ["is_color_swatch", "is_image_swatch", "is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_on", "updated_on"]
    inlines = [VariantOptionValueInline]
    ordering = ["display_order", "name"]

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": ("name", "slug", "display_order"),
            },
        ),
        (
            "Swatch Options",
            {
                "fields": ("is_color_swatch", "is_image_swatch"),
                "description": (
                    "Select swatch type for visual option display. "
                    "Only one can be active at a time."
                ),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    @admin.display(description="Values")
    def values_count(self, obj):
        """Show the number of option values for this type."""
        return obj.values.count()


@admin.register(VariantOptionValue)
class VariantOptionValueAdmin(admin.ModelAdmin):
    """
    Admin configuration for VariantOptionValue model.

    Features:
        - Color swatch preview
        - Filtering by option type
    """

    list_display = [
        "__str__",
        "option_type",
        "value",
        "label",
        "color_code_display",
        "display_order",
        "is_active",
    ]
    list_filter = ["option_type", "is_active"]
    search_fields = ["value", "label", "option_type__name"]
    readonly_fields = ["created_on", "updated_on"]
    autocomplete_fields = ["option_type"]

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": ("option_type", "value", "label", "display_order"),
            },
        ),
        (
            "Swatch",
            {
                "fields": ("color_code", "image"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    @admin.display(description="Color")
    def color_code_display(self, obj):
        """Show a color swatch preview if color_code is set."""
        if obj.color_code:
            return format_html(
                '<span style="background-color: {}; '
                'display: inline-block; width: 20px; height: 20px; '
                'border: 1px solid #ccc; border-radius: 3px;" '
                'title="{}"></span> {}',
                obj.color_code,
                obj.color_code,
                obj.color_code,
            )
        return "-"


# ── Product Variant Admin ────────────────────────────────────────────


class ProductVariantOptionInline(admin.TabularInline):
    """Inline admin for managing option values within a variant."""

    model = ProductVariantOption
    extra = 1
    fields = ["option_value", "display_order"]
    ordering = ["display_order"]
    autocomplete_fields = ["option_value"]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProductVariant model.

    Features:
        - Inline editing of variant options
        - Auto-complete for parent product
        - Override fields in collapsible section
    """

    list_display = [
        "sku",
        "name",
        "product",
        "is_active",
        "sort_order",
        "created_on",
    ]
    list_filter = ["is_active", "product__product_type", "created_on"]
    search_fields = ["sku", "name", "barcode", "product__name"]
    readonly_fields = ["created_on", "updated_on"]
    autocomplete_fields = ["product"]
    inlines = [ProductVariantOptionInline]
    list_per_page = 25

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": ("product", "sku", "barcode", "name"),
            },
        ),
        (
            "Display",
            {
                "fields": ("sort_order", "is_active"),
            },
        ),
        (
            "Weight & Dimension Overrides",
            {
                "classes": ("collapse",),
                "fields": (
                    "weight_override",
                    "length_override",
                    "width_override",
                    "height_override",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return (
            super()
            .get_queryset(request)
            .select_related("product")
        )


# ── Product Option Config Admin ──────────────────────────────────────


@admin.register(ProductOptionConfig)
class ProductOptionConfigAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProductOptionConfig model.

    Features:
        - Links products to their applicable option types
        - Display order control
    """

    list_display = [
        "__str__",
        "product",
        "option_type",
        "display_order",
        "is_active",
    ]
    list_filter = ["option_type", "is_active"]
    search_fields = ["product__name", "option_type__name"]
    autocomplete_fields = ["product", "option_type"]
    readonly_fields = ["created_on", "updated_on"]

    fieldsets = (
        (
            "Configuration",
            {
                "fields": (
                    "product",
                    "option_type",
                    "display_order",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return (
            super()
            .get_queryset(request)
            .select_related("product", "option_type")
        )


# ── Product Image Admin ──────────────────────────────────────────────


class ProductImageInline(admin.TabularInline):
    """Inline display of product images within the Product admin."""

    model = ProductImage
    extra = 0
    fields = ["image", "alt_text", "display_order", "is_primary"]
    readonly_fields = ["original_filename", "file_size", "width", "height"]
    show_change_link = True
    classes = ["collapse"]
    verbose_name = "Image"
    verbose_name_plural = "Images"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProductImage model.

    Features:
        - Image preview in list and detail views
        - Organized fieldsets (Image, Metadata, Technical, Timestamps)
        - Filters by primary status and product
        - Search by filename, alt text, title, product name
    """

    list_display = [
        "id",
        "image_preview",
        "product",
        "original_filename",
        "display_order",
        "is_primary",
        "file_size_display",
        "dimensions",
        "created_on",
    ]
    list_filter = ["is_primary", "product", "processing_status", "created_on"]
    search_fields = [
        "original_filename",
        "alt_text",
        "title",
        "product__name",
    ]
    list_per_page = 50
    ordering = ["-created_on"]
    actions = ["set_as_primary_action"]
    readonly_fields = [
        "image_preview_large",
        "width",
        "height",
        "file_size",
        "original_filename",
        "processing_status",
        "thumbnail_path",
        "medium_path",
        "large_path",
        "created_on",
        "updated_on",
    ]

    fieldsets = (
        (
            "Image",
            {
                "fields": (
                    "product",
                    "image",
                    "image_preview_large",
                    "display_order",
                    "is_primary",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("alt_text", "title", "caption"),
            },
        ),
        (
            "Technical Details",
            {
                "classes": ("collapse",),
                "fields": (
                    "width",
                    "height",
                    "file_size",
                    "original_filename",
                    "processing_status",
                    "thumbnail_path",
                    "medium_path",
                    "large_path",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    @admin.display(description="Preview")
    def image_preview(self, obj):
        """Show a small image thumbnail in the list view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px;" />',
                obj.image.url,
            )
        return "-"

    @admin.display(description="Preview")
    def image_preview_large(self, obj):
        """Show a larger image preview in the detail view."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.image.url,
            )
        return "-"

    @admin.display(description="Size")
    def file_size_display(self, obj):
        """Show human-readable file size."""
        return obj.file_size_human

    @admin.display(description="Dimensions")
    def dimensions(self, obj):
        """Show formatted image dimensions."""
        return obj.dimensions_display

    @admin.action(description="Set selected image as primary")
    def set_as_primary_action(self, request, queryset):
        """Set selected image as primary for its product."""
        if queryset.count() != 1:
            self.message_user(
                request,
                "Please select exactly one image to set as primary.",
                level="error",
            )
            return
        image = queryset.first()
        image.set_as_primary()
        self.message_user(
            request,
            f'Image set as primary for "{image.product}".',
        )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return (
            super()
            .get_queryset(request)
            .select_related("product")
        )


# Add ProductImage inline to the ProductAdmin
ProductAdmin.inlines = list(ProductAdmin.inlines) + [ProductImageInline]


# ── Variant Image Admin ──────────────────────────────────────────────


class VariantImageInline(admin.TabularInline):
    """Inline display of variant images within the ProductVariant admin."""

    model = VariantImage
    extra = 0
    fields = ["image", "display_order", "is_primary", "alt_text"]
    readonly_fields = []


@admin.register(VariantImage)
class VariantImageAdmin(admin.ModelAdmin):
    """Admin for VariantImage with preview and metadata display."""

    list_display = [
        "id",
        "variant",
        "image_thumbnail",
        "display_order",
        "is_primary",
        "file_size_display",
        "processing_status",
        "created_on",
    ]
    list_filter = ["is_primary", "processing_status", "created_on"]
    search_fields = [
        "variant__sku",
        "variant__product__name",
        "alt_text",
    ]
    readonly_fields = [
        "width",
        "height",
        "file_size",
        "original_filename",
        "processing_status",
        "thumbnail_path",
        "medium_path",
        "large_path",
        "created_on",
        "updated_on",
    ]
    autocomplete_fields = ["variant"]
    list_per_page = 25

    fieldsets = (
        ("Image", {"fields": ("variant", "image", "display_order", "is_primary")}),
        ("Metadata", {"fields": ("alt_text", "title", "caption")}),
        (
            "Technical",
            {
                "classes": ("collapse",),
                "fields": (
                    "width",
                    "height",
                    "file_size",
                    "original_filename",
                    "processing_status",
                    "thumbnail_path",
                    "medium_path",
                    "large_path",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_on", "updated_on"),
            },
        ),
    )

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:50px;max-width:50px;" />',
                obj.image.url,
            )
        return "-"

    image_thumbnail.short_description = "Preview"

    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "-"

    file_size_display.short_description = "Size"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("variant", "variant__product")
        )


# Add VariantImage inline to the ProductVariantAdmin
ProductVariantAdmin.inlines = list(ProductVariantAdmin.inlines) + [VariantImageInline]
