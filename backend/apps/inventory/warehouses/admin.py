"""Warehouse admin configuration."""

from django.contrib import admin

from apps.inventory.warehouses.models import (
    BarcodeScan,
    DefaultWarehouseConfig,
    POSWarehouseMapping,
    StorageLocation,
    TransferRoute,
    Warehouse,
    WarehouseCapacity,
    WarehouseZone,
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "code",
        "warehouse_type",
        "district",
        "status",
        "is_default",
    ]
    list_filter = ["status", "warehouse_type", "district", "is_default"]
    search_fields = ["name", "code", "city", "address_line_1"]
    ordering = ["name"]
    date_hierarchy = "created_on"

    readonly_fields = ["created_on", "updated_on", "created_by", "updated_by"]

    fieldsets = [
        (
            "Basic Information",
            {"fields": ["name", "code", "warehouse_type", "status"]},
        ),
        (
            "Address",
            {
                "fields": [
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "district",
                    "postal_code",
                ]
            },
        ),
        (
            "Contact Information",
            {"fields": ["phone", "email", "manager_name"]},
        ),
        (
            "Operating Hours",
            {
                "fields": [
                    "is_24_hours",
                    "opens_at",
                    "closes_at",
                    "breaks_start",
                    "breaks_end",
                ]
            },
        ),
        (
            "Location",
            {
                "fields": ["latitude", "longitude"],
                "classes": ["collapse"],
            },
        ),
        ("Configuration", {"fields": ["is_default"]}),
        (
            "Metadata",
            {
                "fields": [
                    "created_by",
                    "updated_by",
                    "created_on",
                    "updated_on",
                ],
                "classes": ["collapse"],
            },
        ),
    ]

    actions = ["make_active", "make_inactive", "set_default"]

    @admin.action(description="Activate selected warehouses")
    def make_active(self, request, queryset):
        queryset.update(status="active")

    @admin.action(description="Deactivate selected warehouses")
    def make_inactive(self, request, queryset):
        queryset.update(status="inactive")

    @admin.action(description="Set as default warehouse")
    def set_default(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request, "Please select exactly one warehouse.", level="error"
            )
            return
        warehouse = queryset.first()
        try:
            warehouse.set_as_default()
            self.message_user(
                request, f"{warehouse.name} is now the default warehouse."
            )
        except Exception as e:
            self.message_user(request, str(e), level="error")


@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name",
        "warehouse",
        "location_type",
        "parent",
        "is_active",
        "is_pickable",
        "is_receivable",
    ]
    list_filter = [
        "location_type",
        "is_active",
        "is_pickable",
        "is_receivable",
        "warehouse",
    ]
    search_fields = ["name", "code", "barcode"]
    ordering = ["warehouse", "code"]
    raw_id_fields = ["warehouse", "parent"]

    readonly_fields = ["created_on", "updated_on"]

    fieldsets = [
        (
            "Identity",
            {"fields": ["warehouse", "location_type", "name", "code", "barcode"]},
        ),
        (
            "Hierarchy",
            {"fields": ["parent"]},
        ),
        (
            "Capacity",
            {
                "fields": ["max_weight", "max_volume", "max_items"],
                "classes": ["collapse"],
            },
        ),
        (
            "Flags",
            {"fields": ["is_active", "is_pickable", "is_receivable"]},
        ),
        (
            "Details",
            {
                "fields": ["description"],
                "classes": ["collapse"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_on", "updated_on"],
                "classes": ["collapse"],
            },
        ),
    ]

    actions = ["activate", "deactivate"]

    @admin.action(description="Activate selected locations")
    def activate(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected locations")
    def deactivate(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(BarcodeScan)
class BarcodeScanAdmin(admin.ModelAdmin):
    list_display = [
        "scanned_barcode",
        "location",
        "user",
        "scan_type",
        "success",
        "created_on",
    ]
    list_filter = ["scan_type", "success", "created_on", "device_id"]
    search_fields = ["scanned_barcode", "location__code", "user__username"]
    ordering = ["-created_on"]
    readonly_fields = ["created_on", "updated_on"]

    fieldsets = [
        ("Scan Information", {"fields": ["scanned_barcode", "success", "scan_type"]}),
        ("Location & User", {"fields": ["location", "user", "device_id"]}),
        ("Context", {"fields": ["context_data"]}),
        (
            "Timestamps",
            {"fields": ["created_on", "updated_on"], "classes": ["collapse"]},
        ),
    ]


@admin.register(WarehouseZone)
class WarehouseZoneAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "warehouse", "purpose", "is_active"]
    list_filter = ["purpose", "is_active", "warehouse"]
    search_fields = ["code", "name"]
    ordering = ["warehouse", "code"]


@admin.register(TransferRoute)
class TransferRouteAdmin(admin.ModelAdmin):
    list_display = [
        "source_warehouse",
        "destination_warehouse",
        "transit_days",
        "estimated_cost",
        "is_preferred",
        "is_active",
    ]
    list_filter = ["is_active", "is_preferred"]
    search_fields = [
        "source_warehouse__code",
        "destination_warehouse__code",
    ]
    raw_id_fields = ["source_warehouse", "destination_warehouse"]


@admin.register(WarehouseCapacity)
class WarehouseCapacityAdmin(admin.ModelAdmin):
    list_display = [
        "warehouse",
        "max_item_capacity",
        "current_item_count",
        "last_calculated",
    ]
    readonly_fields = ["last_calculated", "created_on", "updated_on"]
    raw_id_fields = ["warehouse"]


@admin.register(DefaultWarehouseConfig)
class DefaultWarehouseConfigAdmin(admin.ModelAdmin):
    list_display = ["scope", "user", "default_warehouse"]
    list_filter = ["scope"]
    raw_id_fields = ["user", "default_warehouse", "default_receiving_zone", "default_picking_zone"]


@admin.register(POSWarehouseMapping)
class POSWarehouseMappingAdmin(admin.ModelAdmin):
    list_display = ["terminal_id", "warehouse", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["terminal_id"]
    raw_id_fields = ["warehouse"]
