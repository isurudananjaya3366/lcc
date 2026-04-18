'use client';

import { useEffect, useRef } from 'react';
import { useStoreAuthStore } from '@/stores/store';
import { useStoreCartStore } from '@/stores/store';
import { mergeGuestCart, syncCartToServer } from '@/services/storefront/cartService';
import type { ServerCartItem } from '@/services/storefront/cartService';

export function useCartMergeOnLogin() {
  const isAuthenticated = useStoreAuthStore((s) => s.isAuthenticated);
  const wasAuthenticated = useRef(isAuthenticated);
  const cartItems = useStoreCartStore((s) => s.items);

  useEffect(() => {
    const prev = wasAuthenticated.current;
    wasAuthenticated.current = isAuthenticated;

    // Transition from unauthenticated to authenticated
    if (!prev && isAuthenticated && cartItems.length > 0) {
      const guestItems: ServerCartItem[] = cartItems.map((item) => ({
        id: item.id,
        productId: item.productId,
        name: item.name,
        sku: item.sku,
        price: item.price,
        quantity: item.quantity,
        image: item.image,
        variant: item.variant,
      }));

      // Merge and sync — fire and forget, non-blocking
      (async () => {
        try {
          // mergeGuestCart is a pure function that merges guest with server items.
          // Since there's no server cart at first login, the merge just returns guest items.
          const merged = mergeGuestCart(guestItems, []);

          // Sync merged cart to server
          await syncCartToServer(
            merged.map((item) => ({
              productId: item.productId,
              quantity: item.quantity,
              variant: item.variant,
            }))
          );
        } catch {
          // Non-critical — local cart is still intact
        }
      })();
    }
  }, [isAuthenticated, cartItems]);
}
