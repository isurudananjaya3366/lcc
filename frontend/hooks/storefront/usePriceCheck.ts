import { useState, useEffect, useRef } from 'react';
import { useStoreCartStore } from '@/stores/store/cart';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface PriceChange {
  itemId: string;
  productId: string;
  name: string;
  oldPrice: number;
  newPrice: number;
}

interface UsePriceCheckReturn {
  /** Items whose prices differ from when they were added */
  priceChanges: PriceChange[];
  /** Whether the price check is in progress */
  isChecking: boolean;
}

// ─── Config ─────────────────────────────────────────────────────────────────

const API_BASE = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`;

// ─── Hook ───────────────────────────────────────────────────────────────────

/**
 * Checks if prices have changed since items were added to cart.
 * Runs once on mount and exposes the list of changed items.
 */
export function usePriceCheck(): UsePriceCheckReturn {
  const [priceChanges, setPriceChanges] = useState<PriceChange[]>([]);
  const [isChecking, setIsChecking] = useState(false);
  const didRun = useRef(false);

  useEffect(() => {
    if (didRun.current) return;
    didRun.current = true;

    const items = useStoreCartStore.getState().items;
    if (items.length === 0) return;

    setIsChecking(true);

    const checks = items.map(async (item) => {
      try {
        const res = await fetch(`${API_BASE}/products/${item.productId}/`);
        if (!res.ok) return null;
        const product = await res.json();
        const currentPrice = product.price ?? item.price;
        if (currentPrice !== item.price) {
          return {
            itemId: item.id,
            productId: item.productId,
            name: item.name,
            oldPrice: item.price,
            newPrice: currentPrice,
          } satisfies PriceChange;
        }
      } catch {
        // API not available — skip
      }
      return null;
    });

    Promise.all(checks)
      .then((results) => {
        const changed = results.filter((r): r is PriceChange => r !== null);
        setPriceChanges(changed);
      })
      .catch(() => {
        // Silent failure
      })
      .finally(() => setIsChecking(false));
  }, []);

  return { priceChanges, isChecking };
}
