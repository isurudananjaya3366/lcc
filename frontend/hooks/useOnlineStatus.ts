'use client';

import { useEffect, useState, useCallback } from 'react';

/**
 * React hook that monitors network connectivity status.
 * Listens to browser online/offline events and exposes current state.
 *
 * @returns {{ isOnline: boolean; wasOffline: boolean }} current connectivity
 *
 * @example
 * ```tsx
 * function App() {
 *   const { isOnline, wasOffline } = useOnlineStatus();
 *
 *   if (!isOnline) return <OfflineBanner />;
 *   if (wasOffline) return <ReconnectedToast />;
 * }
 * ```
 */
export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState<boolean>(() =>
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );
  const [wasOffline, setWasOffline] = useState(false);

  const handleOnline = useCallback(() => {
    setIsOnline(true);
    setWasOffline(true);
  }, []);

  const handleOffline = useCallback(() => {
    setIsOnline(false);
  }, []);

  const clearWasOffline = useCallback(() => {
    setWasOffline(false);
  }, []);

  useEffect(() => {
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [handleOnline, handleOffline]);

  return { isOnline, wasOffline, clearWasOffline };
}
