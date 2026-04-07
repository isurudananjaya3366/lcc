// ================================================================
// useOfflineStatus — Tasks 73-74
// ================================================================
// Hook providing live connection status for the POS offline module.
// ================================================================

'use client';

import { useCallback, useEffect, useState } from 'react';

export type ConnectionStatusType =
  | 'ONLINE'
  | 'OFFLINE'
  | 'SYNCING'
  | 'SYNC_ERROR';

export interface OfflineStatusState {
  status: ConnectionStatusType;
  lastSyncTime: Date | null;
  isOnline: boolean;
  isSyncing: boolean;
  syncError: string | null;
}

export function useOfflineStatus(): OfflineStatusState {
  const [state, setState] = useState<OfflineStatusState>({
    status:
      typeof navigator !== 'undefined' && navigator.onLine
        ? 'ONLINE'
        : 'OFFLINE',
    lastSyncTime: null,
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    isSyncing: false,
    syncError: null,
  });

  const handleOnline = useCallback(() => {
    setState((s) => ({ ...s, status: 'ONLINE', isOnline: true }));
  }, []);

  const handleOffline = useCallback(() => {
    setState((s) => ({ ...s, status: 'OFFLINE', isOnline: false }));
  }, []);

  useEffect(() => {
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [handleOnline, handleOffline]);

  return state;
}
