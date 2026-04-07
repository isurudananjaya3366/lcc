# Core Utilities & Helpers

Comprehensive reusable utilities for **LankaCommerce Cloud POS** (SubPhase-12).

All modules are fully tested, tenant-aware where applicable, and designed for
the Sri Lankan business context.

---

## Overview

| Module     | Location               | Purpose                                             |
| ---------- | ---------------------- | --------------------------------------------------- |
| Pagination | `apps.core.pagination` | DRF pagination classes                              |
| Filters    | `apps.core.filters`    | Custom filter backends & FilterSets                 |
| Validators | `apps.core.validators` | Data validation utilities                           |
| DateTime   | `apps.core.datetime`   | Sri Lankan timezone & date helpers                  |
| Sri Lanka  | `apps.core.srilanka`   | Localization utilities (LKR, phone, NIC, provinces) |

---

## Module Structure

```
apps/core/
├── pagination/
│   ├── __init__.py           # Package exports
│   ├── standard.py           # StandardPagination (default, page_size=20, max=100)
│   ├── cursor.py             # LCCCursorPagination (ordered by -created_on)
│   ├── limit_offset.py       # LCCLimitOffsetPagination (default=20, max=100)
│   └── none.py               # NoPagination (for small datasets)
├── filters/
│   ├── __init__.py           # Package exports
│   ├── backends.py           # 7 filter backends
│   └── filtersets.py         # BaseFilterSet
├── validators/
│   ├── __init__.py           # Package exports
│   ├── common.py             # Email, URL, Slug, Number, Decimal, Percentage
│   ├── file_validators.py    # File size, image dimension, extension validators
│   └── content.py            # JSON, NoHTML, UniqueForTenant
├── datetime/
│   ├── __init__.py           # Package exports
│   ├── timezone.py           # UTC ↔ Asia/Colombo conversion
│   └── date_utils.py         # Date ranges, formatting, fiscal year
└── srilanka/
    ├── __init__.py           # Package exports
    ├── currency.py           # LKR formatting (Rs. 1,500.00)
    ├── phone.py              # +94 phone validation & formatting
    ├── nic.py                # NIC validation & DOB parsing
    └── provinces.py          # 9 provinces, 25 districts
```

---

## Pagination

> **Module:** `apps.core.pagination`
> **Version:** 1.0.0

Four pagination classes extending Django REST Framework.

### Classes

#### StandardPagination (Default)

The project-wide default pagination class. Set in Django settings:

```python
# config/settings/base.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
}
```

| Attribute               | Value       |
| ----------------------- | ----------- |
| `page_size`             | 20          |
| `max_page_size`         | 100         |
| `page_size_query_param` | `page_size` |

**Usage:**

```python
from apps.core.pagination import StandardPagination

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = StandardPagination  # or omit — it's the default
```

**API Request:**

```
GET /api/products/?page=1&page_size=10
```

**Response Shape:**

```json
{
    "count": 150,
    "next": "http://api.example.com/products/?page=2&page_size=10",
    "previous": null,
    "total_pages": 15,
    "current_page": 1,
    "page_size": 10,
    "results": [ ... ]
}
```

---

#### LCCCursorPagination

Cursor-based pagination for large, frequently changing datasets. Uses opaque
cursor tokens — no page jumping, but results remain stable even when data
changes between requests.

| Attribute            | Value         |
| -------------------- | ------------- |
| `page_size`          | 20            |
| `ordering`           | `-created_on` |
| `cursor_query_param` | `cursor`      |

**Best for:** Activity feeds, notifications, audit logs, real-time streams.

```python
from apps.core.pagination import LCCCursorPagination

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    pagination_class = LCCCursorPagination
```

**API Request:**

```
GET /api/audit-logs/?cursor=cD0yMDI2LTAxLTIz
```

> **Note:** Ordering field is `created_on`, matching the project's
> `TimeStampedModel` convention (not `created_at`).

---

#### LCCLimitOffsetPagination

SQL-style `LIMIT`/`OFFSET` pagination for maximum client flexibility.

| Attribute       | Value |
| --------------- | ----- |
| `default_limit` | 20    |
| `max_limit`     | 100   |

```python
from apps.core.pagination import LCCLimitOffsetPagination

class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    pagination_class = LCCLimitOffsetPagination
```

**API Request:**

```
GET /api/reports/?limit=50&offset=100
```

**Response Shape:**

```json
{
    "count": 500,
    "next": "http://api.example.com/reports/?limit=50&offset=150",
    "previous": "http://api.example.com/reports/?limit=50&offset=50",
    "limit": 50,
    "offset": 100,
    "results": [ ... ]
}
```

> **Performance:** For offsets > 10,000 consider `LCCCursorPagination`.

---

#### NoPagination

Disables pagination entirely. Returns all results in a single response.

```python
from apps.core.pagination import NoPagination

class ProvinceListView(ListAPIView):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    pagination_class = NoPagination
```

> **Warning:** Only use for small, bounded datasets (< 100 items) such as
> dropdown options, lookup tables, or settings data. Never use for unbounded
> collections.

---

### Pagination Best Practices

| Scenario                      | Recommended Class              |
| ----------------------------- | ------------------------------ |
| Standard CRUD endpoints       | `StandardPagination` (default) |
| Large datasets (10,000+ rows) | `LCCCursorPagination`          |
| Data exports / reporting      | `LCCLimitOffsetPagination`     |
| Dropdown/select options       | `NoPagination`                 |
| Real-time feeds               | `LCCCursorPagination`          |

- Always enforce `max_page_size` to prevent DoS via large page requests.
- The default `page_size=20` balances response size with UX.
- All classes include enhanced response metadata (total pages, current page, etc.).

---

## Filters

> **Module:** `apps.core.filters`
> **Version:** 1.0.0

Seven filter backends and one base FilterSet class.

### Filter Backends

| Backend                   | Query Params                        | Purpose                                 |
| ------------------------- | ----------------------------------- | --------------------------------------- |
| `TenantFilterBackend`     | _(automatic)_                       | Automatic tenant data isolation         |
| `DateRangeFilterBackend`  | `date_from`, `date_to`              | Filter by `created_on` date range       |
| `LCCSearchFilter`         | `search`                            | Full-text search across `search_fields` |
| `LCCOrderingFilter`       | `ordering`                          | Result ordering via `ordering_fields`   |
| `IsActiveFilterBackend`   | `is_active`                         | Active/inactive boolean filtering       |
| `CreatedByFilterBackend`  | `created_by`                        | Filter by creator (supports `"me"`)     |
| `ModifiedAtFilterBackend` | `modified_after`, `modified_before` | Filter by `updated_on` range            |

---

#### TenantFilterBackend

**Must be first** in the filter backends list. Automatically scopes querysets
to the current tenant.

```python
from apps.core.filters import TenantFilterBackend

class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [TenantFilterBackend, ...]
```

---

#### DateRangeFilterBackend

Filters by `created_on` date range. Accepts ISO 8601 strings.

```
GET /api/orders/?date_from=2026-01-01&date_to=2026-01-31
```

---

#### LCCSearchFilter

Enhanced DRF `SearchFilter`. Define `search_fields` on the view.

```python
from apps.core.filters import LCCSearchFilter

class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [TenantFilterBackend, LCCSearchFilter]
    search_fields = ['name', 'sku', 'description']
```

```
GET /api/products/?search=laptop
```

---

#### LCCOrderingFilter

Enhanced DRF `OrderingFilter`. Define `ordering_fields` on the view.

```python
from apps.core.filters import LCCOrderingFilter

class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [TenantFilterBackend, LCCOrderingFilter]
    ordering_fields = ['name', 'price', 'created_on']
    ordering = ['-created_on']  # Default ordering
```

```
GET /api/products/?ordering=-price
```

---

#### IsActiveFilterBackend

Boolean filter on the `is_active` field.

```
GET /api/products/?is_active=true
GET /api/products/?is_active=false
```

---

#### CreatedByFilterBackend

Filter by `created_by` user. Supports the special value `"me"` to filter
records created by the current authenticated user.

```
GET /api/orders/?created_by=5
GET /api/orders/?created_by=me
```

---

#### ModifiedAtFilterBackend

Filter by `updated_on` date range.

```
GET /api/orders/?modified_after=2026-01-01&modified_before=2026-01-31
```

---

### BaseFilterSet

Reusable base FilterSet with common filter fields. Extend for model-specific
filtering.

```python
from apps.core.filters import BaseFilterSet

class ProductFilterSet(BaseFilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta(BaseFilterSet.Meta):
        model = Product
        fields = ['category', 'brand']
```

**Base fields provided:**

- `is_active` — Boolean filter
- `created_after` / `created_before` → filters on `created_on`
- `modified_after` / `modified_before` → filters on `updated_on`

### Combining Filter Backends

```python
from apps.core.filters import (
    TenantFilterBackend,
    DateRangeFilterBackend,
    LCCSearchFilter,
    LCCOrderingFilter,
    IsActiveFilterBackend,
)

class OrderViewSet(viewsets.ModelViewSet):
    filter_backends = [
        TenantFilterBackend,        # MUST be first
        IsActiveFilterBackend,
        DateRangeFilterBackend,
        LCCSearchFilter,
        LCCOrderingFilter,
    ]
    search_fields = ['order_number', 'customer__name']
    ordering_fields = ['created_on', 'total']
    ordering = ['-created_on']
```

---

## Validators

> **Module:** `apps.core.validators`
> **Version:** 1.0.0

Twelve reusable validators. All are callable classes that raise
`django.core.exceptions.ValidationError` on invalid input.

### Available Validators

| Validator                  | Purpose                                          | Example                                                       |
| -------------------------- | ------------------------------------------------ | ------------------------------------------------------------- |
| `LCCEmailValidator`        | Email validation with disposable domain blocking | `LCCEmailValidator()`                                         |
| `LCCURLValidator`          | URL validation (http/https)                      | `LCCURLValidator()`                                           |
| `LCCSlugValidator`         | Slug: 3-50 chars, lowercase + digits + hyphens   | `LCCSlugValidator()`                                          |
| `PositiveNumberValidator`  | Positive numbers only                            | `PositiveNumberValidator()`                                   |
| `DecimalValidator`         | Decimal with max_digits/decimal_places           | `DecimalValidator(max_digits=10, decimal_places=2)`           |
| `PercentageValidator`      | Range 0–100                                      | `PercentageValidator()`                                       |
| `FileSizeValidator`        | Maximum file size in MB                          | `FileSizeValidator(max_size_mb=5)`                            |
| `ImageDimensionValidator`  | Max image width/height                           | `ImageDimensionValidator(max_width=1920, max_height=1080)`    |
| `FileExtensionValidator`   | Allowed file extensions                          | `FileExtensionValidator(allowed_extensions=['.pdf', '.jpg'])` |
| `JSONValidator`            | Valid JSON string                                | `JSONValidator()`                                             |
| `NoHTMLValidator`          | Rejects strings containing HTML tags             | `NoHTMLValidator()`                                           |
| `UniqueForTenantValidator` | Tenant-scoped unique constraint                  | `UniqueForTenantValidator(model, field)`                      |

---

### Usage in Django Models

```python
from django.db import models
from apps.core.validators import (
    LCCSlugValidator,
    PositiveNumberValidator,
    DecimalValidator,
)

class Product(models.Model):
    slug = models.SlugField(
        max_length=50,
        validators=[LCCSlugValidator()],
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[PositiveNumberValidator(), DecimalValidator(max_digits=10, decimal_places=2)],
    )
```

### Usage in DRF Serializers

```python
from rest_framework import serializers
from apps.core.validators import LCCEmailValidator, PercentageValidator

class CustomerSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[LCCEmailValidator()])
    discount = serializers.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[PercentageValidator()],
    )
```

### File Validators on Upload Fields

```python
from apps.core.validators import FileSizeValidator, FileExtensionValidator

class DocumentSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[
            FileSizeValidator(max_size_mb=10),
            FileExtensionValidator(allowed_extensions=['.pdf', '.docx', '.xlsx']),
        ],
    )
```

### Tenant-Scoped Uniqueness

```python
from apps.core.validators import UniqueForTenantValidator

class CategorySerializer(serializers.Serializer):
    slug = serializers.SlugField(
        validators=[UniqueForTenantValidator(model=Category, field='slug')],
    )
```

---

## DateTime Helpers

> **Module:** `apps.core.datetime`
> **Version:** 1.0.0

Sri Lankan timezone utilities and date helpers.

### Constants

| Name          | Value                           | Description      |
| ------------- | ------------------------------- | ---------------- |
| `SL_TIMEZONE` | `pytz.timezone('Asia/Colombo')` | UTC+5:30, no DST |

### Functions

| Function                                  | Purpose                            |
| ----------------------------------------- | ---------------------------------- |
| `get_local_now()`                         | Current datetime in Asia/Colombo   |
| `convert_to_utc(dt)`                      | Local → UTC                        |
| `convert_to_local(dt)`                    | UTC → Local                        |
| `get_date_range(date)`                    | Start/end of a day (SL timezone)   |
| `get_month_range(year, month)`            | Start/end of a month               |
| `get_year_range(year, fiscal=False)`      | Start/end of a year or fiscal year |
| `format_date(dt)`                         | Format as DD/MM/YYYY               |
| `format_datetime(dt, show_seconds=False)` | Format as DD/MM/YYYY HH:MM         |

---

### Timezone Conversion

```python
from apps.core.datetime import (
    SL_TIMEZONE,
    get_local_now,
    convert_to_utc,
    convert_to_local,
)

# Current time in Sri Lanka
now = get_local_now()
# >>> 2026-03-11 14:30:00+05:30

# Local → UTC (for database storage)
from datetime import datetime
sl_time = datetime(2026, 1, 23, 14, 30)
utc_time = convert_to_utc(sl_time)
# >>> 2026-01-23 09:00:00+00:00

# UTC → Local (for display)
import pytz
utc_time = datetime(2026, 1, 23, 9, 0, tzinfo=pytz.UTC)
local_time = convert_to_local(utc_time)
# >>> 2026-01-23 14:30:00+05:30
```

### Date Ranges

```python
from datetime import date
from apps.core.datetime import get_date_range, get_month_range, get_year_range

# Today's range
start, end = get_date_range(date(2026, 1, 23))
# start = 2026-01-23 00:00:00+05:30
# end   = 2026-01-23 23:59:59.999999+05:30

# Monthly range
start, end = get_month_range(2026, 1)
# start = 2026-01-01 00:00:00+05:30
# end   = 2026-01-31 23:59:59.999999+05:30

# Calendar year
start, end = get_year_range(2026)
# start = 2026-01-01 00:00:00+05:30
# end   = 2026-12-31 23:59:59.999999+05:30

# Fiscal year (April–March)
start, end = get_year_range(2026, fiscal=True)
# start = 2026-04-01 00:00:00+05:30
# end   = 2027-03-31 23:59:59.999999+05:30
```

### Date Formatting

```python
from datetime import date, datetime
from apps.core.datetime import format_date, format_datetime

format_date(date(2026, 1, 23))
# >>> '23/01/2026'

format_datetime(datetime(2026, 1, 23, 14, 30))
# >>> '23/01/2026 14:30'

format_datetime(datetime(2026, 1, 23, 14, 30, 45), show_seconds=True)
# >>> '23/01/2026 14:30:45'
```

### Best Practices

- **Always store UTC** in the database. Convert only for display.
- Use `get_local_now()` instead of `datetime.now()` or `timezone.now()`.
- Use `fiscal=True` for financial reports (Sri Lankan fiscal year: April–March).
- Naive datetimes passed to `convert_to_utc()` are assumed to be in SL time.
- Naive datetimes passed to `convert_to_local()` are assumed to be in UTC.

---

## Sri Lanka Utilities

> **Module:** `apps.core.srilanka`
> **Version:** 1.0.0

Localization utilities specific to Sri Lanka.

---

### Currency (LKR)

Format, parse, and convert Sri Lankan Rupees.

```python
from apps.core.srilanka import format_lkr, parse_lkr, convert_currency

# Formatting
format_lkr(1500)                    # "Rs. 1,500.00"
format_lkr(1500000)                 # "Rs. 1,500,000.00"
format_lkr(1500.50, show_symbol=False)  # "1,500.50"
format_lkr(-500)                    # "Rs. -500.00"

# Parsing
parse_lkr("Rs. 1,500.00")          # Decimal('1500.00')
parse_lkr("1,500")                  # Decimal('1500')
parse_lkr(1500)                     # Decimal('1500')

# Currency conversion (exchange_rate required until Phase 09)
convert_currency(300, 'LKR', 'USD', exchange_rate=0.0033)
# >>> Decimal('0.99')
```

---

### Phone Validation

Validate, format, and normalize Sri Lankan mobile numbers.

**Valid mobile prefixes:** 70, 71, 72, 74, 75, 76, 77, 78

```python
from apps.core.srilanka import validate_sl_phone, format_sl_phone, normalize_sl_phone

# Validation
validate_sl_phone("+94 71 234 5678")   # True
validate_sl_phone("0712345678")        # True
validate_sl_phone("712345678")         # True
validate_sl_phone("0732345678")        # False (73 not a valid prefix)

# Formatting (+94 XX XXX XXXX)
format_sl_phone("0712345678")          # "+94 71 234 5678"

# Normalization (storage format)
normalize_sl_phone("0712345678")       # "+94712345678"
normalize_sl_phone("+94 71 234 5678")  # "+94712345678"
```

**Accepted input formats:**

- `+94 XX XXX XXXX` (international with spaces)
- `+94XXXXXXXXX` (international compact)
- `0XXXXXXXXX` (local with leading zero)
- `XXXXXXXXX` (9 digits starting with 7)

---

### NIC Validation

Validate Sri Lankan National Identity Cards and extract date of birth/gender.

**Formats:**

- **Old:** 9 digits + V/X (e.g., `881234567V`)
- **New:** 12 digits (e.g., `198812345678`)

```python
from apps.core.srilanka import validate_nic, parse_nic_dob

# Validation
validate_nic("881234567V")      # True  (old format)
validate_nic("198812345678")    # True  (new format)
validate_nic("invalid")         # False

# Parse DOB and gender
dob, gender = parse_nic_dob("881234567V")
# dob = date object (day 123 of 1988)
# gender = 'M' or 'F'
```

**NIC structure:**

- Old format: first 2 digits = birth year, next 3 = day of year (+500 for female)
- New format: first 4 digits = birth year, next 3 = day of year (+500 for female)
- Day > 500 → Female, day ≤ 366 → Male

---

### Administrative Divisions

9 provinces, 25 districts — each with English name, Sinhala name, and code.

```python
from apps.core.srilanka import (
    PROVINCES,
    DISTRICTS,
    get_province_by_code,
    get_province_choices,
    get_districts_by_province,
    get_district_by_code,
    get_district_choices,
)

# Province lookup
province = get_province_by_code('WP')
# {"code": "WP", "name": "Western Province", "sinhala": "බස්නාහිර පළාත"}

# Province choices (for Django forms/models)
choices = get_province_choices()
# [("WP", "Western Province"), ("CP", "Central Province"), ...]

# Districts by province
districts = get_districts_by_province('WP')
# [{"code": "CO", "name": "Colombo", ...}, {"code": "GM", ...}, {"code": "KT", ...}]

# District lookup
district = get_district_by_code('CO')
# {"code": "CO", "name": "Colombo", "sinhala": "කොළඹ", "province": "WP"}

# District choices (optionally filtered by province)
all_choices = get_district_choices()              # All 25 districts
wp_choices = get_district_choices('WP')           # Only Western Province
```

**Data:**

- 9 Provinces: WP, CP, SP, NP, EP, NWP, NCP, UP, SG
- 25 Districts: CO, GM, KT, KY, MT, NE, GL, MH, HB, JA, KL, MN, MU, VA, AP, BD, TC, KR, PT, AD, PO, BA, MO, KG, RP

---

## Testing

### Running Tests

Run all core utility tests via Docker:

```bash
docker compose run --rm \
  -e DJANGO_SETTINGS_MODULE=config.settings.test_pg \
  --entrypoint "" backend bash -c \
  "pip install -q pytest pytest-django pytz && python -m pytest tests/core/ --tb=short -q"
```

Run a specific module's tests:

```bash
# Pagination
python -m pytest tests/core/test_pagination.py --tb=short -q

# Filters
python -m pytest tests/core/test_filters.py --tb=short -q

# Validators
python -m pytest tests/core/test_validators.py --tb=short -q

# DateTime
python -m pytest tests/core/test_datetime.py --tb=short -q

# Sri Lanka
python -m pytest tests/core/test_srilanka.py --tb=short -q

# Integration
python -m pytest tests/core/test_integration.py --tb=short -q
```

### Test Suite Summary

| Module      | Tests    | File                             |
| ----------- | -------- | -------------------------------- |
| Pagination  | 73       | `tests/core/test_pagination.py`  |
| Filters     | 100      | `tests/core/test_filters.py`     |
| Validators  | 200      | `tests/core/test_validators.py`  |
| DateTime    | 122      | `tests/core/test_datetime.py`    |
| Sri Lanka   | 293      | `tests/core/test_srilanka.py`    |
| Integration | 50+      | `tests/core/test_integration.py` |
| **Total**   | **838+** |                                  |

### Verification Script

```bash
python scripts/verify_sp12.py
```

Checks all imports, key attributes, functional tests, and file existence.

---

## Quick Reference

### Import Cheat Sheet

```python
# Pagination
from apps.core.pagination import (
    StandardPagination, LCCCursorPagination,
    LCCLimitOffsetPagination, NoPagination,
)

# Filters
from apps.core.filters import (
    TenantFilterBackend, DateRangeFilterBackend,
    LCCSearchFilter, LCCOrderingFilter,
    IsActiveFilterBackend, CreatedByFilterBackend,
    ModifiedAtFilterBackend, BaseFilterSet,
)

# Validators
from apps.core.validators import (
    LCCEmailValidator, LCCURLValidator, LCCSlugValidator,
    PositiveNumberValidator, DecimalValidator, PercentageValidator,
    FileSizeValidator, ImageDimensionValidator, FileExtensionValidator,
    JSONValidator, NoHTMLValidator, UniqueForTenantValidator,
)

# DateTime
from apps.core.datetime import (
    SL_TIMEZONE, get_local_now, convert_to_utc, convert_to_local,
    get_date_range, get_month_range, get_year_range,
    format_date, format_datetime,
)

# Sri Lanka
from apps.core.srilanka import (
    format_lkr, parse_lkr, convert_currency,
    validate_sl_phone, format_sl_phone, normalize_sl_phone,
    validate_nic, parse_nic_dob,
    PROVINCES, DISTRICTS,
    get_province_by_code, get_province_choices,
    get_districts_by_province, get_district_by_code, get_district_choices,
)
```

---

## Version History

| Version | Module | Notes                  |
| ------- | ------ | ---------------------- |
| 1.0.0   | All    | Initial release (SP12) |

---

_SubPhase-12: Core Utilities & Helpers — LankaCommerce Cloud POS_
