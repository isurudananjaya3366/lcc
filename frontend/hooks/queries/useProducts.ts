/**
 * useProducts — fetch paginated product list
 */

import { useQuery } from '@tanstack/react-query';
import { productKeys } from '@/lib/queryKeys';
import type { ProductFilters } from '@/lib/queryKeys';
import { productService } from '@/services/api';

export function useProducts(filters?: ProductFilters) {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: () => productService.getProducts(filters),
    staleTime: 5 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}
