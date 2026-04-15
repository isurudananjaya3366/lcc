/**
 * Query Key Factories
 *
 * Structured query-key factories for every domain module.
 * Using the factory pattern ensures consistent cache
 * invalidation and query matching.
 *
 * @see https://tkdodo.eu/blog/effective-react-query-keys
 */

// ── Filter Interfaces ──────────────────────────────────────────

export interface ProductFilters {
  category?: string;
  status?: string;
  search?: string;
  minPrice?: number;
  maxPrice?: number;
  inStock?: boolean;
  tags?: string[];
}

export interface InventoryFilters {
  warehouse?: string;
  product?: string;
  status?: string;
  category?: string;
  location?: string;
  threshold?: number;
}

export interface CustomerFilters {
  status?: string;
  type?: string;
  search?: string;
  country?: string;
  loyaltyTier?: string;
  hasOrders?: boolean;
  dateJoined?: string;
}

export interface SalesFilters {
  status?: string;
  paymentStatus?: string;
  dateFrom?: string;
  dateTo?: string;
  customer?: string;
  cashier?: string;
  minAmount?: number;
  maxAmount?: number;
  paymentMethod?: string;
}

export interface HRFilters {
  department?: string;
  role?: string;
  status?: string;
  search?: string;
  manager?: string;
  location?: string;
  employmentType?: string;
  hireDate?: string;
}

// ── Product Keys ───────────────────────────────────────────────

export const productKeys = {
  all: () => ['products'] as const,
  lists: () => ['products', 'list'] as const,
  list: (filters?: ProductFilters) => ['products', 'list', filters] as const,
  details: () => ['products', 'detail'] as const,
  detail: (id: string | number) => ['products', 'detail', id] as const,
  categories: () => ['products', 'categories'] as const,
  variants: (productId: string | number) => ['products', 'variants', productId] as const,
  stock: (productId: string | number) => ['products', 'stock', productId] as const,
  pricing: (productId: string | number) => ['products', 'pricing', productId] as const,
};

// ── Inventory Keys ─────────────────────────────────────────────

export const inventoryKeys = {
  all: () => ['inventory'] as const,
  lists: () => ['inventory', 'list'] as const,
  list: (filters?: InventoryFilters) => ['inventory', 'list', filters] as const,
  details: () => ['inventory', 'detail'] as const,
  detail: (id: string | number) => ['inventory', 'detail', id] as const,
  stockLevels: () => ['inventory', 'stockLevels'] as const,
  stockLevel: (productId: string | number, warehouseId: string | number) =>
    ['inventory', 'stockLevel', productId, warehouseId] as const,
  movements: () => ['inventory', 'movements'] as const,
  movement: (id: string | number) => ['inventory', 'movement', id] as const,
  warehouses: () => ['inventory', 'warehouses'] as const,
  warehouse: (id: string | number) => ['inventory', 'warehouse', id] as const,
  lowStock: () => ['inventory', 'lowStock'] as const,
};

// ── Customer Keys ──────────────────────────────────────────────

export const customerKeys = {
  all: () => ['customers'] as const,
  lists: () => ['customers', 'list'] as const,
  list: (filters?: CustomerFilters) => ['customers', 'list', filters] as const,
  details: () => ['customers', 'detail'] as const,
  detail: (id: string | number) => ['customers', 'detail', id] as const,
  addresses: (customerId: string | number) => ['customers', 'addresses', customerId] as const,
  address: (addressId: string | number) => ['customers', 'address', addressId] as const,
  orders: (customerId: string | number) => ['customers', 'orders', customerId] as const,
  paymentMethods: (customerId: string | number) =>
    ['customers', 'paymentMethods', customerId] as const,
  paymentMethod: (id: string | number) => ['customers', 'paymentMethod', id] as const,
  loyaltyPoints: (customerId: string | number) =>
    ['customers', 'loyaltyPoints', customerId] as const,
};

// ── Sales Keys ─────────────────────────────────────────────────

export const salesKeys = {
  all: () => ['sales'] as const,
  lists: () => ['sales', 'list'] as const,
  list: (filters?: SalesFilters) => ['sales', 'list', filters] as const,
  details: () => ['sales', 'detail'] as const,
  detail: (id: string | number) => ['sales', 'detail', id] as const,
  orders: () => ['sales', 'orders'] as const,
  order: (id: string | number) => ['sales', 'order', id] as const,
  invoices: () => ['sales', 'invoices'] as const,
  invoice: (id: string | number) => ['sales', 'invoice', id] as const,
  payments: () => ['sales', 'payments'] as const,
  payment: (id: string | number) => ['sales', 'payment', id] as const,
  refunds: () => ['sales', 'refunds'] as const,
  refund: (id: string | number) => ['sales', 'refund', id] as const,
  quotes: () => ['sales', 'quotes'] as const,
  quote: (id: string | number) => ['sales', 'quote', id] as const,
  analytics: (range: string) => ['sales', 'analytics', range] as const,
  dailySummary: (date: string) => ['sales', 'dailySummary', date] as const,
};

// ── HR Keys ────────────────────────────────────────────────────

export const hrKeys = {
  all: () => ['hr'] as const,
  lists: () => ['hr', 'list'] as const,
  list: (filters?: HRFilters) => ['hr', 'list', filters] as const,
  details: () => ['hr', 'detail'] as const,
  detail: (id: string | number) => ['hr', 'detail', id] as const,
  employees: () => ['hr', 'employees'] as const,
  employee: (id: string | number) => ['hr', 'employee', id] as const,
  schedules: () => ['hr', 'schedules'] as const,
  schedule: (id: string | number) => ['hr', 'schedule', id] as const,
  attendance: () => ['hr', 'attendance'] as const,
  attendanceRecord: (id: string | number) => ['hr', 'attendanceRecord', id] as const,
  leaves: () => ['hr', 'leaves'] as const,
  leave: (id: string | number) => ['hr', 'leave', id] as const,
  payroll: (period: string) => ['hr', 'payroll', period] as const,
  performance: (employeeId: string | number) => ['hr', 'performance', employeeId] as const,
};

// ── Vendor Keys ────────────────────────────────────────────────

export interface VendorFilters {
  status?: string;
  category?: string;
  search?: string;
  vendorType?: string;
}

export const vendorKeys = {
  all: () => ['vendors'] as const,
  lists: () => ['vendors', 'list'] as const,
  list: (filters?: VendorFilters) => ['vendors', 'list', filters] as const,
  details: () => ['vendors', 'detail'] as const,
  detail: (id: string | number) => ['vendors', 'detail', id] as const,
  contacts: (vendorId: string | number) => ['vendors', 'contacts', vendorId] as const,
  products: (vendorId: string | number) => ['vendors', 'products', vendorId] as const,
  purchaseOrders: (vendorId: string | number) => ['vendors', 'purchaseOrders', vendorId] as const,
  performance: (vendorId: string | number) => ['vendors', 'performance', vendorId] as const,
  stats: () => ['vendors', 'stats'] as const,
};

// ── Purchase Order Keys ────────────────────────────────────────

export interface POFilters {
  status?: string;
  vendorId?: string;
  search?: string;
  startDate?: string;
  endDate?: string;
}

export const purchaseOrderKeys = {
  all: () => ['purchaseOrders'] as const,
  lists: () => ['purchaseOrders', 'list'] as const,
  list: (filters?: POFilters) => ['purchaseOrders', 'list', filters] as const,
  details: () => ['purchaseOrders', 'detail'] as const,
  detail: (id: string | number) => ['purchaseOrders', 'detail', id] as const,
};

// ── Aggregate Export ───────────────────────────────────────────

export const queryKeys = {
  products: productKeys,
  inventory: inventoryKeys,
  customers: customerKeys,
  sales: salesKeys,
  hr: hrKeys,
  vendors: vendorKeys,
  purchaseOrders: purchaseOrderKeys,
};
