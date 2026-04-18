'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { getAccessToken, getRefreshToken, setAccessToken, setRefreshToken, isTokenExpired, getTokenExpiryMs, getRememberMe } from '@/services/storefront/tokenService';
import { refreshTokenApi } from '@/services/storefront/authService';
import { useStoreAuthStore } from '@/stores/store';

const CHECK_INTERVAL_MS = 4 * 60 * 1000; // 4 minutes
const EXPIRY_WARNING_MS = 2 * 60 * 1000; // 2 minutes before expiry

export function useTokenRefresh() {
  const logout = useStoreAuthStore((s) => s.logout);
  const isAuthenticated = useStoreAuthStore((s) => s.isAuthenticated);
  const [isExpiringSoon, setIsExpiringSoon] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const refresh = getRefreshToken();
      if (!refresh || isTokenExpired(refresh, 0)) {
        logout();
        return false;
      }

      const result = await refreshTokenApi();
      // If the API returns tokens in the response body, store them.
      // Otherwise the backend sets them via cookies with credentials: 'include'.
      const responseAny = result as Record<string, unknown>;
      if (responseAny.access) {
        const rememberMe = getRememberMe();
        setAccessToken(responseAny.access as string, rememberMe);
      }
      if (responseAny.refresh) {
        const rememberMe = getRememberMe();
        setRefreshToken(responseAny.refresh as string, rememberMe);
      }

      setIsExpiringSoon(false);
      return true;
    } catch {
      logout();
      return false;
    }
  }, [logout]);

  const checkAndRefresh = useCallback(() => {
    const accessToken = getAccessToken();
    if (!accessToken) return;

    const remainingMs = getTokenExpiryMs(accessToken);
    if (remainingMs !== null && remainingMs <= EXPIRY_WARNING_MS) {
      setIsExpiringSoon(true);

      if (isTokenExpired(accessToken, 0)) {
        refreshToken();
      }
    } else {
      setIsExpiringSoon(false);
    }
  }, [refreshToken]);

  useEffect(() => {
    if (!isAuthenticated) {
      setIsExpiringSoon(false);
      return;
    }

    // Initial check
    checkAndRefresh();

    intervalRef.current = setInterval(checkAndRefresh, CHECK_INTERVAL_MS);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isAuthenticated, checkAndRefresh]);

  return {
    isExpiringSoon,
    refreshToken,
  };
}
