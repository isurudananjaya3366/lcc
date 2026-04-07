# File Storage System

> **Module:** `apps.core.storage`
> **Phase:** SP10 — File Storage Configuration
> **Status:** Production-ready

---

## Overview

The LankaCommerce Cloud file storage system provides a secure, scalable,
multi-tenant file storage solution with built-in image processing, validation,
and AWS S3 integration.

### Key Features

- **Multi-Tenant Isolation** — Each tenant's files stored under `tenant-{schema}/` paths
- **Local & Cloud Storage** — Seamlessly switch between local filesystem and AWS S3
- **Image Processing** — Resize, compress, convert, thumbnails, web optimisation
- **File Validation** — Extension, size, MIME type, and malware scanning
- **Secure Access** — Signed URLs for temporary private file access
- **Async Processing** — Background image processing with Celery
- **Storage Cleanup** — Automatic orphaned file detection and removal

### Technology Stack

| Component        | Library                           |
| ---------------- | --------------------------------- |
| Backend          | Django 5.x with `django-storages` |
| Cloud Storage    | AWS S3 via `boto3`                |
| Image Processing | `Pillow` (PIL)                    |
| Async Tasks      | `Celery`                          |
| MIME Detection   | `python-magic` (optional)         |
| Malware Scanning | `pyclamd` / VirusTotal (optional) |

---

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                     Client Application                     │
└───────────────────────┬───────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│                   Django Application                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │             TenantFileStorage                       │  │
│  │  - Multi-tenant path generation                     │  │
│  │  - Storage backend abstraction                      │  │
│  └──────────────┬──────────────────┬───────────────────┘  │
│                 │                  │                       │
│     ┌───────────▼──────┐   ┌──────▼──────────────┐       │
│     │  FileValidator   │   │  ImageProcessor     │       │
│     │  - Extension     │   │  - Resize           │       │
│     │  - Size          │   │  - Compress          │       │
│     │  - MIME type     │   │  - Convert format    │       │
│     │  - Malware scan  │   │  - Thumbnails        │       │
│     └──────────────────┘   └─────────────────────┘       │
└───────────────┬───────────────────────┬───────────────────┘
                │                       │
    ┌───────────▼───────┐    ┌──────────▼─────────┐
    │  Local Filesystem │    │     AWS S3         │
    │  (Development)    │    │   (Production)     │
    └───────────────────┘    └────────────────────┘
         tenant-*/                tenant-*/
```

Every file operation passes through a tenant-aware backend that automatically
prefixes paths with `tenant-{schema_name}/`, ensuring complete data isolation.

---

## Module Layout

```
apps/core/storage/
├── __init__.py        # Public API re-exports
├── backends.py        # Storage backend classes
├── paths.py           # Upload-to path generators
├── validators.py      # File validation pipeline
├── images.py          # ImageProcessor & helpers
├── handlers.py        # Upload handler orchestration
├── constants.py       # Sizes, extensions, expiries
├── s3.py              # Signed URL utilities
├── cleanup.py         # Orphaned file cleanup
└── README.md          # ← This file
```

---

## Quick Start

### Basic Configuration (Development)

```python
# config/settings/storage.py (already included)
STORAGE_BACKEND = "local"          # "local" or "s3"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
```

### Upload a File

```python
from apps.core.storage import TenantFileStorage
from django.core.files.base import ContentFile

storage = TenantFileStorage()
path = storage.save("documents/hello.txt", ContentFile(b"Hello!"))
# → media/tenant-{schema}/documents/hello.txt
```

### Process an Image

```python
from apps.core.storage import ImageProcessor

processor = ImageProcessor(image_file)
result = (
    processor
    .resize(800, 600, mode="fit")
    .compress(quality=80)
    .save(format="WEBP")
)
```

### Validate an Upload

```python
from apps.core.storage import get_image_validator

validator = get_image_validator()
validator.validate_all(uploaded_file)   # raises ValidationError on failure
```

### Generate a Signed URL

```python
from apps.core.storage import generate_signed_url

url = generate_signed_url("private/invoice.pdf", expiry=3600)
```

---

## Storage Backends

| Class                    | Backend  | ACL           | Use Case                    |
| ------------------------ | -------- | ------------- | --------------------------- |
| `TenantFileStorage`      | Local FS | —             | Development                 |
| `TenantMediaStorage`     | Local FS | —             | `MEDIA_ROOT` shortcut       |
| `PublicStorage`          | Local FS | —             | Public/shared assets        |
| `TenantS3Storage`        | S3       | Factory       | Auto-selects private/public |
| `PrivateTenantS3Storage` | S3       | `private`     | Invoices, documents         |
| `PublicTenantS3Storage`  | S3       | `public-read` | Product images              |

Switch backends via `STORAGE_BACKEND = "s3"` in storage settings.  
Use `get_storage_class(kind)` to obtain the correct class at runtime.

---

## Upload Handlers

```python
from apps.core.storage import handle_image_upload

# Automatically chooses sync (<1 MB) or async (>=1 MB) processing
result = handle_image_upload(uploaded_file, instance=product)
```

- `handle_image_upload` — orchestrator (sync/async threshold)
- `process_image_sync` — synchronous resize + compress + save
- `generate_thumbnails` — create all configured thumbnail sizes

---

## Path Generators

Use with `upload_to` on `FileField` / `ImageField`:

```python
from apps.core.storage import product_path

class Product(models.Model):
    image = models.ImageField(upload_to=product_path)
    # → products/YYYY/MM/DD/{uuid}.ext
```

Available generators: `product_path`, `invoice_path`, `document_path`,
`avatar_path`, `tenant_upload_path`.

---

## File Validation

```python
from apps.core.storage import FileValidator

validator = FileValidator(
    allowed_extensions={".jpg", ".png", ".webp"},
    max_size=5 * 1024 * 1024,          # 5 MB
    allowed_mime_types={"image/jpeg", "image/png", "image/webp"},
    scan_malware=True,
)
validator.validate_all(file)
```

Pre-built validators: `get_image_validator()`, `get_document_validator()`,
`get_avatar_validator()`, `get_invoice_validator()`.

---

## Image Processing

```python
from apps.core.storage import ImageProcessor

proc = ImageProcessor(file)

# Chain operations
buf = proc.resize(1200, 900, mode="fit").compress(quality=85).save(format="WEBP")

# Thumbnails
thumbs = proc.generate_thumbnails({"sm": (100, 100), "md": (300, 300)})

# Full web pipeline
buf = proc.optimize_for_web(max_width=1920, quality=85, output_format="WEBP")

# Responsive set
variants = proc.optimize_for_responsive(widths=[480, 768, 1200, 1920])
```

---

## Signed URLs (S3)

```python
from apps.core.storage import generate_signed_url, generate_bulk_signed_urls

url = generate_signed_url("private/doc.pdf", expiry=3600)
urls = generate_bulk_signed_urls(["a.pdf", "b.pdf"], expiry=3600)
```

Expiry presets in `constants.py`: `SHORT` (15 min), `DEFAULT` (1 h),
`MEDIUM` (6 h), `LONG` (24 h), `EXTENDED` (7 d).

---

## Cleanup & Maintenance

```python
from apps.core.storage import FileCleanup

cleaner = FileCleanup()
orphans = cleaner.find_orphaned_files()
cleaner.delete_orphaned_files(dry_run=True)
```

Management command:

```bash
python manage.py cleanmedia --dry-run
python manage.py cleanmedia --min-age-days 30
python manage.py cleanmedia --tenant myshop --force
```

---

## Configuration Reference

All settings live in `config/settings/storage.py`. Key variables:

| Setting                   | Default                                  | Description              |
| ------------------------- | ---------------------------------------- | ------------------------ |
| `STORAGE_BACKEND`         | `"local"`                                | `"local"` or `"s3"`      |
| `MAX_IMAGE_SIZE`          | 5 MB                                     | Max image upload size    |
| `MAX_DOCUMENT_SIZE`       | 25 MB                                    | Max document upload size |
| `MAX_ARCHIVE_SIZE`        | 100 MB                                   | Max archive upload size  |
| `IMAGE_EXTENSIONS`        | jpg, png, gif, webp, svg, bmp, tiff      | Allowed image types      |
| `DOCUMENT_EXTENSIONS`     | pdf, doc, docx, xls, xlsx, csv, txt, rtf | Allowed document types   |
| `AWS_ACCESS_KEY_ID`       | —                                        | S3 access key            |
| `AWS_SECRET_ACCESS_KEY`   | —                                        | S3 secret key            |
| `AWS_STORAGE_BUCKET_NAME` | —                                        | S3 bucket name           |
| `AWS_S3_REGION_NAME`      | `"ap-south-1"`                           | S3 region                |

See `config/settings/storage.py` and `docs/storage/configuration.md` for the
full reference.

---

## Troubleshooting

| Problem                  | Solution                                                     |
| ------------------------ | ------------------------------------------------------------ |
| Files not uploading      | Check `MEDIA_ROOT` is writable; verify AWS credentials if S3 |
| Images not processing    | Ensure `Pillow` is installed; check image file validity      |
| S3 connection errors     | Verify credentials, bucket, region, and IAM permissions      |
| Signed URLs not working  | Check URL expiry, CORS config, and bucket policy             |
| MIME validation fails    | Install `python-magic` (`libmagic` on Linux)                 |
| Malware scan unavailable | Install ClamAV daemon or configure VirusTotal API key        |

Enable debug logging:

```python
LOGGING["loggers"]["apps.core.storage"] = {
    "level": "DEBUG",
    "handlers": ["console"],
}
```

---

## Best Practices

### Security

- Use `PrivateTenantS3Storage` for sensitive files
- Always validate uploads (extension + size + MIME + malware)
- Use signed URLs with short expiry for private content
- Never expose raw S3 keys to clients

### Performance

- Process images asynchronously via Celery for files ≥ 1 MB
- Use WEBP format for web-facing images
- Generate thumbnails at upload time, not on-the-fly
- Set up CloudFront CDN in front of S3 for public assets

### Multi-Tenancy

- Always use `TenantFileStorage` (never default Django storage)
- Paths are auto-prefixed with `tenant-{schema}/`
- Run `cleanmedia` per-tenant with `--tenant` flag
- Monitor per-tenant quota via `TENANT_STORAGE_QUOTA_MB`

---

## Additional Resources

- [Storage Configuration Guide](../../../docs/storage/configuration.md)
- [Performance Tuning](../../../docs/storage/performance.md)
- [API Integration Patterns](../../../docs/storage/api.md)
- [Django File Storage Docs](https://docs.djangoproject.com/en/5.0/ref/files/storage/)
- [django-storages](https://django-storages.readthedocs.io/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Pillow (PIL)](https://pillow.readthedocs.io/)
