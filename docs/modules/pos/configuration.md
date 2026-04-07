# POS Configuration

## Django Settings

The POS module relies on global project settings. No separate POS-specific
settings file is needed — all configuration is done via the terminal model
fields and environment variables.

### Required Apps

```python
INSTALLED_APPS = [
    # ...
    "apps.pos",
    "apps.products",
    "apps.inventory",
    "apps.customers",
]
```

### REST Framework

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}
```

### URL Configuration

In `config/urls.py` (or tenant URL conf):

```python
urlpatterns = [
    path("api/v1/pos/", include("apps.pos.urls")),
]
```

## Environment Variables

| Variable                    | Default | Description                       |
| --------------------------- | ------- | --------------------------------- |
| `POS_SESSION_TIMEOUT_HOURS` | `24`    | Auto-close sessions after N hours |
| `POS_MAX_CART_ITEMS`        | `100`   | Maximum items per cart            |
| `POS_RECEIPT_LANGUAGE`      | `en`    | Default receipt language          |

## Terminal-Level Configuration

All POS behaviour that may differ between registers is stored on the
`POSTerminal` model, not in settings. This includes:

- **Printer**: `printer_type`, `receipt_printer_ip`
- **Hardware**: `cash_drawer_enabled`, `barcode_scanner_enabled`, `scanner_interface`
- **Rules**: `allow_price_override`, `allow_discount`, `max_discount_percent`,
  `require_customer`, `allow_negative_inventory`
- **Receipt**: `auto_print_receipt`, `receipt_copies`, `receipt_header`,
  `receipt_footer`, `receipt_language`
- **Offline**: `offline_mode_enabled`

This design allows each terminal to be configured independently via the
admin or API without restarting the application.

## Currency & Localization

The system uses `Decimal` fields with 2 decimal places for all monetary
values. Currency symbol and formatting are handled on the frontend.

Sri Lanka-specific settings:

- Default currency: LKR (Sri Lankan Rupee)
- Tax configuration via `TaxClass` model
- Mobile payment methods: FriMi (`mobile_frimi`), Genie (`mobile_genie`)

## Database

PostgreSQL is required (multi-tenant via `django-tenants`). Each tenant
has its own schema with isolated POS data.

## Dependencies

```
djangorestframework>=3.14
django-filter>=25.2
django-tenants
djangorestframework-simplejwt
django-mptt          # category tree for search filtering
```
