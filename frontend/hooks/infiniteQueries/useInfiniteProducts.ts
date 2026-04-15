/**
 * Infinite Products Query
 *
 * Uses TanStack Query's `useInfiniteQuery` for cursor /
 * offset-based pagination of large product lists.
 */

import { useInfiniteQuery } from '@tanstack/react-query';
import productService from '@/services/api/productService';
import { productKeys } from '@/lib/queryKeys';
import type { ProductFilters } from '@/lib/queryKeys';

const PAGE_SIZE = 20;

export function useInfiniteProducts(filters?: ProductFilters) {
  return useInfiniteQuery({
    queryKey: [...productKeys.list(filters ?? {}), 'infinite'],
    queryFn: ({ pageParam = 1 }) =>
      productService.getProducts({
        ...filters,
        page: pageParam as number,
        pageSize: PAGE_SIZE,
      } as Parameters<typeof productService.getProducts>[0]),
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.length * PAGE_SIZE;
      return loaded < lastPage.pagination.totalCount ? allPages.length + 1 : undefined;
    },
    initialPageParam: 1,
    staleTime: 5 * 60 * 1000,
  });
}
