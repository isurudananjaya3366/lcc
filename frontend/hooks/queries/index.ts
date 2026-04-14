/**
 * Query Hooks — Barrel Export
 *
 * All TanStack React Query hooks for data fetching,
 * organised by domain module.
 */

// ── Products ───────────────────────────────────────────────────
export { useProducts } from './useProducts';
export { useProduct } from './useProduct';
export { useCategories } from './useCategories';
export type { CategoryFilters } from './useCategories';

// ── Inventory ──────────────────────────────────────────────────
export { useInventory } from './useInventory';
export { useWarehouses } from './useWarehouses';
export type { WarehouseFilters } from './useWarehouses';
export { useStockMovements } from './useStockMovements';
export type { MovementFilters } from './useStockMovements';

// ── Customers ──────────────────────────────────────────────────
export { useCustomers } from './useCustomers';
export { useCustomer } from './useCustomer';

// ── Vendors ────────────────────────────────────────────────────
export { useVendors } from './useVendors';
export type { VendorFilters } from './useVendors';

// ── Sales / Orders ─────────────────────────────────────────────
export { useOrders } from './useOrders';
export { useOrder } from './useOrder';

// ── Invoices ───────────────────────────────────────────────────
export { useInvoices } from './useInvoices';
export type { InvoiceFilters } from './useInvoices';

// ── HR ─────────────────────────────────────────────────────────
export { useEmployees } from './useEmployees';
export { useEmployee } from './useEmployee';
export { useAttendance } from './useAttendance';
export type { AttendanceFilters } from './useAttendance';

// ── Dashboard & Reports ────────────────────────────────────────
export { useDashboardStats } from './useDashboardStats';
export type { StatsFilters } from './useDashboardStats';
export { useReports } from './useReports';
export type { ReportFilters } from './useReports';
