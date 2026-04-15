/**
 * useOrders — fetch paginated order list
 */

import { useQuery } from '@tanstack/react-query';
import { salesKeys } from '@/lib/queryKeys';
import type { SalesFilters } from '@/lib/queryKeys';
import salesService from '@/services/api/salesService';

export function useOrders(filters?: SalesFilters) {
  return useQuery({
    queryKey: salesKeys.list(filters),
    queryFn: () => salesService.getOrders(filters as Parameters<typeof salesService.getOrders>[0]),
    staleTime: 1 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}
