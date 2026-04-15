/**
 * useCategories — fetch product categories
 */

import { useQuery } from '@tanstack/react-query';
import { productKeys } from '@/lib/queryKeys';
import categoryService from '@/services/api/categoryService';

interface CategoryFilters {
  parentId?: string;
  includeInactive?: boolean;
  format?: 'flat' | 'tree';
  sortBy?: 'name' | 'order' | 'created';
}

export type { CategoryFilters };

export function useCategories(filters?: CategoryFilters) {
  const isTree = filters?.format === 'tree';

  return useQuery({
    queryKey: productKeys.categories(),
    queryFn: () =>
      (isTree
        ? categoryService.getCategoryTree()
        : categoryService.getCategories({
            parentId: filters?.parentId,
            includeInactive: filters?.includeInactive,
          })) as unknown as ReturnType<typeof categoryService.getCategoryTree>,
    staleTime: 30 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
    refetchOnMount: false,
  });
}
