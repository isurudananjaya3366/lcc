/**
 * useEmployees — fetch paginated employee list
 */

import { useQuery } from '@tanstack/react-query';
import { hrKeys } from '@/lib/queryKeys';
import type { HRFilters } from '@/lib/queryKeys';
import { employeeService } from '@/services/api';

export function useEmployees(filters?: HRFilters) {
  return useQuery({
    queryKey: hrKeys.list(filters),
    queryFn: () => employeeService.getEmployees(filters),
    staleTime: 10 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: false,
  });
}
