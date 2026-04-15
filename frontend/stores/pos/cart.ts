'use client';

import { createStore } from '@/stores/utils';
import type { POSCartItem, POSDiscount, POSCustomer } from '@/components/modules/pos/types';

// ── Helpers ────────────────────────────────────────────────────

function calculateLineTotal(item: POSCartItem): POSCartItem {
  const subtotal = item.quantity * item.unitPrice;
  let discountAmount = 0;
  if (item.discount) {
    discountAmount =
      item.discount.type === 'percentage'
        ? subtotal * (item.discount.value / 100)
        : Math.min(item.discount.value, subtotal);
  }
  const afterDiscount = subtotal - discountAmount;
  const taxAmount = item.isTaxable ? afterDiscount * (item.taxRate / 100) : 0;
  return { ...item, discountAmount, taxAmount, lineTotal: afterDiscount + taxAmount };
}

// ── Store Definition ───────────────────────────────────────────

interface CartState {
  items: POSCartItem[];
  discount: POSDiscount | null;
  customer: POSCustomer | null;
  lastUpdate: string;

  // Computed helpers
  getItems: () => POSCartItem[];
  getItemCount: () => number;
  getSubtotal: () => number;
  getDiscountTotal: () => number;
  getTaxTotal: () => number;
  getGrandTotal: () => number;
  hasItems: () => boolean;

  // Actions
  addItem: (
    item: Omit<POSCartItem, 'id' | 'addedAt' | 'lineTotal' | 'discountAmount' | 'taxAmount'>
  ) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  removeItem: (itemId: string) => void;
  clearCart: () => void;
  applyItemDiscount: (itemId: string, discount: POSDiscount) => void;
  removeItemDiscount: (itemId: string) => void;
  applyCartDiscount: (discount: POSDiscount) => void;
  removeCartDiscount: () => void;
  setCustomer: (customer: POSCustomer | null) => void;
}

export const useCartStore = createStore<CartState>(
  'POS-Cart',
  (set, get) => ({
    items: [],
    discount: null,
    customer: null,
    lastUpdate: new Date().toISOString(),

    // ── Computed ──────────────────────────────────────────────

    getItems: () => get().items,

    getItemCount: () => get().items.reduce((sum, i) => sum + i.quantity, 0),

    getSubtotal: () => get().items.reduce((sum, i) => sum + i.quantity * i.unitPrice, 0),

    getDiscountTotal: () => {
      const itemDiscounts = get().items.reduce((sum, i) => sum + i.discountAmount, 0);
      const cartDiscount = get().discount;
      if (!cartDiscount) return itemDiscounts;
      const subtotal = get().getSubtotal() - itemDiscounts;
      const cartDiscountAmount =
        cartDiscount.type === 'percentage'
          ? subtotal * (cartDiscount.value / 100)
          : Math.min(cartDiscount.value, subtotal);
      return itemDiscounts + cartDiscountAmount;
    },

    getTaxTotal: () => get().items.reduce((sum, i) => sum + i.taxAmount, 0),

    getGrandTotal: () => {
      const subtotal = get().getSubtotal();
      const discount = get().getDiscountTotal();
      const tax = get().getTaxTotal();
      return subtotal - discount + tax;
    },

    hasItems: () => get().items.length > 0,

    // ── Actions ──────────────────────────────────────────────

    addItem: (itemData) => {
      set((state) => {
        const existingIdx = state.items.findIndex(
          (i) => i.productId === itemData.productId && i.variantId === itemData.variantId
        );

        if (existingIdx >= 0) {
          const existing = state.items[existingIdx]!;
          state.items[existingIdx] = calculateLineTotal({
            ...(existing as POSCartItem),
            quantity: existing.quantity + (itemData.quantity || 1),
          });
        } else {
          const newItem: POSCartItem = calculateLineTotal({
            ...(itemData as POSCartItem),
            id: crypto.randomUUID(),
            addedAt: new Date().toISOString(),
            discountAmount: 0,
            taxAmount: 0,
            lineTotal: 0,
          });
          state.items.push(newItem);
        }
        state.lastUpdate = new Date().toISOString();
      });
    },

    updateQuantity: (itemId, quantity) => {
      set((state) => {
        const idx = state.items.findIndex((i) => i.id === itemId);
        if (idx >= 0) {
          if (quantity <= 0) {
            state.items.splice(idx, 1);
          } else {
            state.items[idx] = calculateLineTotal({
              ...(state.items[idx] as POSCartItem),
              quantity,
            });
          }
          state.lastUpdate = new Date().toISOString();
        }
      });
    },

    removeItem: (itemId) => {
      set((state) => {
        state.items = state.items.filter((i) => i.id !== itemId);
        state.lastUpdate = new Date().toISOString();
      });
    },

    clearCart: () => {
      set((state) => {
        state.items = [];
        state.discount = null;
        state.customer = null;
        state.lastUpdate = new Date().toISOString();
      });
    },

    applyItemDiscount: (itemId, discount) => {
      set((state) => {
        const idx = state.items.findIndex((i) => i.id === itemId);
        if (idx >= 0) {
          state.items[idx] = calculateLineTotal({ ...(state.items[idx] as POSCartItem), discount });
          state.lastUpdate = new Date().toISOString();
        }
      });
    },

    removeItemDiscount: (itemId) => {
      set((state) => {
        const idx = state.items.findIndex((i) => i.id === itemId);
        if (idx >= 0) {
          state.items[idx] = calculateLineTotal({
            ...(state.items[idx] as POSCartItem),
            discount: undefined,
          });
          state.lastUpdate = new Date().toISOString();
        }
      });
    },

    applyCartDiscount: (discount) => {
      set((state) => {
        state.discount = discount;
        state.lastUpdate = new Date().toISOString();
      });
    },

    removeCartDiscount: () => {
      set((state) => {
        state.discount = null;
        state.lastUpdate = new Date().toISOString();
      });
    },

    setCustomer: (customer) => {
      set((state) => {
        state.customer = customer;
        state.lastUpdate = new Date().toISOString();
      });
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-pos-cart',
    },
  }
);
