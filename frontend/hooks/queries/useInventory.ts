/**
 * useInventory — fetch paginated inventory / stock levels
 */

import { useQuery } from '@tanstack/react-query';
import { inventoryKeys } from '@/lib/queryKeys';
import type { InventoryFilters } from '@/lib/queryKeys';
import inventoryService from '@/services/api/inventoryService';

export function useInventory(filters?: InventoryFilters) {
  return useQuery({
    queryKey: inventoryKeys.list(filters),
    queryFn: () =>
      inventoryService.getStockLevels(
        filters as Parameters<typeof inventoryService.getStockLevels>[0]
      ),
    staleTime: 2 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}
