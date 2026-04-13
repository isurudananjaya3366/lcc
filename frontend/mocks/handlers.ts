/**
 * MSW Request Handlers
 *
 * Mock API handlers for development and testing.
 */

import { http, HttpResponse, delay } from 'msw';
import {
  mockUsers,
  mockProducts,
  mockOrders,
  mockCategories,
  mockTokens,
  paginate,
} from './data';

const API_BASE = '/api/v1';

export const handlers = [
  // ── Auth ───────────────────────────────────────────────────
  http.post(`${API_BASE}/auth/login/`, async ({ request }) => {
    await delay(150);
    const body = (await request.json()) as Record<string, string>;
    if (body.email === 'admin@lankacommerce.com' && body.password === 'password') {
      return HttpResponse.json({
        data: { user: mockUsers[0], ...mockTokens },
        message: 'Login successful',
      });
    }
    return HttpResponse.json(
      { message: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  http.post(`${API_BASE}/auth/logout/`, async () => {
    await delay(50);
    return HttpResponse.json({ message: 'Logged out' });
  }),

  http.post(`${API_BASE}/auth/token/refresh/`, async () => {
    await delay(100);
    return HttpResponse.json({
      data: { accessToken: 'refreshed-access-token' },
    });
  }),

  http.get(`${API_BASE}/auth/me/`, async () => {
    await delay(80);
    return HttpResponse.json({ data: mockUsers[0] });
  }),

  // ── Products ───────────────────────────────────────────────
  http.get(`${API_BASE}/products/`, async ({ request }) => {
    await delay(120);
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10');
    return HttpResponse.json(paginate(mockProducts, page, pageSize));
  }),

  http.get(`${API_BASE}/products/:id/`, async ({ params }) => {
    await delay(80);
    const product = mockProducts.find((p) => p.id === params.id);
    if (!product)
      return HttpResponse.json({ message: 'Not found' }, { status: 404 });
    return HttpResponse.json({ data: product });
  }),

  http.post(`${API_BASE}/products/`, async ({ request }) => {
    await delay(200);
    const body = await request.json();
    return HttpResponse.json(
      { data: { id: crypto.randomUUID(), ...body, createdAt: new Date().toISOString() } },
      { status: 201 }
    );
  }),

  http.patch(`${API_BASE}/products/:id/`, async ({ params, request }) => {
    await delay(150);
    const body = await request.json();
    const product = mockProducts.find((p) => p.id === params.id);
    if (!product)
      return HttpResponse.json({ message: 'Not found' }, { status: 404 });
    return HttpResponse.json({ data: { ...product, ...body } });
  }),

  http.delete(`${API_BASE}/products/:id/`, async ({ params }) => {
    await delay(100);
    const product = mockProducts.find((p) => p.id === params.id);
    if (!product)
      return HttpResponse.json({ message: 'Not found' }, { status: 404 });
    return HttpResponse.json({ message: 'Deleted' });
  }),

  // ── Categories ─────────────────────────────────────────────
  http.get(`${API_BASE}/categories/`, async () => {
    await delay(80);
    return HttpResponse.json(paginate(mockCategories, 1, 50));
  }),

  http.get(`${API_BASE}/categories/tree/`, async () => {
    await delay(80);
    return HttpResponse.json({ data: mockCategories });
  }),

  // ── Orders ─────────────────────────────────────────────────
  http.get(`${API_BASE}/orders/`, async ({ request }) => {
    await delay(120);
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const pageSize = parseInt(url.searchParams.get('pageSize') || '10');
    return HttpResponse.json(paginate(mockOrders, page, pageSize));
  }),

  http.get(`${API_BASE}/orders/:id/`, async ({ params }) => {
    await delay(80);
    const order = mockOrders.find((o) => o.id === params.id);
    if (!order)
      return HttpResponse.json({ message: 'Not found' }, { status: 404 });
    return HttpResponse.json({ data: order });
  }),

  http.post(`${API_BASE}/orders/`, async ({ request }) => {
    await delay(300);
    const body = await request.json();
    return HttpResponse.json(
      {
        data: {
          id: crypto.randomUUID(),
          orderNumber: `ORD-2025-${String(mockOrders.length + 1).padStart(4, '0')}`,
          status: 'pending',
          ...body,
          createdAt: new Date().toISOString(),
        },
      },
      { status: 201 }
    );
  }),

  // ── Inventory ──────────────────────────────────────────────
  http.get(`${API_BASE}/inventory/stock-levels/`, async () => {
    await delay(100);
    const levels = mockProducts.map((p) => ({
      productId: p.id,
      productName: p.name,
      sku: p.sku,
      quantity: p.stock,
      warehouseId: 'wh-1',
    }));
    return HttpResponse.json(paginate(levels, 1, 50));
  }),

  http.get(`${API_BASE}/inventory/low-stock/`, async () => {
    await delay(100);
    const lowStock = mockProducts
      .filter((p) => p.stock < 10)
      .map((p) => ({
        productId: p.id,
        productName: p.name,
        currentStock: p.stock,
        reorderLevel: 20,
      }));
    return HttpResponse.json({ data: lowStock });
  }),

  // ── Reports ────────────────────────────────────────────────
  http.get(`${API_BASE}/reports/dashboard/`, async () => {
    await delay(200);
    return HttpResponse.json({
      data: {
        totalSales: 31860.0,
        totalOrders: 2,
        averageOrderValue: 15930.0,
        topProducts: mockProducts.slice(0, 3).map((p) => ({
          productId: p.id,
          name: p.name,
          quantity: Math.floor(Math.random() * 100),
          revenue: Math.floor(Math.random() * 50000),
        })),
        recentOrders: mockOrders.map((o) => ({
          id: o.id,
          orderNumber: o.orderNumber,
          total: o.total,
          createdAt: o.createdAt,
        })),
        charts: [],
      },
    });
  }),

  // ── Settings ───────────────────────────────────────────────
  http.get(`${API_BASE}/settings/`, async () => {
    await delay(80);
    return HttpResponse.json({
      data: {
        tenantId: 'tenant-1',
        tenantName: 'LankaCommerce Demo',
        settings: [
          { key: 'currency', value: 'LKR', category: 'localization', label: 'Currency', type: 'string', isEditable: true },
          { key: 'timezone', value: 'Asia/Colombo', category: 'localization', label: 'Timezone', type: 'string', isEditable: true },
          { key: 'tax_rate', value: 8, category: 'billing', label: 'Default Tax Rate', type: 'number', isEditable: true },
        ],
        updatedAt: '2025-03-01T00:00:00Z',
      },
    });
  }),
];
