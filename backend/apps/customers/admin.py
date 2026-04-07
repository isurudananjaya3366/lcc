"""Customer admin configuration."""

from django.contrib import admin

from apps.customers.models import (
    Customer,
    CustomerAddress,
    CustomerCommunication,
    CustomerHistory,
    CustomerImport,
    CustomerMerge,
    CustomerPhone,
    CustomerSegment,
    CustomerSettings,
    CustomerTag,
    CustomerTagAssignment,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "customer_code",
        "display_name",
        "customer_type",
        "status",
        "email",
        "phone",
        "is_active",
    ]
    list_filter = [
        "customer_type",
        "status",
        "is_active",
        "source",
        "accepts_marketing",
        "tax_exempt_status",
    ]
    search_fields = [
        "customer_code",
        "first_name",
        "last_name",
        "business_name",
        "display_name",
        "email",
        "phone",
        "mobile",
    ]
    ordering = ["display_name"]
    date_hierarchy = "created_on"

    readonly_fields = [
        "customer_code",
        "created_on",
        "updated_on",
        "created_by",
        "first_purchase_date",
    ]

    fieldsets = [
        (
            "Identity",
            {
                "fields": [
                    "customer_code",
                    "customer_type",
                    "status",
                    "is_active",
                ],
            },
        ),
        (
            "Name",
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "display_name",
                    "business_name",
                ],
            },
        ),
        (
            "Contact",
            {
                "fields": ["email", "phone", "mobile"],
            },
        ),
        (
            "Billing Address",
            {
                "fields": [
                    "billing_address_line_1",
                    "billing_address_line_2",
                    "billing_city",
                    "billing_state_province",
                    "billing_postal_code",
                    "billing_country",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Shipping Address",
            {
                "fields": [
                    "shipping_address_line_1",
                    "shipping_address_line_2",
                    "shipping_city",
                    "shipping_state_province",
                    "shipping_postal_code",
                    "shipping_country",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Business / Organization",
            {
                "fields": [
                    "company_registration",
                    "department_name",
                    "department_code",
                    "organization_name",
                    "registration_number",
                    "tax_exempt_status",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Tax Information",
            {
                "fields": ["tax_id", "vat_number"],
                "classes": ["collapse"],
            },
        ),
        (
            "Financial Summary",
            {
                "fields": [
                    "credit_limit",
                    "current_balance",
                    "total_purchases",
                    "total_payments",
                    "outstanding_balance",
                    "order_count",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Dates",
            {
                "fields": [
                    "first_purchase_date",
                    "last_purchase_date",
                    "last_contact_date",
                    "next_follow_up_date",
                    "date_of_birth",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Marketing",
            {
                "fields": [
                    "accepts_marketing",
                    "marketing_opt_in_date",
                    "marketing_opt_out_date",
                    "last_marketing_email_sent",
                    "marketing_email_count",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Notes",
            {
                "fields": ["notes", "internal_notes"],
                "classes": ["collapse"],
            },
        ),
        (
            "Source & Tracking",
            {
                "fields": ["source", "created_by", "profile_image"],
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

    actions = ["make_active", "make_inactive", "block_customers", "archive_customers"]

    @admin.action(description="Activate selected customers")
    def make_active(self, request, queryset):
        queryset.update(status="active", is_active=True)

    @admin.action(description="Deactivate selected customers")
    def make_inactive(self, request, queryset):
        queryset.update(status="inactive", is_active=False)

    @admin.action(description="Block selected customers")
    def block_customers(self, request, queryset):
        queryset.update(status="blocked", is_active=False)

    @admin.action(description="Archive selected customers")
    def archive_customers(self, request, queryset):
        queryset.update(status="archived", is_active=False)


@admin.register(CustomerAddress)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "address_type",
        "address_line_1",
        "city",
        "district",
        "is_default_billing",
        "is_default_shipping",
    ]
    list_filter = ["address_type", "district", "province", "country"]
    search_fields = ["address_line_1", "city", "district", "postal_code"]
    ordering = ["customer", "-is_default_billing"]
    raw_id_fields = ["customer"]


@admin.register(CustomerPhone)
class CustomerPhoneAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "phone_type",
        "phone_number",
        "is_primary",
        "is_verified",
        "is_whatsapp",
    ]
    list_filter = ["phone_type", "is_primary", "is_verified", "is_whatsapp"]
    search_fields = ["phone_number"]
    ordering = ["customer", "-is_primary"]
    raw_id_fields = ["customer"]


@admin.register(CustomerCommunication)
class CustomerCommunicationAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "communication_type",
        "subject",
        "contacted_by",
        "communication_date",
        "follow_up_date",
        "follow_up_completed",
    ]
    list_filter = [
        "communication_type",
        "follow_up_completed",
        "communication_date",
    ]
    search_fields = ["subject", "content"]
    ordering = ["-communication_date"]
    raw_id_fields = ["customer", "contacted_by", "related_order", "related_invoice"]


@admin.register(CustomerHistory)
class CustomerHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "customer",
        "change_type",
        "field_name",
        "changed_by",
        "changed_at",
    ]
    list_filter = ["change_type", "changed_at"]
    search_fields = ["field_name", "old_value", "new_value"]
    ordering = ["-changed_at"]
    raw_id_fields = ["customer", "changed_by"]
    readonly_fields = [
        "customer",
        "changed_by",
        "changed_at",
        "field_name",
        "old_value",
        "new_value",
        "change_type",
    ]


@admin.register(CustomerSettings)
class CustomerSettingsAdmin(admin.ModelAdmin):
    list_display = [
        "customer_code_prefix",
        "customer_code_start",
        "require_email",
        "require_phone",
        "default_status",
    ]
    fieldsets = [
        (
            "Code Generation",
            {"fields": ["customer_code_prefix", "customer_code_start"]},
        ),
        (
            "Validation Rules",
            {"fields": ["require_email", "require_phone", "default_status"]},
        ),
        (
            "Duplicate Rules",
            {"fields": ["allow_duplicate_email", "allow_duplicate_phone"]},
        ),
    ]


@admin.register(CustomerTag)
class CustomerTagAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "is_active", "created_by"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["name"]
    raw_id_fields = ["created_by"]


@admin.register(CustomerTagAssignment)
class CustomerTagAssignmentAdmin(admin.ModelAdmin):
    list_display = ["customer", "tag", "assigned_by", "assigned_at"]
    list_filter = ["tag", "assigned_at"]
    search_fields = ["customer__display_name", "tag__name"]
    ordering = ["-assigned_at"]
    raw_id_fields = ["customer", "tag", "assigned_by"]


@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_active",
        "auto_assign",
        "customer_count",
        "created_by",
    ]
    list_filter = ["is_active", "auto_assign"]
    search_fields = ["name", "description"]
    ordering = ["name"]
    raw_id_fields = ["created_by"]
    readonly_fields = ["customer_count"]


@admin.register(CustomerMerge)
class CustomerMergeAdmin(admin.ModelAdmin):
    list_display = [
        "primary_customer",
        "duplicate_customer",
        "duplicate_score",
        "merged_by",
        "merged_at",
    ]
    list_filter = ["merged_at"]
    search_fields = [
        "primary_customer__display_name",
        "duplicate_customer__display_name",
    ]
    ordering = ["-merged_at"]
    raw_id_fields = ["primary_customer", "duplicate_customer", "merged_by"]
    readonly_fields = [
        "primary_customer",
        "duplicate_customer",
        "merged_by",
        "merged_at",
        "merge_reason",
        "duplicate_score",
        "orders_transferred",
        "invoices_transferred",
        "payments_transferred",
        "addresses_transferred",
        "phones_transferred",
        "total_purchases_added",
        "duplicate_customer_snapshot",
    ]


@admin.register(CustomerImport)
class CustomerImportAdmin(admin.ModelAdmin):
    list_display = [
        "filename",
        "status",
        "total_rows",
        "successful_rows",
        "failed_rows",
        "uploaded_by",
        "started_at",
        "completed_at",
    ]
    list_filter = ["status", "started_at"]
    search_fields = ["filename"]
    ordering = ["-started_at"]
    raw_id_fields = ["uploaded_by"]
    readonly_fields = [
        "filename",
        "status",
        "total_rows",
        "processed_rows",
        "successful_rows",
        "failed_rows",
        "skipped_rows",
        "error_log",
        "started_at",
        "completed_at",
        "uploaded_by",
    ]
