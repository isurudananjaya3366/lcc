# Frontend Hooks

> Custom React hooks, data-fetching patterns, and hook conventions for LankaCommerce Cloud.

**Navigation:** [Docs Index](../index.md) · [Frontend README](../../frontend/README.md) · [Components](components.md) · [State Management](state.md)

---

## Overview

Custom hooks encapsulate reusable logic across the frontend application. They live in the `frontend/hooks/` directory and follow React's rules of hooks. Hooks handle common patterns such as data fetching, form management, local storage, and responsive behavior.

---

## Hook Directory

```
hooks/
├── index.ts          # Barrel export for all hooks
├── useAuth.ts        # Authentication state and actions
├── useApi.ts         # API fetch wrapper with error handling
├── useDebounce.ts    # Debounced value for search inputs
├── useLocalStorage.ts # Persistent local storage state
├── useMediaQuery.ts  # Responsive breakpoint detection
├── usePagination.ts  # Pagination logic for data tables
├── useToast.ts       # Toast notification trigger
└── ...               # Additional hooks as needed
```

> Hooks are added as needed during feature implementation.

---

## Hook Categories

### Authentication Hooks

| Hook             | Purpose                                                              |
| ---------------- | -------------------------------------------------------------------- |
| `useAuth`        | Access current user, login/logout actions, and authentication status |
| `usePermissions` | Check user permissions and role-based access                         |
| `useTenant`      | Access current tenant context and tenant-switching logic             |

### Data Fetching Hooks

| Hook             | Purpose                                                    |
| ---------------- | ---------------------------------------------------------- |
| `useApi`         | Generic fetch wrapper with loading, error, and data states |
| `useProducts`    | Fetch and cache product list with filtering                |
| `useInventory`   | Fetch stock levels and warehouse data                      |
| `useSalesOrders` | Fetch sales order list with pagination                     |
| `useCustomers`   | Fetch customer list and details                            |

Data fetching hooks will use **React Query** (TanStack Query) for:

- Automatic caching and background re-fetching
- Optimistic updates for mutations
- Infinite scroll and pagination support
- Request deduplication

### UI Utility Hooks

| Hook              | Purpose                                                             |
| ----------------- | ------------------------------------------------------------------- |
| `useDebounce`     | Debounce a value for delayed search/filter triggers                 |
| `useMediaQuery`   | Detect responsive breakpoints (`isMobile`, `isTablet`, `isDesktop`) |
| `useLocalStorage` | Persist state to localStorage with SSR safety                       |
| `useClickOutside` | Detect clicks outside a ref element (for dropdowns, modals)         |
| `useKeyboard`     | Listen for keyboard shortcuts                                       |

### Form Hooks

| Hook                | Purpose                                       |
| ------------------- | --------------------------------------------- |
| `useFormValidation` | Form validation logic with error messages     |
| `useCurrencyFormat` | Format and parse LKR currency values          |
| `useFileUpload`     | Handle file selection, validation, and upload |

---

## Hook Conventions

### Naming

- All hooks start with `use` prefix: `useAuth`, `useDebounce`, `useProducts`
- One hook per file, file named same as the hook: `useAuth.ts`
- Exported as named exports from `hooks/index.ts`

### Structure

A standard hook follows this pattern:

```typescript
// hooks/useDebounce.ts
import { useState, useEffect } from "react";

/**
 * Debounce a value by a specified delay.
 * Useful for search inputs to avoid excessive API calls.
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

### Guidelines

- **Keep hooks focused** — Each hook should do one thing well
- **Return consistent shapes** — Use `{ data, error, isLoading }` for async hooks
- **Handle cleanup** — Always return cleanup functions from `useEffect`
- **Type everything** — Use generics where the hook accepts varying types
- **Test independently** — Hooks should be testable with `@testing-library/react-hooks`
- **Document parameters** — Use JSDoc comments for hook signatures

### Client-Only Constraint

All custom hooks require `"use client"` in the consuming component because hooks use React state and effects. Hooks cannot be used directly in Server Components.

---

## Data Fetching Patterns

### Server Components (Preferred for Initial Data)

Server Components fetch data directly without hooks:

```typescript
// app/products/page.tsx (Server Component — no "use client")
async function ProductsPage() {
  const products = await fetch(`${process.env.API_BASE_URL}/products`);
  return <ProductList products={products} />;
}
```

### Client Components (For Interactive Data)

Client Components use hooks for interactive, real-time data:

```typescript
// components/ProductSearch.tsx
"use client";
import { useProducts } from "@/hooks";
import { useDebounce } from "@/hooks";

export function ProductSearch() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 300);
  const { data, isLoading } = useProducts({ search: debouncedQuery });

  return (
    // ... search UI
  );
}
```

### When to Use Which

| Pattern                | Use When                                             |
| ---------------------- | ---------------------------------------------------- |
| Server Component fetch | Initial page load, SEO-critical content, static data |
| React Query hook       | Interactive filtering, real-time updates, pagination |
| SWR / fetch in effect  | Simple client-side fetches (rare cases)              |

---

## Adding New Hooks

1. Create the hook file in `hooks/` with `use` prefix: `useNewHook.ts`
2. Define the return type interface
3. Implement the hook logic
4. Export from `hooks/index.ts`
5. Add JSDoc documentation
6. Write tests in `__tests__/hooks/useNewHook.test.ts`

---

## Related Documentation

- [Frontend README](../../frontend/README.md) — Setup and development guide
- [Components Documentation](components.md) — UI components and patterns
- [State Management](state.md) — Zustand stores and state patterns
- [Docs Index](../index.md) — Full documentation hub
