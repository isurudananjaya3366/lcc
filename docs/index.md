# LankaCommerce Cloud — Documentation Hub

> Central navigation hub for all project documentation.

---

## 📖 Getting Started

| Document                                           | Description                                                        |
| -------------------------------------------------- | ------------------------------------------------------------------ |
| [Project README](../README.md)                     | Project overview, quick start, and tech stack                      |
| [Getting Started Guide](guides/getting-started.md) | New developer onboarding and quick start steps                     |
| [Development Setup](guides/development-setup.md)   | Full local development setup (backend, frontend, database)         |
| [Docker Development](guides/docker-development.md) | Docker Compose-based development workflow                          |
| [Database Guide](guides/database.md)               | Migrations, seeding, backups, and maintenance                      |
| [Multi-Tenancy Guide](guides/multi-tenancy.md)     | Tenant provisioning, schema isolation, and operations              |
| [Docker Environment Variables](DOCKER_ENV.md)      | Docker-specific env configuration and service mapping              |
| [Environment Variable Reference](ENV_VARIABLES.md) | Complete reference for all backend, frontend, and Docker variables |

---

## 🛠 Developer Guides

| Document                                           | Description                                           |
| -------------------------------------------------- | ----------------------------------------------------- |
| [Testing Guide](guides/testing.md)                 | Test strategy, execution steps, and coverage targets  |
| [Debugging Guide](guides/debugging.md)             | Logging, tracing, and debugging tooling               |
| [Deployment Guide](guides/deployment.md)           | Deployment steps, production checklist, and rollbacks |
| [Troubleshooting Guide](guides/troubleshooting.md) | Common issues and step-by-step resolutions            |

---

## 🔧 Backend Documentation

| Document                                          | Description                                                |
| ------------------------------------------------- | ---------------------------------------------------------- |
| [Backend README](../backend/README.md)            | Backend setup, directory structure, and development guide  |
| [Backend Docs Overview](backend/README.md)        | Backend documentation index                                |
| [Apps Guide](backend/apps.md)                     | Django app structure, responsibilities, and conventions    |
| [Models Guide](backend/models.md)                 | Base models, mixins, domain models, and naming conventions |
| [API Guide](backend/api.md)                       | API architecture, authentication, and endpoint reference   |
| [API Overview](api/overview.md)                   | API entry points, modules, and response formats            |
| [API Authentication](api/authentication.md)       | JWT flows, tokens, and security best practices             |
| [API Errors](api/errors.md)                       | Error response formats and troubleshooting                 |
| [API Pagination](api/pagination.md)               | Page-number pagination model and parameters                |
| [API Rate Limiting](api/rate-limiting.md)         | Throttle limits, headers, and retry guidance               |
| [API Versioning](api/versioning.md)               | URL versioning strategy and deprecation policy             |
| [Architecture Overview](architecture/overview.md) | System architecture, boundaries, and design decisions      |

---

## 🎨 Frontend Documentation

| Document                                     | Description                                                |
| -------------------------------------------- | ---------------------------------------------------------- |
| [Frontend README](../frontend/README.md)     | Frontend setup, component structure, and development guide |
| [Frontend Docs Overview](frontend/README.md) | Frontend documentation index                               |
| [Components Guide](frontend/components.md)   | UI component categories, conventions, and patterns         |
| [Hooks Guide](frontend/hooks.md)             | Custom hooks, data fetching, and React Query patterns      |
| [State Management](frontend/state.md)        | Zustand stores, state boundaries, and middleware           |

---

## � Database Documentation

| Document                                                                | Description                                                    |
| ----------------------------------------------------------------------- | -------------------------------------------------------------- |
| [Schema Naming & Multi-Tenancy Layout](database/schema-naming.md)       | Tenant schema naming, public schema baseline, search_path      |
| [Tenant Settings Reference](database/tenant-settings.md)                | Django-tenants configuration, storage, and safety rules        |
| [App Classification — SHARED vs TENANT](database/app-classification.md) | How apps are classified for multi-tenant schema isolation      |
| [Tenant and Domain Models](database/tenant-models.md)                   | Tenant and Domain model reference, fields, and admin           |
| [Database Routers](database/database-routers.md)                        | Router configuration, routing rules, cross-schema prevention   |
| [Database Routing Guide](multi-tenancy/database-routing.md)             | How routing works across schemas (overview)                    |
| [Tenant Management Commands](multi-tenancy/tenant-commands.md)          | tenant_create, tenant_list commands and Makefile targets       |
| [Public Schema ERD](database/public-schema-erd.md)                      | Entity relationships and model reference for the public schema |
| [Naming Conventions](database/naming-conventions.md)                    | Table, field, schema, and index naming rules                   |
| [PgBouncer Connection Pooling](database/pgbouncer.md)                   | Connection pooling configuration, Django integration           |
| [Indexing Guidelines](database/indexing-guidelines.md)                  | Index strategy, naming conventions, monitoring                 |
| [Performance Tuning Guide](database/performance-tuning.md)              | All tuning parameters, rationale, and checklist                |
| [Backup and Recovery Procedures](database/backup-procedures.md)         | Backup strategy, restore workflows, WAL archiving              |
| [Monitoring Queries](database/monitoring-queries.md)                    | Database health, performance, and capacity monitoring          |

---

## 💼 SaaS Platform

| Document                                         | Description                                               |
| ------------------------------------------------ | --------------------------------------------------------- |
| [Subscription Plans](saas/subscription-plans.md) | Plan tiers, pricing in LKR, resource limits, and features |
| [Feature Flags](saas/feature-flags.md)           | Feature flag model, rollout strategy, and key naming      |

---

## 🏢 Platform Services

| Document                                   | Description                                             |
| ------------------------------------------ | ------------------------------------------------------- |
| [Audit Logging](platform/audit-logging.md) | Audit event types, actor tracking, and retention policy |
| [Billing Setup](platform/billing-setup.md) | Billing model, BRN validation, and payment lifecycle    |

---

## � Users & Authentication

| Document                                      | Description                                            |
| --------------------------------------------- | ------------------------------------------------------ |
| [User Hierarchy](users/user-hierarchy.md)     | Platform vs tenant user architecture and access levels |
| [Role Permissions](users/role-permissions.md) | Platform role definitions and permission matrix        |

---

## �🔒 Security & Secrets

| Document                          | Description                                                      |
| --------------------------------- | ---------------------------------------------------------------- |
| [Secrets Management](SECRETS.md)  | Secrets classification, rotation policy, and security checklists |
| [Security Policy](../SECURITY.md) | Vulnerability disclosure and reporting process                   |

---

## � Architecture Decision Records

| Document                                                           | Description                                       |
| ------------------------------------------------------------------ | ------------------------------------------------- |
| [ADR Index](adr/README.md)                                         | Full list of architecture decision records        |
| [ADR-0001: Monorepo Structure](adr/0001-monorepo-structure.md)     | Why we chose a monorepo over polyrepo             |
| [ADR-0002: Multi-Tenancy](adr/0002-multi-tenancy-approach.md)      | Schema-based multi-tenancy with django-tenants    |
| [ADR-0003: Technology Stack](adr/0003-technology-stack.md)         | Django, Next.js, PostgreSQL, and supporting tools |
| [ADR-0004: Per-Tenant Auth](adr/0004-per-tenant-authentication.md) | Per-tenant authentication and user isolation      |
| [ADR Template](adr/template.md)                                    | Template for creating new ADRs                    |

---

## �📏 Standards & Workflows

| Document                                  | Description                             |
| ----------------------------------------- | --------------------------------------- |
| [Branching Strategy](BRANCHING.md)        | Git workflow, branch naming conventions |
| [Branch Protection](BRANCH_PROTECTION.md) | PR requirements and merge rules         |
| [Commit Conventions](COMMITS.md)          | Conventional commit format and examples |
| [Code Review Guidelines](CODE_REVIEW.md)  | Review checklist and approval standards |

---

## 🤝 Community & Contribution

| Document                                 | Description                                    |
| ---------------------------------------- | ---------------------------------------------- |
| [Contributing Guide](../CONTRIBUTING.md) | How to contribute code, docs, and translations |
| [Code of Conduct](../CODE_OF_CONDUCT.md) | Community standards and expectations           |

---

## 📊 Project Management

| Document                               | Description                                  |
| -------------------------------------- | -------------------------------------------- |
| [Changelog](../CHANGELOG.md)           | Version history and release notes            |
| [Verification Record](VERIFICATION.md) | Environment validation results and checklist |

---

## 🏗 Infrastructure

| Document                                    | Description                                            |
| ------------------------------------------- | ------------------------------------------------------ |
| [Docker Setup](../docker/README.md)         | Docker directory structure and container configuration |
| [Docker Development Setup](docker-setup.md) | Step-by-step Docker development environment guide      |

---

## 📂 Directory Map

```
docs/
├── index.md              # This file — documentation hub
├── README.md             # Documentation directory overview
├── docker-setup.md       # Docker development guide
├── DOCKER_ENV.md         # Docker environment variables
├── ENV_VARIABLES.md      # Complete variable reference
├── SECRETS.md            # Secrets management policy
├── VERIFICATION.md       # Validation records
├── BRANCHING.md          # Branching strategy
├── BRANCH_PROTECTION.md  # Branch protection rules
├── COMMITS.md            # Commit conventions
├── CODE_REVIEW.md        # Code review guidelines
├── adr/                  # Architecture Decision Records
│   ├── README.md
│   ├── template.md
│   ├── 0001-monorepo-structure.md
│   ├── 0002-multi-tenancy-approach.md
│   ├── 0003-technology-stack.md
│   └── 0004-per-tenant-authentication.md
├── api/                  # API documentation
│   ├── overview.md
│   ├── authentication.md
│   ├── errors.md
│   ├── pagination.md
│   ├── rate-limiting.md
│   └── versioning.md
├── architecture/         # Architecture docs
│   └── overview.md
├── backend/              # Backend technical docs
│   ├── README.md
│   ├── apps.md
│   ├── models.md
│   └── api.md
├── database/             # Database architecture docs
│   ├── schema-naming.md
│   ├── tenant-settings.md
│   ├── app-classification.md
│   ├── tenant-models.md
│   ├── database-routers.md
│   ├── public-schema-erd.md
│   ├── naming-conventions.md
│   ├── pgbouncer.md
│   ├── indexing-guidelines.md
│   ├── performance-tuning.md
│   ├── backup-procedures.md
│   └── monitoring-queries.md
├── multi-tenancy/        # Multi-tenancy guides
│   ├── database-routing.md
│   └── tenant-commands.md
├── saas/                 # SaaS platform docs
│   ├── subscription-plans.md
│   └── feature-flags.md
├── platform/             # Platform services docs
│   ├── audit-logging.md
│   └── billing-setup.md
├── users/                # User & auth docs
│   └── user-hierarchy.md
├── frontend/             # Frontend technical docs
│   ├── README.md
│   ├── components.md
│   ├── hooks.md
│   └── state.md
└── guides/               # Developer guides
    ├── getting-started.md
    ├── development-setup.md
    ├── docker-development.md
    ├── database.md
    ├── multi-tenancy.md
    ├── testing.md
    ├── debugging.md
    ├── deployment.md
    └── troubleshooting.md
```

---

> See the [Documentation README](README.md) for a compact reference, or the [Project README](../README.md) for the project overview.
