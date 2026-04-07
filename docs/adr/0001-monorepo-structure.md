# ADR-0001: Monorepo Structure

> **Status:** Accepted  
> **Date:** 2025-01-01  
> **Authors:** LankaCommerce Cloud Team

---

## Context

LankaCommerce Cloud consists of multiple components: a Django backend, a Next.js frontend, Docker configuration, shared types and constants, documentation, and end-to-end tests. The team needed to decide whether to organize these as separate repositories (polyrepo) or a single repository (monorepo).

Key considerations included:

- The backend and frontend share types, constants, and environment configuration
- Docker Compose requires access to both backend and frontend Dockerfiles
- CI/CD pipelines need to build and test both components together
- A small team manages all components, making coordination overhead important
- Shared documentation should live close to the code it describes

---

## Decision

We will use a **monorepo structure** with the backend, frontend, Docker configuration, documentation, and shared code all living in a single Git repository.

The top-level directory structure is:

| Directory   | Purpose                                 |
| ----------- | --------------------------------------- |
| `backend/`  | Django REST API and business logic      |
| `frontend/` | Next.js dashboard and webstore UI       |
| `docker/`   | Dockerfiles and container configuration |
| `docs/`     | Project documentation                   |
| `shared/`   | Shared constants and TypeScript types   |
| `scripts/`  | Utility and automation scripts          |
| `tests/`    | End-to-end and integration tests        |

---

## Consequences

### Positive

- Single source of truth for all project code and configuration
- Atomic commits that span backend and frontend changes
- Shared Docker Compose configuration works without cross-repo references
- Simplified CI/CD — one pipeline builds and tests everything
- Easier onboarding — new developers clone one repository
- Shared types and constants are immediately available to both components

### Negative

- Repository size will grow larger over time
- Git history includes changes for all components, making per-component history noisier
- CI pipelines must selectively run tests based on which directories changed (or run everything)
- IDE indexing may be slower with the full project open

### Neutral

- Code ownership and review assignments must be managed through CODEOWNERS or CI rules rather than repository-level permissions

---

## Alternatives Considered

| Alternative                                        | Reason for Rejection                                                                                               |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Polyrepo (separate repos for backend and frontend) | Increased coordination overhead, duplicate CI configuration, harder to share types and keep Docker Compose in sync |
| Git submodules                                     | Added complexity for developers, fragile cross-repo references, difficult to maintain atomic commits               |
| Monorepo tooling (Nx, Turborepo)                   | Unnecessary complexity at current project scale; can be adopted later if needed                                    |

---

## References

- [Monorepo vs Polyrepo — Atlassian](https://www.atlassian.com/git/tutorials/monorepos)
- [Project Structure](../../README.md) — Root README project structure section
