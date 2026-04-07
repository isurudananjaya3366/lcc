# Environment Variables Reference

> **LankaCommerce Cloud (LCC)** — Comprehensive environment variable guide for backend, frontend, and Docker environments.

---

## Table of Contents

- [Overview & Conventions](#overview--conventions)
- [Backend Variables](#backend-variables)
  - [Security](#security)
  - [Database](#database)
  - [Redis / Cache](#redis--cache)
  - [Celery](#celery)
  - [Email / SMTP](#email--smtp)
  - [AWS / S3](#aws--s3)
  - [CORS](#cors)
  - [JWT](#jwt)
  - [Sentry](#sentry)
  - [Stripe](#stripe)
  - [SMS](#sms)
  - [AI / OpenAI](#ai--openai)
  - [Site / App](#site--app)
  - [Multi-Tenancy](#multi-tenancy)
  - [Security (Additional)](#security-additional)
- [Frontend Variables](#frontend-variables)
  - [Client-Side (NEXT_PUBLIC\_)](#client-side-next_public_)
  - [Server-Side Only](#server-side-only)
- [Docker-Specific Variables](#docker-specific-variables)
- [Environment File Loading Order](#environment-file-loading-order)
- [Troubleshooting](#troubleshooting)
- [Related Documentation](#related-documentation)

---

## Overview & Conventions

### Naming Conventions

| Prefix / Pattern | Scope                             | Example                           |
| ---------------- | --------------------------------- | --------------------------------- |
| `DJANGO_*`       | Django framework settings         | `DJANGO_SECRET_KEY`               |
| `DB_*`           | Database connection               | `DB_HOST`, `DB_PORT`              |
| `CELERY_*`       | Celery task queue                 | `CELERY_BROKER_URL`               |
| `NEXT_PUBLIC_*`  | Frontend — **exposed to browser** | `NEXT_PUBLIC_API_URL`             |
| _(no prefix)_    | Frontend server-side only         | `API_BASE_URL`, `NEXTAUTH_SECRET` |
| `POSTGRES_*`     | Docker Postgres init only         | `POSTGRES_DB`                     |
| `AWS_*`          | AWS / S3 storage                  | `AWS_ACCESS_KEY_ID`               |

### Value Types

| Type    | Format                                                    | Examples                                |
| ------- | --------------------------------------------------------- | --------------------------------------- |
| `str`   | Plain string                                              | `config.settings.local`                 |
| `bool`  | `True` / `False` (backend) or `true` / `false` (frontend) | `True`, `false`                         |
| `int`   | Integer number                                            | `5432`, `30`                            |
| `float` | Decimal number                                            | `0.1`                                   |
| `list`  | Comma-separated values                                    | `localhost,127.0.0.1,.lankacommerce.lk` |

### Required Status Legend

| Label               | Meaning                                   |
| ------------------- | ----------------------------------------- |
| **Yes**             | Always required in every environment      |
| **Yes (prod)**      | Required in production; optional locally  |
| **No**              | Optional; sensible default provided       |
| **For \<feature\>** | Required only when the feature is enabled |

### General Rules

1. **Never commit secrets** to version control — use `.env` files or a vault.
2. **Production** values must override every `(empty)` and `insecure` default.
3. Boolean values in Django use Python-style `True` / `False`; Next.js uses `true` / `false`.
4. List values are **comma-separated** with no spaces (unless noted).
5. URLs should **not** have a trailing slash.

---

## Backend Variables

> Source: `backend/config/env.py` · Loaded via **django-environ**

### Security

| Variable                 | Type | Default                     | Required   | Description                                                                                                                    |
| ------------------------ | ---- | --------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `DJANGO_SECRET_KEY`      | str  | `django-insecure-CHANGE-ME` | Yes (prod) | Django cryptographic signing key used for sessions, tokens, and CSRF. **Must** be a unique, unpredictable value in production. |
| `DEBUG`                  | bool | `False`                     | No         | Enable Django debug mode. **Never** enable in production.                                                                      |
| `ALLOWED_HOSTS`          | list | `[]`                        | Yes (prod) | Comma-separated list of hostnames the server will respond to.                                                                  |
| `DJANGO_SETTINGS_MODULE` | str  | `config.settings.local`     | Yes        | Python path to the active settings module.                                                                                     |
| `LOG_LEVEL`              | str  | `INFO`                      | No         | Root logger level. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.                                                     |

**Example:**

```bash
DJANGO_SECRET_KEY="y0ur-super-s3cr3t-key-here-$(openssl rand -hex 32)"
DEBUG=False
ALLOWED_HOSTS=lankacommerce.lk,.lankacommerce.lk,api.lankacommerce.lk
DJANGO_SETTINGS_MODULE=config.settings.production
LOG_LEVEL=WARNING
```

---

### Database

| Variable       | Type | Default                                                     | Required   | Description                                                                   |
| -------------- | ---- | ----------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------- |
| `DATABASE_URL` | str  | `postgres://postgres:postgres@localhost:5432/lankacommerce` | Yes        | Full PostgreSQL connection URL. Takes precedence over individual `DB_*` vars. |
| `DB_ENGINE`    | str  | `django.db.backends.postgresql`                             | No         | Django database engine.                                                       |
| `DB_HOST`      | str  | `localhost`                                                 | No         | Database server hostname.                                                     |
| `DB_PORT`      | int  | `5432`                                                      | No         | Database server port.                                                         |
| `DB_NAME`      | str  | `lankacommerce_dev`                                         | No         | Database name.                                                                |
| `DB_USER`      | str  | `lcc_user`                                                  | No         | Database username.                                                            |
| `DB_PASSWORD`  | str  | _(empty)_                                                   | Yes (prod) | Database password.                                                            |

> **Note:** When `DATABASE_URL` is provided, the individual `DB_*` variables are ignored.

**Example:**

```bash
DATABASE_URL=postgres://lcc_user:strong_password@db:5432/lankacommerce
```

---

### Redis / Cache

| Variable    | Type | Default                    | Required | Description                                                |
| ----------- | ---- | -------------------------- | -------- | ---------------------------------------------------------- |
| `REDIS_URL` | str  | `redis://localhost:6379/0` | Yes      | Primary Redis connection URL.                              |
| `CACHE_URL` | str  | `redis://localhost:6379/1` | No       | Django cache backend URL (uses a separate Redis DB index). |

**Example:**

```bash
REDIS_URL=redis://redis:6379/0
CACHE_URL=redis://redis:6379/1
```

---

### Celery

| Variable                | Type | Default                                           | Required | Description                                         |
| ----------------------- | ---- | ------------------------------------------------- | -------- | --------------------------------------------------- |
| `CELERY_BROKER_URL`     | str  | `redis://localhost:6379/0`                        | Yes      | Message broker URL for Celery workers.              |
| `CELERY_RESULT_BACKEND` | str  | `redis://localhost:6379/0`                        | No       | Backend for storing task results.                   |
| `CELERY_APP`            | str  | `config.celery:app`                               | No       | Python path to the Celery application instance.     |
| `CELERY_CONCURRENCY`    | int  | `2`                                               | No       | Number of concurrent worker processes/threads.      |
| `CELERY_LOG_LEVEL`      | str  | `info`                                            | No       | Celery worker log level.                            |
| `CELERY_QUEUES`         | str  | `default,high_priority,low_priority`              | No       | Comma-separated list of queues the worker consumes. |
| `CELERY_BEAT_SCHEDULER` | str  | `django_celery_beat.schedulers:DatabaseScheduler` | No       | Scheduler class for periodic tasks.                 |

**Example:**

```bash
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_CONCURRENCY=4
CELERY_LOG_LEVEL=info
CELERY_QUEUES=default,high_priority,low_priority
```

---

### Email / SMTP

| Variable              | Type | Default                                          | Required   | Description                                                                           |
| --------------------- | ---- | ------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------- |
| `EMAIL_BACKEND`       | str  | `django.core.mail.backends.console.EmailBackend` | No         | Email backend class. Use `django.core.mail.backends.smtp.EmailBackend` in production. |
| `EMAIL_HOST`          | str  | `smtp.gmail.com`                                 | No         | SMTP server hostname.                                                                 |
| `EMAIL_PORT`          | int  | `587`                                            | No         | SMTP server port.                                                                     |
| `EMAIL_HOST_USER`     | str  | _(empty)_                                        | Yes (prod) | SMTP authentication username.                                                         |
| `EMAIL_HOST_PASSWORD` | str  | _(empty)_                                        | Yes (prod) | SMTP authentication password or app-specific password.                                |
| `EMAIL_USE_TLS`       | bool | `True`                                           | No         | Enable STARTTLS for the SMTP connection.                                              |
| `DEFAULT_FROM_EMAIL`  | str  | `noreply@lankacommerce.lk`                       | No         | Default "From" address for outgoing emails.                                           |

**Example (production):**

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=notifications@lankacommerce.lk
EMAIL_HOST_PASSWORD=app-specific-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL="LankaCommerce <noreply@lankacommerce.lk>"
```

---

### AWS / S3

| Variable                  | Type | Default                                       | Required      | Description                                                                            |
| ------------------------- | ---- | --------------------------------------------- | ------------- | -------------------------------------------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`       | str  | _(empty)_                                     | For S3        | IAM access key ID.                                                                     |
| `AWS_SECRET_ACCESS_KEY`   | str  | _(empty)_                                     | For S3        | IAM secret access key.                                                                 |
| `AWS_STORAGE_BUCKET_NAME` | str  | `lcc-media-dev`                               | For S3        | S3 bucket name for media uploads.                                                      |
| `AWS_S3_REGION_NAME`      | str  | `ap-south-1`                                  | For S3        | AWS region (Mumbai is closest to Sri Lanka).                                           |
| `AWS_S3_ENDPOINT_URL`     | str  | _(empty)_                                     | For S3-compat | Custom endpoint for S3-compatible stores (e.g., MinIO, DigitalOcean Spaces).           |
| `DEFAULT_FILE_STORAGE`    | str  | `django.core.files.storage.FileSystemStorage` | No            | Django file storage backend. Set to `storages.backends.s3boto3.S3Boto3Storage` for S3. |

**Example (production with S3):**

```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=lcc-media-prod
AWS_S3_REGION_NAME=ap-south-1
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
```

---

### CORS

| Variable                 | Type | Default                 | Required | Description                                                            |
| ------------------------ | ---- | ----------------------- | -------- | ---------------------------------------------------------------------- |
| `CORS_ALLOWED_ORIGINS`   | list | `http://localhost:3000` | Yes      | Comma-separated list of origins permitted for cross-origin requests.   |
| `CORS_ALLOW_CREDENTIALS` | bool | `True`                  | No       | Whether cookies and auth headers are allowed in cross-origin requests. |

**Example:**

```bash
CORS_ALLOWED_ORIGINS=https://lankacommerce.lk,https://admin.lankacommerce.lk
CORS_ALLOW_CREDENTIALS=True
```

---

### JWT

| Variable                            | Type | Default | Required | Description                                     |
| ----------------------------------- | ---- | ------- | -------- | ----------------------------------------------- |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | int  | `30`    | No       | Access token validity in minutes.               |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS`   | int  | `7`     | No       | Refresh token validity in days.                 |
| `JWT_ROTATE_REFRESH_TOKENS`         | bool | `True`  | No       | Issue a new refresh token on each refresh.      |
| `JWT_BLACKLIST_AFTER_ROTATION`      | bool | `True`  | No       | Blacklist the old refresh token after rotation. |

**Example:**

```bash
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
JWT_ROTATE_REFRESH_TOKENS=True
JWT_BLACKLIST_AFTER_ROTATION=True
```

---

### Sentry

| Variable                    | Type  | Default   | Required       | Description                                                                     |
| --------------------------- | ----- | --------- | -------------- | ------------------------------------------------------------------------------- |
| `SENTRY_DSN`                | str   | _(empty)_ | For monitoring | Sentry project DSN (Data Source Name).                                          |
| `SENTRY_ENVIRONMENT`        | str   | `local`   | No             | Environment tag sent with every event (e.g., `local`, `staging`, `production`). |
| `SENTRY_TRACES_SAMPLE_RATE` | float | `0.1`     | No             | Percentage of transactions to trace (`0.0` – `1.0`).                            |

**Example:**

```bash
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.2
```

---

### Stripe

| Variable                 | Type | Default      | Required     | Description                                              |
| ------------------------ | ---- | ------------ | ------------ | -------------------------------------------------------- |
| `STRIPE_SECRET_KEY`      | str  | _(empty)_    | For payments | Stripe secret key (`sk_test_...` or `sk_live_...`).      |
| `STRIPE_PUBLISHABLE_KEY` | str  | _(empty)_    | For payments | Stripe publishable key (`pk_test_...` or `pk_live_...`). |
| `STRIPE_WEBHOOK_SECRET`  | str  | _(empty)_    | For webhooks | Stripe webhook signing secret (`whsec_...`).             |
| `STRIPE_API_VERSION`     | str  | `2024-06-20` | No           | Pinned Stripe API version for deterministic behavior.    |

**Example:**

```bash
STRIPE_SECRET_KEY=sk_test_51Abc...
STRIPE_PUBLISHABLE_KEY=pk_test_51Abc...
STRIPE_WEBHOOK_SECRET=whsec_abc123...
STRIPE_API_VERSION=2024-06-20
```

---

### SMS

| Variable        | Type | Default   | Required | Description                                    |
| --------------- | ---- | --------- | -------- | ---------------------------------------------- |
| `SMS_PROVIDER`  | str  | _(empty)_ | For SMS  | SMS gateway provider name.                     |
| `SMS_API_KEY`   | str  | _(empty)_ | For SMS  | Provider API key.                              |
| `SMS_SENDER_ID` | str  | `LCC`     | No       | Sender ID displayed on the recipient's device. |

---

### AI / OpenAI

| Variable            | Type | Default       | Required | Description                            |
| ------------------- | ---- | ------------- | -------- | -------------------------------------- |
| `OPENAI_API_KEY`    | str  | _(empty)_     | For AI   | OpenAI API key.                        |
| `OPENAI_MODEL`      | str  | `gpt-4o-mini` | No       | Model identifier for AI requests.      |
| `OPENAI_MAX_TOKENS` | int  | `4096`        | No       | Maximum tokens per completion request. |

---

### Site / App

| Variable        | Type | Default                    | Required | Description                                      |
| --------------- | ---- | -------------------------- | -------- | ------------------------------------------------ |
| `SITE_NAME`     | str  | `LankaCommerce Cloud`      | No       | Application display name.                        |
| `SITE_URL`      | str  | `http://localhost:3000`    | No       | Canonical frontend URL (used for emails, links). |
| `SUPPORT_EMAIL` | str  | `support@lankacommerce.lk` | No       | Support contact email address.                   |
| `LANGUAGE_CODE` | str  | `en-us`                    | No       | Django i18n default language.                    |
| `TIME_ZONE`     | str  | `Asia/Colombo`             | No       | IANA timezone for the application.               |

---

### Multi-Tenancy

| Variable              | Type | Default          | Required | Description                                        |
| --------------------- | ---- | ---------------- | -------- | -------------------------------------------------- |
| `TENANT_MODEL`        | str  | `tenants.Tenant` | Yes      | Python path to the Tenant model.                   |
| `TENANT_DOMAIN_MODEL` | str  | `tenants.Domain` | Yes      | Python path to the Domain model.                   |
| `PUBLIC_SCHEMA_NAME`  | str  | `public`         | No       | PostgreSQL schema used for shared (public) tables. |

---

### Security (Additional)

| Variable               | Type | Default                 | Required           | Description                                                                     |
| ---------------------- | ---- | ----------------------- | ------------------ | ------------------------------------------------------------------------------- |
| `CSRF_TRUSTED_ORIGINS` | str  | `http://localhost:3000` | Yes (prod)         | Comma-separated origins trusted for CSRF. Must match actual deployment domains. |
| `SECURE_SSL_REDIRECT`  | bool | `False`                 | Yes (prod: `True`) | Redirect all HTTP requests to HTTPS.                                            |

**Example (production):**

```bash
CSRF_TRUSTED_ORIGINS=https://lankacommerce.lk,https://admin.lankacommerce.lk
SECURE_SSL_REDIRECT=True
```

---

## Frontend Variables

> Source: `frontend/.env.local` · Loaded by **Next.js** automatically

### Client-Side (`NEXT_PUBLIC_`)

> ⚠️ **These variables are embedded into the JavaScript bundle at build time and are visible to end users.** Never put secrets here.

| Variable                          | Default                        | Required | Description                                             |
| --------------------------------- | ------------------------------ | -------- | ------------------------------------------------------- |
| `NEXT_PUBLIC_API_URL`             | `http://localhost:8000/api/v1` | Yes      | API endpoint called from the **browser**.               |
| `NEXT_PUBLIC_WS_URL`              | `ws://localhost:8000/ws`       | No       | WebSocket endpoint for real-time features.              |
| `NEXT_PUBLIC_SITE_URL`            | `http://localhost:3000`        | Yes      | Canonical frontend URL.                                 |
| `NEXT_PUBLIC_SITE_NAME`           | `LankaCommerce Cloud`          | No       | Full display name (page titles, branding).              |
| `NEXT_PUBLIC_APP_NAME`            | `LCC`                          | No       | Short name (PWA manifest, mobile).                      |
| `NEXT_PUBLIC_SITE_DESCRIPTION`    | `Multi-tenant SaaS...`         | No       | SEO meta description.                                   |
| `NEXT_PUBLIC_APP_URL`             | `http://localhost:3000`        | No       | Application URL (PWA start URL).                        |
| `NEXT_PUBLIC_AUTH_COOKIE_NAME`    | `lcc_auth`                     | No       | Name of the authentication cookie.                      |
| `NEXT_PUBLIC_TOKEN_EXPIRY_BUFFER` | `60`                           | No       | Seconds before expiry to trigger token refresh.         |
| `NEXT_PUBLIC_ENABLE_ANALYTICS`    | `false`                        | No       | Enable/disable analytics tracking.                      |
| `NEXT_PUBLIC_ENABLE_AI_FEATURES`  | `false`                        | No       | Enable/disable AI-powered features.                     |
| `NEXT_PUBLIC_ENABLE_WEBSTORE`     | `true`                         | No       | Enable/disable webstore module.                         |
| `NEXT_PUBLIC_ENABLE_POS`          | `true`                         | No       | Enable/disable POS module.                              |
| `NEXT_PUBLIC_ENABLE_OFFLINE`      | `true`                         | No       | Enable/disable offline mode (service worker).           |
| `NEXT_PUBLIC_DEBUG`               | `false`                        | No       | Enable frontend debug logging.                          |
| `NEXT_PUBLIC_GA_TRACKING_ID`      | _(empty)_                      | No       | Google Analytics measurement ID.                        |
| `NEXT_PUBLIC_SENTRY_DSN`          | _(empty)_                      | No       | Sentry DSN for frontend error tracking.                 |
| `NEXT_PUBLIC_PAYHERE_MERCHANT_ID` | _(empty)_                      | No       | PayHere merchant ID (Sri Lanka payments).               |
| `NEXT_PUBLIC_STRIPE_PUBLIC_KEY`   | _(empty)_                      | No       | Stripe publishable key (`pk_test_...` / `pk_live_...`). |
| `NEXT_PUBLIC_MAPS_API_KEY`        | _(empty)_                      | No       | Google Maps JavaScript API key.                         |
| `NEXT_PUBLIC_DEFAULT_LOCALE`      | `en-LK`                        | No       | BCP 47 locale tag.                                      |
| `NEXT_PUBLIC_DEFAULT_TIMEZONE`    | `Asia/Colombo`                 | No       | IANA timezone for UI display.                           |
| `NEXT_PUBLIC_DEFAULT_CURRENCY`    | `LKR`                          | No       | ISO 4217 currency code.                                 |
| `NEXT_PUBLIC_CURRENCY_SYMBOL`     | `Rs.`                          | No       | Currency display symbol.                                |
| `NEXT_PUBLIC_DEFAULT_TENANT`      | `demo`                         | No       | Default tenant slug for development.                    |
| `NEXT_PUBLIC_TENANT_PATTERN`      | `{tenant}.lankacommerce.lk`    | No       | Tenant subdomain URL pattern.                           |
| `NEXT_PUBLIC_IMAGE_DOMAIN`        | `cdn.lankacommerce.lk`         | No       | Image CDN domain (Next.js `images.domains`).            |
| `NEXT_PUBLIC_CLOUDINARY_CLOUD`    | _(empty)_                      | No       | Cloudinary cloud name for image transforms.             |

**Example:**

```bash
NEXT_PUBLIC_API_URL=https://api.lankacommerce.lk/api/v1
NEXT_PUBLIC_WS_URL=wss://api.lankacommerce.lk/ws
NEXT_PUBLIC_SITE_URL=https://lankacommerce.lk
NEXT_PUBLIC_SITE_NAME="LankaCommerce Cloud"
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_DEFAULT_CURRENCY=LKR
```

---

### Server-Side Only

> These variables are **only** available in Next.js API routes, `getServerSideProps`, server components, and middleware. They are **never** shipped to the browser.

| Variable                | Default                      | Required     | Description                                                                               |
| ----------------------- | ---------------------------- | ------------ | ----------------------------------------------------------------------------------------- |
| `API_BASE_URL`          | `http://backend:8000/api/v1` | Yes          | Backend URL used from SSR and API routes. In Docker this uses the service name `backend`. |
| `API_TIMEOUT`           | `30000`                      | No           | HTTP request timeout in milliseconds.                                                     |
| `NEXTAUTH_URL`          | `http://localhost:3000`      | Yes          | NextAuth.js callback URL. Must match the canonical frontend URL.                          |
| `NEXTAUTH_SECRET`       | _(empty)_                    | Yes (prod)   | Secret used by NextAuth.js to sign/encrypt JWTs.                                          |
| `STRIPE_SECRET_KEY`     | _(empty)_                    | For payments | Stripe secret key (server-side only).                                                     |
| `STRIPE_WEBHOOK_SECRET` | _(empty)_                    | For webhooks | Stripe webhook signing secret.                                                            |
| `SENTRY_AUTH_TOKEN`     | _(empty)_                    | No           | Sentry auth token for uploading source maps during build.                                 |

**Example:**

```bash
API_BASE_URL=http://backend:8000/api/v1
API_TIMEOUT=30000
NEXTAUTH_URL=https://lankacommerce.lk
NEXTAUTH_SECRET=$(openssl rand -base64 32)
```

---

## Docker-Specific Variables

> These values differ between local development (bare-metal) and Docker Compose environments because containers reference each other by **service name** rather than `localhost`.

| Variable               | Docker Value                                                       | Local Value                                                 | Purpose                        |
| ---------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------- | ------------------------------ |
| `DB_HOST`              | `db`                                                               | `localhost`                                                 | PostgreSQL service hostname    |
| `REDIS_HOST`           | `redis`                                                            | `localhost`                                                 | Redis service hostname         |
| `DATABASE_URL`         | `postgres://postgres:dev_password_change_me@db:5432/lankacommerce` | `postgres://postgres:postgres@localhost:5432/lankacommerce` | Full PostgreSQL connection URL |
| `REDIS_URL`            | `redis://redis:6379/0`                                             | `redis://localhost:6379/0`                                  | Redis connection URL           |
| `CELERY_BROKER_URL`    | `redis://redis:6379/0`                                             | `redis://localhost:6379/0`                                  | Celery message broker          |
| `API_BASE_URL`         | `http://backend:8000/api/v1`                                       | `http://localhost:8000/api/v1`                              | Frontend SSR → Backend         |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,backend,0.0.0.0`                              | `localhost,127.0.0.1`                                       | Django allowed hosts           |

### Docker-Only Init Variables

These variables are used **exclusively** by Docker Compose services for first-time initialization and are **not** read by the application code.

| Variable            | Default                  | Service              | Purpose                                                     |
| ------------------- | ------------------------ | -------------------- | ----------------------------------------------------------- |
| `POSTGRES_DB`       | `lankacommerce`          | `db` (PostgreSQL)    | Database created on first run                               |
| `POSTGRES_USER`     | `postgres`               | `db` (PostgreSQL)    | Superuser created on first run                              |
| `POSTGRES_PASSWORD` | `dev_password_change_me` | `db` (PostgreSQL)    | Superuser password                                          |
| `WATCHPACK_POLLING` | `true`                   | `frontend` (Next.js) | Enable file-system polling for hot reload inside containers |
| `NODE_ENV`          | `development`            | `frontend` (Next.js) | Node.js environment mode                                    |
| `FLOWER_PORT`       | `5555`                   | `flower` (Celery)    | Flower monitoring dashboard port                            |
| `FLOWER_BASIC_AUTH` | `admin:admin`            | `flower` (Celery)    | Flower HTTP basic auth credentials                          |

> **Tip:** Copy `.env.docker.example` to `.env.docker` and customize before running `docker compose up`.

---

## Environment File Loading Order

### Backend (Django)

1. System environment variables (highest priority)
2. `.env` file in `backend/` directory (loaded by django-environ)
3. Defaults defined in `config/env.py`

### Frontend (Next.js)

1. System environment variables (highest priority)
2. `.env.local` (git-ignored, local overrides)
3. `.env.development` or `.env.production` (per-environment)
4. `.env` (base defaults, lowest priority)

### Docker Compose

1. Shell environment variables (highest priority)
2. `.env.docker` (project root)
3. `docker-compose.override.yml` `environment:` blocks
4. `docker-compose.yml` `environment:` blocks (lowest priority)

---

## Troubleshooting

### Common Validation Failures

#### ❌ "Variable not found"

**Cause:** The variable is not defined in any loaded `.env` file or system environment.

**Fix:**

1. Verify the `.env` file exists in the expected location.
2. Check the [loading order](#environment-file-loading-order) — a higher-priority source may be shadowing it.
3. Ensure there are no typos in the variable name.
4. For Docker, confirm the variable is in `.env.docker` or the `environment:` block in `docker-compose.yml`.

---

#### ❌ "Invalid DATABASE_URL format"

**Cause:** The URL does not conform to the expected `postgres://` scheme.

**Fix:**

```bash
# ✅ Correct
DATABASE_URL=postgres://user:password@host:5432/dbname

# ❌ Wrong scheme
DATABASE_URL=postgresql://user:password@host:5432/dbname

# ❌ Missing components
DATABASE_URL=postgres://localhost/dbname
```

> **Note:** Django-environ expects `postgres://`, not `postgresql://`.

---

#### ❌ "DJANGO_SECRET_KEY is insecure"

**Cause:** The key still has the default `django-insecure-CHANGE-ME` value.

**Fix:** Generate a new cryptographic key:

```bash
# Using Python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Using OpenSSL
openssl rand -hex 50
```

Set the generated value in your `.env` file:

```bash
DJANGO_SECRET_KEY="your-generated-secret-key-here"
```

---

#### ❌ "NEXT_PUBLIC_API_URL unreachable"

**Cause:** The frontend cannot reach the backend API.

**Fix:**

1. Confirm the backend is running: `curl http://localhost:8000/api/v1/health/`
2. In Docker, ensure both services are on the same network and the frontend uses `http://backend:8000/api/v1` for SSR (`API_BASE_URL`) and `http://localhost:8000/api/v1` for browser requests (`NEXT_PUBLIC_API_URL`).
3. Check that `CORS_ALLOWED_ORIGINS` includes the frontend origin.

---

#### ❌ "CELERY_BROKER_URL connection refused"

**Cause:** Redis is not running or not reachable.

**Fix:**

1. Verify Redis is running: `redis-cli ping` (should return `PONG`).
2. In Docker, ensure the Redis service is healthy: `docker compose ps redis`.
3. Confirm the URL uses the correct hostname (`redis` in Docker, `localhost` locally).

---

#### ❌ "NEXTAUTH_SECRET not set"

**Cause:** `NEXTAUTH_SECRET` is empty or missing in production.

**Fix:** Generate a secret and add it to your environment:

```bash
openssl rand -base64 32
```

```bash
NEXTAUTH_SECRET="your-generated-base64-secret"
```

> This variable is **required** in production. NextAuth.js will refuse to start without it.

---

#### ❌ "CORS/CSRF origin mismatch"

**Cause:** The `CORS_ALLOWED_ORIGINS` or `CSRF_TRUSTED_ORIGINS` do not match the actual domain the frontend is served from.

**Fix:**

- Both variables must include the **exact** origin (scheme + host + port if non-standard).
- They must match the domain users see in their browser address bar.

```bash
# ✅ Correct — matches deployment domain
CORS_ALLOWED_ORIGINS=https://lankacommerce.lk,https://admin.lankacommerce.lk
CSRF_TRUSTED_ORIGINS=https://lankacommerce.lk,https://admin.lankacommerce.lk

# ❌ Wrong — trailing slash, missing scheme, or mismatched domain
CORS_ALLOWED_ORIGINS=https://lankacommerce.lk/,lankacommerce.lk
```

---

### Validation Commands

| Command                    | Description                                                        |
| -------------------------- | ------------------------------------------------------------------ |
| `make validate-env`        | Run basic environment validation (warns on missing optional vars). |
| `make validate-env-strict` | Strict validation — fails on any missing required variable.        |
| `make validate-env-docker` | Validate the Docker-specific `.env.docker` file.                   |

```bash
# Quick validation
make validate-env

# Strict mode for CI/CD pipelines
make validate-env-strict

# Docker environment check
make validate-env-docker
```

---

## Related Documentation

| Resource                                | Description                            |
| --------------------------------------- | -------------------------------------- |
| [docs/DOCKER_ENV.md](DOCKER_ENV.md)     | Docker environment setup guide         |
| [docs/SECRETS.md](SECRETS.md)           | Secrets management policy              |
| [docs/docker-setup.md](docker-setup.md) | Docker development setup walkthrough   |
| `backend/.env.example`                  | Backend environment template           |
| `frontend/.env.local.example`           | Frontend environment template          |
| `.env.docker.example`                   | Docker environment template            |
| `scripts/validate_env.py`               | Backend environment validation script  |
| `frontend/scripts/check-env.js`         | Frontend environment validation script |

---

_Last updated: 2026-02-15_
