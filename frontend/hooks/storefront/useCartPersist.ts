import { useState, useEffect, useRef } from 'react';
import { useStoreCartStore } from '@/stores/store/cart';

// ─── Types ──────────────────────────────────────────────────────────────────

interface UseCartPersistReturn {
  /** Whether an expiry cleanup is in progress */
  isLoading: boolean;
  /** Timestamp of the last sync / cleanup, or null if none yet */
  lastSynced: Date | null;
}

// ─── Constants ──────────────────────────────────────────────────────────────

const THIRTY_DAYS_MS = 30 * 24 * 60 * 60 * 1000;
const TIMESTAMPS_KEY = 'lcc-store-cart-timestamps';

// ─── Helpers ────────────────────────────────────────────────────────────────

function getTimestamps(): Record<string, number> {
  if (typeof window === 'undefined') return {};
  try {
    return JSON.parse(localStorage.getItem(TIMESTAMPS_KEY) || '{}');
  } catch {
    return {};
  }
}

function setTimestamps(ts: Record<string, number>): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TIMESTAMPS_KEY, JSON.stringify(ts));
}

// ─── Hook ───────────────────────────────────────────────────────────────────

/**
 * Manages cart persistence extras on top of Zustand's built-in persist:
 * - Cleans expired items (> 30 days old) on mount
 * - Listens for cross-tab `storage` events to keep cart in sync
 */
export function useCartPersist(): UseCartPersistReturn {
  const [isLoading, setIsLoading] = useState(true);
  const [lastSynced, setLastSynced] = useState<Date | null>(null);
  const didRun = useRef(false);

  // Expiry cleanup on mount
  useEffect(() => {
    if (didRun.current) return;
    didRun.current = true;

    const items = useStoreCartStore.getState().items;
    const timestamps = getTimestamps();
    const now = Date.now();

    const expiredIds = items
      .filter((item) => {
        const addedAt = timestamps[item.id];
        return addedAt && now - addedAt > THIRTY_DAYS_MS;
      })
      .map((item) => item.id);

    if (expiredIds.length > 0) {
      const removeFromCart = useStoreCartStore.getState().removeFromCart;
      expiredIds.forEach((id) => {
        removeFromCart(id);
        delete timestamps[id];
      });
      setTimestamps(timestamps);
    }

    setLastSynced(new Date());
    setIsLoading(false);
  }, []);

  // Cross-tab sync via storage event
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handler = (e: StorageEvent) => {
      if (e.key === 'lcc-store-cart') {
        // Force a re-read from localStorage by triggering a no-op state update
        window.location.reload();
      }
    };

    window.addEventListener('storage', handler);
    return () => window.removeEventListener('storage', handler);
  }, []);

  return { isLoading, lastSynced };
}
