/**
 * TanStack Query — QueryClient Configuration
 *
 * Centralised QueryClient instance with sensible defaults for
 * the LankaCommerce Cloud POS dashboard.
 */

import { QueryClient } from '@tanstack/react-query';
import type { AxiosError } from 'axios';

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
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
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
