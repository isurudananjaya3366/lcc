/**
 * useCustomers — fetch paginated customer list
 */

import { useQuery } from '@tanstack/react-query';
import { customerKeys } from '@/lib/queryKeys';
import type { CustomerFilters } from '@/lib/queryKeys';
import customerService from '@/services/api/customerService';

export function useCustomers(filters?: CustomerFilters) {
  return useQuery({
    queryKey: customerKeys.list(filters),
    queryFn: () =>
      customerService.getCustomers(filters as Parameters<typeof customerService.getCustomers>[0]),
    staleTime: 3 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}
