/**
 * useOrder — fetch a single order by ID
 */

import { useQuery } from '@tanstack/react-query';
import { salesKeys } from '@/lib/queryKeys';
import { salesService } from '@/services/api';

export function useOrder(id: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: salesKeys.detail(id),
    queryFn: () => salesService.getOrderById(id),
    staleTime: 2 * 60 * 1000,
    enabled: (options?.enabled ?? true) && !!id,
    retry: 2,
  });
}
