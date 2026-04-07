# Frontend State Management

> State management patterns, Zustand stores, and state boundaries for LankaCommerce Cloud.

**Navigation:** [Docs Index](../index.md) · [Frontend README](../../frontend/README.md) · [Components](components.md) · [Hooks](hooks.md)

---

## Overview

LankaCommerce Cloud uses a **layered state management** approach that separates server state from client state. Server state (API data) is managed by **React Query**, while client state (UI state, user preferences) is managed by **Zustand** stores. This separation keeps the codebase clean and avoids common pitfalls of over-centralized state management.

---

## State Categories

| Category         | Tool                         | Examples                                          |
| ---------------- | ---------------------------- | ------------------------------------------------- |
| **Server State** | React Query (TanStack Query) | Products, orders, customers, inventory data       |
| **Client State** | Zustand                      | UI toggles, sidebar collapsed, active tab, theme  |
| **Form State**   | React Hook Form              | Form field values, validation errors, dirty state |
| **URL State**    | Next.js Router               | Current route, query parameters, search filters   |
| **Auth State**   | Zustand + JWT                | Current user, tokens, permissions, tenant context |

### When to Use Which

| Situation                                             | Solution                 |
| ----------------------------------------------------- | ------------------------ |
| Data from the API that is read-only or rarely changed | React Query              |
| Data that the user edits and submits                  | React Hook Form          |
| UI state shared across multiple components            | Zustand store            |
| State that should persist across page navigations     | Zustand with persistence |
| State encoded in the URL (filters, pagination)        | Next.js `searchParams`   |
| State that only one component needs                   | Local `useState`         |

---

## Zustand Stores

All Zustand stores live in `frontend/stores/` and follow a consistent pattern.

### Store Directory

```
stores/
├── index.ts             # Barrel export for all stores
├── useAuthStore.ts      # Authentication and user session
├── useUIStore.ts        # UI preferences (sidebar, theme, modals)
├── useCartStore.ts      # Shopping cart (webstore)
├── usePOSStore.ts       # POS terminal state
├── useNotificationStore.ts  # In-app notifications
└── ...                  # Additional stores as needed
```

> Stores are added as needed during feature implementation.

### Store Pattern

Each Zustand store follows this structure:

```typescript
// stores/useUIStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface UIState {
  sidebarCollapsed: boolean;
  theme: "light" | "dark" | "system";
  toggleSidebar: () => void;
  setTheme: (theme: "light" | "dark" | "system") => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      theme: "system",
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setTheme: (theme) => set({ theme }),
    }),
    { name: "lcc-ui-preferences" },
  ),
);
```

---

## Planned Stores

### useAuthStore — Authentication

Manages the current user session, JWT tokens, and tenant context.

| Field             | Type             | Purpose                       |
| ----------------- | ---------------- | ----------------------------- |
| `user`            | `User \| null`   | Current authenticated user    |
| `accessToken`     | `string \| null` | JWT access token              |
| `refreshToken`    | `string \| null` | JWT refresh token             |
| `tenant`          | `Tenant \| null` | Active tenant context         |
| `isAuthenticated` | `boolean`        | Whether the user is logged in |
| `login()`         | action           | Authenticate and store tokens |
| `logout()`        | action           | Clear session and redirect    |
| `switchTenant()`  | action           | Change active tenant          |

### useUIStore — UI Preferences

Manages global UI state that persists across sessions.

| Field              | Type                            | Purpose                         |
| ------------------ | ------------------------------- | ------------------------------- |
| `sidebarCollapsed` | `boolean`                       | Sidebar open/collapsed state    |
| `theme`            | `"light" \| "dark" \| "system"` | Color theme preference          |
| `locale`           | `string`                        | Selected language (en, si, ta)  |
| `activeModal`      | `string \| null`                | Currently open modal identifier |

### useCartStore — Shopping Cart

Manages the webstore shopping cart with persistence.

| Field              | Type         | Purpose                        |
| ------------------ | ------------ | ------------------------------ |
| `items`            | `CartItem[]` | Items in the cart              |
| `total`            | `number`     | Calculated total in LKR        |
| `addItem()`        | action       | Add a product to the cart      |
| `removeItem()`     | action       | Remove a product from the cart |
| `updateQuantity()` | action       | Change item quantity           |
| `clearCart()`      | action       | Empty the cart                 |

### usePOSStore — Point of Sale

Manages the POS terminal state for in-store transactions.

| Field                   | Type                  | Purpose                    |
| ----------------------- | --------------------- | -------------------------- |
| `currentTransaction`    | `Transaction \| null` | Active sale in progress    |
| `scannedItems`          | `ScanItem[]`          | Barcode-scanned items      |
| `paymentMethod`         | `string`              | Selected payment method    |
| `addScannedItem()`      | action                | Add item by barcode        |
| `completeTransaction()` | action                | Finalize and print receipt |
| `voidTransaction()`     | action                | Cancel the current sale    |

### useNotificationStore — Notifications

Manages in-app notification state for real-time updates.

| Field               | Type             | Purpose                     |
| ------------------- | ---------------- | --------------------------- |
| `notifications`     | `Notification[]` | Unread notification list    |
| `unreadCount`       | `number`         | Badge count                 |
| `addNotification()` | action           | Push a new notification     |
| `markRead()`        | action           | Mark a notification as read |
| `clearAll()`        | action           | Dismiss all notifications   |

---

## State Boundaries

### Rules

1. **Keep server state in React Query** — Never duplicate API data in Zustand stores
2. **Keep form state in React Hook Form** — Avoid syncing form fields to global stores
3. **Minimize global state** — Use local `useState` for component-specific state
4. **Persist sparingly** — Only persist state that should survive page refreshes (preferences, cart, auth tokens)
5. **No business logic in stores** — Stores hold state and simple actions; complex logic belongs in hooks or services

### Data Flow

```
API (Backend) → React Query (cache) → Server Components / Client Components
                                          ↓
                                     Zustand (UI state, auth, cart)
                                          ↓
                                     Components (render)
                                          ↓
                                     User Actions → API mutations → React Query invalidation
```

---

## Zustand Middleware

| Middleware | Purpose                                     | Used In                           |
| ---------- | ------------------------------------------- | --------------------------------- |
| `persist`  | Save state to localStorage across sessions  | UI preferences, cart, auth tokens |
| `devtools` | Redux DevTools integration for debugging    | All stores in development         |
| `immer`    | Immutable state updates with mutable syntax | Complex nested state _(optional)_ |

---

## Store Conventions

### Naming

- Store hooks start with `use` and end with `Store`: `useAuthStore`, `useUIStore`
- One store per file, file named same as the store
- Exported as named exports from `stores/index.ts`

### Access Pattern

```typescript
// Access a single field (re-renders only when this field changes)
const theme = useUIStore((state) => state.theme);

// Access an action (never causes re-renders)
const toggleSidebar = useUIStore((state) => state.toggleSidebar);

// Avoid: selecting the entire store (causes unnecessary re-renders)
// const store = useUIStore(); ← Don't do this
```

### Testing

- Test stores independently using the store's `getState()` and `setState()` methods
- Mock stores in component tests with Zustand's testing utilities
- Reset store state between tests to avoid cross-test contamination

---

## Related Documentation

- [Frontend README](../../frontend/README.md) — Setup and development guide
- [Components Documentation](components.md) — UI components and patterns
- [Hooks Documentation](hooks.md) — Custom hooks and data fetching
- [Docs Index](../index.md) — Full documentation hub
