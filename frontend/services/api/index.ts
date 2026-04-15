/**
 * API Service Index
 *
 * Central entry point for all API services, utilities, and types.
 * Import from '@/services/api' for clean, organized access.
 *
 * @example
 * import { apiClient, productService, salesService } from '@/services/api';
 * import type { Product, Order } from '@/services/api';
 */

// ── Core API Client ────────────────────────────────────────────
export { apiClient, createApiClient, DEFAULT_CONFIG } from './apiClient';

// ── Auth Service ───────────────────────────────────────────────
export { default as authService } from './authService';

// ── Module Services ────────────────────────────────────────────
export { default as productService } from './productService';
export { default as categoryService } from './categoryService';
export { default as inventoryService } from './inventoryService';
export { default as warehouseService } from './warehouseService';
export { default as customerService } from './customerService';
export { default as vendorService } from './vendorService';
export { default as salesService } from './salesService';
export { default as invoiceService } from './invoiceService';
export { default as employeeService } from './employeeService';
export { default as attendanceService } from './attendanceService';
export { default as payrollService } from './payrollService';
export { default as reportsService } from './reportsService';
export { default as settingsService } from './settingsService';

// ── Dashboard Service ──────────────────────────────────────────
export {
  fetchKPIs,
  fetchActivityFeed,
  fetchSalesChart,
  type KPIData,
  type SalesChartPoint,
} from './dashboardService';

// ── Interceptors ──────────────────────────────────────────────
export { requestInterceptor, requestErrorHandler } from './interceptors/request.interceptor';
export {
  responseSuccessHandler,
  createResponseErrorHandler,
} from './interceptors/response.interceptor';

// ── Re-export Types ────────────────────────────────────────────
export type {
  APIResponse,
  PaginatedResponse,
  APIError,
  RequestConfig,
  PaginationParams,
  SearchParams,
  FilterParams,
  SortConfig,
  SortDirection,
  APIErrorCode,
} from '@/types/api';

export type {
  User,
  LoginRequest,
  LoginResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  AuthResponse,
} from '@/types/auth';

export type {
  Product,
  ProductVariant,
  ProductCategory,
  ProductBrand,
  ProductCreateRequest,
  ProductUpdateRequest,
  ProductSearchParams,
} from '@/types/product';

export type {
  StockLevel,
  StockMovement,
  StockAdjustment,
  StockTransfer,
  Warehouse,
  WarehouseLocation,
  LowStockAlert,
  InventorySearchParams,
} from '@/types/inventory';

export type {
  Customer,
  CustomerCreateRequest,
  CustomerUpdateRequest,
  CustomerSearchParams,
} from '@/types/customer';

export type {
  Vendor,
  VendorCreateRequest,
  VendorUpdateRequest,
  VendorSearchParams,
  PurchaseOrder,
} from '@/types/vendor';

export type {
  Order,
  OrderItem,
  OrderCreateRequest,
  OrderUpdateRequest,
  OrderSearchParams,
  QuickSaleRequest,
} from '@/types/sales';

export type {
  Employee,
  EmployeeCreateRequest,
  EmployeeUpdateRequest,
  EmployeeSearchParams,
  Department,
  Position,
  Attendance,
  Payroll,
  PayrollItem,
  LeaveRequest,
} from '@/types/hr';

export type {
  ReportConfig,
  ReportRequest,
  ReportResult,
  SalesReport,
  InventoryReport,
  CustomerReport,
} from '@/types/reports';

// ── Re-export Utility Types ────────────────────────────────────
export type { InvoiceStatus, Invoice, InvoiceSearchParams } from './invoiceService';
