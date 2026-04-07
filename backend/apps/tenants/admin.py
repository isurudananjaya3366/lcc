"""
LankaCommerce Cloud - Tenants Admin Configuration.

Registers Tenant, Domain, TenantSettings, and TenantSubscription models
in Django admin for platform administrators to manage tenants, their
domain mappings, per-tenant settings, and subscription billing.

Admin visibility:
    - Only superusers and platform administrators should have access
      to tenant management. These models live in the public schema.
    - TenantAdmin displays tenant identity, business info, contact,
      address, branding, locale, status, billing, onboarding, and
      schema information with inline editors for domains and settings.
    - DomainAdmin displays domain-to-tenant mapping, type, verification
      status, SSL status, and primary flag.
    - TenantSubscription is accessible both standalone and via inline
      on the TenantAdmin page.

Security note:
    - Tenant and Domain admin operates on the public schema only.
    - Business data (products, sales, etc.) is in tenant schemas and
      is NOT accessible through this admin interface.
    - Schema creation/deletion triggers are controlled by
      AUTO_CREATE_SCHEMA and AUTO_DROP_SCHEMA settings.
"""

import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

from apps.tenants.models import Domain, Tenant, TenantSettings, TenantSubscription


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------


class DomainInline(admin.TabularInline):
    """
    Inline editor for domains on the Tenant admin page.

    Allows platform administrators to add, edit, and remove domains
    directly from the tenant detail view. The primary domain constraint
    (exactly one per tenant) should be enforced at the model/save level.
    """

    model = Domain
    extra = 0
    fields = [
        "domain",
        "is_primary",
        "domain_type",
        "is_verified",
        "verified_at",
        "ssl_status",
        "ssl_expires_at",
        "created_on",
    ]
    readonly_fields = [
        "verified_at",
        "ssl_expires_at",
        "created_on",
    ]
    show_change_link = True


class TenantSettingsInline(admin.StackedInline):
    """
    Inline editor for tenant settings (one-to-one).

    Each tenant has exactly one TenantSettings record, auto-created by
    the post_save signal. This inline allows editing theme, prefixes,
    tax rate, footer text, and JSON configuration directly on the
    tenant detail page.
    """

    model = TenantSettings
    can_delete = False
    extra = 0
    max_num = 1
    fields = [
        "theme_color",
        "invoice_prefix",
        "order_prefix",
        "tax_rate",
        "invoice_footer",
        "receipt_footer",
        "notification_settings",
        "feature_settings",
        "integration_settings",
        "created_on",
        "updated_on",
    ]
    readonly_fields = [
        "created_on",
        "updated_on",
    ]


class TenantSubscriptionInline(admin.TabularInline):
    """
    Inline editor for subscriptions on the Tenant admin page.

    Displays subscription history and current status. Each tenant may
    have multiple subscriptions over time (trial → active → renewed).
    """

    model = TenantSubscription
    extra = 0
    fields = [
        "plan",
        "status",
        "billing_cycle",
        "amount",
        "started_at",
        "expires_at",
        "trial_ends_at",
        "next_billing_date",
        "payment_method",
        "is_auto_renew",
        "created_on",
    ]
    readonly_fields = [
        "created_on",
    ]
    raw_id_fields = ["plan"]
    show_change_link = True


# ---------------------------------------------------------------------------
# Admin Actions
# ---------------------------------------------------------------------------


@admin.action(description="Mark selected domains as verified")
def verify_domains(modeladmin, request, queryset):
    """
    Bulk action to mark selected domains as verified.

    Sets is_verified=True and verified_at to the current timestamp for
    all selected domains that are not already verified. Displays a
    confirmation message with the count of newly verified domains.
    """
    now = timezone.now()
    updated = queryset.filter(is_verified=False).update(
        is_verified=True,
        verified_at=now,
    )
    modeladmin.message_user(
        request,
        f"{updated} domain(s) marked as verified.",
    )


@admin.action(description="Suspend selected tenants")
def suspend_tenants(modeladmin, request, queryset):
    """
    Bulk action to suspend selected tenants.

    Sets the status to 'suspended' for all selected tenants that are
    not already suspended. Displays a confirmation message with the
    count of suspended tenants.
    """
    updated = queryset.exclude(status="suspended").update(status="suspended")
    modeladmin.message_user(
        request,
        f"{updated} tenant(s) suspended.",
    )


@admin.action(description="Activate selected tenants")
def activate_tenants(modeladmin, request, queryset):
    """
    Bulk action to activate selected tenants.

    Sets the status to 'active' for all selected tenants that are
    not already active. Displays a confirmation message with the
    count of activated tenants.
    """
    updated = queryset.exclude(status="active").update(status="active")
    modeladmin.message_user(
        request,
        f"{updated} tenant(s) activated.",
    )


@admin.action(description="Export selected tenants to CSV")
def export_tenants_csv(modeladmin, request, queryset):
    """
    Bulk action to export selected tenants as a CSV file.

    Exports tenant identity, business information, contact details,
    address, branding, locale preferences, billing status, onboarding
    state, and timestamps. The CSV is returned as a downloadable file
    attachment with the filename 'tenants_export.csv'.
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="tenants_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "ID",
        "Name",
        "Slug",
        "Schema Name",
        "Business Type",
        "Industry",
        "Business Registration Number",
        "Contact Name",
        "Contact Email",
        "Contact Phone",
        "Address Line 1",
        "Address Line 2",
        "City",
        "District",
        "Province",
        "Postal Code",
        "Language",
        "Timezone",
        "Status",
        "On Trial",
        "Paid Until",
        "Onboarding Step",
        "Onboarding Completed",
        "Schema Version",
        "Created On",
        "Updated On",
    ])

    for tenant in queryset.iterator():
        writer.writerow([
            tenant.pk,
            tenant.name,
            tenant.slug,
            tenant.schema_name,
            tenant.business_type,
            tenant.industry,
            tenant.business_registration_number,
            tenant.contact_name,
            tenant.contact_email,
            tenant.contact_phone,
            tenant.address_line_1,
            tenant.address_line_2,
            tenant.city,
            tenant.district,
            tenant.province,
            tenant.postal_code,
            tenant.language,
            tenant.timezone,
            tenant.status,
            tenant.on_trial,
            tenant.paid_until,
            tenant.onboarding_step,
            tenant.onboarding_completed,
            tenant.schema_version,
            tenant.created_on,
            tenant.updated_on,
        ])

    return response


# ---------------------------------------------------------------------------
# Model Admins
# ---------------------------------------------------------------------------


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Admin interface for managing tenants.

    Provides comprehensive list view with key tenant fields, search,
    and filtering. Organized into fieldsets covering identity, business
    information, contact details, address, branding, locale preferences,
    billing/subscription, lifecycle, onboarding, schema metadata,
    configuration, and timestamps.

    Includes inline editors for:
        - DomainInline: manage tenant domains
        - TenantSettingsInline: manage per-tenant settings
        - TenantSubscriptionInline: manage subscription records

    Schema name is read-only because it is auto-generated from the slug
    and should not be changed after creation (changing it would orphan
    the PostgreSQL schema).
    """

    list_display = [
        "name",
        "slug",
        "schema_name",
        "business_type",
        "status",
        "on_trial",
        "paid_until",
        "created_on",
    ]
    list_filter = [
        "status",
        "on_trial",
        "business_type",
        "industry",
        "province",
        "language",
    ]
    search_fields = [
        "name",
        "slug",
        "schema_name",
        "contact_email",
        "contact_name",
        "business_registration_number",
    ]
    readonly_fields = [
        "schema_name",
        "created_on",
        "updated_on",
    ]
    ordering = ["name"]
    list_per_page = 25

    fieldsets = [
        (
            "Identity",
            {
                "fields": ["name", "slug", "schema_name"],
            },
        ),
        (
            "Business Information",
            {
                "fields": ["business_type", "industry", "business_registration_number"],
            },
        ),
        (
            "Primary Contact",
            {
                "fields": ["contact_name", "contact_email", "contact_phone"],
            },
        ),
        (
            "Address",
            {
                "fields": [
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "district",
                    "province",
                    "postal_code",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Branding",
            {
                "fields": ["logo", "primary_color", "secondary_color"],
                "classes": ["collapse"],
            },
        ),
        (
            "Locale Preferences",
            {
                "fields": ["language", "timezone"],
                "classes": ["collapse"],
            },
        ),
        (
            "Billing & Subscription",
            {
                "fields": ["paid_until", "on_trial"],
            },
        ),
        (
            "Lifecycle",
            {
                "fields": ["status"],
            },
        ),
        (
            "Onboarding",
            {
                "fields": ["onboarding_step", "onboarding_completed"],
                "classes": ["collapse"],
            },
        ),
        (
            "Schema & Metadata",
            {
                "fields": ["schema_version"],
                "classes": ["collapse"],
            },
        ),
        (
            "Configuration",
            {
                "fields": ["settings"],
                "classes": ["collapse"],
            },
        ),
        (
            "Timestamps",
            {
                "fields": ["created_on", "updated_on"],
                "classes": ["collapse"],
            },
        ),
    ]

    inlines = [
        DomainInline,
        TenantSettingsInline,
        TenantSubscriptionInline,
    ]

    actions = [
        suspend_tenants,
        activate_tenants,
        export_tenants_csv,
    ]


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """
    Admin interface for managing tenant domains.

    Each domain maps a hostname or subdomain to a tenant. The primary
    domain is used for canonical URL generation. TenantMainMiddleware
    uses domain lookups to resolve the current tenant from the Host header.

    Extended fields include domain type (platform/custom), verification
    status, SSL status, and metadata.
    """

    list_display = [
        "domain",
        "tenant",
        "is_primary",
        "domain_type",
        "is_verified",
        "ssl_status",
    ]
    list_filter = [
        "is_primary",
        "domain_type",
        "is_verified",
        "ssl_status",
    ]
    search_fields = [
        "domain",
        "tenant__name",
        "tenant__slug",
    ]
    readonly_fields = [
        "verified_at",
        "ssl_expires_at",
        "created_on",
        "updated_on",
    ]
    ordering = ["domain"]
    list_per_page = 25
    raw_id_fields = ["tenant"]

    fieldsets = [
        (
            "Domain",
            {
                "fields": ["domain", "tenant", "is_primary", "domain_type"],
            },
        ),
        (
            "Verification",
            {
                "fields": ["is_verified", "verified_at"],
            },
        ),
        (
            "SSL",
            {
                "fields": ["ssl_status", "ssl_expires_at"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["metadata"],
                "classes": ["collapse"],
            },
        ),
        (
            "Timestamps",
            {
                "fields": ["created_on", "updated_on"],
                "classes": ["collapse"],
            },
        ),
    ]

    actions = [
        verify_domains,
    ]


@admin.register(TenantSubscription)
class TenantSubscriptionAdmin(admin.ModelAdmin):
    """
    Standalone admin interface for tenant subscriptions.

    Provides a dedicated view for managing all subscriptions across
    tenants. Useful for billing oversight, identifying expiring plans,
    and managing payment methods.
    """

    list_display = [
        "tenant",
        "plan",
        "status",
        "billing_cycle",
        "amount",
        "started_at",
        "expires_at",
        "is_auto_renew",
        "created_on",
    ]
    list_filter = [
        "status",
        "billing_cycle",
        "is_auto_renew",
    ]
    search_fields = [
        "tenant__name",
        "tenant__slug",
        "payment_method",
    ]
    readonly_fields = [
        "created_on",
        "updated_on",
    ]
    ordering = ["-created_on"]
    list_per_page = 25
    raw_id_fields = ["tenant", "plan"]

    fieldsets = [
        (
            "Subscription",
            {
                "fields": ["tenant", "plan", "status", "billing_cycle"],
            },
        ),
        (
            "Billing",
            {
                "fields": [
                    "amount",
                    "payment_method",
                    "is_auto_renew",
                    "next_billing_date",
                ],
            },
        ),
        (
            "Dates",
            {
                "fields": [
                    "started_at",
                    "expires_at",
                    "trial_ends_at",
                ],
            },
        ),
        (
            "Timestamps",
            {
                "fields": ["created_on", "updated_on"],
                "classes": ["collapse"],
            },
        ),
    ]
