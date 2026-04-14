# Zustand Stores

## Creating a Store

Use `createStore` from `@/stores/utils` which applies the standard
middleware chain: **devtools → persist → immer**.

```ts
import { createStore } from '@/stores/utils';

interface CounterState {
  count: number;
  increment: () => void;
  reset: () => void;
}

export const useCounterStore = createStore<CounterState>(
  'Counter',
  (set) => ({
    count: 0,
    increment: () => set((s) => { s.count += 1; }),
    reset: () => set({ count: 0 }),
  }),
  { persist: true },
);
```

## Conventions

- **Naming:** `use<Domain>Store` (e.g. `useUIStore`, `useAuthStore`)
- **DevTools name:** `LCC/<Domain>` — set automatically from the first arg
- **Persistence:** opt-in via `persist: true` in the options object.
  Use `partialize` to exclude transient fields.
- **Reset:** every store must expose a `reset()` action and register it
  with `registerStoreReset` so `resetAllStores()` works.

## Available Stores

| Store | Key | Persisted Fields |
|-------|-----|------------------|
| `useUIStore` | `lcc-ui` | `isCollapsed`, `theme` |
| `useAuthStore` | `lcc-auth` | `user`, `tenant`, `permissions`, `isAuthenticated` |

## SSR / Hydration

Zustand persist uses `localStorage` which is unavailable during SSR.
Use `useHydration()` to guard client-only rendering:

```tsx
const hydrated = useHydration();
if (!hydrated) return <Skeleton />;
```
