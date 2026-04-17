import { useState, useEffect, useRef } from 'react';
import { toast } from 'sonner';
import { useStoreCartStore, type StoreCartItem } from '@/stores/store/cart';
import { validateCartStock, type ServerCartItem } from '@/services/storefront/cartService';

// ─── Types ──────────────────────────────────────────────────────────────────

interface StockIssue {
  itemId: string;
  productId: string;
  name: string;
  reason: 'out_of_stock' | 'low_stock' | 'price_changed';
}

interface UseStockValidationReturn {
  /** Whether validation is in progress */
  isValidating: boolean;
  /** Items with stock or availability problems */
  stockIssues: StockIssue[];
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function toServerItem(item: StoreCartItem): ServerCartItem {
  return {
    id: item.id,
    productId: item.productId,
    name: item.name,
    sku: item.sku,
    price: item.price,
    quantity: item.quantity,
    image: item.image,
    variant: item.variant,
  };
}

// ─── Hook ───────────────────────────────────────────────────────────────────

/**
 * Re-validates stock levels for all cart items on mount.
 * Surfaces issues via toasts and the returned `stockIssues` array.
 */
export function useStockValidation(): UseStockValidationReturn {
  const [isValidating, setIsValidating] = useState(false);
  const [stockIssues, setStockIssues] = useState<StockIssue[]>([]);
  const didRun = useRef(false);

  useEffect(() => {
    if (didRun.current) return;
    didRun.current = true;

    const items = useStoreCartStore.getState().items;
    if (items.length === 0) return;

    setIsValidating(true);

    validateCartStock(items.map(toServerItem))
      .then(({ invalidItems, priceChanges }) => {
        const issues: StockIssue[] = [];

        for (const inv of invalidItems) {
          issues.push({
            itemId: inv.id,
            productId: inv.productId,
            name: inv.name,
            reason: inv.reason,
          });
        }

        for (const pc of priceChanges) {
          const item = items.find((i) => i.id === pc.itemId);
          if (item) {
            issues.push({
              itemId: pc.itemId,
              productId: item.productId,
              name: item.name,
              reason: 'price_changed',
            });
          }
        }

        setStockIssues(issues);

        if (invalidItems.length > 0) {
          toast.warning(
            `${invalidItems.length} item${invalidItems.length > 1 ? 's' : ''} in your cart ${invalidItems.length > 1 ? 'have' : 'has'} stock issues`
          );
        }
        if (priceChanges.length > 0) {
          toast.info(
            `${priceChanges.length} item${priceChanges.length > 1 ? 's' : ''} ${priceChanges.length > 1 ? 'have' : 'has'} updated prices`
          );
        }
      })
      .catch(() => {
        // Validation failed silently — cart remains as-is
      })
      .finally(() => setIsValidating(false));
  }, []);

  return { isValidating, stockIssues };
}
