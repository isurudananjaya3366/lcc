/**
 * Dashboard API Service — KPI, activity feed, and chart data endpoints.
 */

import apiClient from './apiClient';
import type { ActivityEvent } from '@/components/dashboard/ActivityFeed';

// ─── Response Types ─────────────────────────────────────────────

export interface KPIData {
  todaySales: number;
  yesterdaySales: number;
  todayOrders: number;
  yesterdayOrders: number;
  lowStockCount: number;
  criticalStockCount: number;
  pendingApprovals: number;
}

export interface SalesChartPoint {
  date: string;
  sales: number;
}

export interface DashboardActivityResponse {
  results: ActivityEvent[];
}

export interface DashboardChartResponse {
  results: SalesChartPoint[];
}

// ─── API Functions ──────────────────────────────────────────────

export async function fetchKPIs(): Promise<KPIData> {
  const { data } = await apiClient.get<KPIData>('/dashboard/kpis');
  return data;
}

export async function fetchActivityFeed(): Promise<ActivityEvent[]> {
  const { data } = await apiClient.get<DashboardActivityResponse>('/dashboard/activity');
  return data.results;
}

export async function fetchSalesChart(period: string = '7d'): Promise<SalesChartPoint[]> {
  const { data } = await apiClient.get<DashboardChartResponse>('/dashboard/sales-chart', {
    params: { period },
  });
  return data.results;
}
