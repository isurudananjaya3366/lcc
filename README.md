# LankaCommerce Cloud (LCC)

> **Sri Lanka-first multi-tenant POS + ERP + Webstore platform** — LKR-ready, trilingual (English, Sinhala, Tamil) 🇱🇰

<!-- Badges -->

![Build](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-0.1.0-informational)
![Python](https://img.shields.io/badge/python-3.12+-3776AB?logo=python&logoColor=white)
![Node](https://img.shields.io/badge/node-20_LTS-339933?logo=node.js&logoColor=white)
![Django](https://img.shields.io/badge/django-5.x-092E20?logo=django&logoColor=white)
![Next.js](https://img.shields.io/badge/next.js-15.x-000000?logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/typescript-5.x-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-compose-2496ED?logo=docker&logoColor=white)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Documentation](#-documentation)
- [Community](#-community)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📋 Overview

LankaCommerce Cloud (LCC) is a modern, cloud-native **SaaS platform** purpose-built for Sri Lankan small and medium enterprises. It unifies **Point-of-Sale**, **Enterprise Resource Planning**, and a **customer-facing Webstore** into a single multi-tenant system with complete tenant isolation.

**Target Users:** Retail shops, wholesalers, distributors, and SME businesses across Sri Lanka.

**Core Modules:**

| Module             | Description                                                                 |
| ------------------ | --------------------------------------------------------------------------- |
| 🏪 **POS**         | Sales terminals, receipt printing, barcode scanning, cash management        |
| 📦 **Inventory**   | Warehouse management, stock tracking, location management, low-stock alerts |
| 🛒 **Webstore**    | Product catalog, shopping cart, checkout, order management                  |
| 💰 **Accounting**  | Invoicing, payments, basic financial reporting                              |
| 👥 **HR**          | Employee management, attendance, payroll basics                             |
| 📊 **Reports**     | Sales analytics, inventory reports, financial dashboards                    |
| 🤖 **AI Features** | Smart product descriptions, intelligent search, demand forecasting          |

## ✨ Key Features

- **Multi-Tenant Architecture** — Secure schema-level tenant isolation via PostgreSQL schemas
- **Sri Lanka Localization** — LKR currency, Asia/Colombo timezone, Sinhala/Tamil language support
- **Local Payment Integration** — PayHere gateway with sandbox and live support
- **Local Delivery Integration** — Domex, Koombiyo courier services _(planned)_
- **Sinhala/Singlish-Aware Search** — Natural language search in local languages _(planned)_
- **Offline-First POS** — Service worker support for reliable in-store operation _(planned)_
- **Real-Time Updates** — WebSocket-powered live notifications and order tracking
- **Role-Based Access Control** — Granular permissions per tenant and user role
- **API-First Design** — RESTful API with comprehensive OpenAPI documentation
- **Background Task Processing** — Celery workers for async jobs, scheduled tasks, and email

## 🛠 Tech Stack

### Backend

| Technology                | Purpose                                                       |
| ------------------------- | ------------------------------------------------------------- |
| **Django 5.x**            | Web framework with multi-tenant support via `django-tenants`  |
| **Django REST Framework** | API layer with serialization, authentication, and permissions |
| **PostgreSQL 15**         | Primary database with schema-based tenant isolation           |
| **Redis 7**               | Caching layer and Celery message broker                       |
| **Celery**                | Distributed task queue for background processing              |
| **Celery Beat**           | Periodic task scheduler                                       |

### Frontend

| Technology       | Purpose                                         |
| ---------------- | ----------------------------------------------- |
| **Next.js 15**   | React framework with SSR, SSG, and API routes   |
| **TypeScript**   | Type-safe JavaScript for reliability            |
| **Tailwind CSS** | Utility-first styling with shadcn/ui components |
| **Zustand**      | Lightweight state management                    |

### Infrastructure

| Technology                  | Purpose                                                   |
| --------------------------- | --------------------------------------------------------- |
| **Docker & Docker Compose** | Containerized development and production environments     |
| **Nginx**                   | Reverse proxy and static file serving _(production)_      |
| **GitHub Actions**          | CI/CD pipeline _(planned)_                                |
| **AWS**                     | Cloud hosting, S3 storage, Secrets Manager _(production)_ |

## 🚀 Quick Start

### Prerequisites

- **Git** — Version control
- **Docker Desktop** 24.x+ — Container runtime (includes Docker Compose v2)
- **Python** 3.12+ — For running validation scripts locally
- **Node.js** 20 LTS — For running frontend scripts locally
- **8 GB RAM minimum** (16 GB recommended)

### Getting Started

1. **Clone the repository** and navigate to the project root
2. **Copy the Docker environment file** from `.env.docker.example` to `.env.docker`
3. **Generate secrets** — Create unique values for `DJANGO_SECRET_KEY` and `NEXTAUTH_SECRET`
4. **Start the development stack** using Docker Compose
5. **Open the applications** in your browser

### Development URLs

| Service     | URL                   | Description                   |
| ----------- | --------------------- | ----------------------------- |
| Backend API | http://localhost:8000 | Django REST API               |
| Frontend    | http://localhost:3000 | Next.js application           |
| Flower      | http://localhost:5555 | Celery monitoring dashboard   |
| PostgreSQL  | localhost:5432        | Database (for external tools) |
| Redis       | localhost:6379        | Cache (for external tools)    |

> 🕐 **Timezone:** All services default to `Asia/Colombo` (UTC+5:30)

## 📁 Project Structure

```
lankacommerce-cloud/
├── backend/              # Django REST API + tenant services
│   ├── apps/             # Django application modules
│   ├── config/           # Django settings and configuration
│   ├── tests/            # Backend test suite
│   └── requirements/     # Python dependency files
├── frontend/             # Next.js ERP dashboard + webstore
│   ├── app/              # Next.js app router pages
│   ├── components/       # Reusable UI components
│   ├── services/         # API service layer
│   └── stores/           # State management
├── docker/               # Docker configuration files
│   ├── backend/          # Backend Dockerfiles
│   ├── frontend/         # Frontend Dockerfiles
│   ├── postgres/         # Database init and config
│   ├── redis/            # Redis configuration
│   └── scripts/          # Container entrypoints and utilities
├── docs/                 # Project documentation
├── scripts/              # Development utility scripts
├── shared/               # Shared constants and types
├── Document-Series/      # AI-agent task documents (internal)
└── tests/                # Cross-cutting integration tests
```

> For a detailed breakdown of each directory, see the [Documentation Index](docs/README.md).

## 🧪 Development

### Common Commands (Makefile)

| Command             | Description                        |
| ------------------- | ---------------------------------- |
| `make dev`          | Start development environment      |
| `make down`         | Stop all containers                |
| `make logs`         | View container logs (follow mode)  |
| `make test`         | Run all tests (backend + frontend) |
| `make lint`         | Run all linters                    |
| `make format`       | Format all code                    |
| `make validate-env` | Validate environment variables     |
| `make migrate`      | Run database migrations            |
| `make shell`        | Open Django shell                  |
| `make status`       | Show container health status       |

Run `make help` to see all available commands.

## 📖 Documentation

> Full documentation hub: [docs/index.md](docs/index.md)

### Guides

- [Docker Development Setup](docs/docker-setup.md) — Full Docker environment guide
- [Docker Environment Variables](docs/DOCKER_ENV.md) — Docker-specific env configuration
- [Environment Variable Reference](docs/ENV_VARIABLES.md) — Complete variable documentation
- [Secrets Management](docs/SECRETS.md) — Secrets handling policy and security

### Standards

- [Branching Strategy](docs/BRANCHING.md) — Git workflow and branch naming
- [Branch Protection & Merge Rules](docs/BRANCH_PROTECTION.md) — PR and merge policies
- [Commit Conventions](docs/COMMITS.md) — Conventional commit format
- [Code Review Guidelines](docs/CODE_REVIEW.md) — Review standards and checklist

### References

- [Changelog](CHANGELOG.md) — Version history
- [API Documentation](docs/api/) — API reference _(planned)_
- [Architecture Overview](docs/architecture/) — System architecture _(planned)_

## 🤝 Community

- [Contributing Guide](CONTRIBUTING.md) — How to contribute code, docs, and translations
- [Code of Conduct](CODE_OF_CONDUCT.md) — Community standards and expectations
- [Security Policy](SECURITY.md) — How to report vulnerabilities privately

### 💬 Support

For questions, feature requests, or general discussion:

- **GitHub Issues** — [Open an issue](https://github.com/AkbarBeiwormo/pos/issues) for bugs and feature requests
- **GitHub Discussions** — Community Q&A and ideas _(planned)_
- **Email** — `support@lankacommerce.lk` _(placeholder)_

## 🤲 Contributing

Contributions are welcome — please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

We follow:

- **Conventional Commits** — see [COMMITS.md](docs/COMMITS.md)
- **Git Flow** branching — see [BRANCHING.md](docs/BRANCHING.md)
- **Code Review** standards — see [CODE_REVIEW.md](docs/CODE_REVIEW.md)

## 📄 License

MIT — see [LICENSE](LICENSE).

---

© 2026 LankaCommerce Cloud Contributors
