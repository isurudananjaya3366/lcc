'use client';

import { useEffect, useState, useCallback, useRef } from 'react';

import { getAccessToken, getRefreshToken, isTokenExpired } from '@/lib/tokenStorage';
import { authService } from '@/services/api/authService';
import { useAuthStore } from '@/stores/useAuthStore';

export type SessionStatus = 'active' | 'expiring' | 'expired';

const CHECK_INTERVAL_MS = 60_000; // 1 minute
const WARNING_THRESHOLD_MS = 5 * 60_000; // 5 minutes

/**
 * Get the expiry time (ms) from the current access token.
 */
function getTokenExpiryMs(): number | null {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp ? payload.exp * 1000 : null;
  } catch {
    return null;
  }
}

export function useSessionMonitor() {
  const [sessionStatus, setSessionStatus] = useState<SessionStatus>('active');
  const [timeUntilExpiry, setTimeUntilExpiry] = useState<number>(Infinity);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const { isAuthenticated, logout } = useAuthStore();

  const checkSession = useCallback(() => {
    if (!isAuthenticated) {
      setSessionStatus('active');
      return;
    }

    const token = getAccessToken();
    if (!token) {
      setSessionStatus('expired');
      return;
    }

    const expiryMs = getTokenExpiryMs();
    if (!expiryMs) {
      setSessionStatus('active');
      return;
    }

    const remaining = expiryMs - Date.now();
    setTimeUntilExpiry(remaining);

    if (remaining <= 0) {
      setSessionStatus('expired');
    } else if (remaining <= WARNING_THRESHOLD_MS) {
      setSessionStatus('expiring');
    } else {
      setSessionStatus('active');
    }
  }, [isAuthenticated]);

  const refreshSession = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await authService.refreshToken();
      setSessionStatus('active');
      checkSession();
    } catch {
      setSessionStatus('expired');
    } finally {
      setIsRefreshing(false);
    }
  }, [checkSession]);

  const handleExpiry = useCallback(() => {
    logout();
  }, [logout]);

  // Periodic session check
  useEffect(() => {
    if (!isAuthenticated) return;

    checkSession();
    intervalRef.current = setInterval(checkSession, CHECK_INTERVAL_MS);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isAuthenticated, checkSession]);

  // Multi-tab sync via storage events
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'lcc_access_token' && !e.newValue) {
        setSessionStatus('expired');
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Auto-attempt refresh when expiring
  useEffect(() => {
    if (sessionStatus === 'expiring' && !isRefreshing) {
      const refreshToken = getRefreshToken();
      if (refreshToken && !isTokenExpired(refreshToken)) {
        // Background refresh attempt
        refreshSession();
      }
    }
  }, [sessionStatus, isRefreshing, refreshSession]);

  return {
    sessionStatus,
    timeUntilExpiry,
    isRefreshing,
    refreshSession,
    handleExpiry,
  };
}
