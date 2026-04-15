'use client';

import { createStore } from '../utils';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface WishlistProduct {
  productId: string;
  name: string;
  slug: string;
  price: number;
  salePrice: number | null;
  image: string;
  inStock: boolean;
  addedAt: string;
}

interface WishlistState {
  items: WishlistProduct[];

  // Selectors
  getItemCount: () => number;
  isInWishlist: (productId: string) => boolean;

  // Actions
  add: (product: WishlistProduct) => void;
  remove: (productId: string) => void;
  toggle: (product: WishlistProduct) => void;
  clear: () => void;
}

// ─── Store ──────────────────────────────────────────────────────────────────

export const useWishlistStore = createStore<WishlistState>(
  'Wishlist',
  (set, get) => ({
    items: [],

    getItemCount: () => get().items.length,

    isInWishlist: (productId: string) => get().items.some((item) => item.productId === productId),

    add: (product: WishlistProduct) => {
      if (get().isInWishlist(product.productId)) return;

      set((state) => {
        state.items.push({
          ...product,
          addedAt: product.addedAt || new Date().toISOString(),
        });
      });
    },

    remove: (productId: string) => {
      set((state) => {
        state.items = state.items.filter((item) => item.productId !== productId);
      });
    },

    toggle: (product: WishlistProduct) => {
      if (get().isInWishlist(product.productId)) {
        get().remove(product.productId);
      } else {
        get().add(product);
      }
    },

    clear: () => {
      set((state) => {
        state.items = [];
      });
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-store-wishlist',
      partialize: (state: WishlistState) => ({
        items: state.items,
      }),
    },
  }
);
