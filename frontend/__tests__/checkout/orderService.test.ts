/**
 * Order Service Tests — Task 94 (Unit Testing Suite) + Task 95 (Integration Testing)
 *
 * Tests the orderService API functions using MSW to mock HTTP requests.
 * Covers: submitOrder, getOrderStatus, cartItemsToOrderLines
 */

import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { http, HttpResponse } from 'msw';
import { server } from '@/mocks/server';
import {
  submitOrder,
  getOrderStatus,
  cartItemsToOrderLines,
  type OrderSubmitPayload,
} from '@/services/storefront/orderService';
import type { StoreCartItem } from '@/stores/store';

// ─── MSW Lifecycle ────────────────────────────────────────────────────────────

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// ─── Test Fixtures ────────────────────────────────────────────────────────────

const mockPayload: OrderSubmitPayload = {
  contactInfo: {
    email: 'kasun@example.com',
    phone: '771234567',
    firstName: 'Kasun',
    lastName: 'Perera',
  },
  shippingAddress: {
    province: 'Western Province',
    district: 'Colombo',
    city: 'Colombo 03',
    address1: '123 Galle Road',
    address2: 'Apt 4B',
    landmark: 'Near Cinnamon Grand',
    postalCode: '00300',
  },
  shippingMethodId: 'standard',
  paymentMethod: 'cod',
  items: [
    {
      productId: 'prod-001',
      name: 'Test Product',
      sku: 'SKU-001',
      price: 1500,
      quantity: 2,
      variant: null,
    },
  ],
};

const mockConfirmation = {
  orderId: '550e8400-e29b-41d4-a716-446655440000',
  orderNumber: 'LCC-2026-00001',
  status: 'pending',
  total: 3000,
  currency: 'LKR',
  estimatedDelivery: '2026-04-23',
  createdAt: '2026-04-18T10:00:00Z',
};

// ─── cartItemsToOrderLines Tests ──────────────────────────────────────────────

describe('cartItemsToOrderLines', () => {
  const mockCartItems: StoreCartItem[] = [
    {
      productId: 'prod-001',
      name: 'Test Product A',
      sku: 'SKU-A',
      price: 1500,
      quantity: 2,
      image: '/img/a.jpg',
      slug: 'test-product-a',
      variant: { size: 'L', color: 'Blue' },
    },
    {
      productId: 'prod-002',
      name: 'Test Product B',
      sku: 'SKU-B',
      price: 2500,
      quantity: 1,
      image: '/img/b.jpg',
      slug: 'test-product-b',
      variant: null,
    },
  ];

  it('converts cart items to order line format', () => {
    const lines = cartItemsToOrderLines(mockCartItems);
    expect(lines).toHaveLength(2);
  });

  it('maps productId correctly', () => {
    const lines = cartItemsToOrderLines(mockCartItems);
    expect(lines[0]!.productId).toBe('prod-001');
    expect(lines[1]!.productId).toBe('prod-002');
  });

  it('maps name correctly', () => {
    const lines = cartItemsToOrderLines(mockCartItems);
    expect(lines[0]!.name).toBe('Test Product A');
  });

  it('maps sku correctly', () => {
    const lines = cartItemsToOrderLines(mockCartItems);
    expect(lines[0]!.sku).toBe('SKU-A');
  });

  it('maps price correctly', () => {
    const lines = cartItemsToOrderLines(mockCartItems);
    expect(lines[0]!.price).toBe(1500);
  });

  it('maps quantity correctly', () => {
    const lines = cartItemsToOrderLines(mockCartItems);
    expect(lines[0]!.quantity).toBe(2);
  });

  it('maps variant correctly', () => {
    const lines = cartItemsToOrderLines(mockCartItems);
    expect(lines[0]!.variant).toEqual({ size: 'L', color: 'Blue' });
    expect(lines[1]!.variant).toBeNull();
  });

  it('returns empty array for empty cart', () => {
    const lines = cartItemsToOrderLines([]);
    expect(lines).toHaveLength(0);
  });
});

// ─── submitOrder Tests ────────────────────────────────────────────────────────

describe('submitOrder', () => {
  it('returns order confirmation on success', async () => {
    server.use(
      http.post('*/api/v1/store/orders/', () => {
        return HttpResponse.json(mockConfirmation, { status: 201 });
      })
    );

    const result = await submitOrder(mockPayload);
    expect(result.orderId).toBe(mockConfirmation.orderId);
    expect(result.orderNumber).toBe('LCC-2026-00001');
    expect(result.status).toBe('pending');
    expect(result.currency).toBe('LKR');
  });

  it('throws on 400 bad request', async () => {
    server.use(
      http.post('*/api/v1/store/orders/', () => {
        return HttpResponse.json({ detail: 'Invalid order data' }, { status: 400 });
      })
    );

    await expect(submitOrder(mockPayload)).rejects.toThrow('Invalid order data');
  });

  it('throws on 500 server error', async () => {
    server.use(
      http.post('*/api/v1/store/orders/', () => {
        return HttpResponse.json({}, { status: 500 });
      })
    );

    await expect(submitOrder(mockPayload)).rejects.toThrow('Order submission failed (500)');
  });

  it('sends correct payload structure', async () => {
    let capturedBody: unknown = null;

    server.use(
      http.post('*/api/v1/store/orders/', async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json(mockConfirmation, { status: 201 });
      })
    );

    await submitOrder(mockPayload);

    expect(capturedBody).toMatchObject({
      contactInfo: expect.objectContaining({
        email: 'kasun@example.com',
        firstName: 'Kasun',
      }),
      paymentMethod: 'cod',
      shippingMethodId: 'standard',
    });
  });

  it('sends items array in payload', async () => {
    let capturedBody: unknown = null;

    server.use(
      http.post('*/api/v1/store/orders/', async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json(mockConfirmation, { status: 201 });
      })
    );

    await submitOrder(mockPayload);

    expect(capturedBody).toMatchObject({
      items: expect.arrayContaining([expect.objectContaining({ sku: 'SKU-001', quantity: 2 })]),
    });
  });
});

// ─── getOrderStatus Tests ──────────────────────────────────────────────────────

describe('getOrderStatus', () => {
  it('returns order status on success', async () => {
    const mockStatus = {
      orderId: '550e8400-e29b-41d4-a716-446655440000',
      orderNumber: 'LCC-2026-00001',
      status: 'confirmed',
      updatedAt: '2026-04-18T11:00:00Z',
    };

    server.use(
      http.get('*/api/v1/store/orders/*/status/', () => {
        return HttpResponse.json(mockStatus);
      })
    );

    const result = await getOrderStatus('550e8400-e29b-41d4-a716-446655440000');
    expect(result.status).toBe('confirmed');
    expect(result.orderNumber).toBe('LCC-2026-00001');
  });

  it('throws on 404 not found', async () => {
    server.use(
      http.get('*/api/v1/store/orders/*/status/', () => {
        return HttpResponse.json({ detail: 'Order not found' }, { status: 404 });
      })
    );

    await expect(getOrderStatus('non-existent-id')).rejects.toThrow('Order not found');
  });
});
