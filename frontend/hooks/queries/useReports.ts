/**
 * useReports — generate and fetch a report
 */

import { useQuery } from '@tanstack/react-query';
import reportsService from '@/services/api/reportsService';
import { DateRangeType } from '@/types/reports';

interface ReportFilters {
  dateRange: { startDate: string; endDate: string };
  groupBy?: 'day' | 'week' | 'month' | 'quarter' | 'year';
  format?: 'table' | 'chart' | 'summary';
  includeChartData?: boolean;
  filters?: Record<string, unknown>;
}

export type { ReportFilters };

type ReportType = 'sales' | 'inventory' | 'financial' | 'customer' | 'custom';

export function useReports(reportType: ReportType, filters: ReportFilters) {
  return useQuery({
    queryKey: ['reports', reportType, filters] as const,
    queryFn: () =>
      reportsService.generateReport({
        reportId: reportType,
        dateRange: {
          startDate: filters.dateRange.startDate,
          endDate: filters.dateRange.endDate,
          rangeType: DateRangeType.CUSTOM,
        },
        ...(filters.groupBy ? { parameters: { groupBy: filters.groupBy } } : {}),
        ...filters.filters,
      }),
    staleTime: 5 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}
