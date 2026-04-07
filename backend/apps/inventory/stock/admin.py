"""Admin configuration for stock models."""

from django.contrib import admin
from django.utils.html import format_html

from apps.inventory.stock.constants import IN_STOCK, LOW_STOCK, OUT_OF_STOCK
from apps.inventory.stock.models.stock_level import StockLevel
from apps.inventory.stock.models.stock_movement import StockMovement
from apps.inventory.stock.models.stock_take import StockTake
from apps.inventory.stock.models.stock_take_item import StockTakeItem


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    """Admin interface for StockLevel model."""

    list_display = [
        "product",
        "variant",
        "warehouse",
        "location",
        "quantity",
        "reserved_quantity",
        "display_available_quantity",
        "display_stock_status",
        "cost_per_unit",
        "last_stock_update",
    ]
    list_filter = [
        "warehouse",
        "last_stock_update",
    ]
    search_fields = [
        "product__name",
        "product__sku",
        "warehouse__name",
    ]
    readonly_fields = [
        "last_stock_update",
        "display_available_quantity",
        "display_stock_status",
        "display_projected_quantity",
        "display_stock_value",
    ]
    raw_id_fields = ["product", "variant", "warehouse", "location"]
    list_per_page = 50
    list_select_related = ["product", "variant", "warehouse", "location"]

    fieldsets = (
        ("Product & Location", {
            "fields": ("product", "variant", "warehouse", "location"),
        }),
        ("Quantities", {
            "fields": (
                "quantity",
                "reserved_quantity",
                "incoming_quantity",
                "reorder_point",
            ),
        }),
        ("Calculated", {
            "fields": (
                "display_available_quantity",
                "display_projected_quantity",
                "display_stock_status",
                "display_stock_value",
            ),
        }),
        ("Cost", {
            "fields": ("cost_per_unit",),
        }),
        ("Tracking", {
            "fields": ("last_stock_update",),
        }),
    )

    @admin.display(description="Available")
    def display_available_quantity(self, obj):
        return obj.available_quantity

    @admin.display(description="Projected")
    def display_projected_quantity(self, obj):
        return obj.projected_quantity

    @admin.display(description="Status")
    def display_stock_status(self, obj):
        status = obj.stock_status
        color = obj.get_stock_status_color()
        label = obj.get_stock_status_display()
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            label,
        )

    @admin.display(description="Stock Value")
    def display_stock_value(self, obj):
        return obj.stock_value


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Admin interface for StockMovement model (read-only)."""

    list_display = [
        "product",
        "variant",
        "movement_type",
        "quantity",
        "from_warehouse",
        "to_warehouse",
        "reason",
        "reference_number",
        "is_reversed",
        "movement_date",
        "created_by",
    ]
    list_filter = [
        "movement_type",
        "reason",
        "is_reversed",
        "movement_date",
        "from_warehouse",
        "to_warehouse",
    ]
    search_fields = [
        "product__name",
        "product__sku",
        "reference_number",
        "reference_id",
        "notes",
    ]
    readonly_fields = [
        "id",
        "created_on",
        "updated_on",
        "movement_date",
        "is_reversed",
        "reversed_by",
        "reversed_at",
        "reversal_reason",
        "original_movement",
        "display_total_cost",
    ]
    raw_id_fields = [
        "product", "variant", "from_warehouse", "to_warehouse",
        "from_location", "to_location", "created_by",
    ]
    list_per_page = 50
    list_select_related = [
        "product", "variant", "from_warehouse", "to_warehouse", "created_by",
    ]
    date_hierarchy = "movement_date"

    fieldsets = (
        ("Movement Details", {
            "fields": (
                "product", "variant", "movement_type", "quantity",
                "reason", "movement_date",
            ),
        }),
        ("Warehouses & Locations", {
            "fields": (
                "from_warehouse", "to_warehouse",
                "from_location", "to_location",
            ),
        }),
        ("Reference", {
            "fields": (
                "reference_type", "reference_id", "reference_number",
                "notes",
            ),
        }),
        ("Cost", {
            "fields": ("cost_per_unit", "display_total_cost"),
        }),
        ("Reversal", {
            "fields": (
                "is_reversed", "reversed_by", "reversed_at",
                "reversal_reason", "original_movement",
            ),
            "classes": ("collapse",),
        }),
        ("Audit", {
            "fields": ("created_by", "created_on", "updated_on"),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description="Total Cost")
    def display_total_cost(self, obj):
        return obj.total_cost


class StockTakeItemInline(admin.TabularInline):
    """Inline for StockTakeItem within StockTakeAdmin."""

    model = StockTakeItem
    extra = 0
    readonly_fields = [
        "product",
        "variant",
        "location",
        "expected_quantity",
        "counted_quantity",
        "variance_quantity",
        "variance_percentage",
        "variance_value",
        "status",
        "counted_by",
        "counted_at",
    ]
    fields = [
        "product",
        "variant",
        "location",
        "expected_quantity",
        "counted_quantity",
        "variance_quantity",
        "variance_percentage",
        "status",
    ]
    show_change_link = True
    can_delete = False


@admin.register(StockTake)
class StockTakeAdmin(admin.ModelAdmin):
    """Admin interface for StockTake model."""

    list_display = [
        "reference",
        "name",
        "warehouse",
        "status",
        "scope",
        "is_blind_count",
        "total_items",
        "counted_items",
        "items_with_variance",
        "total_variance_value",
        "created_by",
        "created_on",
    ]
    list_filter = [
        "status",
        "scope",
        "is_blind_count",
        "warehouse",
        "approval_status",
    ]
    search_fields = [
        "reference",
        "name",
        "warehouse__name",
    ]
    readonly_fields = [
        "reference",
        "total_items",
        "counted_items",
        "items_with_variance",
        "total_variance_value",
        "started_at",
        "completed_at",
        "cancelled_at",
        "created_on",
        "updated_on",
    ]
    raw_id_fields = ["warehouse", "created_by", "completed_by", "approved_by"]
    list_per_page = 30
    list_select_related = ["warehouse", "created_by"]
    date_hierarchy = "created_on"
    inlines = [StockTakeItemInline]

    fieldsets = (
        ("Identification", {
            "fields": ("reference", "name", "description", "warehouse"),
        }),
        ("Configuration", {
            "fields": ("status", "scope", "is_blind_count", "scheduled_date"),
        }),
        ("Approval", {
            "fields": ("approval_status", "approved_by"),
        }),
        ("Statistics", {
            "fields": (
                "total_items",
                "counted_items",
                "items_with_variance",
                "total_variance_value",
            ),
        }),
        ("Users", {
            "fields": ("created_by", "completed_by"),
        }),
        ("Timestamps", {
            "fields": ("started_at", "completed_at", "cancelled_at", "created_on", "updated_on"),
            "classes": ("collapse",),
        }),
    )


@admin.register(StockTakeItem)
class StockTakeItemAdmin(admin.ModelAdmin):
    """Admin interface for StockTakeItem model."""

    list_display = [
        "stock_take",
        "product",
        "variant",
        "location",
        "expected_quantity",
        "counted_quantity",
        "variance_quantity",
        "variance_percentage",
        "display_classification",
        "status",
        "counted_by",
    ]
    list_filter = [
        "status",
        "requires_recount",
        "is_locked",
    ]
    search_fields = [
        "stock_take__reference",
        "product__name",
        "product__sku",
    ]
    readonly_fields = [
        "variance_quantity",
        "variance_percentage",
        "variance_value",
        "expected_value",
        "counted_value",
        "counted_at",
        "display_classification",
        "created_on",
        "updated_on",
    ]
    raw_id_fields = [
        "stock_take",
        "product",
        "variant",
        "location",
        "counted_by",
    ]
    list_per_page = 50
    list_select_related = [
        "stock_take",
        "product",
        "variant",
        "location",
        "counted_by",
    ]

    fieldsets = (
        ("Item", {
            "fields": ("stock_take", "product", "variant", "location"),
        }),
        ("Quantities", {
            "fields": (
                "expected_quantity",
                "counted_quantity",
                "system_quantity",
                "variance_quantity",
                "variance_percentage",
                "display_classification",
            ),
        }),
        ("Cost & Value", {
            "fields": (
                "cost_per_unit",
                "expected_value",
                "counted_value",
                "variance_value",
            ),
        }),
        ("Status", {
            "fields": (
                "status",
                "count_sequence",
                "is_locked",
                "requires_recount",
                "notes",
                "discrepancy_reason",
            ),
        }),
        ("Counter", {
            "fields": ("counted_by", "counted_at"),
        }),
    )

    @admin.display(description="Classification")
    def display_classification(self, obj):
        classification = obj.get_variance_classification()
        colors = {
            "NONE": "gray",
            "MINOR": "green",
            "MODERATE": "orange",
            "SIGNIFICANT": "red",
        }
        color = colors.get(classification, "gray")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            classification,
        )
