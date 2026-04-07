"""Vendors admin configuration."""

from django.contrib import admin

from apps.vendors.models import (
    Vendor, VendorContact, VendorBankAccount, VendorAddress,
    VendorProduct, VendorPriceList, VendorPriceListItem,
    VendorPerformance, VendorCommunication,
    VendorDocument, VendorHistory,
)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = [
        "vendor_code",
        "company_name",
        "status",
        "vendor_type",
        "primary_email",
        "primary_phone",
        "is_preferred_vendor",
    ]
    list_filter = ["status", "vendor_type", "is_local_vendor", "is_preferred_vendor"]
    search_fields = ["vendor_code", "company_name", "primary_email", "tax_id"]
    readonly_fields = ["vendor_code", "created_on", "updated_on"]
    ordering = ["company_name"]


@admin.register(VendorContact)
class VendorContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "vendor", "role", "email", "phone", "is_primary")
    list_filter = ("role", "is_primary")
    search_fields = ("first_name", "last_name", "email")


@admin.register(VendorBankAccount)
class VendorBankAccountAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "account_name", "account_number", "vendor", "currency", "is_default", "verification_status")
    list_filter = ("is_default", "is_active", "verification_status", "currency")
    search_fields = ("bank_name", "account_name", "account_number")


@admin.register(VendorAddress)
class VendorAddressAdmin(admin.ModelAdmin):
    list_display = ("vendor", "address_type", "city", "district", "province", "is_default")
    list_filter = ("address_type", "is_default", "is_active")
    search_fields = ("city", "district", "address_line_1")


@admin.register(VendorProduct)
class VendorProductAdmin(admin.ModelAdmin):
    list_display = ("vendor", "product", "vendor_sku", "unit_cost", "currency", "is_active", "is_preferred")
    list_filter = ("is_active", "is_preferred", "currency")
    search_fields = ("vendor__company_name", "vendor_sku", "vendor_product_name")


@admin.register(VendorPriceList)
class VendorPriceListAdmin(admin.ModelAdmin):
    list_display = ("vendor", "name", "effective_from", "effective_to", "is_current")
    list_filter = ("is_current",)
    search_fields = ("name", "vendor__company_name")


@admin.register(VendorPriceListItem)
class VendorPriceListItemAdmin(admin.ModelAdmin):
    list_display = ("price_list", "product", "unit_price", "min_qty", "max_qty")
    search_fields = ("product__name",)


@admin.register(VendorPerformance)
class VendorPerformanceAdmin(admin.ModelAdmin):
    list_display = ("vendor", "period_start", "period_end", "on_time_delivery_rate", "quality_score", "overall_rating")
    list_filter = ("period_start",)
    search_fields = ("vendor__company_name",)


@admin.register(VendorCommunication)
class VendorCommunicationAdmin(admin.ModelAdmin):
    list_display = ("vendor", "communication_type", "subject", "contact_date", "follow_up_date")
    list_filter = ("communication_type",)
    search_fields = ("subject", "vendor__company_name")


@admin.register(VendorDocument)
class VendorDocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "document_type", "expiry_date", "uploaded_by", "created_on")
    list_filter = ("document_type",)
    search_fields = ("name", "vendor__company_name")


@admin.register(VendorHistory)
class VendorHistoryAdmin(admin.ModelAdmin):
    list_display = ("vendor", "field_name", "change_type", "changed_by", "changed_at")
    list_filter = ("change_type",)
    search_fields = ("vendor__company_name", "field_name")
    readonly_fields = ("vendor", "changed_by", "changed_at", "field_name", "old_value", "new_value", "change_type")
