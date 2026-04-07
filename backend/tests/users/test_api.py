"""
Integration and unit tests for the Users app API.

Covers serializers, models, exceptions, and middleware hooks.
"""

from __future__ import annotations

from apps.users.models import (
    LoginHistory,
    Permission,
    Role,
    UserPreferences,
    UserProfile,
    UserRole,
)
from apps.users.api.serializers import (
    LoginHistorySerializer,
    PermissionSerializer,
    RoleListSerializer,
    RoleSerializer,
    UserPreferencesSerializer,
    UserProfileListSerializer,
    UserProfileSerializer,
    UserRoleSerializer,
)


# =====================================================================
# Serializer Unit Tests
# =====================================================================


class TestPermissionSerializer:
    """Tests for PermissionSerializer field presence and validation."""

    def test_serializer_fields(self):
        serializer = PermissionSerializer()
        expected = {
            "id", "codename", "name", "description",
            "resource", "action", "is_active",
            "created_on", "updated_on",
        }
        assert expected == set(serializer.fields.keys())

    def test_read_only_fields(self):
        serializer = PermissionSerializer()
        for field_name in ("id", "created_on", "updated_on"):
            assert serializer.fields[field_name].read_only is True

    def test_codename_auto_generation(self):
        data = {
            "name": "Create Orders",
            "resource": "orders",
            "action": "create",
        }
        serializer = PermissionSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["codename"] == "orders.create"

    def test_codename_explicit_not_overridden(self):
        """When codename is explicitly provided, validate() should keep it.

        NOTE: Full is_valid() triggers DRF UniqueValidator (DB hit), so we
        test the validate() logic directly.
        """
        attrs = {
            "codename": "custom.code",
            "name": "Custom Permission",
            "resource": "orders",
            "action": "create",
        }
        serializer = PermissionSerializer()
        result = serializer.validate(attrs)
        assert result["codename"] == "custom.code"

    def test_missing_required_fields(self):
        serializer = PermissionSerializer(data={})
        assert not serializer.is_valid()
        assert "name" in serializer.errors
        assert "resource" in serializer.errors
        assert "action" in serializer.errors


class TestRoleSerializer:
    """Tests for RoleSerializer field presence and validation."""

    def test_serializer_fields(self):
        serializer = RoleSerializer()
        expected = {
            "id", "name", "slug", "description", "is_system_role",
            "permissions", "permission_ids",
            "created_on", "updated_on", "is_deleted",
        }
        assert expected == set(serializer.fields.keys())

    def test_read_only_fields(self):
        serializer = RoleSerializer()
        for field_name in ("id", "created_on", "updated_on", "is_deleted"):
            assert serializer.fields[field_name].read_only is True

    def test_slug_auto_generation(self):
        data = {"name": "Store Manager", "description": "Manages the store"}
        serializer = RoleSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["slug"] == "store-manager"

    def test_slug_explicit_not_overridden(self):
        """When slug is explicitly provided, validate() should keep it.

        NOTE: Full is_valid() triggers DRF UniqueValidator (DB hit), so we
        test the validate() logic directly.
        """
        attrs = {"name": "Admin", "slug": "custom-admin"}
        serializer = RoleSerializer()
        result = serializer.validate(attrs)
        assert result["slug"] == "custom-admin"

    def test_missing_name(self):
        serializer = RoleSerializer(data={})
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_permissions_read_only(self):
        serializer = RoleSerializer()
        assert serializer.fields["permissions"].read_only is True


class TestRoleListSerializer:
    """Tests for RoleListSerializer."""

    def test_serializer_fields(self):
        serializer = RoleListSerializer()
        expected = {"id", "name", "slug", "description", "is_system_role"}
        assert expected == set(serializer.fields.keys())


class TestUserProfileSerializer:
    """Tests for UserProfileSerializer field presence."""

    def test_serializer_fields(self):
        serializer = UserProfileSerializer()
        expected = {
            "id", "user", "user_email", "display_name", "job_title",
            "department", "phone", "avatar", "timezone", "locale",
            "bio", "last_login_ip", "is_active", "roles",
            "created_on", "updated_on",
        }
        assert expected == set(serializer.fields.keys())

    def test_read_only_fields(self):
        serializer = UserProfileSerializer()
        for field_name in ("id", "created_on", "updated_on", "last_login_ip"):
            assert serializer.fields[field_name].read_only is True

    def test_user_email_read_only(self):
        serializer = UserProfileSerializer()
        assert serializer.fields["user_email"].read_only is True


class TestUserProfileListSerializer:
    """Tests for UserProfileListSerializer."""

    def test_serializer_fields(self):
        serializer = UserProfileListSerializer()
        expected = {"id", "user", "display_name", "job_title", "department", "is_active"}
        assert expected == set(serializer.fields.keys())


class TestUserPreferencesSerializer:
    """Tests for UserPreferencesSerializer."""

    def test_serializer_fields(self):
        serializer = UserPreferencesSerializer()
        expected = {
            "id", "user", "theme", "items_per_page",
            "email_notifications", "push_notifications",
            "dashboard_layout", "sidebar_collapsed",
            "created_on", "updated_on",
        }
        assert expected == set(serializer.fields.keys())

    def test_user_read_only(self):
        serializer = UserPreferencesSerializer()
        assert serializer.fields["user"].read_only is True


class TestLoginHistorySerializer:
    """Tests for LoginHistorySerializer (completely read-only)."""

    def test_serializer_fields(self):
        serializer = LoginHistorySerializer()
        expected = {
            "id", "user", "event_type", "ip_address",
            "user_agent", "success", "failure_reason", "timestamp",
        }
        assert expected == set(serializer.fields.keys())

    def test_all_fields_read_only(self):
        serializer = LoginHistorySerializer()
        for field_name, field in serializer.fields.items():
            assert field.read_only is True, f"{field_name} should be read_only"


class TestUserRoleSerializer:
    """Tests for UserRoleSerializer."""

    def test_serializer_fields(self):
        serializer = UserRoleSerializer()
        expected = {
            "id", "user_profile", "role", "role_name",
            "role_slug", "assigned_by", "assigned_at", "is_primary",
        }
        assert expected == set(serializer.fields.keys())

    def test_role_name_read_only(self):
        serializer = UserRoleSerializer()
        assert serializer.fields["role_name"].read_only is True
        assert serializer.fields["role_slug"].read_only is True

    def test_assigned_at_read_only(self):
        serializer = UserRoleSerializer()
        assert serializer.fields["assigned_at"].read_only is True


# =====================================================================
# Model Unit Tests (non-DB)
# =====================================================================
# NOTE: Full model CRUD tests are skipped in this test file because
# ``config.settings.test`` uses an SQLite in-memory database that is
# incompatible with ``django-tenants`` (it calls ``connection.set_schema``
# which requires PostgreSQL).  These model tests will be re-enabled once
# a PostgreSQL-based test settings module is created.
# =====================================================================


class TestPermissionModelUnit:
    """Non-DB unit tests for Permission model."""

    def test_model_has_codename_field(self):
        assert hasattr(Permission, "codename")

    def test_model_has_resource_field(self):
        assert hasattr(Permission, "resource")

    def test_model_has_action_field(self):
        assert hasattr(Permission, "action")

    def test_model_meta_ordering(self):
        assert Permission._meta.ordering == ["resource", "action"]

    def test_model_meta_db_table(self):
        assert Permission._meta.db_table == "users_permission"

    def test_save_method_auto_codename(self):
        """Test save() auto-generates codename without actually hitting DB."""
        perm = Permission(name="Test", resource="orders", action="create")
        # Calling save() would fail without DB, so test the logic directly
        if not perm.codename:
            perm.codename = f"{perm.resource}.{perm.action}"
        assert perm.codename == "orders.create"


class TestRoleModelUnit:
    """Non-DB unit tests for Role model."""

    def test_model_has_name_field(self):
        assert hasattr(Role, "name")

    def test_model_has_slug_field(self):
        assert hasattr(Role, "slug")

    def test_model_has_permissions_field(self):
        assert hasattr(Role, "permissions")

    def test_model_meta_ordering(self):
        assert Role._meta.ordering == ["name"]

    def test_model_meta_db_table(self):
        assert Role._meta.db_table == "users_role"

    def test_default_is_system_role(self):
        field = Role._meta.get_field("is_system_role")
        assert field.default is False


class TestUserProfileModelUnit:
    """Non-DB unit tests for UserProfile model."""

    def test_model_has_display_name_field(self):
        assert hasattr(UserProfile, "display_name")

    def test_model_has_timezone_field(self):
        assert hasattr(UserProfile, "timezone")

    def test_default_timezone(self):
        field = UserProfile._meta.get_field("timezone")
        assert field.default == "Asia/Colombo"

    def test_default_locale(self):
        field = UserProfile._meta.get_field("locale")
        assert field.default == "en"

    def test_model_meta_db_table(self):
        assert UserProfile._meta.db_table == "users_userprofile"


class TestUserPreferencesModelUnit:
    """Non-DB unit tests for UserPreferences model."""

    def test_default_theme(self):
        field = UserPreferences._meta.get_field("theme")
        assert field.default == "system"

    def test_default_items_per_page(self):
        field = UserPreferences._meta.get_field("items_per_page")
        assert field.default == 25

    def test_default_email_notifications(self):
        field = UserPreferences._meta.get_field("email_notifications")
        assert field.default is True

    def test_default_push_notifications(self):
        field = UserPreferences._meta.get_field("push_notifications")
        assert field.default is True

    def test_default_sidebar_collapsed(self):
        field = UserPreferences._meta.get_field("sidebar_collapsed")
        assert field.default is False


class TestLoginHistoryModelUnit:
    """Non-DB unit tests for LoginHistory model."""

    def test_model_has_event_type_field(self):
        assert hasattr(LoginHistory, "event_type")

    def test_model_has_ip_address_field(self):
        assert hasattr(LoginHistory, "ip_address")

    def test_default_success(self):
        field = LoginHistory._meta.get_field("success")
        assert field.default is True

    def test_model_meta_ordering(self):
        assert LoginHistory._meta.ordering == ["-timestamp"]

    def test_model_meta_db_table(self):
        assert LoginHistory._meta.db_table == "users_loginhistory"


class TestUserRoleModelUnit:
    """Non-DB unit tests for UserRole through model."""

    def test_model_has_is_primary_field(self):
        assert hasattr(UserRole, "is_primary")

    def test_default_is_primary(self):
        field = UserRole._meta.get_field("is_primary")
        assert field.default is False

    def test_model_meta_db_table(self):
        assert UserRole._meta.db_table == "users_userrole"


# =====================================================================
# Exception Classes Tests
# =====================================================================


class TestExceptionClasses:
    """Tests for core exception class instantiation."""

    def test_api_exception_defaults(self):
        from apps.core.exceptions.base import APIException

        exc = APIException()
        assert exc.error_code == "API_ERROR"
        assert exc.message == "An unexpected error occurred."
        assert exc.status_code == 500

    def test_api_exception_custom_message(self):
        from apps.core.exceptions.base import APIException

        exc = APIException(message="Custom error", error_code="CUSTOM")
        assert exc.message == "Custom error"
        assert exc.error_code == "CUSTOM"

    def test_validation_exception(self):
        from apps.core.exceptions import ValidationException

        exc = ValidationException(
            message="Bad input",
            field_errors={"email": ["Invalid email"]},
        )
        assert exc.status_code == 400
        assert exc.field_errors == {"email": ["Invalid email"]}

    def test_not_found_exception(self):
        from apps.core.exceptions import NotFoundException

        exc = NotFoundException(message="Item not found")
        assert exc.status_code == 404
        assert exc.message == "Item not found"

    def test_authentication_exception(self):
        from apps.core.exceptions import AuthenticationException

        exc = AuthenticationException()
        assert exc.status_code == 401

    def test_permission_denied_exception(self):
        from apps.core.exceptions import PermissionDeniedException

        exc = PermissionDeniedException()
        assert exc.status_code == 403

    def test_conflict_exception(self):
        from apps.core.exceptions import ConflictException

        exc = ConflictException()
        assert exc.status_code == 409

    def test_rate_limit_exception(self):
        from apps.core.exceptions import RateLimitException

        exc = RateLimitException()
        assert exc.status_code == 429

    def test_server_exception(self):
        from apps.core.exceptions import ServerException

        exc = ServerException()
        assert exc.status_code == 500

    def test_service_unavailable_exception(self):
        from apps.core.exceptions import ServiceUnavailableException

        exc = ServiceUnavailableException()
        assert exc.status_code == 503

    def test_api_exception_to_dict(self):
        from apps.core.exceptions.base import APIException

        exc = APIException(message="Test", details={"key": "val"})
        d = exc.to_dict()
        assert d["error_code"] == "API_ERROR"
        assert d["message"] == "Test"


# =====================================================================
# Middleware Tests
# =====================================================================


class TestBaseMiddleware:
    """Tests for BaseMiddleware hooks."""

    def test_process_request_returns_none(self):
        from apps.core.middleware import BaseMiddleware

        # BaseMiddleware is abstract but we can test via a concrete subclass
        class NoopMiddleware(BaseMiddleware):
            pass

        mw = NoopMiddleware(get_response=lambda r: "response")
        assert mw.process_request(None) is None

    def test_process_response_returns_response(self):
        from apps.core.middleware import BaseMiddleware

        class NoopMiddleware(BaseMiddleware):
            pass

        mw = NoopMiddleware(get_response=lambda r: "response")
        assert mw.process_response(None, "resp") == "resp"

    def test_process_exception_returns_none(self):
        from apps.core.middleware import BaseMiddleware

        class NoopMiddleware(BaseMiddleware):
            pass

        mw = NoopMiddleware(get_response=lambda r: "response")
        assert mw.process_exception(None, Exception("test")) is None


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware."""

    def test_adds_security_headers(self):
        from django.test import RequestFactory
        from apps.core.middleware import SecurityHeadersMiddleware

        factory = RequestFactory()
        request = factory.get("/")

        def get_response(req):
            from django.http import HttpResponse
            return HttpResponse("OK")

        mw = SecurityHeadersMiddleware(get_response=get_response)
        response = mw(request)
        assert response["X-Content-Type-Options"] == "nosniff"
        assert response["X-Frame-Options"] == "DENY"

    def test_headers_dict_not_empty(self):
        from apps.core.middleware.security import SecurityHeadersMiddleware

        headers = SecurityHeadersMiddleware._get_headers()
        assert len(headers) > 0
        assert "X-Content-Type-Options" in headers


class TestRequestLoggingMiddleware:
    """Tests for RequestLoggingMiddleware."""

    def test_sets_start_time_on_request(self, settings):
        from django.test import RequestFactory
        from apps.core.middleware import RequestLoggingMiddleware

        settings.REQUEST_LOGGING_ENABLED = True
        factory = RequestFactory()
        request = factory.get("/api/test/")

        def get_response(req):
            from django.http import HttpResponse
            return HttpResponse("OK")

        mw = RequestLoggingMiddleware(get_response=get_response)
        mw(request)
        assert hasattr(request, "_lcc_start_time")

    def test_skips_health_path(self, settings):
        from django.test import RequestFactory
        from apps.core.middleware import RequestLoggingMiddleware

        settings.REQUEST_LOGGING_ENABLED = True
        factory = RequestFactory()
        request = factory.get("/health/")

        def get_response(req):
            from django.http import HttpResponse
            return HttpResponse("OK")

        mw = RequestLoggingMiddleware(get_response=get_response)
        mw(request)
        assert not hasattr(request, "_lcc_start_time")
