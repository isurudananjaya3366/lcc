from django.contrib import admin
from django.utils.html import format_html

from apps.pos.cart.models import POSCart, POSCartItem
from apps.pos.payment.models import POSPayment
from apps.pos.search.models import QuickButton, QuickButtonGroup, SearchHistory
from apps.pos.terminal.models import POSSession, POSTerminal


@admin.register(POSTerminal)
class POSTerminalAdmin(admin.ModelAdmin):
    """Admin interface for POS Terminal management."""

    list_display = [
        "name",
        "code",
        "status_display",
        "warehouse",
        "printer_type",
        "cash_drawer_enabled",
        "is_mobile",
        "created_on",
    ]
    list_filter = [
        "status",
        "warehouse",
        "printer_type",
        "cash_drawer_enabled",
        "is_mobile",
    ]
    search_fields = ["name", "code", "warehouse__name"]
    readonly_fields = ["created_on", "updated_on"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "code", "status", "warehouse", "description")},
        ),
        (
            "Hardware Configuration",
            {
                "fields": (
                    "printer_type",
                    "receipt_printer_ip",
                    "receipt_printer_port",
                    "cash_drawer_enabled",
                    "cash_drawer_auto_open",
                    "barcode_scanner_enabled",
                    "scanner_interface",
                ),
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "location",
                    "floor",
                    "section",
                    "is_mobile",
                    "ip_address",
                ),
            },
        ),
        (
            "Settings",
            {
                "fields": (
                    "default_tax",
                    "allow_price_override",
                    "allow_discount",
                    "max_discount_percent",
                    "require_customer",
                    "allow_negative_inventory",
                    "auto_print_receipt",
                    "receipt_copies",
                    "offline_mode_enabled",
                ),
            },
        ),
        (
            "Receipt Configuration",
            {
                "fields": (
                    "receipt_header",
                    "receipt_footer",
                    "receipt_language",
                ),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_on", "updated_on"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["activate_terminals", "deactivate_terminals", "set_maintenance"]

    @admin.display(description="Status")
    def status_display(self, obj):
        colors = {
            "active": "green",
            "inactive": "gray",
            "maintenance": "orange",
            "offline": "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.action(description="Activate selected terminals")
    def activate_terminals(self, request, queryset):
        queryset.update(status="active")

    @admin.action(description="Deactivate selected terminals")
    def deactivate_terminals(self, request, queryset):
        queryset.update(status="inactive")

    @admin.action(description="Set maintenance mode")
    def set_maintenance(self, request, queryset):
        queryset.update(status="maintenance")


@admin.register(POSSession)
class POSSessionAdmin(admin.ModelAdmin):
    """Admin interface for POS Session management."""

    list_display = [
        "session_number",
        "terminal",
        "user",
        "status_display",
        "opened_at",
        "closed_at",
        "total_sales",
        "cash_variance_display",
        "transaction_count",
    ]
    list_filter = ["status", "terminal", "user", "opened_at"]
    search_fields = [
        "session_number",
        "terminal__name",
        "terminal__code",
        "user__email",
    ]
    readonly_fields = [
        "opened_at",
        "closed_at",
        "expected_cash",
        "cash_variance",
        "total_sales",
        "total_refunds",
        "net_sales_amount",
        "transaction_count",
        "refund_count",
        "cash_sales_amount",
        "card_sales_amount",
        "other_payment_amount",
        "items_sold_count",
        "session_duration_display",
    ]
    date_hierarchy = "opened_at"

    fieldsets = (
        (
            "Session Information",
            {"fields": ("terminal", "user", "status", "session_number")},
        ),
        (
            "Timing",
            {
                "fields": (
                    "opened_at",
                    "closed_at",
                    "expected_close_time",
                    "session_duration_display",
                ),
            },
        ),
        (
            "Cash Reconciliation",
            {
                "fields": (
                    "opening_cash_amount",
                    "opening_cash_counted_by",
                    "opening_cash_counted_at",
                    "opening_cash_notes",
                    "expected_cash",
                    "actual_cash_amount",
                    "cash_variance",
                    "closing_cash_counted_by",
                    "closing_cash_counted_at",
                    "closing_notes",
                    "variance_reason",
                ),
            },
        ),
        (
            "Sales Totals",
            {
                "fields": (
                    "total_sales",
                    "total_refunds",
                    "net_sales_amount",
                    "transaction_count",
                    "refund_count",
                    "cash_sales_amount",
                    "card_sales_amount",
                    "other_payment_amount",
                    "items_sold_count",
                ),
            },
        ),
    )

    actions = ["force_close_sessions"]

    @admin.display(description="Status")
    def status_display(self, obj):
        colors = {
            "open": "green",
            "closed": "blue",
            "suspended": "orange",
            "force_closed": "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="Variance")
    def cash_variance_display(self, obj):
        if obj.cash_variance is None:
            return "-"
        color = "green" if obj.cash_variance >= 0 else "red"
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            f"Rs. {obj.cash_variance:,.2f}",
        )

    @admin.display(description="Duration")
    def session_duration_display(self, obj):
        duration = obj.duration
        if duration is None:
            return "-"
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}m"

    @admin.action(description="Force close selected sessions")
    def force_close_sessions(self, request, queryset):
        for session in queryset.filter(status__in=["open", "suspended"]):
            session.force_close()


class POSCartItemInline(admin.TabularInline):
    """Inline admin for cart items."""

    model = POSCartItem
    extra = 0
    readonly_fields = [
        "product",
        "variant",
        "quantity",
        "original_price",
        "unit_price",
        "line_total",
        "discount_type",
        "discount_amount",
        "tax_rate",
        "tax_amount",
    ]


@admin.register(POSCart)
class POSCartAdmin(admin.ModelAdmin):
    """Admin interface for POS Cart management."""

    list_display = [
        "reference_number",
        "session",
        "status",
        "item_count",
        "subtotal",
        "grand_total",
        "created_on",
    ]
    list_filter = ["status", "created_on"]
    search_fields = ["reference_number", "session__session_number"]
    readonly_fields = [
        "reference_number",
        "subtotal",
        "discount_total",
        "tax_total",
        "grand_total",
        "created_on",
        "updated_on",
    ]
    inlines = [POSCartItemInline]


# ── Quick Button Admin ─────────────────────────────────────────────────


class QuickButtonInline(admin.TabularInline):
    """Inline admin for quick buttons within a group."""

    model = QuickButton
    extra = 0
    fields = ["product", "label", "color", "row", "column", "quick_quantity", "is_active"]


@admin.register(QuickButtonGroup)
class QuickButtonGroupAdmin(admin.ModelAdmin):
    """Admin interface for Quick Button Groups."""

    list_display = [
        "name",
        "code",
        "display_order",
        "rows",
        "columns",
        "is_default",
        "is_active",
    ]
    list_filter = ["is_default", "is_active"]
    search_fields = ["name", "code"]
    inlines = [QuickButtonInline]


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """Admin for POS search history (read-only analytics view)."""

    list_display = [
        "query",
        "search_method",
        "result_count",
        "user",
        "terminal",
        "timestamp",
    ]
    list_filter = ["search_method", "timestamp"]
    search_fields = ["query"]
    readonly_fields = [
        "query",
        "search_method",
        "result_count",
        "user",
        "terminal",
        "selected_product",
        "timestamp",
    ]
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(POSPayment)
class POSPaymentAdmin(admin.ModelAdmin):
    """Admin interface for POS Payment records."""

    list_display = [
        "cart",
        "method",
        "amount",
        "status",
        "processed_by",
        "paid_at",
        "created_on",
    ]
    list_filter = ["method", "status", "created_on"]
    search_fields = [
        "cart__reference_number",
        "reference_number",
        "transaction_id",
    ]
    readonly_fields = [
        "cart",
        "method",
        "amount",
        "status",
        "processed_by",
        "amount_tendered",
        "change_due",
        "reference_number",
        "authorization_code",
        "transaction_id",
        "gateway_response",
        "paid_at",
        "voided_at",
        "notes",
        "created_on",
        "updated_on",
    ]
    date_hierarchy = "created_on"
