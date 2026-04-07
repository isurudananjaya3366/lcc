"""
LankaCommerce Cloud – API Documentation Settings (SP11).

Configuration for drf-spectacular OpenAPI 3.0 schema generation.
These settings control how API documentation is generated and displayed
in Swagger UI and ReDoc interfaces.

Settings are imported into ``base.py`` via::

    from config.settings.api_docs import *

Documentation: https://drf-spectacular.readthedocs.io/
"""

from apps.core.api_docs.extensions import DESCRIPTION_SUPPLEMENT
from config.env import env

# ════════════════════════════════════════════════════════════════════════
# DRF SPECTACULAR — OpenAPI 3.0 Schema Configuration
# ════════════════════════════════════════════════════════════════════════
# Controls how the /api/schema/ endpoint generates the OpenAPI document.
# Swagger UI (/api/docs/) and ReDoc (/api/redoc/) consume this schema.

SPECTACULAR_SETTINGS: dict = {
    # ── General Metadata ──────────────────────────────────────────────
    "TITLE": "LankaCommerce Cloud API",
    "DESCRIPTION": (
        "Multi-tenant SaaS ERP platform for Sri Lankan SMEs.\n\n"
        "LankaCommerce Cloud provides integrated POS, Webstore, and ERP "
        "modules with full support for Sri Lankan business requirements "
        "including LKR currency, Sinhala language, and local integrations."
        + DESCRIPTION_SUPPLEMENT
    ),
    "VERSION": "v1.0.0",

    # ── Contact & License ─────────────────────────────────────────────
    "CONTACT": {
        "name": "LankaCommerce Cloud Support",
        "email": "support@lankacommerce.com",
        "url": "https://lankacommerce.com/support",
    },
    "LICENSE": {
        "name": "Proprietary",
        "url": "https://lankacommerce.com/terms",
    },

    # ── Schema Behaviour ──────────────────────────────────────────────
    # Do not include the schema endpoint itself in the generated schema.
    "SERVE_INCLUDE_SCHEMA": False,

    # Only document paths under /api/v{N}/ (versioned API routes).
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",

    # ── Preprocessing Hooks (Tasks 55-56) ─────────────────────────────
    # Custom hooks executed during schema generation.
    "PREPROCESSING_HOOKS": [
        "apps.core.api_docs.extensions.custom_preprocessing_hook",
    ],

    # ── API Servers ───────────────────────────────────────────────────
    # Available server environments for API testing in documentation UI.
    "SERVERS": [
        {
            "url": "http://localhost:8000",
            "description": "Development Server",
        },
        {
            "url": env(
                "API_BASE_URL", default="https://api.lankacommerce.com"
            ),
            "description": "Production Server",
        },
    ],

    # ── Endpoint Tags ────────────────────────────────────────────────
    # Organise API endpoints into logical groups for documentation.
    "TAGS": [
        {
            "name": "Authentication",
            "description": (
                "User authentication, JWT token management, "
                "and session handling"
            ),
        },
        {
            "name": "Core",
            "description": (
                "Core system endpoints including users, tenants, "
                "and system configuration"
            ),
        },
        {
            "name": "Products",
            "description": (
                "Product catalog, categories, variants, "
                "and pricing management"
            ),
        },
        {
            "name": "Orders",
            "description": (
                "Sales orders, purchase orders, and POS transactions"
            ),
        },
        {
            "name": "Inventory",
            "description": (
                "Stock management, warehouses, and inventory transfers"
            ),
        },
        {
            "name": "Customers",
            "description": (
                "Customer management, CRM, and loyalty programs"
            ),
        },
        {
            "name": "Vendors",
            "description": (
                "Vendor management, supplier contacts, "
                "and purchase relationships"
            ),
        },
        {
            "name": "Sales",
            "description": (
                "Point-of-sale operations, receipts, "
                "and sales processing"
            ),
        },
        {
            "name": "Financial",
            "description": (
                "Invoices, payments, accounting, "
                "and LKR currency handling"
            ),
        },
        {
            "name": "HR",
            "description": (
                "Human resources, employee management, "
                "and payroll operations"
            ),
        },
        {
            "name": "Reports",
            "description": (
                "Business reports, analytics, and data exports"
            ),
        },
        {
            "name": "Webstore",
            "description": (
                "E-commerce storefront, shopping cart, "
                "and customer orders"
            ),
        },
        {
            "name": "Tenants",
            "description": (
                "Multi-tenant administration and tenant provisioning"
            ),
        },
        {
            "name": "Users",
            "description": (
                "User accounts, roles, permissions, and profile management"
            ),
        },
        {
            "name": "Platform",
            "description": (
                "Platform-level administration, health checks, "
                "and system settings"
            ),
        },
    ],

    # ── Security Configuration (Task 35) ─────────────────────────────
    # Split request serializers into separate input/output components.
    "COMPONENT_SPLIT_REQUEST": True,

    # Default security requirement applied to every endpoint unless
    # overridden with @extend_schema(auth=[]).
    "SECURITY": [{"Bearer": []}],

    # JWT Bearer token security scheme – appears as the "Authorize"
    # button in Swagger UI.  Users paste the raw access token; the UI
    # automatically prepends "Bearer ".
    "COMPONENT_SECURITY_SCHEMES": {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
    },

    # ── Sidecar (self-hosted Swagger UI / ReDoc assets) ───────────────
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",

    # ── Swagger UI Behaviour (Tasks 31-40) ────────────────────────────
    # These keys are passed straight through to the Swagger UI
    # JavaScript initialiser.  Full reference:
    # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    "SWAGGER_UI_SETTINGS": {
        # Theme & display (Task 33) ───────────────────────────────────
        "deepLinking": True,
        "displayOperationId": False,
        "defaultModelsExpandDepth": 3,
        "defaultModelExpandDepth": 3,
        "docExpansion": "list",  # "none" | "list" | "full"
        "syntaxHighlight.theme": "monokai",

        # Try-It-Out (Task 34) ────────────────────────────────────────
        "supportedSubmitMethods": [
            "get",
            "post",
            "put",
            "patch",
            "delete",
        ],
        "tryItOutEnabled": True,
        "displayRequestDuration": True,

        # Persist authorisation (Task 36) ─────────────────────────────
        # Stores the JWT token in browser localStorage so it survives
        # page reloads during development / testing sessions.
        "persistAuthorization": True,

        # Filter / search (Task 38) ───────────────────────────────────
        "filter": True,

        # Display options (Task 39) ───────────────────────────────────
        "operationsSorter": "alpha",
        "tagsSorter": "alpha",
        "showExtensions": True,
        "showCommonExtensions": True,
    },

    # ── Custom CSS (Task 40) ──────────────────────────────────────────
    # Brand-specific stylesheet loaded after the default Swagger UI CSS.
    "SWAGGER_UI_CSS": "/static/api_docs/custom.css",

    # ══════════════════════════════════════════════════════════════════
    # ReDoc UI Configuration (Tasks 43-54)
    # ══════════════════════════════════════════════════════════════════
    # ReDoc is a read-only, three-panel API documentation interface.
    # Unlike Swagger UI it has no "Try It Out" — it is optimised for
    # comprehensive, production-quality API reference documentation.
    # Full reference: https://redocly.com/docs/redoc/config/
    "REDOC_UI_SETTINGS": {

        # ── Theme (Tasks 45-46) ───────────────────────────────────────
        # Customise colours to match LankaCommerce Cloud brand palette.
        "theme": {
            "colors": {
                "primary": {
                    "main": "#1976d2",          # LankaCommerce primary blue
                    "contrastText": "#ffffff",   # White text on primary bg
                },
                "success": {"main": "#4caf50"},  # Green — 2xx responses
                "warning": {"main": "#ff9800"},  # Orange — deprecations
                "error": {"main": "#f44336"},    # Red — 4xx / 5xx
                "text": {
                    "primary": "#333333",
                    "secondary": "#666666",
                },
            },

            # ── Typography (Task 47) ─────────────────────────────────
            # System font stack: fast loading, native look, no web-font
            # requests.
            "typography": {
                "fontSize": "14px",
                "lineHeight": "1.6",
                "fontFamily": (
                    '-apple-system, BlinkMacSystemFont, "Segoe UI", '
                    'Roboto, "Helvetica Neue", Arial, sans-serif'
                ),
                "headings": {
                    "fontFamily": (
                        '-apple-system, BlinkMacSystemFont, "Segoe UI", '
                        'Roboto, "Helvetica Neue", Arial, sans-serif'
                    ),
                    "fontWeight": "600",
                },
                "code": {
                    "fontSize": "13px",
                    "fontFamily": (
                        '"Courier New", Courier, monospace'
                    ),
                    "backgroundColor": "#f5f5f5",
                },
            },

            # ── Sidebar (Task 48) ────────────────────────────────────
            "sidebar": {
                "backgroundColor": "#fafafa",
                "textColor": "#333333",
                "activeTextColor": "#1976d2",
            },

            # ── Right panel (code samples) ───────────────────────────
            "rightPanel": {
                "backgroundColor": "#263238",
            },
        },

        # ── Menu / Navigation (Task 48) ──────────────────────────────
        "scrollYOffset": 0,
        "menuToggle": True,

        # ── Search (Task 49) ─────────────────────────────────────────
        # Search is enabled by default in ReDoc's menu panel.
        # It searches endpoints, tags, and descriptions in real-time.

        # ── Expand Responses (Task 50) ───────────────────────────────
        # Show all response schemas expanded on first load so users
        # don't need to click each status code individually.
        "expandResponses": "all",

        # ── Display Options ──────────────────────────────────────────
        "pathInMiddlePanel": True,
        "sortPropsAlphabetically": True,
        "nativeScrollbars": False,

        # ── Download Button (Task 51) ────────────────────────────────
        # Keep the schema download button visible so developers can
        # export the OpenAPI spec for code-gen tools and Postman.
        "hideDownloadButton": False,

        # ── Hide Hostname ────────────────────────────────────────────
        "hideHostname": False,
    },

    # ── Logo / Branding (Task 52) ─────────────────────────────────────
    # x-logo is an OpenAPI extension consumed by ReDoc to display a
    # brand logo above the navigation menu.
    "EXTENSIONS_INFO": {
        "x-logo": {
            "url": "/static/api_docs/logo.png",
            "altText": "LankaCommerce Cloud",
            "backgroundColor": "#ffffff",
            "href": "https://lankacommerce.com",
        },
    },
}
