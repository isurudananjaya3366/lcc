'use client';

import { createStore } from '../utils';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface StoreCartItem {
  id: string;
  productId: string;
  name: string;
  sku: string;
  price: number;
  quantity: number;
  image: string;
  variant: Record<string, string> | null;
  lineSubtotal: number;
  lineDiscount: number;
  lineTax: number;
}

interface CartState {
  items: StoreCartItem[];
  isLoading: boolean;
  error: string | null;
  discount: { code: string; type: 'percentage' | 'fixed'; value: number } | null;

  // Computed selectors
  getItemCount: () => number;
  getSubtotal: () => number;
  getTax: () => number;
  getTotal: () => number;
  getDiscount: () => number;
  getItemById: (id: string) => StoreCartItem | undefined;
  getItemByProductId: (productId: string) => StoreCartItem | undefined;
  getItemByVariantKey: (key: string) => StoreCartItem | undefined;
  isProductInCart: (productId: string) => boolean;
  getCartSummary: () => {
    itemCount: number;
    subtotal: number;
    discount: number;
    tax: number;
    total: number;
    formattedTotal: string;
  };

  // Actions
  addToCart: (
    product: {
      productId: string;
      name: string;
      sku: string;
      price: number;
      image: string;
      variant?: Record<string, string>;
    },
    quantity?: number
  ) => boolean;
  updateCartItem: (cartItemId: string, newQuantity: number) => boolean;
  removeFromCart: (cartItemId: string) => boolean;
  clearCart: () => void;
  clearCartAfterCheckout: () => void;
  applyCoupon: (code: string, type: 'percentage' | 'fixed', value: number) => void;
  removeCoupon: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// ─── Tax Calculation ────────────────────────────────────────────────────────

const TAX_RATE = 0.08; // 8% VAT Sri Lanka

function calculateTax(subtotal: number): number {
  return Math.round(subtotal * TAX_RATE * 100) / 100;
}

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

function generateCartItemId(): string {
  return `cart-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Generate a unique variant key for a product + variant combination.
 * e.g. `prod-123-color:Red-size:M`
 */
export function generateVariantKey(
  productId: string,
  variant: Record<string, string> | null
): string {
  if (!variant || Object.keys(variant).length === 0) {
    return `prod-${productId}`;
  }
  const sortedParts = Object.entries(variant)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${k.toLowerCase()}:${v}`)
    .join('-');
  return `prod-${productId}-${sortedParts}`;
}

// ─── Store ──────────────────────────────────────────────────────────────────

export const useStoreCartStore = createStore<CartState>(
  'StoreCart',
  (set, get) => ({
    items: [],
    isLoading: false,
    error: null,
    discount: null,

    // Computed
    getItemCount: () => get().items.reduce((sum, item) => sum + item.quantity, 0),

    getSubtotal: () => get().items.reduce((sum, item) => sum + item.lineSubtotal, 0),

    getTax: () => calculateTax(get().getSubtotal()),

    getTotal: () => {
      const subtotal = get().getSubtotal();
      const discountAmount = get().getDiscount();
      const taxableAmount = subtotal - discountAmount;
      return Math.max(0, taxableAmount + calculateTax(taxableAmount));
    },

    getDiscount: () => {
      const { discount } = get();
      if (!discount) return 0;
      const subtotal = get().getSubtotal();
      if (discount.type === 'percentage') {
        return Math.round(subtotal * (discount.value / 100) * 100) / 100;
      }
      return Math.min(discount.value, subtotal);
    },

    getItemById: (id: string) => get().items.find((item) => item.id === id),

    getItemByProductId: (productId: string) =>
      get().items.find((item) => item.productId === productId),

    getItemByVariantKey: (key: string) =>
      get().items.find(
        (item) => generateVariantKey(item.productId, item.variant) === key
      ),

    isProductInCart: (productId: string) =>
      get().items.some((item) => item.productId === productId),

    getCartSummary: () => {
      const subtotal = get().getSubtotal();
      const discountAmount = get().getDiscount();
      const taxableAmount = subtotal - discountAmount;
      const tax = calculateTax(taxableAmount);
      const total = Math.max(0, taxableAmount + tax);
      return {
        itemCount: get().getItemCount(),
        subtotal,
        discount: discountAmount,
        tax,
        total,
        formattedTotal: formatLKR(total),
      };
    },

    // Actions
    addToCart: (product, quantity = 1) => {
      if (quantity <= 0 || product.price < 0) return false;

      const existing = get().getItemByProductId(product.productId);

      if (existing) {
        const newQuantity = existing.quantity + quantity;
        set((state) => {
          const item = state.items.find((i) => i.id === existing.id);
          if (item) {
            item.quantity = newQuantity;
            item.lineSubtotal = item.price * newQuantity;
          }
        });
      } else {
        const newItem: StoreCartItem = {
          id: generateCartItemId(),
          productId: product.productId,
          name: product.name,
          sku: product.sku,
          price: product.price,
          quantity,
          image: product.image,
          variant: product.variant ?? null,
          lineSubtotal: product.price * quantity,
          lineDiscount: 0,
          lineTax: 0,
        };
        set((state) => {
          state.items.push(newItem);
        });
      }

      return true;
    },

    updateCartItem: (cartItemId: string, newQuantity: number) => {
      if (newQuantity < 0) return false;

      if (newQuantity === 0) {
        return get().removeFromCart(cartItemId);
      }

      const item = get().getItemById(cartItemId);
      if (!item) return false;

      set((state) => {
        const target = state.items.find((i) => i.id === cartItemId);
        if (target) {
          target.quantity = newQuantity;
          target.lineSubtotal = target.price * newQuantity;
        }
      });

      return true;
    },

    removeFromCart: (cartItemId: string) => {
      const item = get().getItemById(cartItemId);
      if (!item) return false;

      set((state) => {
        state.items = state.items.filter((i) => i.id !== cartItemId);
      });

      return true;
    },

    clearCart: () => {
      set((state) => {
        state.items = [];
        state.discount = null;
        state.error = null;
      });
    },

    clearCartAfterCheckout: () => {
      set((state) => {
        state.items = [];
        state.discount = null;
        state.error = null;
      });
    },

    applyCoupon: (code: string, type: 'percentage' | 'fixed', value: number) => {
      set((state) => {
        state.discount = { code, type, value };
      });
    },

    removeCoupon: () => {
      set((state) => {
        state.discount = null;
      });
    },

    setLoading: (loading: boolean) => set({ isLoading: loading }),
    setError: (error: string | null) => set({ error }),
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-store-cart',
      partialize: (state: CartState) => ({
        items: state.items,
        discount: state.discount,
      }),
    },
  }
);
