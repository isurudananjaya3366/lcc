"""
API Documentation Examples.

Realistic request and response examples for the LankaCommerce Cloud API.
These are designed to be used with ``drf-spectacular``'s
:class:`~drf_spectacular.utils.OpenApiExample` inside ``@extend_schema``
decorators, or referenced directly in custom documentation.

All monetary values use **LKR** (Sri Lankan Rupee).
Phone numbers use the **+94** international dialling code.
Timestamps are in the **Asia/Colombo** timezone (UTC+05:30).
"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiExample

# ═══════════════════════════════════════════════════════════════════════
# Authentication — request examples
# ═══════════════════════════════════════════════════════════════════════

LOGIN_REQUEST_EXAMPLE = OpenApiExample(
    name="Login Request",
    value={
        "username": "john.doe@example.com",
        "password": "SecurePassword123!",
    },
    request_only=True,
    summary="Obtain JWT token pair",
)

TOKEN_REFRESH_REQUEST_EXAMPLE = OpenApiExample(
    name="Token Refresh Request",
    value={
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    },
    request_only=True,
    summary="Refresh an expired access token",
)

# ═══════════════════════════════════════════════════════════════════════
# Authentication — response examples
# ═══════════════════════════════════════════════════════════════════════

LOGIN_RESPONSE_EXAMPLE = OpenApiExample(
    name="Login Response",
    value={
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    },
    response_only=True,
    status_codes=["200"],
    summary="JWT token pair",
)

TOKEN_REFRESH_RESPONSE_EXAMPLE = OpenApiExample(
    name="Token Refresh Response",
    value={
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    },
    response_only=True,
    status_codes=["200"],
    summary="New access token",
)

# ═══════════════════════════════════════════════════════════════════════
# Products — request examples
# ═══════════════════════════════════════════════════════════════════════

CREATE_PRODUCT_REQUEST_EXAMPLE = OpenApiExample(
    name="Create Product",
    value={
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with USB receiver",
        "category": "electronics",
        "price": "2499.99",
        "sku": "MOUSE-WL-001",
        "in_stock": True,
        "quantity": 50,
    },
    request_only=True,
    summary="Create a new product (LKR)",
)

UPDATE_PRODUCT_REQUEST_EXAMPLE = OpenApiExample(
    name="Update Product",
    value={
        "price": "2299.99",
        "quantity": 45,
    },
    request_only=True,
    summary="Partial product update",
)

# ═══════════════════════════════════════════════════════════════════════
# Products — response examples
# ═══════════════════════════════════════════════════════════════════════

PRODUCT_RESPONSE_EXAMPLE = OpenApiExample(
    name="Product Detail",
    value={
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with USB receiver",
        "category": "electronics",
        "price": "2499.99",
        "currency": "LKR",
        "sku": "MOUSE-WL-001",
        "in_stock": True,
        "quantity": 50,
        "created_at": "2024-01-15T10:30:00+05:30",
        "updated_at": "2024-01-15T10:30:00+05:30",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
    },
    response_only=True,
    status_codes=["200", "201"],
    summary="Single product resource",
)

PRODUCT_LIST_RESPONSE_EXAMPLE = OpenApiExample(
    name="Product List",
    value={
        "count": 150,
        "next": "/api/v1/products/?page=2",
        "previous": None,
        "results": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440010",
                "name": "Wireless Mouse",
                "price": "2499.99",
                "currency": "LKR",
                "in_stock": True,
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440011",
                "name": "Mechanical Keyboard",
                "price": "5999.99",
                "currency": "LKR",
                "in_stock": True,
            },
        ],
    },
    response_only=True,
    status_codes=["200"],
    summary="Paginated product list",
)

# ═══════════════════════════════════════════════════════════════════════
# Orders — request examples
# ═══════════════════════════════════════════════════════════════════════

CREATE_ORDER_REQUEST_EXAMPLE = OpenApiExample(
    name="Create Order",
    value={
        "customer_id": "550e8400-e29b-41d4-a716-446655440001",
        "items": [
            {
                "product_id": "550e8400-e29b-41d4-a716-446655440010",
                "quantity": 2,
                "unit_price": "2499.99",
            },
            {
                "product_id": "550e8400-e29b-41d4-a716-446655440011",
                "quantity": 1,
                "unit_price": "5999.99",
            },
        ],
        "shipping_address": {
            "line1": "123 Galle Road",
            "line2": "Apartment 4B",
            "city": "Colombo",
            "postal_code": "00300",
            "country": "LK",
        },
        "payment_method": "cash_on_delivery",
    },
    request_only=True,
    summary="Place a new order (LKR)",
)

# ═══════════════════════════════════════════════════════════════════════
# Orders — response examples
# ═══════════════════════════════════════════════════════════════════════

ORDER_RESPONSE_EXAMPLE = OpenApiExample(
    name="Order Detail",
    value={
        "id": "550e8400-e29b-41d4-a716-446655440020",
        "order_number": "ORD-2024-0001",
        "status": "pending",
        "customer": {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Amal Perera",
            "email": "amal.perera@example.com",
        },
        "items": [
            {
                "product": {
                    "id": "550e8400-e29b-41d4-a716-446655440010",
                    "name": "Wireless Mouse",
                },
                "quantity": 2,
                "unit_price": "2499.99",
                "subtotal": "4999.98",
            },
        ],
        "subtotal": "4999.98",
        "tax": "750.00",
        "total": "5749.98",
        "currency": "LKR",
        "created_at": "2024-01-15T14:30:00+05:30",
        "tenant_id": "550e8400-e29b-41d4-a716-446655440001",
    },
    response_only=True,
    status_codes=["200", "201"],
    summary="Single order resource",
)

# ═══════════════════════════════════════════════════════════════════════
# Customers — request examples
# ═══════════════════════════════════════════════════════════════════════

CREATE_CUSTOMER_REQUEST_EXAMPLE = OpenApiExample(
    name="Create Customer",
    value={
        "name": "Amal Perera",
        "email": "amal.perera@example.com",
        "phone": "+94771234567",
        "address": {
            "line1": "456 Kandy Road",
            "city": "Kandy",
            "postal_code": "20000",
            "country": "LK",
        },
        "preferred_language": "si",
    },
    request_only=True,
    summary="Register a new customer",
)

# ═══════════════════════════════════════════════════════════════════════
# Error — response examples
# ═══════════════════════════════════════════════════════════════════════

VALIDATION_ERROR_RESPONSE_EXAMPLE = OpenApiExample(
    name="Validation Error (400)",
    value={
        "error_code": "VALIDATION_ERROR",
        "message": "Invalid input data.",
        "details": {
            "price": ["Ensure this value is greater than 0."],
        },
    },
    response_only=True,
    status_codes=["400"],
)

AUTHENTICATION_ERROR_RESPONSE_EXAMPLE = OpenApiExample(
    name="Authentication Error (401)",
    value={
        "error_code": "AUTHENTICATION_FAILED",
        "message": "Authentication credentials were not provided.",
    },
    response_only=True,
    status_codes=["401"],
)

PERMISSION_DENIED_RESPONSE_EXAMPLE = OpenApiExample(
    name="Permission Denied (403)",
    value={
        "error_code": "PERMISSION_DENIED",
        "message": "You do not have permission to perform this action.",
    },
    response_only=True,
    status_codes=["403"],
)

NOT_FOUND_RESPONSE_EXAMPLE = OpenApiExample(
    name="Not Found (404)",
    value={
        "error_code": "NOT_FOUND",
        "message": "The requested resource was not found.",
    },
    response_only=True,
    status_codes=["404"],
)

RATE_LIMIT_RESPONSE_EXAMPLE = OpenApiExample(
    name="Rate Limit Exceeded (429)",
    value={
        "error_code": "RATE_LIMIT_EXCEEDED",
        "message": "API rate limit exceeded. Please wait before retrying.",
        "details": {
            "retry_after": 3600,
            "limit": 1000,
            "reset_at": "2024-01-15T15:00:00Z",
        },
    },
    response_only=True,
    status_codes=["429"],
)
