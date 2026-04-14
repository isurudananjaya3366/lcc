/**
 * useEmployee — fetch a single employee by ID
 */

import { useQuery } from '@tanstack/react-query';
import { hrKeys } from '@/lib/queryKeys';
import { employeeService } from '@/services/api';

export function useEmployee(
  id: string,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: hrKeys.detail(id),
    queryFn: () => employeeService.getEmployeeById(id),
    staleTime: 15 * 60 * 1000,
    enabled: (options?.enabled ?? true) && !!id,
    retry: 2,
  });
}
