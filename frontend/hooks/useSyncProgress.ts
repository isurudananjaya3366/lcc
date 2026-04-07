// ================================================================
// useSyncProgress — Tasks 75-76
// ================================================================
// Real-time sync progress hook for SyncStatusBar integration.
// ================================================================

'use client';

import { useCallback, useEffect, useState } from 'react';

export interface SyncProgressState {
  status: 'idle' | 'syncing' | 'complete' | 'error';
  phase: string;
  progress: number;
  currentOperation: string;
  startedAt: Date | null;
  completedAt: Date | null;
}

const INITIAL: SyncProgressState = {
  status: 'idle',
  phase: '',
  progress: 0,
  currentOperation: '',
  startedAt: null,
  completedAt: null,
};

export function useSyncProgress() {
  const [state, setState] = useState<SyncProgressState>(INITIAL);

  // Listen for BroadcastChannel sync events
  useEffect(() => {
    let channel: BroadcastChannel | null = null;
    try {
      channel = new BroadcastChannel('pos-sync-channel');
      channel.onmessage = (event) => {
        const { type, payload } = event.data ?? {};
        if (type === 'SYNC_STARTED') {
          setState({
            status: 'syncing',
            phase: payload?.phase ?? 'Initializing',
            progress: 0,
            currentOperation: 'Starting sync...',
            startedAt: new Date(),
            completedAt: null,
          });
        } else if (type === 'SYNC_PROGRESS') {
          setState((prev) => ({
            ...prev,
            status: 'syncing',
            phase: payload?.phase ?? prev.phase,
            progress: payload?.percentage ?? prev.progress,
            currentOperation:
              payload?.currentOperation ?? prev.currentOperation,
          }));
        } else if (type === 'SYNC_COMPLETED') {
          setState((prev) => ({
            ...prev,
            status: 'complete',
            progress: 100,
            completedAt: new Date(),
          }));
        } else if (type === 'SYNC_ERROR') {
          setState((prev) => ({
            ...prev,
            status: 'error',
            currentOperation: payload?.message ?? 'Sync failed',
          }));
        }
      };
    } catch {
      // BroadcastChannel not supported
    }
    return () => {
      channel?.close();
    };
  }, []);

  const reset = useCallback(() => setState(INITIAL), []);

  return { ...state, reset };
}
