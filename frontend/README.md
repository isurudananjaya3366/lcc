# LankaCommerce Cloud — Frontend

Frontend application for the **LankaCommerce Cloud** multi-tenant SaaS ERP platform, designed for Sri Lankan SMEs.

## Overview

The LankaCommerce Cloud frontend is a modern, multi-tenant web application built with Next.js (App Router). It provides:

- **ERP Dashboard** — inventory, sales, purchasing, accounting, HR modules
- **POS Interface** — point-of-sale with offline support
- **Webstore / E-Commerce** — customer-facing storefront
- **AI-Powered Features** — demand forecasting, smart search, recommendations

For the full project overview, see the [main project README](../README.md).

---

## Technology Stack

| Category       | Technology               | Version   |
| -------------- | ------------------------ | --------- |
| **Framework**  | Next.js (App Router)     | 16.x      |
| **Language**   | TypeScript               | 5.x       |
| **Styling**    | Tailwind CSS             | 3.x       |
| **State**      | Zustand                  | (planned) |
| **Icons**      | Lucide React             | 0.x       |
| **Theming**    | next-themes              | 0.x       |
| **Components** | Shadcn/UI                | (planned) |
| **Variants**   | class-variance-authority | 0.7.x     |
| **Utilities**  | clsx + tailwind-merge    | latest    |

---

## Prerequisites

- **Node.js** 20.x LTS or later
- **pnpm** 8.x or later
- **Git** ≥ 2.40

---

## Getting Started

### 1. Install Dependencies

```bash
pnpm install
```

### 2. Set Up Environment

```bash
cp .env.local.example .env.local
# Edit .env.local with your values
```

### 3. Start Development Server

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Available Scripts

| Command           | Description                           |
| ----------------- | ------------------------------------- |
| `pnpm dev`        | Start development server              |
| `pnpm build`      | Build for production                  |
| `pnpm start`      | Start production server               |
| `pnpm lint`       | Run ESLint                            |
| `pnpm format`     | Format code with Prettier             |
| `pnpm type-check` | Run TypeScript check (`tsc --noEmit`) |
| `pnpm test`       | Run tests                             |
| `pnpm clean`      | Remove build artifacts                |
| `pnpm analyze`    | Analyze bundle size                   |

---

## Project Structure

```
frontend/
├── app/             # Next.js App Router (pages, layouts, error boundaries)
├── components/      # React components
│   ├── ui/          # UI primitives (Button, Input, Card, etc.)
│   ├── layout/      # Layout components (Header, Sidebar, Footer)
│   ├── forms/       # Form components (FormField, Select, DatePicker)
│   └── common/      # Shared components (Logo, Avatar, Spinner)
├── hooks/           # Custom React hooks
├── lib/             # Utility functions (utils, cn, formatters)
├── services/        # API services (fetch wrapper, domain services)
├── stores/          # Zustand state stores
├── constants/       # App configuration & constants
├── styles/          # Global styles (variables, animations)
├── types/           # TypeScript type definitions
├── public/          # Static assets (images, icons, fonts)
├── __tests__/       # Test files
└── ...config files  # tsconfig, tailwind, postcss, etc.
```

> For deeper frontend architecture and component documentation, see [docs/frontend/](../docs/frontend/README.md).

---

## Linting

This project uses [ESLint](https://eslint.org/) for code quality with Next.js, TypeScript, React, and import ordering rules.

### Commands

```bash
# Run lint check
pnpm lint

# Fix auto-fixable issues
pnpm lint:fix

# Strict mode (fails on warnings — use in CI)
pnpm lint:strict
```

### Configuration

ESLint is configured in `.eslintrc.json`:
- **Next.js core-web-vitals** — Performance and best practices
- **TypeScript** — Type-safe code rules (`@typescript-eslint`)
- **React & React Hooks** — Component and hooks best practices
- **Import ordering** — Consistent import organization

### IDE Setup

Install the **ESLint** extension in VS Code for inline feedback.

---

## Formatting

This project uses [Prettier](https://prettier.io/) for code formatting, integrated with ESLint.

### Commands

```bash
# Format all files
pnpm format

# Check formatting (CI)
pnpm format:check
```

### Configuration

Prettier is configured in `.prettierrc`:
- **Semicolons:** required
- **Quotes:** single (JS), double (JSX)
- **Tab width:** 2 spaces
- **Trailing commas:** ES5
- **Print width:** 80 characters

### IDE Setup

Install the **Prettier** extension in VS Code and enable **Format on Save**.

---

## Architecture

### App Router

The frontend uses the **Next.js App Router** (`app/` directory) which provides:

- File-system based routing
- Nested layouts
- Server Components by default
- Streaming and Suspense
- Route handlers for API endpoints

### Component Organization

Components follow the **atomic design** pattern:

- **Atoms** (`ui/`) — basic UI elements (buttons, inputs, badges)
- **Molecules** (`forms/`) — form composites (form fields, selects)
- **Organisms** (`layout/`) — complex sections (header, sidebar, dashboard)
- **Shared** (`common/`) — cross-cutting components (logo, spinner, toast)

### State Management

- **Server state** will be managed via **React Query** (caching, re-fetching, optimistic updates).
- **Client state** is managed via **Zustand** stores (UI state, user preferences, cart).

---

## Path Aliases

Import using `@/` prefix for clean, absolute imports:

```typescript
import { cn } from '@/lib/cn'
import { api } from '@/services/api'
import { APP_CONFIG } from '@/constants/config'
import { Button } from '@/components/ui/Button'
```

---

## Environment Variables

See `.env.local.example` for all available variables with documentation.

> For the complete cross-project variable reference, see the [Environment Variable Reference](../docs/ENV_VARIABLES.md).
> For secrets handling and rotation policy, see [Secrets Management](../docs/SECRETS.md).
> For Docker-specific environment loading, see [Docker Environment Variables](../docs/DOCKER_ENV.md).

### Quick Start

```bash
cp .env.local.example .env.local
# Edit .env.local with your values
```

### NEXT_PUBLIC\_ Exposure Rules

Next.js uses the `NEXT_PUBLIC_` prefix to control which environment variables
are exposed to the browser bundle:

| Pattern           | Available In              | Bundled? | Example                          |
| ----------------- | ------------------------- | -------- | -------------------------------- |
| `NEXT_PUBLIC_*`   | Client + Server           | ✅ Yes   | `NEXT_PUBLIC_API_URL`            |
| Without prefix    | Server only (API routes, SSR, middleware) | ❌ No    | `NEXTAUTH_SECRET`, `API_BASE_URL` |

**⚠️ Security Rules:**

1. **NEVER** put secrets in `NEXT_PUBLIC_` variables — they are embedded in the
   JavaScript bundle and visible to anyone.
2. Server-only variables (`NEXTAUTH_SECRET`, `API_BASE_URL`) are **never**
   accessible in client-side code (`use client` components, event handlers).
3. `NEXT_PUBLIC_` values are **inlined at build time** — changing them requires
   a rebuild (`next build`).

### Environment File Loading Order (Next.js)

Next.js loads env files in this order (last wins):

| File                   | Loaded When           | Committed? | Purpose                    |
| ---------------------- | --------------------- | ---------- | -------------------------- |
| `.env`                 | Always                | ✅ Yes     | Shared defaults            |
| `.env.development`     | `NODE_ENV=development`| ❌ No      | Dev-specific defaults      |
| `.env.production`      | `NODE_ENV=production` | ❌ No      | Prod-specific defaults     |
| `.env.local`           | Always (except test)  | ❌ No      | Local overrides + secrets  |
| `.env.development.local` | Dev + local         | ❌ No      | Dev-local overrides        |
| `.env.production.local`  | Prod + local        | ❌ No      | Prod-local overrides       |

### TypeScript Support

All env variables are typed in `types/env.d.ts`. Access with full IntelliSense:

```typescript
// ✅ Type-safe access
const apiUrl = process.env.NEXT_PUBLIC_API_URL; // string
const secret = process.env.NEXTAUTH_SECRET;     // string | undefined

// ✅ Feature flag check
if (process.env.NEXT_PUBLIC_ENABLE_POS === "true") {
  // POS module enabled
}
```

### Runtime Validation (Zod)

Environment variables are validated at **server startup** using [Zod v4](https://zod.dev/).
If any required variable is missing or has an invalid format, the server will **fail fast**
with a descriptive error message.

**How it works:**

1. `lib/env.ts` defines Zod schemas for all server and client env vars.
2. `instrumentation.ts` imports `lib/env.ts` on startup (Next.js instrumentation hook).
3. If validation fails, the server prints a formatted error list and exits.

**Example error output:**

```
❌ Invalid environment variables:

  ✗ NEXT_PUBLIC_API_URL: Required
  ✗ NEXTAUTH_SECRET: Required
  ✗ API_TIMEOUT: Expected number, received "abc"
```

**Using the validated env object:**

```typescript
import { env } from "@/lib/env";

// ✅ Validated and typed — guaranteed to exist
const apiUrl = env.NEXT_PUBLIC_API_URL;
const timeout = env.API_TIMEOUT; // number
const posEnabled = env.NEXT_PUBLIC_ENABLE_POS; // boolean
```

**Troubleshooting:**

- Compare your `.env.local` against `.env.local.example` for missing variables.
- Boolean variables accept: `true`, `false`, `1`, `0`, `yes`, `no` (case-insensitive).
- Numeric variables must contain valid numbers (e.g., `30000`, not `30s`).
- URL variables must include the protocol (e.g., `http://localhost:3000`).

### Client vs Server Variables

Environment variables fall into two categories based on the `NEXT_PUBLIC_` prefix:

**Client-exposed variables** (`NEXT_PUBLIC_*`) — bundled into JavaScript, visible
to the browser. Use for non-sensitive configuration:

| Variable | Purpose | Runtime |
| -------- | ------- | ------- |
| `NEXT_PUBLIC_API_URL` | API endpoint for fetch calls | Client + Server |
| `NEXT_PUBLIC_WS_URL` | WebSocket for real-time features | Client + Server |
| `NEXT_PUBLIC_SITE_NAME` | Brand name in UI | Client + Server |
| `NEXT_PUBLIC_APP_NAME` | Short name (PWA, tabs) | Client + Server |
| `NEXT_PUBLIC_ENABLE_POS` | Feature flag for POS module | Client + Server |
| `NEXT_PUBLIC_DEFAULT_CURRENCY` | Display currency (LKR) | Client + Server |
| `NEXT_PUBLIC_GA_TRACKING_ID` | Analytics tracking | Client + Server |

**Server-only variables** (no prefix) — available in API routes, middleware,
`getServerSideProps`, and Server Components. Use for secrets and internal config:

| Variable | Purpose | Runtime |
| -------- | ------- | ------- |
| `NEXTAUTH_SECRET` | JWT signing secret | Server only |
| `NEXTAUTH_URL` | Auth callback URL | Server only |
| `API_BASE_URL` | Internal API base for SSR | Server only |
| `API_TIMEOUT` | Request timeout in ms | Server only |
| `NODE_ENV` | Runtime environment | Server only |
| `STRIPE_SECRET_KEY` | Stripe server-side payments | Server only |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook verification | Server only |
| `SENTRY_AUTH_TOKEN` | Source map uploads (build) | Server only |

**When to use which:**

```typescript
// ✅ Client component — use NEXT_PUBLIC_ variables
"use client";
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// ✅ Server component / API route — both are available
import { env } from "@/lib/env";
const secret = env.NEXTAUTH_SECRET;     // server-only
const siteUrl = env.NEXT_PUBLIC_API_URL; // also available server-side

// ❌ WRONG — server-only variable in client code (will be undefined)
"use client";
const secret = process.env.NEXTAUTH_SECRET; // undefined!
```

### Env Helper Usage Conventions

**Always use `lib/env.ts` as the single source of truth** for environment
variables. This ensures runtime validation and type safety.

**Preferred — import from the validated env helper:**

```typescript
import { env } from "@/lib/env";

// ✅ Validated, typed, and guaranteed to exist
const apiUrl = env.NEXT_PUBLIC_API_URL;    // string
const timeout = env.API_TIMEOUT;           // number
const posEnabled = env.NEXT_PUBLIC_ENABLE_POS; // boolean
```

**Avoid — direct `process.env` access in application code:**

```typescript
// ❌ Avoid — no validation, always returns string | undefined
const timeout = process.env.API_TIMEOUT;
const posEnabled = process.env.NEXT_PUBLIC_ENABLE_POS === "true";
```

**When direct access is acceptable:**

- Inside `next.config.js` (runs before the app, cannot import TypeScript)
- Inside configuration files that run at build time
- In client components that only need `NEXT_PUBLIC_*` values where importing
  the env module would cause server-only code to leak into the bundle

**Adding a new variable:**

1. Add to `.env.local.example` with documentation
2. Add to `.env.example` (quick-reference)
3. Add to `types/env.d.ts` for TypeScript support
4. Add the Zod schema to `lib/env.ts` (server or client schema)
5. Add to `.env.local` with the actual value

### All Variables Reference

| Variable | Type | Default | Category |
| -------- | ---- | ------- | -------- |
| `NEXT_PUBLIC_API_URL` | `string` (URL) | `http://localhost:8000/api/v1` | API |
| `NEXT_PUBLIC_WS_URL` | `string` | `ws://localhost:8000/ws` | API |
| `API_BASE_URL` | `string` (URL) | `http://backend:8000/api/v1` | API (server) |
| `API_TIMEOUT` | `number` | `30000` | API (server) |
| `NEXT_PUBLIC_SITE_URL` | `string` (URL) | `http://localhost:3000` | Site |
| `NEXT_PUBLIC_SITE_NAME` | `string` | `LankaCommerce Cloud` | Site |
| `NEXT_PUBLIC_APP_NAME` | `string` | `LCC` | Site |
| `NEXT_PUBLIC_SITE_DESCRIPTION` | `string` | *(SaaS ERP description)* | Site |
| `NEXTAUTH_URL` | `string` (URL) | `http://localhost:3000` | Auth (server) |
| `NEXTAUTH_SECRET` | `string` | *(empty)* | Auth (server) |
| `NEXT_PUBLIC_AUTH_COOKIE_NAME` | `string` | `lcc_auth` | Auth |
| `NEXT_PUBLIC_TOKEN_EXPIRY_BUFFER` | `number` | `60` | Auth |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | `boolean` | `false` | Feature Flags |
| `NEXT_PUBLIC_ENABLE_AI_FEATURES` | `boolean` | `false` | Feature Flags |
| `NEXT_PUBLIC_ENABLE_WEBSTORE` | `boolean` | `true` | Feature Flags |
| `NEXT_PUBLIC_ENABLE_POS` | `boolean` | `true` | Feature Flags |
| `NEXT_PUBLIC_ENABLE_OFFLINE` | `boolean` | `true` | Feature Flags |
| `NEXT_PUBLIC_DEBUG` | `boolean` | `false` | Feature Flags |
| `NEXT_PUBLIC_GA_TRACKING_ID` | `string` | *(empty)* | Analytics |
| `NEXT_PUBLIC_SENTRY_DSN` | `string` | *(empty)* | Monitoring |
| `NEXT_PUBLIC_PAYHERE_MERCHANT_ID` | `string` | *(empty)* | Payments |
| `NEXT_PUBLIC_STRIPE_PUBLIC_KEY` | `string` | *(empty)* | Payments |
| `NEXT_PUBLIC_MAPS_API_KEY` | `string` | *(empty)* | Maps |
| `STRIPE_SECRET_KEY` | `string` | *(empty)* | Payments (server) |
| `STRIPE_WEBHOOK_SECRET` | `string` | *(empty)* | Payments (server) |
| `SENTRY_AUTH_TOKEN` | `string` | *(empty)* | Monitoring (server) |
| `NEXT_PUBLIC_DEFAULT_LOCALE` | `string` | `en-LK` | Localization |
| `NEXT_PUBLIC_DEFAULT_TIMEZONE` | `string` | `Asia/Colombo` | Localization |
| `NEXT_PUBLIC_DEFAULT_CURRENCY` | `string` | `LKR` | Localization |
| `NEXT_PUBLIC_CURRENCY_SYMBOL` | `string` | `Rs.` | Localization |
| `NEXT_PUBLIC_DEFAULT_TENANT` | `string` | `demo` | Tenant |
| `NEXT_PUBLIC_TENANT_PATTERN` | `string` | `{tenant}.lankacommerce.lk` | Tenant |
| `NEXT_PUBLIC_IMAGE_DOMAIN` | `string` | `cdn.lankacommerce.lk` | Image/CDN |
| `NEXT_PUBLIC_CLOUDINARY_CLOUD` | `string` | *(empty)* | Image/CDN |

---

## Sri Lanka Specifics

- **Currency:** LKR (₨) with 2 decimal places
- **Timezone:** Asia/Colombo
- **Phone format:** +94 XX XXX XXXX
- **Date format:** DD/MM/YYYY

---

## Build and Deployment

### Development Build

```bash
pnpm dev
```

Starts Next.js in **development mode** with hot reloading and Turbopack support. Changes are reflected instantly in the browser.

### Production Build

```bash
pnpm build
```

Compiles and optimizes the application for production. TypeScript is checked, pages are pre-rendered where possible, and assets are minified.

### Production Preview

```bash
pnpm start
```

Runs the production build locally so you can verify the output before deploying.

### Static Analysis Before Build

Always run these checks before building for production:

```bash
pnpm type-check   # TypeScript type checking (tsc --noEmit)
pnpm lint          # ESLint checks
```

Both commands must pass cleanly before a production build is created.

### Docker Build

The frontend Dockerfile uses a **multi-stage build** for minimal image size:

1. **deps** — installs production dependencies
2. **build** — compiles the Next.js application
3. **production** — copies only the build output and production `node_modules`

### Build Output

The `.next/` directory contains the compiled application (pages, chunks, static assets). This directory is git-ignored and regenerated on every build.

### Bundle Analysis

```bash
pnpm analyze
```

Opens an interactive treemap of the JavaScript bundle to identify large dependencies and optimization opportunities.

### Environment Note

> **⚠️ Important:** `NEXT_PUBLIC_*` environment variables are **inlined at build time**. If you change any `NEXT_PUBLIC_*` value, you must run `pnpm build` again for the change to take effect.

---

## App Router Conventions

The frontend uses the **Next.js App Router** (`app/` directory). Follow these conventions for consistency.

### File Conventions

| File            | Purpose                                                  |
| --------------- | -------------------------------------------------------- |
| `page.tsx`      | Route page — the UI rendered at that URL segment         |
| `layout.tsx`    | Shared layout — wraps child pages, persists across navigations |
| `loading.tsx`   | Loading state — shown via `<Suspense>` while the page loads  |
| `error.tsx`     | Error boundary — catches and displays runtime errors     |
| `not-found.tsx` | 404 page — shown when no route matches                   |
| `route.ts`      | API route handler — serverless endpoint (GET, POST, etc.) |

### Route Groups

Use parentheses `(group)` for **logical grouping** without affecting the URL:

```
app/
├── (auth)/           # Auth pages — URL is /login, not /auth/login
│   ├── login/
│   └── register/
├── (dashboard)/      # Dashboard pages — URL is /inventory, not /dashboard/inventory
│   ├── inventory/
│   └── sales/
└── (webstore)/       # Webstore pages
    ├── products/
    └── cart/
```

### Server vs Client Components

- **Server Components** are the default — they render on the server, can access databases and secrets directly, and ship zero JavaScript to the client.
- Add the `"use client"` directive **only** when the component needs:
  - Event handlers (`onClick`, `onChange`, etc.)
  - React state (`useState`, `useReducer`)
  - Effects (`useEffect`, `useLayoutEffect`)
  - Browser-only APIs (`window`, `localStorage`, `IntersectionObserver`)

### Data Fetching

- **Server Components** fetch data directly using `async/await` (e.g., call your API in the component body).
- **Client Components** fetch data via **React Query** hooks for caching, re-fetching, and optimistic updates.

### Layout Nesting

Layouts wrap their child segments and **persist across page navigations** (they don't unmount). Use layouts for:

- Navigation bars and sidebars
- Authentication wrappers
- Shared page structure (breadcrumbs, page titles)

### Metadata

Use the `metadata` export or `generateMetadata()` function for SEO:

```typescript
// Static metadata
export const metadata = {
  title: "Inventory | LankaCommerce Cloud",
  description: "Manage your inventory across all locations",
};

// Dynamic metadata
export async function generateMetadata({ params }) {
  const product = await getProduct(params.id);
  return { title: product.name };
}
```

---

## Styling Guidelines

### Tailwind CSS First

Use **Tailwind CSS utility classes** for all styling. Avoid writing custom CSS unless absolutely necessary (e.g., complex animations, third-party overrides).

```tsx
// ✅ Good — Tailwind utilities
<div className="flex items-center gap-4 rounded-lg bg-white p-6 shadow-sm">

// ❌ Avoid — custom CSS
<div className={styles.card}>
```

### Shadcn/UI Components

Use pre-built components from the **shadcn/ui** library as the design base. Customize appearance via the `className` prop:

```tsx
import { Button } from "@/components/ui/Button";

<Button variant="outline" className="w-full">
  Save Changes
</Button>
```

### Theming

- **Dark / light mode** is supported via `next-themes`.
- Use **CSS variables** for color tokens so themes switch seamlessly.
- Toggle theme with the `useTheme()` hook from `next-themes`.

### Responsive Design

Follow a **mobile-first** approach. Use Tailwind breakpoint prefixes to scale up:

| Prefix | Min-width | Target          |
| ------ | --------- | --------------- |
| *(none)* | 0px     | Mobile (default) |
| `sm:`  | 640px     | Small tablets    |
| `md:`  | 768px     | Tablets          |
| `lg:`  | 1024px    | Laptops          |
| `xl:`  | 1280px    | Desktops         |

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

### Class Merging

Use the `cn()` utility (from `@/lib/cn`) to safely merge conditional Tailwind classes without conflicts:

```tsx
import { cn } from "@/lib/cn";

<button className={cn("rounded px-4 py-2", isActive && "bg-primary text-white")}>
```

### Class Variance Authority (CVA)

Use **CVA** for components with multiple variants (size, color, state):

```tsx
import { cva } from "class-variance-authority";

const badge = cva("inline-flex items-center rounded-full font-medium", {
  variants: {
    variant: { default: "bg-gray-100", success: "bg-green-100 text-green-800" },
    size: { sm: "px-2 py-0.5 text-xs", md: "px-3 py-1 text-sm" },
  },
  defaultVariants: { variant: "default", size: "md" },
});
```

### Avoid

- **Inline styles** (`style={{ }}`) — hard to maintain, no responsive support
- **CSS Modules** (`*.module.css`) — not needed with Tailwind
- **styled-components** — adds runtime overhead, conflicts with Server Components
- **Global CSS** — only acceptable for CSS variable definitions in `styles/globals.css`

---

## Component Conventions

### File Naming

Use **PascalCase** for component files:

```
Button.tsx    SalesTable.tsx    InvoiceCard.tsx
```

### Directory Structure

If a component has related files (tests, types, sub-components), give it its own directory:

```
components/
├── ui/
│   └── Button.tsx             # Simple — single file
├── forms/
│   └── DatePicker/
│       ├── DatePicker.tsx     # Main component
│       ├── DatePicker.test.tsx
│       └── types.ts           # Local types
```

### Exports

Prefer **named exports** over default exports:

```typescript
// ✅ Named export
export function SalesTable({ data }: SalesTableProps) { ... }

// ❌ Avoid default export
export default function SalesTable({ data }: SalesTableProps) { ... }
```

### Props Interface

Define props as an `interface` named `ComponentNameProps` at the top of the file:

```typescript
interface SalesTableProps {
  data: Sale[];
  onRowClick?: (sale: Sale) => void;
  isLoading?: boolean;
}

export function SalesTable({ data, onRowClick, isLoading }: SalesTableProps) {
  // ...
}
```

### Component Categories

| Directory   | Purpose                                 | Examples                              |
| ----------- | --------------------------------------- | ------------------------------------- |
| `ui/`       | Base UI primitives from shadcn/ui       | Button, Input, Card, Dialog, Badge    |
| `layout/`   | Page structure components               | Header, Sidebar, Footer, PageWrapper  |
| `forms/`    | Form-related components                 | FormField, Select, DatePicker, FileUpload |
| `common/`   | Shared business components              | Logo, Avatar, Spinner, EmptyState     |

### When to Create Shared Components

If a component is used in **3 or more places**, extract it to `components/common/`. Before that, keep it co-located with the feature that owns it.

### Server vs Client Components

- **Default to Server Components** — they ship zero JS, can access server resources, and are faster.
- Only add `"use client"` when the component needs browser APIs, React state (`useState`), or effects (`useEffect`).
- Keep client boundaries as low as possible — wrap only the interactive part, not the entire page.

---

## Testing

### Test Framework

Tests use **Jest** with **React Testing Library** for component testing. This combination provides fast unit tests with a DOM-like environment that encourages testing components the way users interact with them.

### Commands

```bash
pnpm test              # Run all tests
pnpm test --watch      # Watch mode (re-runs on file changes)
pnpm test --coverage   # Generate coverage report
```

### Test Categories

| Category             | Scope                                     | Status   |
| -------------------- | ----------------------------------------- | -------- |
| **Unit tests**       | Components, hooks, utility functions      | ✅ Active |
| **Integration tests** | Page-level rendering, connected components | ✅ Active |
| **E2E tests**        | Full user flows across pages              | 🔜 Planned (Playwright) |

### Test Location

- **Global tests:** `__tests__/` directory at the project root
- **Co-located tests:** alongside the component they test (e.g., `components/ui/Button.test.tsx`)

### Naming Convention

```
ComponentName.test.tsx    # Component tests
useHookName.test.ts       # Hook tests
formatCurrency.test.ts    # Utility tests
```

All test files use the `*.test.ts` or `*.test.tsx` extension.

### Coverage Targets

| Area                    | Minimum Coverage |
| ----------------------- | ---------------- |
| Utilities and hooks     | 80%              |
| Components              | 70%              |

### Common Test Patterns

**Render testing** — verify the component renders correctly:

```tsx
import { render, screen } from "@testing-library/react";
import { Badge } from "@/components/ui/Badge";

test("renders badge with text", () => {
  render(<Badge>Active</Badge>);
  expect(screen.getByText("Active")).toBeInTheDocument();
});
```

**User interaction** — simulate clicks, typing, and other events:

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

test("calls onClick when button is pressed", async () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick}>Save</Button>);
  await userEvent.click(screen.getByRole("button", { name: /save/i }));
  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

**API mocking** — mock fetch/service calls for isolated tests:

```tsx
import { rest } from "msw";
import { server } from "@/tests/mocks/server";

beforeEach(() => {
  server.use(
    rest.get("/api/v1/products", (_req, res, ctx) =>
      res(ctx.json([{ id: 1, name: "Widget" }]))
    )
  );
});
```

---

## Further Reading

- [Main Project README](../README.md)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Zustand Documentation](https://zustand.docs.pmnd.rs)
- [Lucide Icons](https://lucide.dev/icons)
- [Shadcn/UI Documentation](https://ui.shadcn.com)
