/**
 * Cache Invalidation Utilities
 *
 * Centralised helpers for invalidating TanStack Query cache
 * after mutations.
 */

import type { QueryClient, QueryKey } from '@tanstack/react-query';

// ── Strategy Enum ──────────────────────────────────────────────

export type InvalidationStrategy = 'EXACT' | 'PARTIAL' | 'ALL' | 'RELATED' | 'SELECTIVE';

// ── Config ─────────────────────────────────────────────────────

export interface InvalidationConfig {
  resource: string;
  id?: string | number;
  strategy: InvalidationStrategy;
  relatedResources?: string[];
  predicate?: (query: { queryKey: QueryKey }) => boolean;
}

// ── Invalidation Matrix ────────────────────────────────────────

const RELATED_RESOURCES: Record<string, Record<string, string[]>> = {
  products: {
    create: ['inventory'],
    update: ['orders', 'inventory'],
    delete: ['orders', 'inventory'],
  },
  orders: {
    create: ['products', 'customers'],
    update: ['products', 'customers'],
    delete: ['products', 'customers'],
  },
  customers: {
    create: [],
    update: ['orders'],
    delete: ['orders'],
  },
};

// ── Main Function ──────────────────────────────────────────────

export function invalidateCache(queryClient: QueryClient, config: InvalidationConfig): void {
  const { resource, id, strategy, relatedResources, predicate } = config;

  switch (strategy) {
    case 'EXACT':
      if (id) {
        queryClient.invalidateQueries({
          queryKey: [resource, id] as QueryKey,
          exact: true,
        });
      }
      break;

    case 'PARTIAL':
      queryClient.invalidateQueries({
        queryKey: [resource] as QueryKey,
      });
      break;

    case 'ALL':
      queryClient.invalidateQueries({
        predicate: (q) => Array.isArray(q.queryKey) && q.queryKey[0] === resource,
      });
      break;

    case 'RELATED':
      // Invalidate primary
      queryClient.invalidateQueries({
        queryKey: [resource] as QueryKey,
      });
      // Invalidate related
      if (relatedResources) {
        for (const related of relatedResources) {
          queryClient.invalidateQueries({
            queryKey: [related] as QueryKey,
          });
        }
      }
      break;

    case 'SELECTIVE':
      if (predicate) {
        queryClient.invalidateQueries({ predicate });
      }
      break;
  }

  if (process.env.NODE_ENV === 'development') {
    // eslint-disable-next-line no-console
    console.debug(
      `[Cache] Invalidated "${resource}" (strategy: ${strategy})`,
      id ? `id: ${id}` : ''
    );
  }
}

/**
 * Remove a specific resource entry from cache (hard delete).
 */
export function removeFromCache(
  queryClient: QueryClient,
  resource: string,
  id: string | number
): void {
  queryClient.removeQueries({
    queryKey: [resource, id] as QueryKey,
  });
}

/**
 * Get related resources for a given resource and action.
 */
export function getRelatedResources(
  resource: string,
  action: 'create' | 'update' | 'delete'
): string[] {
  return RELATED_RESOURCES[resource]?.[action] ?? [];
}
