/**
 * Reports Types
 *
 * TypeScript types for reporting functionality including
 * report configurations, parameters, and result formats.
 */

// ── Enums ──────────────────────────────────────────────────────

export enum ReportType {
  SALES = 'SALES',
  INVENTORY = 'INVENTORY',
  CUSTOMERS = 'CUSTOMERS',
  VENDORS = 'VENDORS',
  HR = 'HR',
  FINANCIAL = 'FINANCIAL',
  CUSTOM = 'CUSTOM',
}

export enum ReportFormat {
  PDF = 'PDF',
  EXCEL = 'EXCEL',
  CSV = 'CSV',
  JSON = 'JSON',
}

export enum DateRangeType {
  TODAY = 'TODAY',
  YESTERDAY = 'YESTERDAY',
  THIS_WEEK = 'THIS_WEEK',
  LAST_WEEK = 'LAST_WEEK',
  THIS_MONTH = 'THIS_MONTH',
  LAST_MONTH = 'LAST_MONTH',
  THIS_QUARTER = 'THIS_QUARTER',
  LAST_QUARTER = 'LAST_QUARTER',
  THIS_YEAR = 'THIS_YEAR',
  LAST_YEAR = 'LAST_YEAR',
  CUSTOM = 'CUSTOM',
}

// ── Supporting Interfaces ──────────────────────────────────────

export interface ReportParameter {
  name: string;
  type: 'STRING' | 'NUMBER' | 'DATE' | 'BOOLEAN' | 'SELECT';
  label: string;
  required: boolean;
  defaultValue?: unknown;
  options?: { label: string; value: string }[];
}

export interface ReportConfig {
  id: string;
  name: string;
  description?: string;
  reportType: ReportType;
  parameters: ReportParameter[];
  isPublic: boolean;
  createdBy?: string;
}

export interface ChartData {
  chartType: 'BAR' | 'LINE' | 'PIE' | 'AREA';
  title: string;
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string;
  }[];
  xAxis?: string;
  yAxis?: string;
  legend?: boolean;
}

// ── Specific Report Interfaces ─────────────────────────────────

export interface SalesReport {
  period: { startDate: string; endDate: string };
  totalSales: number;
  totalOrders: number;
  averageOrderValue: number;
  salesByDay: { date: string; amount: number; orders: number }[];
  salesByProduct: { productId: string; productName: string; quantity: number; revenue: number }[];
  salesByCustomer: { customerId: string; customerName: string; orders: number; revenue: number }[];
  paymentMethodBreakdown: Record<string, number>;
  topProducts: { productId: string; productName: string; quantity: number; revenue: number }[];
}

export interface InventoryReport {
  totalProducts: number;
  totalValue: number;
  lowStockItems: number;
  stockByCategory: Record<string, { count: number; value: number }>;
  stockByWarehouse: Record<string, { count: number; value: number }>;
  topMovingProducts: { productId: string; productName: string; movementCount: number }[];
  slowMovingProducts: { productId: string; productName: string; lastMovementDate: string }[];
}

export interface CustomerReport {
  totalCustomers: number;
  newCustomers: number;
  activeCustomers: number;
  topCustomers: { customerId: string; customerName: string; totalSpent: number; orderCount: number }[];
  customersBySegment: Record<string, number>;
  averageLifetimeValue: number;
  retentionRate: number;
}

// ── API Request/Response Interfaces ────────────────────────────

export interface ReportRequest {
  reportId: string;
  parameters?: Record<string, unknown>;
  dateRange?: {
    startDate: string;
    endDate: string;
    rangeType: DateRangeType;
  };
  format?: ReportFormat;
  filters?: Record<string, unknown>;
}

export interface ReportResult {
  id: string;
  reportId: string;
  reportName: string;
  generatedAt: string;
  parameters: Record<string, unknown>;
  data: unknown;
  summary?: Record<string, number | string>;
  charts?: ChartData[];
  totalRecords: number;
  executionTime: number;
}
