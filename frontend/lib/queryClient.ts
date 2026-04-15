/**
 * TanStack Query — QueryClient Configuration
 *
 * Centralised QueryClient instance with sensible defaults for
 * the LankaCommerce Cloud POS platform (dashboard + webstore).
 *
 * Staleness & Cache Strategy:
 * - staleTime (5 min): Product/inventory data considered fresh for short periods.
 *   Components receive cached data instantly; background refetch occurs after staleness.
 * - gcTime (30 min): Cached entries kept in memory for quick return-visits.
 *   After 30 min of no usage the entry is garbage-collected.
 * - Retry: 3 attempts with exponential backoff (1 s → 2 s → 4 s).
 *   Client errors (400/401/403/404/422) skip retry — they won't succeed on retry.
 * - Window focus: Stale queries refetch automatically when the user returns to tab.
 */

import { QueryClient } from '@tanstack/react-query';
import type { AxiosError } from 'axios';
import { storeQueryKeys } from './storeQueryKeys';

// ── Retry helpers ──────────────────────────────────────────────

/** HTTP status codes that should NOT be retried */
const NON_RETRYABLE_STATUS = new Set([400, 401, 403, 404, 422]);

function shouldRetry(failureCount: number, error: unknown): boolean {
  if (failureCount >= 3) return false;

  // Axios errors carry a response object
  const status = (error as AxiosError)?.response?.status;
  if (status && NON_RETRYABLE_STATUS.has(status)) return false;

  return true;
}

/** Exponential backoff: 1 s → 2 s → 4 s */
function retryDelay(attemptIndex: number): number {
  return Math.min(1000 * 2 ** attemptIndex, 30_000);
}

// ── QueryClient ────────────────────────────────────────────────

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes — fresh window
      gcTime: 30 * 60 * 1000, // 30 minutes — cache retention
      retry: shouldRetry,
      retryDelay,
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
      refetchOnMount: true,
    },
    mutations: {
      retry: false,
    },
  },
});

// ── Cache Invalidation Utilities ───────────────────────────────

/** Invalidate all product-related queries (after add/update/delete) */
export function invalidateProductQueries() {
  return queryClient.invalidateQueries({ queryKey: storeQueryKeys.products.all() });
}

/** Invalidate all category queries (after category changes) */
export function invalidateCategoryQueries() {
  return queryClient.invalidateQueries({ queryKey: storeQueryKeys.categories.all() });
}

/** Prefetch a single product detail for anticipated navigation */
export function prefetchProduct(slug: string, queryFn: () => Promise<unknown>) {
  return queryClient.prefetchQuery({
    queryKey: storeQueryKeys.products.detail(slug),
    queryFn,
    staleTime: 5 * 60 * 1000,
  });
}

/** Prefetch related products for anticipated navigation */
export function prefetchRelatedProducts(
  productId: number,
  limit: number,
  queryFn: () => Promise<unknown>
) {
  return queryClient.prefetchQuery({
    queryKey: storeQueryKeys.products.related(productId, limit),
    queryFn,
  });
}

/** Directly update product query data in cache (optimistic update) */
export function setProductQueryData<T>(slug: string, updater: T | ((old: T | undefined) => T)) {
  queryClient.setQueryData(storeQueryKeys.products.detail(slug), updater);
}
