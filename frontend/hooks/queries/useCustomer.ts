/**
 * useCustomer — fetch a single customer by ID
 */

import { useQuery } from '@tanstack/react-query';
import { customerKeys } from '@/lib/queryKeys';
import customerService from '@/services/api/customerService';

export function useCustomer(
  id: string,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: customerKeys.detail(id),
    queryFn: () => customerService.getCustomerById(id),
    staleTime: 5 * 60 * 1000,
    enabled: (options?.enabled ?? true) && !!id,
    retry: 2,
  });
}
