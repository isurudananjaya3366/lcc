/**
 * useProduct — fetch a single product by ID
 */

import { useQuery } from '@tanstack/react-query';
import { productKeys } from '@/lib/queryKeys';
import { productService } from '@/services/api';

export function useProduct(
  id: string,
  options?: { enabled?: boolean; staleTime?: number; retry?: number },
) {
  return useQuery({
    queryKey: productKeys.detail(id),
    queryFn: () => productService.getProductById(id),
    staleTime: options?.staleTime ?? 10 * 60 * 1000,
    enabled: (options?.enabled ?? true) && !!id,
    retry: options?.retry ?? 2,
  });
}
