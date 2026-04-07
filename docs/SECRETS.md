# Secrets Management — LankaCommerce Cloud

> **Document Series**: Infrastructure & Security  
> **Tasks Covered**: 69 · 70 · 71 · 72 · 73  
> **Last Updated**: 2026-02-15  
> **Status**: Active

---

## Table of Contents

1. [Overview & Scope](#1-overview--scope)
2. [Sensitivity Classification](#2-sensitivity-classification)
3. [Development Secrets Handling](#3-development-secrets-handling)
4. [Staging Secrets Handling](#4-staging-secrets-handling)
5. [Production Secrets Handling](#5-production-secrets-handling)
6. [Access Control Matrix](#6-access-control-matrix)
7. [Secret Rotation Policy](#7-secret-rotation-policy)
8. [Incident Response](#8-incident-response)
9. [Related Documentation](#9-related-documentation)

---

## 1. Overview & Scope

### 1.1 Purpose

This document defines how secrets — credentials, API keys, tokens, and sensitive configuration — are managed across every environment of the **LankaCommerce Cloud** platform. It establishes classification tiers, handling procedures, access controls, and audit requirements so that no secret is stored in plain text in version control, logs, or client bundles.

### 1.2 Scope

| In Scope                                                   | Out of Scope                                               |
| ---------------------------------------------------------- | ---------------------------------------------------------- |
| All environment variables containing credentials or keys   | Application-level RBAC / tenant permissions                |
| Connection strings for PostgreSQL, Redis, third-party APIs | End-user passwords (managed by Django auth)                |
| JWT / session signing material                             | SSL/TLS certificate provisioning (see infrastructure docs) |
| Cloud provider credentials (AWS, payment gateways)         | Domain & DNS configuration                                 |
| CI/CD pipeline secrets (GitHub Actions)                    | Infrastructure-as-Code templates (Terraform, etc.)         |

### 1.3 Platform Architecture Context

LankaCommerce Cloud is a **multi-tenant SaaS ERP** platform targeting Sri Lankan SMEs. The system comprises:

| Component      | Technology                     | Relevant Secrets                                |
| -------------- | ------------------------------ | ----------------------------------------------- |
| Backend API    | Django REST Framework          | `DJANGO_SECRET_KEY`, DB credentials, JWT keys   |
| Frontend       | Next.js (App Router)           | `NEXTAUTH_SECRET`, `NEXT_PUBLIC_*` (non-secret) |
| Database       | PostgreSQL 15+                 | `POSTGRES_PASSWORD`, `DATABASE_URL`             |
| Cache / Broker | Redis 7+                       | `REDIS_URL`, `CELERY_BROKER_URL`                |
| Task Queue     | Celery Worker + Beat           | Broker/backend URLs, concurrency config         |
| Monitoring     | Flower, Sentry                 | `FLOWER_BASIC_AUTH`, `SENTRY_DSN`               |
| Payments       | PayHere, Stripe                | Merchant secrets, webhook secrets               |
| Messaging      | SMS Gateway, WhatsApp Business | API keys, tokens                                |
| AI Features    | OpenAI                         | `OPENAI_API_KEY`                                |
| Email          | SMTP                           | `EMAIL_HOST_PASSWORD`                           |
| Cloud Storage  | AWS S3                         | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`    |

### 1.4 Guiding Principles

1. **Least Privilege** — every person and service gets the minimum access required.
2. **Defense in Depth** — secrets are protected at rest, in transit, and in use.
3. **Zero Plain-Text Commits** — no real secret value is ever committed to Git.
4. **Auditability** — every secret access in staging/production is logged.
5. **Rotation Without Downtime** — secrets can be rotated without service interruption.

---

## 2. Sensitivity Classification

Every secret or configuration variable is assigned to one of three tiers. The tier determines storage requirements, access controls, rotation frequency, and breach-response urgency.

### 2.1 Tier Definitions

| Tier          | Label        | Description                                                                                                                                     | Breach Impact                                       |
| ------------- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 🔴 **HIGH**   | Restricted   | Credentials and keys granting write/admin access to critical systems. Compromise leads to data breach, financial loss, or full system takeover. | **Critical** — immediate incident response required |
| 🟡 **MEDIUM** | Confidential | Configuration that reveals infrastructure topology or grants limited/read access. Compromise enables reconnaissance or partial access.          | **High** — investigate within 4 hours               |
| 🟢 **LOW**    | Internal     | Public-facing configuration, feature flags, UI defaults. Exposure has negligible security impact.                                               | **Low** — review in next sprint                     |

### 2.2 Complete Variable Classification

#### 🔴 HIGH — Restricted Secrets

| Variable                  | Service         | Description                                        | Rotation Cycle             |
| ------------------------- | --------------- | -------------------------------------------------- | -------------------------- |
| `DJANGO_SECRET_KEY`       | Django          | Cryptographic signing for sessions, tokens, CSRF   | 90 days                    |
| `POSTGRES_PASSWORD`       | PostgreSQL      | Database superuser / app-user password             | 90 days                    |
| `DB_PASSWORD`             | Django          | Application-level DB credential (alias)            | 90 days                    |
| `JWT_SIGNING_KEY`         | Django / Auth   | RSA or HMAC key for JWT token signing              | 90 days                    |
| `NEXTAUTH_SECRET`         | Next.js         | NextAuth.js session encryption key                 | 90 days                    |
| `STRIPE_SECRET_KEY`       | Stripe          | Full API access — charges, refunds, customers      | 180 days                   |
| `STRIPE_WEBHOOK_SECRET`   | Stripe          | Webhook signature verification                     | On rotation of Stripe keys |
| `AWS_SECRET_ACCESS_KEY`   | AWS             | IAM secret key — S3, SES, or other services        | 90 days                    |
| `EMAIL_HOST_PASSWORD`     | SMTP            | Email relay authentication                         | 90 days                    |
| `SMS_API_KEY`             | SMS Provider    | Send SMS — OTP, notifications                      | 180 days                   |
| `SMS_GATEWAY_API_KEY`     | SMS Gateway     | Gateway-level SMS dispatch key                     | 180 days                   |
| `OPENAI_API_KEY`          | OpenAI          | AI feature access — usage billed per call          | 180 days                   |
| `SENTRY_AUTH_TOKEN`       | Sentry          | Organization-level auth — manage projects/releases | 180 days                   |
| `WHATSAPP_BUSINESS_TOKEN` | Meta / WhatsApp | WhatsApp Business API messaging                    | 90 days                    |
| `PAYHERE_MERCHANT_SECRET` | PayHere         | Payment gateway signing secret (Sri Lanka)         | 180 days                   |

#### 🟡 MEDIUM — Confidential Configuration

| Variable                | Service | Description                                                  | Rotation Cycle            |
| ----------------------- | ------- | ------------------------------------------------------------ | ------------------------- |
| `DATABASE_URL`          | Django  | Full connection string (includes host, port, credentials)    | When password rotates     |
| `REDIS_URL`             | Redis   | Connection URI (may include auth token)                      | 90 days (if auth enabled) |
| `CELERY_BROKER_URL`     | Celery  | Broker connection string (Redis/RabbitMQ)                    | When Redis URL rotates    |
| `CELERY_RESULT_BACKEND` | Celery  | Result backend connection string                             | When Redis URL rotates    |
| `FLOWER_BASIC_AUTH`     | Flower  | HTTP Basic Auth for Celery monitoring UI                     | 90 days                   |
| `CORS_ALLOWED_ORIGINS`  | Django  | Allowed cross-origin domains                                 | On infrastructure change  |
| `CSRF_TRUSTED_ORIGINS`  | Django  | Trusted origins for CSRF validation                          | On infrastructure change  |
| `DJANGO_ALLOWED_HOSTS`  | Django  | Permitted Host headers                                       | On infrastructure change  |
| `AWS_ACCESS_KEY_ID`     | AWS     | IAM access key identifier (not secret alone, but paired)     | 90 days                   |
| `SENTRY_DSN`            | Sentry  | Data Source Name — project ingest endpoint                   | On project rotation       |
| `PAYHERE_MERCHANT_ID`   | PayHere | Merchant identifier (semi-public, but limits attack surface) | N/A (static)              |

#### 🟢 LOW — Internal / Public Configuration

| Variable                 | Service         | Description                                          |
| ------------------------ | --------------- | ---------------------------------------------------- |
| `DEBUG` / `DJANGO_DEBUG` | Django          | Debug mode toggle (`True`/`False`)                   |
| `NODE_ENV`               | Next.js         | Runtime environment (`development` / `production`)   |
| `APP_NAME`               | App             | Application display name                             |
| `APP_ENV`                | App             | Environment label (`dev` / `staging` / `production`) |
| `APP_URL`                | App             | Base URL of the application                          |
| `NEXT_PUBLIC_API_URL`    | Next.js         | Client-exposed API endpoint                          |
| `NEXT_PUBLIC_APP_NAME`   | Next.js         | Client-exposed app name                              |
| `NEXT_PUBLIC_*`          | Next.js         | All client-side public variables                     |
| `DEFAULT_CURRENCY`       | App             | Default currency code (`LKR`)                        |
| `DEFAULT_TIMEZONE`       | App             | Default timezone (`Asia/Colombo`)                    |
| `DEFAULT_LOCALE`         | App             | Default locale (`si` / `ta` / `en`)                  |
| `LOG_LEVEL`              | App             | Logging verbosity (`DEBUG` / `INFO` / `WARNING`)     |
| `CELERY_CONCURRENCY`     | Celery          | Number of worker processes                           |
| `CELERY_LOG_LEVEL`       | Celery          | Worker log verbosity                                 |
| `CELERY_QUEUES`          | Celery          | Comma-separated queue names                          |
| `TZ` / `TIME_ZONE`       | System / Django | System timezone                                      |
| `LANGUAGE_CODE`          | Django          | Default language                                     |
| `SITE_NAME`              | App             | Public site name                                     |
| `SITE_URL`               | App             | Public site URL                                      |
| `SUPPORT_EMAIL`          | App             | Public support email address                         |

---

## 3. Development Secrets Handling

> **Task 71** — Local env files with placeholders, access rules

### 3.1 File Structure

Development secrets are managed through **local `.env` files** that are **never committed** to version control.

```
pos/
├── .env                    # Root-level — Docker Compose variables
├── .env.docker             # Docker-specific overrides
├── backend/
│   └── .env                # Django-specific secrets
├── frontend/
│   └── .env.local          # Next.js local secrets
└── .env.example            # ✅ COMMITTED — placeholder template
    .env.docker.example     # ✅ COMMITTED — Docker placeholder template
```

### 3.2 Gitignore Patterns

The following patterns **must** exist in the root `.gitignore`:

```gitignore
# ── Secrets & Environment Files ──────────────────────────
.env
.env.*
!.env.example
!.env.*.example
backend/.env
backend/.env.*
!backend/.env.example
frontend/.env.local
frontend/.env.development.local
frontend/.env.production.local
```

### 3.3 Placeholder Template (`.env.example`)

Every secret must have a corresponding placeholder in `.env.example` committed to the repository. Placeholders use the format `<DESCRIPTION>` — never real values.

```bash
# ═══════════════════════════════════════════════════════════
# LankaCommerce Cloud — Environment Template
# Copy to .env and fill in values. NEVER commit the .env file.
# ═══════════════════════════════════════════════════════════

# ── Django ────────────────────────────────────────────────
DJANGO_SECRET_KEY=<generate-with-python-secrets-module>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# ── Database ──────────────────────────────────────────────
POSTGRES_DB=lankacommerce_dev
POSTGRES_USER=lankacommerce
POSTGRES_PASSWORD=<your-local-db-password>
DATABASE_URL=postgres://lankacommerce:<password>@localhost:5432/lankacommerce_dev

# ── Redis ─────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# ── Authentication ────────────────────────────────────────
JWT_SIGNING_KEY=<generate-256-bit-key>
NEXTAUTH_SECRET=<generate-with-openssl-rand-base64-32>

# ── Payments (use test/sandbox keys) ─────────────────────
STRIPE_SECRET_KEY=sk_test_<your-stripe-test-key>
STRIPE_WEBHOOK_SECRET=whsec_<your-webhook-secret>
PAYHERE_MERCHANT_ID=<sandbox-merchant-id>
PAYHERE_MERCHANT_SECRET=<sandbox-merchant-secret>

# ── AWS (use localstack or test credentials) ──────────────
AWS_ACCESS_KEY_ID=<your-aws-key-id>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>

# ── Email (use MailHog/Mailtrap in dev) ───────────────────
EMAIL_HOST_PASSWORD=<mailtrap-password>

# ── Third-Party APIs (use test/sandbox keys) ─────────────
SMS_API_KEY=<test-sms-api-key>
SMS_GATEWAY_API_KEY=<test-gateway-key>
OPENAI_API_KEY=sk-<your-openai-test-key>
SENTRY_DSN=<your-sentry-dsn>
SENTRY_AUTH_TOKEN=<your-sentry-auth-token>
WHATSAPP_BUSINESS_TOKEN=<test-whatsapp-token>

# ── Application Config ───────────────────────────────────
APP_NAME=LankaCommerce Cloud
APP_ENV=development
APP_URL=http://localhost:3000
DEFAULT_CURRENCY=LKR
DEFAULT_TIMEZONE=Asia/Colombo
DEFAULT_LOCALE=en
```

### 3.4 Development Rules

| Rule                                       | Details                                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------ |
| **No real production secrets in dev**      | Use sandbox/test keys for Stripe, PayHere, SMS, etc.                                 |
| **Use local service replacements**         | MailHog for email, LocalStack for AWS, Stripe test mode                              |
| **Docker Compose manages service secrets** | Secrets passed via `env_file:` directive in `docker-compose.yml`                     |
| **Generate unique keys per developer**     | Each developer generates their own `DJANGO_SECRET_KEY`, `JWT_SIGNING_KEY`            |
| **Pre-commit hook validation**             | A pre-commit hook scans staged files for high-entropy strings and known key patterns |

### 3.5 Generating Development Secrets

```bash
# Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generic 256-bit key (JWT, NextAuth)
openssl rand -base64 32

# Postgres password
openssl rand -hex 16
```

### 3.6 Pre-Commit Secret Scanning

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
        exclude: \.env\.example$|\.env\..*\.example$
```

Initialize baseline:

```bash
detect-secrets scan --exclude-files '\.env$' > .secrets.baseline
```

---

## 4. Staging Secrets Handling

> **Task 72** — Secure storage, restricted access, approval flow

### 4.1 Storage Backend

| Mechanism                              | Purpose                                          |
| -------------------------------------- | ------------------------------------------------ |
| **GitHub Actions Secrets**             | CI/CD pipeline — build, test, deploy             |
| **GitHub Environments**                | Environment-scoped secrets with protection rules |
| **AWS Parameter Store (SecureString)** | Runtime secrets injected at container start      |

Staging secrets are **never** stored in files on disk, environment templates, or Docker images.

### 4.2 GitHub Environment Configuration

```
GitHub Repository
└── Settings → Environments
    └── staging
        ├── Protection Rules
        │   ├── Required reviewers: 1 (Team Lead or DevOps)
        │   ├── Wait timer: 5 minutes
        │   └── Deployment branch: release/* , staging
        └── Secrets
            ├── DJANGO_SECRET_KEY
            ├── DATABASE_URL
            ├── JWT_SIGNING_KEY
            ├── STRIPE_SECRET_KEY  (test mode)
            ├── AWS_SECRET_ACCESS_KEY
            └── ... (all 🔴 HIGH and 🟡 MEDIUM variables)
```

### 4.3 CI/CD Secret Injection

Secrets are injected into the deployment pipeline — never baked into images.

```yaml
# .github/workflows/deploy-staging.yml (excerpt)
jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging # ← triggers approval gate
    steps:
      - name: Deploy to staging
        env:
          DJANGO_SECRET_KEY: ${{ secrets.DJANGO_SECRET_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          JWT_SIGNING_KEY: ${{ secrets.JWT_SIGNING_KEY }}
          REDIS_URL: ${{ secrets.REDIS_URL }}
          # ... remaining secrets
        run: |
          # Secrets available as env vars during deployment
          ./scripts/deploy-staging.sh
```

### 4.4 AWS Parameter Store (Staging)

For runtime secrets on staging infrastructure:

```bash
# Store a secret
aws ssm put-parameter \
  --name "/lankacommerce/staging/DJANGO_SECRET_KEY" \
  --type "SecureString" \
  --value "<actual-value>" \
  --tags "Key=Environment,Value=staging" "Key=Tier,Value=high"

# Retrieve at container start (entrypoint script)
export DJANGO_SECRET_KEY=$(aws ssm get-parameter \
  --name "/lankacommerce/staging/DJANGO_SECRET_KEY" \
  --with-decryption \
  --query 'Parameter.Value' \
  --output text)
```

### 4.5 Parameter Naming Convention

```
/lankacommerce/{environment}/{VARIABLE_NAME}

Examples:
  /lankacommerce/staging/DJANGO_SECRET_KEY
  /lankacommerce/staging/DATABASE_URL
  /lankacommerce/staging/STRIPE_SECRET_KEY
  /lankacommerce/production/DJANGO_SECRET_KEY
```

### 4.6 Staging Access Rules

| Role                 | Access Level                     | Approval Required                          |
| -------------------- | -------------------------------- | ------------------------------------------ |
| **DevOps Lead**      | Read / Write all staging secrets | No                                         |
| **Tech Lead**        | Read all staging secrets         | No                                         |
| **Senior Developer** | Read non-HIGH staging secrets    | Yes — DevOps Lead approval                 |
| **Developer**        | No direct access                 | Yes — Tech Lead + DevOps approval          |
| **CI/CD Pipeline**   | Read-only at deploy time         | Automatic via environment protection rules |

### 4.7 Approval Workflow

```
Developer requests staging secret access
        │
        ▼
  ┌─────────────┐     ┌──────────────┐
  │ GitHub Issue │────▶│ Team Lead    │──── Approve / Deny
  │ (template)  │     │ Review       │
  └─────────────┘     └──────────────┘
                             │
                             ▼ (if approved)
                      ┌──────────────┐
                      │ DevOps Lead  │──── Grants access
                      │ Provision    │     (time-boxed: 4h)
                      └──────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │ Audit Log    │──── Who, what, when
                      └──────────────┘
```

---

## 5. Production Secrets Handling

> **Task 73** — Secret managers, audit trails, access monitoring

### 5.1 Storage Backend

| Mechanism                   | Purpose                                      | Encryption             |
| --------------------------- | -------------------------------------------- | ---------------------- |
| **AWS Secrets Manager**     | Primary secret store for all 🔴 HIGH secrets | AES-256 (AWS KMS)      |
| **AWS SSM Parameter Store** | 🟡 MEDIUM configuration values               | AES-256 (SecureString) |
| **AWS KMS**                 | Envelope encryption key management           | HSM-backed             |
| **GitHub Environments**     | Deployment pipeline secrets only             | GitHub-managed         |

> **Rule**: No production secret is stored in environment files, Docker images, CI logs, or application config files on disk.

### 5.2 AWS Secrets Manager Structure

```
AWS Secrets Manager
└── lankacommerce/production/
    ├── django
    │   ├── SECRET_KEY
    │   ├── JWT_SIGNING_KEY
    │   └── DATABASE_URL
    ├── postgres
    │   ├── MASTER_PASSWORD
    │   └── APP_PASSWORD
    ├── payments
    │   ├── STRIPE_SECRET_KEY
    │   ├── STRIPE_WEBHOOK_SECRET
    │   ├── PAYHERE_MERCHANT_SECRET
    │   └── PAYHERE_MERCHANT_ID
    ├── aws
    │   ├── ACCESS_KEY_ID
    │   └── SECRET_ACCESS_KEY
    ├── messaging
    │   ├── SMS_API_KEY
    │   ├── SMS_GATEWAY_API_KEY
    │   ├── WHATSAPP_BUSINESS_TOKEN
    │   └── EMAIL_HOST_PASSWORD
    ├── monitoring
    │   ├── SENTRY_AUTH_TOKEN
    │   └── SENTRY_DSN
    └── ai
        └── OPENAI_API_KEY
```

### 5.3 Secret Retrieval at Runtime

Secrets are fetched at container startup — never baked into images.

```python
# config/secrets.py — production secret loader
import boto3
import json
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region: str = "ap-southeast-1") -> dict:
    """Retrieve a secret from AWS Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=region)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        raise RuntimeError(f"Failed to retrieve secret '{secret_name}': {e}")

# Usage in settings/production.py
if APP_ENV == "production":
    django_secrets = get_secret("lankacommerce/production/django")
    SECRET_KEY = django_secrets["SECRET_KEY"]
    JWT_SIGNING_KEY = django_secrets["JWT_SIGNING_KEY"]

    db_secrets = get_secret("lankacommerce/production/postgres")
    DATABASES["default"]["PASSWORD"] = db_secrets["APP_PASSWORD"]
```

### 5.4 Container Entrypoint Integration

```bash
#!/bin/bash
# docker/backend/entrypoint.sh (production mode)
set -euo pipefail

if [ "${APP_ENV}" = "production" ]; then
    echo "Fetching secrets from AWS Secrets Manager..."
    # Secrets are loaded by Django settings via boto3
    # Only non-secret env vars are set here
    export APP_ENV=production
    export LOG_LEVEL=WARNING
    export DEFAULT_CURRENCY=LKR
    export DEFAULT_TIMEZONE=Asia/Colombo
fi

exec "$@"
```

### 5.5 IAM Policy for Secret Access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadProductionSecrets",
      "Effect": "Allow",
      "Action": ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"],
      "Resource": "arn:aws:secretsmanager:ap-southeast-1:ACCOUNT_ID:secret:lankacommerce/production/*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "ap-southeast-1"
        }
      }
    },
    {
      "Sid": "AllowKMSDecrypt",
      "Effect": "Allow",
      "Action": ["kms:Decrypt", "kms:DescribeKey"],
      "Resource": "arn:aws:kms:ap-southeast-1:ACCOUNT_ID:key/KEY_ID"
    }
  ]
}
```

### 5.6 Audit Trails

All production secret access is logged via **AWS CloudTrail** and forwarded to centralized logging.

| Event                            | Logged Data                                 | Retention |
| -------------------------------- | ------------------------------------------- | --------- |
| Secret read (`GetSecretValue`)   | Who, when, which secret, source IP          | 1 year    |
| Secret update (`PutSecretValue`) | Who, when, which secret, version ID         | 2 years   |
| Secret rotation (`RotateSecret`) | Automatic vs. manual, rotation function ARN | 2 years   |
| Failed access attempts           | Principal ARN, error code, secret ARN       | 2 years   |
| IAM policy changes               | Policy diff, who modified, when             | 2 years   |

### 5.7 CloudWatch Alarms

```yaml
# Alerts configured for production secret access anomalies
Alarms:
  - Name: UnauthorizedSecretAccess
    Metric: secretsmanager:AccessDenied
    Threshold: ">= 1 in 5 minutes"
    Action: SNS → PagerDuty → On-Call DevOps

  - Name: UnusualSecretReadVolume
    Metric: secretsmanager:GetSecretValue count
    Threshold: "> 100 in 15 minutes"
    Action: SNS → Slack #security-alerts

  - Name: SecretRotationFailure
    Metric: secretsmanager:RotationFailed
    Threshold: ">= 1"
    Action: SNS → PagerDuty → On-Call DevOps
```

### 5.8 Automatic Secret Rotation

AWS Secrets Manager rotation is enabled for all 🔴 HIGH secrets.

```
┌──────────────────┐
│ Rotation Lambda  │
│ (per secret type)│
└────────┬─────────┘
         │
    ┌────▼─────┐    ┌──────────────┐    ┌────────────────┐
    │ Step 1:  │───▶│ Step 2:      │───▶│ Step 3:        │
    │ Create   │    │ Set in       │    │ Test new       │
    │ new value│    │ target svc   │    │ credential     │
    └──────────┘    └──────────────┘    └───────┬────────┘
                                                │
                                        ┌───────▼────────┐
                                        │ Step 4:        │
                                        │ Mark current   │
                                        │ (finalize)     │
                                        └────────────────┘
```

| Secret                    | Rotation Schedule | Rotation Strategy                                |
| ------------------------- | ----------------- | ------------------------------------------------ |
| `DJANGO_SECRET_KEY`       | Every 90 days     | Dual-key: old key valid for 24h grace period     |
| `POSTGRES_PASSWORD`       | Every 90 days     | Alternating users strategy                       |
| `JWT_SIGNING_KEY`         | Every 90 days     | JWKS rotation — old key verifies, new key signs  |
| `STRIPE_SECRET_KEY`       | Every 180 days    | Manual rotation via Stripe dashboard + update SM |
| `AWS_SECRET_ACCESS_KEY`   | Every 90 days     | Create new key → deploy → delete old key         |
| `PAYHERE_MERCHANT_SECRET` | Every 180 days    | Manual rotation via PayHere portal + update SM   |

---

## 6. Access Control Matrix

### 6.1 Per-Environment Access

| Role                   | Development           | Staging             | Production                           |
| ---------------------- | --------------------- | ------------------- | ------------------------------------ |
| **DevOps Lead**        | Full access           | Full access         | Full access (logged)                 |
| **Tech Lead**          | Full access           | Read all            | Read non-credential secrets (logged) |
| **Senior Developer**   | Full access           | Read MEDIUM + LOW   | No direct access                     |
| **Developer**          | Full access (own env) | No direct access    | No direct access                     |
| **QA Engineer**        | Read LOW only         | Read LOW only       | No access                            |
| **CI/CD Pipeline**     | Read (docker-compose) | Read at deploy time | Read at deploy time (IAM role)       |
| **Monitoring Service** | N/A                   | Read own DSN/token  | Read own DSN/token (IAM role)        |

### 6.2 Break-Glass Procedure

For emergency production access when normal approval is not possible:

1. **Authenticate** via MFA-protected AWS IAM Identity Center.
2. **Assume** break-glass IAM role (max session: 1 hour).
3. **Access** the required secret — all actions are logged.
4. **Notify** security channel (`#security-alerts`) within 15 minutes.
5. **File** post-incident report within 24 hours.
6. **Review** break-glass usage in weekly security standup.

### 6.3 Offboarding Checklist

When a team member leaves or changes roles:

- [ ] Revoke GitHub repository access and environment permissions
- [ ] Remove from AWS IAM groups / SSO assignments
- [ ] Rotate any secrets the individual had direct access to
- [ ] Revoke CI/CD deployment approval rights
- [ ] Remove from Sentry, Stripe, PayHere, and other third-party dashboards
- [ ] Update `.secrets.baseline` if detect-secrets was configured per-user
- [ ] Audit CloudTrail logs for recent secret access by the departing user

---

## 7. Secret Rotation Policy

### 7.1 Schedule Summary

| Tier      | Rotation Frequency   | Grace Period        | Notification          |
| --------- | -------------------- | ------------------- | --------------------- |
| 🔴 HIGH   | Every 90 days        | 24 hours (dual-key) | 14 days before expiry |
| 🟡 MEDIUM | Every 90–180 days    | 48 hours            | 14 days before expiry |
| 🟢 LOW    | No rotation required | N/A                 | N/A                   |

### 7.2 Rotation Notification Flow

```
Day -14:  Slack notification → #devops-alerts
Day -7:   Slack notification → #devops-alerts + email to DevOps Lead
Day -1:   PagerDuty alert → On-Call DevOps
Day 0:    Automatic rotation (if Lambda configured) OR manual rotation required
Day +1:   Old secret enters grace period
Day +2:   Old secret invalidated (HIGH) or Day +3 (MEDIUM)
```

---

## 8. Incident Response

### 8.1 Secret Exposure Response Plan

If a secret is found in a commit, log, or public location:

| Step | Action                                                                              | Timeline          |
| ---- | ----------------------------------------------------------------------------------- | ----------------- |
| 1    | **Detect** — alert from detect-secrets, GitHub secret scanning, or manual discovery | Immediate         |
| 2    | **Contain** — rotate the exposed secret immediately                                 | Within 15 minutes |
| 3    | **Assess** — determine exposure scope (public repo? logs? duration?)                | Within 1 hour     |
| 4    | **Remediate** — force-push to remove from Git history, purge CI logs                | Within 4 hours    |
| 5    | **Notify** — inform affected parties (third-party providers, users if data exposed) | Within 24 hours   |
| 6    | **Review** — post-incident retrospective, update procedures                         | Within 1 week     |

### 8.2 Git History Cleanup

If a secret was accidentally committed:

```bash
# Use BFG Repo-Cleaner to remove from history
java -jar bfg.jar --replace-text passwords.txt repo.git

# Or use git-filter-repo
git filter-repo --invert-paths --path .env

# Force-push cleaned history
git push --force --all
```

> ⚠️ **Warning**: Force-pushing rewrites history. Coordinate with all team members before executing.

---

## 9. Secrets Security Checklist

Use these checklists during development, deployments, and periodic audits.

### 9.1 Development Security Checklist

- [ ] `.env`, `.env.local`, `.env.docker` are listed in `.gitignore`
- [ ] No real secrets exist in `.env.example` or `.env.docker.example` files
- [ ] `detect-secrets` pre-commit hook is installed and active
- [ ] All `NEXT_PUBLIC_` variables contain **only** non-sensitive values
- [ ] `DJANGO_SECRET_KEY` and `NEXTAUTH_SECRET` are locally generated, not shared
- [ ] Database passwords differ from production/staging
- [ ] Stripe/PayHere keys use **test/sandbox** credentials only
- [ ] No API keys or tokens are hardcoded in source code

### 9.2 Pre-Deployment Checklist

- [ ] `DEBUG=False` and `DJANGO_DEBUG=False` for production
- [ ] `SECURE_SSL_REDIRECT=True` for production
- [ ] `DJANGO_SECRET_KEY` is a unique, randomly generated 50+ character string
- [ ] `POSTGRES_PASSWORD` is strong (24+ characters, mixed case, numbers, symbols)
- [ ] All 🔴 HIGH secrets are stored in AWS Secrets Manager (production) or GitHub Secrets (staging)
- [ ] All 🟡 MEDIUM config is stored in AWS SSM Parameter Store or GitHub Secrets
- [ ] `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` match deployment domains only
- [ ] `DJANGO_ALLOWED_HOSTS` is restricted to actual hostnames
- [ ] `FLOWER_BASIC_AUTH` uses strong credentials (not `admin:admin`)
- [ ] Sentry DSN is set for error monitoring
- [ ] SSL certificates are valid and auto-renewing

### 9.3 Periodic Security Review Checklist (Quarterly)

- [ ] All 🔴 HIGH secrets rotated within policy schedule
- [ ] All 🟡 MEDIUM secrets rotated if due
- [ ] GitHub Secrets list reviewed — remove unused entries
- [ ] AWS IAM policies reviewed — least-privilege confirmed
- [ ] Access control matrix (§6) reviewed — no stale permissions
- [ ] Team offboarding completed for departed members (§6.3)
- [ ] `detect-secrets` baseline updated for new file patterns
- [ ] CloudTrail / audit logs reviewed for anomalous secret access
- [ ] CloudWatch alarms are functioning (test notification)
- [ ] Rotation Lambda functions tested and operational

### 9.4 Incident Response Checklist

- [ ] Compromised secret identified and documented
- [ ] Secret immediately rotated in all environments
- [ ] Affected services restarted with new credentials
- [ ] Access logs reviewed for unauthorized use
- [ ] Git history cleaned if secret was committed (§8.2)
- [ ] Team notified via incident channel
- [ ] Post-mortem completed and documented
- [ ] Preventive measures added (e.g., new scanning rules)

### 9.5 New Secret Onboarding Checklist

When adding a new secret to the project:

- [ ] Variable added to appropriate `.env.example` / `.env.docker.example` with placeholder
- [ ] Sensitivity tier assigned (🔴 HIGH / 🟡 MEDIUM / 🟢 LOW) in §2
- [ ] Variable added to `docs/SECRETS.md` classification table
- [ ] Storage location defined for each environment (dev/staging/production)
- [ ] Rotation schedule assigned based on tier
- [ ] CI/CD workflow updated if secret is needed in pipelines
- [ ] Docker Compose interpolation added if used in containers
- [ ] Documentation updated in `docs/DOCKER_ENV.md` if Docker-relevant

---

## 10. Related Documentation

| Document                 | Path                                                                                                              | Description                                      |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Docker Environment Setup | [docs/DOCKER_ENV.md](DOCKER_ENV.md)                                                                               | Docker Compose configuration and local dev setup |
| Docker Setup Guide       | [docs/docker-setup.md](docker-setup.md)                                                                           | Step-by-step Docker development guide            |
| Contributing Guide       | [CONTRIBUTING.md](../CONTRIBUTING.md)                                                                             | Development workflow and PR guidelines           |
| Architecture Overview    | [docs/architecture/](architecture/)                                                                               | System architecture documentation                |
| Branching Strategy       | [docs/BRANCHING.md](BRANCHING.md)                                                                                 | Branch naming and workflow                       |
| Code Review Guide        | [docs/CODE_REVIEW.md](CODE_REVIEW.md)                                                                             | Review checklist (includes security review)      |
| Security Policy          | [SECURITY.md](../SECURITY.md)                                                                                     | Vulnerability reporting and security policy      |
| Phase 3 — Infrastructure | [Document-Series/Phase-03_Core-Backend-Infrastructure/](../Document-Series/Phase-03_Core-Backend-Infrastructure/) | Core backend infrastructure planning             |

---

## Appendix A: Quick Reference Card

```
┌──────────────────────────────────────────────────────────────────┐
│                 SECRETS QUICK REFERENCE                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🔴 HIGH secrets  → AWS Secrets Manager (production)             │
│                    → GitHub Environment Secrets (staging)         │
│                    → .env files ONLY (dev, never committed)      │
│                                                                  │
│  🟡 MEDIUM config → AWS SSM Parameter Store (production)         │
│                    → GitHub Environment Secrets (staging)         │
│                    → .env files (dev)                             │
│                                                                  │
│  🟢 LOW config    → Can live in committed config files           │
│                    → docker-compose.yml, next.config.js           │
│                    → .env.example (placeholders only!)            │
│                                                                  │
│  NEVER commit:    .env, .env.local, .env.docker (with values)   │
│  ALWAYS commit:   .env.example, .env.docker.example              │
│                                                                  │
│  Generate keys:   openssl rand -base64 32                        │
│  Scan for leaks:  detect-secrets scan                            │
│  Rotate secrets:  Follow §7 Rotation Policy                     │
│  Security check:  See §9 Security Checklists                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

_This document is maintained by the DevOps and Security team. For questions or update requests, open an issue with the `security` and `documentation` labels._
