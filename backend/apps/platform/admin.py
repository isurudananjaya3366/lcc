"""
Platform application admin configuration.

Registers platform models with the Django admin interface for managing
subscription plans, feature flags, platform settings, audit logs,
billing records, and platform users.

Admin Scope:
    Platform admin views are accessible only to superusers and staff
    members with appropriate permissions. All platform models reside
    in the public schema and are shared across all tenants.

    - SubscriptionPlan: Manage subscription tiers and resource limits
    - PlatformSetting: Manage global key-value configuration
    - PlatformUser: Manage platform-level user accounts and roles
    - FeatureFlag: Toggle features for tenants
    - AuditLog: View-only platform audit trail (read-only admin)
    - BillingRecord: View and manage tenant billing records

Base Admin Classes:
    PlatformModelAdmin: Base admin class for platform models that
    include UUID, timestamp, status, and soft delete mixins. Provides
    consistent list display, filtering, and read-only field handling.

Model admin registrations will be added as models are created in
subsequent Group-B through Group-G documents.
"""

from django.contrib import admin


class PlatformModelAdmin(admin.ModelAdmin):
    """
    Base admin class for platform models.

    Provides default configuration for models using the platform
    mixins (UUIDMixin, TimestampMixin, StatusMixin, SoftDeleteMixin).

    Subclasses should extend list_display, list_filter, and
    search_fields as needed for their specific model fields.
    """

    readonly_fields = ("id", "created_on", "updated_on")
    list_per_page = 25
    date_hierarchy = "created_on"
    ordering = ("-created_on",)


class StatusModelAdmin(PlatformModelAdmin):
    """
    Admin class for platform models with StatusMixin.

    Adds is_active and deactivated_on to the admin interface.
    """

    readonly_fields = PlatformModelAdmin.readonly_fields + ("deactivated_on",)
    list_filter = ("is_active",)


class SoftDeleteModelAdmin(PlatformModelAdmin):
    """
    Admin class for platform models with SoftDeleteMixin.

    Adds is_deleted and deleted_on to the admin interface.
    """

    readonly_fields = PlatformModelAdmin.readonly_fields + ("deleted_on",)
    list_filter = ("is_deleted",)


class FullPlatformModelAdmin(PlatformModelAdmin):
    """
    Admin class for platform models with both StatusMixin and SoftDeleteMixin.

    Combines status and soft delete admin features for models that
    use all four mixins (UUID, Timestamp, Status, SoftDelete).
    """

    readonly_fields = PlatformModelAdmin.readonly_fields + (
        "deactivated_on",
        "deleted_on",
    )
    list_filter = ("is_active", "is_deleted")


class ReadOnlyPlatformAdmin(PlatformModelAdmin):
    """
    Read-only admin class for immutable platform records.

    Used for models like AuditLog where records should not be
    modified through the admin interface. All fields are read-only
    and add/change/delete permissions are disabled.
    """

    def has_add_permission(self, request):
        """Prevent adding records through admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing records through admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting records through admin."""
        return False


# ════════════════════════════════════════════════════════════════════
# SubscriptionPlan Admin
# ════════════════════════════════════════════════════════════════════

from apps.platform.models.subscription import SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(FullPlatformModelAdmin):
    """
    Admin configuration for SubscriptionPlan model.

    Provides full management of subscription plan tiers including
    pricing in LKR, resource limits, feature keys, billing cycles,
    and status/visibility flags.
    """

    list_display = (
        "name",
        "slug",
        "monthly_price",
        "annual_price",
        "is_free",
        "is_active",
        "is_public",
        "is_archived",
        "display_order",
    )
    list_filter = (
        "is_active",
        "is_deleted",
        "is_free",
        "is_public",
        "is_archived",
        "default_billing_cycle",
    )
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = FullPlatformModelAdmin.readonly_fields + ("id",)
    ordering = ("display_order", "monthly_price")
    list_editable = ("display_order", "is_active", "is_public")

    fieldsets = (
        (
            "Plan Identity",
            {
                "fields": ("id", "name", "slug", "description"),
            },
        ),
        (
            "Pricing (LKR)",
            {
                "fields": (
                    "monthly_price",
                    "annual_price",
                    "is_free",
                ),
            },
        ),
        (
            "Billing Cycle",
            {
                "fields": (
                    "default_billing_cycle",
                    "has_trial",
                    "trial_days",
                ),
            },
        ),
        (
            "Resource Limits",
            {
                "fields": (
                    "max_users",
                    "max_products",
                    "max_locations",
                    "storage_limit_mb",
                    "max_monthly_transactions",
                ),
                "description": "Use -1 for unlimited access.",
            },
        ),
        (
            "Features",
            {
                "fields": ("feature_keys",),
                "description": "JSON list of enabled feature keys.",
            },
        ),
        (
            "Status & Visibility",
            {
                "fields": (
                    "is_active",
                    "deactivated_on",
                    "is_public",
                    "is_archived",
                    "is_deleted",
                    "deleted_on",
                ),
            },
        ),
        (
            "Display",
            {
                "fields": ("display_order",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_on", "updated_on"),
                "classes": ("collapse",),
            },
        ),
    )

# Platform model admin registrations will be added here
# as models are created in subsequent tasks.

# ════════════════════════════════════════════════════════════════════
# FeatureFlag Admin
# ════════════════════════════════════════════════════════════════════

from apps.platform.models.features import FeatureFlag


@admin.register(FeatureFlag)
class FeatureFlagAdmin(StatusModelAdmin):
    """
    Admin configuration for FeatureFlag model.

    Provides management of platform-wide feature flags including
    rollout percentages, activation status, and visibility settings.
    Uses StatusModelAdmin as the base since feature flags use
    StatusMixin but not SoftDeleteMixin.
    """

    list_display = (
        "key",
        "name",
        "is_active",
        "rollout_percentage",
        "is_public",
        "updated_on",
    )
    list_filter = (
        "is_active",
        "is_public",
        "rollout_percentage",
    )
    search_fields = ("key", "name", "description")
    ordering = ("key",)
    list_editable = ("is_active", "rollout_percentage", "is_public")
    readonly_fields = StatusModelAdmin.readonly_fields

    fieldsets = (
        (
            "Flag Identity",
            {
                "fields": ("id", "key", "name", "description"),
            },
        ),
        (
            "Rollout Configuration",
            {
                "fields": ("rollout_percentage",),
                "description": (
                    "Percentage of tenants that receive this feature. "
                    "0 = disabled, 100 = fully rolled out."
                ),
            },
        ),
        (
            "Status & Visibility",
            {
                "fields": (
                    "is_active",
                    "deactivated_on",
                    "is_public",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_on", "updated_on"),
                "classes": ("collapse",),
            },
        ),
    )


# ── TenantFeatureOverride Admin ──────────────────────────────────────
# ════════════════════════════════════════════════════════════════════

from apps.platform.models.overrides import TenantFeatureOverride


@admin.register(TenantFeatureOverride)
class TenantFeatureOverrideAdmin(PlatformModelAdmin):
    """
    Admin configuration for TenantFeatureOverride model.

    Provides management of tenant-specific feature flag overrides.
    Each record represents a single tenant's override for a single
    feature flag, superseding the global flag state.

    Uses PlatformModelAdmin as the base since overrides use only
    UUIDMixin and TimestampMixin — no StatusMixin or SoftDeleteMixin.
    """

    list_display = (
        "feature_flag",
        "tenant",
        "is_enabled",
        "reason",
        "updated_on",
    )
    list_filter = (
        "is_enabled",
        "feature_flag",
    )
    search_fields = (
        "feature_flag__key",
        "feature_flag__name",
        "tenant__name",
        "reason",
    )
    ordering = ("feature_flag__key", "tenant__name")
    list_select_related = ("tenant", "feature_flag")
    readonly_fields = PlatformModelAdmin.readonly_fields

    fieldsets = (
        (
            "Override Target",
            {
                "fields": ("id", "tenant", "feature_flag"),
            },
        ),
        (
            "Override Value",
            {
                "fields": ("is_enabled", "reason"),
                "description": (
                    "Enable or disable the feature for this specific tenant. "
                    "This value supersedes the global feature flag state."
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_on", "updated_on"),
                "classes": ("collapse",),
            },
        ),
    )


# ════════════════════════════════════════════════════════════════════
# AuditLog Admin
# ════════════════════════════════════════════════════════════════════

from apps.platform.models.audit import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(ReadOnlyPlatformAdmin):
    """
    Read-only admin configuration for AuditLog model.

    Audit log entries are immutable records that cannot be created,
    modified, or deleted through the admin interface. This admin
    provides a view-only interface for reviewing platform audit trails.

    Extends ReadOnlyPlatformAdmin which disables add, change, and
    delete permissions.

    Access:
        Only superusers and staff with can_view_audit_logs permission
        should have access. Access restrictions are enforced at the
        role level through PlatformUser permissions.
    """

    list_display = (
        "created_on",
        "action",
        "resource_type",
        "resource_id",
        "actor_email",
        "ip_address",
    )
    list_filter = (
        "action",
        "resource_type",
        "created_on",
    )
    search_fields = (
        "actor_email",
        "resource_type",
        "resource_id",
        "description",
        "ip_address",
    )
    ordering = ("-created_on",)
    list_select_related = ("actor",)
    date_hierarchy = "created_on"
    list_per_page = 50

    readonly_fields = (
        "id",
        "created_on",
        "updated_on",
        "action",
        "resource_type",
        "resource_id",
        "description",
        "actor",
        "actor_email",
        "ip_address",
        "metadata",
        "user_agent",
    )

    fieldsets = (
        (
            "Event Details",
            {
                "fields": (
                    "id",
                    "action",
                    "resource_type",
                    "resource_id",
                    "description",
                ),
            },
        ),
        (
            "Actor Information",
            {
                "fields": ("actor", "actor_email", "ip_address", "user_agent"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("metadata",),
                "description": (
                    "Structured metadata providing additional context "
                    "for the audit event."
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_on", "updated_on"),
                "classes": ("collapse",),
            },
        ),
    )


# ════════════════════════════════════════════════════════════════════
# BillingRecord Admin
# ════════════════════════════════════════════════════════════════════

from apps.platform.models.billing import (
    BILLING_STATUS_CHOICES,
    CURRENCY_SYMBOL,
    BillingRecord,
)


@admin.register(BillingRecord)
class BillingRecordAdmin(FullPlatformModelAdmin):
    """
    Admin configuration for BillingRecord model.

    Provides full management of tenant billing records including
    invoice details, payment status, BRN validation, and billing
    cycle information. Uses FullPlatformModelAdmin for status and
    soft delete support.

    Financial records are never physically deleted — the soft delete
    mechanism preserves the billing audit trail.

    Access:
        Only superusers and staff with billing management permissions
        should have access.
    """

    list_display = (
        "invoice_number",
        "tenant",
        "subscription_plan",
        "total_amount_display",
        "billing_status",
        "billing_cycle",
        "period_start",
        "due_date",
        "paid_on",
        "created_on",
    )
    list_filter = (
        "billing_status",
        "billing_cycle",
        "is_active",
        "is_deleted",
        "brn_validated",
        "created_on",
    )
    search_fields = (
        "invoice_number",
        "business_registration_number",
        "notes",
    )
    ordering = ("-period_start", "-created_on")
    list_select_related = ("tenant", "subscription_plan")
    date_hierarchy = "period_start"
    list_per_page = 25

    readonly_fields = FullPlatformModelAdmin.readonly_fields + (
        "brn_validated_on",
        "paid_on",
    )

    fieldsets = (
        (
            "Invoice Details",
            {
                "fields": (
                    "id",
                    "invoice_number",
                    "tenant",
                    "subscription_plan",
                ),
            },
        ),
        (
            "Billing Amounts",
            {
                "fields": (
                    "amount",
                    "tax_amount",
                    "total_amount",
                    "currency",
                ),
                "description": (
                    "All amounts in LKR (Sri Lankan Rupees, ₨)."
                ),
            },
        ),
        (
            "Billing Cycle",
            {
                "fields": (
                    "billing_cycle",
                    "period_start",
                    "period_end",
                    "due_date",
                ),
            },
        ),
        (
            "Payment Status",
            {
                "fields": (
                    "billing_status",
                    "paid_on",
                ),
            },
        ),
        (
            "Business Registration (Sri Lanka)",
            {
                "fields": (
                    "business_registration_number",
                    "brn_validated",
                    "brn_validated_on",
                ),
                "description": (
                    "Sri Lanka Business Registration Number for "
                    "tax compliance. Formats: PV12345, PB12345, "
                    "GA12345, or numeric."
                ),
            },
        ),
        (
            "Notes",
            {
                "fields": ("notes",),
                "classes": ("collapse",),
            },
        ),
        (
            "Status & Lifecycle",
            {
                "fields": (
                    "is_active",
                    "deactivated_on",
                    "is_deleted",
                    "deleted_on",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_on", "updated_on"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Total (LKR)")
    def total_amount_display(self, obj):
        """Format total amount with currency symbol."""
        return f"{CURRENCY_SYMBOL}{obj.total_amount}"


# ── PlatformSetting Admin ──

from apps.platform.models.settings import PlatformSetting


@admin.register(PlatformSetting)
class PlatformSettingAdmin(PlatformModelAdmin):
    """
    Admin for the singleton platform settings record.

    Inherits PlatformModelAdmin (UUIDMixin + TimestampMixin base).
    No StatusMixin or SoftDeleteMixin — settings are always active.
    Prevents adding new records when one already exists.
    """

    list_display = (
        "platform_name",
        "support_email",
        "default_timezone",
        "default_currency",
        "maintenance_mode",
        "updated_on",
    )
    readonly_fields = ("id", "created_on", "updated_on")
    fieldsets = (
        ("Branding", {
            "fields": ("id", "platform_name", "logo_url", "primary_color"),
        }),
        ("Contact Information", {
            "fields": ("support_email", "support_phone"),
        }),
        ("Localization", {
            "fields": ("default_timezone", "default_currency"),
            "description": "Asia/Colombo timezone, LKR (₨) currency.",
        }),
        ("Feature Toggles", {
            "fields": (
                "enable_webstore",
                "enable_api_access",
                "enable_multi_currency",
                "maintenance_mode",
            ),
            "description": "Global platform feature switches.",
        }),
        ("Billing Configuration", {
            "fields": (
                "default_tax_rate",
                "tax_inclusive_pricing",
                "billing_currency",
            ),
            "description": "Default billing and tax settings.",
        }),
        ("Notification Configuration", {
            "fields": (
                "enable_email_notifications",
                "enable_sms_notifications",
                "notification_sender_email",
            ),
            "description": "Platform notification defaults.",
        }),
        ("Timestamps", {
            "fields": ("created_on", "updated_on"),
            "classes": ("collapse",),
        }),
    )

    def has_add_permission(self, request):
        """Prevent adding a second settings record."""
        if PlatformSetting.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of the singleton settings record."""
        return False


# ════════════════════════════════════════════════════════════════════
# PlatformUser Admin
# ════════════════════════════════════════════════════════════════════

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.platform.models.user import (
    PLATFORM_ROLE_CHOICES,
    PlatformUser,
)


@admin.register(PlatformUser)
class PlatformUserAdmin(BaseUserAdmin):
    """
    Admin configuration for PlatformUser model.

    Extends Django's UserAdmin to provide platform user management
    with email-based authentication, role assignment, and access
    flag controls. Customized for the LankaCommerce Cloud platform
    where email replaces username as the login identifier.

    Access:
        Only superusers and staff with appropriate permissions can
        manage platform users through this admin interface.
    """

    # ── List Display ─────────────────────────────────────────

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("-date_joined",)
    list_per_page = 25

    # ── Fieldsets (Edit View) ────────────────────────────────

    fieldsets = (
        (
            "Identity",
            {
                "fields": ("id", "email", "password"),
            },
        ),
        (
            "Personal Information",
            {
                "fields": ("first_name", "last_name", "phone"),
            },
        ),
        (
            "Role & Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "description": (
                    "Assign a platform role to control access level. "
                    "Super Admin has full access, Viewer is read-only."
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("date_joined", "last_login", "created_on", "updated_on"),
                "classes": ("collapse",),
            },
        ),
    )

    # ── Add Fieldsets (Create View) ──────────────────────────

    add_fieldsets = (
        (
            "Account",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "phone",
                ),
            },
        ),
        (
            "Role & Access",
            {
                "fields": ("role", "is_active", "is_staff", "is_superuser"),
            },
        ),
    )

    # ── Read-Only Fields ─────────────────────────────────────

    readonly_fields = ("id", "date_joined", "last_login", "created_on", "updated_on")

    # ── Filter Horizontal ────────────────────────────────────

    filter_horizontal = ("groups", "user_permissions")
