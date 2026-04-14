/**
 * useDashboardStats — fetch dashboard statistics
 */

import { useQuery } from '@tanstack/react-query';
import { reportsService } from '@/services/api';

interface StatsFilters {
  period?: 'today' | 'week' | 'month' | 'year';
  compareWithPrevious?: boolean;
  modules?: ('sales' | 'orders' | 'inventory' | 'customers' | 'financial')[];
  refreshInterval?: number;
}

export type { StatsFilters };

export function useDashboardStats(filters?: StatsFilters) {
  const interval = filters?.refreshInterval ?? 60_000;

  return useQuery({
    queryKey: ['dashboard', 'stats', filters] as const,
    queryFn: () =>
      reportsService.getDashboardData({
        period: filters?.period,
      }),
    staleTime: 1 * 60 * 1000,
    refetchInterval: interval,
    refetchOnWindowFocus: true,
  });
}
