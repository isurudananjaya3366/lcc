/**
 * Zustand Store Utilities
 *
 * Provides the `createStore` factory that wraps Zustand's `create`
 * with pre-configured middlewares:
 *   DevTools (outermost) → Persist (middle) → Immer (innermost)
 *
 * Also exports helpers for SSR hydration, store resets, and
 * shallow selectors.
 */

'use client';

import { create, type StateCreator } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist, createJSONStorage } from 'zustand/middleware';
import { devtools } from 'zustand/middleware';
import { useEffect, useState } from 'react';
import { useShallow } from 'zustand/shallow';
import type { CreateStoreOptions } from './types';

// ── SSR Guard ──────────────────────────────────────────────────

/** `true` when running in the browser (not SSR) */
export const isClient = typeof window !== 'undefined';

// ── createStore Factory ────────────────────────────────────────

/**
 * Creates a Zustand store with DevTools, Persist, and Immer middlewares.
 *
 * Middleware stacking order (outer → inner):
 *   DevTools → Persist → Immer → Store initialiser
 *
 * @param name    Human-readable domain name, e.g. `"UI"`, `"Auth"`.
 * @param initializer  Standard Zustand state creator `(set, get, api) => T`.
 * @param options Override persist / devtools behaviour.
 *
 * @example
 * ```ts
 * export const useCountStore = createStore<CountStore>('Count', (set) => ({
 *   count: 0,
 *   increment: () => set((s) => { s.count += 1 }),
 *   reset: () => set({ count: 0 }),
 * }));
 * ```
 */
export function createStore<T extends object>(
  name: string,
  initializer: StateCreator<T, [['zustand/immer', never]], []>,
  options?: CreateStoreOptions<T>,
) {
  const enablePersist = options?.persist ?? false;
  const enableDevtools = options?.devtools !== false;

  const persistName = options?.persistConfig?.name ?? `lcc-${name.toLowerCase()}`;

  // Build the layered store creator
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let storeCreator: any;

  if (enablePersist) {
    storeCreator = devtools(
      persist(immer(initializer), {
        name: persistName,
        storage: createJSONStorage(() =>
          isClient ? localStorage : ({
            getItem: () => null,
            setItem: () => {},
            removeItem: () => {},
          } as unknown as Storage),
        ),
        partialize: options?.persistConfig?.partialize as
          | ((state: T) => unknown)
          | undefined,
        version: options?.persistConfig?.version ?? 1,
      }),
      {
        name: `LCC/${name}`,
        enabled: enableDevtools && process.env.NODE_ENV === 'development',
      },
    );
  } else {
    storeCreator = devtools(immer(initializer), {
      name: `LCC/${name}`,
      enabled: enableDevtools && process.env.NODE_ENV === 'development',
    });
  }

  return create<T>()(storeCreator);
}

// ── Persist Helper ─────────────────────────────────────────────

/**
 * Generates a persist configuration with SSR-safe storage.
 *
 * @param storeName  Short domain name, e.g. `"ui"`, `"auth"`.
 * @param partialize Optional filter for which fields to persist.
 */
export function getPersistConfig<T>(
  storeName: string,
  partialize?: (state: T) => Partial<T>,
) {
  return {
    name: `lcc-${storeName}`,
    storage: createJSONStorage(() =>
      isClient ? localStorage : ({
        getItem: () => null,
        setItem: () => {},
        removeItem: () => {},
      } as unknown as Storage),
    ),
    partialize,
    version: 1,
  };
}

// ── Store Reset Utilities ──────────────────────────────────────

/** Registry of all store reset functions — populated by individual stores */
const storeResetFns = new Set<() => void>();

/**
 * Register a store's reset function so `resetAllStores()` can invoke it.
 * Call this once per store file, at module scope.
 */
export function registerStoreReset(resetFn: () => void): void {
  storeResetFns.add(resetFn);
}

/**
 * Reset every registered store and clear their localStorage keys.
 * Typically called on logout.
 */
export function resetAllStores(): void {
  storeResetFns.forEach((reset) => reset());
}

// ── SSR Hydration Hook ─────────────────────────────────────────

/**
 * Returns `true` once the component has mounted on the client.
 * Use to avoid hydration mismatches when rendering persisted state.
 *
 * @example
 * ```tsx
 * const hydrated = useHydration();
 * if (!hydrated) return <Skeleton />;
 * return <ActualContent />;
 * ```
 */
export function useHydration(): boolean {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setHydrated(true);
  }, []);

  return hydrated;
}

// ── Selector Utilities ─────────────────────────────────────────

// Re-export useShallow for multi-property selectors.
// Usage:
//   const { a, b } = useStore(useShallow((s) => ({ a: s.a, b: s.b })));
export { useShallow };
