'use client';

import { createStore } from '../utils';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface RecentProduct {
  productId: string;
  name: string;
  slug: string;
  primaryImage: string;
  currentPrice: number;
  viewedAt: string;
}

interface RecentlyViewedState {
  items: RecentProduct[];
  maxItems: number;

  // Selectors
  getProducts: () => RecentProduct[];

  // Actions
  addProduct: (product: Omit<RecentProduct, 'viewedAt'>) => void;
  removeProduct: (productId: string) => void;
  clearAll: () => void;
}

// ─── Constants ──────────────────────────────────────────────────────────────

const MAX_ITEMS = 10;
const PRUNE_DAYS = 30;

function pruneOldItems(items: RecentProduct[]): RecentProduct[] {
  const cutoff = Date.now() - PRUNE_DAYS * 24 * 60 * 60 * 1000;
  return items.filter((item) => new Date(item.viewedAt).getTime() > cutoff);
}

// ─── Store ──────────────────────────────────────────────────────────────────

export const useRecentlyViewedStore = createStore<RecentlyViewedState>(
  'RecentlyViewed',
  (set, get) => ({
    items: [],
    maxItems: MAX_ITEMS,

    getProducts: () => {
      // Return in reverse chronological order (most recent first)
      return [...get().items].reverse();
    },

    addProduct: (product) => {
      set((state) => {
        // Remove if already exists (will re-add with updated timestamp)
        state.items = state.items.filter((i) => i.productId !== product.productId);

        // Add to end with current timestamp
        state.items.push({
          ...product,
          viewedAt: new Date().toISOString(),
        });

        // Trim to max capacity (remove oldest from beginning)
        if (state.items.length > MAX_ITEMS) {
          state.items = state.items.slice(-MAX_ITEMS);
        }

        // Prune items older than 30 days
        state.items = pruneOldItems(state.items);
      });
    },

    removeProduct: (productId: string) => {
      set((state) => {
        state.items = state.items.filter((i) => i.productId !== productId);
      });
    },

    clearAll: () => {
      set((state) => {
        state.items = [];
      });
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-recently-viewed',
      partialize: (state: RecentlyViewedState) => ({
        items: state.items,
      }),
      onRehydrateStorage: () => (state) => {
        // Prune items older than 30 days on hydration
        if (state) {
          state.items = pruneOldItems(state.items);
        }
      },
    },
  }
);
