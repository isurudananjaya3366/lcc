"""
Users API serializers.

Serializers for user profiles, preferences, roles, permissions,
login history, and role assignments.
"""

from __future__ import annotations

from django.utils.text import slugify
from rest_framework import serializers

from apps.users.models import (
    LoginHistory,
    Permission,
    Role,
    UserPreferences,
    UserProfile,
    UserRole,
)


# ── Permission ───────────────────────────────────────────────────────


class PermissionSerializer(serializers.ModelSerializer):
    """Full CRUD serializer for Permission."""

    class Meta:
        model = Permission
        fields = [
            "id",
            "codename",
            "name",
            "description",
            "resource",
            "action",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]
        extra_kwargs = {"codename": {"required": False}}

    def validate(self, attrs: dict) -> dict:
        """Auto-generate codename from resource.action if not provided."""
        if not attrs.get("codename"):
            resource = attrs.get("resource", "")
            action = attrs.get("action", "")
            if resource and action:
                attrs["codename"] = f"{resource}.{action}"
        return attrs


# ── Role ─────────────────────────────────────────────────────────────


class RoleSerializer(serializers.ModelSerializer):
    """Full CRUD serializer for Role with nested permissions."""

    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="permissions",
    )

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_system_role",
            "permissions",
            "permission_ids",
            "created_on",
            "updated_on",
            "is_deleted",
        ]
        read_only_fields = ["id", "created_on", "updated_on", "is_deleted"]
        extra_kwargs = {"slug": {"required": False}}

    def validate(self, attrs: dict) -> dict:
        """Auto-generate slug from name if not provided."""
        if not attrs.get("slug"):
            name = attrs.get("name", "")
            if name:
                attrs["slug"] = slugify(name)
        return attrs


class RoleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for role list views."""

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_system_role",
        ]
        read_only_fields = ["id"]


# ── UserProfile ──────────────────────────────────────────────────────


class UserProfileSerializer(serializers.ModelSerializer):
    """Full CRUD serializer for UserProfile."""

    roles = RoleListSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "user_email",
            "display_name",
            "job_title",
            "department",
            "phone",
            "avatar",
            "timezone",
            "locale",
            "bio",
            "last_login_ip",
            "is_active",
            "roles",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on", "last_login_ip"]


class UserProfileListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for profile list views."""

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "display_name",
            "job_title",
            "department",
            "is_active",
        ]
        read_only_fields = ["id"]


# ── UserPreferences ──────────────────────────────────────────────────


class UserPreferencesSerializer(serializers.ModelSerializer):
    """CRUD serializer for UserPreferences."""

    class Meta:
        model = UserPreferences
        fields = [
            "id",
            "user",
            "theme",
            "items_per_page",
            "email_notifications",
            "push_notifications",
            "dashboard_layout",
            "sidebar_collapsed",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "user", "created_on", "updated_on"]


# ── LoginHistory ─────────────────────────────────────────────────────


class LoginHistorySerializer(serializers.ModelSerializer):
    """Read-only serializer for LoginHistory."""

    class Meta:
        model = LoginHistory
        fields = [
            "id",
            "user",
            "event_type",
            "ip_address",
            "user_agent",
            "success",
            "failure_reason",
            "timestamp",
        ]
        read_only_fields = fields


# ── UserRole ─────────────────────────────────────────────────────────


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for role assignment (UserRole through model)."""

    role_name = serializers.CharField(source="role.name", read_only=True)
    role_slug = serializers.SlugField(source="role.slug", read_only=True)

    class Meta:
        model = UserRole
        fields = [
            "id",
            "user_profile",
            "role",
            "role_name",
            "role_slug",
            "assigned_by",
            "assigned_at",
            "is_primary",
        ]
        read_only_fields = ["id", "assigned_at", "role_name", "role_slug"]
