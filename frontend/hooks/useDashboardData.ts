'use client';

import { useQuery } from '@tanstack/react-query';
import {
  fetchKPIs,
  fetchActivityFeed,
  fetchSalesChart,
  type KPIData,
  type SalesChartPoint,
} from '@/services/api/dashboardService';
import type { ActivityEvent } from '@/components/dashboard/ActivityFeed';

// ─── Query Keys ─────────────────────────────────────────────────

export const dashboardKeys = {
  all: ['dashboard'] as const,
  kpis: () => [...dashboardKeys.all, 'kpis'] as const,
  activity: () => [...dashboardKeys.all, 'activity'] as const,
  salesChart: (period: string) => [...dashboardKeys.all, 'sales-chart', period] as const,
};

// ─── Hooks ──────────────────────────────────────────────────────

export function useKPIData() {
  return useQuery<KPIData>({
    queryKey: dashboardKeys.kpis(),
    queryFn: fetchKPIs,
    staleTime: 30_000, // 30 seconds
    refetchInterval: 60_000, // Auto-refresh every minute
  });
}

export function useActivityFeed() {
  return useQuery<ActivityEvent[]>({
    queryKey: dashboardKeys.activity(),
    queryFn: fetchActivityFeed,
    staleTime: 15_000, // 15 seconds
    refetchInterval: 30_000,
  });
}

export function useSalesChartData(period: string = '7d') {
  return useQuery<SalesChartPoint[]>({
    queryKey: dashboardKeys.salesChart(period),
    queryFn: () => fetchSalesChart(period),
    staleTime: 5 * 60_000, // 5 minutes
  });
}
