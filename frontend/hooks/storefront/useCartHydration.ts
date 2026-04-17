import { useState, useEffect } from 'react';

// ─── Types ──────────────────────────────────────────────────────────────────

interface UseCartHydrationReturn {
  /** Whether the Zustand cart store has finished hydrating from localStorage */
  isHydrated: boolean;
}

// ─── Hook ───────────────────────────────────────────────────────────────────

/**
 * Tracks SSR → client hydration of the Zustand cart store.
 *
 * Components that render cart data should gate on `isHydrated`
 * to avoid hydration mismatches between server and client.
 *
 * @example
 * ```tsx
 * const { isHydrated } = useCartHydration();
 * if (!isHydrated) return <CartSkeleton />;
 * ```
 */
export function useCartHydration(): UseCartHydrationReturn {
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    // After the first client-side render, localStorage data
    // has been read by the Zustand persist middleware.
    setIsHydrated(true);
  }, []);

  return { isHydrated };
}
