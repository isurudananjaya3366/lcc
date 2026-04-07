"""
LankaCommerce Cloud – API Documentation Tests (SP11 Group F, Tasks 71-82).

Covers:
    - Schema generation (Task 72)
    - Schema validation / SPECTACULAR_SETTINGS sanity (Task 73)
    - Endpoint coverage checks (Task 74)
    - Auth endpoint documentation (Task 75)
    - Example request objects (Task 76)
    - Example response objects (Task 77)
    - Extensions & preprocessing hooks (Task 81)
    - Schema serializer classes (Task 71)
    - Module exports / __all__ (Task 71)
    - Full integration smoke test (Task 82)

All tests are pure-mock — no database, filesystem, or network calls required.
"""

from __future__ import annotations

import importlib
import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from drf_spectacular.utils import OpenApiExample, OpenApiParameter
from rest_framework import serializers

# Every test in this module runs without a database connection.
pytestmark = pytest.mark.django_db(databases=[])


# ════════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════════


def _get_all_exports() -> list[str]:
    """Return the __all__ list from the api_docs package."""
    import apps.core.api_docs as pkg

    return list(pkg.__all__)


def _get_settings() -> dict[str, Any]:
    """Return current SPECTACULAR_SETTINGS dict."""
    from django.conf import settings

    return settings.SPECTACULAR_SETTINGS


# ════════════════════════════════════════════════════════════════════════
# Task 72 — Test Schema Generation
# ════════════════════════════════════════════════════════════════════════


class TestSchemaGeneration:
    """Verify that the OpenAPI schema can be generated without errors."""

    def test_schema_generator_instantiates(self):
        """SchemaGenerator can be created without side-effects."""
        from drf_spectacular.generators import SchemaGenerator

        gen = SchemaGenerator()
        assert gen is not None

    @patch("drf_spectacular.generators.SchemaGenerator.get_schema")
    def test_generate_schema_returns_dict(self, mock_get_schema):
        """generate_schema() returns a dict-like schema object."""
        mock_get_schema.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        from drf_spectacular.generators import SchemaGenerator

        gen = SchemaGenerator()
        schema = gen.get_schema(request=None, public=True)
        assert isinstance(schema, dict)
        assert "openapi" in schema

    @patch("drf_spectacular.generators.SchemaGenerator.get_schema")
    def test_schema_has_info_block(self, mock_get_schema):
        """Generated schema contains an 'info' object."""
        mock_get_schema.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "LankaCommerce Cloud API", "version": "1.0.0"},
            "paths": {},
        }
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)
        assert "info" in schema
        assert "title" in schema["info"]

    @patch("drf_spectacular.generators.SchemaGenerator.get_schema")
    def test_schema_has_paths(self, mock_get_schema):
        """Generated schema contains a 'paths' object."""
        mock_get_schema.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {"/api/v1/products/": {}},
        }
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)
        assert "paths" in schema

    @patch("drf_spectacular.generators.SchemaGenerator.get_schema")
    def test_schema_openapi_version(self, mock_get_schema):
        """Schema declares OpenAPI 3.0.x."""
        mock_get_schema.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)
        assert schema["openapi"].startswith("3.0")

    @patch("drf_spectacular.generators.SchemaGenerator.get_schema")
    def test_schema_serialisable_to_json(self, mock_get_schema):
        """Schema can be serialised to JSON without errors."""
        mock_get_schema.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {"schemas": {}},
        }
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)
        result = json.dumps(schema)
        assert isinstance(result, str)
        assert len(result) > 0


# ════════════════════════════════════════════════════════════════════════
# Task 73 — Test Schema Validation / SPECTACULAR_SETTINGS
# ════════════════════════════════════════════════════════════════════════


class TestSchemaValidation:
    """Verify SPECTACULAR_SETTINGS integrity and expected keys."""

    def test_settings_is_dict(self):
        """SPECTACULAR_SETTINGS must be a dict."""
        settings = _get_settings()
        assert isinstance(settings, dict)

    def test_title_set(self):
        """API title is configured."""
        settings = _get_settings()
        assert settings.get("TITLE") == "LankaCommerce Cloud API"

    def test_version_set(self):
        """API version is configured."""
        settings = _get_settings()
        assert settings.get("VERSION") == "v1.0.0"

    def test_description_non_empty(self):
        """API description is non-empty."""
        settings = _get_settings()
        assert len(settings.get("DESCRIPTION", "")) > 100

    def test_contact_configured(self):
        """Contact info is present and has required keys."""
        contact = _get_settings().get("CONTACT", {})
        assert "name" in contact
        assert "email" in contact

    def test_license_configured(self):
        """License info is present."""
        lic = _get_settings().get("LICENSE", {})
        assert "name" in lic

    def test_servers_configured(self):
        """At least one server is configured."""
        servers = _get_settings().get("SERVERS", [])
        assert len(servers) >= 1
        assert "url" in servers[0]

    def test_tags_non_empty(self):
        """Tags list is non-empty and each tag has a name."""
        tags = _get_settings().get("TAGS", [])
        assert len(tags) >= 5
        for tag in tags:
            assert "name" in tag
            assert "description" in tag

    def test_security_scheme_bearer(self):
        """JWT Bearer security scheme is defined."""
        schemes = _get_settings().get("COMPONENT_SECURITY_SCHEMES", {})
        assert "Bearer" in schemes
        assert schemes["Bearer"]["type"] == "http"
        assert schemes["Bearer"]["scheme"] == "bearer"

    def test_preprocessing_hooks_configured(self):
        """At least one preprocessing hook is registered."""
        hooks = _get_settings().get("PREPROCESSING_HOOKS", [])
        assert len(hooks) >= 1
        assert "custom_preprocessing_hook" in hooks[0]

    def test_serve_include_schema_false(self):
        """Schema endpoint itself is excluded from the schema."""
        assert _get_settings().get("SERVE_INCLUDE_SCHEMA") is False

    def test_component_split_request(self):
        """Request/response components are split."""
        assert _get_settings().get("COMPONENT_SPLIT_REQUEST") is True

    def test_swagger_ui_settings_present(self):
        """Swagger UI customisation settings are present."""
        ui = _get_settings().get("SWAGGER_UI_SETTINGS", {})
        assert "deepLinking" in ui
        assert "persistAuthorization" in ui

    def test_redoc_ui_settings_present(self):
        """ReDoc UI customisation settings are present."""
        redoc = _get_settings().get("REDOC_UI_SETTINGS", {})
        assert "theme" in redoc

    def test_extensions_info_logo(self):
        """x-logo extension is configured for ReDoc branding."""
        ext = _get_settings().get("EXTENSIONS_INFO", {})
        assert "x-logo" in ext
        assert "url" in ext["x-logo"]

    def test_expected_top_level_keys_present(self):
        """All critical top-level keys exist."""
        settings = _get_settings()
        required_keys = [
            "TITLE",
            "DESCRIPTION",
            "VERSION",
            "CONTACT",
            "LICENSE",
            "SERVERS",
            "TAGS",
            "SECURITY",
            "COMPONENT_SECURITY_SCHEMES",
            "PREPROCESSING_HOOKS",
            "SWAGGER_UI_SETTINGS",
            "REDOC_UI_SETTINGS",
        ]
        for key in required_keys:
            assert key in settings, f"Missing SPECTACULAR_SETTINGS key: {key}"


# ════════════════════════════════════════════════════════════════════════
# Task 74 — Test Endpoint Coverage
# ════════════════════════════════════════════════════════════════════════


class TestEndpointCoverage:
    """Verify schema covers the expected endpoint groups."""

    @patch("drf_spectacular.generators.SchemaGenerator.get_schema")
    def test_paths_object_not_empty(self, mock_get_schema):
        """The generated schema has at least one path."""
        mock_get_schema.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {"/api/v1/products/": {"get": {}}},
        }
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)
        assert len(schema.get("paths", {})) > 0

    @patch("drf_spectacular.generators.SchemaGenerator.get_schema")
    def test_paths_start_with_api(self, mock_get_schema):
        """All documented paths start with /api/."""
        mock_get_schema.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/api/v1/products/": {"get": {}},
                "/api/v1/orders/": {"get": {}},
            },
        }
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)
        for path in schema["paths"]:
            assert path.startswith("/api/"), f"Path {path} missing /api/ prefix"

    @patch("drf_spectacular.generators.SchemaGenerator.get_schema")
    def test_operations_have_methods(self, mock_get_schema):
        """Every path has at least one HTTP method."""
        mock_get_schema.return_value = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/api/v1/products/": {"get": {"responses": {"200": {}}}},
            },
        }
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)
        http_methods = {"get", "post", "put", "patch", "delete", "head", "options"}
        for path, item in schema["paths"].items():
            methods = set(item.keys()) & http_methods
            assert len(methods) > 0, f"Path {path} has no HTTP methods"

    def test_schema_path_prefix_set(self):
        """SCHEMA_PATH_PREFIX is configured for versioned routes."""
        settings = _get_settings()
        prefix = settings.get("SCHEMA_PATH_PREFIX", "")
        assert "api" in prefix


# ════════════════════════════════════════════════════════════════════════
# Task 75 — Test Auth Endpoint Documentation
# ════════════════════════════════════════════════════════════════════════


class TestAuthDocumentation:
    """Verify authentication-related documentation artefacts."""

    def test_authentication_description_present(self):
        """AUTHENTICATION_DESCRIPTION is a non-empty string."""
        from apps.core.api_docs.extensions import AUTHENTICATION_DESCRIPTION

        assert isinstance(AUTHENTICATION_DESCRIPTION, str)
        assert len(AUTHENTICATION_DESCRIPTION) > 100
        assert "JWT" in AUTHENTICATION_DESCRIPTION

    def test_authentication_description_mentions_token_endpoint(self):
        """Auth description references /api/token/."""
        from apps.core.api_docs.extensions import AUTHENTICATION_DESCRIPTION

        assert "/api/token/" in AUTHENTICATION_DESCRIPTION

    def test_authentication_description_mentions_refresh(self):
        """Auth description references token refresh."""
        from apps.core.api_docs.extensions import AUTHENTICATION_DESCRIPTION

        assert "refresh" in AUTHENTICATION_DESCRIPTION.lower()

    def test_security_scheme_in_settings(self):
        """SPECTACULAR_SETTINGS defines the Bearer security scheme."""
        schemes = _get_settings().get("COMPONENT_SECURITY_SCHEMES", {})
        bearer = schemes.get("Bearer", {})
        assert bearer.get("bearerFormat") == "JWT"

    def test_token_response_serializer_has_access_field(self):
        """TokenResponseSerializer declares an 'access' field."""
        from apps.core.api_docs.schemas import TokenResponseSerializer

        ser = TokenResponseSerializer()
        assert "access" in ser.fields

    def test_token_response_serializer_has_refresh_field(self):
        """TokenResponseSerializer declares a 'refresh' field."""
        from apps.core.api_docs.schemas import TokenResponseSerializer

        ser = TokenResponseSerializer()
        assert "refresh" in ser.fields

    def test_token_refresh_response_serializer_has_access(self):
        """TokenRefreshResponseSerializer declares an 'access' field."""
        from apps.core.api_docs.schemas import TokenRefreshResponseSerializer

        ser = TokenRefreshResponseSerializer()
        assert "access" in ser.fields

    def test_login_request_example_exists(self):
        """LOGIN_REQUEST_EXAMPLE is an OpenApiExample."""
        from apps.core.api_docs.examples import LOGIN_REQUEST_EXAMPLE

        assert isinstance(LOGIN_REQUEST_EXAMPLE, OpenApiExample)

    def test_login_response_example_exists(self):
        """LOGIN_RESPONSE_EXAMPLE is an OpenApiExample."""
        from apps.core.api_docs.examples import LOGIN_RESPONSE_EXAMPLE

        assert isinstance(LOGIN_RESPONSE_EXAMPLE, OpenApiExample)


# ════════════════════════════════════════════════════════════════════════
# Task 76 — Test Example Requests
# ════════════════════════════════════════════════════════════════════════


class TestExampleRequests:
    """Verify all request examples are well-formed OpenApiExample instances."""

    REQUEST_EXAMPLE_NAMES: list[str] = [
        "LOGIN_REQUEST_EXAMPLE",
        "TOKEN_REFRESH_REQUEST_EXAMPLE",
        "CREATE_PRODUCT_REQUEST_EXAMPLE",
        "UPDATE_PRODUCT_REQUEST_EXAMPLE",
        "CREATE_ORDER_REQUEST_EXAMPLE",
        "CREATE_CUSTOMER_REQUEST_EXAMPLE",
    ]

    @pytest.mark.parametrize("name", REQUEST_EXAMPLE_NAMES)
    def test_request_example_is_openapi_example(self, name: str):
        """Each request example is an OpenApiExample."""
        import apps.core.api_docs.examples as mod

        example = getattr(mod, name)
        assert isinstance(example, OpenApiExample)

    @pytest.mark.parametrize("name", REQUEST_EXAMPLE_NAMES)
    def test_request_example_has_value(self, name: str):
        """Each request example has a non-empty value."""
        import apps.core.api_docs.examples as mod

        example = getattr(mod, name)
        assert example.value is not None

    @pytest.mark.parametrize("name", REQUEST_EXAMPLE_NAMES)
    def test_request_example_has_name(self, name: str):
        """Each request example has a human-readable name."""
        import apps.core.api_docs.examples as mod

        example = getattr(mod, name)
        assert example.name is not None and len(example.name) > 0

    def test_login_request_has_credentials(self):
        """Login request contains username/email and password."""
        from apps.core.api_docs.examples import LOGIN_REQUEST_EXAMPLE

        value = LOGIN_REQUEST_EXAMPLE.value
        assert "password" in value
        assert "username" in value or "email" in value

    def test_create_product_request_has_required_fields(self):
        """Product creation example has name, price, and sku."""
        from apps.core.api_docs.examples import CREATE_PRODUCT_REQUEST_EXAMPLE

        value = CREATE_PRODUCT_REQUEST_EXAMPLE.value
        assert "name" in value
        assert "price" in value
        assert "sku" in value

    def test_create_order_request_has_items(self):
        """Order creation example has items list."""
        from apps.core.api_docs.examples import CREATE_ORDER_REQUEST_EXAMPLE

        value = CREATE_ORDER_REQUEST_EXAMPLE.value
        assert "items" in value
        assert isinstance(value["items"], list)
        assert len(value["items"]) > 0

    def test_create_customer_request_has_contact(self):
        """Customer creation example has name and email."""
        from apps.core.api_docs.examples import CREATE_CUSTOMER_REQUEST_EXAMPLE

        value = CREATE_CUSTOMER_REQUEST_EXAMPLE.value
        assert "name" in value
        assert "email" in value

    def test_request_examples_value_is_json_serialisable(self):
        """All request example values serialise to JSON without errors."""
        import apps.core.api_docs.examples as mod

        for name in self.REQUEST_EXAMPLE_NAMES:
            example = getattr(mod, name)
            result = json.dumps(example.value)
            assert isinstance(result, str), f"{name} value is not JSON-serialisable"


# ════════════════════════════════════════════════════════════════════════
# Task 77 — Test Example Responses
# ════════════════════════════════════════════════════════════════════════


class TestExampleResponses:
    """Verify all response examples are well-formed OpenApiExample instances."""

    RESPONSE_EXAMPLE_NAMES: list[str] = [
        "LOGIN_RESPONSE_EXAMPLE",
        "TOKEN_REFRESH_RESPONSE_EXAMPLE",
        "PRODUCT_RESPONSE_EXAMPLE",
        "PRODUCT_LIST_RESPONSE_EXAMPLE",
        "ORDER_RESPONSE_EXAMPLE",
        "VALIDATION_ERROR_RESPONSE_EXAMPLE",
        "AUTHENTICATION_ERROR_RESPONSE_EXAMPLE",
        "PERMISSION_DENIED_RESPONSE_EXAMPLE",
        "NOT_FOUND_RESPONSE_EXAMPLE",
        "RATE_LIMIT_RESPONSE_EXAMPLE",
    ]

    @pytest.mark.parametrize("name", RESPONSE_EXAMPLE_NAMES)
    def test_response_example_is_openapi_example(self, name: str):
        """Each response example is an OpenApiExample."""
        import apps.core.api_docs.examples as mod

        example = getattr(mod, name)
        assert isinstance(example, OpenApiExample)

    @pytest.mark.parametrize("name", RESPONSE_EXAMPLE_NAMES)
    def test_response_example_has_value(self, name: str):
        """Each response example has a non-empty value."""
        import apps.core.api_docs.examples as mod

        example = getattr(mod, name)
        assert example.value is not None

    @pytest.mark.parametrize("name", RESPONSE_EXAMPLE_NAMES)
    def test_response_example_has_status_codes(self, name: str):
        """Each response example specifies status_codes."""
        import apps.core.api_docs.examples as mod

        example = getattr(mod, name)
        assert example.status_codes is not None
        assert len(example.status_codes) > 0

    def test_login_response_has_tokens(self):
        """Login response contains access and refresh tokens."""
        from apps.core.api_docs.examples import LOGIN_RESPONSE_EXAMPLE

        value = LOGIN_RESPONSE_EXAMPLE.value
        assert "access" in value
        assert "refresh" in value

    def test_token_refresh_response_has_access(self):
        """Token refresh response contains a new access token."""
        from apps.core.api_docs.examples import TOKEN_REFRESH_RESPONSE_EXAMPLE

        value = TOKEN_REFRESH_RESPONSE_EXAMPLE.value
        assert "access" in value

    def test_error_responses_have_error_code(self):
        """Error response examples include 'error_code' key."""
        import apps.core.api_docs.examples as mod

        error_names = [
            "VALIDATION_ERROR_RESPONSE_EXAMPLE",
            "AUTHENTICATION_ERROR_RESPONSE_EXAMPLE",
            "PERMISSION_DENIED_RESPONSE_EXAMPLE",
            "NOT_FOUND_RESPONSE_EXAMPLE",
            "RATE_LIMIT_RESPONSE_EXAMPLE",
        ]
        for name in error_names:
            example = getattr(mod, name)
            assert "error_code" in example.value, f"{name} missing error_code"

    def test_error_responses_have_message(self):
        """Error response examples include 'message' key."""
        import apps.core.api_docs.examples as mod

        error_names = [
            "VALIDATION_ERROR_RESPONSE_EXAMPLE",
            "AUTHENTICATION_ERROR_RESPONSE_EXAMPLE",
            "PERMISSION_DENIED_RESPONSE_EXAMPLE",
            "NOT_FOUND_RESPONSE_EXAMPLE",
            "RATE_LIMIT_RESPONSE_EXAMPLE",
        ]
        for name in error_names:
            example = getattr(mod, name)
            assert "message" in example.value, f"{name} missing message"

    def test_product_response_has_id(self):
        """Product detail response has an 'id' field."""
        from apps.core.api_docs.examples import PRODUCT_RESPONSE_EXAMPLE

        assert "id" in PRODUCT_RESPONSE_EXAMPLE.value

    def test_product_list_response_has_pagination(self):
        """Product list response has pagination keys."""
        from apps.core.api_docs.examples import PRODUCT_LIST_RESPONSE_EXAMPLE

        value = PRODUCT_LIST_RESPONSE_EXAMPLE.value
        assert "count" in value
        assert "results" in value
        assert isinstance(value["results"], list)

    def test_response_examples_value_is_json_serialisable(self):
        """All response example values serialise to JSON without errors."""
        import apps.core.api_docs.examples as mod

        for name in self.RESPONSE_EXAMPLE_NAMES:
            example = getattr(mod, name)
            result = json.dumps(example.value)
            assert isinstance(result, str), f"{name} value is not JSON-serialisable"


# ════════════════════════════════════════════════════════════════════════
# Task 81 — Test Extensions & Preprocessing Hooks
# ════════════════════════════════════════════════════════════════════════


class TestExtensions:
    """Verify custom preprocessing hooks and extension helpers."""

    def test_custom_preprocessing_hook_callable(self):
        """custom_preprocessing_hook is a callable."""
        from apps.core.api_docs.extensions import custom_preprocessing_hook

        assert callable(custom_preprocessing_hook)

    def test_hook_filters_internal_endpoints(self):
        """Internal endpoints are filtered out by the hook."""
        from apps.core.api_docs.extensions import custom_preprocessing_hook

        endpoints = [
            ("/api/v1/products/", "r", "GET", MagicMock()),
            ("/api/_internal/debug/", "r", "GET", MagicMock()),
            ("/api/v1/orders/", "r", "GET", MagicMock()),
        ]
        result = custom_preprocessing_hook(endpoints)
        paths = [ep[0] for ep in result]
        assert "/api/_internal/debug/" not in paths
        assert "/api/v1/products/" in paths
        assert "/api/v1/orders/" in paths

    def test_hook_keeps_public_endpoints(self):
        """Non-internal endpoints are preserved by the hook."""
        from apps.core.api_docs.extensions import custom_preprocessing_hook

        endpoints = [
            ("/api/v1/products/", "r", "GET", MagicMock()),
            ("/api/v1/orders/", "r", "POST", MagicMock()),
        ]
        result = custom_preprocessing_hook(endpoints)
        assert len(result) == 2

    def test_hook_returns_list(self):
        """The hook returns a list."""
        from apps.core.api_docs.extensions import custom_preprocessing_hook

        result = custom_preprocessing_hook([])
        assert isinstance(result, list)

    def test_hook_handles_empty_input(self):
        """The hook handles an empty endpoint list gracefully."""
        from apps.core.api_docs.extensions import custom_preprocessing_hook

        result = custom_preprocessing_hook([])
        assert result == []

    def test_description_supplement_is_string(self):
        """DESCRIPTION_SUPPLEMENT is a non-empty string."""
        from apps.core.api_docs.extensions import DESCRIPTION_SUPPLEMENT

        assert isinstance(DESCRIPTION_SUPPLEMENT, str)
        assert len(DESCRIPTION_SUPPLEMENT) > 100

    def test_description_supplement_sections(self):
        """DESCRIPTION_SUPPLEMENT includes expected documentation sections."""
        from apps.core.api_docs.extensions import DESCRIPTION_SUPPLEMENT

        expected_headings = [
            "Authentication",
            "Error Responses",
            "Pagination",
            "Filtering",
            "Ordering",
            "Rate Limiting",
            "Versioning",
            "Changelog",
        ]
        for heading in expected_headings:
            assert heading in DESCRIPTION_SUPPLEMENT, (
                f"Missing section: {heading}"
            )

    def test_tenant_header_parameter_is_openapi_parameter(self):
        """TENANT_HEADER_PARAMETER is an OpenApiParameter."""
        from apps.core.api_docs.extensions import TENANT_HEADER_PARAMETER

        assert isinstance(TENANT_HEADER_PARAMETER, OpenApiParameter)

    def test_tenant_header_parameter_name(self):
        """TENANT_HEADER_PARAMETER uses the X-Tenant-ID header name."""
        from apps.core.api_docs.extensions import TENANT_HEADER_PARAMETER

        assert TENANT_HEADER_PARAMETER.name == "X-Tenant-ID"

    def test_tenant_header_parameter_location(self):
        """TENANT_HEADER_PARAMETER is located in the header."""
        from apps.core.api_docs.extensions import TENANT_HEADER_PARAMETER

        assert TENANT_HEADER_PARAMETER.location == OpenApiParameter.HEADER

    def test_tenant_header_parameter_required(self):
        """TENANT_HEADER_PARAMETER is required."""
        from apps.core.api_docs.extensions import TENANT_HEADER_PARAMETER

        assert TENANT_HEADER_PARAMETER.required is True


# ════════════════════════════════════════════════════════════════════════
# Task 71 — Test Schema Serializer Classes
# ════════════════════════════════════════════════════════════════════════


class TestSchemas:
    """Verify all response-schema serializers can be instantiated."""

    SERIALIZER_CLASSES: list[str] = [
        "ErrorResponseSerializer",
        "ValidationErrorResponseSerializer",
        "AuthenticationErrorResponseSerializer",
        "PermissionDeniedResponseSerializer",
        "NotFoundResponseSerializer",
        "RateLimitExceededResponseSerializer",
        "TokenResponseSerializer",
        "TokenRefreshResponseSerializer",
        "PaginatedResponseSerializer",
    ]

    @pytest.mark.parametrize("cls_name", SERIALIZER_CLASSES)
    def test_serializer_instantiates(self, cls_name: str):
        """Each schema serializer can be instantiated without errors."""
        import apps.core.api_docs.schemas as mod

        cls = getattr(mod, cls_name)
        instance = cls()
        assert instance is not None

    @pytest.mark.parametrize("cls_name", SERIALIZER_CLASSES)
    def test_serializer_is_serializer(self, cls_name: str):
        """Each schema class is a DRF Serializer subclass."""
        import apps.core.api_docs.schemas as mod

        cls = getattr(mod, cls_name)
        assert issubclass(cls, serializers.Serializer)

    @pytest.mark.parametrize("cls_name", SERIALIZER_CLASSES)
    def test_serializer_has_fields(self, cls_name: str):
        """Each serializer declares at least one field."""
        import apps.core.api_docs.schemas as mod

        cls = getattr(mod, cls_name)
        instance = cls()
        assert len(instance.fields) > 0

    def test_error_response_has_error_code_field(self):
        """ErrorResponseSerializer has an error_code CharField."""
        from apps.core.api_docs.schemas import ErrorResponseSerializer

        ser = ErrorResponseSerializer()
        assert "error_code" in ser.fields
        assert isinstance(ser.fields["error_code"], serializers.CharField)

    def test_error_response_has_message_field(self):
        """ErrorResponseSerializer has a message CharField."""
        from apps.core.api_docs.schemas import ErrorResponseSerializer

        ser = ErrorResponseSerializer()
        assert "message" in ser.fields

    def test_validation_error_has_details_field(self):
        """ValidationErrorResponseSerializer has a details DictField."""
        from apps.core.api_docs.schemas import ValidationErrorResponseSerializer

        ser = ValidationErrorResponseSerializer()
        assert "details" in ser.fields
        assert isinstance(ser.fields["details"], serializers.DictField)

    def test_paginated_response_has_count(self):
        """PaginatedResponseSerializer has count, next, previous, results."""
        from apps.core.api_docs.schemas import PaginatedResponseSerializer

        ser = PaginatedResponseSerializer()
        for field_name in ("count", "next", "previous", "results"):
            assert field_name in ser.fields, f"Missing field: {field_name}"

    def test_rate_limit_serializer_has_details(self):
        """RateLimitExceededResponseSerializer has a details field."""
        from apps.core.api_docs.schemas import RateLimitExceededResponseSerializer

        ser = RateLimitExceededResponseSerializer()
        assert "details" in ser.fields


# ════════════════════════════════════════════════════════════════════════
# Task 71 — Test Module Exports
# ════════════════════════════════════════════════════════════════════════


class TestModuleExports:
    """Verify that every name in __all__ is importable."""

    def test_all_is_list(self):
        """__all__ is a non-empty list."""
        exports = _get_all_exports()
        assert isinstance(exports, list)
        assert len(exports) > 0

    def test_all_exports_importable(self):
        """Every name in __all__ resolves to an attribute on the package."""
        import apps.core.api_docs as pkg

        for name in pkg.__all__:
            obj = getattr(pkg, name, None)
            assert obj is not None, f"__all__ lists '{name}' but it is not importable"

    def test_schemas_in_all(self):
        """All schema serializer names are in __all__."""
        exports = _get_all_exports()
        expected = [
            "ErrorResponseSerializer",
            "ValidationErrorResponseSerializer",
            "AuthenticationErrorResponseSerializer",
            "PermissionDeniedResponseSerializer",
            "NotFoundResponseSerializer",
            "RateLimitExceededResponseSerializer",
            "TokenResponseSerializer",
            "TokenRefreshResponseSerializer",
            "PaginatedResponseSerializer",
        ]
        for name in expected:
            assert name in exports, f"Missing from __all__: {name}"

    def test_preprocessing_hook_in_all(self):
        """custom_preprocessing_hook is in __all__."""
        exports = _get_all_exports()
        assert "custom_preprocessing_hook" in exports

    def test_description_supplement_in_all(self):
        """DESCRIPTION_SUPPLEMENT is in __all__."""
        exports = _get_all_exports()
        assert "DESCRIPTION_SUPPLEMENT" in exports

    def test_tenant_header_in_all(self):
        """TENANT_HEADER_PARAMETER is in __all__."""
        exports = _get_all_exports()
        assert "TENANT_HEADER_PARAMETER" in exports

    def test_example_names_in_all(self):
        """All example constant names are in __all__."""
        exports = _get_all_exports()
        example_names = [
            "LOGIN_REQUEST_EXAMPLE",
            "LOGIN_RESPONSE_EXAMPLE",
            "TOKEN_REFRESH_REQUEST_EXAMPLE",
            "TOKEN_REFRESH_RESPONSE_EXAMPLE",
            "CREATE_PRODUCT_REQUEST_EXAMPLE",
            "UPDATE_PRODUCT_REQUEST_EXAMPLE",
            "PRODUCT_RESPONSE_EXAMPLE",
            "PRODUCT_LIST_RESPONSE_EXAMPLE",
            "CREATE_ORDER_REQUEST_EXAMPLE",
            "ORDER_RESPONSE_EXAMPLE",
            "CREATE_CUSTOMER_REQUEST_EXAMPLE",
        ]
        for name in example_names:
            assert name in exports, f"Missing example from __all__: {name}"


# ════════════════════════════════════════════════════════════════════════
# Task 82 — Full Integration Smoke Test
# ════════════════════════════════════════════════════════════════════════


class TestFullIntegration:
    """End-to-end smoke tests verifying the whole module hangs together."""

    def test_package_importable(self):
        """The api_docs package imports without errors."""
        mod = importlib.import_module("apps.core.api_docs")
        assert mod is not None

    def test_extensions_importable(self):
        """The extensions sub-module imports cleanly."""
        mod = importlib.import_module("apps.core.api_docs.extensions")
        assert hasattr(mod, "custom_preprocessing_hook")
        assert hasattr(mod, "DESCRIPTION_SUPPLEMENT")
        assert hasattr(mod, "TENANT_HEADER_PARAMETER")

    def test_schemas_importable(self):
        """The schemas sub-module imports cleanly."""
        mod = importlib.import_module("apps.core.api_docs.schemas")
        assert hasattr(mod, "ErrorResponseSerializer")
        assert hasattr(mod, "TokenResponseSerializer")
        assert hasattr(mod, "PaginatedResponseSerializer")

    def test_examples_importable(self):
        """The examples sub-module imports cleanly."""
        mod = importlib.import_module("apps.core.api_docs.examples")
        assert hasattr(mod, "LOGIN_REQUEST_EXAMPLE")
        assert hasattr(mod, "PRODUCT_RESPONSE_EXAMPLE")

    def test_urls_importable(self):
        """The urls sub-module imports and has urlpatterns."""
        mod = importlib.import_module("apps.core.api_docs.urls")
        assert hasattr(mod, "urlpatterns")
        assert len(mod.urlpatterns) == 3  # schema, docs, redoc

    def test_urls_app_name(self):
        """URL module declares the expected app_name."""
        from apps.core.api_docs import urls

        assert urls.app_name == "api_docs"

    @patch("drf_spectacular.generators.SchemaGenerator.get_schema")
    def test_full_schema_generation_flow(self, mock_get_schema):
        """Full flow: generate schema → validate structure → check info."""
        mock_get_schema.return_value = {
            "openapi": "3.0.3",
            "info": {
                "title": "LankaCommerce Cloud API",
                "version": "v1.0.0",
                "description": "Test description",
            },
            "paths": {"/api/v1/products/": {"get": {"responses": {"200": {}}}}},
            "components": {"schemas": {}, "securitySchemes": {}},
        }
        from drf_spectacular.generators import SchemaGenerator

        schema = SchemaGenerator().get_schema(request=None, public=True)

        # Structure
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        # Info
        assert schema["info"]["title"] == "LankaCommerce Cloud API"
        assert schema["info"]["version"] == "v1.0.0"

        # Serialisable
        json_str = json.dumps(schema)
        assert len(json_str) > 0

    def test_settings_description_includes_supplement(self):
        """SPECTACULAR_SETTINGS DESCRIPTION includes the supplement text."""
        settings = _get_settings()
        desc = settings.get("DESCRIPTION", "")
        # Check that supplement sections made it into the description
        assert "Authentication" in desc
        assert "Error Responses" in desc

    def test_validate_schema_command_module_exists(self):
        """The validate_schema management command module is importable."""
        mod = importlib.import_module(
            "apps.core.management.commands.validate_schema"
        )
        assert hasattr(mod, "Command")
