"""
Django admin configuration for stock alerts and configuration models.
"""

from django.contrib import admin
from django.utils.html import format_html

from apps.inventory.alerts.models import (
    CategoryStockConfig,
    GlobalStockSettings,
    MonitoringLog,
    ProductStockConfig,
    ReorderSuggestion,
    StockAlert,
    SupplierLeadTimeLog,
)


@admin.register(GlobalStockSettings)
class GlobalStockSettingsAdmin(admin.ModelAdmin):
    """Admin for tenant-wide global stock settings."""

    list_display = (
        "__str__",
        "default_low_threshold",
        "default_reorder_point",
        "default_reorder_qty",
        "email_alerts_enabled",
        "dashboard_alerts_enabled",
        "monitoring_frequency",
    )
    fieldsets = (
        ("Threshold Defaults", {
            "fields": (
                "default_low_threshold",
                "default_reorder_point",
                "default_reorder_qty",
                "critical_threshold_multiplier",
                "enable_auto_reorder",
            ),
        }),
        ("Velocity & Lead Time", {
            "fields": (
                "days_of_history_for_velocity",
                "default_lead_time_days",
            ),
        }),
        ("Notification Channels", {
            "fields": (
                "email_alerts_enabled",
                "email_recipients",
                "dashboard_alerts_enabled",
                "sms_alerts_enabled",
                "sms_recipients",
            ),
        }),
        ("Alert Types", {
            "fields": (
                "alert_on_low_stock",
                "alert_on_critical_stock",
                "alert_on_out_of_stock",
                "alert_on_back_in_stock",
            ),
        }),
        ("Throttling", {
            "fields": (
                "alert_throttle_hours",
                "throttle_low_stock_hours",
                "throttle_critical_stock_hours",
                "throttle_oos_hours",
                "throttle_bypass_threshold",
            ),
        }),
        ("Monitoring Schedule", {
            "fields": (
                "monitoring_frequency",
                "monitoring_start_hour",
                "monitoring_end_hour",
            ),
        }),
        ("Webhook Integration", {
            "fields": (
                "webhook_enabled",
                "webhook_url",
                "webhook_secret",
                "webhook_events",
                "webhook_retry_attempts",
                "webhook_timeout_seconds",
            ),
            "classes": ("collapse",),
        }),
        ("EOQ & Safety Stock", {
            "fields": (
                "use_eoq_calculation",
                "ordering_cost_lkr",
                "holding_cost_percent",
                "target_service_level",
                "safety_stock_days",
            ),
            "classes": ("collapse",),
        }),
        ("Reorder Suggestions", {
            "fields": (
                "reorder_suggestions_enabled",
            ),
        }),
        ("Auto-Reorder", {
            "fields": (
                "auto_reorder_enabled",
                "auto_reorder_min_urgency",
                "auto_reorder_max_value_lkr",
                "auto_reorder_require_approval",
            ),
            "classes": ("collapse",),
        }),
    )

    def has_add_permission(self, request):
        # Allow only one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CategoryStockConfig)
class CategoryStockConfigAdmin(admin.ModelAdmin):
    """Admin for category-level stock configuration."""

    list_display = (
        "category",
        "low_stock_threshold",
        "reorder_point",
        "reorder_quantity",
        "inherit_from_parent",
    )
    list_filter = ("inherit_from_parent",)
    search_fields = ("category__name",)
    raw_id_fields = ("category",)


class ProductStockConfigInline(admin.TabularInline):
    """Inline for editing product stock configs on the Product admin."""

    model = ProductStockConfig
    extra = 0
    fields = (
        "variant",
        "warehouse",
        "low_stock_threshold",
        "reorder_point",
        "reorder_quantity",
        "monitoring_enabled",
        "auto_hide_when_oos",
        "allow_backorder",
    )
    raw_id_fields = ("variant", "warehouse")


@admin.register(ProductStockConfig)
class ProductStockConfigAdmin(admin.ModelAdmin):
    """Admin for product-level stock configuration."""

    list_display = (
        "product",
        "variant",
        "get_warehouse_name",
        "low_stock_threshold",
        "reorder_point",
        "monitoring_enabled",
        "auto_hide_when_oos",
        "allow_backorder",
    )
    list_filter = (
        "monitoring_enabled",
        "auto_hide_when_oos",
        "allow_backorder",
        "use_auto_calculation",
        "webstore_visibility_override",
        "product__category",
    )
    search_fields = (
        "product__name",
        "product__sku",
        "variant__sku",
        "warehouse__name",
        "notes",
    )
    raw_id_fields = ("product", "variant", "warehouse", "preferred_supplier")
    list_select_related = ("product", "variant", "warehouse")
    fieldsets = (
        ("Product", {
            "fields": ("product", "variant", "warehouse"),
        }),
        ("Thresholds", {
            "fields": (
                "low_stock_threshold",
                "reorder_point",
                "reorder_quantity",
            ),
        }),
        ("Auto-Calculation", {
            "fields": (
                "use_auto_calculation",
                "safety_stock_days",
                "lead_time_days",
            ),
        }),
        ("Webstore Visibility", {
            "classes": ("collapse",),
            "fields": (
                "auto_hide_when_oos",
                "auto_show_when_restocked",
                "minimum_stock_for_display",
                "hide_threshold_days",
                "display_as_coming_soon",
                "coming_soon_message",
                "webstore_visibility_override",
            ),
        }),
        ("Backorder", {
            "classes": ("collapse",),
            "fields": (
                "allow_backorder",
                "max_backorder_quantity",
                "backorder_lead_time_days",
                "backorder_message",
                "show_expected_ship_date",
                "backorder_notification_email",
            ),
        }),
        ("Advanced", {
            "classes": ("collapse",),
            "fields": (
                "monitoring_enabled",
                "allow_auto_reorder",
                "preferred_supplier",
                "notes",
            ),
        }),
    )
    readonly_fields = (
        "last_calculated_at",
        "calculated_reorder_point",
        "effective_low_threshold_display",
        "effective_reorder_point_display",
        "created_on",
        "updated_on",
    )
    actions = [
        "enable_monitoring",
        "disable_monitoring",
        "enable_auto_hide",
        "disable_auto_hide",
        "recalculate_effective_configs",
    ]

    @admin.display(description="Warehouse")
    def get_warehouse_name(self, obj):
        return obj.get_warehouse_name()

    @admin.action(description="Enable stock monitoring")
    def enable_monitoring(self, request, queryset):
        updated = queryset.update(monitoring_enabled=True)
        self.message_user(request, f"Enabled monitoring for {updated} configs.")

    @admin.action(description="Disable stock monitoring")
    def disable_monitoring(self, request, queryset):
        updated = queryset.update(monitoring_enabled=False)
        self.message_user(request, f"Disabled monitoring for {updated} configs.")

    @admin.action(description="Enable auto-hide when OOS")
    def enable_auto_hide(self, request, queryset):
        updated = queryset.update(auto_hide_when_oos=True)
        self.message_user(request, f"Enabled auto-hide for {updated} configs.")

    @admin.action(description="Disable auto-hide when OOS")
    def disable_auto_hide(self, request, queryset):
        updated = queryset.update(auto_hide_when_oos=False)
        self.message_user(request, f"Disabled auto-hide for {updated} configs.")

    @admin.action(description="Recalculate effective configs")
    def recalculate_effective_configs(self, request, queryset):
        count = 0
        for config in queryset:
            config.refresh_effective_config()
            count += 1
        self.message_user(request, f"Recalculated effective configs for {count} products.")


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    """Admin interface for stock alerts with lifecycle management."""

    list_display = (
        "alert_type_icon",
        "product",
        "variant",
        "get_warehouse_name",
        "current_stock",
        "threshold_value",
        "colored_status",
        "priority",
        "created_at",
        "get_acknowledger",
    )
    list_filter = (
        "status",
        "alert_type",
        "priority",
        "warehouse",
        ("created_at", admin.DateFieldListFilter),
    )
    search_fields = (
        "product__name",
        "product__sku",
        "warehouse__name",
        "message",
    )
    raw_id_fields = ("product", "variant", "warehouse")
    list_select_related = ("product", "variant", "warehouse", "acknowledged_by", "resolved_by")
    readonly_fields = (
        "created_at",
        "updated_at",
        "acknowledged_at",
        "resolved_at",
        "stock_change_since_alert",
    )
    fieldsets = (
        ("Alert Information", {
            "fields": ("alert_type", "status", "priority", "message"),
        }),
        ("Product & Location", {
            "fields": ("product", "variant", "warehouse"),
        }),
        ("Stock Details", {
            "fields": (
                "current_stock",
                "available_quantity",
                "reserved_quantity",
                "incoming_quantity",
                "threshold_value",
                "threshold_type",
                "threshold_source",
                "velocity_at_alert",
                "days_until_critical",
                "stock_change_since_alert",
            ),
        }),
        ("Lifecycle", {
            "fields": (
                "created_at",
                "updated_at",
                "acknowledged_at",
                "acknowledged_by",
                "resolved_at",
                "resolved_by",
            ),
        }),
        ("Snooze", {
            "classes": ("collapse",),
            "fields": (
                "snoozed_until",
                "snoozed_by",
                "snooze_reason",
                "snooze_count",
            ),
        }),
    )
    actions = [
        "acknowledge_alerts",
        "resolve_alerts",
        "snooze_24_hours",
        "export_to_csv",
        "create_reorder_suggestions",
    ]

    @admin.display(description="Type")
    def alert_type_icon(self, obj):
        icons = {
            "low_stock": "\U0001f7e1",
            "critical_stock": "\U0001f7e0",
            "out_of_stock": "\U0001f534",
            "back_in_stock": "\U0001f7e2",
        }
        return icons.get(obj.alert_type, "\u26aa")

    @admin.display(description="Status")
    def colored_status(self, obj):
        colors = {
            "active": "red",
            "acknowledged": "blue",
            "resolved": "green",
            "snoozed": "gray",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="Warehouse")
    def get_warehouse_name(self, obj):
        return obj.warehouse_name

    @admin.display(description="Acknowledged By")
    def get_acknowledger(self, obj):
        return obj.get_acknowledger_name()

    @admin.action(description="Acknowledge selected alerts")
    def acknowledge_alerts(self, request, queryset):
        count = 0
        for alert in queryset.filter(status="active"):
            alert.acknowledge(request.user)
            count += 1
        self.message_user(request, f"Acknowledged {count} alerts.")

    @admin.action(description="Resolve selected alerts")
    def resolve_alerts(self, request, queryset):
        count = 0
        for alert in queryset.exclude(status="resolved"):
            alert.resolve(user=request.user)
            count += 1
        self.message_user(request, f"Resolved {count} alerts.")

    @admin.action(description="Snooze for 24 hours")
    def snooze_24_hours(self, request, queryset):
        count = 0
        for alert in queryset.filter(status="active"):
            alert.snooze_for_hours(24, request.user, reason="Bulk snooze from admin")
            count += 1
        self.message_user(request, f"Snoozed {count} alerts for 24 hours.")

    @admin.action(description="Export selected alerts to CSV")
    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="stock_alerts.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "ID", "Type", "Status", "Priority", "Product", "Warehouse",
            "Current Stock", "Threshold", "Created", "Message",
        ])
        for alert in queryset.select_related("product", "warehouse"):
            writer.writerow([
                str(alert.pk), alert.alert_type, alert.status, alert.priority,
                str(alert.product), str(alert.warehouse or "All"),
                alert.current_stock, alert.threshold_value,
                alert.created_at.strftime("%Y-%m-%d %H:%M"), alert.message,
            ])
        return response

    @admin.action(description="Create reorder suggestions from alerts")
    def create_reorder_suggestions(self, request, queryset):
        from apps.inventory.alerts.models import ReorderSuggestion

        count = 0
        for alert in queryset.filter(
            alert_type__in=["low_stock", "critical_stock", "out_of_stock"],
            status="active",
        ):
            if not ReorderSuggestion.objects.filter(
                product=alert.product, warehouse=alert.warehouse, status="pending",
            ).exists():
                ReorderSuggestion.objects.create(
                    product=alert.product,
                    warehouse=alert.warehouse,
                    suggested_qty=alert.threshold_value or 50,
                    current_stock=alert.current_stock or 0,
                    urgency="high" if alert.alert_type == "critical_stock" else "medium",
                )
                count += 1
        self.message_user(request, f"Created {count} reorder suggestions.")


@admin.register(MonitoringLog)
class MonitoringLogAdmin(admin.ModelAdmin):
    """Admin for monitoring task execution logs."""

    list_display = (
        "run_started_at",
        "status_badge",
        "products_checked",
        "alerts_created",
        "alerts_resolved",
        "errors_encountered",
        "execution_time",
    )
    list_filter = ("status",)
    readonly_fields = (
        "run_started_at",
        "run_completed_at",
        "status",
        "products_checked",
        "alerts_created",
        "alerts_updated",
        "alerts_resolved",
        "errors_encountered",
        "execution_time",
        "error_message",
        "traceback",
        "statistics",
    )
    ordering = ("-run_started_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "running": "#2196F3",
            "completed": "#4CAF50",
            "failed": "#F44336",
        }
        color = colors.get(obj.status, "#999")
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_status_display(),
        )


@admin.register(ReorderSuggestion)
class ReorderSuggestionAdmin(admin.ModelAdmin):
    """Admin for reorder suggestions with lifecycle actions."""

    list_display = (
        "product",
        "urgency_badge",
        "suggested_qty",
        "current_stock",
        "days_until_stockout",
        "estimated_cost",
        "colored_status",
        "created_at",
    )
    list_filter = (
        "status",
        "urgency",
        "auto_generated",
        ("created_at", admin.DateFieldListFilter),
    )
    search_fields = (
        "product__name",
        "product__sku",
        "notes",
    )
    raw_id_fields = ("product", "variant", "warehouse", "suggested_supplier", "status_changed_by")
    list_select_related = ("product", "variant", "warehouse", "suggested_supplier")
    readonly_fields = (
        "created_at",
        "updated_at",
        "status_changed_at",
        "calculation_details",
    )
    fieldsets = (
        ("Product", {
            "fields": ("product", "variant", "warehouse"),
        }),
        ("Suggestion", {
            "fields": (
                "suggested_qty",
                "minimum_order_qty",
                "current_stock",
                "suggested_supplier",
                "urgency",
            ),
        }),
        ("Calculations", {
            "fields": (
                "days_until_stockout",
                "daily_velocity",
                "safety_stock",
                "eoq",
                "reorder_point",
                "calculation_details",
            ),
            "classes": ("collapse",),
        }),
        ("Cost", {
            "fields": (
                "estimated_cost",
                "unit_cost",
            ),
        }),
        ("Status", {
            "fields": (
                "status",
                "status_changed_at",
                "status_changed_by",
                "dismissal_reason",
                "converted_po_id",
                "auto_generated",
                "notes",
            ),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )
    actions = ["dismiss_suggestions", "mark_as_expired"]

    @admin.display(description="Urgency")
    def urgency_badge(self, obj):
        colors = {
            "critical": "#F44336",
            "high": "#FF9800",
            "medium": "#FFC107",
            "low": "#4CAF50",
        }
        color = colors.get(obj.urgency, "#999")
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_urgency_display(),
        )

    @admin.display(description="Status")
    def colored_status(self, obj):
        colors = {
            "pending": "#2196F3",
            "converted_to_po": "#4CAF50",
            "dismissed": "#999",
            "expired": "#FF9800",
        }
        color = colors.get(obj.status, "#999")
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.action(description="Dismiss selected suggestions")
    def dismiss_suggestions(self, request, queryset):
        count = 0
        for s in queryset.filter(status="pending"):
            s.mark_dismissed(reason="Bulk dismiss from admin", user=request.user)
            count += 1
        self.message_user(request, f"Dismissed {count} suggestions.")

    @admin.action(description="Mark selected as expired")
    def mark_as_expired(self, request, queryset):
        count = queryset.filter(status="pending").update(
            status="expired",
        )
        self.message_user(request, f"Marked {count} suggestions as expired.")


@admin.register(SupplierLeadTimeLog)
class SupplierLeadTimeLogAdmin(admin.ModelAdmin):
    """Admin for supplier lead time tracking (Task 65)."""

    list_display = (
        "supplier",
        "product",
        "ordered_date",
        "expected_delivery_date",
        "actual_delivery_date",
        "days_taken",
        "days_late",
        "on_time",
    )
    list_filter = ("on_time", "supplier", "ordered_date")
    search_fields = ("supplier__name", "product__name", "product__sku")
    readonly_fields = ("days_taken", "days_late", "on_time", "created_at")
    date_hierarchy = "ordered_date"
    raw_id_fields = ("supplier", "product")
