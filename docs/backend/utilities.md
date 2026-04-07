# Backend Utilities

Reusable utilities for the LankaCommerce Cloud POS backend.

> **Full documentation:** See [`backend/apps/core/README.md`](../../backend/apps/core/README.md)

---

## Modules

| Module         | Import Path            | Purpose                                                                              |
| -------------- | ---------------------- | ------------------------------------------------------------------------------------ |
| **Pagination** | `apps.core.pagination` | DRF pagination classes (Standard, Cursor, LimitOffset, None)                         |
| **Filters**    | `apps.core.filters`    | 7 filter backends + BaseFilterSet for tenant-scoped APIs                             |
| **Validators** | `apps.core.validators` | 12 reusable validators (email, URL, slug, numbers, files, JSON, HTML, tenant-unique) |
| **DateTime**   | `apps.core.datetime`   | Asia/Colombo timezone conversion, date ranges, formatting                            |
| **Sri Lanka**  | `apps.core.srilanka`   | LKR currency, phone validation, NIC parsing, provinces & districts                   |

---

## Quick Start

### Pagination

```python
from apps.core.pagination import StandardPagination

# StandardPagination is the project-wide default (page_size=20, max=100)
# Response includes: count, total_pages, current_page, page_size, next, previous, results
```

| Class                      | Use Case                                     |
| -------------------------- | -------------------------------------------- |
| `StandardPagination`       | General CRUD (default)                       |
| `LCCCursorPagination`      | Large datasets, real-time feeds              |
| `LCCLimitOffsetPagination` | Exports, reporting, third-party integrations |
| `NoPagination`             | Dropdowns, lookup tables (< 100 items)       |

### Filters

```python
from apps.core.filters import (
    TenantFilterBackend,    # Auto tenant isolation (always first)
    DateRangeFilterBackend, # ?date_from=...&date_to=...
    LCCSearchFilter,        # ?search=...
    LCCOrderingFilter,      # ?ordering=-price
    IsActiveFilterBackend,  # ?is_active=true
    CreatedByFilterBackend, # ?created_by=me
    ModifiedAtFilterBackend,# ?modified_after=...&modified_before=...
    BaseFilterSet,          # Common filter fields (is_active, created_after/before, modified_after/before)
)
```

### Validators

```python
from apps.core.validators import (
    LCCEmailValidator, LCCURLValidator, LCCSlugValidator,
    PositiveNumberValidator, DecimalValidator, PercentageValidator,
    FileSizeValidator, ImageDimensionValidator, FileExtensionValidator,
    JSONValidator, NoHTMLValidator, UniqueForTenantValidator,
)

# All are callable classes that raise django.core.exceptions.ValidationError
validator = PositiveNumberValidator()
validator(100)  # OK
```

### DateTime

```python
from apps.core.datetime import (
    SL_TIMEZONE,        # pytz.timezone('Asia/Colombo')
    get_local_now,      # Current time in SL
    convert_to_utc,     # Local → UTC (for storage)
    convert_to_local,   # UTC → Local (for display)
    get_date_range,     # Day start/end
    get_month_range,    # Month start/end
    get_year_range,     # Year or fiscal year (April-March)
    format_date,        # DD/MM/YYYY
    format_datetime,    # DD/MM/YYYY HH:MM
)
```

### Sri Lanka

```python
from apps.core.srilanka import (
    # Currency
    format_lkr,          # format_lkr(1500) → "Rs. 1,500.00"
    parse_lkr,           # parse_lkr("Rs. 1,500.00") → Decimal('1500.00')
    convert_currency,    # Placeholder until Phase 09

    # Phone
    validate_sl_phone,   # validate_sl_phone("0712345678") → True
    format_sl_phone,     # format_sl_phone("0712345678") → "+94 71 234 5678"
    normalize_sl_phone,  # normalize_sl_phone("0712345678") → "+94712345678"

    # NIC
    validate_nic,        # validate_nic("881234567V") → True
    parse_nic_dob,       # parse_nic_dob("881234567V") → (date, 'M'/'F')

    # Administrative
    PROVINCES,           # 9 provinces
    DISTRICTS,           # 25 districts
    get_province_by_code, get_province_choices,
    get_districts_by_province, get_district_by_code, get_district_choices,
)
```

---

## Testing

```bash
# All core utility tests (~838 tests)
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.test_pg \
  --entrypoint "" backend bash -c \
  "pip install -q pytest pytest-django pytz && python -m pytest tests/core/ --tb=short -q"
```

| Module      | Tests | File                             |
| ----------- | ----- | -------------------------------- |
| Pagination  | 73    | `tests/core/test_pagination.py`  |
| Filters     | 100   | `tests/core/test_filters.py`     |
| Validators  | 200   | `tests/core/test_validators.py`  |
| DateTime    | 122   | `tests/core/test_datetime.py`    |
| Sri Lanka   | 293   | `tests/core/test_srilanka.py`    |
| Integration | 50+   | `tests/core/test_integration.py` |

### Verification

```bash
python backend/scripts/verify_sp12.py
```

---

## Architecture Notes

- **Timezone:** All database timestamps are stored in UTC. Convert to `Asia/Colombo` only for display.
- **Tenant isolation:** `TenantFilterBackend` must be the first filter backend in every multi-tenant view.
- **Field names:** Models use `created_on` / `updated_on` (not `created_at` / `updated_at`).
- **Fiscal year:** Sri Lanka fiscal year runs April 1 – March 31.
- **NIC formats:** Old (9 digits + V/X) and new (12 digits) are both supported.
- **Phone prefixes:** Valid mobile: 70, 71, 72, 74, 75, 76, 77, 78.

---

_SubPhase-12: Core Utilities & Helpers — LankaCommerce Cloud POS_
