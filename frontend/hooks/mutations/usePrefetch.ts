/**
 * Prefetch Utilities
 *
 * Hooks for prefetching data on hover, focus, or programmatically
 * to improve perceived performance.
 */

import { useCallback, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { QueryKey, QueryFunction } from '@tanstack/react-query';

// ── Config ─────────────────────────────────────────────────────

interface PrefetchConfig<T = unknown> {
  queryKey: QueryKey;
  queryFn: QueryFunction<T>;
  staleTime?: number;
}

// ── usePrefetch ────────────────────────────────────────────────

/**
 * Returns a `prefetch` callback that can be called imperatively.
 */
export function usePrefetch<T = unknown>(config: PrefetchConfig<T>) {
  const queryClient = useQueryClient();

  const prefetch = useCallback(() => {
    queryClient.prefetchQuery({
      queryKey: config.queryKey,
      queryFn: config.queryFn,
      staleTime: config.staleTime ?? 5 * 60 * 1000,
    });
  }, [queryClient, config.queryKey, config.queryFn, config.staleTime]);

  return prefetch;
}

// ── usePrefetchOnHover ─────────────────────────────────────────

interface HoverHandlers {
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}

/**
 * Returns mouse-enter / mouse-leave handlers that prefetch
 * data after a short debounce to avoid excessive calls on
 * rapid hover movements.
 */
export function usePrefetchOnHover<T = unknown>(
  config: PrefetchConfig<T>,
  debounceMs = 150,
): HoverHandlers {
  const prefetch = usePrefetch(config);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const onMouseEnter = useCallback(() => {
    timerRef.current = setTimeout(prefetch, debounceMs);
  }, [prefetch, debounceMs]);

  const onMouseLeave = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  return { onMouseEnter, onMouseLeave };
}

// ── usePrefetchOnFocus ─────────────────────────────────────────

interface FocusHandlers {
  onFocus: () => void;
}

/**
 * Returns an `onFocus` handler that prefetches data when an
 * element receives focus (e.g. keyboard navigation).
 */
export function usePrefetchOnFocus<T = unknown>(
  config: PrefetchConfig<T>,
): FocusHandlers {
  const prefetch = usePrefetch(config);

  const onFocus = useCallback(() => {
    prefetch();
  }, [prefetch]);

  return { onFocus };
}
