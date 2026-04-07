"""
Users admin configuration.

Registers tenant-scoped user models (UserProfile, UserPreferences,
LoginHistory, Role, Permission, UserRole) with Django admin.
"""

from django.contrib import admin

from apps.users.models import (
    LoginHistory,
    Permission,
    Role,
    UserPreferences,
    UserProfile,
    UserRole,
)


# ── Inlines ──────────────────────────────────────────────────────────


class UserRoleInline(admin.TabularInline):
    """Inline for managing role assignments on a UserProfile."""

    model = UserRole
    extra = 0
    autocomplete_fields = ["role"]
    readonly_fields = ["assigned_at"]


# ── UserProfile ──────────────────────────────────────────────────────


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile."""

    list_display = [
        "display_name",
        "user",
        "department",
        "job_title",
        "timezone",
        "is_active",
        "created_on",
    ]
    list_filter = ["is_active", "department", "timezone"]
    search_fields = ["display_name", "user__email", "department", "job_title"]
    readonly_fields = ["created_on", "updated_on"]
    inlines = [UserRoleInline]

    fieldsets = (
        (None, {"fields": ("user", "display_name")}),
        ("Organisation", {"fields": ("department", "job_title")}),
        ("Contact", {"fields": ("phone",)}),
        ("Localisation", {"fields": ("timezone", "locale")}),
        ("Media", {"fields": ("avatar", "bio")}),
        ("Status", {"fields": ("is_active",)}),
        ("Audit", {"fields": ("created_on", "updated_on", "last_login_ip")}),
    )


# ── Role ─────────────────────────────────────────────────────────────


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin for Role."""

    list_display = ["name", "slug", "is_system_role", "created_on"]
    list_filter = ["is_system_role"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["permissions"]
    readonly_fields = ["created_on", "updated_on"]


# ── Permission ───────────────────────────────────────────────────────


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin for Permission."""

    list_display = ["codename", "name", "resource", "action", "is_active"]
    list_filter = ["resource", "is_active"]
    search_fields = ["codename", "name", "resource"]
    readonly_fields = ["created_on", "updated_on"]


# ── LoginHistory ─────────────────────────────────────────────────────


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin for LoginHistory (read-only)."""

    list_display = ["user", "event_type", "ip_address", "success", "timestamp"]
    list_filter = ["event_type", "success"]
    search_fields = ["user__email", "ip_address"]
    readonly_fields = [
        "user",
        "event_type",
        "ip_address",
        "user_agent",
        "success",
        "failure_reason",
        "timestamp",
    ]
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
