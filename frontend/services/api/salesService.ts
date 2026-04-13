/**
 * Sales / Order Service
 *
 * Type-safe CRUD operations for orders, order items, discounts,
 * payments, shipments, and quick sale flow.
 */

import { apiClient } from './apiClient';
import type { APIResponse, PaginatedResponse } from '@/types/api';
import type {
  Order,
  OrderCreateRequest,
  OrderUpdateRequest,
  OrderSearchParams,
  OrderItem,
  OrderDiscount,
  OrderPayment,
  OrderShipment,
  OrderNote,
  OrderSummary,
  QuickSaleRequest,
} from '@/types/sales';

const ORDER_ENDPOINT = '/api/v1/orders';

// ── Order CRUD ─────────────────────────────────────────────────

async function getOrders(
  params?: OrderSearchParams
): Promise<PaginatedResponse<Order>> {
  const { data } = await apiClient.get(`${ORDER_ENDPOINT}/`, { params });
  return data;
}

async function getOrderById(id: string): Promise<APIResponse<Order>> {
  const { data } = await apiClient.get(`${ORDER_ENDPOINT}/${id}/`);
  return data;
}

async function getOrderByNumber(
  orderNumber: string
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.get(
    `${ORDER_ENDPOINT}/by-number/${orderNumber}/`
  );
  return data;
}

async function createOrder(
  orderData: OrderCreateRequest
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(`${ORDER_ENDPOINT}/`, orderData);
  return data;
}

async function updateOrder(
  id: string,
  orderData: OrderUpdateRequest
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.patch(`${ORDER_ENDPOINT}/${id}/`, orderData);
  return data;
}

async function cancelOrder(
  id: string,
  reason: string
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(`${ORDER_ENDPOINT}/${id}/cancel/`, {
    reason,
  });
  return data;
}

async function deleteOrder(id: string): Promise<void> {
  await apiClient.delete(`${ORDER_ENDPOINT}/${id}/`);
}

async function confirmOrder(id: string): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(`${ORDER_ENDPOINT}/${id}/confirm/`);
  return data;
}

async function getOrdersByCustomer(
  customerId: string,
  params?: OrderSearchParams
): Promise<PaginatedResponse<Order>> {
  const { data } = await apiClient.get(
    `${ORDER_ENDPOINT}/by-customer/${customerId}/`,
    { params }
  );
  return data;
}

async function calculateOrderTotal(
  items: Array<{ price: number; quantity: number }>,
  discounts?: Array<{ type: 'percentage' | 'fixed'; value: number }>,
  shippingCost?: number
): Promise<{ subtotal: number; discountTotal: number; shipping: number; total: number }> {
  const subtotal = items.reduce((sum, i) => sum + i.price * i.quantity, 0);
  let discountTotal = 0;
  if (discounts) {
    for (const d of discounts) {
      discountTotal +=
        d.type === 'percentage' ? subtotal * (d.value / 100) : d.value;
    }
  }
  const shipping = shippingCost ?? 0;
  const total = Math.max(0, subtotal - discountTotal + shipping);
  return { subtotal, discountTotal, shipping, total };
}

// ── Order Items ────────────────────────────────────────────────

async function addOrderItem(
  orderId: string,
  item: Omit<OrderItem, 'id'>
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(
    `${ORDER_ENDPOINT}/${orderId}/items/`,
    item
  );
  return data;
}

async function updateOrderItem(
  orderId: string,
  itemId: string,
  itemData: Partial<OrderItem>
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.patch(
    `${ORDER_ENDPOINT}/${orderId}/items/${itemId}/`,
    itemData
  );
  return data;
}

async function removeOrderItem(
  orderId: string,
  itemId: string
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.delete(
    `${ORDER_ENDPOINT}/${orderId}/items/${itemId}/`
  );
  return data;
}

// ── Order Discounts ────────────────────────────────────────────

async function applyDiscount(
  orderId: string,
  discount: Omit<OrderDiscount, 'id'>
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(
    `${ORDER_ENDPOINT}/${orderId}/discounts/`,
    discount
  );
  return data;
}

async function removeDiscount(
  orderId: string,
  discountId: string
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.delete(
    `${ORDER_ENDPOINT}/${orderId}/discounts/${discountId}/`
  );
  return data;
}

// ── Order Payments ─────────────────────────────────────────────

async function recordPayment(
  orderId: string,
  payment: Omit<OrderPayment, 'id' | 'createdAt'>
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(
    `${ORDER_ENDPOINT}/${orderId}/payments/`,
    payment
  );
  return data;
}

async function refundPayment(
  orderId: string,
  paymentId: string,
  amount: number,
  reason: string
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(
    `${ORDER_ENDPOINT}/${orderId}/payments/${paymentId}/refund/`,
    { amount, reason }
  );
  return data;
}

// ── Order Shipments ────────────────────────────────────────────

async function createShipment(
  orderId: string,
  shipment: Omit<OrderShipment, 'id'>
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(
    `${ORDER_ENDPOINT}/${orderId}/shipments/`,
    shipment
  );
  return data;
}

async function updateShipment(
  orderId: string,
  shipmentId: string,
  shipmentData: Partial<OrderShipment>
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.patch(
    `${ORDER_ENDPOINT}/${orderId}/shipments/${shipmentId}/`,
    shipmentData
  );
  return data;
}

async function markDelivered(
  orderId: string,
  shipmentId: string
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(
    `${ORDER_ENDPOINT}/${orderId}/shipments/${shipmentId}/deliver/`
  );
  return data;
}

// ── Order Notes ────────────────────────────────────────────────

async function addOrderNote(
  orderId: string,
  note: Omit<OrderNote, 'id' | 'createdAt' | 'createdBy'>
): Promise<APIResponse<OrderNote>> {
  const { data } = await apiClient.post(
    `${ORDER_ENDPOINT}/${orderId}/notes/`,
    note
  );
  return data;
}

async function getOrderNotes(
  orderId: string
): Promise<APIResponse<OrderNote[]>> {
  const { data } = await apiClient.get(`${ORDER_ENDPOINT}/${orderId}/notes/`);
  return data;
}

// ── Quick Sale ─────────────────────────────────────────────────

async function quickSale(
  saleData: QuickSaleRequest
): Promise<APIResponse<Order>> {
  const { data } = await apiClient.post(
    `${ORDER_ENDPOINT}/quick-sale/`,
    saleData
  );
  return data;
}

// ── Summary / Analytics ────────────────────────────────────────

async function getOrderSummary(params?: {
  startDate?: string;
  endDate?: string;
}): Promise<APIResponse<OrderSummary>> {
  const { data } = await apiClient.get(`${ORDER_ENDPOINT}/summary/`, { params });
  return data;
}

async function getOrderReceipt(
  orderId: string
): Promise<APIResponse<Blob>> {
  const { data } = await apiClient.get(`${ORDER_ENDPOINT}/${orderId}/receipt/`, {
    responseType: 'blob',
  });
  return data;
}

const salesService = {
  getOrders,
  getOrderById,
  getOrderByNumber,
  createOrder,
  updateOrder,
  cancelOrder,
  deleteOrder,
  confirmOrder,
  getOrdersByCustomer,
  calculateOrderTotal,
  addOrderItem,
  updateOrderItem,
  removeOrderItem,
  applyDiscount,
  removeDiscount,
  recordPayment,
  refundPayment,
  createShipment,
  updateShipment,
  markDelivered,
  addOrderNote,
  getOrderNotes,
  quickSale,
  getOrderSummary,
  getOrderReceipt,
};

export default salesService;
