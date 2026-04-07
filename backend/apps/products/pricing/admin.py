"""
Admin configuration for pricing models.
"""

from django.contrib import admin

from .models import (
    FlashSale,
    PriceHistory,
    ProductPrice,
    PromotionAnalytics,
    PromotionalPrice,
    ScheduledPrice,
    TieredPricing,
    VariantPrice,
    VariantTieredPricing,
)
from .utils import format_lkr


class VariantPriceInline(admin.TabularInline):
    model = VariantPrice
    extra = 0
    fields = (
        "variant",
        "use_product_price",
        "base_price",
        "sale_price",
        "wholesale_price",
        "cost_price",
        "price_adjustment_type",
        "price_adjustment_value",
    )
    readonly_fields = ()
    show_change_link = True


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "formatted_base_price",
        "formatted_sale_price",
        "formatted_wholesale_price",
        "formatted_cost_price",
        "is_taxable",
        "is_on_sale_display",
        "formatted_profit_margin",
    )
    list_filter = ("is_taxable", "is_tax_inclusive", "tax_class")
    search_fields = ("product__name", "product__sku")
    readonly_fields = (
        "formatted_base_price",
        "formatted_sale_price",
        "formatted_wholesale_price",
        "formatted_cost_price",
        "formatted_profit_margin",
        "is_on_sale_display",
        "last_cost_update",
    )
    fieldsets = (
        (
            "Product",
            {"fields": ("product",)},
        ),
        (
            "Base Pricing",
            {"fields": ("base_price", "cost_price", "last_cost_update")},
        ),
        (
            "Sale Pricing",
            {
                "fields": (
                    "sale_price",
                    "sale_price_start",
                    "sale_price_end",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Wholesale Pricing",
            {
                "fields": ("wholesale_price", "minimum_wholesale_quantity"),
                "classes": ("collapse",),
            },
        ),
        (
            "Tax Configuration",
            {
                "fields": (
                    "tax_class",
                    "is_taxable",
                    "is_tax_inclusive",
                    "tax_exemption_reason",
                ),
            },
        ),
        (
            "Notes",
            {
                "fields": ("pricing_notes",),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Base Price")
    def formatted_base_price(self, obj):
        return format_lkr(obj.base_price)

    @admin.display(description="Sale Price")
    def formatted_sale_price(self, obj):
        return format_lkr(obj.sale_price) if obj.sale_price else "-"

    @admin.display(description="Wholesale")
    def formatted_wholesale_price(self, obj):
        return format_lkr(obj.wholesale_price) if obj.wholesale_price else "-"

    @admin.display(description="Cost")
    def formatted_cost_price(self, obj):
        return format_lkr(obj.cost_price) if obj.cost_price else "-"

    @admin.display(description="On Sale", boolean=True)
    def is_on_sale_display(self, obj):
        return obj.is_on_sale

    @admin.display(description="Margin %")
    def formatted_profit_margin(self, obj):
        margin = obj.profit_margin
        return f"{margin}%" if margin is not None else "-"


@admin.register(VariantPrice)
class VariantPriceAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "use_product_price",
        "base_price",
        "sale_price",
        "wholesale_price",
    )
    list_filter = ("use_product_price",)
    search_fields = ("variant__sku",)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "variant",
        "price_type",
        "old_value",
        "new_value",
        "change_amount",
        "change_percentage",
        "changed_by",
        "change_source",
        "created_on",
    )
    list_filter = ("price_type", "change_source", "automated_change")
    search_fields = ("product__name",)
    readonly_fields = (
        "content_type",
        "object_id",
        "product",
        "variant",
        "price_type",
        "old_value",
        "new_value",
        "change_amount",
        "change_percentage",
        "changed_by",
        "change_reason",
        "automated_change",
        "change_source",
        "created_on",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class TieredPricingInline(admin.TabularInline):
    model = TieredPricing
    extra = 0
    fields = ("name", "min_quantity", "max_quantity", "tier_price", "tier_type", "is_active")


@admin.register(TieredPricing)
class TieredPricingAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "quantity_range", "formatted_tier_price", "discount_display", "tier_type", "is_active", "created_on")
    list_filter = ("tier_type", "is_active")
    search_fields = ("product__name", "name")
    list_editable = ("is_active",)
    ordering = ("product", "min_quantity")
    date_hierarchy = "created_on"
    actions = ["activate_tiers", "deactivate_tiers"]
    fieldsets = (
        (None, {"fields": ("product", "name", "description")}),
        ("Tier Range", {"fields": ("min_quantity", "max_quantity", "tier_type")}),
        ("Pricing", {"fields": ("tier_price", "discount_percentage")}),
        ("Status", {"fields": ("is_active",)}),
    )

    @admin.display(description="Tier Price")
    def formatted_tier_price(self, obj):
        return format_lkr(obj.tier_price)

    @admin.display(description="Range")
    def quantity_range(self, obj):
        return obj.get_tier_range()

    @admin.display(description="Discount")
    def discount_display(self, obj):
        if obj.discount_percentage:
            return f"{obj.discount_percentage}%"
        return "-"

    @admin.action(description="Activate selected tiers")
    def activate_tiers(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected tiers")
    def deactivate_tiers(self, request, queryset):
        queryset.update(is_active=False)


class VariantTieredPricingInline(admin.TabularInline):
    model = VariantTieredPricing
    extra = 0
    fields = ("name", "min_quantity", "max_quantity", "tier_price", "tier_type", "is_active")


@admin.register(VariantTieredPricing)
class VariantTieredPricingAdmin(admin.ModelAdmin):
    list_display = ("variant", "name", "min_quantity", "max_quantity", "formatted_tier_price", "tier_type", "is_active")
    list_filter = ("tier_type", "is_active")
    search_fields = ("variant__sku", "name")
    list_editable = ("is_active",)
    ordering = ("variant", "min_quantity")

    @admin.display(description="Tier Price")
    def formatted_tier_price(self, obj):
        return format_lkr(obj.tier_price)

    def has_delete_permission(self, request, obj=None):
        return False


# ── Scheduled & Promotional Pricing ───────────────────────────────


@admin.register(ScheduledPrice)
class ScheduledPriceAdmin(admin.ModelAdmin):
    list_display = ("name", "product", "variant", "sale_price", "start_datetime", "end_datetime", "status", "priority")
    list_filter = ("status", "priority")
    search_fields = ("name", "product__name", "variant__sku")
    readonly_fields = ("status",)
    ordering = ("-start_datetime",)
    actions = ["activate_schedules", "deactivate_schedules", "update_status_now", "duplicate_schedules"]

    @admin.action(description="Activate selected schedules")
    def activate_schedules(self, request, queryset):
        queryset.update(status=ScheduledPrice.Status.ACTIVE)

    @admin.action(description="Deactivate selected schedules")
    def deactivate_schedules(self, request, queryset):
        queryset.update(status=ScheduledPrice.Status.EXPIRED)

    @admin.action(description="Update status based on current time")
    def update_status_now(self, request, queryset):
        for sp in queryset:
            sp.update_status()

    @admin.action(description="Duplicate schedules (+7 days)")
    def duplicate_schedules(self, request, queryset):
        from datetime import timedelta

        for sp in queryset:
            ScheduledPrice(
                product=sp.product,
                variant=sp.variant,
                name=f"{sp.name} (Copy)",
                description=sp.description,
                sale_price=sp.sale_price,
                start_datetime=sp.start_datetime + timedelta(days=7),
                end_datetime=sp.end_datetime + timedelta(days=7),
                priority=sp.priority,
                status=ScheduledPrice.Status.PENDING,
                created_by=request.user if request.user.is_authenticated else None,
            ).save()


@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ("scheduled_price", "max_quantity", "quantity_sold", "quantity_remaining", "is_sold_out", "urgency_level")
    list_filter = ("is_sold_out",)
    readonly_fields = ("quantity_sold", "is_sold_out")

    @admin.display(description="Remaining")
    def quantity_remaining(self, obj):
        return obj.quantity_remaining

    @admin.display(description="Urgency")
    def urgency_level(self, obj):
        return obj.urgency_level


@admin.register(PromotionalPrice)
class PromotionalPriceAdmin(admin.ModelAdmin):
    list_display = ("name", "discount_type", "discount_value", "start_datetime", "end_datetime", "priority", "is_stackable", "is_active")
    list_filter = ("discount_type", "is_active", "is_stackable")
    search_fields = ("name",)
    filter_horizontal = ("products", "categories")
    list_editable = ("is_active",)
    ordering = ("-priority", "-start_datetime")


@admin.register(PromotionAnalytics)
class PromotionAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "views", "clicks", "conversions", "revenue_generated", "discount_given", "roi_display")
    readonly_fields = (
        "scheduled_price", "flash_sale", "promotional_price",
        "views", "clicks", "conversions", "revenue_generated",
        "discount_given", "conversion_rate", "average_order_value",
        "last_aggregated_at",
    )

    @admin.display(description="ROI %")
    def roi_display(self, obj):
        return f"{obj.roi}%"

    def has_add_permission(self, request):
        return False
