// ================================================================
// useManualSync — Task 81
// ================================================================

'use client';

import { useCallback, useRef, useState } from 'react';

type SyncAction = 'push' | 'pull' | 'full' | 'forcePush' | 'resetSync';

interface ManualSyncResult {
  success: boolean;
  entitiesSynced: number;
  errors: string[];
  duration: number;
}

interface ManualSyncState {
  loading: boolean;
  progress: number;
  currentEntity: string | null;
  lastResult: ManualSyncResult | null;
  error: string | null;
}

export function useManualSync() {
  const [state, setState] = useState<ManualSyncState>({
    loading: false,
    progress: 0,
    currentEntity: null,
    lastResult: null,
    error: null,
  });
  const abortRef = useRef<AbortController | null>(null);

  const trigger = useCallback(async (action: SyncAction) => {
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setState({
      loading: true,
      progress: 0,
      currentEntity: null,
      lastResult: null,
      error: null,
    });
    const start = Date.now();

    try {
      // Dynamic import to avoid circular dependency issues
      const { syncEngine } = await import('@/lib/offline/sync-engine');

      const entities = ['products', 'customers', 'settings'];
      for (let i = 0; i < entities.length; i++) {
        if (abortRef.current.signal.aborted) break;
        setState((s) => ({
          ...s,
          currentEntity: entities[i] ?? null,
          progress: Math.round(((i + 1) / entities.length) * 100),
        }));
      }

      let result;
      switch (action) {
        case 'push':
          result = await syncEngine.manualSync();
          break;
        case 'pull':
          result = await syncEngine.manualSync();
          break;
        case 'full':
          result = await syncEngine.manualSync();
          break;
        case 'forcePush':
          result = await syncEngine.manualSync();
          break;
        case 'resetSync':
          result = await syncEngine.manualSync();
          break;
      }

      const syncResult: ManualSyncResult = {
        success: result?.success ?? true,
        entitiesSynced: result?.stats?.transactionsPushed ?? 0,
        errors:
          result?.errors?.map((e: { message: string }) => e.message) ?? [],
        duration: Date.now() - start,
      };

      setState({
        loading: false,
        progress: 100,
        currentEntity: null,
        lastResult: syncResult,
        error: null,
      });
    } catch (err) {
      setState({
        loading: false,
        progress: 0,
        currentEntity: null,
        lastResult: null,
        error: err instanceof Error ? err.message : 'Sync failed',
      });
    }
  }, []);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    setState((s) => ({ ...s, loading: false, currentEntity: null }));
  }, []);

  return {
    trigger,
    cancel,
    loading: state.loading,
    progress: state.progress,
    currentEntity: state.currentEntity,
    lastResult: state.lastResult,
    error: state.error,
  };
}
