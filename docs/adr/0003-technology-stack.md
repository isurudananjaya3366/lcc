# ADR-0003: Technology Stack

> **Status:** Accepted  
> **Date:** 2025-01-01  
> **Authors:** LankaCommerce Cloud Team

---

## Context

LankaCommerce Cloud is a multi-tenant SaaS ERP, POS, and e-commerce platform targeting Sri Lankan SMEs. The team needed to select a technology stack that meets the following requirements:

- Rapid development for a small team
- Strong ecosystem for ERP, e-commerce, and REST API development
- Multi-tenancy support at the database level
- Modern, responsive frontend with server-side rendering for SEO
- Background task processing for reports, notifications, and integrations
- Real-time capabilities for POS and inventory updates
- Sri Lanka localization (LKR currency, Sinhala/Tamil languages)
- Docker-based deployment for consistency across environments

---

## Decision

We will use the following technology stack:

### Backend

| Technology                    | Version | Purpose                    |
| ----------------------------- | ------- | -------------------------- |
| Python                        | 3.12+   | Backend language           |
| Django                        | 5.x     | Web framework              |
| Django REST Framework         | 3.14+   | REST API                   |
| PostgreSQL                    | 15      | Primary database           |
| Redis                         | 7       | Cache and message broker   |
| Celery                        | 5.x     | Background task processing |
| django-tenants                | 3.x     | Schema-based multi-tenancy |
| djangorestframework-simplejwt | 5.x     | JWT authentication         |
| drf-spectacular               | 0.26+   | OpenAPI schema generation  |
| Django Channels               | 4.x     | WebSocket support          |

### Frontend

| Technology             | Version | Purpose                            |
| ---------------------- | ------- | ---------------------------------- |
| TypeScript             | 5.x     | Frontend language                  |
| Next.js                | 15+     | React framework with SSR/SSG       |
| React                  | 19+     | UI library                         |
| Tailwind CSS           | 3.x     | Utility-first CSS framework        |
| shadcn/ui              | Latest  | Pre-built accessible UI components |
| Zustand                | Latest  | Client-side state management       |
| React Query (TanStack) | 5.x     | Server state and data fetching     |
| React Hook Form        | Latest  | Form state management              |
| pnpm                   | 9+      | Package manager                    |

### Infrastructure

| Technology     | Purpose                                            |
| -------------- | -------------------------------------------------- |
| Docker         | Containerization                                   |
| Docker Compose | Multi-service orchestration                        |
| Nginx          | Reverse proxy and static file serving (production) |
| WhiteNoise     | Static file serving (Django)                       |
| Sentry         | Error tracking (production)                        |

---

## Consequences

### Positive

- Django's mature ecosystem provides built-in admin, ORM, migrations, and auth — accelerating ERP development
- Django REST Framework is the industry standard for building REST APIs in Python
- PostgreSQL's schema feature enables clean multi-tenancy via `django-tenants`
- Next.js provides server-side rendering for SEO (webstore) and a modern React developer experience
- TypeScript catches errors at compile time, improving frontend code quality
- Tailwind CSS and shadcn/ui enable rapid, consistent UI development
- Celery handles background processing (reports, notifications, integrations) with Django integration
- Redis serves double duty as both cache and Celery broker, reducing infrastructure components
- Docker ensures consistent environments from development to production
- All selected technologies have large communities, extensive documentation, and active maintenance

### Negative

- Two language runtimes (Python + Node.js) increase the learning curve for full-stack developers
- Django's synchronous nature requires Channels for WebSocket features, adding complexity
- Next.js's rapid release cycle may require periodic migration effort
- PostgreSQL schema-based multi-tenancy requires careful management at scale
- The full Docker stack requires significant local resources (RAM, CPU)

### Neutral

- pnpm is chosen over npm/yarn for faster installs and disk efficiency
- Zustand is chosen over Redux for simplicity — the team can migrate to Redux if complexity warrants it
- JWT authentication is stateless, which simplifies scaling but requires token refresh handling

---

## Alternatives Considered

| Alternative       | Reason for Rejection                                                                                        |
| ----------------- | ----------------------------------------------------------------------------------------------------------- |
| FastAPI (backend) | Less mature ecosystem for complex ERP features; Django's admin, ORM, and migration system are more suitable |
| NestJS (backend)  | TypeScript-only stack would simplify language but Django's multi-tenancy and ERP ecosystem are stronger     |
| MySQL / MariaDB   | PostgreSQL's schema feature is essential for `django-tenants` multi-tenancy                                 |
| MongoDB           | Document databases add complexity for relational ERP data; PostgreSQL is better suited                      |
| Vue.js / Nuxt.js  | React/Next.js has a larger ecosystem and component library selection                                        |
| Redux             | Zustand is simpler for the current scope; Redux can be adopted later if needed                              |
| Material UI       | shadcn/ui provides more flexibility and avoids opinionated styling                                          |
| Yarn / npm        | pnpm offers better disk efficiency and faster installs for monorepo setups                                  |

---

## References

- [Django documentation](https://docs.djangoproject.com/)
- [Next.js documentation](https://nextjs.org/docs)
- [django-tenants documentation](https://django-tenants.readthedocs.io/)
- [Project README](../../README.md) — Tech stack overview
- [Backend README](../../backend/README.md) — Backend technology details
- [Frontend README](../../frontend/README.md) — Frontend technology details
