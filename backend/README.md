# LankaCommerce Cloud — Backend

> Django-based REST API backend for the LankaCommerce Cloud POS & ERP platform.

For the overall project documentation, see the [main README](../README.md).

---

## Overview

The backend powers all server-side logic for LankaCommerce Cloud, including multi-tenant SaaS operations, ERP modules, and the web-store API. It is built with **Django 5.x** and **Django REST Framework** and uses **django-tenants** for PostgreSQL schema-based multi-tenancy.

### Technology Stack

| Technology            | Version | Purpose                  |
| --------------------- | ------- | ------------------------ |
| Python                | 3.12+   | Programming language     |
| Django                | 5.x     | Web framework            |
| Django REST Framework | 3.15+   | REST API framework       |
| PostgreSQL            | 15+     | Database                 |
| Redis                 | 7+      | Cache and message broker |
| Celery                | 5.x     | Async task queue         |
| django-tenants        | 3.x     | Multi-tenancy            |

---

## Directory Structure

```
backend/
├── apps/              # Django applications (modular business logic)
│   ├── accounting/    # Invoicing, payments, financial reporting
│   ├── core/          # Shared app utilities and base classes
│   ├── customers/     # Customer management
│   ├── hr/            # Employee management, attendance, payroll
│   ├── integrations/  # Third-party service integrations
│   ├── inventory/     # Warehouse, stock tracking, locations
│   ├── products/      # Product catalog and categories
│   ├── reports/       # Analytics, dashboards, exports
│   ├── sales/         # POS transactions, receipts, orders
│   ├── tenants/       # Multi-tenant configuration
│   ├── users/         # Authentication, profiles, roles
│   ├── vendors/       # Supplier management
│   └── webstore/      # Customer-facing e-commerce API
├── config/            # Django project settings & root URL configuration
├── core/              # Shared utilities, base models, mixins, helpers
├── fixtures/          # Seed data and test fixtures (JSON/YAML)
├── locale/            # Internationalization files (en, si, ta)
├── media/             # User-uploaded files (git-ignored in production)
├── requirements/      # Pip requirement files (base, local, production, test)
├── static/            # Static assets collected by Django
├── templates/         # Django HTML templates (email, admin, errors)
├── tests/             # Project-wide / integration tests
├── manage.py          # Django management CLI entry point
├── pyproject.toml     # Python project & tool configuration
└── README.md          # This file
```

> For deeper backend architecture and module documentation, see [docs/backend/](../docs/backend/README.md).

---

## Prerequisites

Make sure you have the following installed before setting up the backend:

- **Python 3.12+** — [python.org](https://www.python.org/downloads/)
- **PostgreSQL 15+** — [postgresql.org](https://www.postgresql.org/download/)
- **Redis 7+** — [redis.io](https://redis.io/download/)
- **pip** (comes with Python) or **pipx** for CLI tools

---

## Setup

### 1. Create & activate a virtual environment

```bash
cd backend
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements/development.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your local database credentials and secrets
```

### 4. Set up the database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the development server

```bash
python manage.py runserver
```

The API will be available at **http://localhost:8000/**.

---

## Development Commands

### Django

| Command                            | Description                  |
| ---------------------------------- | ---------------------------- |
| `python manage.py runserver`       | Start the development server |
| `python manage.py migrate`         | Apply database migrations    |
| `python manage.py makemigrations`  | Create new migrations        |
| `python manage.py createsuperuser` | Create an admin user         |
| `python manage.py shell`           | Open the Django shell        |
| `python manage.py collectstatic`   | Collect static files         |

### Testing

| Command                 | Description                    |
| ----------------------- | ------------------------------ |
| `pytest`                | Run the full test suite        |
| `pytest --cov`          | Run tests with coverage report |
| `pytest -x`             | Stop on first failure          |
| `pytest -k "test_name"` | Run a specific test            |

### Code Quality

| Command                  | Description           |
| ------------------------ | --------------------- |
| `black .`                | Format code           |
| `black --check --diff .` | Check formatting (CI) |
| `isort .`                | Sort imports          |
| `flake8`                 | Lint code             |
| `mypy .`                 | Type-check code       |

### Code Formatting (Black)

This project uses [Black](https://black.readthedocs.io/) for Python code formatting.

**Quick Commands:**

```bash
# Format all code
make format

# Check formatting (CI)
make format-check

# Format specific file
black path/to/file.py
```

**Configuration** (`pyproject.toml`):

- Line length: 88 characters
- Target: Python 3.12
- Excludes: migrations, venv, cache

**IDE Setup:**

_VS Code_ — Install the Black Formatter extension (`ms-python.black-formatter`), then add to `.vscode/settings.json`:

```json
{
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  },
  "black-formatter.args": ["--config", "pyproject.toml"]
}
```

_PyCharm_ — Settings → Tools → Black → Enable "On code reformat" → Set path to Black executable.

**Guidelines:**

- Run `make format` before committing
- CI will reject unformatted code
- Do not reformat Django migrations (auto-excluded)
- Pre-commit hooks will be set up separately

### Import Sorting (isort)

This project uses [isort](https://pycqa.github.io/isort/) for import sorting, configured for Black compatibility.

**Quick Commands:**

```bash
# Sort all imports
make sort-imports

# Check sorting (CI)
make sort-imports-check

# Format + sort + lint fix in one command
make lint-fix
```

**Configuration** (`pyproject.toml`):

- Profile: black (compatible with Black formatting)
- Sections: FUTURE → STDLIB → DJANGO → THIRDPARTY → FIRSTPARTY → LOCALFOLDER
- First party: apps, config, core, utils
- Skips: migrations, venv, cache directories

### Linting (flake8 & Ruff)

We use two complementary linters:

- **flake8**: Traditional linter with plugins (bugbear, comprehensions, simplify)
- **Ruff**: Fast, modern Rust-based linter (preferred for auto-fixing)

**Quick Commands:**

```bash
# Run all linters
make lint

# Auto-fix issues with Ruff
make ruff-fix

# Full lint, format, and sort
make lint-fix

# Show flake8 statistics
make lint-stats
```

**Configuration:**

- `.flake8`: flake8 configuration (max-line-length 88, max-complexity 10)
- `pyproject.toml` → `[tool.ruff]`: Ruff configuration (F, E, W, I, B, C4, UP, SIM, PL rules)

**Ignored Rules:** E501 (line length — Black handles this), E203 (Black whitespace style)

### Type Checking (mypy)

This project uses [mypy](https://mypy.readthedocs.io/) for static type checking with strict mode enabled.

```bash
# Run type check
make typecheck

# Generate HTML report
make typecheck-report

# Run all quality checks (format + lint + typecheck)
make quality
```

**Configuration:**

- `mypy.ini`: Primary mypy configuration (strict mode, Django plugin, per-module overrides)
- `pyproject.toml` → `[tool.mypy]`: Secondary reference configuration

**Key Settings:**

- Python 3.12 target
- Strict mode enabled
- Django plugin configured (`mypy_django_plugin.main`)
- Migrations ignored (auto-generated)
- Test files have relaxed typing rules

**Adding Type Hints:**

```python
# Function with types
def get_user(user_id: int) -> User:
    return User.objects.get(id=user_id)

# Optional parameter
def find_users(name: str | None = None) -> QuerySet[User]:
    if name:
        return User.objects.filter(name__icontains=name)
    return User.objects.all()
```

**Common Types:**

| Type        | Import                   | Example                |
| ----------- | ------------------------ | ---------------------- |
| QuerySet    | `django.db.models`       | `QuerySet[User]`       |
| HttpRequest | `django.http`            | `request: HttpRequest` |
| Request     | `rest_framework.request` | `request: Request`     |

**IDE Setup:**

- **VS Code:** Install Pylance extension (includes mypy support)
- **PyCharm:** Enable mypy in Settings → Python Integrated Tools → Type Checker

**Ignoring Errors:** Use `# type: ignore[error-code]` sparingly:

```python
result = untyped_library.call()  # type: ignore[no-untyped-call]
```

---

## Architecture

### Multi-Tenancy

LankaCommerce Cloud uses **PostgreSQL schema-based multi-tenancy** via django-tenants. Each tenant (business/store) operates in an isolated database schema while sharing the same application instance.

### App Organization

Django apps are organized by business domain inside `apps/`:

- Each app is self-contained with its own models, views, serializers, and tests.
- Shared logic lives in `core/`.

### API Design

- RESTful endpoints powered by Django REST Framework.
- Versioned API routes (e.g., `/api/v1/`).
- JWT-based authentication.
- Standardized response format and error handling.

---

## Environment Variables

The backend uses **django-environ** to load configuration from environment files. Variables are organized by category.

### Required Variables (Local Development)

| Variable            | Description                  | Example                                      |
| ------------------- | ---------------------------- | -------------------------------------------- |
| `DJANGO_SECRET_KEY` | Cryptographic signing key    | _generate a unique value_                    |
| `DJANGO_DEBUG`      | Enable debug mode            | `True`                                       |
| `DATABASE_URL`      | PostgreSQL connection string | `postgres://user:pass@localhost:5432/lcc_db` |
| `REDIS_URL`         | Redis connection string      | `redis://localhost:6379/0`                   |

### Important Variables

| Variable                 | Description              | Default                    |
| ------------------------ | ------------------------ | -------------------------- |
| `DJANGO_SETTINGS_MODULE` | Settings module path     | `config.settings.local`    |
| `DJANGO_ALLOWED_HOSTS`   | Allowed host headers     | `localhost,127.0.0.1`      |
| `CELERY_BROKER_URL`      | Celery broker connection | _uses REDIS_URL_           |
| `DEFAULT_FROM_EMAIL`     | Sender email address     | `noreply@lankacommerce.lk` |

### Configuration Files

| File                  | Use Case                                 |
| --------------------- | ---------------------------------------- |
| `.env.docker`         | Docker Compose development (recommended) |
| `.env.docker.example` | Template for `.env.docker`               |

> For the complete list of all environment variables (backend, frontend, and Docker), see the [Environment Variable Reference](../docs/ENV_VARIABLES.md).
>
> For secrets handling and rotation policy, see [Secrets Management](../docs/SECRETS.md).
>
> For Docker-specific environment loading, see [Docker Environment Variables](../docs/DOCKER_ENV.md).

---

## Database Migrations

Django migrations track changes to your models and apply them to the database schema.

### Migration Workflow

The standard workflow when changing models is:

1. **Create migrations** — generate migration files from model changes
2. **Review** — inspect the generated migration for correctness
3. **Apply** — run the migration against your database
4. **Verify** — confirm the schema matches expectations

### Key Commands

```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migration for a specific app
python manage.py makemigrations products

# Create migration with a descriptive name
python manage.py makemigrations products --name add_sku_field

# Apply all pending migrations
python manage.py migrate

# Apply migrations for a specific app
python manage.py migrate products

# Show migration status
python manage.py showmigrations

# Revert to a specific migration
python manage.py migrate products 0003_previous_migration

# Generate SQL without applying (preview)
python manage.py sqlmigrate products 0004_add_sku_field
```

### Multi-Tenant Migrations

Because LankaCommerce Cloud uses **django-tenants**, migrations are separated into two categories:

- **`shared_apps`** — Migrations that run on the `public` schema only (e.g., tenants, users). Use `migrate_schemas --shared`.
- **`tenant_apps`** — Migrations that run on every tenant schema (e.g., products, sales, inventory). Use `migrate_schemas --tenant`.

```bash
# Apply shared migrations only
python manage.py migrate_schemas --shared

# Apply tenant migrations only
python manage.py migrate_schemas --tenant

# Apply all migrations (shared + tenant)
python manage.py migrate_schemas
```

### Best Practices

- **Use descriptive names:** Always pass `--name` when creating migrations (e.g., `add_sku_field`, `remove_legacy_column`).
- **Never edit migration files manually** unless you fully understand the implications (e.g., data migrations or squashing).
- **Commit migrations** alongside the model changes that generated them.
- **Review auto-generated migrations** before applying — Django may add unexpected operations.

---

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov --cov-report=html

# Specific app
pytest apps/products/

# Stop on first failure
pytest -x

# Run a specific test by name
pytest -k "test_product_creation"

# Run with verbose output
pytest -v
```

### Test Categories

| Category              | Location            | Description                                                              |
| --------------------- | ------------------- | ------------------------------------------------------------------------ |
| **Unit tests**        | `apps/<app>/tests/` | Test individual models, services, and utility functions in isolation     |
| **Integration tests** | `backend/tests/`    | Test interactions between apps and cross-cutting concerns                |
| **API tests**         | `apps/<app>/tests/` | Test serializers, views, and API endpoint behavior via DRF's test client |

### Test Naming Conventions

- **Files:** Name test files `test_*.py` (e.g., `test_models.py`, `test_views.py`, `test_serializers.py`).
- **Classes:** Name test classes `Test*` (e.g., `TestProductModel`, `TestOrderCreateView`).
- **Methods:** Name test methods `test_*` with a descriptive suffix (e.g., `test_create_product_with_valid_data`).

### Fixtures

- **`conftest.py`:** Shared pytest fixtures are defined in `conftest.py` at each level — project-wide (`backend/tests/conftest.py`) and per-app (`apps/<app>/tests/conftest.py`).
- **`factory_boy`:** Use factory classes to generate model instances with realistic test data. Factories live alongside tests or in a shared `factories.py` module.
- **Pytest fixtures:** Use `@pytest.fixture` for reusable setup (authenticated clients, sample objects, database state).

```python
# Example: conftest.py fixture
@pytest.fixture
def authenticated_client(db, client, user_factory):
    user = user_factory()
    client.force_login(user)
    return client
```

### Coverage

- Target a minimum of **80%** code coverage.
- Coverage reports are generated with `pytest --cov --cov-report=html` and output to `htmlcov/`.
- CI will enforce the coverage threshold — PRs that drop below 80% will fail.

---

## Background Tasks (Celery)

LankaCommerce Cloud uses [Celery](https://docs.celeryq.dev/) for asynchronous and scheduled background processing.

### Celery Worker

The worker process picks up and executes async tasks such as:

- Sending transactional emails and notifications
- Generating reports and PDF exports
- Processing bulk data imports/exports
- Syncing data with third-party integrations

### Celery Beat

The Beat scheduler triggers periodic/scheduled tasks, including:

- Database cleanup and maintenance routines
- Reminder and follow-up notifications
- Data synchronization with external services
- Scheduled report generation

### Flower (Monitoring)

[Flower](https://flower.readthedocs.io/) provides a real-time web dashboard for monitoring Celery workers and tasks.

- **URL:** `http://localhost:5555`
- View active, completed, and failed tasks
- Monitor worker status and resource usage

### Docker

In Docker Compose, Celery runs as separate containers:

| Container       | Purpose                          |
| --------------- | -------------------------------- |
| `celery-worker` | Executes async tasks             |
| `celery-beat`   | Schedules periodic tasks         |
| `flower`        | Monitoring dashboard (port 5555) |

All three containers start automatically with `docker compose up`.

### Local Development

To run Celery outside Docker during local development:

```bash
# Start the Celery worker
celery -A config worker --loglevel=info

# Start Celery Beat (scheduler)
celery -A config beat --loglevel=info

# Start Flower (monitoring)
celery -A config flower --port=5555
```

### Task Discovery

Celery auto-discovers tasks by scanning for a `tasks.py` file in every installed Django app. Place your task definitions in `apps/<app>/tasks.py`:

```python
# apps/sales/tasks.py
from config.celery import app

@app.task
def generate_daily_sales_report():
    # task implementation
    ...
```

---

## API Documentation

When the development server is running, interactive API docs are available at:

| Endpoint           | URL                                 | Description                                |
| ------------------ | ----------------------------------- | ------------------------------------------ |
| **Swagger UI**     | `http://localhost:8000/api/docs/`   | Interactive API explorer and testing       |
| **ReDoc**          | `http://localhost:8000/api/redoc/`  | Clean read-only API documentation          |
| **OpenAPI Schema** | `http://localhost:8000/api/schema/` | Download the raw OpenAPI 3.0 schema (YAML) |

Documentation is auto-generated by **drf-spectacular** from the DRF viewsets and serializers. Schema settings are configured in `config/settings/base.py` under `SPECTACULAR_SETTINGS`.

### Authentication

Most API endpoints require a valid **JWT token** in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained via the authentication endpoints and must be refreshed before expiry.

### Public Endpoints

The following endpoints are accessible without authentication:

- **Health check:** `GET /api/v1/health/`
- **Tenant registration:** `POST /api/v1/tenants/register/`

### API Versioning

All API routes are versioned with a `/api/v1/` prefix. Future breaking changes will be introduced under `/api/v2/` while maintaining backward compatibility for the previous version.

> For the full API reference, endpoint catalog, and usage examples, see [docs/api/](../docs/api/).

---

## Troubleshooting

Common issues and their solutions:

### 1. Database connection refused

- Verify PostgreSQL is running (`pg_isready` or `docker compose ps`).
- Check that `DATABASE_URL` in your `.env` file is correct.
- In Docker, ensure the `db` service is healthy before the backend starts.

### 2. Redis connection error

- Verify Redis is running (`redis-cli ping` should return `PONG`).
- Check that `REDIS_URL` in your `.env` file points to the correct host and port.
- In Docker, ensure the `redis` service is up (`docker compose ps redis`).

### 3. Celery tasks not executing

- Ensure the Celery worker is running (`celery -A config worker --loglevel=info`).
- Verify the broker connection — `CELERY_BROKER_URL` must match your Redis or RabbitMQ URL.
- Confirm the task is registered by checking `celery -A config inspect registered`.

### 4. Migration errors

- For multi-tenant setups, use `python manage.py migrate_schemas` instead of `migrate`.
- Check for conflicting migrations with `python manage.py showmigrations`.
- If schemas are out of sync, run `python manage.py migrate_schemas --shared` followed by `--tenant`.

### 5. Import errors

- Verify your virtual environment is activated (`.venv\Scripts\activate` on Windows, `source .venv/bin/activate` on Linux/macOS).
- Ensure all dependencies are installed: `pip install -r requirements/development.txt`.
- Check that `PYTHONPATH` includes the backend directory.

### 6. Permission denied

- Check file and directory permissions (`chmod` on Linux/macOS).
- In Docker, ensure the container runs as the correct user (see `Dockerfile`).
- On Windows, run your terminal as Administrator if file-lock errors occur.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](../LICENSE) file for details.
