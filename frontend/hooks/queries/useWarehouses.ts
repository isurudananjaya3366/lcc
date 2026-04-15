/**
 * useWarehouses — fetch warehouse list
 */

import { useQuery } from '@tanstack/react-query';
import { inventoryKeys } from '@/lib/queryKeys';
import warehouseService from '@/services/api/warehouseService';

interface WarehouseFilters {
  status?: 'all' | 'active' | 'inactive';
  type?: 'warehouse' | 'retail' | 'all';
  includeStats?: boolean;
}

export type { WarehouseFilters };

export function useWarehouses(filters?: WarehouseFilters) {
  return useQuery({
    queryKey: inventoryKeys.warehouses(),
    queryFn: () =>
      warehouseService.getWarehouses(filters?.status !== 'active'),
    staleTime: 15 * 60 * 1000,
    refetchOnMount: false,
  });
}
