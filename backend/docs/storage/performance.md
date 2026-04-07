# File Storage Performance & Tuning

> **Goal:** minimise upload latency, reduce storage costs, and keep tenant
> file operations responsive under load.

---

## Async Image Processing

Images ≥ 1 MB are processed asynchronously via Celery to avoid blocking the
HTTP request/response cycle.

```
┌──────────┐        ┌──────────────┐       ┌────────────────┐
│  Request  │──►     │ Save raw     │──►    │  Celery task:  │
│  (upload) │        │ to storage   │       │  optimize +    │
└──────────┘        └──────────────┘       │  thumbnails    │
                                           └────────────────┘
```

### Tuning Celery Workers

```python
# config/settings/celery.py
CELERY_TASK_SOFT_TIME_LIMIT = 120   # 2 min per image
CELERY_TASK_TIME_LIMIT = 180        # hard kill at 3 min
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # fair scheduling
```

For dedicated image processing, add a named queue:

```python
CELERY_TASK_ROUTES = {
    "apps.core.storage.tasks.*": {"queue": "images"},
}
```

```bash
celery -A config worker -Q images -c 4 --max-tasks-per-child=50
```

---

## Image Optimisation

### Format Selection

| Format | Use When                    | Quality Savings |
| ------ | --------------------------- | --------------- |
| WEBP   | Modern browsers (default)   | ~30% vs JPEG    |
| JPEG   | Legacy compatibility needed | Baseline        |
| PNG    | Transparency required       | Larger files    |

### Compression Quality

```python
IMAGE_QUALITY = 85   # Good balance of size vs quality
```

| Quality | Typical File Size (1920×1080) | Visual Impact      |
| ------- | ----------------------------- | ------------------ |
| 95      | ~500 KB                       | Near-lossless      |
| 85      | ~250 KB                       | Imperceptible loss |
| 70      | ~150 KB                       | Slight softening   |
| 50      | ~80 KB                        | Visible artefacts  |

### Thumbnail Pre-generation

Generate all thumbnail sizes on upload to avoid on-the-fly resize:

```python
# In post-upload Celery task
proc = ImageProcessor(stored_file)
thumbs = proc.generate_thumbnails(THUMBNAIL_SIZES)
for name, thumb_proc in thumbs.items():
    storage.save(f"thumbs/{name}/{product_id}.webp", thumb_proc.save(format="WEBP"))
```

---

## CDN Integration

### CloudFront with S3

```python
AWS_S3_CUSTOM_DOMAIN = "cdn.example.com"
```

When `AWS_S3_CUSTOM_DOMAIN` is set, all media URLs use the CDN domain instead
of the raw S3 URL. Combined with `PublicTenantS3Storage`, public assets are
served directly from CloudFront without signed URLs.

### Cache Headers

```python
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",  # 24-hour browser cache
}
```

For immutable assets (UUID-named files), extend to 1 year:

```python
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=31536000, immutable",
}
```

---

## Storage Cleanup Scheduling

Run the cleanup job periodically to reclaim disk / S3 space:

### Celery Beat

```python
CELERY_BEAT_SCHEDULE = {
    "cleanup-orphaned-media": {
        "task": "apps.core.storage.tasks.cleanup_orphaned_files",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
        "kwargs": {"days_old": 30, "dry_run": False},
    },
}
```

### Cron (non-Celery deployments)

```bash
0 3 * * * cd /app && python manage.py cleanmedia --force --min-age-days=30
```

---

## Monitoring

### Key Metrics to Track

| Metric                 | Source            | Alert Threshold  |
| ---------------------- | ----------------- | ---------------- |
| Upload latency (p95)   | APM / middleware  | > 2 s            |
| Async task queue depth | Celery Flower     | > 100 pending    |
| Tenant storage usage   | Periodic script   | > 80% of quota   |
| S3 error rate          | CloudWatch        | > 1% of requests |
| Orphaned files (count) | cleanmedia output | > 1000           |

### Quota Enforcement

```python
from config.settings.storage import TENANT_STORAGE_QUOTAS

tenant_plan = tenant.plan  # "free" | "basic" | "pro" | "enterprise"
quota = TENANT_STORAGE_QUOTAS.get(tenant_plan)
if quota and current_usage > quota:
    raise ValidationError("Storage quota exceeded")
```

---

## Best Practices

1. **Always use UUID filenames** – the path generators do this by default;
   avoids collisions and enables immutable caching.
2. **Validate before storing** – call `FileValidator.validate_all()` prior
   to saving to reject bad files early.
3. **Prefer WEBP** – ~30% smaller than JPEG with no visible quality loss.
4. **Pre-generate thumbnails** – avoid on-the-fly resize on page load.
5. **Set CDN cache headers** – immutable UUID filenames enable aggressive
   caching (1 year).
6. **Schedule cleanup** – run `cleanmedia` weekly or daily to avoid orphan
   buildup.
7. **Separate buckets** – put private files (`invoices`, `contracts`) in a
   private bucket; public assets (`product images`, `banners`) in a public one.
8. **Monitor quotas** – alert before tenants hit limits to allow proactive
   plan upgrades.

---

## See Also

- [Storage Overview](overview.md) – architecture, quick start, API
- [Configuration Guide](configuration.md) – all settings reference
