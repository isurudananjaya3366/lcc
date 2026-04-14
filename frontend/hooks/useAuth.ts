/**
 * useAuth Hook
 *
 * Convenience wrapper around `useAuthStore` that exposes a flat
 * object with auth state and actions.  Uses atomic selectors
 * so components only re-render when the specific values they
 * consume change.
 */

'use client';

import { useAuthStore } from '@/stores/useAuthStore';
import type { User, Tenant } from '@/stores/types';

export interface UseAuthReturn {
  user: User | null;
  tenant: Tenant | null;
  permissions: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
  hasPermission: (permission: string) => boolean;
  canAccess: (
    permissions: string[],
    mode?: 'all' | 'any',
  ) => boolean;
  login: (user: User, tenant: Tenant, permissions: string[]) => void;
  logout: () => void;
}

export function useAuth(): UseAuthReturn {
  const user = useAuthStore((s) => s.user);
  const tenant = useAuthStore((s) => s.tenant);
  const permissions = useAuthStore((s) => s.permissions);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const hasPermission = useAuthStore((s) => s.hasPermission);
  const canAccess = useAuthStore((s) => s.canAccess);
  const login = useAuthStore((s) => s.login);
  const logout = useAuthStore((s) => s.logout);

  return {
    user,
    tenant,
    permissions,
    isAuthenticated,
    isLoading,
    hasPermission,
    canAccess,
    login,
    logout,
  };
}
