/**
 * Infinite Customers Query
 *
 * Uses TanStack Query's `useInfiniteQuery` for cursor /
 * offset-based pagination of large customer lists.
 */

import { useInfiniteQuery } from '@tanstack/react-query';
import { customerService } from '@/services/api/customerService';
import { customerKeys } from '@/lib/queryKeys';
import type { CustomerFilters } from '@/lib/queryKeys';

const PAGE_SIZE = 20;

export function useInfiniteCustomers(filters?: CustomerFilters) {
  return useInfiniteQuery({
    queryKey: [...customerKeys.list(filters ?? {}), 'infinite'],
    queryFn: ({ pageParam = 1 }) =>
      customerService.getCustomers({
        ...filters,
        page: pageParam as number,
        page_size: PAGE_SIZE,
      }),
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.length * PAGE_SIZE;
      return loaded < lastPage.count ? allPages.length + 1 : undefined;
    },
    initialPageParam: 1,
    staleTime: 3 * 60 * 1000,
  });
}
