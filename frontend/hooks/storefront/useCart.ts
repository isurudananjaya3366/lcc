'use client';

import { useStoreCartStore } from '@/stores/store/cart';

/**
 * Wrapper hook around the Zustand cart store for storefront components.
 */
export function useCart() {
  const items = useStoreCartStore((s) => s.items);
  const isLoading = useStoreCartStore((s) => s.isLoading);
  const error = useStoreCartStore((s) => s.error);

  const addToCart = useStoreCartStore((s) => s.addToCart);
  const updateCartItem = useStoreCartStore((s) => s.updateCartItem);
  const removeFromCart = useStoreCartStore((s) => s.removeFromCart);
  const clearCart = useStoreCartStore((s) => s.clearCart);
  const applyCoupon = useStoreCartStore((s) => s.applyCoupon);
  const removeCoupon = useStoreCartStore((s) => s.removeCoupon);

  const itemCount = useStoreCartStore((s) => s.getItemCount());
  const subtotal = useStoreCartStore((s) => s.getSubtotal());
  const tax = useStoreCartStore((s) => s.getTax());
  const total = useStoreCartStore((s) => s.getTotal());
  const discountAmount = useStoreCartStore((s) => s.getDiscount());
  const discount = useStoreCartStore((s) => s.discount);

  const isInCart = useStoreCartStore((s) => s.isProductInCart);
  const getItemByVariantKey = useStoreCartStore((s) => s.getItemByVariantKey);

  return {
    items,
    isLoading,
    error,
    itemCount,
    subtotal,
    tax,
    total,
    discount,
    discountAmount,
    addItem: addToCart,
    removeItem: removeFromCart,
    updateQuantity: updateCartItem,
    clearCart,
    isInCart,
    applyCoupon,
    removeCoupon,
    getItemByVariantKey,
  };
}
