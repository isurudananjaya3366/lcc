/**
 * Infinite Orders Query
 *
 * Uses TanStack Query's `useInfiniteQuery` for cursor /
 * offset-based pagination of large order lists.
 */

import { useInfiniteQuery } from '@tanstack/react-query';
import salesService from '@/services/api/salesService';
import { salesKeys } from '@/lib/queryKeys';
import type { OrderSearchParams } from '@/types/sales';

const PAGE_SIZE = 20;

export function useInfiniteOrders(filters?: Partial<OrderSearchParams>) {
  return useInfiniteQuery({
    queryKey: [...salesKeys.list(), 'infinite', filters],
    queryFn: ({ pageParam = 1 }) =>
      salesService.getOrders({
        ...filters,
        page: pageParam as number,
        pageSize: PAGE_SIZE,
      }),
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.length * PAGE_SIZE;
      return loaded < lastPage.pagination.totalCount ? allPages.length + 1 : undefined;
    },
    initialPageParam: 1,
    staleTime: 1 * 60 * 1000,
  });
}
