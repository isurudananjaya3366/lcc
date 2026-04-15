/**
 * useStockMovements — fetch paginated stock movement history
 */

import { useQuery } from '@tanstack/react-query';
import { inventoryKeys } from '@/lib/queryKeys';
import inventoryService from '@/services/api/inventoryService';

interface MovementFilters {
  productId?: string;
  warehouseId?: string;
  movementType?: 'all' | 'in' | 'out' | 'adjustment' | 'transfer';
  startDate?: string;
  endDate?: string;
  page?: number;
  limit?: number;
}

export type { MovementFilters };

export function useStockMovements(filters?: MovementFilters) {
  return useQuery({
    queryKey: inventoryKeys.movements(),
    queryFn: () =>
      inventoryService.getStockMovements(
        filters as Parameters<typeof inventoryService.getStockMovements>[0]
      ),
    staleTime: 1 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}
