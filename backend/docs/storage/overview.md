# File Storage Overview

> **Module path:** `apps.core.storage`
> **Backends:** local filesystem (default) or Amazon S3
> **Isolation:** automatic per-tenant path prefixing

---

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                     Application Code                       │
│  (Models · Views · Services · Tasks · Management cmds)     │
├────────────┬──────────────┬───────────────┬───────────────┤
│  Handlers  │  Validators  │  Image Proc   │  Path Gens    │
│  (handle_  │ (FileValid-  │ (ImageProc-   │ (product_     │
│   image_   │  ator,       │  essor,       │  path,        │
│   upload,  │  get_image_  │  resize,      │  invoice_     │
│   process_ │  validator)  │  compress,    │  path,        │
│   sync)    │              │  thumbnails)  │  avatar_path) │
├────────────┴──────────────┴───────────────┴───────────────┤
│                    Storage Backends                         │
│  TenantFileStorage · TenantMediaStorage · PublicStorage     │
│  TenantS3Storage · PrivateS3 · PublicS3                     │
│  get_storage_class("default"|"private"|"public")            │
├─────────────────────────────────────────────────────────────┤
│            Django Storage Framework (STORAGES)               │
├────────────────────┬────────────────────────────────────────┤
│   Local Filesystem │         Amazon S3 (boto3)              │
└────────────────────┴────────────────────────────────────────┘
```

Every file operation passes through a tenant-aware backend that automatically
prefixes paths with `tenant-{schema_name}/`, ensuring complete data isolation
between tenants.

---

## Module Layout

```
apps/core/storage/
├── __init__.py        # Public API re-exports
├── backends.py        # Storage backend classes
├── paths.py           # Upload-to path generators
├── validators.py      # File validation pipeline
├── images.py          # ImageProcessor & utilities
├── handlers.py        # Upload handler orchestration
├── constants.py       # Sizes, extensions, expiries
├── s3.py              # Presigned URL generation
└── cleanup.py         # Orphaned file cleanup
```

---

## Storage Backends

| Class                    | Base                | Purpose                               |
| ------------------------ | ------------------- | ------------------------------------- |
| `TenantFileStorage`      | `FileSystemStorage` | Default tenant-scoped local storage   |
| `TenantMediaStorage`     | `TenantFileStorage` | Media files (MEDIA_ROOT / MEDIA_URL)  |
| `PublicStorage`          | `FileSystemStorage` | Shared public files (no tenant scope) |
| `TenantS3Storage`        | `S3Boto3Storage`    | S3 with tenant prefix                 |
| `PrivateTenantS3Storage` | `TenantS3Storage`   | Private ACL + query-string auth       |
| `PublicTenantS3Storage`  | `TenantS3Storage`   | Public-read ACL, no auth              |

### Factory

```python
from apps.core.storage import get_storage_class

default_storage = get_storage_class("default")
private_storage = get_storage_class("private")
public_storage  = get_storage_class("public")
```

---

## Tenant Path Isolation

All tenant-aware backends call `get_tenant_path(name)` which:

1. Reads `connection.tenant.schema_name` (falls back to `"public"`)
2. Prepends `tenant-{schema}/` to the relative file path
3. Avoids double-prefixing if the path already starts with the prefix
4. Normalises path traversal attempts (`../`)

```
# Tenant "shop_abc" uploading product.jpg:
tenant-shop_abc/products/2026/01/15/<uuid>.jpg

# Public fallback (no tenant context):
tenant-public/products/2026/01/15/<uuid>.jpg
```

---

## Quick Start

### 1. Store a file

```python
from django.core.files.base import ContentFile
from apps.core.storage import TenantFileStorage

storage = TenantFileStorage()
path = storage.save("reports/q4.pdf", ContentFile(pdf_bytes))
url  = storage.url(path)
```

### 2. Upload an image (with auto-processing)

```python
from apps.core.storage import handle_image_upload

# Small images are processed synchronously
# Large images (≥1 MB) are queued via Celery
processed = handle_image_upload(request.FILES["photo"])
```

### 3. Validate an upload

```python
from apps.core.storage import get_image_validator

validator = get_image_validator()
validator.validate_all(request.FILES["photo"])
```

### 4. Generate thumbnails

```python
from apps.core.storage import ImageProcessor

proc = ImageProcessor(uploaded_file)
thumbs = proc.generate_thumbnails({"small": (100, 100), "large": (600, 600)})
for name, thumb in thumbs.items():
    storage.save(f"thumbs/{name}.webp", thumb.save(format="WEBP"))
```

### 5. Generate a presigned S3 URL

```python
from apps.core.storage import generate_signed_url

url = generate_signed_url("invoices/INV-001.pdf", expiry=7200)
```

---

## Upload Handlers

`apps.core.storage.handlers` provides a high-level orchestration layer:

| Function              | Description                                      |
| --------------------- | ------------------------------------------------ |
| `handle_image_upload` | Sync (< 1 MB) or async (≥ 1 MB) image processing |
| `process_image_sync`  | Runs optimize_for_web on an uploaded image       |
| `generate_thumbnails` | Creates all configured thumbnail sizes           |

### Sync vs Async

```
uploaded_file
    │
    ├─ size < 1 MB ──► process_image_sync() ──► return processed file
    │
    └─ size ≥ 1 MB ──► save raw ──► queue Celery task ──► return raw file
```

---

## Path Generators

Upload-to callables for Django `FileField` / `ImageField`:

| Function             | Pattern                                                  |
| -------------------- | -------------------------------------------------------- |
| `product_path`       | `products/YYYY/MM/DD/{uuid}.{ext}`                       |
| `invoice_path`       | `invoices/{invoice_number}.{ext}` or UUID fallback       |
| `document_path`      | `documents/{type}/{uuid}.{ext}` (`general` default)      |
| `avatar_path`        | `avatars/user_{pk}.{ext}`                                |
| `tenant_upload_path` | `{schema}/{subfolder}/{uuid}.{ext}` (defaults `uploads`) |

```python
class Product(models.Model):
    image = models.ImageField(upload_to=product_path)

class Invoice(models.Model):
    attachment = models.FileField(upload_to=invoice_path)
```

---

## File Validation

`FileValidator` runs a pipeline of checks:

1. **Extension** – Allowlist-based (case-insensitive)
2. **Size** – Configurable max size; rejects empty files
3. **MIME type** – Optional; uses `python-magic` for real content sniffing
4. **Malware scan** – Optional; ClamAV or VirusTotal integration

Pre-built validators:

| Factory                    | Max Size | Extensions               |
| -------------------------- | -------- | ------------------------ |
| `get_image_validator()`    | 5 MB     | `.jpg .png .webp .gif …` |
| `get_document_validator()` | 25 MB    | `.pdf .docx .xlsx …`     |
| `get_avatar_validator()`   | 2 MB     | `.jpg .png .webp …`      |
| `get_invoice_validator()`  | 10 MB    | `.pdf …`                 |

```python
from apps.core.storage import get_image_validator

class ProductImage(models.Model):
    image = models.ImageField(
        upload_to=product_path,
        validators=[get_image_validator()],
    )
```

---

## Image Processing

`ImageProcessor` wraps Pillow with a fluent API:

```python
from apps.core.storage import ImageProcessor

proc = ImageProcessor(uploaded_file)
proc.resize(max_width=1920, max_height=1920, mode="fit") \
    .compress(quality=85, optimize=True)                  \
    .convert_format("WEBP")

output = proc.save(format="WEBP")
```

### Resize Modes

| Mode    | Behaviour                               |
| ------- | --------------------------------------- |
| `fit`   | Scale to fit within bounds (no crop)    |
| `fill`  | Scale + centre-crop to exact dimensions |
| `exact` | Force exact dimensions (may distort)    |

### Web Optimisation

```python
proc.optimize_for_web(
    max_width=1920, max_height=1920,
    target_format="WEBP", quality=85,
    strip_metadata=True,
)
```

---

## Signed URLs (S3)

```python
from apps.core.storage import generate_signed_url, generate_bulk_signed_urls

url = generate_signed_url("invoices/INV-001.pdf", expiry=7200)

urls = generate_bulk_signed_urls(
    ["inv1.pdf", "inv2.pdf", "inv3.pdf"],
    expiry=3600,
)
```

Expiry presets (from `constants.py`):

| Constant                     | Seconds | Duration |
| ---------------------------- | ------- | -------- |
| `SIGNED_URL_SHORT_EXPIRY`    | 1 800   | 30 min   |
| `SIGNED_URL_DEFAULT_EXPIRY`  | 3 600   | 1 hr     |
| `SIGNED_URL_MEDIUM_EXPIRY`   | 14 400  | 4 hr     |
| `SIGNED_URL_LONG_EXPIRY`     | 86 400  | 24 hr    |
| `SIGNED_URL_EXTENDED_EXPIRY` | 604 800 | 7 days   |

---

## Cleanup & Maintenance

### Programmatic

```python
from apps.core.storage import FileCleanup, cleanup_old_files

# Quick convenience
result = cleanup_old_files(days_old=30, dry_run=True)

# Full control
fc = FileCleanup(storage=default_storage, dry_run=False)
orphans = fc.find_orphaned_files(path="products/", min_age_days=30)
result = fc.delete_orphaned_files(orphans)
```

### Management Command

```bash
# Dry-run (default) – report what would be deleted
python manage.py cleanmedia

# Live delete, tenant-scoped
python manage.py cleanmedia --force --tenant=shop1 --min-age-days=60

# Limit to a sub-directory
python manage.py cleanmedia --path=products/ --min-age-days=90
```

---

## Constants Reference

### Size Helpers

```python
from apps.core.storage.constants import KB, MB, GB

KB == 1024
MB == 1024 ** 2
GB == 1024 ** 3
```

### Thumbnail Presets

| Name     | Size      |
| -------- | --------- |
| `small`  | 100 × 100 |
| `medium` | 300 × 300 |
| `large`  | 600 × 600 |

### Extension Sets

- `IMAGE_EXTENSIONS` – `.jpg .jpeg .png .gif .webp .svg .bmp .tiff .ico`
- `DOCUMENT_EXTENSIONS` – `.pdf .doc .docx .xls .xlsx .csv .txt .rtf .odt .ods`
- `ARCHIVE_EXTENSIONS` – `.zip .tar .gz .rar .7z`
- `ALL_ALLOWED_EXTENSIONS` – union of the above

---

## Error Handling

| Scenario             | Behaviour                                   |
| -------------------- | ------------------------------------------- |
| Upload too large     | `ValidationError` raised by `FileValidator` |
| Bad extension        | `ValidationError` raised by `FileValidator` |
| MIME mismatch        | `ValidationError` (strict mode only)        |
| Malware detected     | `ValidationError` with threat details       |
| S3 unavailable       | `generate_signed_url` returns `None`        |
| Missing tenant       | Path falls back to `tenant-public/` prefix  |
| Delete error         | Suppressed with logging (no crash)          |
| invalid image upload | `handle_image_upload` returns original file |

---

## See Also

- [Configuration Guide](configuration.md) – all settings, S3 setup, quotas
- [Performance & Tuning](performance.md) – CDN, caching, async processing
- [API Reference](api.md) – endpoint integration patterns
