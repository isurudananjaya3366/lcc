/**
 * MSW Mock Data — Shared fixtures for development and testing.
 */

export const mockUsers = [
  {
    id: '1',
    email: 'admin@lankacommerce.com',
    firstName: 'Admin',
    lastName: 'User',
    role: 'admin',
    isActive: true,
    tenantId: 'tenant-1',
    createdAt: '2025-01-01T00:00:00Z',
  },
  {
    id: '2',
    email: 'manager@lankacommerce.com',
    firstName: 'Store',
    lastName: 'Manager',
    role: 'manager',
    isActive: true,
    tenantId: 'tenant-1',
    createdAt: '2025-01-15T00:00:00Z',
  },
  {
    id: '3',
    email: 'cashier@lankacommerce.com',
    firstName: 'POS',
    lastName: 'Cashier',
    role: 'cashier',
    isActive: true,
    tenantId: 'tenant-1',
    createdAt: '2025-02-01T00:00:00Z',
  },
];

export const mockProducts = [
  {
    id: '1',
    sku: 'TEA-001',
    barcode: '8901234567890',
    name: 'Ceylon Black Tea 500g',
    description: 'Premium Ceylon black tea',
    status: 'active',
    type: 'physical',
    price: 450.0,
    costPrice: 280.0,
    stock: 150,
    categoryId: '1',
    categoryName: 'Beverages',
    createdAt: '2025-01-10T00:00:00Z',
  },
  {
    id: '2',
    sku: 'RIC-001',
    barcode: '8901234567891',
    name: 'Samba Rice 5kg',
    description: 'Traditional Sri Lankan rice',
    status: 'active',
    type: 'physical',
    price: 1250.0,
    costPrice: 900.0,
    stock: 80,
    categoryId: '2',
    categoryName: 'Groceries',
    createdAt: '2025-01-12T00:00:00Z',
  },
  {
    id: '3',
    sku: 'COC-001',
    barcode: '8901234567892',
    name: 'Coconut Oil 750ml',
    description: 'Pure coconut oil',
    status: 'active',
    type: 'physical',
    price: 680.0,
    costPrice: 420.0,
    stock: 5,
    categoryId: '2',
    categoryName: 'Groceries',
    createdAt: '2025-01-15T00:00:00Z',
  },
];

export const mockOrders = [
  {
    id: '1',
    orderNumber: 'ORD-2025-0001',
    customerId: '1',
    customerName: 'Perera Stores',
    status: 'completed',
    paymentStatus: 'paid',
    items: [
      { id: '1', productId: '1', productName: 'Ceylon Black Tea 500g', quantity: 10, unitPrice: 450.0, total: 4500.0 },
    ],
    subtotal: 4500.0,
    taxTotal: 360.0,
    total: 4860.0,
    createdAt: '2025-03-01T10:00:00Z',
  },
  {
    id: '2',
    orderNumber: 'ORD-2025-0002',
    customerId: '2',
    customerName: 'Silva Mart',
    status: 'pending',
    paymentStatus: 'unpaid',
    items: [
      { id: '2', productId: '2', productName: 'Samba Rice 5kg', quantity: 20, unitPrice: 1250.0, total: 25000.0 },
    ],
    subtotal: 25000.0,
    taxTotal: 2000.0,
    total: 27000.0,
    createdAt: '2025-03-02T14:00:00Z',
  },
];

export const mockCategories = [
  { id: '1', name: 'Beverages', slug: 'beverages', parentId: null, productsCount: 15 },
  { id: '2', name: 'Groceries', slug: 'groceries', parentId: null, productsCount: 42 },
  { id: '3', name: 'Tea', slug: 'tea', parentId: '1', productsCount: 8 },
];

export const mockTokens = {
  accessToken: 'mock-access-token-jwt',
  refreshToken: 'mock-refresh-token-jwt',
};

export function paginate<T>(items: T[], page = 1, pageSize = 10) {
  const start = (page - 1) * pageSize;
  const data = items.slice(start, start + pageSize);
  return {
    data,
    pagination: {
      page,
      pageSize,
      totalPages: Math.ceil(items.length / pageSize),
      totalCount: items.length,
      hasNext: start + pageSize < items.length,
      hasPrevious: page > 1,
    },
  };
}
