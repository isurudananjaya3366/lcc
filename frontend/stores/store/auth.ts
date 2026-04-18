'use client';

import { createStore } from '../utils';
import type { StoreUser } from '@/types/storefront/auth.types';

// ─── Types ──────────────────────────────────────────────────────────────────

interface StoreAuthState {
  user: StoreUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  logout: () => void;
  setUser: (user: StoreUser | null) => void;
  clearError: () => void;
  checkAuth: () => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// ─── Store ──────────────────────────────────────────────────────────────────

export const useStoreAuthStore = createStore<StoreAuthState>(
  'StoreAuth',
  (set) => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,

    login: async (email, password, rememberMe) => {
      set((s) => {
        s.isLoading = true;
        s.error = null;
      });
      try {
        const { loginApi } = await import('@/services/storefront/authService');
        const { setAccessToken, setRefreshToken, setRememberMe } = await import('@/services/storefront/tokenService');
        const result = await loginApi(email, password);
        const responseAny = result as Record<string, unknown>;

        // Store rememberMe preference
        setRememberMe(!!rememberMe);

        // Store tokens if returned in response body
        if (responseAny.access) {
          setAccessToken(responseAny.access as string, rememberMe);
        }
        if (responseAny.refresh) {
          setRefreshToken(responseAny.refresh as string, rememberMe);
        }

        set((s) => {
          s.user = result.user;
          s.isAuthenticated = true;
          s.isLoading = false;
        });
      } catch (err) {
        set((s) => {
          s.isLoading = false;
          s.error = err instanceof Error ? err.message : 'Login failed';
        });
      }
    },

    logout: () => {
      // Fire-and-forget server logout
      import('@/services/storefront/authService').then((m) => m.logoutApi()).catch(() => {});
      // Clear cookie-based tokens
      import('@/services/storefront/tokenService').then((m) => m.clearTokens()).catch(() => {});
      set((s) => {
        s.user = null;
        s.isAuthenticated = false;
        s.error = null;
      });
    },

    setUser: (user) => {
      set((s) => {
        s.user = user;
        s.isAuthenticated = user !== null;
      });
    },

    clearError: () => {
      set((s) => {
        s.error = null;
      });
    },

    checkAuth: async () => {
      set((s) => {
        s.isLoading = true;
      });
      try {
        const { getCurrentUser } = await import('@/services/storefront/authService');
        const { user } = await getCurrentUser();
        set((s) => {
          s.user = user;
          s.isAuthenticated = true;
          s.isLoading = false;
        });
      } catch {
        set((s) => {
          s.user = null;
          s.isAuthenticated = false;
          s.isLoading = false;
        });
      }
    },

    setLoading: (loading) => {
      set((s) => {
        s.isLoading = loading;
      });
    },

    setError: (error) => {
      set((s) => {
        s.error = error;
      });
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-store-auth',
      partialize: (state: StoreAuthState) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  }
);
