# Getting Started

> Onboarding guide for new developers joining the LankaCommerce Cloud project.

**Navigation:** [Docs Index](../index.md) · [Development Setup](development-setup.md) · [Docker Development](docker-development.md)

---

## Welcome

LankaCommerce Cloud (LCC) is a multi-tenant SaaS ERP, POS, and e-commerce platform built for Sri Lankan SMEs. This guide walks you through everything you need to get started contributing.

---

## Prerequisites

Before you begin, ensure you have the following installed:

| Tool           | Minimum Version | Purpose                                    |
| -------------- | --------------- | ------------------------------------------ |
| Git            | 2.40+           | Version control                            |
| Python         | 3.12+           | Backend runtime                            |
| Node.js        | 20+             | Frontend runtime                           |
| pnpm           | 9+              | Frontend package manager                   |
| Docker         | 24+             | Containerized development                  |
| Docker Compose | 2.20+           | Multi-service orchestration                |
| PostgreSQL     | 15+             | Database (or use Docker)                   |
| Redis          | 7+              | Caching and message broker (or use Docker) |

---

## Quick Start

Follow these steps to get the project running locally:

1. Clone the repository: `git clone https://github.com/your-org/lankacommerce-cloud.git`
2. Change into the project directory: `cd lankacommerce-cloud`
3. Copy the environment file: `cp backend/.env.example backend/.env`
4. Start all services with Docker: `docker compose up -d`
5. Run database migrations: `docker compose exec backend python manage.py migrate`
6. Create a superuser: `docker compose exec backend python manage.py createsuperuser`
7. Open the backend in your browser: visit `http://localhost:8000/admin/`
8. Open the frontend in your browser: visit `http://localhost:3000/`

> For a full non-Docker setup, see the [Development Setup Guide](development-setup.md).

---

## Project Structure Overview

| Directory          | Purpose                                                    |
| ------------------ | ---------------------------------------------------------- |
| `backend/`         | Django backend — REST API, business logic, database models |
| `frontend/`        | Next.js frontend — ERP dashboard and webstore UI           |
| `docker/`          | Dockerfiles and container configuration                    |
| `docs/`            | Project documentation                                      |
| `Document-Series/` | Phased implementation plans                                |
| `shared/`          | Shared constants and types                                 |
| `scripts/`         | Utility and automation scripts                             |
| `tests/`           | End-to-end and integration tests                           |

---

## Key Documentation

| Document                                    | Description                                       |
| ------------------------------------------- | ------------------------------------------------- |
| [Development Setup](development-setup.md)   | Full local development setup (backend + frontend) |
| [Docker Development](docker-development.md) | Docker-based development workflow                 |
| [Database Guide](database.md)               | Migrations, seeding, and backups                  |
| [Backend README](../../backend/README.md)   | Backend directory structure and commands          |
| [Frontend README](../../frontend/README.md) | Frontend directory structure and commands         |
| [API Overview](../api/overview.md)          | REST API architecture and entry points            |
| [Contributing Guide](../../CONTRIBUTING.md) | How to contribute code and documentation          |

---

## Development Workflow

1. Create a feature branch from `main`: `git checkout -b feature/your-feature-name`
2. Make your changes and write tests
3. Run backend tests: `cd backend && python -m pytest`
4. Run frontend tests: `cd frontend && pnpm test`
5. Commit using conventional commits: `git commit -m "feat: add your feature description"`
6. Push your branch: `git push origin feature/your-feature-name`
7. Open a Pull Request on GitHub
8. Address review feedback and get approval
9. Merge into `main`

> See [Branching Strategy](../BRANCHING.md) and [Commit Conventions](../COMMITS.md) for details.

---

## Getting Help

| Channel                | Description                           |
| ---------------------- | ------------------------------------- |
| GitHub Issues          | Bug reports and feature requests      |
| GitHub Discussions     | Questions and community conversations |
| Code Review Guidelines | [CODE_REVIEW.md](../CODE_REVIEW.md)   |

---

## Next Steps

- Set up your local environment → [Development Setup](development-setup.md)
- Or use Docker → [Docker Development](docker-development.md)
- Explore the API → [API Overview](../api/overview.md)
- Read the contributing guide → [CONTRIBUTING.md](../../CONTRIBUTING.md)
