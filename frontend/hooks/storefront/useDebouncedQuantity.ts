'use client';

import { useState, useEffect, useRef } from 'react';
import { useDebounce } from '@/hooks/useDebounce';
import { useStoreCartStore } from '@/stores/store/cart';
import { toast } from 'sonner';

interface UseDebouncedQuantityReturn {
  quantity: number;
  setQuantity: (qty: number) => void;
  isPending: boolean;
}

export function useDebouncedQuantity(
  itemId: string,
  initialQty: number
): UseDebouncedQuantityReturn {
  const [quantity, setQuantity] = useState(initialQty);
  const [isPending, setIsPending] = useState(false);
  const debouncedQuantity = useDebounce(quantity, 500);
  const isFirstRender = useRef(true);
  const updateCartItem = useStoreCartStore((s) => s.updateCartItem);

  // Sync when initialQty changes externally
  useEffect(() => {
    setQuantity(initialQty);
  }, [initialQty]);

  // Apply debounced update to the cart store
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    if (debouncedQuantity !== initialQty) {
      const success = updateCartItem(itemId, debouncedQuantity);
      if (success) {
        toast('Quantity updated');
      }
    }
    setIsPending(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuantity]);

  const handleSetQuantity = (qty: number) => {
    setQuantity(qty);
    setIsPending(true);
  };

  return { quantity, setQuantity: handleSetQuantity, isPending };
}
