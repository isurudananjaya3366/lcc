// ================================================================
// useCacheRefresh — Task 84
// ================================================================

'use client';

import { useCallback, useRef, useState } from 'react';

type EntityType =
  | 'all'
  | 'products'
  | 'customers'
  | 'sales'
  | 'inventory'
  | 'settings';
type RefreshStrategy = 'merge' | 'overwrite' | 'clearAndFresh';

interface CacheRefreshState {
  loading: boolean;
  progress: number;
  currentEntity: EntityType | null;
  error: string | null;
  lastRefresh: Date | null;
}

export function useCacheRefresh() {
  const [state, setState] = useState<CacheRefreshState>({
    loading: false,
    progress: 0,
    currentEntity: null,
    error: null,
    lastRefresh: null,
  });
  const abortRef = useRef<AbortController | null>(null);

  const trigger = useCallback(
    async (entity: EntityType = 'all', strategy: RefreshStrategy = 'merge') => {
      abortRef.current?.abort();
      abortRef.current = new AbortController();

      setState({
        loading: true,
        progress: 0,
        currentEntity: entity,
        error: null,
        lastRefresh: state.lastRefresh,
      });

      try {
        const entities: EntityType[] =
          entity === 'all'
            ? ['products', 'customers', 'sales', 'inventory', 'settings']
            : [entity];

        for (let i = 0; i < entities.length; i++) {
          if (abortRef.current.signal.aborted) break;
          const current = entities[i] ?? 'all';
          setState((s) => ({
            ...s,
            currentEntity: current,
            progress: Math.round(((i + 1) / entities.length) * 100),
          }));

          // Dynamic import to avoid circular dependencies
          const { cacheManager } = await import('@/lib/offline/cache-manager');

          if (strategy === 'clearAndFresh') {
            await cacheManager.clearCache(true);
          }

          // Trigger automatic pruning to refresh cache state
          await cacheManager.runAutomaticPruning();
        }

        setState({
          loading: false,
          progress: 100,
          currentEntity: null,
          error: null,
          lastRefresh: new Date(),
        });
      } catch (err) {
        setState((s) => ({
          ...s,
          loading: false,
          progress: 0,
          currentEntity: null,
          error: err instanceof Error ? err.message : 'Cache refresh failed',
        }));
      }
    },
    [state.lastRefresh]
  );

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
    error: state.error,
    lastRefresh: state.lastRefresh,
  };
}
