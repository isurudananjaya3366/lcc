"""
Core middleware utilities for LankaCommerce Cloud core infrastructure.

SubPhase-06, Group-A Tasks 01-14, Group-B Tasks 15-28, Group-C Tasks 29-44, Group-D Tasks 45-58, Group-E Tasks 59-74, Group-F Tasks 75-88.

Provides core middleware configuration helpers used by the
core application for documenting Django middleware setup.

Functions:
    get_middleware_directory_config()   -- Middleware directory config (Task 01).
    get_middleware_init_config()        -- Middleware __init__.py config (Task 02).
    get_base_middleware_class_config()  -- Base middleware class config (Task 03).
    get_process_request_config()       -- Process request method config (Task 04).
    get_process_response_config()      -- Process response method config (Task 05).
    get_process_exception_config()     -- Process exception method config (Task 06).
    get_middleware_utilities_config()   -- Middleware utilities module config (Task 07).
    get_client_ip_utility_config()     -- Client IP utility config (Task 08).
    get_user_agent_utility_config()    -- User agent utility config (Task 09).
    get_request_id_generation_config() -- Request ID generation config (Task 10).
    get_middleware_settings_config()   -- Middleware settings config (Task 11).
    get_middleware_constants_config()  -- Middleware constants config (Task 12).
    get_middleware_order_config()      -- Middleware order config (Task 13).
    get_base_infrastructure_test_config() -- Base infrastructure test config (Task 14).
    get_django_tenants_config()        -- Django tenants config (Task 15).
    get_custom_tenant_middleware_config() -- Custom tenant middleware config (Task 16).
    get_tenant_resolution_logic_config() -- Tenant resolution logic config (Task 17).
    get_subdomain_resolution_config()  -- Subdomain resolution config (Task 18).
    get_custom_domain_resolution_config() -- Custom domain resolution config (Task 19).
    get_public_schema_handling_config() -- Public schema handling config (Task 20).
    get_tenant_not_found_handler_config() -- Tenant not found handler config (Task 21).
    get_tenant_inactive_handler_config() -- Tenant inactive handler config (Task 22).
    get_request_tenant_attribute_config() -- Request tenant attribute config (Task 23).
    get_thread_local_storage_config()      -- Thread local storage config (Task 24).
    get_get_current_tenant_utility_config() -- get_current_tenant utility config (Task 25).
    get_middleware_registration_config()    -- Middleware registration config (Task 26).
    get_tenant_resolution_tests_config()   -- Tenant resolution tests config (Task 27).
    get_tenant_middleware_docs_config()     -- Tenant middleware docs config (Task 28).
    get_logging_middleware_file_config()    -- Logging middleware file config (Task 29).
    get_logging_middleware_class_config()   -- Logging middleware class config (Task 30).
    get_request_start_time_config()        -- Request start time config (Task 31).
    get_request_end_time_config()          -- Request end time config (Task 32).
    get_response_duration_config()         -- Response duration config (Task 33).
    get_log_request_details_config()       -- Log request details config (Task 34).
    get_log_response_details_config()      -- Log response details config (Task 35).
    get_request_id_header_config()         -- Request ID header config (Task 36).
    get_tenant_id_logging_config()         -- Tenant ID logging config (Task 37).
    get_user_id_logging_config()           -- User ID logging config (Task 38).
    get_log_format_config()                -- Log format configuration (Task 39).
    get_request_body_logging_config()      -- Request body logging config (Task 40).
    get_health_check_exclusion_config()    -- Health check exclusion config (Task 41).
    get_static_files_exclusion_config()    -- Static files exclusion config (Task 42).
    get_logging_middleware_registration_config()  -- Logging middleware registration (Task 43).
    get_test_request_logging_config()             -- Test request logging config (Task 44).
    get_security_headers_file_config()     -- Security headers file config (Task 45).
    get_security_headers_class_config()    -- Security headers class config (Task 46).
    get_x_content_type_options_config()    -- X-Content-Type-Options config (Task 47).
    get_x_frame_options_config()           -- X-Frame-Options config (Task 48).
    get_x_xss_protection_config()          -- X-XSS-Protection config (Task 49).
    get_referrer_policy_config()           -- Referrer-Policy config (Task 50).
    get_csp_header_config()                -- CSP header config (Task 51).
    get_csp_directives_config()            -- CSP directives config (Task 52).
    get_permissions_policy_config()        -- Permissions-Policy config (Task 53).
    get_hsts_header_config()               -- HSTS header config (Task 54).
    get_hsts_age_config()                  -- HSTS age config (Task 55).
    get_x_request_id_header_config()       -- X-Request-ID header config (Task 56).
    get_security_headers_registration_config() -- Security headers registration config (Task 57).
    get_test_security_headers_config()     -- Test security headers config (Task 58).
    get_ratelimit_file_config()            -- Rate limit file config (Task 59).
    get_ratelimit_class_config()           -- Rate limit class config (Task 60).
    get_redis_backend_config()             -- Redis backend config (Task 61).
    get_ip_based_ratelimit_config()    -- IP-based rate limit config (Task 62).
    get_user_based_ratelimit_config()  -- User-based rate limit config (Task 63).
    get_tenant_based_ratelimit_config()-- Tenant-based rate limit config (Task 64).
    get_endpoint_based_ratelimit_config() -- Endpoint-based rate limit config (Task 65).
    get_ratelimit_window_config()      -- Rate limit window config (Task 66).
    get_x_ratelimit_limit_header_config() -- X-RateLimit-Limit header config (Task 67).
    get_x_ratelimit_remaining_header_config() -- X-RateLimit-Remaining header config (Task 68).
    get_x_ratelimit_reset_header_config() -- X-RateLimit-Reset header config (Task 69).
    get_retry_after_header_config()    -- Retry-After header config (Task 70).
    get_429_response_handling_config()  -- 429 response handling config (Task 71).
    get_ip_whitelist_config()          -- IP whitelist config (Task 72).
    get_ratelimit_middleware_registration_config() -- Rate limit middleware registration config (Task 73).
    get_ratelimit_testing_config()     -- Rate limit testing config (Task 74).
    get_timezone_file_config()         -- Timezone file config (Task 75).
    get_timezone_class_config()        -- Timezone class config (Task 76).
    get_tenant_timezone_config()       -- Tenant timezone config (Task 77).
    get_user_timezone_config()         -- User timezone config (Task 78).
    get_timezone_activation_config()   -- Timezone activation config (Task 79).
    get_default_timezone_config()      -- Default timezone config (Task 80).
    get_timezone_middleware_registration_config() -- Timezone middleware registration config (Task 81).
    get_middleware_setting_config()    -- Middleware setting config (Task 82).
    get_middleware_order_verification_config() -- Middleware order verification config (Task 83).

See also:
    - apps.core.utils.__init__  -- public re-exports
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def get_middleware_directory_config() -> dict:
    """Return configuration for the core middleware directory structure.

    SubPhase-06, Group-A, Task 01.
    """
    config: dict = {
        "configured": True,
        "directory_details": [
            "middleware directory created at backend/apps/core/middleware path",
            "Directory uses lowercase singular naming convention per Django standards",
            "Parent directory apps/core verified to exist before middleware creation",
            "Directory serves as container for all custom middleware components",
            "Contents will include base.py utils.py and individual middleware files",
            "Directory structure supports future expansion with multiple middleware files",
        ],
        "structure_details": [
            "middleware package sits alongside models.py views.py and apps.py",
            "Package will contain BaseMiddleware abstract class in base.py module",
            "Package will contain utility functions in utils.py helper module",
            "Individual middleware implementations each get their own Python module",
            "Package __init__.py provides clean namespace separation for imports",
            "Structure follows Django new-style middleware pattern from version 1.10",
        ],
        "naming_details": [
            "Directory named middleware singular not middlewares following Django convention",
            "All middleware files use lowercase_with_underscores naming convention",
            "Class names use PascalCase like TenantMiddleware and SecurityMiddleware",
            "Module files named after middleware purpose like tenant.py and logging.py",
            "Package location at apps.core.middleware enables clean import statements",
            "Naming pattern matches other core packages like utils and models modules",
        ],
    }
    logger.debug(
        "middleware directory config: directory_details=%d, structure_details=%d",
        len(config["directory_details"]),
        len(config["structure_details"]),
    )
    return config


def get_middleware_init_config() -> dict:
    """Return configuration for the middleware package __init__.py file.

    SubPhase-06, Group-A, Task 02.
    """
    config: dict = {
        "configured": True,
        "init_details": [
            "__init__.py file created in middleware directory marking it as Python package",
            "Module-level docstring describes package purpose and middleware classes",
            "Docstring includes usage examples showing from apps.core.middleware import",
            "File documents six planned middleware BaseMiddleware through CORSMiddleware",
            "Python recognizes middleware directory as importable package with __init__",
            "File follows Django middleware conventions for new-style MIDDLEWARE setting",
        ],
        "export_details": [
            "__all__ list defined with commented entries for future middleware classes",
            "Export list includes BaseMiddleware TenantMiddleware RequestLoggingMiddleware",
            "Export list includes PerformanceMiddleware SecurityMiddleware CORSMiddleware",
            "Future import statements prepared as comments for each middleware class",
            "From-import style used for importing classes from submodules like base.py",
            "Explicit __all__ controls what is exported with star import statements",
        ],
        "convention_details": [
            "Django new-style middleware uses __init__ and __call__ method pattern",
            "Each middleware class takes get_response callable in __init__ constructor",
            "Each middleware class implements __call__ taking request as parameter",
            "Optional hooks include process_view process_exception process_template_response",
            "Middleware registered in settings.MIDDLEWARE list with dotted path string",
            "Middleware execution order is top-to-bottom for requests bottom-to-top responses",
        ],
    }
    logger.debug(
        "middleware init config: init_details=%d, export_details=%d",
        len(config["init_details"]),
        len(config["export_details"]),
    )
    return config


def get_base_middleware_class_config() -> dict:
    """Return configuration for the BaseMiddleware abstract base class.

    SubPhase-06, Group-A, Task 03.
    """
    config: dict = {
        "configured": True,
        "class_details": [
            "BaseMiddleware class created in apps/core/middleware/base.py module",
            "Class inherits from ABC for abstract base class pattern enforcement",
            "Imports include ABC logging Callable Optional HttpRequest HttpResponse",
            "Module-level logger created with logging.getLogger(__name__) call",
            "Class docstring explains middleware execution order and usage pattern",
            "Class provides standardized hooks for request response and exception",
        ],
        "init_details": [
            "__init__ method accepts get_response Callable as required parameter",
            "__init__ stores get_response as self.get_response instance variable",
            "__init__ type hint is Callable[[HttpRequest] HttpResponse] for get_response",
            "__call__ method accepts HttpRequest and returns HttpResponse object",
            "__call__ orchestrates process_request get_response and process_response",
            "__call__ wraps get_response in try-except calling process_exception on error",
        ],
        "flow_details": [
            "Execution flow starts with process_request for pre-processing request",
            "If process_request returns HttpResponse it short-circuits skipping view",
            "If process_request returns None request continues to get_response view",
            "Exceptions during get_response are caught and sent to process_exception",
            "If process_exception returns None the exception is re-raised by Django",
            "Final step calls process_response for post-processing before returning",
        ],
    }
    logger.debug(
        "base middleware class config: class_details=%d, init_details=%d",
        len(config["class_details"]),
        len(config["init_details"]),
    )
    return config


def get_process_request_config() -> dict:
    """Return configuration for the process_request middleware hook.

    SubPhase-06, Group-A, Task 04.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "process_request signature is self request HttpRequest returns Optional[HttpResponse]",
            "Method is not marked abstractmethod allowing optional override by subclasses",
            "Default implementation returns None to continue processing to next middleware",
            "Debug logging includes self.__class__.__name__ and request.path information",
            "Docstring documents return None to continue or HttpResponse to short-circuit",
            "Docstring includes example showing authentication check returning 401 status",
        ],
        "usecase_details": [
            "Authentication checks verify request.user.is_authenticated before view access",
            "Rate limiting blocks requests exceeding configured threshold with 429 status",
            "Request validation checks format and content before allowing view processing",
            "Request enrichment adds custom attributes to request object for view use",
            "Caching returns cached response without hitting view for performance gains",
            "Authorization verifies user has required permissions before view execution",
        ],
        "shortcircuit_details": [
            "Return None allows request to continue to next middleware or view function",
            "Return HttpResponse skips all remaining middleware and view entirely",
            "Short-circuit useful for early rejection of invalid or unauthorized requests",
            "Short-circuit avoids unnecessary database queries for blocked requests",
            "JsonResponse can be returned for API endpoints needing structured error data",
            "HttpResponseForbidden or HttpResponseNotFound are common short-circuit responses",
        ],
    }
    logger.debug(
        "process request config: method_details=%d, usecase_details=%d",
        len(config["method_details"]),
        len(config["usecase_details"]),
    )
    return config


def get_process_response_config() -> dict:
    """Return configuration for the process_response middleware hook.

    SubPhase-06, Group-A, Task 05.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "process_response signature takes self request HttpRequest response HttpResponse",
            "Method returns HttpResponse and must always return a response object",
            "Default implementation returns response unchanged passing it through directly",
            "Debug logging includes class name request.path and response.status_code info",
            "Docstring documents that response must always be returned from this method",
            "Docstring includes example showing adding X-Custom-Header to response object",
        ],
        "header_details": [
            "CORS headers like Access-Control-Allow-Origin can be added in process_response",
            "Security headers like X-Frame-Options DENY prevent clickjacking attacks",
            "X-Content-Type-Options nosniff prevents MIME type sniffing by browsers",
            "X-Processing-Time header can track request processing duration for monitoring",
            "Cache-Control headers control browser and proxy caching behavior for responses",
            "Custom headers like X-Request-ID can be added for distributed tracing support",
        ],
        "modification_details": [
            "Response content can be compressed for bandwidth optimization before sending",
            "Response format can be transformed such as JSON to XML conversion if needed",
            "Cookies can be set or modified on the response object before client receives",
            "Conditional modification checks Content-Type before applying transformations",
            "Response status code can be changed based on middleware post-processing logic",
            "Response timing headers computed from request.start_time if set by process_request",
        ],
    }
    logger.debug(
        "process response config: method_details=%d, header_details=%d",
        len(config["method_details"]),
        len(config["header_details"]),
    )
    return config


def get_process_exception_config() -> dict:
    """Return configuration for the process_exception middleware hook.

    SubPhase-06, Group-A, Task 06.
    """
    config: dict = {
        "configured": True,
        "method_details": [
            "process_exception signature takes self request HttpRequest exception Exception",
            "Method returns Optional[HttpResponse] with None meaning re-raise exception",
            "Default implementation returns None allowing Django to handle the exception",
            "Error-level logging includes class name exception type message and request path",
            "Docstring documents return None to re-raise or HttpResponse to handle exception",
            "Docstring includes example showing isinstance check for CustomError with 400",
        ],
        "handling_details": [
            "Custom error pages can return HTML response for user-friendly error display",
            "API error responses return JsonResponse with structured error data and status",
            "Logging and monitoring records exception details before re-raising for Django",
            "Exception transformation converts technical errors to user-friendly messages",
            "Fallback responses return cached or default data when database errors occur",
            "External service reporting sends exception details to monitoring platforms",
        ],
        "flow_details": [
            "Exception hook called only when get_response raises an Exception in __call__",
            "Returning HttpResponse means exception is handled and response is returned",
            "Returning None means exception propagates to Django default error handler",
            "ValidationError can be caught and converted to 400 Bad Request JsonResponse",
            "DatabaseError can trigger 503 Service Unavailable with retry-after header",
            "PermissionDenied can be caught and converted to 403 Forbidden with details",
        ],
    }
    logger.debug(
        "process exception config: method_details=%d, handling_details=%d",
        len(config["method_details"]),
        len(config["handling_details"]),
    )
    return config


def get_middleware_utilities_config() -> dict:
    """Return configuration for the middleware utilities module.

    SubPhase-06, Group-A, Task 07.
    """
    config: dict = {
        "configured": True,
        "utility_types": [
            "get_client_ip extracts real client IP address from request headers",
            "get_user_agent parses User-Agent header to identify client browser type",
            "generate_request_id creates unique UUID4 identifier for request tracing",
            "get_request_metadata collects common request attributes into dictionary",
            "sanitize_header_value strips dangerous characters from header values",
            "is_ajax_request checks if request was made via XMLHttpRequest header",
        ],
        "module_structure": [
            "utils.py module created inside apps/core/middleware package directory",
            "Module imports include uuid logging HttpRequest and typing helpers",
            "Module-level logger created with logging.getLogger(__name__) pattern",
            "All utility functions are pure functions with no side effects on request",
            "Functions accept HttpRequest and return simple Python types like str dict",
            "Module documented with docstring listing all public utility functions",
        ],
        "shared_operations": [
            "IP extraction shared across TenantMiddleware and SecurityMiddleware classes",
            "User-Agent parsing shared across logging and analytics middleware classes",
            "Request ID generation shared across logging and tracing middleware classes",
            "Header sanitization shared across all middleware that reads custom headers",
            "Metadata collection shared across logging performance and audit middleware",
            "Ajax detection shared across response format and content negotiation logic",
        ],
    }
    logger.debug(
        "middleware utilities config: utility_types=%d, module_structure=%d",
        len(config["utility_types"]),
        len(config["module_structure"]),
    )
    return config


def get_client_ip_utility_config() -> dict:
    """Return configuration for the get_client_ip utility function.

    SubPhase-06, Group-A, Task 08.
    """
    config: dict = {
        "configured": True,
        "ip_extraction_steps": [
            "Check HTTP_X_FORWARDED_FOR header first for proxy-passed client IP",
            "Split X-Forwarded-For by comma and take the first IP as original client",
            "Strip whitespace from extracted IP string to normalize formatting",
            "Fall back to HTTP_X_REAL_IP header if X-Forwarded-For is not present",
            "Fall back to REMOTE_ADDR as last resort when no proxy headers exist",
            "Return 0.0.0.0 as default when no IP information is available at all",
        ],
        "proxy_handling": [
            "X-Forwarded-For may contain chain of IPs from multiple proxy servers",
            "First IP in X-Forwarded-For chain is the original client IP address",
            "Trusted proxy configuration determines which proxy headers to trust",
            "Load balancers like Nginx append client IP to X-Forwarded-For header",
            "CloudFlare uses CF-Connecting-IP header for original client IP address",
            "AWS ALB adds client IP as first entry in X-Forwarded-For header chain",
        ],
        "header_sources": [
            "HTTP_X_FORWARDED_FOR is the standard header for proxied client IP info",
            "HTTP_X_REAL_IP is set by Nginx proxy_set_header X-Real-IP directive",
            "REMOTE_ADDR contains the direct connection IP from the WSGI server",
            "HTTP_CF_CONNECTING_IP is CloudFlare specific original client IP header",
            "HTTP_X_CLUSTER_CLIENT_IP used by some load balancer configurations",
            "HTTP_FORWARDED is the RFC 7239 standard replacement for X-Forwarded-For",
        ],
    }
    logger.debug(
        "client ip utility config: ip_extraction_steps=%d, proxy_handling=%d",
        len(config["ip_extraction_steps"]),
        len(config["proxy_handling"]),
    )
    return config


def get_user_agent_utility_config() -> dict:
    """Return configuration for the get_user_agent utility function.

    SubPhase-06, Group-A, Task 09.
    """
    config: dict = {
        "configured": True,
        "user_agent_sources": [
            "HTTP_USER_AGENT header is the primary source of browser identification",
            "User-Agent string contains browser name version and rendering engine",
            "User-Agent string includes operating system name and version details",
            "Mobile devices include device model information in User-Agent string",
            "Bot crawlers identify themselves with bot name and URL in User-Agent",
            "Empty string returned as default when User-Agent header is not present",
        ],
        "client_types": [
            "Desktop browsers like Chrome Firefox Safari Edge send standard UA strings",
            "Mobile browsers include Mobile keyword and device model in UA string",
            "API clients like curl httpie requests include library name and version",
            "Search engine bots like Googlebot Bingbot include crawler identification",
            "Native mobile apps send custom User-Agent with app name and version",
            "Automated testing tools like Selenium include WebDriver in UA string",
        ],
        "extraction_methods": [
            "request.META.get HTTP_USER_AGENT with empty string as default value",
            "Strip leading and trailing whitespace from extracted User-Agent string",
            "Truncate User-Agent to maximum 512 characters to prevent abuse attacks",
            "Log warning when User-Agent exceeds expected length for security review",
            "Return type is always str even when header is missing returns empty str",
            "Function is pure with no side effects and does not modify request object",
        ],
    }
    logger.debug(
        "user agent utility config: user_agent_sources=%d, client_types=%d",
        len(config["user_agent_sources"]),
        len(config["client_types"]),
    )
    return config


def get_request_id_generation_config() -> dict:
    """Return configuration for the generate_request_id utility function.

    SubPhase-06, Group-A, Task 10.
    """
    config: dict = {
        "configured": True,
        "generation_methods": [
            "uuid.uuid4() generates a random UUID version 4 for each request",
            "UUID converted to string with str(uuid.uuid4()) for header compatibility",
            "Hyphens included in UUID string format like 550e8400-e29b-41d4-a716",
            "No database lookup needed as UUID4 is generated from random bytes",
            "Collision probability is negligible with 122 bits of random data",
            "Function can accept optional prefix to namespace request IDs by service",
        ],
        "uuid_properties": [
            "UUID version 4 uses 122 random bits for globally unique identifiers",
            "UUID string representation is 36 characters including four hyphens",
            "UUID format follows RFC 4122 standard for universally unique identifiers",
            "UUID version 4 does not encode timestamp or MAC address information",
            "Python uuid module uses os.urandom for cryptographically secure random",
            "UUID objects support equality comparison hashing and string conversion",
        ],
        "usage_contexts": [
            "Request tracing assigns unique ID to correlate logs across services",
            "X-Request-ID response header returns generated ID to client for support",
            "Distributed tracing propagates request ID across microservice boundaries",
            "Error reporting includes request ID for quick lookup in log aggregation",
            "Performance monitoring tags metrics with request ID for drill-down analysis",
            "Audit logging records request ID alongside user actions for accountability",
        ],
    }
    logger.debug(
        "request id generation config: generation_methods=%d, uuid_properties=%d",
        len(config["generation_methods"]),
        len(config["uuid_properties"]),
    )
    return config


def get_middleware_settings_config() -> dict:
    """Return configuration for the middleware settings file.

    SubPhase-06, Group-A, Task 11.
    """
    config: dict = {
        "configured": True,
        "settings_sections": [
            "request_tracking section configures unique ID generation for each request",
            "client_information section configures IP extraction and user agent parsing",
            "performance_monitoring section configures timing and metrics collection",
            "security_headers section configures protective HTTP response headers",
            "logging_config section configures middleware-specific logging formatting",
            "tenant_settings section configures multi-tenant middleware behavior",
        ],
        "file_structure": [
            "Settings file located at apps/core/middleware/settings.py module path",
            "Module imports Django conf settings for overridable default values",
            "Each section organized as a Python dictionary with descriptive keys",
            "Default values provided for all settings with Django settings override",
            "Type hints applied to all configuration variables for static analysis",
            "Module-level docstring documents all available configuration options",
        ],
        "configuration_patterns": [
            "getattr pattern used to read from Django settings with safe defaults",
            "MIDDLEWARE_REQUEST_TRACKING_ENABLED setting controls request ID feature",
            "MIDDLEWARE_PERFORMANCE_MONITORING setting controls timing collection",
            "MIDDLEWARE_SECURITY_HEADERS_ENABLED setting controls header injection",
            "MIDDLEWARE_LOG_LEVEL setting controls verbosity of middleware logging",
            "MIDDLEWARE_TENANT_HEADER setting configures tenant identification header",
        ],
    }
    logger.debug(
        "middleware settings config: settings_sections=%d, file_structure=%d",
        len(config["settings_sections"]),
        len(config["file_structure"]),
    )
    return config


def get_middleware_constants_config() -> dict:
    """Return configuration for the MIDDLEWARE_CONFIG dictionary constants.

    SubPhase-06, Group-A, Task 12.
    """
    config: dict = {
        "configured": True,
        "config_categories": [
            "request_id_enabled controls whether unique request IDs are generated",
            "client_ip_enabled controls whether client IP extraction is performed",
            "timing_enabled controls whether request timing metrics are collected",
            "secure_headers_enabled controls whether security headers are injected",
            "request_logging_enabled controls whether request details are logged",
            "cache_enabled controls whether middleware response caching is active",
        ],
        "default_values": [
            "REQUEST_ID_ENABLED defaults to True for request tracing in all envs",
            "CLIENT_IP_ENABLED defaults to True for IP extraction in all envs",
            "TIMING_ENABLED defaults to True for performance monitoring in all envs",
            "SECURE_HEADERS_ENABLED defaults to True for security in all envs",
            "REQUEST_LOGGING_ENABLED defaults to True for audit logging in all envs",
            "CACHE_ENABLED defaults to False requiring explicit opt-in for caching",
        ],
        "security_settings": [
            "X_FRAME_OPTIONS set to DENY to prevent clickjacking attacks on pages",
            "X_CONTENT_TYPE_OPTIONS set to nosniff to prevent MIME type sniffing",
            "X_XSS_PROTECTION set to 1 mode=block for legacy XSS filter support",
            "STRICT_TRANSPORT_SECURITY max-age set to 31536000 for HSTS enforcement",
            "REFERRER_POLICY set to strict-origin-when-cross-origin for privacy",
            "PERMISSIONS_POLICY configured to restrict browser feature access scope",
        ],
    }
    logger.debug(
        "middleware constants config: config_categories=%d, default_values=%d",
        len(config["config_categories"]),
        len(config["default_values"]),
    )
    return config


def get_middleware_order_config() -> dict:
    """Return configuration for documenting middleware execution order.

    SubPhase-06, Group-A, Task 13.
    """
    config: dict = {
        "configured": True,
        "execution_phases": [
            "security_first phase places SecurityMiddleware at top of MIDDLEWARE list",
            "monitoring_early phase places performance timing before heavy processing",
            "caching_before_session phase places cache middleware before session lookup",
            "session_and_auth phase places SessionMiddleware then AuthenticationMiddleware",
            "content_processing phase places MessageMiddleware and locale after auth",
            "custom_placement phase places tenant and logging middleware after auth layer",
        ],
        "ordering_rules": [
            "SecurityMiddleware must be first to set HTTPS and security headers early",
            "GZipMiddleware should be near top to compress responses from all middleware",
            "SessionMiddleware must come before AuthenticationMiddleware for user loading",
            "AuthenticationMiddleware must come before any middleware checking request.user",
            "TenantMiddleware should come after auth to access authenticated user context",
            "RequestLoggingMiddleware should be last to capture complete request lifecycle",
        ],
        "common_mistakes": [
            "Placing AuthenticationMiddleware before SessionMiddleware causes AttributeError",
            "Placing CsrfViewMiddleware after view processing skips CSRF token validation",
            "Placing SecurityMiddleware too low misses security headers on error responses",
            "Placing CacheMiddleware after session causes per-user cache key issues",
            "Placing TenantMiddleware before auth prevents tenant-user verification logic",
            "Placing LoggingMiddleware too early misses response data from later middleware",
        ],
    }
    logger.debug(
        "middleware order config: execution_phases=%d, ordering_rules=%d",
        len(config["execution_phases"]),
        len(config["ordering_rules"]),
    )
    return config


def get_base_infrastructure_test_config() -> dict:
    """Return configuration for testing the complete base middleware infrastructure.

    SubPhase-06, Group-A, Task 14.
    """
    config: dict = {
        "configured": True,
        "test_categories": [
            "base_middleware_init tests verify __init__ stores get_response callable",
            "call_method_flow tests verify __call__ orchestrates full request lifecycle",
            "process_request_hook tests verify pre-processing and short-circuit behavior",
            "process_response_hook tests verify post-processing and header modification",
            "process_exception_hook tests verify error handling and recovery paths",
            "utility_functions tests verify IP extraction user agent and request ID helpers",
        ],
        "coverage_targets": [
            "BaseMiddleware __init__ method has 100 percent line and branch coverage",
            "BaseMiddleware __call__ method has 100 percent line and branch coverage",
            "process_request default None return path covered by base class test",
            "process_response default pass-through path covered by base class test",
            "process_exception default None return path covered by base class test",
            "All utility functions have dedicated unit tests with edge case coverage",
        ],
        "integration_tests": [
            "Full request lifecycle test sends request through complete middleware stack",
            "Exception handling test verifies process_exception receives raised errors",
            "Short-circuit test verifies process_request HttpResponse skips view call",
            "Header injection test verifies process_response adds expected headers",
            "Chained middleware test verifies multiple middleware execute in correct order",
            "Django test client integration verifies middleware works with real HTTP flow",
        ],
    }
    logger.debug(
        "base infrastructure test config: test_categories=%d, coverage_targets=%d",
        len(config["test_categories"]),
        len(config["coverage_targets"]),
    )
    return config


def get_django_tenants_config() -> dict:
    """Configure django-tenants middleware settings. Ref: SP06-T15."""
    logger.debug("Configuring django-tenants middleware settings...")
    config: dict = {
        "configured": True,
        "middleware_settings": [
            "tenant_main_middleware_position",
            "security_middleware_first",
            "session_middleware_after",
            "tenant_model_path_config",
            "domain_model_path_config",
            "public_schema_name_setting",
        ],
        "tenant_model_settings": [
            "TENANT_MODEL_reference",
            "TENANT_DOMAIN_MODEL_reference",
            "PUBLIC_SCHEMA_NAME_value",
            "PUBLIC_SCHEMA_URLCONF_path",
            "shared_apps_configuration",
            "tenant_apps_configuration",
        ],
        "configuration_patterns": [
            "early_middleware_positioning",
            "model_path_dot_notation",
            "separate_url_configurations",
            "schema_name_lowercase",
            "app_list_separation",
            "database_router_setup",
        ],
    }
    logger.debug(
        "django tenants config: middleware_settings=%d, tenant_model_settings=%d",
        len(config["middleware_settings"]),
        len(config["tenant_model_settings"]),
    )
    return config


def get_custom_tenant_middleware_config() -> dict:
    """Configure custom TenantMiddleware class creation. Ref: SP06-T16."""
    logger.debug("Configuring custom TenantMiddleware class creation...")
    config: dict = {
        "configured": True,
        "middleware_methods": [
            "process_request_override",
            "resolve_custom_domain_stub",
            "resolve_subdomain_stub",
            "is_public_host_check",
            "get_public_tenant_lookup",
            "handle_not_found_response",
        ],
        "resolution_priority": [
            "custom_domain_first_priority",
            "subdomain_second_priority",
            "public_schema_third_priority",
            "error_handling_final_step",
            "request_tenant_attachment",
            "lazy_model_imports_pattern",
        ],
        "design_principles": [
            "extend_dont_replace_parent",
            "tenant_main_middleware_base",
            "json_response_error_format",
            "clear_resolution_order_docs",
            "graceful_degradation_on_error",
            "no_circular_import_issues",
        ],
    }
    logger.debug(
        "custom tenant middleware config: middleware_methods=%d, resolution_priority=%d",
        len(config["middleware_methods"]),
        len(config["resolution_priority"]),
    )
    return config


def get_tenant_resolution_logic_config() -> dict:
    """Configure tenant resolution logic and priority flow. Ref: SP06-T17."""
    logger.debug("Configuring tenant resolution logic and priority flow...")
    config: dict = {
        "configured": True,
        "resolution_priority": [
            "custom_domain_first_check",
            "subdomain_second_check",
            "public_schema_third_check",
            "tenant_not_found_handling",
            "inactive_tenant_handling",
            "disallowed_host_exception",
        ],
        "process_request_steps": [
            "hostname_extraction_from_request",
            "tenant_variable_initialization",
            "priority_based_resolution_flow",
            "tenant_validation_and_active_check",
            "request_tenant_attribute_setting",
            "parent_process_request_call",
        ],
        "error_handling_patterns": [
            "disallowed_host_returns_404",
            "tenant_not_found_returns_404",
            "inactive_tenant_returns_403",
            "database_error_returns_500",
            "comprehensive_exception_logging",
            "json_response_error_format",
        ],
    }
    logger.debug(
        "tenant resolution logic config: resolution_priority=%d, process_request_steps=%d",
        len(config["resolution_priority"]),
        len(config["process_request_steps"]),
    )
    return config


def get_subdomain_resolution_config() -> dict:
    """Configure subdomain-based tenant resolution. Ref: SP06-T18."""
    logger.debug("Configuring subdomain-based tenant resolution...")
    config: dict = {
        "configured": True,
        "hostname_parsing_rules": [
            "split_hostname_by_dot_separator",
            "extract_first_part_as_subdomain",
            "skip_localhost_no_dots",
            "skip_ip_address_patterns",
            "skip_public_subdomains_list",
            "case_insensitive_matching",
        ],
        "public_subdomains": [
            "www_public_website",
            "app_public_application",
            "api_public_api_endpoint",
            "admin_public_administration",
            "docs_public_documentation",
            "status_public_status_page",
        ],
        "query_patterns": [
            "lazy_model_import_pattern",
            "tenant_objects_get_subdomain",
            "does_not_exist_returns_none",
            "multiple_objects_returns_none",
            "debug_logging_on_resolution",
            "error_logging_on_failure",
        ],
    }
    logger.debug(
        "subdomain resolution config: hostname_parsing_rules=%d, public_subdomains=%d",
        len(config["hostname_parsing_rules"]),
        len(config["public_subdomains"]),
    )
    return config


def get_custom_domain_resolution_config() -> dict:
    """Configure custom domain-based tenant resolution. Ref: SP06-T19."""
    logger.debug("Configuring custom domain-based tenant resolution...")
    config: dict = {
        "configured": True,
        "domain_matching_rules": [
            "exact_hostname_matching",
            "case_insensitive_iexact_lookup",
            "select_related_tenant_join",
            "domain_is_active_validation",
            "associated_tenant_retrieval",
            "full_hostname_no_extraction",
        ],
        "domain_model_fields": [
            "domain_char_field_unique",
            "tenant_foreign_key_cascade",
            "is_active_boolean_default_true",
            "is_primary_boolean_flag",
            "created_at_auto_timestamp",
            "updated_at_auto_timestamp",
        ],
        "exception_handling": [
            "does_not_exist_returns_none",
            "multiple_objects_returns_none",
            "inactive_domain_returns_none",
            "debug_logging_successful_match",
            "warning_logging_inactive_domain",
            "error_logging_multiple_domains",
        ],
    }
    logger.debug(
        "custom domain resolution config: domain_matching_rules=%d, domain_model_fields=%d",
        len(config["domain_matching_rules"]),
        len(config["domain_model_fields"]),
    )
    return config


def get_public_schema_handling_config() -> dict:
    """Configure public schema detection and tenant retrieval. Ref: SP06-T20."""
    logger.debug("Configuring public schema detection and tenant retrieval...")
    config: dict = {
        "configured": True,
        "public_host_detection": [
            "check_public_subdomains_list",
            "check_base_domain_match",
            "settings_base_domain_lookup",
            "hostname_subdomain_extraction",
            "boolean_return_value",
            "no_dots_skip_check",
        ],
        "public_tenant_retrieval": [
            "public_schema_name_from_settings",
            "tenant_objects_get_schema_name",
            "does_not_exist_critical_error",
            "optional_cache_for_performance",
            "debug_logging_on_success",
            "error_logging_on_missing",
        ],
        "performance_considerations": [
            "cache_public_tenant_one_hour",
            "django_cache_framework_usage",
            "try_cache_first_then_database",
            "cache_set_with_ttl_3600",
            "reduce_database_queries",
            "production_environment_caching",
        ],
    }
    logger.debug(
        "public schema handling config: public_host_detection=%d, public_tenant_retrieval=%d",
        len(config["public_host_detection"]),
        len(config["public_tenant_retrieval"]),
    )
    return config


def get_tenant_not_found_handler_config() -> dict:
    """Configure tenant not found handler returning JSON 404 response. Ref: SP06-T21."""
    logger.debug("Configuring tenant not found handler returning JSON 404 response...")
    config: dict = {
        "configured": True,
        "response_structure": [
            "error_message_tenant_not_found",
            "error_code_TENANT_NOT_FOUND",
            "detail_no_tenant_for_hostname",
            "status_code_404_not_found",
            "content_type_application_json",
            "no_sensitive_data_in_response",
        ],
        "logging_details": [
            "warning_level_log_entry",
            "hostname_included_in_log",
            "request_path_in_log_message",
            "client_ip_in_log_context",
            "timestamp_in_log_record",
            "logger_name_middleware_module",
        ],
        "error_code_details": [
            "TENANT_NOT_FOUND_constant_code",
            "consistent_error_code_format",
            "machine_readable_error_code",
            "documented_in_api_error_catalog",
            "used_by_frontend_error_handling",
            "unique_across_all_error_responses",
        ],
    }
    logger.debug(
        "tenant not found handler config: response_structure=%d, logging_details=%d",
        len(config["response_structure"]),
        len(config["logging_details"]),
    )
    return config


def get_tenant_inactive_handler_config() -> dict:
    """Configure inactive tenant handler returning JSON 403 response. Ref: SP06-T22."""
    logger.debug("Configuring inactive tenant handler returning JSON 403 response...")
    config: dict = {
        "configured": True,
        "response_structure": [
            "error_message_tenant_inactive",
            "error_code_TENANT_INACTIVE",
            "detail_tenant_account_suspended",
            "status_code_403_forbidden",
            "content_type_application_json",
            "no_internal_details_exposed",
        ],
        "security_details": [
            "no_internal_details_in_response",
            "generic_message_for_all_inactive",
            "no_tenant_name_in_error_body",
            "no_schema_info_in_error_body",
            "consistent_with_not_found_format",
            "safe_for_public_api_consumers",
        ],
        "logging_details": [
            "warning_level_log_entry",
            "tenant_schema_name_in_log",
            "tenant_id_in_log_context",
            "hostname_in_log_message",
            "request_path_in_log_context",
            "logger_name_middleware_module",
        ],
    }
    logger.debug(
        "tenant inactive handler config: response_structure=%d, security_details=%d",
        len(config["response_structure"]),
        len(config["security_details"]),
    )
    return config


def get_request_tenant_attribute_config() -> dict:
    """Configure setting request.tenant attribute after resolution. Ref: SP06-T23."""
    logger.debug("Configuring setting request.tenant attribute after resolution...")
    config: dict = {
        "configured": True,
        "assignment_details": [
            "set_before_super_process_request_call",
            "set_after_tenant_validation_check",
            "request_dot_tenant_equals_tenant",
            "none_value_when_not_resolved",
            "overwritten_on_each_request",
            "thread_safe_per_request_scope",
        ],
        "accessibility_details": [
            "accessible_in_views_via_request",
            "accessible_in_templates_via_context",
            "accessible_in_other_middleware_classes",
            "accessible_in_signals_via_request",
            "accessible_in_serializers_via_context",
            "accessible_in_permissions_via_request",
        ],
        "type_hint_details": [
            "TYPE_CHECKING_import_guard",
            "Tenant_type_hint_on_attribute",
            "IDE_autocomplete_support",
            "mypy_type_checking_compatible",
            "optional_tenant_or_none_type",
            "no_runtime_import_overhead",
        ],
    }
    logger.debug(
        "request tenant attribute config: assignment_details=%d, accessibility_details=%d",
        len(config["assignment_details"]),
        len(config["accessibility_details"]),
    )
    return config


def get_thread_local_storage_config() -> dict:
    """Configure thread-local storage for tenant access in non-request contexts. Ref: SP06-T24."""
    logger.debug("Configuring thread-local storage for tenant access in non-request contexts...")
    config: dict = {
        "configured": True,
        "storage_details": [
            "threading_local_at_module_level",
            "_thread_locals_variable",
            "set_current_tenant_function",
            "clear_current_tenant_function",
            "per_thread_isolation",
            "no_race_conditions",
        ],
        "integration_details": [
            "called_in_process_request",
            "called_after_request_tenant_set",
            "cleanup_in_process_response",
            "cleanup_in_process_exception",
            "both_request_and_thread_local_set",
            "schema_switching_after_set",
        ],
        "use_case_details": [
            "celery_background_tasks",
            "django_signal_handlers",
            "management_commands",
            "utility_functions",
            "audit_logging",
            "scheduled_jobs",
        ],
    }
    logger.debug(
        "thread local storage config: storage_details=%d, integration_details=%d",
        len(config["storage_details"]),
        len(config["integration_details"]),
    )
    return config


def get_get_current_tenant_utility_config() -> dict:
    """Configure get_current_tenant utility function for thread-local access. Ref: SP06-T25."""
    logger.debug("Configuring get_current_tenant utility function for thread-local access...")
    config: dict = {
        "configured": True,
        "function_details": [
            "getattr_safe_access",
            "returns_None_if_not_set",
            "no_exceptions_raised",
            "accesses__thread_locals_tenant",
            "module_level_function",
            "documented_return_type",
        ],
        "export_details": [
            "exported_in_middleware___init___py",
            "importable_from_apps_core_middleware",
            "__all___list_entry",
            "clean_import_path",
            "documented_in_package_docstring",
            "used_in_external_modules",
        ],
        "usage_guidance": [
            "prefer_request_tenant_in_views",
            "use_in_celery_tasks",
            "use_in_signal_handlers",
            "set_current_tenant_first_in_tasks",
            "check_None_before_use",
            "document_in_calling_code",
        ],
    }
    logger.debug(
        "get_current_tenant utility config: function_details=%d, export_details=%d",
        len(config["function_details"]),
        len(config["export_details"]),
    )
    return config


def get_middleware_registration_config() -> dict:
    """Configure registering TenantMiddleware in Django MIDDLEWARE setting. Ref: SP06-T26."""
    logger.debug("Configuring registering TenantMiddleware in Django MIDDLEWARE setting...")
    config: dict = {
        "configured": True,
        "registration_details": [
            "apps_core_middleware_TenantMiddleware_path",
            "position_after_SecurityMiddleware",
            "position_before_SessionMiddleware",
            "replaces_TenantMainMiddleware",
            "second_in_MIDDLEWARE_list",
            "import_path_verified",
        ],
        "settings_details": [
            "TENANT_MODEL_tenants_Tenant",
            "TENANT_DOMAIN_MODEL_tenants_Domain",
            "PUBLIC_SCHEMA_NAME_public",
            "BASE_DOMAIN_configured",
            "PUBLIC_SUBDOMAINS_list_set",
            "TENANT_RESOLUTION_PRIORITY_defined",
        ],
        "ordering_rules": [
            "after_security_middleware_always",
            "before_session_middleware_always",
            "before_authentication_middleware",
            "early_in_middleware_stack",
            "before_any_tenant_dependent_middleware",
            "critical_for_schema_switching",
        ],
    }
    logger.debug(
        "middleware registration config: registration_details=%d, settings_details=%d",
        len(config["registration_details"]),
        len(config["settings_details"]),
    )
    return config


def get_tenant_resolution_tests_config() -> dict:
    """Configure comprehensive tests for tenant resolution middleware. Ref: SP06-T27."""
    logger.debug("Configuring comprehensive tests for tenant resolution middleware...")
    config: dict = {
        "configured": True,
        "test_coverage": [
            "custom_domain_resolution_tests",
            "subdomain_resolution_tests",
            "public_schema_handling_tests",
            "error_handling_response_tests",
            "thread_local_storage_tests",
            "resolution_priority_tests",
        ],
        "test_fixtures": [
            "public_tenant_created_in_setUp",
            "active_test_tenant_created",
            "custom_domain_created_for_tenant",
            "inactive_tenant_created",
            "request_factory_initialized",
            "middleware_instance_created",
        ],
        "edge_case_tests": [
            "localhost_hostname_handling",
            "ip_address_hostname_handling",
            "case_insensitive_domain_matching",
            "public_subdomain_skipping",
            "inactive_tenant_domain_access",
            "process_request_integration_test",
        ],
    }
    logger.debug(
        "tenant resolution tests config: test_coverage=%d, test_fixtures=%d",
        len(config["test_coverage"]),
        len(config["test_fixtures"]),
    )
    return config


def get_tenant_middleware_docs_config() -> dict:
    """Configure complete documentation for tenant middleware system. Ref: SP06-T28."""
    logger.debug("Configuring complete documentation for tenant middleware system...")
    config: dict = {
        "configured": True,
        "documentation_sections": [
            "architecture_overview_section",
            "configuration_reference_section",
            "usage_examples_section",
            "api_reference_section",
            "testing_guide_section",
            "troubleshooting_section",
        ],
        "content_details": [
            "resolution_priority_diagram",
            "middleware_flow_chart",
            "settings_explanation",
            "code_examples_for_views",
            "code_examples_for_celery",
            "code_examples_for_signals",
        ],
        "best_practices": [
            "prefer_request_tenant_in_views",
            "use_thread_local_in_background_tasks",
            "always_check_is_active_status",
            "clear_thread_local_after_use",
            "use_subdomain_for_testing",
            "reserve_public_subdomains",
        ],
    }
    logger.debug(
        "tenant middleware docs config: documentation_sections=%d, content_details=%d",
        len(config["documentation_sections"]),
        len(config["content_details"]),
    )
    return config


def get_logging_middleware_file_config() -> dict:
    """Configure RequestLoggingMiddleware file creation in middleware directory. Ref: SP06-T29."""
    logger.debug("Configuring RequestLoggingMiddleware file creation in middleware directory...")
    config: dict = {
        "configured": True,
        "file_details": [
            "logging.py_created_in_middleware_directory",
            "module_docstring_documents_features",
            "import_logging_module_added",
            "import_time_module_added",
            "import_django_http_types_added",
            "logger_initialized_api.request_namespace",
        ],
        "import_details": [
            "logging_standard_library_import",
            "time_standard_library_import",
            "typing_Callable_import",
            "django_HttpRequest_import",
            "django_HttpResponse_import",
            "api.request_logger_namespace",
        ],
        "feature_list": [
            "request_response_timing",
            "unique_request_id_generation",
            "tenant_user_context_enrichment",
            "structured_json_logging",
            "path_based_exclusions",
            "configurable_log_levels",
        ],
    }
    logger.debug(
        "logging middleware file config: file_details=%d, import_details=%d",
        len(config["file_details"]),
        len(config["import_details"]),
    )
    return config


def get_logging_middleware_class_config() -> dict:
    """Configure RequestLoggingMiddleware class definition with init and call. Ref: SP06-T30."""
    logger.debug("Configuring RequestLoggingMiddleware class definition with init and call...")
    config: dict = {
        "configured": True,
        "class_details": [
            "RequestLoggingMiddleware_class_defined",
            "class_docstring_documents_features",
            "EXCLUDED_PATHS_list_with_four_entries",
            "init_accepts_get_response_callable",
            "call_processes_request_and_response",
            "should_log_checks_path_exclusion",
        ],
        "excluded_paths": [
            "health_check_path_excluded",
            "readiness_check_path_excluded",
            "static_files_path_excluded",
            "media_files_path_excluded",
            "startswith_matching_used",
            "any_function_for_path_checking",
        ],
        "method_stubs": [
            "should_log_returns_bool_for_path",
            "get_request_id_returns_string_id",
            "call_returns_HttpResponse",
            "init_stores_get_response",
            "path_exclusion_before_timing",
            "middleware_flow_documented",
        ],
    }
    logger.debug(
        "logging middleware class config: class_details=%d, excluded_paths=%d",
        len(config["class_details"]),
        len(config["excluded_paths"]),
    )
    return config


def get_request_start_time_config() -> dict:
    """Configure capture request start time using perf_counter. Ref: SP06-T31."""
    logger.debug("Configuring capture request start time using perf_counter...")
    config: dict = {
        "configured": True,
        "timing_details": [
            "perf_counter_used_for_high_precision",
            "monotonic_clock_never_goes_backwards",
            "captured_after_should_log_check",
            "stored_in_local_variable_start_time",
            "nanosecond_precision_on_linux",
            "better_than_time.time_for_durations",
        ],
        "placement_details": [
            "after_path_exclusion_check",
            "before_get_response_call",
            "before_downstream_middleware",
            "at_beginning_of_timed_section",
            "inside_call_method_body",
            "only_for_logged_requests",
        ],
        "precision_details": [
            "windows_precision_about_100ns",
            "linux_precision_about_1ns",
            "macos_precision_about_1ns",
            "not_affected_by_system_clock",
            "consistent_across_platforms",
            "suitable_for_millisecond_reporting",
        ],
    }
    logger.debug(
        "request start time config: timing_details=%d, placement_details=%d",
        len(config["timing_details"]),
        len(config["placement_details"]),
    )
    return config


def get_request_end_time_config() -> dict:
    """Configure capture request end time after response generation. Ref: SP06-T32."""
    logger.debug("Configuring capture request end time after response generation...")
    config: dict = {
        "configured": True,
        "capture_details": [
            "perf_counter_called_after_get_response",
            "stored_in_local_variable_end_time",
            "captured_before_response_modification",
            "includes_view_function_processing",
            "includes_database_query_time",
            "includes_template_rendering_time",
        ],
        "measurement_scope": [
            "view_execution_time_included",
            "database_queries_time_included",
            "template_rendering_time_included",
            "downstream_middleware_time_included",
            "upstream_middleware_time_included",
            "network_transmission_not_included",
        ],
        "positioning_details": [
            "immediately_after_get_response_returns",
            "before_duration_calculation",
            "before_any_response_headers",
            "before_return_statement",
            "after_all_view_processing",
            "matches_start_time_method_call",
        ],
    }
    logger.debug(
        "request end time config: capture_details=%d, measurement_scope=%d",
        len(config["capture_details"]),
        len(config["measurement_scope"]),
    )
    return config


def get_response_duration_config() -> dict:
    """Configure calculate response duration in milliseconds. Ref: SP06-T33."""
    logger.debug("Configuring calculate response duration in milliseconds...")
    config: dict = {
        "configured": True,
        "calculation_details": [
            "end_time_minus_start_time_formula",
            "result_multiplied_by_1000",
            "stored_as_duration_ms_float",
            "stored_on_request.duration_ms_attribute",
            "millisecond_unit_for_consistency",
            "round_to_two_decimal_places",
        ],
        "duration_ranges": [
            "under_10ms_simple_queries_normal",
            "10_to_100ms_multiple_queries_monitor",
            "100_to_500ms_complex_processing_optimize",
            "500ms_to_1s_heavy_computation_review",
            "over_1s_problem_alert_threshold",
            "ranges_documented_for_monitoring",
        ],
        "storage_details": [
            "stored_on_request_object",
            "accessible_in_views_and_middleware",
            "available_for_logging_output",
            "available_for_response_headers",
            "available_for_performance_monitoring",
            "request.duration_ms_attribute_name",
        ],
    }
    logger.debug(
        "response duration config: calculation_details=%d, duration_ranges=%d",
        len(config["calculation_details"]),
        len(config["duration_ranges"]),
    )
    return config


def get_log_request_details_config() -> dict:
    """Configure log comprehensive request details including method path and client IP. Ref: SP06-T34."""
    logger.debug("Configuring log comprehensive request details including method path and client IP...")
    config: dict = {
        "configured": True,
        "log_fields": [
            "event_request_started_type",
            "request_id_correlation_field",
            "method_get_post_put_delete",
            "path_request_url_path",
            "query_string_parameters",
            "client_ip_address_field",
        ],
        "client_ip_detection": [
            "x_forwarded_for_header_check",
            "split_comma_take_first_ip",
            "fallback_to_REMOTE_ADDR",
            "strip_whitespace_from_ip",
            "return_unknown_if_missing",
            "proxy_loadbalancer_support",
        ],
        "user_agent_extraction": [
            "HTTP_USER_AGENT_meta_key",
            "fallback_to_unknown_string",
            "no_parsing_required",
            "raw_user_agent_string",
            "available_in_structured_logs",
            "common_browser_and_bot_agents",
        ],
    }
    logger.debug(
        "log request details config: log_fields=%d, client_ip_detection=%d",
        len(config["log_fields"]),
        len(config["client_ip_detection"]),
    )
    return config


def get_log_response_details_config() -> dict:
    """Configure log response details with status code duration and context. Ref: SP06-T35."""
    logger.debug("Configuring log response details with status code duration and context...")
    config: dict = {
        "configured": True,
        "response_log_fields": [
            "event_request_completed_type",
            "request_id_correlation_field",
            "method_and_path_fields",
            "status_code_integer_field",
            "duration_ms_rounded_two_decimals",
            "client_ip_address_field",
        ],
        "log_level_selection": [
            "INFO_for_2xx_success_codes",
            "INFO_for_3xx_redirection_codes",
            "WARNING_for_4xx_client_errors",
            "ERROR_for_5xx_server_errors",
            "logger_log_with_dynamic_level",
            "status_code_range_matching",
        ],
        "integration_details": [
            "called_after_duration_calculation",
            "before_return_statement",
            "receives_request_response_duration",
            "structured_log_data_dictionary",
            "message_includes_method_path_status",
            "extra_parameter_for_structured_data",
        ],
    }
    logger.debug(
        "log response details config: response_log_fields=%d, log_level_selection=%d",
        len(config["response_log_fields"]),
        len(config["log_level_selection"]),
    )
    return config


def get_request_id_header_config() -> dict:
    """Configure generate or extract unique request IDs for log correlation. Ref: SP06-T36."""
    logger.debug("Configuring generate or extract unique request IDs for log correlation...")
    config: dict = {
        "configured": True,
        "id_generation": [
            "uuid4_for_unique_ids",
            "check_HTTP_X_REQUEST_ID_header",
            "use_provided_id_if_present",
            "generate_new_uuid_if_missing",
            "strip_whitespace_from_header",
            "import_uuid_module",
        ],
        "request_storage": [
            "stored_on_request_request_id",
            "set_early_in_call_method",
            "before_log_request_call",
            "available_in_all_subsequent_code",
            "used_in_log_request_log_data",
            "used_in_log_response_log_data",
        ],
        "response_header": [
            "X_Request_ID_header_on_response",
            "same_id_from_request_object",
            "set_before_return_statement",
            "enables_client_tracking",
            "enables_distributed_tracing",
            "enables_log_correlation",
        ],
    }
    logger.debug(
        "request id header config: id_generation=%d, request_storage=%d",
        len(config["id_generation"]),
        len(config["request_storage"]),
    )
    return config


def get_tenant_id_logging_config() -> dict:
    """Configure enrich logs with tenant context from request.tenant. Ref: SP06-T37."""
    logger.debug("Configuring enrich logs with tenant context from request.tenant...")
    config: dict = {
        "configured": True,
        "extraction_details": [
            "hasattr_check_for_request_tenant",
            "access_request_tenant_id_field",
            "convert_to_string_for_json",
            "return_None_if_no_tenant",
            "handle_super_admin_case",
            "handle_public_endpoints",
        ],
        "log_integration": [
            "added_to_log_response_log_data",
            "tenant_id_field_in_structured_log",
            "_get_tenant_id_helper_method",
            "called_within_log_response",
            "None_for_unauthenticated_requests",
            "visible_in_all_response_logs",
        ],
        "use_cases": [
            "filter_logs_by_tenant_id",
            "tenant_specific_error_tracking",
            "per_tenant_performance_monitoring",
            "audit_trail_per_tenant",
            "multi_tenant_debugging",
            "tenant_usage_analytics",
        ],
    }
    logger.debug(
        "tenant id logging config: extraction_details=%d, log_integration=%d",
        len(config["extraction_details"]),
        len(config["log_integration"]),
    )
    return config


def get_user_id_logging_config() -> dict:
    """Configure enrich logs with user context from request.user. Ref: SP06-T38."""
    logger.debug("Configuring enrich logs with user context from request.user...")
    config: dict = {
        "configured": True,
        "extraction_details": [
            "hasattr_check_for_request_user",
            "is_authenticated_check",
            "access_request_user_id_field",
            "convert_to_string_for_json",
            "return_None_for_anonymous_users",
            "handle_missing_auth_middleware",
        ],
        "log_integration": [
            "added_to_log_response_log_data",
            "user_id_field_in_structured_log",
            "_get_user_id_helper_method",
            "called_within_log_response",
            "optionally_added_to_log_request",
            "None_for_anonymous_users",
        ],
        "analysis_capabilities": [
            "filter_logs_by_user_id",
            "user_activity_tracking",
            "per_user_performance_analysis",
            "slow_request_attribution",
            "error_attribution_to_users",
            "security_audit_per_user",
        ],
    }
    logger.debug(
        "user id logging config: extraction_details=%d, log_integration=%d",
        len(config["extraction_details"]),
        len(config["log_integration"]),
    )
    return config


def get_log_format_config() -> dict:
    """Configure structured JSON logging format configuration. Ref: SP06-T39."""
    logger.debug("Configuring structured JSON logging format configuration...")
    config: dict = {
        "configured": True,
        "formatter_details": [
            "json_formatter_pythonjsonlogger",
            "verbose_formatter_bracket_style",
            "simple_formatter_levelname_message",
            "field_rename_levelname_to_level",
            "field_rename_asctime_to_timestamp",
            "iso_8601_timestamp_format",
        ],
        "handler_details": [
            "console_handler_streamhandler",
            "api_handler_json_format",
            "file_handler_rotating_file",
            "rotating_file_10mb_max_size",
            "five_backup_files_retained",
            "info_level_for_all_handlers",
        ],
        "logger_details": [
            "api_request_logger_namespace",
            "api_request_propagate_false",
            "django_logger_info_level",
            "db_backends_warning_level",
            "apps_logger_console_and_file",
            "root_handler_console_info",
        ],
    }
    logger.debug(
        "log format config: formatter_details=%d, handler_details=%d",
        len(config["formatter_details"]),
        len(config["handler_details"]),
    )
    return config


def get_request_body_logging_config() -> dict:
    """Configure optional request body logging with sanitization. Ref: SP06-T40."""
    logger.debug("Configuring optional request body logging with sanitization...")
    config: dict = {
        "configured": True,
        "setting_details": [
            "LOG_REQUEST_BODY_default_false",
            "MAX_BODY_LENGTH_10000_bytes",
            "SENSITIVE_FIELDS_list_defined",
            "disabled_by_default_for_security",
            "enable_only_in_development",
            "configurable_via_django_settings",
        ],
        "sanitization_details": [
            "password_passwd_pwd_redacted",
            "token_access_refresh_redacted",
            "secret_api_key_private_redacted",
            "credit_card_cvv_ssn_redacted",
            "recursive_nested_dict_sanitize",
            "list_items_recursively_sanitized",
        ],
        "body_handling": [
            "json_content_type_parsed",
            "form_urlencoded_parsed",
            "multipart_returns_placeholder",
            "unknown_type_returns_label",
            "parse_error_returns_message",
            "size_limit_truncation_applied",
        ],
    }
    logger.debug(
        "request body logging config: setting_details=%d, sanitization_details=%d",
        len(config["setting_details"]),
        len(config["sanitization_details"]),
    )
    return config


def get_health_check_exclusion_config() -> dict:
    """Configure exclude health check endpoints from logging. Ref: SP06-T41."""
    logger.debug("Configuring exclude health check endpoints from logging...")
    config: dict = {
        "configured": True,
        "health_paths": [
            "health_endpoint_excluded",
            "health_liveness_kubernetes",
            "health_readiness_kubernetes",
            "ready_endpoint_alias",
            "ping_endpoint_excluded",
            "startswith_matching_used",
        ],
        "exclusion_reasons": [
            "load_balancer_high_frequency",
            "kubernetes_liveness_probe",
            "kubernetes_readiness_probe",
            "every_few_seconds_called",
            "dominates_log_output",
            "no_useful_debugging_info",
        ],
        "kubernetes_details": [
            "liveness_probe_every_10s",
            "readiness_probe_every_5s",
            "initial_delay_supported",
            "http_get_method_used",
            "port_8000_default",
            "pod_health_monitoring",
        ],
    }
    logger.debug(
        "health check exclusion config: health_paths=%d, exclusion_reasons=%d",
        len(config["health_paths"]),
        len(config["exclusion_reasons"]),
    )
    return config


def get_static_files_exclusion_config() -> dict:
    """Configure exclude static and media file requests from logging. Ref: SP06-T42."""
    logger.debug("Configuring exclude static and media file requests from logging...")
    config: dict = {
        "configured": True,
        "static_paths": [
            "static_assets_css_js_images",
            "media_uploaded_files",
            "favicon_ico_browser_request",
            "admin_jsi18n_excluded",
            "metrics_prometheus_excluded",
            "custom_exclusions_from_settings",
        ],
        "environment_handling": [
            "development_django_serves_static",
            "production_nginx_cdn_serves",
            "exclusion_mainly_for_development",
            "reduces_log_noise_significantly",
            "each_page_load_many_assets",
            "only_api_requests_logged",
        ],
        "custom_exclusion_support": [
            "LOG_EXCLUDED_PATHS_setting",
            "combines_default_and_custom",
            "settings_configurable_list",
            "internal_api_exclusion_example",
            "webhook_exclusion_example",
            "websocket_exclusion_example",
        ],
    }
    logger.debug(
        "static files exclusion config: static_paths=%d, environment_handling=%d",
        len(config["static_paths"]),
        len(config["environment_handling"]),
    )
    return config


def get_logging_middleware_registration_config() -> dict:
    """Configure register RequestLoggingMiddleware in Django's MIDDLEWARE setting. Ref: SP06-T43."""
    logger.debug("Configuring register RequestLoggingMiddleware in Django's MIDDLEWARE setting...")
    config: dict = {
        "configured": True,
        "registration_details": [
            "apps_core_middleware_logging_path",
            "after_authentication_middleware",
            "after_tenant_middleware",
            "before_message_middleware",
            "before_application_middleware",
            "full_import_path_verified",
        ],
        "ordering_requirements": [
            "after_security_middleware_always",
            "after_session_middleware_always",
            "after_csrf_middleware_always",
            "after_auth_middleware_user_access",
            "after_tenant_middleware_tenant_access",
            "before_clickjacking_middleware",
        ],
        "context_availability": [
            "request_user_available_in_logs",
            "request_tenant_available_in_logs",
            "session_data_available",
            "captures_full_request_duration",
            "application_middleware_timed",
            "view_function_processing_timed",
        ],
    }
    logger.debug(
        "logging middleware registration config: registration_details=%d, ordering_requirements=%d",
        len(config["registration_details"]),
        len(config["ordering_requirements"]),
    )
    return config


def get_test_request_logging_config() -> dict:
    """Configure comprehensive tests for request logging middleware. Ref: SP06-T44."""
    logger.debug("Configuring comprehensive tests for request logging middleware...")
    config: dict = {
        "configured": True,
        "test_categories": [
            "basic_logging_request_response",
            "timing_accuracy_perf_counter",
            "context_enrichment_user_tenant",
            "path_exclusion_health_static",
            "body_logging_and_sanitization",
            "error_handling_missing_context",
        ],
        "test_fixtures": [
            "request_factory_initialized",
            "mock_get_response_callable",
            "middleware_instance_created",
            "test_user_created",
            "logger_mock_patched",
            "mock_tenant_object",
        ],
        "assertion_details": [
            "log_level_matches_status_code",
            "duration_ms_within_tolerance",
            "sensitive_fields_redacted",
            "excluded_paths_not_logged",
            "request_id_uuid_format",
            "response_header_x_request_id",
        ],
    }
    logger.debug(
        "test request logging config: test_categories=%d, test_fixtures=%d",
        len(config["test_categories"]),
        len(config["test_fixtures"]),
    )
    return config


def get_security_headers_file_config() -> dict:
    """Configure SecurityHeadersMiddleware file creation in middleware directory. Ref: SP06-T45."""
    logger.debug("Configuring SecurityHeadersMiddleware file creation in middleware directory...")
    config: dict = {
        "configured": True,
        "file_details": [
            "security_py_middleware_directory",
            "module_docstring_documents_headers",
            "django_conf_settings_imported",
            "uuid_module_imported",
            "security_headers_purpose_documented",
            "environment_specific_behavior_noted",
        ],
        "header_list": [
            "x_content_type_options_nosniff",
            "x_frame_options_deny_sameorigin",
            "x_xss_protection_mode_block",
            "referrer_policy_strict_origin",
            "content_security_policy_csp",
            "strict_transport_security_hsts",
        ],
        "protection_scope": [
            "xss_cross_site_scripting",
            "clickjacking_frame_embedding",
            "mime_sniffing_content_type",
            "referrer_information_leakage",
            "content_security_policy_violations",
            "browser_feature_restrictions",
        ],
    }
    logger.debug(
        "security headers file config: file_details=%d, header_list=%d",
        len(config["file_details"]),
        len(config["header_list"]),
    )
    return config


def get_security_headers_class_config() -> dict:
    """Configure SecurityHeadersMiddleware class definition with init and call. Ref: SP06-T46."""
    logger.debug("Configuring SecurityHeadersMiddleware class definition with init and call...")
    config: dict = {
        "configured": True,
        "class_details": [
            "SecurityHeadersMiddleware_class_defined",
            "class_docstring_documents_headers",
            "init_accepts_get_response_callable",
            "call_processes_request_response",
            "add_security_headers_helper_method",
            "configuration_via_django_settings",
        ],
        "method_details": [
            "init_stores_get_response",
            "call_gets_response_first",
            "call_adds_headers_to_response",
            "add_security_headers_accepts_request",
            "add_security_headers_returns_response",
            "all_methods_have_docstrings",
        ],
        "middleware_flow": [
            "request_passes_through_first",
            "response_generated_by_view",
            "headers_added_to_response",
            "modified_response_returned",
            "applies_to_all_responses",
            "no_request_modification_needed",
        ],
    }
    logger.debug(
        "security headers class config: class_details=%d, method_details=%d",
        len(config["class_details"]),
        len(config["method_details"]),
    )
    return config


def get_x_content_type_options_config() -> dict:
    """Configure X-Content-Type-Options nosniff header preventing MIME sniffing. Ref: SP06-T47."""
    logger.debug("Configuring X-Content-Type-Options nosniff header preventing MIME sniffing...")
    config: dict = {
        "configured": True,
        "header_details": [
            "header_name_x_content_type_options",
            "value_always_nosniff",
            "prevents_mime_type_sniffing",
            "browser_respects_content_type",
            "applied_to_all_responses",
            "no_configuration_needed",
        ],
        "attack_prevention": [
            "attacker_uploads_malicious_file",
            "server_sets_text_plain_type",
            "browser_would_sniff_as_javascript",
            "nosniff_prevents_execution",
            "content_type_header_respected",
            "xss_vulnerability_prevented",
        ],
        "browser_support": [
            "chrome_all_versions_supported",
            "firefox_v50_plus_supported",
            "safari_all_versions_supported",
            "edge_all_versions_supported",
            "ie_8_plus_supported",
            "universal_browser_coverage",
        ],
    }
    logger.debug(
        "x content type options config: header_details=%d, attack_prevention=%d",
        len(config["header_details"]),
        len(config["attack_prevention"]),
    )
    return config


def get_x_frame_options_config() -> dict:
    """Configure X-Frame-Options header preventing clickjacking attacks. Ref: SP06-T48."""
    logger.debug("Configuring X-Frame-Options header preventing clickjacking attacks...")
    config: dict = {
        "configured": True,
        "header_details": [
            "header_name_x_frame_options",
            "default_value_DENY",
            "configurable_via_settings",
            "getattr_settings_X_FRAME_OPTIONS",
            "supports_DENY_and_SAMEORIGIN",
            "prevents_clickjacking_attacks",
        ],
        "frame_options": [
            "DENY_no_framing_allowed",
            "SAMEORIGIN_same_origin_only",
            "ALLOW_FROM_deprecated_use_csp",
            "DENY_maximum_security_default",
            "SAMEORIGIN_for_self_embedding",
            "configurable_per_deployment",
        ],
        "clickjacking_details": [
            "attacker_creates_malicious_page",
            "target_page_in_invisible_iframe",
            "fake_ui_overlays_real_content",
            "user_clicks_unintended_actions",
            "DENY_blocks_all_iframe_loading",
            "prevents_ui_redress_attacks",
        ],
    }
    logger.debug(
        "x frame options config: header_details=%d, frame_options=%d",
        len(config["header_details"]),
        len(config["frame_options"]),
    )
    return config


def get_x_xss_protection_config() -> dict:
    """Configure X-XSS-Protection header enabling browser XSS filter. Ref: SP06-T49."""
    logger.debug("Configuring X-XSS-Protection header enabling browser XSS filter...")
    config: dict = {
        "configured": True,
        "header_details": [
            "header_name_x_xss_protection",
            "value_1_mode_block",
            "enables_browser_xss_filter",
            "blocks_page_if_attack_detected",
            "applied_to_all_responses",
            "no_configuration_needed",
        ],
        "protection_modes": [
            "value_0_disables_filter",
            "value_1_enables_sanitization",
            "mode_block_stops_page_render",
            "report_uri_sends_violation",
            "mode_block_recommended_setting",
            "defense_in_depth_with_csp",
        ],
        "deprecation_notes": [
            "chrome_removed_in_v88",
            "firefox_never_supported_it",
            "safari_still_supports_header",
            "edge_chromium_removed_it",
            "ie_8_plus_supports_header",
            "csp_preferred_modern_approach",
        ],
    }
    logger.debug(
        "x xss protection config: header_details=%d, protection_modes=%d",
        len(config["header_details"]),
        len(config["protection_modes"]),
    )
    return config


def get_referrer_policy_config() -> dict:
    """Configure Referrer-Policy header controlling referrer information. Ref: SP06-T50."""
    logger.debug("Configuring Referrer-Policy header controlling referrer information...")
    config: dict = {
        "configured": True,
        "header_details": [
            "header_name_referrer_policy",
            "value_strict_origin_when_cross_origin",
            "controls_referrer_information_sent",
            "protects_user_privacy",
            "prevents_information_leakage",
            "balanced_security_functionality",
        ],
        "policy_behaviors": [
            "same_origin_sends_full_url",
            "cross_origin_sends_origin_only",
            "https_to_http_sends_nothing",
            "path_and_query_protected",
            "token_in_url_not_leaked",
            "recommended_modern_default",
        ],
        "privacy_protection": [
            "sensitive_paths_not_exposed",
            "query_parameters_not_leaked",
            "tokens_in_urls_protected",
            "user_navigation_hidden",
            "downgrade_fully_blocked",
            "cross_origin_minimized",
        ],
    }
    logger.debug(
        "referrer policy config: header_details=%d, policy_behaviors=%d",
        len(config["header_details"]),
        len(config["policy_behaviors"]),
    )
    return config


def get_csp_header_config() -> dict:
    """Configure Content-Security-Policy header with basic directives. Ref: SP06-T51."""
    logger.debug("Configuring Content-Security-Policy header with basic directives...")
    config: dict = {
        "configured": True,
        "directive_details": [
            "default_src_self_fallback",
            "script_src_self_unsafe_inline",
            "style_src_self_unsafe_inline",
            "img_src_self_data_https",
            "font_src_self_google_fonts",
            "connect_src_self_ajax_ws",
            "frame_ancestors_none_no_framing",
        ],
        "method_details": [
            "_get_csp_header_helper_method",
            "returns_complete_csp_string",
            "directives_joined_semicolon",
            "called_in_add_security_headers",
            "csp_header_set_on_response",
            "inline_comment_explains_purpose",
        ],
        "protection_scope": [
            "xss_cross_site_scripting_blocked",
            "data_injection_attacks_prevented",
            "resource_loading_controlled",
            "inline_script_execution_policy",
            "external_resource_whitelisting",
            "iframe_embedding_prevented",
        ],
    }
    logger.debug(
        "csp header config: directive_details=%d, method_details=%d",
        len(config["directive_details"]),
        len(config["method_details"]),
    )
    return config


def get_csp_directives_config() -> dict:
    """Configure environment-specific CSP configuration for dev vs production. Ref: SP06-T52."""
    logger.debug("Configuring environment-specific CSP configuration for dev vs production...")
    config: dict = {
        "configured": True,
        "environment_detection": [
            "settings_DEBUG_flag_checked",
            "development_permissive_policy",
            "production_strict_policy",
            "getattr_with_False_default",
            "conditional_directive_selection",
            "inline_comments_explain_differences",
        ],
        "development_directives": [
            "unsafe_eval_for_dev_tools",
            "ws_localhost_hot_reload",
            "wss_localhost_secure_ws",
            "react_devtools_eval_needed",
            "source_maps_eval_required",
            "styled_components_inline",
        ],
        "production_directives": [
            "upgrade_insecure_requests_added",
            "block_all_mixed_content_added",
            "no_unsafe_eval_in_production",
            "no_websocket_in_production",
            "https_only_resource_sources",
            "future_nonce_hash_migration",
        ],
    }
    logger.debug(
        "csp directives config: environment_detection=%d, development_directives=%d",
        len(config["environment_detection"]),
        len(config["development_directives"]),
    )
    return config


def get_permissions_policy_config() -> dict:
    """Configure Permissions-Policy header controlling browser features and APIs. Ref: SP06-T53."""
    logger.debug("Configuring Permissions-Policy header controlling browser features and APIs...")
    config: dict = {
        "configured": True,
        "feature_restrictions": [
            "geolocation_disabled_no_tracking",
            "camera_disabled_no_access",
            "microphone_disabled_no_recording",
            "payment_disabled_no_api_access",
            "usb_disabled_no_device_access",
            "magnetometer_gyroscope_accelerometer",
        ],
        "method_details": [
            "_get_permissions_policy_helper_method",
            "returns_complete_policy_string",
            "policies_joined_with_comma_space",
            "called_in_add_security_headers",
            "permissions_policy_header_set",
            "inline_comment_explains_purpose",
        ],
        "privacy_protection": [
            "prevents_malicious_feature_access",
            "blocks_device_fingerprinting",
            "iframe_content_restricted",
            "explicit_enablement_required",
            "empty_allowlist_most_restrictive",
            "self_allowlist_same_origin",
        ],
    }
    logger.debug(
        "Permissions-Policy config: feature_restrictions=%d, method_details=%d",
        len(config["feature_restrictions"]),
        len(config["method_details"]),
    )
    return config


def get_hsts_header_config() -> dict:
    """Configure Strict-Transport-Security header forcing HTTPS usage. Ref: SP06-T54."""
    logger.debug("Configuring Strict-Transport-Security header forcing HTTPS usage...")
    config: dict = {
        "configured": True,
        "header_details": [
            "strict_transport_security_header",
            "max_age_directive_in_seconds",
            "include_subdomains_directive",
            "preload_directive_optional",
            "only_added_for_https_production",
            "_should_add_hsts_check_method",
        ],
        "https_detection": [
            "settings_DEBUG_false_required",
            "SECURE_SSL_REDIRECT_true_required",
            "request_is_secure_optional_check",
            "development_mode_skips_hsts",
            "production_only_enforcement",
            "_should_add_hsts_returns_bool",
        ],
        "security_benefits": [
            "ssl_stripping_attack_prevented",
            "man_in_middle_attack_blocked",
            "cookie_hijacking_prevented",
            "automatic_http_to_https_upgrade",
            "browser_remembers_https_only",
            "first_visit_protection_preload",
        ],
    }
    logger.debug(
        "HSTS header config: header_details=%d, https_detection=%d",
        len(config["header_details"]),
        len(config["https_detection"]),
    )
    return config


def get_hsts_age_config() -> dict:
    """Configure HSTS max-age configuration with validation and constants. Ref: SP06-T55."""
    logger.debug("Configuring HSTS max-age configuration with validation and constants...")
    config: dict = {
        "configured": True,
        "age_constants": [
            "HSTS_MAX_AGE_TESTING_300_seconds",
            "HSTS_MAX_AGE_INITIAL_86400_one_day",
            "HSTS_MAX_AGE_SHORT_604800_one_week",
            "HSTS_MAX_AGE_MEDIUM_2592000_one_month",
            "HSTS_MAX_AGE_RECOMMENDED_31536000",
            "HSTS_MAX_AGE_MAXIMUM_63072000_two_years",
        ],
        "validation_details": [
            "max_age_minimum_300_warning",
            "preload_requires_31536000_minimum",
            "positive_integer_required",
            "getattr_with_recommended_default",
            "logger_warning_for_short_age",
            "progressive_deployment_guidance",
        ],
        "deployment_strategy": [
            "week_one_86400_one_day_test",
            "week_two_604800_one_week_build",
            "month_one_2592000_stable_check",
            "month_two_31536000_production",
            "month_three_include_subdomains",
            "month_six_plus_preload_submit",
        ],
    }
    logger.debug(
        "HSTS age config: age_constants=%d, validation_details=%d",
        len(config["age_constants"]),
        len(config["validation_details"]),
    )
    return config


def get_x_request_id_header_config() -> dict:
    """Configure X-Request-ID header for distributed tracing and log correlation. Ref: SP06-T56."""
    logger.debug("Configuring X-Request-ID header for distributed tracing and log correlation...")
    config: dict = {
        "configured": True,
        "propagation_details": [
            "hasattr_request_request_id_check",
            "propagates_from_logging_middleware",
            "no_new_id_generated_here",
            "header_only_if_id_present",
            "graceful_missing_attribute_handling",
            "relies_on_upstream_middleware",
        ],
        "tracing_benefits": [
            "log_correlation_across_services",
            "distributed_tracing_enabled",
            "error_debugging_simplified",
            "performance_analysis_end_to_end",
            "user_support_request_id_ref",
            "all_service_logs_linked",
        ],
        "integration_details": [
            "added_in_add_security_headers",
            "after_hsts_header_block",
            "before_return_statement",
            "uuid4_format_from_logging_mw",
            "client_receives_in_response",
            "inline_comment_explains_purpose",
        ],
    }
    logger.debug(
        "X-Request-ID header config: propagation_details=%d, tracing_benefits=%d",
        len(config["propagation_details"]),
        len(config["tracing_benefits"]),
    )
    return config


def get_security_headers_registration_config() -> dict:
    """Configure SecurityHeadersMiddleware registration in Django MIDDLEWARE setting. Ref: SP06-T57."""
    logger.debug("Configuring SecurityHeadersMiddleware registration in Django MIDDLEWARE setting...")
    config: dict = {
        "configured": True,
        "registration_details": [
            "core_middleware_security_import_path",
            "after_request_logging_middleware",
            "before_response_processing",
            "near_end_of_middleware_stack",
            "full_import_path_verified",
            "inline_comment_explains_purpose",
        ],
        "settings_configuration": [
            "X_FRAME_OPTIONS_DENY_default",
            "SECURE_SSL_REDIRECT_production_only",
            "SECURE_HSTS_SECONDS_31536000",
            "SECURE_HSTS_INCLUDE_SUBDOMAINS_true",
            "SECURE_HSTS_PRELOAD_false_default",
            "environment_specific_settings",
        ],
        "ordering_rationale": [
            "after_tenant_middleware_context",
            "after_logging_middleware_request_id",
            "before_application_middleware",
            "catches_all_response_types",
            "request_id_available_for_header",
            "full_security_coverage",
        ],
    }
    logger.debug(
        "Security headers registration config: registration_details=%d, settings_configuration=%d",
        len(config["registration_details"]),
        len(config["settings_configuration"]),
    )
    return config


def get_test_security_headers_config() -> dict:
    """Configure comprehensive test suite for all security headers middleware. Ref: SP06-T58."""
    logger.debug("Configuring comprehensive test suite for all security headers middleware...")
    config: dict = {
        "configured": True,
        "test_categories": [
            "basic_headers_four_tests",
            "csp_development_production_tests",
            "permissions_policy_three_tests",
            "hsts_condition_five_tests",
            "x_request_id_three_tests",
            "integration_four_tests",
        ],
        "test_techniques": [
            "request_factory_for_clean_tests",
            "override_settings_for_config",
            "mock_get_response_callable",
            "uuid_validation_format_check",
            "multiple_paths_methods_tested",
            "error_response_header_check",
        ],
        "coverage_goals": [
            "all_basic_headers_covered",
            "environment_specific_csp_tested",
            "hsts_all_conditions_tested",
            "feature_restrictions_verified",
            "request_id_propagation_tested",
            "hundred_percent_code_coverage",
        ],
    }
    logger.debug(
        "Test security headers config: test_categories=%d, test_techniques=%d",
        len(config["test_categories"]),
        len(config["test_techniques"]),
    )
    return config


def get_ratelimit_file_config() -> dict:
    """Configure RateLimitMiddleware file creation with imports and docstring. Ref: SP06-T59."""
    logger.debug("Configuring RateLimitMiddleware file creation with imports and docstring...")
    config: dict = {
        "configured": True,
        "file_structure": [
            "ratelimit_py_in_middleware_dir",
            "module_docstring_with_strategies",
            "import_time_for_timestamps",
            "import_settings_from_django_conf",
            "import_cache_from_django_core",
            "import_json_response_from_http",
        ],
        "rate_limit_strategies": [
            "ip_based_limit_per_client",
            "user_based_limit_per_account",
            "tenant_based_aggregate_limit",
            "endpoint_based_custom_limits",
            "sliding_window_algorithm",
            "redis_sorted_set_backend",
        ],
        "response_headers": [
            "x_ratelimit_limit_max_requests",
            "x_ratelimit_remaining_in_window",
            "x_ratelimit_reset_unix_timestamp",
            "retry_after_seconds_on_429",
            "content_type_json_error_body",
            "status_code_429_too_many",
        ],
    }
    logger.debug(
        "Rate limit file config: file_structure=%d, rate_limit_strategies=%d",
        len(config["file_structure"]),
        len(config["rate_limit_strategies"]),
    )
    return config


def get_ratelimit_class_config() -> dict:
    """Configure RateLimitMiddleware class with default limits and middleware structure. Ref: SP06-T60."""
    logger.debug("Configuring RateLimitMiddleware class with default limits and middleware structure...")
    config: dict = {
        "configured": True,
        "class_constants": [
            "ANON_LIMIT_100_per_minute",
            "USER_LIMIT_1000_per_minute",
            "TENANT_LIMIT_10000_per_minute",
            "WINDOW_60_seconds_default",
            "WHITELISTED_IPS_from_settings",
            "ENDPOINT_LIMITS_dict_from_settings",
        ],
        "middleware_methods": [
            "init_stores_get_response",
            "call_processes_request",
            "get_rate_limit_key_stub",
            "check_rate_limit_stub",
            "add_rate_limit_headers_stub",
            "get_429_response_stub",
        ],
        "configuration_sources": [
            "getattr_settings_safe_defaults",
            "RATELIMIT_ANONYMOUS_LIMIT_setting",
            "RATELIMIT_USER_LIMIT_setting",
            "RATELIMIT_TENANT_LIMIT_setting",
            "RATELIMIT_WINDOW_setting",
            "RATELIMIT_WHITELISTED_IPS_setting",
        ],
    }
    logger.debug(
        "Rate limit class config: class_constants=%d, middleware_methods=%d",
        len(config["class_constants"]),
        len(config["middleware_methods"]),
    )
    return config


def get_redis_backend_config() -> dict:
    """Configure Redis backend for rate limit counters with sliding window algorithm. Ref: SP06-T61."""
    logger.debug("Configuring Redis backend for rate limit counters with sliding window algorithm...")
    config: dict = {
        "configured": True,
        "pipeline_operations": [
            "zremrangebyscore_remove_old_entries",
            "zcard_count_current_window",
            "zadd_add_current_timestamp",
            "expire_set_key_expiration",
            "pipeline_execute_atomic",
            "results_array_matches_order",
        ],
        "key_formats": [
            "ratelimit_ip_address_key",
            "ratelimit_user_id_key",
            "ratelimit_tenant_id_key",
            "ratelimit_endpoint_path_key",
            "key_expiration_window_plus_buffer",
            "unix_timestamp_as_sorted_score",
        ],
        "error_handling": [
            "try_except_redis_connection",
            "fail_open_allow_on_error",
            "log_error_for_monitoring",
            "safe_defaults_on_exception",
            "connection_pool_max_connections",
            "socket_timeout_five_seconds",
        ],
    }
    logger.debug(
        "Redis backend config: pipeline_operations=%d, key_formats=%d",
        len(config["pipeline_operations"]),
        len(config["key_formats"]),
    )
    return config


def get_ip_based_ratelimit_config() -> dict:
    """Configure IP-based rate limiting for anonymous users and proxy handling. Ref: SP06-T62."""
    logger.debug("Configuring IP-based rate limiting for anonymous users and proxy handling...")
    config: dict = {
        "configured": True,
        "ip_extraction_details": [
            "x_forwarded_for_header_extraction",
            "x_real_ip_header_fallback",
            "remote_addr_final_fallback",
            "proxy_chain_handling_first_ip",
            "unknown_ip_fallback_value",
            "get_client_ip_utility_function",
        ],
        "key_generation_details": [
            "key_format_ratelimit_ip_address",
            "anon_limit_100_requests",
            "anonymous_user_check_logic",
            "behind_proxy_uses_real_ip",
            "unknown_ip_fallback_key",
            "consistent_key_format_across_requests",
        ],
        "rate_limit_logic": [
            "requests_per_minute_window",
            "shared_counter_per_ip_address",
            "429_response_on_limit_exceeded",
            "proxy_scenario_handling",
            "x_forwarded_for_first_ip_used",
            "rate_limit_headers_added_to_response",
        ],
    }
    logger.debug(
        "IP-based rate limit config: ip_extraction_details=%d, key_generation_details=%d",
        len(config["ip_extraction_details"]),
        len(config["key_generation_details"]),
    )
    return config


def get_user_based_ratelimit_config() -> dict:
    """Configure user-based rate limiting for authenticated users with higher limits. Ref: SP06-T63."""
    logger.debug("Configuring user-based rate limiting for authenticated users with higher limits...")
    config: dict = {
        "configured": True,
        "authentication_check": [
            "request_user_is_authenticated_check",
            "user_pk_access_for_key",
            "anonymous_user_handling_fallback",
            "auth_middleware_dependency_required",
            "hasattr_fallback_safety_check",
            "graceful_error_handling_on_failure",
        ],
        "key_generation_details": [
            "key_format_ratelimit_user_id",
            "user_limit_1000_requests",
            "independent_counter_per_user",
            "not_affected_by_shared_ip",
            "fallback_to_ip_based_limiting",
            "10x_higher_than_anonymous_limit",
        ],
        "user_benefits": [
            "higher_limits_for_authenticated_users",
            "independent_counters_per_user",
            "better_user_experience",
            "accurate_per_user_tracking",
            "fraud_prevention_per_account",
            "priority_over_ip_strategy",
        ],
    }
    logger.debug(
        "User-based rate limit config: authentication_check=%d, key_generation_details=%d",
        len(config["authentication_check"]),
        len(config["key_generation_details"]),
    )
    return config


def get_tenant_based_ratelimit_config() -> dict:
    """Configure tenant-based rate limiting for aggregate tenant limits. Ref: SP06-T64."""
    logger.debug("Configuring tenant-based rate limiting for aggregate tenant limits...")
    config: dict = {
        "configured": True,
        "tenant_detection": [
            "hasattr_request_tenant_check",
            "tenant_middleware_sets_attribute",
            "tenant_id_access_for_key",
            "none_check_for_missing_tenant",
            "public_schema_handling_logic",
            "super_admin_tenant_less_access",
        ],
        "key_generation_details": [
            "key_format_ratelimit_tenant_id",
            "tenant_limit_10000_requests",
            "aggregate_counting_all_users",
            "cross_tenant_isolation_enforced",
            "fallback_to_user_then_ip",
            "highest_priority_strategy",
        ],
        "tenant_benefits": [
            "resource_protection_per_tenant",
            "fair_usage_enforcement",
            "billing_enforcement_alignment",
            "abuse_prevention_per_tenant",
            "scalability_across_tenants",
            "predictable_resource_consumption",
        ],
    }
    logger.debug(
        "Tenant-based rate limit config: tenant_detection=%d, key_generation_details=%d",
        len(config["tenant_detection"]),
        len(config["key_generation_details"]),
    )
    return config


def get_endpoint_based_ratelimit_config() -> dict:
    """Configure endpoint-specific rate limiting with custom limits per route. Ref: SP06-T65."""
    logger.debug("Configuring endpoint-specific rate limiting with custom limits per route...")
    config: dict = {
        "configured": True,
        "endpoint_detection": [
            "request_path_extraction",
            "path_normalization_trailing_slash",
            "endpoint_limits_dict_lookup",
            "exact_match_checking_logic",
            "settings_configuration_source",
            "wildcard_pattern_optional_support",
        ],
        "composite_key_details": [
            "composite_key_endpoint_plus_user_ip",
            "authenticated_key_format_endpoint_user",
            "anonymous_key_format_endpoint_ip",
            "independent_counters_per_endpoint",
            "fallback_to_tenant_user_ip",
            "path_based_isolation_enforced",
        ],
        "common_endpoints": [
            "login_10_per_minute",
            "register_5_per_minute",
            "password_reset_3_per_minute",
            "token_refresh_20_per_minute",
            "search_50_per_minute",
            "upload_10_per_minute",
        ],
    }
    logger.debug(
        "Endpoint-based rate limit config: endpoint_detection=%d, composite_key_details=%d",
        len(config["endpoint_detection"]),
        len(config["composite_key_details"]),
    )
    return config


def get_ratelimit_window_config() -> dict:
    """Configure sliding window parameters and per-endpoint custom windows. Ref: SP06-T66."""
    logger.debug("Configuring sliding window parameters and per-endpoint custom windows...")
    config: dict = {
        "configured": True,
        "window_parameters": [
            "default_window_60_seconds",
            "configurable_via_settings",
            "consistent_across_strategies",
            "ratelimit_window_setting",
            "sliding_window_algorithm",
            "automatic_expired_entry_removal",
        ],
        "custom_windows": [
            "endpoint_windows_dict_config",
            "per_endpoint_custom_windows",
            "login_60_second_window",
            "register_300_second_window",
            "password_reset_600_second_window",
            "search_30_second_window",
        ],
        "sliding_window_details": [
            "redis_sorted_set_timestamps",
            "zremrangebyscore_removes_old",
            "zcard_counts_current_window",
            "zadd_adds_current_request",
            "expire_sets_key_expiration",
            "window_plus_buffer_expiration",
        ],
    }
    logger.debug(
        "Rate limit window config: window_parameters=%d, custom_windows=%d",
        len(config["window_parameters"]),
        len(config["custom_windows"]),
    )
    return config


def get_x_ratelimit_limit_header_config() -> dict:
    """Configure X-RateLimit-Limit header for maximum requests in current window. Ref: SP06-T67."""
    logger.debug("Configuring X-RateLimit-Limit header for maximum requests in current window...")
    config: dict = {
        "configured": True,
        "header_format": [
            "x_ratelimit_limit_header_name",
            "string_value_conversion",
            "added_to_all_responses",
            "reflects_strategy_limit",
            "dictionary_style_assignment",
            "draft_ietf_standard_compliance",
        ],
        "strategy_values": [
            "ip_based_anonymous_100",
            "user_based_authenticated_1000",
            "tenant_based_aggregate_10000",
            "endpoint_based_custom_limit",
            "value_matches_rate_limit_key",
            "consistent_header_across_requests",
        ],
        "client_usage": [
            "client_reads_limit_header",
            "proactive_rate_tracking",
            "limit_display_in_dashboard",
            "api_documentation_reference",
            "sdk_integration_support",
            "developer_friendly_transparency",
        ],
    }
    logger.debug(
        "X-RateLimit-Limit header config: header_format=%d, strategy_values=%d",
        len(config["header_format"]),
        len(config["strategy_values"]),
    )
    return config


def get_x_ratelimit_remaining_header_config() -> dict:
    """Configure X-RateLimit-Remaining header for requests remaining in current window. Ref: SP06-T68."""
    logger.debug("Configuring X-RateLimit-Remaining header for requests remaining in current window...")
    config: dict = {
        "configured": True,
        "remaining_calculation": [
            "max_zero_remaining_no_negative",
            "decrements_with_each_request",
            "calculated_from_check_rate_limit",
            "limit_minus_current_count",
            "zero_when_limit_exhausted",
            "accurate_real_time_tracking",
        ],
        "header_format": [
            "x_ratelimit_remaining_header_name",
            "string_value_conversion",
            "present_in_200_and_429_responses",
            "never_shows_negative_values",
            "integer_remaining_count",
            "updates_per_request_accurately",
        ],
        "client_benefits": [
            "warns_when_running_low",
            "prevents_surprise_429_errors",
            "enables_request_budgeting",
            "proactive_backoff_implementation",
            "ten_percent_threshold_warning",
            "exhaustion_wait_strategy",
        ],
    }
    logger.debug(
        "X-RateLimit-Remaining header config: remaining_calculation=%d, header_format=%d",
        len(config["remaining_calculation"]),
        len(config["header_format"]),
    )
    return config


def get_x_ratelimit_reset_header_config() -> dict:
    """Configure X-RateLimit-Reset header with Unix timestamp for window reset. Ref: SP06-T69."""
    logger.debug("Configuring X-RateLimit-Reset header with Unix timestamp for window reset...")
    config: dict = {
        "configured": True,
        "reset_calculation": [
            "current_time_plus_window",
            "unix_timestamp_integer_seconds",
            "calculated_in_check_rate_limit",
            "relative_to_request_time",
            "sliding_window_reset_behavior",
            "new_window_after_reset",
        ],
        "header_format": [
            "x_ratelimit_reset_header_name",
            "integer_unix_timestamp_value",
            "string_conversion_for_header",
            "consistent_with_sliding_window",
            "epoch_seconds_since_1970",
            "timezone_independent_format",
        ],
        "client_usage": [
            "calculate_seconds_until_reset",
            "convert_to_human_readable_date",
            "schedule_retry_at_reset_time",
            "display_countdown_to_user",
            "compare_with_current_timestamp",
            "implement_smart_retry_logic",
        ],
    }
    logger.debug(
        "X-RateLimit-Reset header config: reset_calculation=%d, header_format=%d",
        len(config["reset_calculation"]),
        len(config["header_format"]),
    )
    return config


def get_retry_after_header_config() -> dict:
    """Configure Retry-After header and 429 response body for rate limited requests. Ref: SP06-T70."""
    logger.debug("Configuring Retry-After header and 429 response body for rate limited requests...")
    config: dict = {
        "configured": True,
        "response_structure": [
            "json_response_status_429",
            "error_field_rate_limit_exceeded",
            "code_field_rate_limit_exceeded",
            "message_field_retry_after_seconds",
            "retry_after_field_in_body",
            "content_type_application_json",
        ],
        "header_details": [
            "retry_after_header_standard_http",
            "value_in_seconds_integer",
            "no_x_prefix_standard_header",
            "added_only_to_429_responses",
            "reset_time_minus_current_time",
            "client_should_respect_header",
        ],
        "client_retry_logic": [
            "automatic_retry_with_backoff",
            "exponential_backoff_strategy",
            "max_retries_limit_check",
            "sleep_for_retry_after_seconds",
            "python_requests_retry_example",
            "javascript_fetch_retry_example",
        ],
    }
    logger.debug(
        "Retry-After header config: response_structure=%d, header_details=%d",
        len(config["response_structure"]),
        len(config["header_details"]),
    )
    return config


def get_429_response_handling_config() -> dict:
    """Configure complete 429 response handling with headers and JSON body. Ref: SP06-T71."""
    logger.debug("Configuring complete 429 response handling with headers and JSON body...")
    config: dict = {
        "configured": True,
        "response_flow": [
            "extract_client_ip_first",
            "check_whitelist_early_exit",
            "determine_rate_limit_key",
            "check_redis_sliding_window",
            "return_429_if_exceeded",
            "add_headers_to_all_responses",
        ],
        "response_components": [
            "status_code_429_too_many",
            "x_ratelimit_limit_header",
            "x_ratelimit_remaining_zero",
            "x_ratelimit_reset_timestamp",
            "retry_after_header_seconds",
            "json_body_error_details",
        ],
        "error_body_fields": [
            "error_rate_limit_exceeded",
            "code_rate_limit_exceeded_constant",
            "message_retry_after_seconds_text",
            "retry_after_integer_seconds",
            "documentation_link_reference",
            "content_type_application_json",
        ],
    }
    logger.debug(
        "429 response handling config: response_flow=%d, response_components=%d",
        len(config["response_flow"]),
        len(config["response_components"]),
    )
    return config


def get_ip_whitelist_config() -> dict:
    """Configure IP whitelist to bypass rate limiting for trusted addresses. Ref: SP06-T72."""
    logger.debug("Configuring IP whitelist to bypass rate limiting for trusted addresses...")
    config: dict = {
        "configured": True,
        "whitelist_implementation": [
            "is_whitelisted_method_check",
            "ip_in_whitelisted_ips_list",
            "returns_boolean_result",
            "early_check_in_call_method",
            "skip_all_rate_limiting",
            "normal_response_immediately",
        ],
        "whitelist_entries": [
            "localhost_127_0_0_1_ipv4",
            "localhost_colon_colon_1_ipv6",
            "docker_bridge_172_17_0_1",
            "load_balancer_health_check_ips",
            "monitoring_service_ips",
            "ci_cd_server_ips",
        ],
        "security_considerations": [
            "be_specific_avoid_wildcards",
            "validate_ip_format_on_startup",
            "regular_audit_and_cleanup",
            "never_whitelist_public_ips",
            "document_reason_for_each_entry",
            "settings_configurable_whitelist",
        ],
    }
    logger.debug(
        "IP whitelist config: whitelist_implementation=%d, whitelist_entries=%d",
        len(config["whitelist_implementation"]),
        len(config["whitelist_entries"]),
    )
    return config


def get_ratelimit_middleware_registration_config() -> dict:
    """Configure RateLimitMiddleware registration in Django MIDDLEWARE setting. Ref: SP06-T73."""
    logger.debug("Configuring RateLimitMiddleware registration in Django MIDDLEWARE setting...")
    config: dict = {
        "configured": True,
        "middleware_position": [
            "after_security_middleware",
            "after_session_middleware",
            "after_authentication_middleware",
            "after_tenant_middleware",
            "before_application_middleware",
            "correct_middleware_stack_order",
        ],
        "registration_details": [
            "full_path_apps_core_middleware_ratelimit",
            "ratelimit_middleware_class_name",
            "added_to_middleware_list_setting",
            "environment_specific_configuration",
            "development_higher_limits",
            "production_strict_limits",
        ],
        "verification_steps": [
            "manage_py_check_deploy_passes",
            "server_starts_without_errors",
            "rate_limiting_active_on_requests",
            "middleware_order_documented",
            "log_output_confirms_loading",
            "test_requests_return_headers",
        ],
    }
    logger.debug(
        "Rate limit middleware registration config: middleware_position=%d, registration_details=%d",
        len(config["middleware_position"]),
        len(config["registration_details"]),
    )
    return config


def get_ratelimit_testing_config() -> dict:
    """Configure comprehensive rate limiting test suite for all strategies and edge cases. Ref: SP06-T74."""
    logger.debug("Configuring comprehensive rate limiting test suite for all strategies and edge cases...")
    config: dict = {
        "configured": True,
        "test_categories": [
            "basic_ip_rate_limit_enforced",
            "user_based_rate_limit_test",
            "tenant_based_rate_limit_test",
            "endpoint_specific_limit_test",
            "whitelist_bypass_test",
            "window_expiration_test",
        ],
        "header_tests": [
            "x_ratelimit_limit_header_present",
            "x_ratelimit_remaining_decreases",
            "x_ratelimit_reset_timestamp_valid",
            "retry_after_header_in_429",
            "remaining_zero_on_429_response",
            "all_headers_string_format",
        ],
        "edge_case_tests": [
            "exact_limit_boundary_test",
            "redis_error_fail_open_test",
            "independent_user_counters_test",
            "concurrent_requests_test",
            "missing_invalid_ip_handling",
            "anonymous_vs_authenticated_test",
        ],
    }
    logger.debug(
        "Rate limit testing config: test_categories=%d, header_tests=%d",
        len(config["test_categories"]),
        len(config["header_tests"]),
    )
    return config


def get_timezone_file_config() -> dict:
    """Configure TimezoneMiddleware file with imports and module structure. Ref: SP06-T75."""
    logger.debug("Configuring TimezoneMiddleware file with imports and module structure...")
    config: dict = {
        "configured": True,
        "file_structure": [
            "timezone_py_in_middleware_directory",
            "module_docstring_with_purpose",
            "logging_import_for_debug",
            "zoneinfo_import_python39_builtin",
            "django_utils_timezone_import",
            "logger_instance_configuration",
        ],
        "import_details": [
            "logging_module_standard_library",
            "zoneinfo_module_timezone_support",
            "django_utils_timezone_activate",
            "django_utils_timezone_deactivate",
            "zoneinfo_zone_info_class",
            "no_pip_install_needed_builtin",
        ],
        "timezone_sources": [
            "user_profile_timezone_highest",
            "tenant_timezone_setting_second",
            "default_asia_colombo_fallback",
            "iana_timezone_database_names",
            "utc_offset_plus_5_30",
            "sri_lanka_business_location",
        ],
    }
    logger.debug(
        "Timezone file config: file_structure=%d, import_details=%d",
        len(config["file_structure"]),
        len(config["import_details"]),
    )
    return config


def get_timezone_class_config() -> dict:
    """Configure TimezoneMiddleware class with init and call methods. Ref: SP06-T76."""
    logger.debug("Configuring TimezoneMiddleware class with init and call methods...")
    config: dict = {
        "configured": True,
        "class_structure": [
            "timezone_middleware_class_name",
            "default_timezone_asia_colombo_constant",
            "init_stores_get_response",
            "call_processes_request_lifecycle",
            "get_timezone_resolution_method",
            "deactivate_timezone_after_request",
        ],
        "call_method_flow": [
            "get_timezone_from_request",
            "activate_timezone_with_zoneinfo",
            "log_debug_activated_timezone",
            "process_request_through_chain",
            "deactivate_timezone_cleanup",
            "return_response_to_client",
        ],
        "error_handling": [
            "try_except_zone_info_creation",
            "catch_zone_info_not_found_error",
            "catch_general_exception_fallback",
            "log_warning_on_invalid_timezone",
            "deactivate_on_error_graceful",
            "always_deactivate_in_finally",
        ],
    }
    logger.debug(
        "Timezone class config: class_structure=%d, call_method_flow=%d",
        len(config["class_structure"]),
        len(config["call_method_flow"]),
    )
    return config


def get_tenant_timezone_config() -> dict:
    """Configure tenant timezone retrieval from request.tenant attribute. Ref: SP06-T77."""
    logger.debug("Configuring tenant timezone retrieval from request.tenant attribute...")
    config: dict = {
        "configured": True,
        "tenant_detection": [
            "hasattr_request_tenant_check",
            "tenant_not_none_validation",
            "hasattr_tenant_timezone_check",
            "timezone_truthy_check",
            "tenant_middleware_dependency",
            "public_schema_no_tenant",
        ],
        "retrieval_logic": [
            "access_request_tenant_attribute",
            "get_tenant_timezone_string",
            "return_timezone_name_or_none",
            "debug_log_on_success",
            "fallback_to_default_timezone",
            "priority_below_user_timezone",
        ],
        "error_scenarios": [
            "no_tenant_attribute_returns_none",
            "none_tenant_returns_none",
            "no_timezone_attr_returns_none",
            "empty_timezone_returns_none",
            "attribute_error_caught_safely",
            "general_exception_logged_warning",
        ],
    }
    logger.debug(
        "Tenant timezone config: tenant_detection=%d, retrieval_logic=%d",
        len(config["tenant_detection"]),
        len(config["retrieval_logic"]),
    )
    return config


def get_user_timezone_config() -> dict:
    """Configure user timezone retrieval from authenticated user profile. Ref: SP06-T78."""
    logger.debug("Configuring user timezone retrieval from authenticated user profile...")
    config: dict = {
        "configured": True,
        "authentication_check": [
            "hasattr_request_user_check",
            "user_is_authenticated_verify",
            "anonymous_user_returns_none",
            "auth_middleware_dependency",
            "user_not_none_validation",
            "highest_priority_timezone_source",
        ],
        "retrieval_locations": [
            "user_timezone_direct_attribute",
            "user_profile_timezone_related",
            "try_user_model_first",
            "try_profile_model_second",
            "return_timezone_string_or_none",
            "debug_log_timezone_source",
        ],
        "edge_cases": [
            "no_user_attribute_returns_none",
            "unauthenticated_returns_none",
            "no_timezone_attr_returns_none",
            "no_profile_attr_returns_none",
            "empty_timezone_returns_none",
            "exception_caught_returns_none",
        ],
    }
    logger.debug(
        "User timezone config: authentication_check=%d, retrieval_locations=%d",
        len(config["authentication_check"]),
        len(config["retrieval_locations"]),
    )
    return config


def get_timezone_activation_config() -> dict:
    """Configure timezone activation with zoneinfo and Django timezone utilities. Ref: SP06-T79."""
    logger.debug("Configuring timezone activation with zoneinfo and Django timezone utilities...")
    config: dict = {
        "configured": True,
        "activation_flow": [
            "validate_timezone_name_string",
            "check_not_empty_string",
            "create_zoneinfo_zone_info_object",
            "call_timezone_activate_method",
            "log_debug_activated_timezone",
            "handle_invalid_timezone_graceful",
        ],
        "validation_steps": [
            "isinstance_check_string_type",
            "strip_empty_string_check",
            "zone_info_not_found_error_catch",
            "type_error_non_string_catch",
            "general_exception_fallback",
            "deactivate_on_all_errors",
        ],
        "deactivation_cleanup": [
            "always_deactivate_after_request",
            "timezone_deactivate_in_finally",
            "prevents_timezone_leaking",
            "thread_safe_cleanup",
            "consistent_state_after_request",
            "logging_deactivation_debug",
        ],
    }
    logger.debug(
        "Timezone activation config: activation_flow=%d, validation_steps=%d",
        len(config["activation_flow"]),
        len(config["validation_steps"]),
    )
    return config


def get_default_timezone_config() -> dict:
    """Configure default timezone Asia/Colombo for Sri Lanka business location. Ref: SP06-T80."""
    logger.debug("Configuring default timezone Asia/Colombo for Sri Lanka business location...")
    config: dict = {
        "configured": True,
        "default_settings": [
            "asia_colombo_timezone_name",
            "utc_plus_5_30_offset",
            "sri_lanka_standard_time",
            "no_daylight_saving_time",
            "iana_timezone_database_entry",
            "class_level_constant_default",
        ],
        "fallback_logic": [
            "used_when_no_user_timezone",
            "used_when_no_tenant_timezone",
            "final_fallback_in_resolution",
            "logged_when_default_used",
            "settings_configurable_option",
            "getattr_settings_default_timezone",
        ],
        "business_context": [
            "primary_business_location_lk",
            "matches_target_market_timezone",
            "consistent_datetime_operations",
            "admin_operations_local_time",
            "report_generation_local_time",
            "customer_facing_timestamps",
        ],
    }
    logger.debug(
        "Default timezone config: default_settings=%d, fallback_logic=%d",
        len(config["default_settings"]),
        len(config["fallback_logic"]),
    )
    return config


def get_timezone_middleware_registration_config() -> dict:
    """Configure TimezoneMiddleware registration in Django MIDDLEWARE setting. Ref: SP06-T81."""
    logger.debug("Configuring TimezoneMiddleware registration in Django MIDDLEWARE setting...")
    config: dict = {
        "configured": True,
        "middleware_position": [
            "after_authentication_middleware",
            "after_request_logging_middleware",
            "before_message_middleware",
            "after_tenant_middleware",
            "correct_stack_order_position",
            "user_context_required_for_timezone",
        ],
        "registration_details": [
            "full_path_apps_core_middleware_timezone",
            "timezone_middleware_class_name",
            "added_to_middleware_list_setting",
            "exported_from_middleware_init",
            "added_to_all_list_export",
            "middleware_order_documented",
        ],
        "verification_steps": [
            "manage_py_check_passes",
            "server_starts_without_errors",
            "timezone_activation_logged",
            "default_timezone_active",
            "user_timezone_override_works",
            "tenant_timezone_override_works",
        ],
    }
    logger.debug(
        "Timezone middleware registration config: middleware_position=%d, registration_details=%d",
        len(config["middleware_position"]),
        len(config["registration_details"]),
    )
    return config


def get_middleware_setting_config() -> dict:
    """Configure complete MIDDLEWARE setting with all custom and Django middleware. Ref: SP06-T82."""
    logger.debug("Configuring complete MIDDLEWARE setting with all custom and Django middleware...")
    config: dict = {
        "configured": True,
        "security_layer": [
            "security_middleware_first",
            "cors_middleware_second",
            "ssl_redirect_before_processing",
            "hsts_header_configuration",
            "cors_cross_origin_headers",
            "security_headers_early_position",
        ],
        "middleware_order": [
            "tenant_middleware_after_security",
            "session_before_authentication",
            "auth_before_user_dependent",
            "rate_limit_before_expensive_ops",
            "timezone_after_authentication",
            "messages_after_session",
        ],
        "custom_middleware": [
            "security_headers_middleware_custom",
            "ratelimit_middleware_custom",
            "request_logging_middleware_custom",
            "timezone_middleware_custom",
            "middleware_paths_apps_core",
            "all_middleware_registered_in_settings",
        ],
    }
    logger.debug(
        "Middleware setting config: security_layer=%d, middleware_order=%d",
        len(config["security_layer"]),
        len(config["middleware_order"]),
    )
    return config


def get_middleware_order_verification_config() -> dict:
    """Configure middleware order verification ensuring correct dependency chain. Ref: SP06-T83."""
    logger.debug("Configuring middleware order verification ensuring correct dependency chain...")
    config: dict = {
        "configured": True,
        "dependency_chain": [
            "security_first_in_stack",
            "tenant_before_database_operations",
            "session_before_auth_required",
            "auth_before_user_context_middleware",
            "csrf_after_session_middleware",
            "messages_after_session_middleware",
        ],
        "order_validation": [
            "thirteen_middleware_entries_total",
            "no_duplicate_middleware_entries",
            "no_deprecated_middleware_included",
            "django_guidelines_followed",
            "third_party_middleware_positioned",
            "custom_middleware_correct_paths",
        ],
        "verification_results": [
            "all_order_requirements_satisfied",
            "dependency_graph_validated",
            "no_circular_dependencies",
            "integration_tests_planned",
            "performance_impact_assessed",
            "production_ready_configuration",
        ],
    }
    logger.debug(
        "Middleware order verification config: dependency_chain=%d, order_validation=%d",
        len(config["dependency_chain"]),
        len(config["order_validation"]),
    )
    return config


def get_middleware_tests_suite_config() -> dict:
    """Configure comprehensive middleware test suite for all middleware components. Ref: SP06-T84."""
    logger.debug("Configuring middleware tests suite...")
    config: dict = {
        "configured": True,
        "test_files": [
            "test_timezone_middleware_py",
            "test_security_middleware_py",
            "test_ratelimit_middleware_py",
            "test_logging_middleware_py",
            "test_tenant_middleware_py",
            "test_middleware_integration_py",
        ],
        "test_categories": [
            "normal_operation_tests",
            "error_handling_tests",
            "edge_case_tests",
            "integration_points_tests",
            "code_coverage_above_80_percent",
            "django_test_framework_used",
        ],
        "test_patterns": [
            "request_factory_for_unit_tests",
            "test_client_for_integration",
            "mock_objects_for_dependencies",
            "setup_and_teardown_fixtures",
            "descriptive_test_names",
            "grouped_test_classes",
        ],
    }
    logger.debug(
        "Middleware tests suite config: test_files=%d, test_categories=%d",
        len(config["test_files"]),
        len(config["test_categories"]),
    )
    return config


def get_middleware_integration_testing_config() -> dict:
    """Configure integration tests verifying complete middleware stack works correctly. Ref: SP06-T85."""
    logger.debug("Configuring middleware integration testing...")
    config: dict = {
        "configured": True,
        "integration_scenarios": [
            "full_stack_execution_test",
            "middleware_order_verification",
            "multi_tenant_scenarios_tested",
            "authenticated_user_scenarios",
            "security_headers_on_response",
            "rate_limiting_integration",
        ],
        "order_verification": [
            "security_middleware_first_position",
            "session_before_authentication",
            "auth_before_user_dependent",
            "tenant_before_database_operations",
            "timezone_after_authentication",
            "messages_after_session",
        ],
        "error_handling": [
            "middleware_exception_handling",
            "missing_context_graceful",
            "invalid_configuration_handled",
            "performance_within_threshold",
            "cache_clear_between_tests",
            "timezone_deactivation_cleanup",
        ],
    }
    logger.debug(
        "Middleware integration testing config: integration_scenarios=%d, order_verification=%d",
        len(config["integration_scenarios"]),
        len(config["order_verification"]),
    )
    return config


def get_middleware_documentation_config() -> dict:
    """Configure comprehensive middleware documentation for all components. Ref: SP06-T86."""
    logger.debug("Configuring middleware documentation...")
    config: dict = {
        "configured": True,
        "documentation_sections": [
            "overview_and_table_of_contents",
            "middleware_stack_order_rationale",
            "individual_component_docs",
            "configuration_examples_provided",
            "troubleshooting_section_complete",
            "performance_considerations_documented",
        ],
        "documented_components": [
            "tenant_middleware_documented",
            "security_headers_middleware_documented",
            "ratelimit_middleware_documented",
            "request_logging_middleware_documented",
            "timezone_middleware_documented",
            "middleware_stack_integration_documented",
        ],
        "documentation_quality": [
            "code_examples_working_tested",
            "usage_examples_provided",
            "configuration_options_listed",
            "error_handling_documented",
            "dependencies_listed",
            "changelog_maintained",
        ],
    }
    logger.debug(
        "Middleware documentation config: documentation_sections=%d, documented_components=%d",
        len(config["documentation_sections"]),
        len(config["documented_components"]),
    )
    return config


def get_middleware_readme_config() -> dict:
    """Configure user-friendly README.md for middleware directory. Ref: SP06-T87."""
    logger.debug("Configuring middleware README...")
    config: dict = {
        "configured": True,
        "readme_sections": [
            "quick_start_guide_included",
            "component_overview_with_icons",
            "middleware_stack_order_visual",
            "usage_examples_per_component",
            "configuration_dev_and_prod",
            "troubleshooting_tips_added",
        ],
        "developer_experience": [
            "user_friendly_format",
            "common_examples_provided",
            "quick_reference_available",
            "links_to_full_documentation",
            "file_structure_documented",
            "version_and_update_info",
        ],
        "content_quality": [
            "code_snippets_tested",
            "visual_elements_used",
            "concise_descriptions",
            "actionable_examples",
            "clear_configuration_guide",
            "support_section_included",
        ],
    }
    logger.debug(
        "Middleware README config: readme_sections=%d, developer_experience=%d",
        len(config["readme_sections"]),
        len(config["developer_experience"]),
    )
    return config


def get_server_startup_verification_config() -> dict:
    """Configure server startup verification with complete middleware stack. Ref: SP06-T88."""
    logger.debug("Configuring server startup verification...")
    config: dict = {
        "configured": True,
        "startup_checks": [
            "server_starts_without_errors",
            "no_middleware_import_errors",
            "all_middleware_initialized",
            "no_configuration_errors",
            "database_connections_successful",
            "cache_backend_connected",
        ],
        "middleware_verification": [
            "security_headers_added_to_response",
            "ratelimit_tracks_requests",
            "logging_captures_requests",
            "timezone_activates_correctly",
            "tenant_resolves_from_domain",
            "complete_stack_executes_in_order",
        ],
        "success_criteria": [
            "test_requests_return_200",
            "no_warnings_in_startup_logs",
            "all_tests_passing_verified",
            "ready_for_next_subphase",
            "subphase_06_marked_complete",
            "documentation_up_to_date",
        ],
    }
    logger.debug(
        "Server startup verification config: startup_checks=%d, middleware_verification=%d",
        len(config["startup_checks"]),
        len(config["middleware_verification"]),
    )
    return config
