"""
Model-level tests for the Users app.

These tests verify model field configurations, validators, constraints,
manager/queryset methods, decorator logic, and model behaviours using
the ``_meta`` API and mocking — no database hits required.

The full CRUD DB tests are deferred because the Users app models live
in tenant schemas (django-tenants), and database tests would need
``TenantTestCase`` with a PostgreSQL backend.  The tests here provide
comprehensive coverage without requiring a running database.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from unittest.mock import MagicMock, Mock, PropertyMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.http import JsonResponse
from django.test import RequestFactory

from apps.users.models import (
    DEFAULT_LOCALE,
    DEFAULT_THEME,
    DEFAULT_TIMEZONE,
    LOGIN_EVENT_CHOICES,
    PHONE_REGEX,
    THEME_CHOICES,
    LoginHistory,
    Permission,
    Role,
    UserPreferences,
    UserProfile,
    UserRole,
)
from apps.users.managers import (
    LoginHistoryManager,
    LoginHistoryQuerySet,
    RoleManager,
    RoleQuerySet,
)
from apps.users.decorators import (
    require_all_permissions,
    require_any_permission,
    require_permission,
    require_role,
)


# =====================================================================
# Helper utilities
# =====================================================================


def _get_field(model, name):
    """Shortcut to retrieve a field from model._meta."""
    return model._meta.get_field(name)


def _field_names(model):
    """Return set of concrete field names (excl. reverse relations)."""
    return {f.name for f in model._meta.get_fields() if hasattr(f, "column")}


# =====================================================================
# UserProfile — field configuration & meta
# =====================================================================


class TestUserProfileFieldConfig:
    """Verify every field on UserProfile is configured correctly."""

    def test_user_field_is_one_to_one(self):
        field = _get_field(UserProfile, "user")
        assert isinstance(field, models.OneToOneField)

    def test_user_related_name(self):
        field = _get_field(UserProfile, "user")
        assert field.remote_field.related_name == "profile"

    def test_user_on_delete_cascade(self):
        field = _get_field(UserProfile, "user")
        assert field.remote_field.on_delete is models.CASCADE

    def test_display_name_max_length(self):
        assert _get_field(UserProfile, "display_name").max_length == 150

    def test_display_name_blank_default(self):
        field = _get_field(UserProfile, "display_name")
        assert field.blank is True
        assert field.default == ""

    def test_job_title_max_length(self):
        assert _get_field(UserProfile, "job_title").max_length == 100

    def test_department_max_length(self):
        assert _get_field(UserProfile, "department").max_length == 100

    def test_phone_max_length(self):
        assert _get_field(UserProfile, "phone").max_length == 20

    def test_phone_has_regex_validator(self):
        field = _get_field(UserProfile, "phone")
        regex_validators = [
            v for v in field.validators if isinstance(v, RegexValidator)
        ]
        assert len(regex_validators) == 1
        assert regex_validators[0].regex.pattern == PHONE_REGEX

    def test_avatar_upload_to(self):
        field = _get_field(UserProfile, "avatar")
        assert "users/avatars/" in field.upload_to

    def test_avatar_nullable_and_blank(self):
        field = _get_field(UserProfile, "avatar")
        assert field.null is True
        assert field.blank is True

    def test_timezone_default(self):
        assert _get_field(UserProfile, "timezone").default == DEFAULT_TIMEZONE

    def test_timezone_max_length(self):
        assert _get_field(UserProfile, "timezone").max_length == 50

    def test_locale_default(self):
        assert _get_field(UserProfile, "locale").default == DEFAULT_LOCALE

    def test_locale_max_length(self):
        assert _get_field(UserProfile, "locale").max_length == 10

    def test_bio_blank_default(self):
        field = _get_field(UserProfile, "bio")
        assert field.blank is True
        assert field.default == ""

    def test_last_login_ip_nullable(self):
        field = _get_field(UserProfile, "last_login_ip")
        assert field.null is True
        assert field.blank is True

    def test_last_login_ip_is_generic_ip(self):
        field = _get_field(UserProfile, "last_login_ip")
        assert isinstance(field, models.GenericIPAddressField)

    def test_roles_m2m_through_user_role(self):
        field = _get_field(UserProfile, "roles")
        assert field.remote_field.through is UserRole

    def test_roles_m2m_related_name(self):
        field = _get_field(UserProfile, "roles")
        assert field.remote_field.related_name == "user_profiles"

    def test_inherits_uuid_mixin(self):
        field = _get_field(UserProfile, "id")
        assert isinstance(field, models.UUIDField)
        assert field.primary_key is True

    def test_inherits_timestamp_mixin(self):
        assert "created_on" in _field_names(UserProfile)
        assert "updated_on" in _field_names(UserProfile)

    def test_inherits_soft_delete_mixin(self):
        assert "is_deleted" in _field_names(UserProfile)
        assert "deleted_on" in _field_names(UserProfile)

    def test_inherits_status_mixin(self):
        assert "is_active" in _field_names(UserProfile)
        assert "deactivated_on" in _field_names(UserProfile)


class TestUserProfileMeta:
    """Meta options for UserProfile."""

    def test_db_table(self):
        assert UserProfile._meta.db_table == "users_userprofile"

    def test_verbose_name(self):
        assert UserProfile._meta.verbose_name == "User Profile"

    def test_verbose_name_plural(self):
        assert UserProfile._meta.verbose_name_plural == "User Profiles"

    def test_ordering(self):
        assert UserProfile._meta.ordering == ["display_name"]


class TestUserProfileStr:
    """__str__ representation for UserProfile."""

    def test_str_with_display_name(self):
        mock_self = Mock()
        mock_self.display_name = "Jane Doe"
        result = UserProfile.__str__(mock_self)
        assert result == "Profile: Jane Doe"

    def test_str_falls_back_to_user(self):
        mock_self = Mock()
        mock_self.display_name = ""
        mock_self.user.__str__ = Mock(return_value="user@example.com")
        result = UserProfile.__str__(mock_self)
        assert result == "Profile: user@example.com"


class TestUserProfileManagers:
    """Verify manager assignments on UserProfile."""

    def test_default_manager_is_active_manager(self):
        from apps.core.managers import ActiveManager

        assert isinstance(UserProfile.objects, ActiveManager)

    def test_all_objects_is_soft_delete_manager(self):
        from apps.core.managers import SoftDeleteManager

        assert isinstance(UserProfile.all_objects, SoftDeleteManager)


# =====================================================================
# UserPreferences — field configuration & meta
# =====================================================================


class TestUserPreferencesFieldConfig:
    """Verify every field on UserPreferences is configured correctly."""

    def test_user_field_is_one_to_one(self):
        field = _get_field(UserPreferences, "user")
        assert isinstance(field, models.OneToOneField)

    def test_user_related_name(self):
        field = _get_field(UserPreferences, "user")
        assert field.remote_field.related_name == "preferences"

    def test_user_on_delete_cascade(self):
        field = _get_field(UserPreferences, "user")
        assert field.remote_field.on_delete is models.CASCADE

    def test_theme_choices(self):
        field = _get_field(UserPreferences, "theme")
        assert field.choices == THEME_CHOICES

    def test_theme_default(self):
        assert _get_field(UserPreferences, "theme").default == DEFAULT_THEME

    def test_theme_max_length(self):
        assert _get_field(UserPreferences, "theme").max_length == 20

    def test_items_per_page_default(self):
        assert _get_field(UserPreferences, "items_per_page").default == 25

    def test_items_per_page_is_positive_small_int(self):
        field = _get_field(UserPreferences, "items_per_page")
        assert isinstance(field, models.PositiveSmallIntegerField)

    def test_email_notifications_default(self):
        assert _get_field(UserPreferences, "email_notifications").default is True

    def test_push_notifications_default(self):
        assert _get_field(UserPreferences, "push_notifications").default is True

    def test_dashboard_layout_default(self):
        field = _get_field(UserPreferences, "dashboard_layout")
        assert field.default is dict

    def test_dashboard_layout_is_json_field(self):
        field = _get_field(UserPreferences, "dashboard_layout")
        assert isinstance(field, models.JSONField)

    def test_sidebar_collapsed_default(self):
        assert _get_field(UserPreferences, "sidebar_collapsed").default is False

    def test_inherits_uuid_mixin(self):
        field = _get_field(UserPreferences, "id")
        assert isinstance(field, models.UUIDField)
        assert field.primary_key is True

    def test_inherits_timestamp_mixin(self):
        assert "created_on" in _field_names(UserPreferences)
        assert "updated_on" in _field_names(UserPreferences)


class TestUserPreferencesMeta:
    """Meta options for UserPreferences."""

    def test_db_table(self):
        assert UserPreferences._meta.db_table == "users_userpreferences"

    def test_verbose_name(self):
        assert UserPreferences._meta.verbose_name == "User Preferences"

    def test_verbose_name_plural(self):
        assert UserPreferences._meta.verbose_name_plural == "User Preferences"


class TestUserPreferencesStr:
    """__str__ representation for UserPreferences."""

    def test_str_representation(self):
        mock_self = Mock()
        mock_self.user.__str__ = Mock(return_value="user@example.com")
        result = UserPreferences.__str__(mock_self)
        assert result == "Preferences: user@example.com"


# =====================================================================
# LoginHistory — field configuration & meta
# =====================================================================


class TestLoginHistoryFieldConfig:
    """Verify every field on LoginHistory is configured correctly."""

    def test_user_field_is_fk(self):
        field = _get_field(LoginHistory, "user")
        assert isinstance(field, models.ForeignKey)

    def test_user_related_name(self):
        field = _get_field(LoginHistory, "user")
        assert field.remote_field.related_name == "login_history"

    def test_user_on_delete_cascade(self):
        field = _get_field(LoginHistory, "user")
        assert field.remote_field.on_delete is models.CASCADE

    def test_event_type_choices(self):
        field = _get_field(LoginHistory, "event_type")
        assert field.choices == LOGIN_EVENT_CHOICES

    def test_event_type_max_length(self):
        assert _get_field(LoginHistory, "event_type").max_length == 20

    def test_event_type_db_index(self):
        assert _get_field(LoginHistory, "event_type").db_index is True

    def test_ip_address_nullable(self):
        field = _get_field(LoginHistory, "ip_address")
        assert field.null is True
        assert field.blank is True

    def test_ip_address_is_generic_ip(self):
        field = _get_field(LoginHistory, "ip_address")
        assert isinstance(field, models.GenericIPAddressField)

    def test_user_agent_blank_default(self):
        field = _get_field(LoginHistory, "user_agent")
        assert field.blank is True
        assert field.default == ""

    def test_success_default(self):
        assert _get_field(LoginHistory, "success").default is True

    def test_failure_reason_blank_default(self):
        field = _get_field(LoginHistory, "failure_reason")
        assert field.blank is True
        assert field.default == ""

    def test_failure_reason_max_length(self):
        assert _get_field(LoginHistory, "failure_reason").max_length == 255

    def test_timestamp_db_index(self):
        assert _get_field(LoginHistory, "timestamp").db_index is True

    def test_inherits_uuid_mixin(self):
        field = _get_field(LoginHistory, "id")
        assert isinstance(field, models.UUIDField)
        assert field.primary_key is True

    def test_does_not_inherit_timestamp_mixin(self):
        """LoginHistory has its own 'timestamp' but NOT created_on/updated_on."""
        assert "created_on" not in _field_names(LoginHistory)
        assert "updated_on" not in _field_names(LoginHistory)


class TestLoginHistoryMeta:
    """Meta options for LoginHistory."""

    def test_db_table(self):
        assert LoginHistory._meta.db_table == "users_loginhistory"

    def test_verbose_name(self):
        assert LoginHistory._meta.verbose_name == "Login History"

    def test_verbose_name_plural(self):
        assert LoginHistory._meta.verbose_name_plural == "Login History"

    def test_ordering(self):
        assert LoginHistory._meta.ordering == ["-timestamp"]

    def test_indexes_count(self):
        """LoginHistory defines 3 custom indexes."""
        assert len(LoginHistory._meta.indexes) == 3

    def test_index_names(self):
        names = {idx.name for idx in LoginHistory._meta.indexes}
        expected = {
            "idx_login_history_user_time",
            "idx_login_history_event_time",
            "idx_login_history_ip",
        }
        assert expected == names


class TestLoginHistoryStr:
    """__str__ representation for LoginHistory."""

    def test_str_representation(self):
        mock_self = Mock()
        mock_self.event_type = "login_success"
        mock_self.user.__str__ = Mock(return_value="admin@test.com")
        mock_self.timestamp = datetime(2025, 6, 15, 10, 30)
        result = LoginHistory.__str__(mock_self)
        assert result == "login_success: admin@test.com @ 2025-06-15 10:30"


# =====================================================================
# Permission — field configuration & meta
# =====================================================================


class TestPermissionFieldConfig:
    """Verify every field on Permission is configured correctly."""

    def test_codename_unique(self):
        assert _get_field(Permission, "codename").unique is True

    def test_codename_db_index(self):
        assert _get_field(Permission, "codename").db_index is True

    def test_codename_max_length(self):
        assert _get_field(Permission, "codename").max_length == 100

    def test_name_max_length(self):
        assert _get_field(Permission, "name").max_length == 200

    def test_description_blank_default(self):
        field = _get_field(Permission, "description")
        assert field.blank is True
        assert field.default == ""

    def test_resource_max_length(self):
        assert _get_field(Permission, "resource").max_length == 50

    def test_resource_db_index(self):
        assert _get_field(Permission, "resource").db_index is True

    def test_action_max_length(self):
        assert _get_field(Permission, "action").max_length == 50

    def test_is_active_default(self):
        assert _get_field(Permission, "is_active").default is True

    def test_is_active_db_index(self):
        assert _get_field(Permission, "is_active").db_index is True

    def test_inherits_uuid_mixin(self):
        field = _get_field(Permission, "id")
        assert isinstance(field, models.UUIDField)
        assert field.primary_key is True

    def test_inherits_timestamp_mixin(self):
        assert "created_on" in _field_names(Permission)
        assert "updated_on" in _field_names(Permission)


class TestPermissionMeta:
    """Meta options for Permission."""

    def test_db_table(self):
        assert Permission._meta.db_table == "users_permission"

    def test_ordering(self):
        assert Permission._meta.ordering == ["resource", "action"]

    def test_indexes_count(self):
        assert len(Permission._meta.indexes) == 1

    def test_index_name(self):
        assert Permission._meta.indexes[0].name == "idx_perm_resource_action"


class TestPermissionStr:
    """__str__ representation for Permission."""

    def test_str_representation(self):
        perm = Permission.__new__(Permission)
        perm.resource = "orders"
        perm.action = "create"
        assert str(perm) == "orders.create"


class TestPermissionSaveAutoCodename:
    """Test Permission.save() auto-generates codename."""

    def test_save_auto_generates_codename_when_empty(self):
        """Codename should be auto-set to '{resource}.{action}' if blank."""
        perm = Permission.__new__(Permission)
        perm.codename = ""
        perm.resource = "inventory"
        perm.action = "view"
        perm.name = "View Inventory"
        perm.description = ""
        perm.is_active = True
        perm.id = uuid.uuid4()

        with patch.object(models.Model, "save"):
            perm.save()

        assert perm.codename == "inventory.view"

    def test_save_preserves_explicit_codename(self):
        """If codename is already set, save() should not overwrite it."""
        perm = Permission.__new__(Permission)
        perm.codename = "custom.perm"
        perm.resource = "orders"
        perm.action = "create"
        perm.name = "Custom"
        perm.description = ""
        perm.is_active = True
        perm.id = uuid.uuid4()

        with patch.object(models.Model, "save"):
            perm.save()

        assert perm.codename == "custom.perm"


# =====================================================================
# Role — field configuration & meta
# =====================================================================


class TestRoleFieldConfig:
    """Verify every field on Role is configured correctly."""

    def test_name_max_length(self):
        assert _get_field(Role, "name").max_length == 100

    def test_name_db_index(self):
        assert _get_field(Role, "name").db_index is True

    def test_slug_max_length(self):
        assert _get_field(Role, "slug").max_length == 100

    def test_slug_db_index(self):
        assert _get_field(Role, "slug").db_index is True

    def test_slug_field_type(self):
        assert isinstance(_get_field(Role, "slug"), models.SlugField)

    def test_description_blank_default(self):
        field = _get_field(Role, "description")
        assert field.blank is True
        assert field.default == ""

    def test_is_system_role_default(self):
        assert _get_field(Role, "is_system_role").default is False

    def test_permissions_m2m_related_name(self):
        field = _get_field(Role, "permissions")
        assert field.remote_field.related_name == "roles"

    def test_permissions_m2m_blank(self):
        field = _get_field(Role, "permissions")
        assert field.blank is True

    def test_inherits_uuid_mixin(self):
        field = _get_field(Role, "id")
        assert isinstance(field, models.UUIDField)
        assert field.primary_key is True

    def test_inherits_timestamp_mixin(self):
        assert "created_on" in _field_names(Role)
        assert "updated_on" in _field_names(Role)

    def test_inherits_soft_delete_mixin(self):
        assert "is_deleted" in _field_names(Role)
        assert "deleted_on" in _field_names(Role)


class TestRoleMeta:
    """Meta options for Role."""

    def test_db_table(self):
        assert Role._meta.db_table == "users_role"

    def test_ordering(self):
        assert Role._meta.ordering == ["name"]

    def test_constraints_count(self):
        assert len(Role._meta.constraints) == 1

    def test_unique_active_role_slug_constraint(self):
        constraint = Role._meta.constraints[0]
        assert isinstance(constraint, models.UniqueConstraint)
        assert constraint.name == "unique_active_role_slug"
        assert list(constraint.fields) == ["slug"]

    def test_unique_constraint_condition(self):
        """The constraint only applies to non-deleted roles."""
        constraint = Role._meta.constraints[0]
        assert constraint.condition == models.Q(is_deleted=False)


class TestRoleStr:
    """__str__ representation for Role."""

    def test_str_representation(self):
        role = Role.__new__(Role)
        role.name = "Manager"
        assert str(role) == "Manager"


class TestRoleManagers:
    """Verify manager assignments on Role."""

    def test_default_manager_is_soft_delete_manager(self):
        from apps.core.managers import SoftDeleteManager

        assert isinstance(Role.objects, SoftDeleteManager)

    def test_all_objects_is_base_manager(self):
        assert isinstance(Role.all_objects, models.Manager)


class TestRoleHasPermission:
    """Test Role.has_permission() without hitting the DB."""

    def test_has_permission_returns_true_when_exists(self):
        mock_self = Mock()
        mock_self.permissions.filter.return_value.exists.return_value = True

        assert Role.has_permission(mock_self, "orders.create") is True
        mock_self.permissions.filter.assert_called_once_with(codename="orders.create")

    def test_has_permission_returns_false_when_missing(self):
        mock_self = Mock()
        mock_self.permissions.filter.return_value.exists.return_value = False

        assert Role.has_permission(mock_self, "secret.launch") is False


# =====================================================================
# UserRole — field configuration & meta
# =====================================================================


class TestUserRoleFieldConfig:
    """Verify every field on UserRole (through model) is configured correctly."""

    def test_user_profile_fk(self):
        field = _get_field(UserRole, "user_profile")
        assert isinstance(field, models.ForeignKey)

    def test_user_profile_related_name(self):
        field = _get_field(UserRole, "user_profile")
        assert field.remote_field.related_name == "user_roles"

    def test_user_profile_on_delete_cascade(self):
        field = _get_field(UserRole, "user_profile")
        assert field.remote_field.on_delete is models.CASCADE

    def test_role_fk(self):
        field = _get_field(UserRole, "role")
        assert isinstance(field, models.ForeignKey)

    def test_role_related_name(self):
        field = _get_field(UserRole, "role")
        assert field.remote_field.related_name == "user_roles"

    def test_role_on_delete_cascade(self):
        field = _get_field(UserRole, "role")
        assert field.remote_field.on_delete is models.CASCADE

    def test_assigned_by_nullable(self):
        field = _get_field(UserRole, "assigned_by")
        assert field.null is True
        assert field.blank is True

    def test_assigned_by_on_delete_set_null(self):
        field = _get_field(UserRole, "assigned_by")
        assert field.remote_field.on_delete is models.SET_NULL

    def test_assigned_by_related_name(self):
        field = _get_field(UserRole, "assigned_by")
        assert field.remote_field.related_name == "role_assignments_made"

    def test_assigned_at_auto_now_add(self):
        field = _get_field(UserRole, "assigned_at")
        assert field.auto_now_add is True

    def test_is_primary_default(self):
        assert _get_field(UserRole, "is_primary").default is False

    def test_inherits_uuid_mixin(self):
        field = _get_field(UserRole, "id")
        assert isinstance(field, models.UUIDField)
        assert field.primary_key is True

    def test_inherits_timestamp_mixin(self):
        assert "created_on" in _field_names(UserRole)
        assert "updated_on" in _field_names(UserRole)


class TestUserRoleMeta:
    """Meta options for UserRole."""

    def test_db_table(self):
        assert UserRole._meta.db_table == "users_userrole"

    def test_verbose_name(self):
        assert UserRole._meta.verbose_name == "User Role Assignment"

    def test_verbose_name_plural(self):
        assert UserRole._meta.verbose_name_plural == "User Role Assignments"

    def test_constraints_count(self):
        assert len(UserRole._meta.constraints) == 1

    def test_unique_user_role_constraint(self):
        constraint = UserRole._meta.constraints[0]
        assert isinstance(constraint, models.UniqueConstraint)
        assert constraint.name == "unique_user_role"
        assert set(constraint.fields) == {"user_profile", "role"}


class TestUserRoleStr:
    """__str__ representation for UserRole."""

    def test_str_representation(self):
        mock_self = Mock()
        mock_self.user_profile.__str__ = Mock(return_value="Profile: Jane")
        mock_self.role.__str__ = Mock(return_value="Admin")
        result = UserRole.__str__(mock_self)
        assert result == "Profile: Jane \u2192 Admin"


# =====================================================================
# LoginHistoryQuerySet — method inspection & mock-based logic
# =====================================================================


class TestLoginHistoryQuerySet:
    """Verify LoginHistoryQuerySet filtering methods exist and behave."""

    def test_successful_method_exists(self):
        assert callable(getattr(LoginHistoryQuerySet, "successful", None))

    def test_failed_method_exists(self):
        assert callable(getattr(LoginHistoryQuerySet, "failed", None))

    def test_logins_method_exists(self):
        assert callable(getattr(LoginHistoryQuerySet, "logins", None))

    def test_for_user_method_exists(self):
        assert callable(getattr(LoginHistoryQuerySet, "for_user", None))

    def test_for_ip_method_exists(self):
        assert callable(getattr(LoginHistoryQuerySet, "for_ip", None))

    def test_recent_method_exists(self):
        assert callable(getattr(LoginHistoryQuerySet, "recent", None))

    def test_successful_calls_filter(self):
        qs = MagicMock(spec=LoginHistoryQuerySet)
        LoginHistoryQuerySet.successful(qs)
        qs.filter.assert_called_once_with(success=True)

    def test_failed_calls_filter(self):
        qs = MagicMock(spec=LoginHistoryQuerySet)
        LoginHistoryQuerySet.failed(qs)
        qs.filter.assert_called_once_with(success=False)

    def test_logins_calls_filter_with_event_types(self):
        qs = MagicMock(spec=LoginHistoryQuerySet)
        LoginHistoryQuerySet.logins(qs)
        qs.filter.assert_called_once_with(
            event_type__in=("login_success", "login_failed")
        )

    def test_for_user_calls_filter(self):
        qs = MagicMock(spec=LoginHistoryQuerySet)
        sentinel_user = object()
        LoginHistoryQuerySet.for_user(qs, sentinel_user)
        qs.filter.assert_called_once_with(user=sentinel_user)

    def test_for_ip_calls_filter(self):
        qs = MagicMock(spec=LoginHistoryQuerySet)
        LoginHistoryQuerySet.for_ip(qs, "192.168.1.1")
        qs.filter.assert_called_once_with(ip_address="192.168.1.1")

    def test_recent_orders_and_slices(self):
        qs = MagicMock(spec=LoginHistoryQuerySet)
        LoginHistoryQuerySet.recent(qs, limit=10)
        qs.order_by.assert_called_once_with("-timestamp")
        qs.order_by.return_value.__getitem__.assert_called_once_with(slice(None, 10))

    def test_recent_default_limit_50(self):
        qs = MagicMock(spec=LoginHistoryQuerySet)
        LoginHistoryQuerySet.recent(qs)
        qs.order_by.return_value.__getitem__.assert_called_once_with(slice(None, 50))


# =====================================================================
# LoginHistoryManager — delegation to QuerySet
# =====================================================================


class TestLoginHistoryManager:
    """Verify LoginHistoryManager delegates to LoginHistoryQuerySet."""

    def test_manager_class_exists(self):
        assert LoginHistoryManager is not None

    def test_successful_method_exists(self):
        assert callable(getattr(LoginHistoryManager, "successful", None))

    def test_failed_method_exists(self):
        assert callable(getattr(LoginHistoryManager, "failed", None))

    def test_logins_method_exists(self):
        assert callable(getattr(LoginHistoryManager, "logins", None))

    def test_get_queryset_returns_login_history_queryset(self):
        """Manager.get_queryset() should return LoginHistoryQuerySet type."""
        manager = LoginHistoryManager()
        manager.model = LoginHistory
        manager._db = None
        qs = manager.get_queryset()
        assert isinstance(qs, LoginHistoryQuerySet)


# =====================================================================
# RoleQuerySet — method inspection & mock-based logic
# =====================================================================


class TestRoleQuerySet:
    """Verify RoleQuerySet filtering methods exist and behave."""

    def test_system_roles_method_exists(self):
        assert callable(getattr(RoleQuerySet, "system_roles", None))

    def test_custom_roles_method_exists(self):
        assert callable(getattr(RoleQuerySet, "custom_roles", None))

    def test_with_permission_method_exists(self):
        assert callable(getattr(RoleQuerySet, "with_permission", None))

    def test_with_users_method_exists(self):
        assert callable(getattr(RoleQuerySet, "with_users", None))

    def test_system_roles_calls_filter(self):
        qs = MagicMock(spec=RoleQuerySet)
        RoleQuerySet.system_roles(qs)
        qs.filter.assert_called_once_with(is_system_role=True)

    def test_custom_roles_calls_filter(self):
        qs = MagicMock(spec=RoleQuerySet)
        RoleQuerySet.custom_roles(qs)
        qs.filter.assert_called_once_with(is_system_role=False)

    def test_with_permission_calls_filter(self):
        qs = MagicMock(spec=RoleQuerySet)
        RoleQuerySet.with_permission(qs, "orders.create")
        qs.filter.assert_called_once_with(permissions__codename="orders.create")

    def test_with_users_calls_filter_and_distinct(self):
        qs = MagicMock(spec=RoleQuerySet)
        RoleQuerySet.with_users(qs)
        qs.filter.assert_called_once_with(user_roles__isnull=False)
        qs.filter.return_value.distinct.assert_called_once()


# =====================================================================
# RoleManager — delegation to QuerySet
# =====================================================================


class TestRoleManager:
    """Verify RoleManager delegates to RoleQuerySet."""

    def test_manager_class_exists(self):
        assert RoleManager is not None

    def test_system_roles_method_exists(self):
        assert callable(getattr(RoleManager, "system_roles", None))

    def test_custom_roles_method_exists(self):
        assert callable(getattr(RoleManager, "custom_roles", None))

    def test_with_permission_method_exists(self):
        assert callable(getattr(RoleManager, "with_permission", None))

    def test_get_queryset_returns_role_queryset(self):
        manager = RoleManager()
        manager.model = Role
        manager._db = None
        qs = manager.get_queryset()
        assert isinstance(qs, RoleQuerySet)


# =====================================================================
# Constants / Choices tests
# =====================================================================


class TestModelConstants:
    """Verify constant values used across models."""

    def test_phone_regex_pattern(self):
        assert PHONE_REGEX == r"^\+94\s?\d{2}\s?\d{3}\s?\d{4}$"

    def test_default_timezone(self):
        assert DEFAULT_TIMEZONE == "Asia/Colombo"

    def test_default_locale(self):
        assert DEFAULT_LOCALE == "en"

    def test_default_theme(self):
        assert DEFAULT_THEME == "system"

    def test_theme_choices_count(self):
        assert len(THEME_CHOICES) == 3

    def test_theme_choice_values(self):
        values = [c[0] for c in THEME_CHOICES]
        assert values == ["light", "dark", "system"]

    def test_login_event_choices_count(self):
        assert len(LOGIN_EVENT_CHOICES) == 7

    def test_login_event_choice_values(self):
        values = [c[0] for c in LOGIN_EVENT_CHOICES]
        expected = [
            "login_success",
            "login_failed",
            "logout",
            "token_refresh",
            "password_change",
            "password_reset",
            "account_locked",
        ]
        assert values == expected


# =====================================================================
# Phone Regex Validator tests
# =====================================================================


class TestPhoneRegexValidation:
    """Test the Sri Lankan phone regex used by UserProfile.phone."""

    import re

    pattern = re.compile(PHONE_REGEX)

    @pytest.mark.parametrize(
        "valid_phone",
        [
            "+94 77 123 4567",
            "+9477 123 4567",
            "+94771234567",
            "+94 11 234 5678",
            "+9411 234 5678",
        ],
    )
    def test_valid_phone_numbers(self, valid_phone):
        assert self.pattern.match(valid_phone) is not None

    @pytest.mark.parametrize(
        "invalid_phone",
        [
            "0771234567",          # missing +94
            "+94",                 # too short
            "+94 77 123 456",      # one digit short
            "+94 77 123 45678",    # one digit too many
            "+1 777 123 4567",     # wrong country code
            "not-a-number",
            "",
        ],
    )
    def test_invalid_phone_numbers(self, invalid_phone):
        assert self.pattern.match(invalid_phone) is None


# =====================================================================
# Decorator tests — require_permission
# =====================================================================


class TestRequirePermissionDecorator:
    """Test require_permission decorator logic with mocks."""

    def _make_request(self, *, authenticated=True, superuser=False, profile=None):
        factory = RequestFactory()
        request = factory.get("/test/")
        user = Mock()
        user.is_authenticated = authenticated
        user.is_superuser = superuser
        if profile is not None:
            user.profile = profile
        else:
            # No profile attribute at all
            user.profile = None
        request.user = user
        return request

    def _dummy_view(self, request):
        return JsonResponse({"ok": True})

    def test_unauthenticated_returns_401(self):
        decorated = require_permission("orders.create")(self._dummy_view)
        request = self._make_request(authenticated=False)
        resp = decorated(request)
        assert resp.status_code == 401

    def test_superuser_bypasses_check(self):
        decorated = require_permission("orders.create")(self._dummy_view)
        request = self._make_request(authenticated=True, superuser=True)
        resp = decorated(request)
        assert resp.status_code == 200

    def test_user_with_permission_allowed(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = True
        decorated = require_permission("orders.create")(self._dummy_view)
        request = self._make_request(profile=profile)
        resp = decorated(request)
        assert resp.status_code == 200

    def test_user_without_permission_denied(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = False
        decorated = require_permission("orders.create")(self._dummy_view)
        request = self._make_request(profile=profile)
        resp = decorated(request)
        assert resp.status_code == 403

    def test_user_no_profile_denied(self):
        decorated = require_permission("orders.create")(self._dummy_view)
        request = self._make_request(profile=None)
        resp = decorated(request)
        assert resp.status_code == 403

    def test_permission_codename_passed_to_filter(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = True
        decorated = require_permission("inventory.view")(self._dummy_view)
        request = self._make_request(profile=profile)
        decorated(request)
        profile.roles.filter.assert_called_once_with(
            permissions__codename="inventory.view",
            is_deleted=False,
        )


# =====================================================================
# Decorator tests — require_any_permission
# =====================================================================


class TestRequireAnyPermissionDecorator:
    """Test require_any_permission decorator logic with mocks."""

    def _make_request(self, *, authenticated=True, superuser=False, profile=None):
        factory = RequestFactory()
        request = factory.get("/test/")
        user = Mock()
        user.is_authenticated = authenticated
        user.is_superuser = superuser
        user.profile = profile
        request.user = user
        return request

    def _dummy_view(self, request):
        return JsonResponse({"ok": True})

    def test_unauthenticated_returns_401(self):
        decorated = require_any_permission("a", "b")(self._dummy_view)
        request = self._make_request(authenticated=False)
        assert decorated(request).status_code == 401

    def test_superuser_bypasses(self):
        decorated = require_any_permission("a", "b")(self._dummy_view)
        request = self._make_request(superuser=True)
        assert decorated(request).status_code == 200

    def test_has_any_permission_allowed(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = True
        decorated = require_any_permission("a", "b")(self._dummy_view)
        request = self._make_request(profile=profile)
        assert decorated(request).status_code == 200

    def test_has_none_denied(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = False
        decorated = require_any_permission("a", "b")(self._dummy_view)
        request = self._make_request(profile=profile)
        assert decorated(request).status_code == 403

    def test_codenames_passed_as_in_lookup(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = True
        decorated = require_any_permission("x", "y")(self._dummy_view)
        request = self._make_request(profile=profile)
        decorated(request)
        profile.roles.filter.assert_called_once_with(
            permissions__codename__in=("x", "y"),
            is_deleted=False,
        )


# =====================================================================
# Decorator tests — require_all_permissions
# =====================================================================


class TestRequireAllPermissionsDecorator:
    """Test require_all_permissions decorator logic with mocks."""

    def _make_request(self, *, authenticated=True, superuser=False, profile=None):
        factory = RequestFactory()
        request = factory.get("/test/")
        user = Mock()
        user.is_authenticated = authenticated
        user.is_superuser = superuser
        user.profile = profile
        request.user = user
        return request

    def _dummy_view(self, request):
        return JsonResponse({"ok": True})

    def test_unauthenticated_returns_401(self):
        decorated = require_all_permissions("a", "b")(self._dummy_view)
        request = self._make_request(authenticated=False)
        assert decorated(request).status_code == 401

    def test_superuser_bypasses(self):
        decorated = require_all_permissions("a", "b")(self._dummy_view)
        request = self._make_request(superuser=True)
        assert decorated(request).status_code == 200

    def test_all_permissions_present_allowed(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = True
        decorated = require_all_permissions("a", "b")(self._dummy_view)
        request = self._make_request(profile=profile)
        assert decorated(request).status_code == 200

    def test_missing_one_permission_denied(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.side_effect = [True, False]
        decorated = require_all_permissions("a", "b")(self._dummy_view)
        request = self._make_request(profile=profile)
        resp = decorated(request)
        assert resp.status_code == 403
        body = json.loads(resp.content)
        assert body["missing"] == "b"

    def test_no_profile_denied(self):
        decorated = require_all_permissions("a")(self._dummy_view)
        request = self._make_request(profile=None)
        assert decorated(request).status_code == 403


# =====================================================================
# Decorator tests — require_role
# =====================================================================


class TestRequireRoleDecorator:
    """Test require_role decorator logic with mocks."""

    def _make_request(self, *, authenticated=True, superuser=False, profile=None):
        factory = RequestFactory()
        request = factory.get("/test/")
        user = Mock()
        user.is_authenticated = authenticated
        user.is_superuser = superuser
        user.profile = profile
        request.user = user
        return request

    def _dummy_view(self, request):
        return JsonResponse({"ok": True})

    def test_unauthenticated_returns_401(self):
        decorated = require_role("admin")(self._dummy_view)
        request = self._make_request(authenticated=False)
        assert decorated(request).status_code == 401

    def test_superuser_bypasses(self):
        decorated = require_role("admin")(self._dummy_view)
        request = self._make_request(superuser=True)
        assert decorated(request).status_code == 200

    def test_user_has_role_allowed(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = True
        decorated = require_role("manager")(self._dummy_view)
        request = self._make_request(profile=profile)
        assert decorated(request).status_code == 200

    def test_user_missing_role_denied(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = False
        decorated = require_role("admin")(self._dummy_view)
        request = self._make_request(profile=profile)
        resp = decorated(request)
        assert resp.status_code == 403
        body = json.loads(resp.content)
        assert body["required_role"] == "admin"

    def test_slug_passed_to_filter(self):
        profile = Mock()
        profile.roles.filter.return_value.exists.return_value = True
        decorated = require_role("cashier")(self._dummy_view)
        request = self._make_request(profile=profile)
        decorated(request)
        profile.roles.filter.assert_called_once_with(
            slug="cashier", is_deleted=False,
        )


# =====================================================================
# Cross-model relationship tests (via _meta)
# =====================================================================


class TestCrossModelRelationships:
    """Verify FK and M2M relationships between all 6 models."""

    def test_userprofile_fk_to_auth_user(self):
        field = _get_field(UserProfile, "user")
        from django.conf import settings

        assert field.related_model._meta.label == settings.AUTH_USER_MODEL

    def test_userpreferences_fk_to_auth_user(self):
        field = _get_field(UserPreferences, "user")
        from django.conf import settings

        assert field.related_model._meta.label == settings.AUTH_USER_MODEL

    def test_loginhistory_fk_to_auth_user(self):
        field = _get_field(LoginHistory, "user")
        from django.conf import settings

        assert field.related_model._meta.label == settings.AUTH_USER_MODEL

    def test_userrole_fk_to_userprofile(self):
        field = _get_field(UserRole, "user_profile")
        assert field.related_model is UserProfile

    def test_userrole_fk_to_role(self):
        field = _get_field(UserRole, "role")
        assert field.related_model is Role

    def test_userrole_assigned_by_fk_to_auth_user(self):
        field = _get_field(UserRole, "assigned_by")
        from django.conf import settings

        assert field.related_model._meta.label == settings.AUTH_USER_MODEL

    def test_role_permissions_m2m_to_permission(self):
        field = _get_field(Role, "permissions")
        assert field.related_model is Permission

    def test_userprofile_roles_m2m_through_userrole(self):
        field = _get_field(UserProfile, "roles")
        assert field.remote_field.through is UserRole
        assert field.related_model is Role


# =====================================================================
# Model class hierarchy tests
# =====================================================================


class TestModelInheritance:
    """Verify each model inherits from expected mixins."""

    def test_userprofile_inherits_uuid_mixin(self):
        from apps.core.mixins import UUIDMixin

        assert issubclass(UserProfile, UUIDMixin)

    def test_userprofile_inherits_timestamp_mixin(self):
        from apps.core.mixins import TimestampMixin

        assert issubclass(UserProfile, TimestampMixin)

    def test_userprofile_inherits_soft_delete_mixin(self):
        from apps.core.mixins import SoftDeleteMixin

        assert issubclass(UserProfile, SoftDeleteMixin)

    def test_userprofile_inherits_status_mixin(self):
        from apps.core.mixins import StatusMixin

        assert issubclass(UserProfile, StatusMixin)

    def test_userpreferences_inherits_uuid_mixin(self):
        from apps.core.mixins import UUIDMixin

        assert issubclass(UserPreferences, UUIDMixin)

    def test_userpreferences_inherits_timestamp_mixin(self):
        from apps.core.mixins import TimestampMixin

        assert issubclass(UserPreferences, TimestampMixin)

    def test_loginhistory_inherits_uuid_mixin(self):
        from apps.core.mixins import UUIDMixin

        assert issubclass(LoginHistory, UUIDMixin)

    def test_permission_inherits_uuid_mixin(self):
        from apps.core.mixins import UUIDMixin

        assert issubclass(Permission, UUIDMixin)

    def test_permission_inherits_timestamp_mixin(self):
        from apps.core.mixins import TimestampMixin

        assert issubclass(Permission, TimestampMixin)

    def test_role_inherits_uuid_mixin(self):
        from apps.core.mixins import UUIDMixin

        assert issubclass(Role, UUIDMixin)

    def test_role_inherits_timestamp_mixin(self):
        from apps.core.mixins import TimestampMixin

        assert issubclass(Role, TimestampMixin)

    def test_role_inherits_soft_delete_mixin(self):
        from apps.core.mixins import SoftDeleteMixin

        assert issubclass(Role, SoftDeleteMixin)

    def test_userrole_inherits_uuid_mixin(self):
        from apps.core.mixins import UUIDMixin

        assert issubclass(UserRole, UUIDMixin)

    def test_userrole_inherits_timestamp_mixin(self):
        from apps.core.mixins import TimestampMixin

        assert issubclass(UserRole, TimestampMixin)
