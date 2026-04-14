/**
 * Auth State Store
 *
 * Manages authentication state: user profile, tenant context,
 * permissions, and auth status flags.
 *
 * Persisted: user, tenant, permissions, isAuthenticated
 * Excluded: isLoading (recalculated on load)
 */

'use client';

import { createStore, registerStoreReset, isClient } from './utils';
import type { User, Tenant } from './types';

// ── Interfaces ─────────────────────────────────────────────────

interface AuthState {
  user: User | null;
  tenant: Tenant | null;
  permissions: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthActions {
  setUser: (user: User | null) => void;
  setTenant: (tenant: Tenant | null) => void;
  setPermissions: (permissions: string[]) => void;
  login: (user: User, tenant: Tenant, permissions: string[]) => void;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
  canAccess: (requiredPermissions: string[], mode?: 'all' | 'any') => boolean;
  reset: () => void;
}

type AuthStore = AuthState & AuthActions;

// ── Initial state ──────────────────────────────────────────────

const initialState: AuthState = {
  user: null,
  tenant: null,
  permissions: [],
  isAuthenticated: false,
  isLoading: true,
};

// ── Token cleanup ──────────────────────────────────────────────

function clearTokens(): void {
  if (!isClient) return;
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('token_expiry');
}

// ── Store ──────────────────────────────────────────────────────

export const useAuthStore = createStore<AuthStore>(
  'Auth',
  (set, get) => ({
    ...initialState,

    // ── Setters ──────────────────────────────────────────────

    setUser: (user) =>
      set((state) => {
        state.user = user;
      }),

    setTenant: (tenant) =>
      set((state) => {
        state.tenant = tenant;
      }),

    setPermissions: (permissions) =>
      set((state) => {
        state.permissions = permissions;
      }),

    // ── Login ────────────────────────────────────────────────

    login: (user, tenant, permissions) =>
      set((state) => {
        state.user = user;
        state.tenant = tenant;
        state.permissions = permissions;
        state.isAuthenticated = true;
        state.isLoading = false;
      }),

    // ── Logout ───────────────────────────────────────────────

    logout: () => {
      clearTokens();
      set((state) => {
        state.user = null;
        state.tenant = null;
        state.permissions = [];
        state.isAuthenticated = false;
        state.isLoading = false;
      });
    },

    // ── Permission Selectors ─────────────────────────────────

    hasPermission: (permission) => {
      const { isAuthenticated, permissions } = get();
      if (!isAuthenticated || permissions.length === 0) return false;

      // Exact match
      if (permissions.includes(permission)) return true;

      // Module wildcard: "products:*"
      const [module] = permission.split(':');
      if (permissions.includes(`${module}:*`)) return true;

      // Superuser wildcard
      if (permissions.includes('*:*')) return true;

      return false;
    },

    canAccess: (requiredPermissions, mode = 'all') => {
      const { isAuthenticated, hasPermission: hasPerm } = get();
      if (!isAuthenticated) return false;
      if (requiredPermissions.length === 0) return true;

      return mode === 'all'
        ? requiredPermissions.every((p) => hasPerm(p))
        : requiredPermissions.some((p) => hasPerm(p));
    },

    // ── Reset ────────────────────────────────────────────────

    reset: () => {
      clearTokens();
      set(initialState);
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-auth',
      version: 1,
      partialize: (state: AuthStore) => ({
        user: state.user,
        tenant: state.tenant,
        permissions: state.permissions,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  }
);

// Register for global resetAllStores()
registerStoreReset(() => useAuthStore.getState().reset());
