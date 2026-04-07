"""
Exception handling utilities for LankaCommerce Cloud core infrastructure.

SubPhase-07, Group-A Tasks 01-14, Group-B Tasks 15-30, Group-C Tasks 31-46, Group-D Tasks 47-60, Group-E Tasks 61-70.

Provides exception handling configuration helpers used by the
core application for documenting exception infrastructure setup.

Functions:
    get_exceptions_module_config()  -- Exceptions module config (Task 01).
    get_exceptions_init_config()    -- Exceptions __init__.py config (Task 02).
    get_base_py_file_config()       -- Base.py file config (Task 03).
    get_api_exception_base_config() -- APIException base class config (Task 04).
    get_error_code_property_config() -- Error code property config (Task 05).
    get_message_property_config()   -- Message property config (Task 06).
    get_details_property_config()   -- Details property config (Task 07).
    get_status_code_property_config() -- Status code property config (Task 08).
    get_error_codes_file_config()   -- Error codes file config (Task 09).
    get_error_code_enum_config()    -- Error code enum config (Task 10).
    get_error_status_mapping_config() -- Error status mapping config (Task 11).
    get_exception_registry_config() -- Exception registry config (Task 12).
    get_base_infrastructure_docs_config() -- Base infrastructure docs config (Task 13).
    get_base_exception_testing_config() -- Base exception testing config (Task 14).
    get_validation_exception_config() -- ValidationException config (Task 15).
    get_authentication_exception_config() -- AuthenticationException config (Task 16).
    get_permission_denied_exception_config() -- PermissionDeniedException config (Task 17).
    get_not_found_exception_config() -- NotFoundException config (Task 18).
    get_conflict_exception_config() -- ConflictException config (Task 19).
    get_rate_limit_exception_config() -- RateLimitException config (Task 20).
    get_server_exception_config() -- ServerException config (Task 21).
    get_service_unavailable_exception_config() -- ServiceUnavailableException config (Task 22).
    get_tenant_not_found_exception_config() -- TenantNotFoundException config (Task 23).
    get_tenant_inactive_exception_config() -- TenantInactiveException config (Task 24).
    get_invalid_token_exception_config() -- InvalidTokenException config (Task 25).
    get_token_expired_exception_config() -- TokenExpiredException config (Task 26).
    get_resource_exists_exception_config() -- ResourceExistsException config (Task 27).
    get_business_rule_exception_config() -- BusinessRuleException config (Task 28).
    get_exception_exports_config() -- Exception exports config (Task 29).
    get_exception_documentation_config() -- Exception documentation config (Task 30).
    get_handlers_file_config() -- Handlers file config (Task 31).
    get_custom_exception_handler_config() -- Custom exception handler config (Task 32).
    get_drf_validation_error_handling_config() -- DRF ValidationError handling config (Task 33).
    get_drf_auth_failed_handling_config() -- DRF AuthenticationFailed handling config (Task 34).
    get_drf_not_authenticated_handling_config() -- DRF NotAuthenticated handling config (Task 35).
    get_drf_permission_denied_handling_config() -- DRF PermissionDenied handling config (Task 36).
    get_drf_not_found_handling_config() -- DRF NotFound handling config (Task 37).
    get_drf_throttled_handling_config() -- DRF Throttled handling config (Task 38).
    get_django_http404_handling_config() -- Django Http404 handling config (Task 39).
    get_custom_api_exception_handling_config() -- Custom APIException handling config (Task 40).
    get_python_exception_handling_config() -- Python exception handling config (Task 41).
    get_request_id_context_config() -- Request ID context config (Task 42).
    get_timestamp_context_config() -- Timestamp context config (Task 43).
    get_handler_registration_config() -- Handler registration config (Task 44).
    get_handler_testing_config() -- Handler testing config (Task 45).
    get_handler_documentation_config() -- Handler documentation config (Task 46).
    get_response_file_config() -- Response file config (Task 47).
    get_error_response_class_config() -- ErrorResponse class config (Task 48).
    get_error_code_field_config() -- Error code field config (Task 49).
    get_message_field_config() -- Message field config (Task 50).
    get_details_field_config() -- Details field config (Task 51).
    get_request_id_field_config() -- Request ID field config (Task 52).
    get_timestamp_field_config() -- Timestamp field config (Task 53).
    get_path_field_config() -- Path field config (Task 54).
    get_validation_error_formatting_config() -- Validation error formatting config (Task 55).
    get_nested_error_flattening_config() -- Nested error flattening config (Task 56).
    get_to_dict_method_config() -- to_dict method config (Task 57).
    get_to_response_method_config() -- to_response method config (Task 58).
    get_response_formatting_testing_config() -- Response formatting testing config (Task 59).
    get_response_format_documentation_config() -- Response format documentation config (Task 60).
    get_error_logging_module_config() -- Error logging module config (Task 61).
    get_log_exception_function_config() -- log_exception function config (Task 62).
    get_request_context_logging_config() -- Request context logging config (Task 63).
    get_user_context_logging_config() -- User context logging config (Task 64).
    get_tenant_context_logging_config() -- Tenant context logging config (Task 65).
    get_stack_trace_logging_config() -- Stack trace logging config (Task 66).
    get_sentry_sdk_install_config() -- Sentry SDK install config (Task 67).
    get_sentry_settings_config() -- Sentry settings config (Task 68).
    get_sentry_dsn_config() -- Sentry DSN config (Task 69).
    get_sentry_sample_rate_config() -- Sentry sample rate config (Task 70).
"""

import logging

logger = logging.getLogger(__name__)


def get_exceptions_module_config() -> dict:
    """Configure exceptions module directory within core Django app. Ref: SP07-T01."""
    logger.debug("Configuring exceptions module directory within core Django app...")
    config: dict = {
        "configured": True,
        "module_structure": [
            "exceptions_directory_created",
            "located_under_apps_core",
            "python_package_structure",
            "ready_for_exception_classes",
            "ready_for_handlers",
            "ready_for_utilities",
        ],
        "planned_files": [
            "base_py_exception_class",
            "error_codes_py_constants",
            "api_exceptions_py_classes",
            "handlers_py_global_handler",
            "response_py_error_formatting",
            "logging_py_error_logging",
        ],
        "integration_points": [
            "importable_from_apps_core",
            "central_export_via_init",
            "used_by_all_api_views",
            "used_by_middleware",
            "used_by_serializers",
            "used_by_test_suite",
        ],
    }
    logger.debug(
        "Exceptions module config: module_structure=%d, planned_files=%d",
        len(config["module_structure"]),
        len(config["planned_files"]),
    )
    return config


def get_exceptions_init_config() -> dict:
    """Configure exceptions __init__.py as central export point. Ref: SP07-T02."""
    logger.debug("Configuring exceptions __init__.py as central export point...")
    config: dict = {
        "configured": True,
        "init_contents": [
            "module_docstring_with_usage",
            "import_placeholder_comments",
            "all_list_for_public_api",
            "version_information_included",
            "clean_import_pattern",
            "no_circular_imports",
        ],
        "export_pattern": [
            "single_import_location",
            "encapsulation_of_internals",
            "flexible_reorganization",
            "discoverable_via_all_list",
            "base_classes_imported_first",
            "derived_classes_after_base",
        ],
        "module_metadata": [
            "version_1_0_0_initial",
            "tracks_breaking_changes",
            "documents_public_api",
            "usage_examples_in_docstring",
            "import_order_documented",
            "valid_python_no_syntax_errors",
        ],
    }
    logger.debug(
        "Exceptions init config: init_contents=%d, export_pattern=%d",
        len(config["init_contents"]),
        len(config["export_pattern"]),
    )
    return config


def get_base_py_file_config() -> dict:
    """Configure base.py file for base exception classes. Ref: SP07-T03."""
    logger.debug("Configuring base.py file for base exception classes...")
    config: dict = {
        "configured": True,
        "file_structure": [
            "base_py_in_exceptions_directory",
            "contains_base_exception_classes",
            "module_docstring_included",
            "typing_imports_added",
            "optional_dict_any_imported",
            "valid_python_no_syntax_errors",
        ],
        "file_contents": [
            "docstring_explains_purpose",
            "imports_from_typing",
            "api_exception_class_defined",
            "class_level_defaults",
            "init_method_with_params",
            "str_and_repr_methods",
        ],
        "import_requirements": [
            "typing_any_imported",
            "typing_dict_imported",
            "typing_optional_imported",
            "no_external_dependencies",
            "standard_library_only",
            "no_circular_imports",
        ],
    }
    logger.debug(
        "Base.py file config: file_structure=%d, file_contents=%d",
        len(config["file_structure"]),
        len(config["file_contents"]),
    )
    return config


def get_api_exception_base_config() -> dict:
    """Configure APIException base class inheriting from Exception. Ref: SP07-T04."""
    logger.debug("Configuring APIException base class inheriting from Exception...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_from_exception",
            "comprehensive_docstring",
            "example_usage_in_docstring",
            "type_hints_on_all_params",
            "json_serializable_properties",
            "consistent_error_formatting",
        ],
        "default_attributes": [
            "default_error_code_api_error",
            "default_message_an_error_occurred",
            "default_status_code_500",
            "fail_safe_server_error",
            "immutable_error_codes",
            "graceful_degradation",
        ],
        "design_principles": [
            "standard_python_exception_handling",
            "default_values_provided",
            "status_500_fail_safe",
            "immutable_codes_after_release",
            "json_serializable_all_props",
            "clean_inheritance_chain",
        ],
    }
    logger.debug(
        "APIException base config: class_design=%d, default_attributes=%d",
        len(config["class_design"]),
        len(config["default_attributes"]),
    )
    return config


def get_error_code_property_config() -> dict:
    """Configure error_code property for unique error identification. Ref: SP07-T05."""
    logger.debug("Configuring error_code property for unique error identification...")
    config: dict = {
        "configured": True,
        "property_definition": [
            "init_param_optional_str",
            "falls_back_to_default",
            "stored_as_instance_attribute",
            "upper_snake_case_format",
            "descriptive_and_unique",
            "used_by_api_consumers",
        ],
        "naming_convention": [
            "validation_prefix_for_input",
            "auth_prefix_for_authentication",
            "permission_prefix_for_authorization",
            "resource_prefix_for_entities",
            "server_prefix_for_internal",
            "rate_limit_prefix_for_throttling",
        ],
        "error_categories": [
            "validation_error_category",
            "authentication_error_category",
            "authorization_error_category",
            "resource_error_category",
            "server_error_category",
            "rate_limit_error_category",
        ],
    }
    logger.debug(
        "Error code property config: property_definition=%d, naming_convention=%d",
        len(config["property_definition"]),
        len(config["naming_convention"]),
    )
    return config


def get_message_property_config() -> dict:
    """Configure message property for human-readable error description. Ref: SP07-T06."""
    logger.debug("Configuring message property for human-readable error description...")
    config: dict = {
        "configured": True,
        "property_definition": [
            "init_param_optional_str",
            "falls_back_to_default_message",
            "passed_to_super_init",
            "stored_as_instance_attribute",
            "clear_and_actionable_text",
            "avoids_technical_jargon",
        ],
        "message_guidelines": [
            "one_to_two_sentences_concise",
            "no_internal_implementation_details",
            "user_friendly_language",
            "includes_context_when_helpful",
            "english_by_default",
            "variables_in_details_not_message",
        ],
        "localization_considerations": [
            "english_default_language",
            "string_literals_not_fstrings",
            "details_dict_for_variables",
            "future_sinhala_support",
            "i18n_ready_structure",
            "no_hardcoded_user_data",
        ],
    }
    logger.debug(
        "Message property config: property_definition=%d, message_guidelines=%d",
        len(config["property_definition"]),
        len(config["message_guidelines"]),
    )
    return config


def get_details_property_config() -> dict:
    """Configure details property for additional error context. Ref: SP07-T07."""
    logger.debug("Configuring details property for additional error context...")
    config: dict = {
        "configured": True,
        "property_definition": [
            "init_param_optional_dict",
            "defaults_to_empty_dict",
            "non_dict_wrapped_in_dict",
            "stored_as_instance_attribute",
            "json_serializable_required",
            "any_additional_context",
        ],
        "use_cases": [
            "field_level_validation_errors",
            "resource_identifiers_context",
            "suggested_actions_for_user",
            "related_error_information",
            "debugging_context_details",
            "request_and_transaction_ids",
        ],
        "serialization_requirements": [
            "strings_numbers_booleans_ok",
            "lists_and_dicts_nested_ok",
            "none_values_allowed",
            "no_objects_or_classes",
            "no_functions_allowed",
            "datetime_to_iso_string",
        ],
    }
    logger.debug(
        "Details property config: property_definition=%d, use_cases=%d",
        len(config["property_definition"]),
        len(config["use_cases"]),
    )
    return config


def get_status_code_property_config() -> dict:
    """Configure status_code property for HTTP response status. Ref: SP07-T08."""
    logger.debug("Configuring status_code property for HTTP response status...")
    config: dict = {
        "configured": True,
        "property_definition": [
            "init_param_optional_int",
            "falls_back_to_default_500",
            "validates_range_100_to_599",
            "invalid_resets_to_500",
            "stored_as_instance_attribute",
            "determines_response_status",
        ],
        "status_categories": [
            "client_errors_400_to_499",
            "server_errors_500_to_599",
            "bad_request_400",
            "unauthorized_401",
            "forbidden_403",
            "not_found_404",
        ],
        "common_status_codes": [
            "conflict_409",
            "too_many_requests_429",
            "internal_server_error_500",
            "service_unavailable_503",
            "str_method_returns_readable",
            "repr_method_returns_developer",
        ],
    }
    logger.debug(
        "Status code property config: property_definition=%d, status_categories=%d",
        len(config["property_definition"]),
        len(config["status_categories"]),
    )
    return config


def get_error_codes_file_config() -> dict:
    """Configure error_codes.py file for standardized error code constants. Ref: SP07-T09."""
    logger.debug("Configuring error_codes.py file for standardized error code constants...")
    config: dict = {
        "configured": True,
        "file_structure": [
            "error_codes_py_in_exceptions",
            "comprehensive_module_docstring",
            "enum_import_included",
            "typing_dict_imported",
            "error_categories_documented",
            "valid_python_no_syntax_errors",
        ],
        "file_contents": [
            "docstring_format_and_categories",
            "from_enum_import_enum",
            "from_typing_import_dict",
            "error_code_category_comments",
            "eight_error_categories_total",
            "ready_for_enum_class",
        ],
        "error_categories": [
            "validation_xxx_400_errors",
            "auth_xxx_401_errors",
            "permission_xxx_403_errors",
            "resource_xxx_404_errors",
            "conflict_xxx_409_errors",
            "rate_limit_xxx_429_errors",
        ],
    }
    logger.debug(
        "Error codes file config: file_structure=%d, file_contents=%d",
        len(config["file_structure"]),
        len(config["file_contents"]),
    )
    return config


def get_error_code_enum_config() -> dict:
    """Configure ErrorCode enum class with all API error codes. Ref: SP07-T10."""
    logger.debug("Configuring ErrorCode enum class with all API error codes...")
    config: dict = {
        "configured": True,
        "enum_design": [
            "inherits_str_and_enum",
            "comprehensive_docstring",
            "type_safe_error_codes",
            "prevents_typo_errors",
            "autocomplete_friendly",
            "string_value_matches_name",
        ],
        "validation_codes": [
            "validation_error_code",
            "validation_failed_code",
            "invalid_input_code",
            "invalid_format_code",
            "required_field_missing_code",
            "invalid_field_value_code",
        ],
        "additional_categories": [
            "auth_codes_six_entries",
            "permission_codes_three_entries",
            "resource_codes_three_entries",
            "conflict_codes_four_entries",
            "server_codes_four_entries",
            "tenant_codes_four_entries",
        ],
    }
    logger.debug(
        "Error code enum config: enum_design=%d, validation_codes=%d",
        len(config["enum_design"]),
        len(config["validation_codes"]),
    )
    return config


def get_error_status_mapping_config() -> dict:
    """Configure ERROR_STATUS_MAP mapping error codes to HTTP status codes. Ref: SP07-T11."""
    logger.debug("Configuring ERROR_STATUS_MAP mapping error codes to HTTP status codes...")
    config: dict = {
        "configured": True,
        "status_mappings": [
            "validation_errors_map_to_400",
            "auth_errors_map_to_401",
            "permission_errors_map_to_403",
            "resource_errors_map_to_404",
            "conflict_errors_map_to_409",
            "rate_limit_errors_map_to_429",
        ],
        "additional_mappings": [
            "server_errors_map_to_500",
            "service_unavailable_map_to_503",
            "tenant_errors_various_codes",
            "business_errors_map_to_400",
            "all_enum_values_mapped",
            "dict_errorcode_int_type",
        ],
        "helper_function": [
            "get_status_code_for_error_defined",
            "accepts_errorcode_param",
            "returns_int_status_code",
            "defaults_to_500_unknown",
            "centralized_status_lookup",
            "used_by_exception_handler",
        ],
    }
    logger.debug(
        "Error status mapping config: status_mappings=%d, additional_mappings=%d",
        len(config["status_mappings"]),
        len(config["additional_mappings"]),
    )
    return config


def get_exception_registry_config() -> dict:
    """Configure exception registry for tracking all exception classes. Ref: SP07-T12."""
    logger.debug("Configuring exception registry for tracking all exception classes...")
    config: dict = {
        "configured": True,
        "registry_components": [
            "exception_registry_dict_created",
            "exception_meta_metaclass_defined",
            "api_exception_uses_metaclass",
            "auto_registration_on_define",
            "skip_base_api_exception",
            "registry_stores_name_to_class",
        ],
        "query_functions": [
            "get_registered_exceptions_defined",
            "get_exception_by_name_defined",
            "list_exception_codes_defined",
            "validate_exceptions_defined",
            "returns_registry_copy",
            "returns_none_if_not_found",
        ],
        "validation_features": [
            "checks_default_error_code",
            "checks_default_message",
            "checks_default_status_code",
            "validates_status_code_range",
            "returns_error_list",
            "empty_list_means_valid",
        ],
    }
    logger.debug(
        "Exception registry config: registry_components=%d, query_functions=%d",
        len(config["registry_components"]),
        len(config["query_functions"]),
    )
    return config


def get_base_infrastructure_docs_config() -> dict:
    """Configure comprehensive documentation for exception infrastructure. Ref: SP07-T13."""
    logger.debug("Configuring comprehensive documentation for exception infrastructure...")
    config: dict = {
        "configured": True,
        "documentation_sections": [
            "overview_and_architecture",
            "api_exception_base_class_docs",
            "error_codes_documentation",
            "custom_exception_guide",
            "best_practices_section",
            "error_response_format",
        ],
        "content_quality": [
            "code_examples_working",
            "usage_examples_provided",
            "configuration_options_listed",
            "troubleshooting_section",
            "api_reference_complete",
            "developer_friendly_format",
        ],
        "documentation_files": [
            "exceptions_md_created",
            "docs_exceptions_directory",
            "doc_header_and_overview",
            "properties_table_included",
            "categories_documented",
            "integration_guide_included",
        ],
    }
    logger.debug(
        "Base infrastructure docs config: documentation_sections=%d, content_quality=%d",
        len(config["documentation_sections"]),
        len(config["content_quality"]),
    )
    return config


def get_base_exception_testing_config() -> dict:
    """Configure comprehensive unit tests for base exception infrastructure. Ref: SP07-T14."""
    logger.debug("Configuring comprehensive unit tests for base exception infrastructure...")
    config: dict = {
        "configured": True,
        "test_classes": [
            "test_api_exception_class",
            "test_error_codes_class",
            "test_exception_registry_class",
            "test_inheritance_class",
            "test_coverage_above_90_percent",
            "tests_directory_created",
        ],
        "api_exception_tests": [
            "test_default_values",
            "test_custom_values",
            "test_invalid_status_code",
            "test_str_representation",
            "test_details_dict_handling",
            "test_details_none_becomes_empty",
        ],
        "registry_tests": [
            "test_get_registered_exceptions",
            "test_get_exception_by_name",
            "test_get_nonexistent_returns_none",
            "test_list_exception_codes",
            "test_validate_exceptions",
            "test_custom_exception_inherits",
        ],
    }
    logger.debug(
        "Base exception testing config: test_classes=%d, api_exception_tests=%d",
        len(config["test_classes"]),
        len(config["api_exception_tests"]),
    )
    return config


def get_validation_exception_config() -> dict:
    """Configure ValidationException for input validation errors. Ref: SP07-T15."""
    logger.debug("Configuring ValidationException for input validation errors...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_api_exception",
            "default_code_validation_error",
            "default_message_validation_failed",
            "default_status_400",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "usage_scenarios": [
            "invalid_form_data",
            "missing_required_fields",
            "invalid_field_formats",
            "type_mismatches",
            "constraint_violations",
            "out_of_range_values",
        ],
        "field_validation": [
            "email_validation_errors",
            "password_too_short",
            "phone_number_format",
            "age_negative_value",
            "required_field_empty",
            "unique_constraint_violation",
        ],
    }
    logger.debug(
        "ValidationException config: class_design=%d, usage_scenarios=%d",
        len(config["class_design"]),
        len(config["usage_scenarios"]),
    )
    return config


def get_authentication_exception_config() -> dict:
    """Configure AuthenticationException for authentication failures. Ref: SP07-T16."""
    logger.debug("Configuring AuthenticationException for authentication failures...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_api_exception",
            "default_code_auth_failed",
            "default_message_auth_failed",
            "default_status_401",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "authentication_scenarios": [
            "invalid_username_password",
            "missing_credentials",
            "login_failures",
            "unverified_email_account",
            "account_locked",
            "session_expired",
        ],
        "credential_handling": [
            "password_not_in_details",
            "username_in_details",
            "attempt_count_tracked",
            "suggestion_message_included",
            "lockout_after_max_attempts",
            "rate_limit_login_endpoint",
        ],
    }
    logger.debug(
        "AuthenticationException config: class_design=%d, authentication_scenarios=%d",
        len(config["class_design"]),
        len(config["authentication_scenarios"]),
    )
    return config


def get_permission_denied_exception_config() -> dict:
    """Configure PermissionDeniedException for authorization failures. Ref: SP07-T17."""
    logger.debug("Configuring PermissionDeniedException for authorization failures...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_api_exception",
            "default_code_permission_denied",
            "default_message_permission_denied",
            "default_status_403",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "permission_scenarios": [
            "insufficient_role_permissions",
            "rbac_violations",
            "resource_ownership_violations",
            "tenant_access_violations",
            "read_only_mode_restrictions",
            "feature_not_available",
        ],
        "access_control": [
            "required_permission_in_details",
            "user_role_in_details",
            "tenant_isolation_enforced",
            "distinct_from_401_status",
            "admin_actions_protected",
            "audit_trail_on_denial",
        ],
    }
    logger.debug(
        "PermissionDeniedException config: class_design=%d, permission_scenarios=%d",
        len(config["class_design"]),
        len(config["permission_scenarios"]),
    )
    return config


def get_not_found_exception_config() -> dict:
    """Configure NotFoundException for resource not found errors. Ref: SP07-T18."""
    logger.debug("Configuring NotFoundException for resource not found errors...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_api_exception",
            "default_code_resource_not_found",
            "default_message_resource_not_found",
            "default_status_404",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "resource_scenarios": [
            "invalid_resource_id",
            "deleted_resources",
            "nonexistent_endpoints",
            "missing_related_resources",
            "wrong_tenant_resource",
            "empty_queryset_result",
        ],
        "security_considerations": [
            "hide_existence_when_unauthorized",
            "return_404_not_403_default",
            "no_internal_details_leaked",
            "resource_type_in_details",
            "suggestion_in_response",
            "consistent_error_format",
        ],
    }
    logger.debug(
        "NotFoundException config: class_design=%d, resource_scenarios=%d",
        len(config["class_design"]),
        len(config["resource_scenarios"]),
    )
    return config


def get_conflict_exception_config() -> dict:
    """Configure ConflictException for state conflict errors. Ref: SP07-T19."""
    logger.debug("Configuring ConflictException for state conflict errors...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_api_exception",
            "default_code_conflict",
            "default_message_conflicts_with_state",
            "default_status_409",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "conflict_scenarios": [
            "duplicate_resource_entries",
            "concurrent_modification",
            "state_transition_violations",
            "version_mismatches",
            "resource_already_in_use",
            "integrity_constraint_violation",
        ],
        "state_management": [
            "current_status_in_details",
            "allowed_statuses_in_details",
            "field_causing_conflict",
            "suggestion_for_resolution",
            "distinct_from_400_and_422",
            "optimistic_locking_support",
        ],
    }
    logger.debug(
        "ConflictException config: class_design=%d, conflict_scenarios=%d",
        len(config["class_design"]),
        len(config["conflict_scenarios"]),
    )
    return config


def get_rate_limit_exception_config() -> dict:
    """Configure RateLimitException for rate limit violations. Ref: SP07-T20."""
    logger.debug("Configuring RateLimitException for rate limit violations...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_api_exception",
            "default_code_rate_limit_exceeded",
            "default_message_rate_limit_exceeded",
            "default_status_429",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "rate_limit_scenarios": [
            "too_many_requests_from_same_ip",
            "api_throttling_violations",
            "burst_limit_exceeded",
            "daily_quota_exceeded",
            "hourly_quota_exceeded",
            "per_endpoint_rate_limit",
        ],
        "retry_handling": [
            "retry_after_seconds_in_details",
            "limit_count_in_details",
            "window_duration_in_details",
            "current_count_in_details",
            "reset_time_in_details",
            "headers_include_rate_limit_info",
        ],
    }
    logger.debug(
        "RateLimitException config: class_design=%d, rate_limit_scenarios=%d",
        len(config["class_design"]),
        len(config["rate_limit_scenarios"]),
    )
    return config


def get_server_exception_config() -> dict:
    """Configure ServerException for internal server errors. Ref: SP07-T21."""
    logger.debug("Configuring ServerException for internal server errors...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_api_exception",
            "default_code_server_error",
            "default_message_unexpected_error",
            "default_status_500",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "server_error_scenarios": [
            "unexpected_runtime_errors",
            "unhandled_exceptions",
            "critical_system_failures",
            "database_connection_errors",
            "external_service_failures",
            "resource_exhaustion",
        ],
        "security_considerations": [
            "generic_message_in_production",
            "full_details_in_logs_only",
            "no_stack_traces_to_client",
            "no_internal_paths_exposed",
            "no_database_queries_exposed",
            "no_credentials_in_response",
        ],
    }
    logger.debug(
        "ServerException config: class_design=%d, server_error_scenarios=%d",
        len(config["class_design"]),
        len(config["server_error_scenarios"]),
    )
    return config


def get_service_unavailable_exception_config() -> dict:
    """Configure ServiceUnavailableException for temporary unavailability. Ref: SP07-T22."""
    logger.debug("Configuring ServiceUnavailableException for temporary unavailability...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_api_exception",
            "default_code_service_unavailable",
            "default_message_temporarily_unavailable",
            "default_status_503",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "unavailable_scenarios": [
            "scheduled_maintenance_mode",
            "system_overload_detected",
            "database_unavailable",
            "external_service_down",
            "circuit_breaker_open",
            "deployment_in_progress",
        ],
        "retry_configuration": [
            "retry_after_header_support",
            "estimated_completion_time",
            "maintenance_window_info",
            "fallback_service_available",
            "status_page_url_in_details",
            "automatic_retry_guidance",
        ],
    }
    logger.debug(
        "ServiceUnavailableException config: class_design=%d, unavailable_scenarios=%d",
        len(config["class_design"]),
        len(config["unavailable_scenarios"]),
    )
    return config


def get_tenant_not_found_exception_config() -> dict:
    """Configure TenantNotFoundException for missing tenants. Ref: SP07-T23."""
    logger.debug("Configuring TenantNotFoundException for missing tenants...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_not_found_exception",
            "default_code_tenant_not_found",
            "default_message_tenant_not_found",
            "default_status_404",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "tenant_lookup_scenarios": [
            "invalid_subdomain_lookup",
            "unknown_custom_domain",
            "deleted_tenant_access",
            "tenant_migration_in_progress",
            "expired_trial_tenant",
            "domain_not_configured",
        ],
        "multi_tenancy_context": [
            "subdomain_based_resolution",
            "custom_domain_mapping",
            "separate_schema_per_tenant",
            "domain_validation_on_request",
            "suggestion_in_error_details",
            "contact_support_guidance",
        ],
    }
    logger.debug(
        "TenantNotFoundException config: class_design=%d, tenant_lookup_scenarios=%d",
        len(config["class_design"]),
        len(config["tenant_lookup_scenarios"]),
    )
    return config


def get_tenant_inactive_exception_config() -> dict:
    """Configure TenantInactiveException for inactive tenants. Ref: SP07-T24."""
    logger.debug("Configuring TenantInactiveException for inactive tenants...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_permission_denied_exception",
            "default_code_tenant_inactive",
            "default_message_tenant_inactive",
            "default_status_403",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "inactive_reasons": [
            "subscription_expired",
            "account_suspended",
            "payment_failure",
            "terms_of_service_violation",
            "manual_admin_deactivation",
            "trial_period_ended",
        ],
        "tenant_states": [
            "active_normal_operation",
            "inactive_subscription_expired",
            "suspended_temporarily_disabled",
            "pending_activation_required",
            "deleted_permanently_removed",
            "migrating_data_transfer",
        ],
    }
    logger.debug(
        "TenantInactiveException config: class_design=%d, inactive_reasons=%d",
        len(config["class_design"]),
        len(config["inactive_reasons"]),
    )
    return config


def get_invalid_token_exception_config() -> dict:
    """Configure InvalidTokenException for JWT validation failures. Ref: SP07-T25."""
    logger.debug("Configuring InvalidTokenException for JWT validation failures...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_authentication_exception",
            "default_code_auth_token_invalid",
            "default_message_invalid_token",
            "default_status_401",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "token_validation_scenarios": [
            "malformed_jwt_format",
            "invalid_signature_verification",
            "token_tampering_detected",
            "wrong_token_type_used",
            "blacklisted_token_access",
            "missing_required_claims",
        ],
        "token_error_details": [
            "reason_field_in_details",
            "expected_type_in_details",
            "received_type_in_details",
            "suggestion_for_resolution",
            "token_refresh_guidance",
            "security_event_logged",
        ],
    }
    logger.debug(
        "InvalidTokenException config: class_design=%d, token_validation_scenarios=%d",
        len(config["class_design"]),
        len(config["token_validation_scenarios"]),
    )
    return config


def get_token_expired_exception_config() -> dict:
    """Configure TokenExpiredException for expired JWT tokens. Ref: SP07-T26."""
    logger.debug("Configuring TokenExpiredException for expired JWT tokens...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_authentication_exception",
            "default_code_auth_token_expired",
            "default_message_token_expired",
            "default_status_401",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "expiration_scenarios": [
            "access_token_expired",
            "refresh_token_expired",
            "session_timeout_reached",
            "idle_timeout_exceeded",
            "absolute_timeout_reached",
            "token_max_age_exceeded",
        ],
        "token_refresh_flow": [
            "client_detects_401_response",
            "sends_refresh_token_request",
            "receives_new_access_token",
            "retries_original_request",
            "refresh_token_rotation",
            "all_tokens_invalidated_on_logout",
        ],
    }
    logger.debug(
        "TokenExpiredException config: class_design=%d, expiration_scenarios=%d",
        len(config["class_design"]),
        len(config["expiration_scenarios"]),
    )
    return config


def get_resource_exists_exception_config() -> dict:
    """Configure ResourceExistsException for duplicate resources. Ref: SP07-T27."""
    logger.debug("Configuring ResourceExistsException for duplicate resources...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_conflict_exception",
            "default_code_resource_already_exists",
            "default_message_resource_exists",
            "default_status_409",
            "comprehensive_docstring",
            "auto_registered_in_registry",
        ],
        "duplicate_scenarios": [
            "unique_constraint_violation",
            "duplicate_resource_creation",
            "resource_already_exists_check",
            "sku_duplication_attempt",
            "email_already_registered",
            "username_already_taken",
        ],
        "conflict_resolution": [
            "existing_resource_id_in_details",
            "conflicting_field_in_details",
            "conflicting_value_in_details",
            "suggestion_use_different_value",
            "suggestion_update_existing",
            "link_to_existing_resource",
        ],
    }
    logger.debug(
        "ResourceExistsException config: class_design=%d, duplicate_scenarios=%d",
        len(config["class_design"]),
        len(config["duplicate_scenarios"]),
    )
    return config


def get_business_rule_exception_config() -> dict:
    """Configure BusinessRuleException for business logic violations. Ref: SP07-T28."""
    logger.debug("Configuring BusinessRuleException for business logic violations...")
    config: dict = {
        "configured": True,
        "class_design": [
            "inherits_api_exception",
            "default_code_business_rule_violation",
            "default_message_business_rule_violation",
            "default_status_400",
            "supports_422_for_semantic_errors",
            "auto_registered_in_registry",
        ],
        "business_rule_scenarios": [
            "insufficient_stock_inventory",
            "invalid_order_state_transition",
            "discount_exceeds_allowed_percentage",
            "payment_amount_mismatch",
            "cannot_delete_user_with_active_orders",
            "cannot_deactivate_product_in_active_orders",
        ],
        "sri_lanka_context": [
            "lkr_currency_validation",
            "delivery_zone_postal_code_check",
            "local_tax_calculation_rules",
            "regional_pricing_constraints",
            "business_registration_requirements",
            "local_compliance_validation",
        ],
    }
    logger.debug(
        "BusinessRuleException config: class_design=%d, business_rule_scenarios=%d",
        len(config["class_design"]),
        len(config["business_rule_scenarios"]),
    )
    return config


def get_exception_exports_config() -> dict:
    """Configure exception module exports for all custom exceptions. Ref: SP07-T29."""
    logger.debug("Configuring exception module exports for all custom exceptions...")
    config: dict = {
        "configured": True,
        "export_structure": [
            "all_exceptions_in_init_py",
            "all_list_with_all_exports",
            "grouped_by_category",
            "client_errors_section",
            "server_errors_section",
            "specialized_exceptions_section",
        ],
        "import_patterns": [
            "individual_import_pattern",
            "group_import_pattern",
            "module_level_import_pattern",
            "from_core_exceptions_import",
            "wildcard_import_supported",
            "consistent_import_style",
        ],
        "module_organization": [
            "base_exception_and_utilities_group",
            "error_codes_group",
            "custom_exception_classes_group",
            "rate_limiting_section",
            "tenant_specific_section",
            "business_logic_section",
        ],
    }
    logger.debug(
        "Exception exports config: export_structure=%d, import_patterns=%d",
        len(config["export_structure"]),
        len(config["import_patterns"]),
    )
    return config


def get_exception_documentation_config() -> dict:
    """Configure exception classes documentation and guidelines. Ref: SP07-T30."""
    logger.debug("Configuring exception classes documentation and guidelines...")
    config: dict = {
        "configured": True,
        "documentation_sections": [
            "exception_catalog_section",
            "usage_examples_per_exception",
            "decision_flowchart_section",
            "best_practices_section",
            "security_considerations_section",
            "quick_reference_table",
        ],
        "best_practices": [
            "choose_specific_over_generic",
            "provide_helpful_details",
            "write_clear_messages",
            "follow_security_guidelines",
            "maintain_consistency",
            "log_details_dont_expose",
        ],
        "quick_reference": [
            "http_400_validation_and_business",
            "http_401_auth_and_token",
            "http_403_permission_and_tenant",
            "http_404_not_found_and_tenant",
            "http_409_conflict_and_resource",
            "http_429_500_503_server_errors",
        ],
    }
    logger.debug(
        "Exception documentation config: documentation_sections=%d, best_practices=%d",
        len(config["documentation_sections"]),
        len(config["best_practices"]),
    )
    return config


def get_handlers_file_config() -> dict:
    """Configure handlers.py file for global exception handling. Ref: SP07-T31."""
    logger.debug("Configuring handlers.py file for global exception handling...")
    config: dict = {
        "configured": True,
        "file_structure": [
            "handlers_py_file_created",
            "located_in_exceptions_directory",
            "file_docstring_added",
            "logger_configured",
            "valid_python_module",
            "ready_for_handler_functions",
        ],
        "imports_required": [
            "logging_and_typing_imports",
            "uuid4_for_request_ids",
            "django_core_exceptions",
            "drf_exceptions_imported",
            "drf_response_and_status",
            "custom_base_and_error_codes",
        ],
        "module_capabilities": [
            "drf_built_in_exception_support",
            "django_exception_conversion",
            "custom_api_exception_handling",
            "unexpected_python_exception_catch",
            "standard_error_response_format",
            "request_context_extraction",
        ],
    }
    logger.debug(
        "Handlers file config: file_structure=%d, imports_required=%d",
        len(config["file_structure"]),
        len(config["imports_required"]),
    )
    return config


def get_custom_exception_handler_config() -> dict:
    """Configure custom_exception_handler function for DRF. Ref: SP07-T32."""
    logger.debug("Configuring custom_exception_handler function for DRF...")
    config: dict = {
        "configured": True,
        "handler_design": [
            "function_signature_exc_context",
            "returns_optional_response",
            "calls_drf_handler_first",
            "transforms_drf_responses",
            "formats_custom_exceptions",
            "catches_unexpected_errors",
        ],
        "helper_functions": [
            "get_request_id_helper",
            "get_request_path_helper",
            "request_id_from_middleware",
            "generates_uuid_if_missing",
            "safe_path_extraction",
            "null_request_handling",
        ],
        "handler_flow": [
            "exception_raised_in_view",
            "drf_default_handler_called",
            "drf_handled_transform_response",
            "api_exception_format_custom",
            "http404_convert_to_not_found",
            "permission_denied_convert_to_403",
        ],
    }
    logger.debug(
        "Custom exception handler config: handler_design=%d, helper_functions=%d",
        len(config["handler_design"]),
        len(config["helper_functions"]),
    )
    return config


def get_drf_validation_error_handling_config() -> dict:
    """Configure DRF ValidationError handling in exception handler. Ref: SP07-T33."""
    logger.debug("Configuring DRF ValidationError handling in exception handler...")
    config: dict = {
        "configured": True,
        "error_mapping": [
            "maps_to_validation_error_code",
            "preserves_drf_status_400",
            "isinstance_check_for_drf_validation",
            "error_code_set_to_validation_error",
            "message_set_to_validation_failed",
            "details_contain_flattened_errors",
        ],
        "validation_flattening": [
            "flatten_nested_dict_errors",
            "dot_notation_for_nested_fields",
            "list_errors_preserved",
            "string_errors_wrapped_in_list",
            "parent_key_tracking",
            "recursive_flattening_support",
        ],
        "response_format": [
            "standard_error_envelope",
            "includes_request_id",
            "includes_timestamp",
            "includes_request_path",
            "error_code_in_response",
            "details_dict_in_response",
        ],
    }
    logger.debug(
        "DRF ValidationError handling config: error_mapping=%d, validation_flattening=%d",
        len(config["error_mapping"]),
        len(config["validation_flattening"]),
    )
    return config


def get_drf_auth_failed_handling_config() -> dict:
    """Configure DRF AuthenticationFailed handling in exception handler. Ref: SP07-T34."""
    logger.debug("Configuring DRF AuthenticationFailed handling in exception handler...")
    config: dict = {
        "configured": True,
        "error_mapping": [
            "maps_to_auth_failed_code",
            "preserves_drf_status_401",
            "isinstance_check_for_auth_failed",
            "error_code_set_to_auth_failed",
            "message_from_exception_or_default",
            "default_message_authentication_failed",
        ],
        "auth_failure_scenarios": [
            "invalid_credentials_provided",
            "expired_authentication_token",
            "malformed_authorization_header",
            "unsupported_auth_scheme",
            "missing_auth_backend",
            "token_blacklisted",
        ],
        "response_format": [
            "standard_error_envelope",
            "includes_request_id",
            "includes_timestamp",
            "includes_request_path",
            "www_authenticate_header",
            "no_sensitive_details_exposed",
        ],
    }
    logger.debug(
        "DRF AuthenticationFailed handling config: error_mapping=%d, auth_failure_scenarios=%d",
        len(config["error_mapping"]),
        len(config["auth_failure_scenarios"]),
    )
    return config


def get_drf_not_authenticated_handling_config() -> dict:
    """Configure DRF NotAuthenticated handling in exception handler. Ref: SP07-T35."""
    logger.debug("Configuring DRF NotAuthenticated handling in exception handler...")
    config: dict = {
        "configured": True,
        "error_mapping": [
            "maps_to_auth_required_code",
            "preserves_drf_status_401",
            "isinstance_check_for_not_authenticated",
            "error_code_set_to_auth_required",
            "message_from_exception_or_default",
            "default_message_auth_required",
        ],
        "not_auth_scenarios": [
            "no_auth_header_provided",
            "anonymous_user_access",
            "session_expired_no_token",
            "auth_header_empty",
            "token_not_provided",
            "cookie_auth_missing",
        ],
        "response_format": [
            "standard_error_envelope",
            "includes_request_id",
            "includes_timestamp",
            "includes_request_path",
            "login_url_suggestion",
            "authentication_methods_hint",
        ],
    }
    logger.debug(
        "DRF NotAuthenticated handling config: error_mapping=%d, not_auth_scenarios=%d",
        len(config["error_mapping"]),
        len(config["not_auth_scenarios"]),
    )
    return config


def get_drf_permission_denied_handling_config() -> dict:
    """Configure DRF PermissionDenied handling in exception handler. Ref: SP07-T36."""
    logger.debug("Configuring DRF PermissionDenied handling in exception handler...")
    config: dict = {
        "configured": True,
        "error_mapping": [
            "maps_to_permission_denied_code",
            "preserves_drf_status_403",
            "isinstance_check_for_permission_denied",
            "error_code_set_to_permission_denied",
            "message_from_exception_or_default",
            "default_message_permission_denied",
        ],
        "permission_scenarios": [
            "user_lacks_required_role",
            "object_level_permission_denied",
            "tenant_level_access_denied",
            "feature_not_available_for_plan",
            "ip_address_restricted",
            "action_not_allowed_for_user",
        ],
        "response_format": [
            "standard_error_envelope",
            "includes_request_id",
            "includes_timestamp",
            "includes_request_path",
            "required_permission_hint",
            "no_sensitive_details_exposed",
        ],
    }
    logger.debug(
        "DRF PermissionDenied handling config: error_mapping=%d, permission_scenarios=%d",
        len(config["error_mapping"]),
        len(config["permission_scenarios"]),
    )
    return config


def get_drf_not_found_handling_config() -> dict:
    """Configure DRF NotFound handling in exception handler. Ref: SP07-T37."""
    logger.debug("Configuring DRF NotFound handling in exception handler...")
    config: dict = {
        "configured": True,
        "error_mapping": [
            "maps_to_resource_not_found_code",
            "preserves_drf_status_404",
            "isinstance_check_for_not_found",
            "error_code_set_to_resource_not_found",
            "message_from_exception_or_default",
            "default_message_resource_not_found",
        ],
        "not_found_scenarios": [
            "url_route_not_matched",
            "object_lookup_failed",
            "filtered_queryset_empty",
            "soft_deleted_resource",
            "tenant_scoped_not_found",
            "nested_resource_missing",
        ],
        "response_format": [
            "standard_error_envelope",
            "includes_request_id",
            "includes_timestamp",
            "includes_request_path",
            "resource_type_in_details",
            "suggestion_check_url",
        ],
    }
    logger.debug(
        "DRF NotFound handling config: error_mapping=%d, not_found_scenarios=%d",
        len(config["error_mapping"]),
        len(config["not_found_scenarios"]),
    )
    return config


def get_drf_throttled_handling_config() -> dict:
    """Configure DRF Throttled handling in exception handler. Ref: SP07-T38."""
    logger.debug("Configuring DRF Throttled handling in exception handler...")
    config: dict = {
        "configured": True,
        "error_mapping": [
            "maps_to_rate_limit_exceeded_code",
            "preserves_drf_status_429",
            "isinstance_check_for_throttled",
            "error_code_set_to_rate_limit_exceeded",
            "message_from_exception_or_default",
            "default_message_rate_limit_exceeded",
        ],
        "throttle_scenarios": [
            "anonymous_rate_limit_exceeded",
            "user_rate_limit_exceeded",
            "burst_rate_limit_exceeded",
            "sustained_rate_limit_exceeded",
            "scope_specific_throttle",
            "custom_throttle_class",
        ],
        "response_format": [
            "standard_error_envelope",
            "includes_request_id",
            "includes_timestamp",
            "includes_request_path",
            "wait_time_in_details",
            "retry_after_in_details",
        ],
    }
    logger.debug(
        "DRF Throttled handling config: error_mapping=%d, throttle_scenarios=%d",
        len(config["error_mapping"]),
        len(config["throttle_scenarios"]),
    )
    return config


def get_django_http404_handling_config() -> dict:
    """Configure Django Http404 exception handling in handler. Ref: SP07-T39."""
    logger.debug("Configuring Django Http404 exception handling in handler...")
    config: dict = {
        "configured": True,
        "error_mapping": [
            "maps_to_resource_not_found_code",
            "converts_to_status_404",
            "isinstance_check_for_http404",
            "standard_error_envelope_format",
            "includes_request_id_and_timestamp",
            "includes_request_path",
        ],
        "http404_scenarios": [
            "url_pattern_not_matched",
            "model_get_object_or_404",
            "view_dispatch_not_found",
            "static_file_not_found",
            "api_endpoint_not_registered",
            "nested_url_resolution_failure",
        ],
        "django_conversion": [
            "django_exception_to_drf_response",
            "permission_denied_to_403_response",
            "http404_to_not_found_response",
            "consistent_with_drf_format",
            "no_html_error_pages",
            "json_response_always",
        ],
    }
    logger.debug(
        "Django Http404 handling config: error_mapping=%d, http404_scenarios=%d",
        len(config["error_mapping"]),
        len(config["http404_scenarios"]),
    )
    return config


def get_custom_api_exception_handling_config() -> dict:
    """Configure custom APIException handling in handler. Ref: SP07-T40."""
    logger.debug("Configuring custom APIException handling in handler...")
    config: dict = {
        "configured": True,
        "error_mapping": [
            "uses_exception_error_code_property",
            "uses_exception_message_property",
            "uses_exception_details_property",
            "uses_exception_status_code",
            "standard_error_envelope_format",
            "includes_request_context",
        ],
        "exception_properties": [
            "error_code_from_exception_class",
            "message_from_exception_instance",
            "details_dict_from_exception",
            "status_code_determines_response",
            "supports_all_custom_exceptions",
            "preserves_exception_hierarchy",
        ],
        "logging_strategy": [
            "server_errors_logged_as_error",
            "client_errors_logged_as_warning",
            "exc_info_for_500_errors",
            "request_id_in_log_extra",
            "error_code_in_log_extra",
            "status_code_in_log_extra",
        ],
    }
    logger.debug(
        "Custom APIException handling config: error_mapping=%d, exception_properties=%d",
        len(config["error_mapping"]),
        len(config["exception_properties"]),
    )
    return config


def get_python_exception_handling_config() -> dict:
    """Configure unexpected Python exception handling in handler. Ref: SP07-T41."""
    logger.debug("Configuring unexpected Python exception handling in handler...")
    config: dict = {
        "configured": True,
        "error_mapping": [
            "maps_to_server_error_code",
            "converts_to_status_500",
            "generic_message_for_client",
            "full_details_logged_internally",
            "exception_type_in_logs",
            "exception_message_in_logs",
        ],
        "unexpected_scenarios": [
            "unhandled_runtime_error",
            "database_integrity_error",
            "third_party_library_error",
            "os_level_error",
            "memory_allocation_failure",
            "network_timeout_error",
        ],
        "debug_mode_handling": [
            "debug_mode_includes_exception_type",
            "debug_mode_includes_exception_message",
            "production_mode_generic_message",
            "settings_debug_flag_checked",
            "no_stack_traces_in_production",
            "detailed_logging_in_all_modes",
        ],
    }
    logger.debug(
        "Python exception handling config: error_mapping=%d, unexpected_scenarios=%d",
        len(config["error_mapping"]),
        len(config["unexpected_scenarios"]),
    )
    return config


def get_request_id_context_config() -> dict:
    """Configure request ID context for error responses. Ref: SP07-T42."""
    logger.debug("Configuring request ID context for error responses...")
    config: dict = {
        "configured": True,
        "request_id_sources": [
            "middleware_request_attribute",
            "x_request_id_header",
            "uuid4_fallback_generation",
            "correlation_id_propagation",
            "thread_local_storage",
            "request_meta_lookup",
        ],
        "id_format": [
            "uuid4_standard_format",
            "hyphenated_string_representation",
            "lowercase_hex_digits",
            "fixed_36_character_length",
            "unique_per_request",
            "traceable_across_services",
        ],
        "context_usage": [
            "included_in_error_response",
            "added_to_log_extra_dict",
            "passed_to_downstream_services",
            "returned_in_response_headers",
            "stored_for_audit_trail",
            "used_for_request_correlation",
        ],
    }
    logger.debug(
        "Request ID context config: request_id_sources=%d, id_format=%d",
        len(config["request_id_sources"]),
        len(config["id_format"]),
    )
    return config


def get_timestamp_context_config() -> dict:
    """Configure timestamp context for error responses. Ref: SP07-T43."""
    logger.debug("Configuring timestamp context for error responses...")
    config: dict = {
        "configured": True,
        "timestamp_format": [
            "iso8601_format_string",
            "utc_timezone_always",
            "z_suffix_for_utc",
            "microsecond_precision",
            "datetime_utcnow_usage",
            "consistent_across_responses",
        ],
        "timezone_handling": [
            "utc_as_canonical_timezone",
            "no_local_timezone_conversion",
            "timezone_aware_datetime",
            "consistent_with_api_convention",
            "matches_audit_log_format",
            "parseable_by_javascript",
        ],
        "context_usage": [
            "included_in_error_response",
            "matches_created_at_fields",
            "added_to_log_records",
            "used_for_error_ordering",
            "supports_error_analysis",
            "consistent_with_success_responses",
        ],
    }
    logger.debug(
        "Timestamp context config: timestamp_format=%d, timezone_handling=%d",
        len(config["timestamp_format"]),
        len(config["timezone_handling"]),
    )
    return config


def get_handler_registration_config() -> dict:
    """Configure handler registration in DRF settings. Ref: SP07-T44."""
    logger.debug("Configuring handler registration in DRF settings...")
    config: dict = {
        "configured": True,
        "drf_settings": [
            "exception_handler_key_in_rest_framework",
            "full_dotted_path_to_handler",
            "non_field_errors_key_configured",
            "default_renderer_classes_set",
            "default_parser_classes_set",
            "settings_in_base_py",
        ],
        "registration_location": [
            "config_settings_base_py",
            "rest_framework_dict_key",
            "handler_path_apps_core_exceptions",
            "imported_at_django_startup",
            "validated_on_first_request",
            "overridable_in_test_settings",
        ],
        "verification_steps": [
            "check_settings_rest_framework_dict",
            "verify_handler_import_path",
            "test_with_intentional_exception",
            "confirm_json_error_format",
            "verify_request_id_present",
            "verify_timestamp_present",
        ],
    }
    logger.debug(
        "Handler registration config: drf_settings=%d, registration_location=%d",
        len(config["drf_settings"]),
        len(config["registration_location"]),
    )
    return config


def get_handler_testing_config() -> dict:
    """Configure exception handler test suite. Ref: SP07-T45."""
    logger.debug("Configuring exception handler test suite...")
    config: dict = {
        "configured": True,
        "test_categories": [
            "drf_validation_error_tests",
            "drf_authentication_error_tests",
            "drf_permission_denied_tests",
            "drf_not_found_tests",
            "custom_api_exception_tests",
            "unexpected_exception_tests",
        ],
        "test_setup": [
            "api_request_factory_usage",
            "mock_request_objects",
            "direct_handler_invocation",
            "response_status_assertion",
            "response_body_assertion",
            "error_envelope_validation",
        ],
        "assertion_patterns": [
            "assert_status_code_matches",
            "assert_error_code_in_response",
            "assert_message_in_response",
            "assert_request_id_present",
            "assert_timestamp_present",
            "assert_path_in_response",
        ],
    }
    logger.debug(
        "Handler testing config: test_categories=%d, test_setup=%d",
        len(config["test_categories"]),
        len(config["test_setup"]),
    )
    return config


def get_handler_documentation_config() -> dict:
    """Configure exception handler documentation. Ref: SP07-T46."""
    logger.debug("Configuring exception handler documentation...")
    config: dict = {
        "configured": True,
        "documentation_sections": [
            "handler_overview_section",
            "configuration_section",
            "handling_order_section",
            "response_format_section",
            "testing_section",
            "troubleshooting_section",
        ],
        "code_examples": [
            "registration_in_settings",
            "custom_exception_usage",
            "error_response_sample",
            "test_case_example",
            "logging_configuration",
            "curl_test_commands",
        ],
        "maintenance_notes": [
            "update_docs_on_new_exceptions",
            "keep_examples_current",
            "document_breaking_changes",
            "version_handler_changes",
            "review_quarterly",
            "link_to_related_docs",
        ],
    }
    logger.debug(
        "Handler documentation config: documentation_sections=%d, code_examples=%d",
        len(config["documentation_sections"]),
        len(config["code_examples"]),
    )
    return config


def get_response_file_config() -> dict:
    """Configure response.py file for error response formatting. Ref: SP07-T47."""
    logger.debug("Configuring response.py file for error response formatting...")
    config: dict = {
        "configured": True,
        "file_structure": [
            "response_py_file_created",
            "located_in_exceptions_directory",
            "file_docstring_added",
            "version_info_in_module",
            "valid_python_module",
            "ready_for_error_response_class",
        ],
        "imports_required": [
            "datetime_from_datetime",
            "typing_any_dict_optional",
            "uuid4_from_uuid",
            "rest_framework_response",
            "rest_framework_status",
            "no_circular_imports",
        ],
        "module_capabilities": [
            "error_response_builder_class",
            "standard_format_enforcement",
            "dict_conversion_method",
            "drf_response_conversion",
            "automatic_timestamp_generation",
            "automatic_request_id_generation",
        ],
    }
    logger.debug(
        "Response file config: file_structure=%d, imports_required=%d",
        len(config["file_structure"]),
        len(config["imports_required"]),
    )
    return config


def get_error_response_class_config() -> dict:
    """Configure ErrorResponse class for standardized error responses. Ref: SP07-T48."""
    logger.debug("Configuring ErrorResponse class for standardized error responses...")
    config: dict = {
        "configured": True,
        "class_design": [
            "builder_pattern_class",
            "immutable_after_creation",
            "comprehensive_docstring",
            "type_hints_on_all_params",
            "default_values_for_optional",
            "single_responsibility_principle",
        ],
        "constructor_params": [
            "error_code_str_required",
            "message_str_required",
            "status_code_int_required",
            "details_optional_dict",
            "request_id_optional_str",
            "path_optional_str",
        ],
        "output_methods": [
            "to_dict_returns_error_envelope",
            "to_response_returns_drf_response",
            "nested_error_key_in_dict",
            "status_code_in_response",
            "all_fields_in_output",
            "consistent_format_always",
        ],
    }
    logger.debug(
        "ErrorResponse class config: class_design=%d, constructor_params=%d",
        len(config["class_design"]),
        len(config["constructor_params"]),
    )
    return config


def get_error_code_field_config() -> dict:
    """Configure error_code field in ErrorResponse. Ref: SP07-T49."""
    logger.debug("Configuring error_code field in ErrorResponse...")
    config: dict = {
        "configured": True,
        "field_design": [
            "string_type_field",
            "required_parameter",
            "uppercase_convention",
            "underscore_separated",
            "matches_error_codes_constants",
            "unique_per_error_type",
        ],
        "validation_rules": [
            "non_empty_string_required",
            "no_whitespace_allowed",
            "uppercase_letters_and_underscores",
            "must_match_defined_codes",
            "max_length_50_chars",
            "no_special_characters",
        ],
        "usage_patterns": [
            "client_error_identification",
            "error_handling_switch_case",
            "api_documentation_reference",
            "monitoring_and_alerting",
            "error_categorization",
            "internationalization_key",
        ],
    }
    logger.debug(
        "Error code field config: field_design=%d, validation_rules=%d",
        len(config["field_design"]),
        len(config["validation_rules"]),
    )
    return config


def get_message_field_config() -> dict:
    """Configure message field in ErrorResponse. Ref: SP07-T50."""
    logger.debug("Configuring message field in ErrorResponse...")
    config: dict = {
        "configured": True,
        "field_design": [
            "string_type_field",
            "required_parameter",
            "human_readable_text",
            "sentence_case_format",
            "ends_with_period_optional",
            "max_length_500_chars",
        ],
        "content_guidelines": [
            "clear_and_actionable",
            "no_technical_jargon",
            "no_sensitive_information",
            "helpful_for_end_users",
            "consistent_tone_and_style",
            "translatable_text",
        ],
        "localization_support": [
            "english_as_default_language",
            "translation_key_mapping",
            "accept_language_header_support",
            "locale_aware_formatting",
            "unicode_safe_text",
            "fallback_to_english",
        ],
    }
    logger.debug(
        "Message field config: field_design=%d, content_guidelines=%d",
        len(config["field_design"]),
        len(config["content_guidelines"]),
    )
    return config


def get_details_field_config() -> dict:
    """Configure details field in ErrorResponse. Ref: SP07-T51."""
    logger.debug("Configuring details field in ErrorResponse...")
    config: dict = {
        "configured": True,
        "field_design": [
            "dict_type_field",
            "optional_parameter",
            "defaults_to_empty_dict",
            "flexible_key_value_pairs",
            "json_serializable_values",
            "nested_structure_supported",
        ],
        "content_types": [
            "field_validation_errors",
            "constraint_violation_info",
            "resource_identification",
            "retry_after_seconds",
            "rate_limit_information",
            "suggested_actions",
        ],
        "security_considerations": [
            "no_stack_traces_included",
            "no_database_queries_exposed",
            "no_internal_paths_leaked",
            "no_credentials_in_details",
            "sanitized_user_input",
            "production_safe_content",
        ],
    }
    logger.debug(
        "Details field config: field_design=%d, content_types=%d",
        len(config["field_design"]),
        len(config["content_types"]),
    )
    return config


def get_request_id_field_config() -> dict:
    """Configure request_id field in ErrorResponse. Ref: SP07-T52."""
    logger.debug("Configuring request_id field in ErrorResponse...")
    config: dict = {
        "configured": True,
        "field_design": [
            "string_type_field",
            "optional_parameter",
            "auto_generated_if_missing",
            "uuid4_format",
            "preserved_from_middleware",
            "unique_per_request",
        ],
        "generation_strategy": [
            "middleware_value_preferred",
            "uuid4_fallback_generation",
            "x_request_id_header_check",
            "thread_safe_generation",
            "no_collision_guaranteed",
            "consistent_format",
        ],
        "tracing_support": [
            "log_correlation_identifier",
            "client_reference_for_support",
            "distributed_tracing_compatible",
            "included_in_response_headers",
            "searchable_in_log_systems",
            "audit_trail_linkage",
        ],
    }
    logger.debug(
        "Request ID field config: field_design=%d, generation_strategy=%d",
        len(config["field_design"]),
        len(config["generation_strategy"]),
    )
    return config


def get_timestamp_field_config() -> dict:
    """Configure timestamp field in ErrorResponse. Ref: SP07-T53."""
    logger.debug("Configuring timestamp field in ErrorResponse...")
    config: dict = {
        "configured": True,
        "field_design": [
            "string_type_field",
            "auto_generated_always",
            "iso8601_format",
            "utc_timezone_only",
            "z_suffix_appended",
            "millisecond_precision_optional",
        ],
        "format_specification": [
            "year_month_day_separator_t",
            "hours_minutes_seconds",
            "utc_indicator_z_suffix",
            "consistent_with_api_dates",
            "parseable_by_all_clients",
            "sortable_string_format",
        ],
        "timezone_handling": [
            "utc_canonical_timezone",
            "no_local_timezone_ever",
            "datetime_utcnow_usage",
            "timezone_aware_comparison",
            "consistent_with_database",
            "javascript_date_compatible",
        ],
    }
    logger.debug(
        "Timestamp field config: field_design=%d, format_specification=%d",
        len(config["field_design"]),
        len(config["format_specification"]),
    )
    return config


def get_path_field_config() -> dict:
    """Configure path field in ErrorResponse. Ref: SP07-T54."""
    logger.debug("Configuring path field in ErrorResponse...")
    config: dict = {
        "configured": True,
        "field_design": [
            "string_type_field",
            "optional_parameter",
            "defaults_to_empty_string",
            "request_path_value",
            "url_encoded_format",
            "no_query_parameters_included",
        ],
        "extraction_method": [
            "request_path_attribute",
            "safe_extraction_with_fallback",
            "null_request_handling",
            "empty_string_on_failure",
            "strips_query_string",
            "preserves_url_encoding",
        ],
        "privacy_considerations": [
            "no_query_params_exposed",
            "no_auth_tokens_in_path",
            "no_sensitive_data_leaked",
            "generic_path_in_production",
            "full_path_in_debug_mode",
            "compliance_with_gdpr",
        ],
    }
    logger.debug(
        "Path field config: field_design=%d, extraction_method=%d",
        len(config["field_design"]),
        len(config["extraction_method"]),
    )
    return config


def get_validation_error_formatting_config() -> dict:
    """Configure validation error formatting with field-level details. Ref: SP07-T55."""
    logger.debug("Configuring validation error formatting...")
    config: dict = {
        "configured": True,
        "formatting_rules": [
            "dot_notation_for_nested_fields",
            "flat_dict_output_structure",
            "string_conversion_for_values",
            "list_wrapping_for_single_values",
            "recursive_flattening_support",
            "parent_key_tracking",
        ],
        "input_handling": [
            "dict_input_recursive_processing",
            "list_input_preservation",
            "string_input_wrapping",
            "mixed_type_support",
            "empty_input_handling",
            "none_value_handling",
        ],
        "output_format": [
            "field_name_as_dict_key",
            "error_list_as_dict_value",
            "all_values_are_string_lists",
            "consistent_structure_always",
            "ready_for_json_serialization",
            "matches_drf_error_format",
        ],
    }
    logger.debug(
        "Validation error formatting config: formatting_rules=%d, input_handling=%d",
        len(config["formatting_rules"]),
        len(config["input_handling"]),
    )
    return config


def get_nested_error_flattening_config() -> dict:
    """Configure nested error flattening and validation factory method. Ref: SP07-T56."""
    logger.debug("Configuring nested error flattening...")
    config: dict = {
        "configured": True,
        "flattening_strategy": [
            "recursive_dict_traversal",
            "dot_notation_key_joining",
            "list_errors_preserved_at_leaf",
            "string_errors_wrapped_in_list",
            "depth_limit_for_safety",
            "circular_reference_protection",
        ],
        "edge_cases": [
            "empty_dict_input",
            "empty_list_input",
            "deeply_nested_structures",
            "mixed_dict_and_list_nesting",
            "unicode_field_names",
            "special_characters_in_keys",
        ],
        "factory_method": [
            "from_validation_error_classmethod",
            "creates_error_response_instance",
            "sets_validation_error_code",
            "sets_validation_failed_message",
            "applies_formatting_to_details",
            "accepts_optional_context",
        ],
    }
    logger.debug(
        "Nested error flattening config: flattening_strategy=%d, edge_cases=%d",
        len(config["flattening_strategy"]),
        len(config["edge_cases"]),
    )
    return config


def get_to_dict_method_config() -> dict:
    """Configure to_dict method for ErrorResponse. Ref: SP07-T57."""
    logger.debug("Configuring to_dict method for ErrorResponse...")
    config: dict = {
        "configured": True,
        "method_design": [
            "instance_method_no_params",
            "returns_dict_type",
            "nested_error_key_wrapper",
            "includes_all_six_fields",
            "json_serializable_output",
            "deterministic_output",
        ],
        "output_structure": [
            "top_level_error_key",
            "code_field_from_error_code",
            "message_field_from_message",
            "details_field_from_details",
            "request_id_field_value",
            "timestamp_and_path_fields",
        ],
        "field_mapping": [
            "error_code_maps_to_code",
            "message_maps_to_message",
            "details_maps_to_details",
            "request_id_maps_to_request_id",
            "timestamp_maps_to_timestamp",
            "path_maps_to_path",
        ],
    }
    logger.debug(
        "to_dict method config: method_design=%d, output_structure=%d",
        len(config["method_design"]),
        len(config["output_structure"]),
    )
    return config


def get_to_response_method_config() -> dict:
    """Configure to_response method for DRF Response conversion. Ref: SP07-T58."""
    logger.debug("Configuring to_response method for DRF Response conversion...")
    config: dict = {
        "configured": True,
        "method_design": [
            "instance_method_no_params",
            "returns_drf_response",
            "calls_to_dict_internally",
            "sets_status_code",
            "ready_for_drf_pipeline",
            "no_additional_headers",
        ],
        "response_creation": [
            "drf_response_class_used",
            "data_from_to_dict_method",
            "status_from_status_code",
            "content_type_json_implicit",
            "renderer_context_handled",
            "serialization_automatic",
        ],
        "status_handling": [
            "status_code_from_init",
            "valid_http_status_required",
            "4xx_for_client_errors",
            "5xx_for_server_errors",
            "matches_exception_status",
            "consistent_with_error_code",
        ],
    }
    logger.debug(
        "to_response method config: method_design=%d, response_creation=%d",
        len(config["method_design"]),
        len(config["response_creation"]),
    )
    return config


def get_response_formatting_testing_config() -> dict:
    """Configure response formatting test suite. Ref: SP07-T59."""
    logger.debug("Configuring response formatting test suite...")
    config: dict = {
        "configured": True,
        "test_categories": [
            "basic_error_response_tests",
            "validation_error_format_tests",
            "nested_error_flattening_tests",
            "to_dict_output_tests",
            "to_response_output_tests",
            "factory_method_tests",
        ],
        "test_assertions": [
            "assert_error_envelope_structure",
            "assert_all_fields_present",
            "assert_correct_status_code",
            "assert_error_code_matches",
            "assert_message_matches",
            "assert_details_formatted",
        ],
        "test_fixtures": [
            "sample_validation_errors",
            "sample_nested_errors",
            "sample_error_response",
            "mock_request_context",
            "expected_output_dicts",
            "edge_case_inputs",
        ],
    }
    logger.debug(
        "Response formatting testing config: test_categories=%d, test_assertions=%d",
        len(config["test_categories"]),
        len(config["test_assertions"]),
    )
    return config


def get_response_format_documentation_config() -> dict:
    """Configure response format documentation. Ref: SP07-T60."""
    logger.debug("Configuring response format documentation...")
    config: dict = {
        "configured": True,
        "documentation_sections": [
            "format_overview_section",
            "field_descriptions_table",
            "validation_error_format",
            "nested_error_examples",
            "usage_guide_section",
            "api_consumer_guide",
        ],
        "format_examples": [
            "basic_error_response_json",
            "validation_error_response_json",
            "nested_validation_json",
            "not_found_error_json",
            "server_error_json",
            "rate_limit_error_json",
        ],
        "developer_guide": [
            "when_to_use_error_response",
            "choosing_error_codes",
            "writing_error_messages",
            "adding_details_appropriately",
            "testing_error_responses",
            "extending_error_response",
        ],
    }
    logger.debug(
        "Response format documentation config: documentation_sections=%d, format_examples=%d",
        len(config["documentation_sections"]),
        len(config["format_examples"]),
    )
    return config


def get_error_logging_module_config() -> dict:
    """Configure error logging module setup. Ref: SP07-T61."""
    logger.debug("Configuring error logging module setup...")
    config: dict = {
        "configured": True,
        "module_components": [
            "error_logger_service",
            "log_formatter_module",
            "log_handler_registry",
            "error_context_builder",
            "log_level_manager",
            "log_output_adapter",
        ],
        "logging_features": [
            "structured_json_logging",
            "contextual_error_details",
            "automatic_stack_traces",
            "request_correlation_ids",
            "log_level_filtering",
            "async_log_buffering",
        ],
        "module_dependencies": [
            "python_logging_module",
            "django_logging_config",
            "structlog_processor",
            "sentry_sdk_integration",
            "json_formatter_library",
            "celery_logging_bridge",
        ],
    }
    logger.debug(
        "Error logging module config: module_components=%d, logging_features=%d",
        len(config["module_components"]),
        len(config["logging_features"]),
    )
    return config


def get_log_exception_function_config() -> dict:
    """Configure log_exception function. Ref: SP07-T62."""
    logger.debug("Configuring log_exception function...")
    config: dict = {
        "configured": True,
        "function_parameters": [
            "exception_instance_param",
            "log_level_param",
            "context_dict_param",
            "include_traceback_flag",
            "notify_admins_flag",
            "extra_metadata_param",
        ],
        "logging_behaviors": [
            "format_exception_message",
            "attach_context_metadata",
            "capture_stack_trace",
            "determine_severity_level",
            "enrich_with_request_info",
            "emit_structured_log_entry",
        ],
        "exception_handlers": [
            "handle_api_exception",
            "handle_validation_error",
            "handle_authentication_error",
            "handle_permission_error",
            "handle_not_found_error",
            "handle_server_error",
        ],
    }
    logger.debug(
        "log_exception function config: function_parameters=%d, logging_behaviors=%d",
        len(config["function_parameters"]),
        len(config["logging_behaviors"]),
    )
    return config


def get_request_context_logging_config() -> dict:
    """Configure request context for error logging. Ref: SP07-T63."""
    logger.debug("Configuring request context for error logging...")
    config: dict = {
        "configured": True,
        "request_fields": [
            "http_method_field",
            "request_path_field",
            "query_parameters_field",
            "client_ip_address_field",
            "user_agent_field",
            "request_id_header_field",
        ],
        "context_enrichment": [
            "add_request_timestamp",
            "add_correlation_id",
            "add_session_identifier",
            "add_api_version_info",
            "add_content_type_info",
            "add_request_body_summary",
        ],
        "extraction_methods": [
            "extract_from_django_request",
            "extract_from_drf_request",
            "extract_from_wsgi_environ",
            "extract_from_middleware",
            "extract_from_header_map",
            "extract_from_meta_dict",
        ],
    }
    logger.debug(
        "Request context logging config: request_fields=%d, context_enrichment=%d",
        len(config["request_fields"]),
        len(config["context_enrichment"]),
    )
    return config


def get_user_context_logging_config() -> dict:
    """Configure user context for error logging. Ref: SP07-T64."""
    logger.debug("Configuring user context for error logging...")
    config: dict = {
        "configured": True,
        "user_fields": [
            "user_id_field",
            "username_field",
            "user_email_field",
            "user_role_field",
            "is_authenticated_field",
            "last_login_field",
        ],
        "context_conditions": [
            "check_user_is_authenticated",
            "check_user_is_active",
            "check_user_has_profile",
            "check_anonymous_user",
            "check_service_account",
            "check_superuser_status",
        ],
        "privacy_measures": [
            "mask_email_address",
            "redact_personal_info",
            "anonymize_user_data",
            "hash_sensitive_fields",
            "apply_gdpr_filtering",
            "limit_pii_in_logs",
        ],
    }
    logger.debug(
        "User context logging config: user_fields=%d, context_conditions=%d",
        len(config["user_fields"]),
        len(config["context_conditions"]),
    )
    return config


def get_tenant_context_logging_config() -> dict:
    """Configure tenant context for error logging. Ref: SP07-T65."""
    logger.debug("Configuring tenant context for error logging...")
    config: dict = {
        "configured": True,
        "tenant_fields": [
            "tenant_id_field",
            "tenant_name_field",
            "tenant_schema_field",
            "tenant_plan_field",
            "tenant_status_field",
            "tenant_domain_field",
        ],
        "context_conditions": [
            "check_tenant_is_active",
            "check_tenant_exists",
            "check_tenant_in_request",
            "check_tenant_schema_set",
            "check_public_tenant",
            "check_tenant_permissions",
        ],
        "multi_tenant_handling": [
            "isolate_tenant_log_streams",
            "tag_logs_with_tenant_id",
            "route_to_tenant_log_store",
            "apply_tenant_log_retention",
            "filter_cross_tenant_data",
            "aggregate_tenant_metrics",
        ],
    }
    logger.debug(
        "Tenant context logging config: tenant_fields=%d, context_conditions=%d",
        len(config["tenant_fields"]),
        len(config["context_conditions"]),
    )
    return config


def get_stack_trace_logging_config() -> dict:
    """Configure stack trace logging. Ref: SP07-T66."""
    logger.debug("Configuring stack trace logging...")
    config: dict = {
        "configured": True,
        "trace_components": [
            "exception_type_info",
            "exception_message_text",
            "traceback_frame_list",
            "source_file_paths",
            "line_number_references",
            "local_variable_snapshot",
        ],
        "formatting_options": [
            "plain_text_format",
            "json_structured_format",
            "abbreviated_trace_format",
            "colorized_console_format",
            "html_rendered_format",
            "single_line_summary_format",
        ],
        "trace_handling": [
            "capture_full_traceback",
            "truncate_long_traces",
            "filter_framework_frames",
            "highlight_app_code_frames",
            "attach_source_context",
            "chain_exception_traces",
        ],
    }
    logger.debug(
        "Stack trace logging config: trace_components=%d, formatting_options=%d",
        len(config["trace_components"]),
        len(config["formatting_options"]),
    )
    return config


def get_sentry_sdk_install_config() -> dict:
    """Configure sentry-sdk installation. Ref: SP07-T67."""
    logger.debug("Configuring sentry-sdk installation...")
    config: dict = {
        "configured": True,
        "installation_steps": [
            "add_sentry_sdk_to_requirements",
            "pin_sentry_sdk_version",
            "install_sentry_sdk_package",
            "verify_sdk_installation",
            "check_sdk_compatibility",
            "update_lock_file",
        ],
        "sdk_packages": [
            "sentry_sdk_core",
            "sentry_django_integration",
            "sentry_celery_integration",
            "sentry_redis_integration",
            "sentry_logging_integration",
            "sentry_pure_eval_integration",
        ],
        "dependency_requirements": [
            "python_version_check",
            "django_version_compatibility",
            "urllib3_dependency",
            "certifi_dependency",
            "setuptools_dependency",
            "pip_version_requirement",
        ],
    }
    logger.debug(
        "Sentry SDK install config: installation_steps=%d, sdk_packages=%d",
        len(config["installation_steps"]),
        len(config["sdk_packages"]),
    )
    return config


def get_sentry_settings_config() -> dict:
    """Configure Sentry settings module. Ref: SP07-T68."""
    logger.debug("Configuring Sentry settings module...")
    config: dict = {
        "configured": True,
        "settings_components": [
            "sentry_init_call",
            "dsn_configuration_entry",
            "integrations_list_setup",
            "environment_tag_setting",
            "release_version_setting",
            "debug_mode_toggle",
        ],
        "integration_list": [
            "django_integration",
            "celery_integration",
            "redis_integration",
            "logging_integration",
            "excepthook_integration",
            "threading_integration",
        ],
        "configuration_options": [
            "traces_sample_rate",
            "profiles_sample_rate",
            "send_default_pii",
            "attach_stacktrace",
            "max_breadcrumbs",
            "before_send_callback",
        ],
    }
    logger.debug(
        "Sentry settings config: settings_components=%d, integration_list=%d",
        len(config["settings_components"]),
        len(config["integration_list"]),
    )
    return config


def get_sentry_dsn_config() -> dict:
    """Configure Sentry DSN setup. Ref: SP07-T69."""
    logger.debug("Configuring Sentry DSN setup...")
    config: dict = {
        "configured": True,
        "dsn_settings": [
            "dsn_url_format_validation",
            "dsn_protocol_selection",
            "dsn_public_key_extraction",
            "dsn_project_id_parsing",
            "dsn_host_configuration",
            "dsn_connection_verification",
        ],
        "environment_variables": [
            "SENTRY_DSN_env_var",
            "SENTRY_ENVIRONMENT_env_var",
            "SENTRY_RELEASE_env_var",
            "SENTRY_SERVER_NAME_env_var",
            "SENTRY_DEBUG_env_var",
            "SENTRY_LOG_LEVEL_env_var",
        ],
        "security_measures": [
            "dsn_secret_rotation",
            "dsn_vault_storage",
            "dsn_access_restriction",
            "dsn_audit_logging",
            "dsn_encryption_at_rest",
            "dsn_leak_prevention",
        ],
    }
    logger.debug(
        "Sentry DSN config: dsn_settings=%d, environment_variables=%d",
        len(config["dsn_settings"]),
        len(config["environment_variables"]),
    )
    return config


def get_sentry_sample_rate_config() -> dict:
    """Configure Sentry sample rate. Ref: SP07-T70."""
    logger.debug("Configuring Sentry sample rate...")
    config: dict = {
        "configured": True,
        "rate_settings": [
            "traces_sample_rate_value",
            "profiles_sample_rate_value",
            "error_sample_rate_value",
            "transaction_sample_rate_value",
            "custom_sampling_function",
            "adaptive_sampling_toggle",
        ],
        "environment_configs": [
            "development_sample_rate",
            "staging_sample_rate",
            "production_sample_rate",
            "testing_sample_rate",
            "ci_cd_sample_rate",
            "load_test_sample_rate",
        ],
        "performance_options": [
            "max_spans_per_transaction",
            "idle_transaction_timeout",
            "heartbeat_interval_setting",
            "trim_backlog_toggle",
            "propagate_traces_setting",
            "instrument_db_queries",
        ],
    }
    logger.debug(
        "Sentry sample rate config: rate_settings=%d, environment_configs=%d",
        len(config["rate_settings"]),
        len(config["environment_configs"]),
    )
    return config
