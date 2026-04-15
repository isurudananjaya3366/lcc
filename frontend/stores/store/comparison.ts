'use client';

import { createStore } from '../utils';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ComparisonProduct {
  productId: string;
  name: string;
  slug: string;
  categoryId: string;
  categoryName: string;
  currentPrice: number;
  specifications: { name: string; value: string }[];
  features: { name: string; available: boolean }[];
  primaryImage: string;
  addedAt: string;
}

interface ComparisonState {
  items: ComparisonProduct[];
  currentCategory: string | null;
  error: string | null;
  maxItems: number;

  // Selectors
  canAddProduct: (product: { productId: string; categoryId: string }) => {
    canAdd: boolean;
    reason?: string;
  };
  getProductCount: () => number;
  getComparisonData: () => ComparisonProduct[];

  // Actions
  addProduct: (product: ComparisonProduct) => boolean;
  removeProduct: (productId: string) => void;
  clearAll: () => void;
}

// ─── Constants ──────────────────────────────────────────────────────────────

const MAX_COMPARISON_ITEMS = 4;

// ─── Store ──────────────────────────────────────────────────────────────────

export const useComparisonStore = createStore<ComparisonState>(
  'Comparison',
  (set, get) => ({
    items: [],
    currentCategory: null,
    error: null,
    maxItems: MAX_COMPARISON_ITEMS,

    canAddProduct: (product) => {
      const state = get();

      if (state.items.length >= MAX_COMPARISON_ITEMS) {
        return { canAdd: false, reason: 'Maximum comparison items reached (4)' };
      }

      if (state.currentCategory && state.currentCategory !== product.categoryId) {
        return { canAdd: false, reason: 'Products must be from the same category' };
      }

      if (state.items.some((i) => i.productId === product.productId)) {
        return { canAdd: false, reason: 'Product already in comparison' };
      }

      return { canAdd: true };
    },

    getProductCount: () => get().items.length,

    getComparisonData: () => get().items,

    addProduct: (product: ComparisonProduct) => {
      const check = get().canAddProduct({
        productId: product.productId,
        categoryId: product.categoryId,
      });

      if (!check.canAdd) {
        set({ error: check.reason ?? null });
        return false;
      }

      set((state) => {
        state.items.push({
          ...product,
          addedAt: product.addedAt || new Date().toISOString(),
        });
        state.currentCategory = product.categoryId;
        state.error = null;
      });

      return true;
    },

    removeProduct: (productId: string) => {
      set((state) => {
        state.items = state.items.filter((i) => i.productId !== productId);
        if (state.items.length === 0) {
          state.currentCategory = null;
        }
        state.error = null;
      });
    },

    clearAll: () => {
      set((state) => {
        state.items = [];
        state.currentCategory = null;
        state.error = null;
      });
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-product-comparison',
      partialize: (state: ComparisonState) => ({
        items: state.items,
        currentCategory: state.currentCategory,
      }),
    },
  }
);
