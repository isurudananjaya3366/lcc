"""Django admin configuration for the attributes app."""

from django.contrib import admin

from .models import Attribute, AttributeGroup, AttributeOption


class AttributeOptionInline(admin.TabularInline):
    """Inline editor for AttributeOption within Attribute admin."""

    model = AttributeOption
    extra = 3
    fields = [
        "value",
        "label",
        "color_code",
        "image",
        "display_order",
        "is_default",
        "is_active",
    ]
    ordering = ["display_order", "label"]


@admin.register(AttributeGroup)
class AttributeGroupAdmin(admin.ModelAdmin):
    """Admin interface for AttributeGroup."""

    list_display = [
        "name",
        "slug",
        "display_order",
        "is_active",
        "attribute_count",
        "created_on",
    ]
    list_filter = ["is_active", "created_on"]
    search_fields = ["name", "description"]
    ordering = ["display_order", "name"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_on", "updated_on"]

    @admin.display(description="Attributes", ordering="name")
    def attribute_count(self, obj):
        return obj.attributes.count()


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    """Admin interface for Attribute with inline options."""

    list_display = [
        "name",
        "group",
        "attribute_type",
        "is_required",
        "is_filterable",
        "is_visible_on_product",
        "display_order",
        "option_count",
    ]
    list_filter = [
        "attribute_type",
        "is_required",
        "is_filterable",
        "is_searchable",
        "is_comparable",
        "is_visible_on_product",
        "group",
    ]
    search_fields = ["name"]
    ordering = ["display_order", "name"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["categories"]
    readonly_fields = ["created_on", "updated_on"]
    inlines = [AttributeOptionInline]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "group",
                    "attribute_type",
                    "unit",
                ),
            },
        ),
        (
            "Display Settings",
            {
                "fields": (
                    "is_required",
                    "is_filterable",
                    "is_searchable",
                    "is_comparable",
                    "is_visible_on_product",
                    "display_order",
                ),
            },
        ),
        (
            "Validation Rules",
            {
                "fields": (
                    "validation_regex",
                    "min_value",
                    "max_value",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Categories",
            {
                "fields": ("categories",),
            },
        ),
        (
            "Status & Timestamps",
            {
                "fields": (
                    "is_active",
                    "created_on",
                    "updated_on",
                ),
            },
        ),
    )

    @admin.display(description="Options")
    def option_count(self, obj):
        return obj.options.count()


@admin.register(AttributeOption)
class AttributeOptionAdmin(admin.ModelAdmin):
    """Admin interface for AttributeOption."""

    list_display = [
        "label",
        "value",
        "attribute",
        "color_code",
        "display_order",
        "is_default",
        "is_active",
    ]
    list_filter = ["attribute__attribute_type", "is_default", "is_active"]
    search_fields = ["label", "value", "attribute__name"]
    ordering = ["attribute", "display_order", "label"]
    readonly_fields = ["created_on", "updated_on"]
