# Frontend Architecture

## Overview

The LankaCommerce Cloud frontend is a Next.js 16 application using the App Router, TypeScript, and Tailwind CSS. It serves as the ERP dashboard, POS interface, and webstore for Sri Lankan SMEs.

## Technology Stack

- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript 5.x (strict mode)
- **Styling:** Tailwind CSS 3.x + shadcn/ui
- **State:** Zustand (client) + Server Components (server)
- **Validation:** Zod v4
- **Package Manager:** pnpm 8.x

## Project Structure

```
frontend/
├── app/                 # App Router — pages, layouts, API routes
│   ├── (auth)/          # Auth pages (login, register)
│   ├── (dashboard)/     # Dashboard pages (inventory, sales, etc.)
│   ├── api/             # API route handlers
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Home page
│   ├── loading.tsx      # Root loading state
│   ├── error.tsx        # Root error boundary
│   └── not-found.tsx    # 404 page
├── components/          # React components
│   ├── ui/              # UI primitives (Button, Input, Card)
│   ├── layout/          # Layout components (Header, Sidebar)
│   ├── forms/           # Form composites
│   ├── common/          # Shared components (Logo, Spinner)
│   └── modules/         # Feature-specific module components
├── lib/                 # Utilities & helpers
│   ├── env.ts           # Environment variable validation (Zod)
│   ├── cn.ts            # Tailwind class merger
│   └── utils.ts         # General utilities
├── hooks/               # Custom React hooks
├── services/            # API service layer
├── stores/              # Zustand state stores
├── types/               # TypeScript type definitions
├── constants/           # App configuration & constants
├── styles/              # Global styles
├── public/              # Static assets
└── __tests__/           # Test files
```

## App Router Architecture

### Routing

File-system based routing via the `app/` directory:

- `page.tsx` — route page
- `layout.tsx` — shared layout (persists across navigation)
- `loading.tsx` — loading state (Suspense fallback)
- `error.tsx` — error boundary
- `not-found.tsx` — 404 page
- `route.ts` — API route handler

### Route Groups

Parentheses `(group)` for logical grouping without URL impact:

- `(auth)` — login, register pages
- `(dashboard)` — ERP dashboard modules

### Server vs Client Components

- **Server Components** (default) — render on server, no client JS
- **Client Components** (`"use client"`) — for interactivity, state, effects

## Data Flow

```
Browser → Next.js Server → Django API (port 8000)
                ↓
         Server Components (fetch data)
                ↓
         Client Components (interactivity)
```

## Multi-Tenant Architecture

- Tenant ID sent via `X-Tenant-ID` header
- Tenant context provider wraps the dashboard
- Data isolation enforced at the API layer
- Tenant-specific routing via subdomain pattern

## Authentication

- JWT token-based authentication
- Token stored in httpOnly cookies
- Automatic token refresh before expiry
- Protected routes via Next.js middleware
- Auth state managed in Zustand store

## State Management

| Type          | Technology       | Use Case                        |
| ------------- | ---------------- | ------------------------------- |
| Server state  | Server Components | Data fetching, initial load     |
| Client state  | Zustand          | UI state, user preferences      |
| Form state    | React Hook Form  | Form validation, submission     |
| URL state     | Next.js Router   | Filters, pagination, search     |

## Build & Deployment

- **Output:** Standalone (optimized for Docker)
- **Docker:** Multi-stage build (~100MB production image)
- **Dev:** Turbopack for fast hot reloading
- **CI:** Type-check + lint + test before build

## Styling Architecture

- **Tailwind CSS** for utility-first styling
- **`cn()` helper** merges classes and resolves Tailwind conflicts (`lib/cn.ts`)
- **Design tokens** defined in `tailwind.config.ts` (colors, spacing, typography)
- **Responsive design:** Mobile-first breakpoints (sm, md, lg, xl, 2xl)
- **Dark mode:** Planned via `next-themes` (class-based strategy)
- **Component styling:** Tailwind utilities + CVA (`class-variance-authority`) for variant patterns

## Type System

- **Strict mode** with all 9 strict options enabled
- **Type definitions** organized in `types/` directory
- **API types:** Mirror backend response shapes
- **Component props:** Interface-first (`interface ButtonProps`)
- **Utility types:** `Nullable<T>`, `Optional<T>`, `ID`, `Timestamp`, `Currency` in `types/index.d.ts`
- **Zod schemas** for runtime validation (env vars, forms, API responses)

## Error Handling Strategy

- **Error boundaries:** `error.tsx` at root and route group levels
- **API errors:** Centralized error transformation in API service layer
- **User-friendly messages:** No technical details exposed to users
- **Logging:** `console.error` in dev, Sentry in production (planned)
- **Recovery:** "Try Again" reset and "Go Home" navigation options

## Scalability Considerations

- **Code splitting:** Automatic per-route via App Router
- **Lazy loading:** `next/dynamic` for heavy components
- **Image optimization:** `next/image` with WebP/AVIF formats
- **Bundle analysis:** `pnpm analyze` to monitor bundle sizes
- **Tree shaking:** ES modules with individual exports
- **Cache strategy:** ISR and SWR for data freshness vs performance
