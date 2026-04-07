# Architecture Overview

> LankaCommerce Cloud — High-level system architecture and design boundaries.

---

## Table of Contents

- [System Summary](#system-summary)
- [Architecture Diagram](#architecture-diagram)
- [Application Layers](#application-layers)
- [Repository Structure](#repository-structure)
- [Multi-Tenancy Model](#multi-tenancy-model)
- [Technology Stack](#technology-stack)
- [Service Topology](#service-topology)
- [Data Flow](#data-flow)
- [Security Boundaries](#security-boundaries)
- [Related Decisions](#related-decisions)

---

## System Summary

LankaCommerce Cloud (LCC) is a multi-tenant SaaS ERP platform tailored for Sri Lankan SMEs. The system provides point-of-sale, inventory management, accounting, HR, and e-commerce capabilities through a monorepo containing a Django REST API backend and a Next.js frontend.

Key architectural characteristics:

| Characteristic     | Approach                                          |
| ------------------ | ------------------------------------------------- |
| Deployment model   | Containerised Docker Compose services             |
| Tenancy            | Schema-per-tenant via django-tenants              |
| API style          | RESTful JSON over HTTPS                           |
| Authentication     | JWT (SimpleJWT) with refresh rotation             |
| Background work    | Celery workers with Redis broker                  |
| Frontend rendering | Server-side rendering (SSR) and client components |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                       Clients                           │
│   Browser / POS Terminal / Mobile / External Services   │
└──────────────────────┬──────────────────────────────────┘
                       │  HTTPS
┌──────────────────────▼──────────────────────────────────┐
│                    Nginx (prod)                         │
│          Reverse proxy · TLS termination                │
└─────────┬───────────────────────┬───────────────────────┘
          │                       │
┌─────────▼──────────┐ ┌─────────▼──────────┐
│  Next.js Frontend  │ │  Django Backend     │
│  (SSR + SPA)       │ │  (REST API)         │
│  Port 3000         │ │  Port 8000          │
└────────────────────┘ └────────┬────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
┌─────────▼────┐  ┌─────────────▼────┐  ┌────────────▼───┐
│ PostgreSQL   │  │     Redis        │  │   Celery       │
│ (schemas)    │  │  Cache + Broker  │  │  Worker + Beat │
│ Port 5432    │  │  Port 6379       │  │                │
└──────────────┘  └──────────────────┘  └────────────────┘
```

---

## Application Layers

The backend follows a layered architecture within each Django app:

| Layer            | Responsibility                                | Location         |
| ---------------- | --------------------------------------------- | ---------------- |
| URL routing      | Map HTTP paths to views                       | `urls.py`        |
| Views / ViewSets | Request handling, authentication, permissions | `views.py`       |
| Serializers      | Validation, transformation, representation    | `serializers.py` |
| Models           | Data definition, business constraints         | `models.py`      |
| Services         | Complex business logic (optional layer)       | `services.py`    |
| Signals          | Side-effects and cross-app events             | `signals.py`     |
| Tasks            | Asynchronous background processing            | `tasks.py`       |
| Admin            | Django admin configuration                    | `admin.py`       |

The frontend follows a component-based architecture:

| Layer          | Responsibility                    | Location      |
| -------------- | --------------------------------- | ------------- |
| Pages / Routes | Route definitions and page shells | `app/`        |
| Components     | Reusable UI elements              | `components/` |
| Hooks          | Shared logic and data fetching    | `hooks/`      |
| Stores         | Client-side state (Zustand)       | `stores/`     |
| Services       | API client and request helpers    | `services/`   |
| Types          | Shared TypeScript interfaces      | `types/`      |

---

## Repository Structure

The monorepo contains seven top-level directories (see [ADR-0001](../adr/0001-monorepo-structure.md)):

| Directory          | Purpose                                             |
| ------------------ | --------------------------------------------------- |
| `backend/`         | Django project — REST API, models, business logic   |
| `frontend/`        | Next.js application — SSR pages, components, stores |
| `shared/`          | Cross-stack constants and type definitions          |
| `docker/`          | Dockerfiles, Nginx config, database scripts         |
| `docs/`            | Project documentation, guides, ADRs                 |
| `scripts/`         | Development and CI helper scripts                   |
| `tests/`           | End-to-end and integration test suites              |
| `Document-Series/` | Phased implementation plans and task documents      |

---

## Multi-Tenancy Model

LCC uses schema-based multi-tenancy powered by django-tenants (see [ADR-0002](../adr/0002-multi-tenancy-approach.md)):

| Schema          | Contents                                                  | Isolation                 |
| --------------- | --------------------------------------------------------- | ------------------------- |
| `public`        | Tenant registry, domains, subscription plans, admin users | Shared across all tenants |
| `tenant_<slug>` | Products, inventory, orders, customers, HR, accounting    | Fully isolated per tenant |

Tenant resolution flow:

1. Request arrives with a `Host` header (e.g., `acme.lankacommerce.lk`)
2. `TenantMainMiddleware` looks up the domain in the `public` schema
3. PostgreSQL `search_path` is set to the matching tenant schema
4. All ORM queries automatically scope to the correct schema
5. Response is returned — no cross-tenant data leakage possible

App classification:

| Category    | Examples                                                       | Schema          |
| ----------- | -------------------------------------------------------------- | --------------- |
| SHARED_APPS | tenants, users, django.contrib.admin                           | `public`        |
| TENANT_APPS | products, inventory, sales, customers, vendors, hr, accounting | `tenant_<slug>` |

---

## Technology Stack

Full stack rationale is documented in [ADR-0003](../adr/0003-technology-stack.md).

### Backend

| Technology                | Role                      |
| ------------------------- | ------------------------- |
| Python 3.12+              | Runtime                   |
| Django 5.x                | Web framework             |
| Django REST Framework 3.x | API toolkit               |
| PostgreSQL 15             | Primary database          |
| Redis 7                   | Cache and message broker  |
| Celery 5.x                | Task queue                |
| django-tenants 3.x        | Multi-tenancy             |
| SimpleJWT 5.x             | JWT authentication        |
| drf-spectacular           | OpenAPI schema generation |

### Frontend

| Technology         | Role                         |
| ------------------ | ---------------------------- |
| TypeScript 5.x     | Language                     |
| Next.js 15+        | React framework (SSR)        |
| React 19+          | UI library                   |
| Tailwind CSS 3.x   | Utility-first styling        |
| shadcn/ui          | Component library            |
| Zustand            | Client state management      |
| TanStack Query 5.x | Server state / data fetching |
| React Hook Form    | Form handling and validation |

### Infrastructure

| Technology       | Role                          |
| ---------------- | ----------------------------- |
| Docker + Compose | Container orchestration       |
| Nginx            | Production reverse proxy      |
| WhiteNoise       | Static file serving           |
| Sentry           | Error tracking and monitoring |

---

## Service Topology

Docker Compose defines seven services for local development:

| Service       | Image            | Port | Purpose                     |
| ------------- | ---------------- | ---- | --------------------------- |
| backend       | Custom (Django)  | 8000 | REST API server             |
| frontend      | Custom (Next.js) | 3000 | SSR web application         |
| db            | postgres:15      | 5432 | PostgreSQL database         |
| redis         | redis:7          | 6379 | Cache and Celery broker     |
| celery-worker | Same as backend  | —    | Async task processing       |
| celery-beat   | Same as backend  | —    | Periodic task scheduling    |
| flower        | mher/flower      | 5555 | Celery monitoring dashboard |

---

## Data Flow

### API Request Lifecycle

1. Client sends HTTPS request to the API
2. Nginx terminates TLS and proxies to the Django backend
3. `TenantMainMiddleware` resolves the tenant from the Host header
4. DRF authentication validates the JWT access token
5. Permission classes enforce role-based access control
6. Serializer validates the request payload
7. View or ViewSet executes the business logic
8. Response serializer formats the output as JSON
9. Pagination wrapper adds count, next, and previous links
10. JSON response is returned to the client

### Background Task Flow

1. View or signal dispatches a Celery task with `.delay()` or `.apply_async()`
2. Task message is serialised and pushed to the Redis broker
3. Celery worker picks up the task from the queue
4. Worker sets the tenant schema context before execution
5. Task runs to completion and result is stored
6. Celery Beat schedules periodic tasks (reports, cleanups)

---

## Security Boundaries

| Boundary                 | Mechanism                                                        |
| ------------------------ | ---------------------------------------------------------------- |
| Tenant data isolation    | PostgreSQL schema separation                                     |
| Authentication           | JWT access + refresh tokens                                      |
| Authorisation            | DRF permission classes (role-based)                              |
| Transport security       | HTTPS / TLS via Nginx                                            |
| CSRF protection          | Django CSRF middleware (session views)                           |
| CORS                     | django-cors-headers with allowlisted origins                     |
| Rate limiting            | DRF throttle classes (anonymous: 100/hr, authenticated: 1000/hr) |
| Secret management        | Environment variables, never committed to source                 |
| Input validation         | DRF serializer field-level and object-level validation           |
| SQL injection prevention | Django ORM parameterised queries                                 |

---

## Related Decisions

| ADR      | Decision                   | Link                                                                    |
| -------- | -------------------------- | ----------------------------------------------------------------------- |
| ADR-0001 | Monorepo structure         | [0001-monorepo-structure.md](../adr/0001-monorepo-structure.md)         |
| ADR-0002 | Schema-based multi-tenancy | [0002-multi-tenancy-approach.md](../adr/0002-multi-tenancy-approach.md) |
| ADR-0003 | Technology stack           | [0003-technology-stack.md](../adr/0003-technology-stack.md)             |

---

## Further Reading

- [Backend Documentation](../backend/README.md)
- [Frontend Documentation](../frontend/README.md)
- [API Overview](../api/overview.md)
- [Getting Started Guide](../guides/getting-started.md)
- [Multi-Tenancy Guide](../guides/multi-tenancy.md)
