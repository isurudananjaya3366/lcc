'use client';

import { useEffect, useRef } from 'react';
import { useStoreAuthStore } from '@/stores/store';
import { getCurrentUser, refreshTokenApi } from '@/services/storefront/authService';
import {
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
  isTokenExpired,
  getRememberMe,
} from '@/services/storefront/tokenService';

/**
 * Convenience hook over useStoreAuthStore.
 * Hydrates auth state on mount by checking existing tokens.
 */
export function useAuth() {
  const store = useStoreAuthStore();
  const hydrated = useRef(false);

  useEffect(() => {
    if (hydrated.current) return;
    hydrated.current = true;

    let cancelled = false;

    async function hydrate() {
      store.setLoading(true);

      try {
        const accessToken = getAccessToken();
        const refreshToken = getRefreshToken();

        // Case 1: Valid access token — fetch user profile
        if (accessToken && !isTokenExpired(accessToken)) {
          const { user } = await getCurrentUser();
          if (!cancelled) {
            store.setUser(user);
          }
          return;
        }

        // Case 2: Access token expired but refresh token exists — try refresh
        if (refreshToken && !isTokenExpired(refreshToken, 0)) {
          try {
            const result = await refreshTokenApi();
            const responseAny = result as Record<string, unknown>;
            const rememberMe = getRememberMe();

            if (responseAny.access) {
              setAccessToken(responseAny.access as string, rememberMe);
            }
            if (responseAny.refresh) {
              setRefreshToken(responseAny.refresh as string, rememberMe);
            }

            const { user } = await getCurrentUser();
            if (!cancelled) {
              store.setUser(user);
            }
            return;
          } catch {
            // Refresh failed — fall through to unauthenticated
          }
        }

        // Case 3: No valid tokens
        if (!cancelled) {
          store.setUser(null);
        }
      } catch {
        if (!cancelled) {
          store.setUser(null);
        }
      } finally {
        if (!cancelled) {
          store.setLoading(false);
        }
      }
    }

    hydrate();

    return () => {
      cancelled = true;
    };
    // Run only on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    error: store.error,
    login: store.login,
    logout: store.logout,
    setUser: store.setUser,
    clearError: store.clearError,
    checkAuth: store.checkAuth,
  };
}
