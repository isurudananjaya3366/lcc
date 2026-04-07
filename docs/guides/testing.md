# Testing Guide

> Test strategy, test types, execution steps, and coverage targets for LankaCommerce Cloud.

**Navigation:** [Getting Started](getting-started.md) · [Debugging](debugging.md) · [Docs Index](../index.md)

---

## Overview

LankaCommerce Cloud maintains a comprehensive test suite covering backend (Django/pytest) and frontend (Jest/React Testing Library). Tests run in CI on every pull request and must pass before merging.

---

## Test Categories

| Category             | Framework  | Location                                     | Purpose                                                    |
| -------------------- | ---------- | -------------------------------------------- | ---------------------------------------------------------- |
| Backend Unit         | pytest     | `backend/tests/` and `backend/apps/*/tests/` | Test individual functions, models, serializers             |
| Backend Integration  | pytest     | `backend/tests/`                             | Test API endpoints, database queries, service interactions |
| Frontend Unit        | Jest + RTL | `frontend/__tests__/`                        | Test components, hooks, utilities                          |
| Frontend Integration | Jest + RTL | `frontend/__tests__/`                        | Test page-level rendering and interactions                 |
| End-to-End           | (Phase 9)  | `tests/`                                     | Full-stack user flow testing                               |

---

## Backend Testing

### Running Tests

1. Run all backend tests: `cd backend && python -m pytest`
2. Run tests for a specific app: `python -m pytest apps/core/tests/`
3. Run a specific test file: `python -m pytest tests/test_health.py`
4. Run a specific test function: `python -m pytest tests/test_health.py::test_health_check`
5. Run tests with verbose output: `python -m pytest -v`
6. Run tests with coverage report: `python -m pytest --cov=apps --cov-report=html`
7. In Docker: `docker compose exec backend python -m pytest`

### Test Configuration

| Setting         | Value                  | Source                    |
| --------------- | ---------------------- | ------------------------- |
| Test runner     | pytest                 | `pytest.ini`              |
| Django settings | `config.settings.test` | `DJANGO_ENV=test`         |
| Database        | In-memory SQLite       | `config/settings/test.py` |
| Password hasher | MD5 (fast, insecure)   | `config/settings/test.py` |
| Email backend   | In-memory              | `config/settings/test.py` |
| Cache backend   | Local memory           | `config/settings/test.py` |

### Test Structure

Each Django app should organize tests as follows:

| File                        | Purpose                             |
| --------------------------- | ----------------------------------- |
| `tests/__init__.py`         | Package marker                      |
| `tests/test_models.py`      | Model creation, validation, methods |
| `tests/test_serializers.py` | Serializer validation and output    |
| `tests/test_views.py`       | API endpoint behavior               |
| `tests/test_services.py`    | Business logic functions            |
| `tests/factories.py`        | Test data factories (factory_boy)   |
| `tests/conftest.py`         | App-specific fixtures               |

### Fixtures

Shared fixtures live in `backend/tests/conftest.py`. Common fixtures include:

| Fixture      | Purpose                       |
| ------------ | ----------------------------- |
| `api_client` | Authenticated DRF test client |
| `user`       | Standard test user            |
| `admin_user` | Admin test user               |
| `tenant`     | Test tenant (Phase 2)         |

---

## Frontend Testing

### Running Tests

1. Run all frontend tests: `cd frontend && pnpm test`
2. Run tests in watch mode: `pnpm test:watch`
3. Run a specific test file: `pnpm test __tests__/components/Button.test.tsx`
4. Run tests with coverage: `pnpm test:coverage`
5. In Docker: `docker compose exec frontend pnpm test`

### Test Structure

| Directory               | Purpose                                   |
| ----------------------- | ----------------------------------------- |
| `__tests__/components/` | Component rendering and interaction tests |
| `__tests__/hooks/`      | Custom hook behavior tests                |
| `__tests__/pages/`      | Page-level integration tests              |
| `__tests__/utils/`      | Utility function tests                    |

### Testing Patterns

| Pattern           | Description                                              |
| ----------------- | -------------------------------------------------------- |
| Render and assert | Render a component and verify expected output            |
| User interaction  | Simulate clicks, typing, and form submissions            |
| Mock API calls    | Mock fetch/React Query to test data-dependent components |
| Snapshot testing  | Use sparingly for complex UI components                  |

---

## Coverage Targets

| Area                    | Target | Rationale             |
| ----------------------- | ------ | --------------------- |
| Backend models          | 90%+   | Core business logic   |
| Backend serializers     | 85%+   | Data validation layer |
| Backend views/endpoints | 80%+   | API contract          |
| Frontend components     | 70%+   | UI rendering          |
| Frontend hooks          | 80%+   | Data logic            |
| Overall                 | 75%+   | Project minimum       |

---

## Writing Good Tests

| Practice                     | Description                                                  |
| ---------------------------- | ------------------------------------------------------------ |
| Arrange-Act-Assert           | Structure every test in three clear phases                   |
| One assertion per test       | Test a single behavior per test function                     |
| Descriptive names            | Name tests to describe the expected behavior                 |
| Isolated tests               | Each test should run independently — no shared mutable state |
| Fast execution               | Use mocks and in-memory databases to keep tests fast         |
| Test edge cases              | Cover empty inputs, boundaries, and error conditions         |
| Avoid testing implementation | Test behavior and outputs, not internal method calls         |

---

## Continuous Integration

Tests run automatically on every pull request:

| Step | Action                                        |
| ---- | --------------------------------------------- |
| 1    | CI installs dependencies                      |
| 2    | Backend tests run with pytest                 |
| 3    | Frontend tests run with Jest                  |
| 4    | Coverage reports are generated                |
| 5    | PR is blocked if tests fail or coverage drops |

---

## Related Documentation

- [Debugging Guide](debugging.md) — Debugging practices and tooling
- [Backend README](../../backend/README.md) — Backend testing section
- [Frontend README](../../frontend/README.md) — Frontend testing section
- [Docs Index](../index.md) — Documentation hub
