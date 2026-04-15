/**
 * Infinite Customers Query
 *
 * Uses TanStack Query's `useInfiniteQuery` for cursor /
 * offset-based pagination of large customer lists.
 */

import { useInfiniteQuery } from '@tanstack/react-query';
import customerService from '@/services/api/customerService';
import { customerKeys } from '@/lib/queryKeys';
import type { CustomerSearchParams } from '@/types/customer';

const PAGE_SIZE = 20;

export function useInfiniteCustomers(filters?: Partial<CustomerSearchParams>) {
  return useInfiniteQuery({
    queryKey: [...customerKeys.list(), 'infinite', filters],
    queryFn: ({ pageParam = 1 }) =>
      customerService.getCustomers({
        ...filters,
        page: pageParam as number,
        pageSize: PAGE_SIZE,
      }),
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.length * PAGE_SIZE;
      return loaded < lastPage.pagination.totalCount ? allPages.length + 1 : undefined;
    },
    initialPageParam: 1,
    staleTime: 3 * 60 * 1000,
  });
}
