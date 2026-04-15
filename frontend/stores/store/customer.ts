'use client';

import { createStore } from '../utils';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface StoreCustomer {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone: string;
  avatarUrl: string | null;
  isVerified: boolean;
}

interface CustomerAuthState {
  customer: StoreCustomer | null;
  isLoggedIn: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  setCustomer: (customer: StoreCustomer | null) => void;
  login: (customer: StoreCustomer) => void;
  logout: () => void;
  updateProfile: (data: Partial<StoreCustomer>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// ─── Store ──────────────────────────────────────────────────────────────────

export const useCustomerStore = createStore<CustomerAuthState>(
  'StoreCustomer',
  (set, get) => ({
    customer: null,
    isLoggedIn: false,
    isLoading: false,
    error: null,

    setCustomer: (customer: StoreCustomer | null) => {
      set((state) => {
        state.customer = customer;
        state.isLoggedIn = customer !== null;
      });
    },

    login: (customer: StoreCustomer) => {
      set((state) => {
        state.customer = customer;
        state.isLoggedIn = true;
        state.error = null;
      });
    },

    logout: () => {
      set((state) => {
        state.customer = null;
        state.isLoggedIn = false;
        state.error = null;
      });
      // Clear auth tokens
      if (typeof window !== 'undefined') {
        localStorage.removeItem('store-auth-token');
        localStorage.removeItem('store-refresh-token');
      }
    },

    updateProfile: (data: Partial<StoreCustomer>) => {
      const current = get().customer;
      if (!current) return;
      set((state) => {
        state.customer = { ...current, ...data };
      });
    },

    setLoading: (loading: boolean) => set({ isLoading: loading }),
    setError: (error: string | null) => set({ error }),
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-store-customer',
      partialize: (state: CustomerAuthState) => ({
        customer: state.customer,
        isLoggedIn: state.isLoggedIn,
      }),
    },
  }
);
