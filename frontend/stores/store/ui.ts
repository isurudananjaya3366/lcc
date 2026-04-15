'use client';

import { createStore } from '../utils';

// ─── Types ──────────────────────────────────────────────────────────────────

interface StoreUIState {
  mobileMenuOpen: boolean;
  cartDrawerOpen: boolean;
  searchOpen: boolean;
  quickViewProductId: string | null;

  // Actions
  setMobileMenuOpen: (value: boolean) => void;
  setCartDrawerOpen: (value: boolean) => void;
  setSearchOpen: (value: boolean) => void;
  setQuickViewProduct: (productId: string | null) => void;
  closeAllModals: () => void;
  toggleMobileMenu: () => void;
  toggleCartDrawer: () => void;
}

// ─── Store ──────────────────────────────────────────────────────────────────

export const useStoreUIStore = createStore<StoreUIState>(
  'StoreUI',
  (set, get) => ({
    mobileMenuOpen: false,
    cartDrawerOpen: false,
    searchOpen: false,
    quickViewProductId: null,

    setMobileMenuOpen: (value: boolean) => {
      set((state) => {
        state.mobileMenuOpen = value;
      });
    },

    setCartDrawerOpen: (value: boolean) => {
      set((state) => {
        state.cartDrawerOpen = value;
      });
    },

    setSearchOpen: (value: boolean) => {
      set((state) => {
        state.searchOpen = value;
      });
    },

    setQuickViewProduct: (productId: string | null) => {
      set((state) => {
        state.quickViewProductId = productId;
      });
    },

    closeAllModals: () => {
      set((state) => {
        state.mobileMenuOpen = false;
        state.cartDrawerOpen = false;
        state.searchOpen = false;
        state.quickViewProductId = null;
      });
    },

    toggleMobileMenu: () => {
      set((state) => {
        state.mobileMenuOpen = !state.mobileMenuOpen;
      });
    },

    toggleCartDrawer: () => {
      set((state) => {
        state.cartDrawerOpen = !state.cartDrawerOpen;
      });
    },
  })
);
