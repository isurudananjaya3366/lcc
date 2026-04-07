# File Storage Configuration Guide

> **Settings module:** `config.settings.storage`
> **Environment-driven:** all values can be overridden via env vars

---

## Table of Contents

- [File Storage Configuration Guide](#file-storage-configuration-guide)
  - [Table of Contents](#table-of-contents)
  - [Storage Backend Selection](#storage-backend-selection)
  - [Local Filesystem Settings](#local-filesystem-settings)
  - [Amazon S3 Settings](#amazon-s3-settings)
    - [Required Settings (when `STORAGE_BACKEND = "s3"`)](#required-settings-when-storage_backend--s3)
    - [Optional Settings](#optional-settings)
    - [Private vs Public Buckets](#private-vs-public-buckets)
    - [S3 Bucket Policy Example](#s3-bucket-policy-example)
    - [CORS Configuration (for direct browser uploads)](#cors-configuration-for-direct-browser-uploads)
  - [Upload Size Limits](#upload-size-limits)
    - [Dynamic Size Checking](#dynamic-size-checking)
  - [Allowed Extensions](#allowed-extensions)
    - [Extension Helpers](#extension-helpers)
  - [Image Processing Settings](#image-processing-settings)
    - [Thumbnail Use-Case Mapping](#thumbnail-use-case-mapping)
  - [Signed URL Configuration](#signed-url-configuration)
    - [Expiry Presets (constants.py)](#expiry-presets-constantspy)
    - [Per-Type Mapping](#per-type-mapping)
  - [Tenant Storage Quotas](#tenant-storage-quotas)
  - [Malware Scanning](#malware-scanning)
    - [Supported Scanners](#supported-scanners)
  - [Django STORAGES Dictionary](#django-storages-dictionary)
    - [Local mode](#local-mode)
    - [S3 mode](#s3-mode)
  - [Environment Variable Reference](#environment-variable-reference)
  - [See Also](#see-also)

---

## Storage Backend Selection

```python
# config/settings/storage.py
STORAGE_BACKEND = env("STORAGE_BACKEND", default="local")  # "local" | "s3"
```

| Value   | Active Backend      | Notes                    |
| ------- | ------------------- | ------------------------ |
| `local` | `TenantFileStorage` | Default, stores on disk  |
| `s3`    | `TenantS3Storage`   | Requires AWS credentials |

When `STORAGE_BACKEND = "s3"`, the system validates that all required AWS
settings are present and overrides the Django `STORAGES` dictionary
automatically.

---

## Local Filesystem Settings

```python
MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"
```

| Setting      | Default       | Description                    |
| ------------ | ------------- | ------------------------------ |
| `MEDIA_URL`  | `/media/`     | URL prefix for media files     |
| `MEDIA_ROOT` | `mediafiles/` | Absolute path for file uploads |

Files are stored under:

```
<MEDIA_ROOT>/tenant-<schema_name>/<relative_path>
```

For the public storage backend:

```
<MEDIA_ROOT>/public/<relative_path>
```

---

## Amazon S3 Settings

All S3 settings are read from environment variables with safe defaults.

### Required Settings (when `STORAGE_BACKEND = "s3"`)

| Setting                   | Env Var                   | Description                    |
| ------------------------- | ------------------------- | ------------------------------ |
| `AWS_ACCESS_KEY_ID`       | `AWS_ACCESS_KEY_ID`       | IAM access key                 |
| `AWS_SECRET_ACCESS_KEY`   | `AWS_SECRET_ACCESS_KEY`   | IAM secret key                 |
| `AWS_STORAGE_BUCKET_NAME` | `AWS_STORAGE_BUCKET_NAME` | Default S3 bucket              |
| `AWS_S3_REGION_NAME`      | `AWS_S3_REGION_NAME`      | AWS region (e.g. `ap-south-1`) |

### Optional Settings

| Setting                    | Default           | Description                         |
| -------------------------- | ----------------- | ----------------------------------- |
| `AWS_S3_CUSTOM_DOMAIN`     | `None`            | CloudFront / custom domain          |
| `AWS_S3_ENDPOINT_URL`      | `None`            | Custom S3-compatible endpoint       |
| `AWS_S3_FILE_OVERWRITE`    | `False`           | Prevent filename deduplication      |
| `AWS_DEFAULT_ACL`          | `None`            | Default ACL for new objects         |
| `AWS_QUERYSTRING_AUTH`     | `True`            | Include auth in URLs                |
| `AWS_S3_SIGNATURE_VERSION` | `s3v4`            | Signature version                   |
| `AWS_S3_OBJECT_PARAMETERS` | `CacheControl: …` | Default object parameters           |
| `AWS_PRESIGNED_URL_EXPIRY` | `3600`            | Default signed URL expiry (seconds) |
| `AWS_PRIVATE_BUCKET_NAME`  | main bucket       | Bucket for private files            |
| `AWS_PUBLIC_BUCKET_NAME`   | main bucket       | Bucket for public files             |

### Private vs Public Buckets

```python
AWS_PRIVATE_BUCKET_NAME = env("AWS_PRIVATE_BUCKET_NAME", default=AWS_STORAGE_BUCKET_NAME)
AWS_PUBLIC_BUCKET_NAME  = env("AWS_PUBLIC_BUCKET_NAME",  default=AWS_STORAGE_BUCKET_NAME)
```

`PrivateTenantS3Storage` uses `AWS_PRIVATE_BUCKET_NAME` with:

- `default_acl = "private"`
- `querystring_auth = True`

`PublicTenantS3Storage` uses `AWS_PUBLIC_BUCKET_NAME` with:

- `default_acl = "public-read"`
- `querystring_auth = False`

### S3 Bucket Policy Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::your-bucket/*", "arn:aws:s3:::your-bucket"]
    }
  ]
}
```

### CORS Configuration (for direct browser uploads)

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": ["https://your-domain.com"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```

---

## Upload Size Limits

All size limits are configured in `config/settings/storage.py`:

```python
MAX_IMAGE_SIZE    = env.int("MAX_IMAGE_SIZE",    default=5  * 1024 * 1024)   # 5 MB
MAX_AVATAR_SIZE   = env.int("MAX_AVATAR_SIZE",   default=2  * 1024 * 1024)   # 2 MB
MAX_DOCUMENT_SIZE = env.int("MAX_DOCUMENT_SIZE", default=25 * 1024 * 1024)   # 25 MB
MAX_INVOICE_SIZE  = env.int("MAX_INVOICE_SIZE",  default=10 * 1024 * 1024)   # 10 MB
MAX_REPORT_SIZE   = env.int("MAX_REPORT_SIZE",   default=25 * 1024 * 1024)   # 25 MB
MAX_CONTRACT_SIZE = env.int("MAX_CONTRACT_SIZE", default=50 * 1024 * 1024)   # 50 MB
MAX_BANNER_SIZE   = env.int("MAX_BANNER_SIZE",   default=10 * 1024 * 1024)   # 10 MB
```

| Setting             | Default | Use Case               |
| ------------------- | ------- | ---------------------- |
| `MAX_IMAGE_SIZE`    | 5 MB    | Product/general images |
| `MAX_AVATAR_SIZE`   | 2 MB    | User profile pictures  |
| `MAX_DOCUMENT_SIZE` | 25 MB   | PDF, DOCX, XLSX, etc.  |
| `MAX_INVOICE_SIZE`  | 10 MB   | Invoice attachments    |
| `MAX_REPORT_SIZE`   | 25 MB   | Generated reports      |
| `MAX_CONTRACT_SIZE` | 50 MB   | Legal contracts        |
| `MAX_BANNER_SIZE`   | 10 MB   | Marketing banners      |

### Dynamic Size Checking

```python
from apps.core.storage.constants import (
    validate_image_size,
    validate_document_size,
    get_max_size_for_extension,
)

ok, max_size, error = validate_image_size(file_size)
ok, max_size, error = validate_document_size(file_size)
max_size = get_max_size_for_extension(".pdf")  # returns MAX_DOCUMENT_SIZE
```

---

## Allowed Extensions

```python
IMAGE_EXTENSIONS    = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff", ".ico"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".csv", ".txt", ".rtf", ".odt", ".ods"}
ARCHIVE_EXTENSIONS  = {".zip", ".tar", ".gz", ".rar", ".7z"}
ALL_ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS | ARCHIVE_EXTENSIONS
```

### Extension Helpers

```python
from apps.core.storage.constants import (
    is_image_extension,
    is_document_extension,
    is_archive_extension,
    get_allowed_extensions_by_type,
)

is_image_extension(".jpg")        # True
is_document_extension(".pdf")     # True
get_allowed_extensions_by_type("image")     # [".jpg", ".jpeg", ".png", …]
get_allowed_extensions_by_type("document")  # [".pdf", ".doc", …]
get_allowed_extensions_by_type("all")       # everything
```

---

## Image Processing Settings

```python
# Thumbnail presets
THUMB_SMALL   = (100, 100)
THUMB_MEDIUM  = (300, 300)
THUMB_LARGE   = (600, 600)
THUMB_PRODUCT = (500, 500)   # Product-specific preset

# Compression defaults
IMAGE_QUALITY = 85            # JPEG/WEBP quality (1-100)
IMAGE_FORMAT  = "WEBP"        # Default output format for web optimisation
```

### Thumbnail Use-Case Mapping

Defined in `apps.core.storage.constants`:

| Use Case         | Maps To  | Size      |
| ---------------- | -------- | --------- |
| `product_list`   | `small`  | 100 × 100 |
| `product_detail` | `large`  | 600 × 600 |
| `cart`           | `small`  | 100 × 100 |
| `avatar`         | `small`  | 100 × 100 |
| `banner`         | `large`  | 600 × 600 |
| `admin_list`     | `medium` | 300 × 300 |

```python
from apps.core.storage.constants import get_thumbnail_size

size = get_thumbnail_size("product_list")   # (100, 100)
size = get_thumbnail_size("product_detail") # (600, 600)
```

---

## Signed URL Configuration

```python
AWS_PRESIGNED_URL_EXPIRY = env.int("AWS_PRESIGNED_URL_EXPIRY", default=3600)
```

### Expiry Presets (constants.py)

| Constant                     | Value     | When to Use                  |
| ---------------------------- | --------- | ---------------------------- |
| `SIGNED_URL_SHORT_EXPIRY`    | 1 800 s   | Temporary previews           |
| `SIGNED_URL_DEFAULT_EXPIRY`  | 3 600 s   | General file access          |
| `SIGNED_URL_MEDIUM_EXPIRY`   | 14 400 s  | Report downloads             |
| `SIGNED_URL_LONG_EXPIRY`     | 86 400 s  | Shared links (24 hours)      |
| `SIGNED_URL_EXTENDED_EXPIRY` | 604 800 s | External partner access (7d) |

### Per-Type Mapping

The `SIGNED_URL_EXPIRY_BY_TYPE` dict in `constants.py` maps file types to
their recommended expiry period. The `get_signed_url_expiry()` helper resolves
the appropriate expiry by file type or by inspecting the file path.

```python
from apps.core.storage.constants import get_signed_url_expiry

expiry = get_signed_url_expiry(file_type="invoice")            # 3600
expiry = get_signed_url_expiry(file_path="reports/q4.pdf")     # inferred
expiry = get_signed_url_expiry()                               # 3600 (default)
```

---

## Tenant Storage Quotas

Per-plan storage quotas are defined for multi-tenant deployments:

```python
TENANT_STORAGE_QUOTAS = {
    "free":       1  * 1024 * 1024 * 1024,   #  1 GB
    "basic":      10 * 1024 * 1024 * 1024,   # 10 GB
    "pro":        50 * 1024 * 1024 * 1024,   # 50 GB
    "enterprise": None,                       # Unlimited
}
```

| Plan       | Quota     |
| ---------- | --------- |
| Free       | 1 GB      |
| Basic      | 10 GB     |
| Pro        | 50 GB     |
| Enterprise | Unlimited |

---

## Malware Scanning

Optional malware scanning can be enabled on file uploads:

```python
ENABLE_MALWARE_SCANNING = env.bool("ENABLE_MALWARE_SCANNING", default=False)
```

### Supported Scanners

| Scanner    | Requirement          | Configuration            |
| ---------- | -------------------- | ------------------------ |
| ClamAV     | `pyclamd` + ClamAV   | Connects via Unix socket |
| VirusTotal | `VIRUSTOTAL_API_KEY` | Cloud API, rate-limited  |

```python
from apps.core.storage import FileValidator

v = FileValidator(allowed_extensions={".pdf"}, max_size=25 * MB)
v.scan_for_malware(uploaded_file, scanner="clamav")
```

The `validate_all()` method automatically runs the scan when enabled.

---

## Django STORAGES Dictionary

The system auto-configures Django's `STORAGES` setting:

### Local mode

```python
STORAGES = {
    "default": {
        "BACKEND": "apps.core.storage.backends.TenantFileStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
```

### S3 mode

```python
STORAGES = {
    "default": {
        "BACKEND": "apps.core.storage.backends.TenantS3Storage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
}
```

---

## Environment Variable Reference

Complete list of environment variables for the storage system:

| Variable                   | Type | Default     | Required (S3) |
| -------------------------- | ---- | ----------- | ------------- |
| `STORAGE_BACKEND`          | str  | `local`     | —             |
| `MEDIA_URL`                | str  | `/media/`   | —             |
| `AWS_ACCESS_KEY_ID`        | str  | —           | ✅            |
| `AWS_SECRET_ACCESS_KEY`    | str  | —           | ✅            |
| `AWS_STORAGE_BUCKET_NAME`  | str  | —           | ✅            |
| `AWS_S3_REGION_NAME`       | str  | —           | ✅            |
| `AWS_S3_CUSTOM_DOMAIN`     | str  | `None`      | —             |
| `AWS_S3_ENDPOINT_URL`      | str  | `None`      | —             |
| `AWS_PRESIGNED_URL_EXPIRY` | int  | `3600`      | —             |
| `AWS_PRIVATE_BUCKET_NAME`  | str  | main bucket | —             |
| `AWS_PUBLIC_BUCKET_NAME`   | str  | main bucket | —             |
| `MAX_IMAGE_SIZE`           | int  | `5242880`   | —             |
| `MAX_AVATAR_SIZE`          | int  | `2097152`   | —             |
| `MAX_DOCUMENT_SIZE`        | int  | `26214400`  | —             |
| `MAX_INVOICE_SIZE`         | int  | `10485760`  | —             |
| `MAX_REPORT_SIZE`          | int  | `26214400`  | —             |
| `MAX_CONTRACT_SIZE`        | int  | `52428800`  | —             |
| `MAX_BANNER_SIZE`          | int  | `10485760`  | —             |
| `ENABLE_MALWARE_SCANNING`  | bool | `False`     | —             |
| `VIRUSTOTAL_API_KEY`       | str  | —           | —             |

---

## See Also

- [Storage Overview](overview.md) – architecture, API reference, quick start
- [Performance & Tuning](performance.md) – CDN, caching, async processing
