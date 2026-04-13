/**
 * Reports Service
 *
 * Type-safe operations for generating, exporting, and retrieving
 * business reports — sales, inventory, customer, P&L, and dashboard.
 */

import { apiClient } from './apiClient';
import type { APIResponse } from '@/types/api';
import type {
  ReportConfig,
  ReportRequest,
  ReportResult,
  SalesReport,
  InventoryReport,
  CustomerReport,
  ReportFormat,
  ChartData,
} from '@/types/reports';

const REPORTS_ENDPOINT = '/api/v1/reports';

async function getReportConfigs(): Promise<APIResponse<ReportConfig[]>> {
  const { data } = await apiClient.get(`${REPORTS_ENDPOINT}/configs/`);
  return data;
}

async function generateReport(
  request: ReportRequest
): Promise<APIResponse<ReportResult>> {
  const { data } = await apiClient.post(`${REPORTS_ENDPOINT}/generate/`, request);
  return data;
}

async function exportReport(
  request: ReportRequest & { format: ReportFormat }
): Promise<Blob> {
  const { data } = await apiClient.post(`${REPORTS_ENDPOINT}/export/`, request, {
    responseType: 'blob',
  });
  return data;
}

async function getSalesReport(params: {
  startDate: string;
  endDate: string;
  groupBy?: 'day' | 'week' | 'month';
}): Promise<APIResponse<SalesReport>> {
  const { data } = await apiClient.get(`${REPORTS_ENDPOINT}/sales/`, { params });
  return data;
}

async function getInventoryReport(): Promise<APIResponse<InventoryReport>> {
  const { data } = await apiClient.get(`${REPORTS_ENDPOINT}/inventory/`);
  return data;
}

async function getCustomerReport(params: {
  startDate: string;
  endDate: string;
}): Promise<APIResponse<CustomerReport>> {
  const { data } = await apiClient.get(`${REPORTS_ENDPOINT}/customers/`, {
    params,
  });
  return data;
}

async function getDashboardData(params?: {
  period?: string;
}): Promise<
  APIResponse<{
    totalSales: number;
    totalOrders: number;
    averageOrderValue: number;
    topProducts: { productId: string; name: string; quantity: number; revenue: number }[];
    recentOrders: { id: string; orderNumber: string; total: number; createdAt: string }[];
    charts: ChartData[];
  }>
> {
  const { data } = await apiClient.get(`${REPORTS_ENDPOINT}/dashboard/`, {
    params,
  });
  return data;
}

async function getProfitAndLoss(params: {
  startDate: string;
  endDate: string;
}): Promise<
  APIResponse<{
    revenue: number;
    costOfGoods: number;
    grossProfit: number;
    expenses: { category: string; amount: number }[];
    netProfit: number;
    margin: number;
  }>
> {
  const { data } = await apiClient.get(`${REPORTS_ENDPOINT}/profit-loss/`, {
    params,
  });
  return data;
}

async function getTopProducts(params: {
  startDate: string;
  endDate: string;
  limit?: number;
}): Promise<
  APIResponse<
    { productId: string; name: string; sku: string; quantitySold: number; revenue: number }[]
  >
> {
  const { data } = await apiClient.get(`${REPORTS_ENDPOINT}/top-products/`, {
    params,
  });
  return data;
}

const reportsService = {
  getReportConfigs,
  generateReport,
  exportReport,
  getSalesReport,
  getInventoryReport,
  getCustomerReport,
  getDashboardData,
  getProfitAndLoss,
  getTopProducts,
};

export default reportsService;
