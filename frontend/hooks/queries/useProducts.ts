/**
 * useProducts — fetch paginated product list
 */

import { useQuery } from '@tanstack/react-query';
import { productKeys } from '@/lib/queryKeys';
import type { ProductFilters } from '@/lib/queryKeys';
import productService from '@/services/api/productService';

export function useProducts(filters?: ProductFilters) {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: () =>
      productService.getProducts(filters as Parameters<typeof productService.getProducts>[0]),
    staleTime: 5 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}
