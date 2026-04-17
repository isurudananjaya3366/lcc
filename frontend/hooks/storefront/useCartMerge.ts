import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import { useStoreCartStore, type StoreCartItem } from '@/stores/store/cart';
import { mergeGuestCart, fetchServerCart, type ServerCartItem } from '@/services/storefront/cartService';

// ─── Types ──────────────────────────────────────────────────────────────────

interface UseCartMergeReturn {
  /** Merge the current guest cart with the server cart */
  mergeCart: () => Promise<void>;
  /** Whether a merge operation is in progress */
  isMerging: boolean;
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
 * Merges the local (guest) cart with the server cart on login.
 *
 * After merging, the Zustand store is replaced with the merged result
 * and the user is notified about any items that were combined.
 */
export function useCartMerge(): UseCartMergeReturn {
  const [isMerging, setIsMerging] = useState(false);

  const mergeCart = useCallback(async () => {
    setIsMerging(true);
    try {
      const guestItems = useStoreCartStore.getState().items.map(toServerItem);
      const serverItems = await fetchServerCart();

      const merged = mergeGuestCart(guestItems, serverItems);
      const addedCount = merged.length - guestItems.length;

      // Replace the store with merged items
      const { clearCart, addToCart } = useStoreCartStore.getState();
      clearCart();
      for (const item of merged) {
        addToCart(
          {
            productId: item.productId,
            name: item.name,
            sku: item.sku,
            price: item.price,
            image: item.image,
            variant: item.variant ?? undefined,
          },
          item.quantity
        );
      }

      if (addedCount > 0) {
        toast.success(`Merged ${addedCount} item${addedCount > 1 ? 's' : ''} from your account cart`);
      } else if (merged.length > 0) {
        toast.info('Cart synced with your account');
      }
    } catch {
      toast.error('Failed to merge cart with your account');
    } finally {
      setIsMerging(false);
    }
  }, []);

  return { mergeCart, isMerging };
}
