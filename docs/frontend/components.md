# Frontend Components

> Component organization, UI patterns, and usage guide for LankaCommerce Cloud.

**Navigation:** [Docs Index](../index.md) · [Frontend README](../../frontend/README.md) · [Hooks](hooks.md) · [State Management](state.md)

---

## Overview

The frontend uses a structured component library organized by responsibility. Components are built with **React** (Server and Client Components), styled with **Tailwind CSS**, and based on the **shadcn/ui** component library for UI primitives.

---

## Component Directory

All components live under `frontend/components/` and are organized into four categories:

```
components/
├── ui/          # UI primitives (Button, Input, Card, Dialog, etc.)
├── layout/      # Page structure (Header, Sidebar, Footer, PageWrapper)
├── forms/       # Form components (FormField, Select, DatePicker)
├── common/      # Shared business components (Logo, Avatar, Spinner)
└── index.ts     # Barrel export for top-level imports
```

Each subdirectory has its own `index.ts` barrel file for clean imports.

---

## Component Categories

### ui/ — UI Primitives

Base UI building blocks from the shadcn/ui library. These are low-level, highly reusable components that form the design system foundation.

| Component | Purpose                                                                         |
| --------- | ------------------------------------------------------------------------------- |
| Button    | Action triggers with variants (primary, secondary, outline, ghost, destructive) |
| Input     | Text input fields with validation states                                        |
| Card      | Content container with header, body, and footer                                 |
| Dialog    | Modal dialog for confirmations and forms                                        |
| Select    | Dropdown selection with search support                                          |
| Table     | Data table with sorting and pagination                                          |
| Badge     | Status indicators and labels                                                    |
| Toast     | Notification messages (success, error, warning, info)                           |
| Tooltip   | Hover-triggered contextual information                                          |
| Tabs      | Tab-based content switching                                                     |

**Usage:** Import from `@/components/ui`:

```typescript
import { Button } from "@/components/ui";
```

**Customization:** shadcn/ui components are copied into the project (not installed as a package), so they can be customized directly. Use the `cn()` utility for conditional class merging.

---

### layout/ — Page Structure

Components that define the overall page layout and navigation structure.

| Component     | Purpose                                               |
| ------------- | ----------------------------------------------------- |
| Header        | Top navigation bar with tenant switcher and user menu |
| Sidebar       | Collapsible side navigation for ERP modules           |
| Footer        | Page footer with links and copyright                  |
| PageWrapper   | Consistent page container with breadcrumbs and title  |
| MobileSidebar | Responsive sidebar for mobile viewports               |

**Usage:** Layout components are typically used in Next.js `layout.tsx` files:

```typescript
import { Header, Sidebar } from "@/components/layout";
```

---

### forms/ — Form Components

Higher-level form components built on top of UI primitives with built-in validation.

| Component     | Purpose                                  |
| ------------- | ---------------------------------------- |
| FormField     | Label + input + error message wrapper    |
| FormSelect    | Dropdown with form integration           |
| DatePicker    | Date selection with calendar popup       |
| FileUpload    | File input with drag-and-drop support    |
| SearchInput   | Debounced search input with clear button |
| CurrencyInput | Formatted currency input for LKR values  |

**Usage:** Form components integrate with form libraries (e.g., React Hook Form):

```typescript
import { FormField, CurrencyInput } from "@/components/forms";
```

---

### common/ — Shared Business Components

Cross-cutting components used throughout multiple pages and features.

| Component     | Purpose                                                       |
| ------------- | ------------------------------------------------------------- |
| Logo          | Brand logo with responsive sizing                             |
| Avatar        | User avatar with fallback initials                            |
| Spinner       | Loading indicator                                             |
| EmptyState    | Placeholder for empty lists and search results                |
| ErrorBoundary | Error fallback UI                                             |
| ConfirmDialog | Reusable confirmation modal                                   |
| DataTable     | Feature-rich data table with filters, sorting, and pagination |
| StatusBadge   | Colored badge for order/task status display                   |

---

## Component Conventions

### File Naming

- PascalCase for component files: `Button.tsx`, `SalesTable.tsx`
- Index barrel files for directory exports: `index.ts`
- Co-located test files: `Button.test.tsx`

### Exports

- **Named exports** preferred over default exports
- Barrel files re-export from subdirectories

```typescript
// components/ui/index.ts
export { Button } from "./Button";
export { Input } from "./Input";
export { Card } from "./Card";
```

### Props

- Define props as an interface named `ComponentNameProps`
- Use `React.HTMLAttributes` for extending native element props
- Document complex props with JSDoc comments

```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "destructive";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}
```

### Server vs Client Components

- Default to **Server Components** (no directive needed)
- Add `"use client"` only when the component needs:
  - Event handlers (`onClick`, `onChange`)
  - React hooks (`useState`, `useEffect`, `useRef`)
  - Browser-only APIs (`window`, `document`, `localStorage`)
- Keep `"use client"` boundary as low as possible in the component tree

---

## Adding New Components

1. Determine the correct category (`ui/`, `layout/`, `forms/`, or `common/`)
2. Create the component file with PascalCase naming
3. Define the props interface
4. Implement the component
5. Export from the category's barrel file (`index.ts`)
6. Add tests alongside the component
7. If used in 3+ places, consider moving to `common/`

---

## Related Documentation

- [Frontend README](../../frontend/README.md) — Setup and development guide
- [Hooks Documentation](hooks.md) — Custom React hooks
- [State Management](state.md) — Zustand stores and state patterns
- [Docs Index](../index.md) — Full documentation hub
