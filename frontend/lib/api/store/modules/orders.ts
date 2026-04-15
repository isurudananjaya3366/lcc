import { getStoreClient, type PaginatedResponse } from '../client';

// ─── Types ──────────────────────────────────────────────────────────────────

export type OrderStatus =
  | 'PENDING'
  | 'PAYMENT_PENDING'
  | 'CONFIRMED'
  | 'PROCESSING'
  | 'READY_TO_SHIP'
  | 'SHIPPED'
  | 'OUT_FOR_DELIVERY'
  | 'DELIVERED'
  | 'CANCELLED'
  | 'RETURN_REQUESTED'
  | 'RETURNED'
  | 'REFUNDED';

export type PaymentStatus =
  | 'PENDING'
  | 'AUTHORIZED'
  | 'PAID'
  | 'FAILED'
  | 'REFUNDED'
  | 'PARTIALLY_REFUNDED';

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  product_name: string;
  sku: string;
  variant_id: number | null;
  quantity: number;
  unit_price: number;
  line_total: number;
  thumbnail_url: string | null;
}

export interface OrderTracking {
  status: string;
  status_label: string;
  timestamp: string;
  location: string | null;
  courier_name: string | null;
  tracking_number: string | null;
  estimated_delivery: string | null;
}

export interface Order {
  id: number;
  order_number: string;
  user_id: number;
  status: OrderStatus;
  order_date: string;
  items: OrderItem[];
  subtotal: number;
  discount: number;
  shipping: number;
  tax: number;
  total: number;
  currency: string;
  shipping_address: {
    full_name: string;
    phone: string;
    address_line1: string;
    city: string;
    district: string;
    province: string;
    postal_code: string;
  };
  payment_method: string;
  payment_status: PaymentStatus;
  tracking_info: OrderTracking[] | null;
  created_at: string;
  updated_at: string;
}

export interface OrdersListParams {
  status?: OrderStatus;
  date_from?: string;
  date_to?: string;
  search?: string;
  sort?: string;
  page?: number;
  page_size?: number;
}

export interface ReturnRequestParams {
  item_ids: number[];
  reason: string;
  type: 'refund' | 'exchange';
  description?: string;
  images?: string[];
}

// ─── Status Utilities ───────────────────────────────────────────────────────

const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  PENDING: 'Pending',
  PAYMENT_PENDING: 'Awaiting Payment',
  CONFIRMED: 'Confirmed',
  PROCESSING: 'Processing',
  READY_TO_SHIP: 'Ready to Ship',
  SHIPPED: 'Shipped',
  OUT_FOR_DELIVERY: 'Out for Delivery',
  DELIVERED: 'Delivered',
  CANCELLED: 'Cancelled',
  RETURN_REQUESTED: 'Return Requested',
  RETURNED: 'Returned',
  REFUNDED: 'Refunded',
};

export function getOrderStatusLabel(status: OrderStatus): string {
  return ORDER_STATUS_LABELS[status] || status;
}

export function canCancelOrder(order: Order): boolean {
  const cancellableStatuses: OrderStatus[] = [
    'PENDING',
    'PAYMENT_PENDING',
    'CONFIRMED',
    'PROCESSING',
  ];
  return cancellableStatuses.includes(order.status);
}

export function canReturnOrder(order: Order): boolean {
  if (order.status !== 'DELIVERED') return false;
  const deliveredDate = new Date(order.updated_at);
  const daysSinceDelivery = (Date.now() - deliveredDate.getTime()) / (1000 * 60 * 60 * 24);
  return daysSinceDelivery <= 14;
}

export function formatOrderTotal(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function listOrders(params?: OrdersListParams): Promise<PaginatedResponse<Order>> {
  const { data } = await getStoreClient().get('/customer/orders/', { params });
  return data;
}

export async function getOrderById(orderId: number): Promise<Order> {
  const { data } = await getStoreClient().get(`/customer/orders/${orderId}/`);
  return data;
}

export async function getOrderByNumber(orderNumber: string): Promise<Order> {
  const { data } = await getStoreClient().get(`/customer/orders/by-number/${orderNumber}/`);
  return data;
}

export async function trackOrder(orderId: number): Promise<OrderTracking[]> {
  const { data } = await getStoreClient().get(`/customer/orders/${orderId}/tracking/`);
  return data;
}

export async function cancelOrder(
  orderId: number,
  reason?: string,
  notes?: string
): Promise<Order> {
  const { data } = await getStoreClient().post(`/customer/orders/${orderId}/cancel/`, {
    reason,
    notes,
  });
  return data;
}

export async function requestReturn(
  orderId: number,
  params: ReturnRequestParams
): Promise<{ id: number; status: string }> {
  const { data } = await getStoreClient().post(`/customer/orders/${orderId}/return/`, params);
  return data;
}

export async function reorder(orderId: number): Promise<{ cart_id: number; items_added: number }> {
  const { data } = await getStoreClient().post(`/customer/orders/${orderId}/reorder/`);
  return data;
}

export async function downloadInvoice(orderId: number): Promise<Blob> {
  const { data } = await getStoreClient().get(`/customer/orders/${orderId}/invoice/`, {
    responseType: 'blob',
  });
  return data;
}

export async function downloadReceipt(orderId: number): Promise<Blob> {
  const { data } = await getStoreClient().get(`/customer/orders/${orderId}/receipt/`, {
    responseType: 'blob',
  });
  return data;
}

export async function sendInvoiceEmail(orderId: number): Promise<{ message: string }> {
  const { data } = await getStoreClient().post(`/customer/orders/${orderId}/send-invoice/`);
  return data;
}

const ordersApi = {
  listOrders,
  getOrderById,
  getOrderByNumber,
  trackOrder,
  cancelOrder,
  requestReturn,
  reorder,
  downloadInvoice,
  downloadReceipt,
  sendInvoiceEmail,
  getOrderStatusLabel,
  canCancelOrder,
  canReturnOrder,
  formatOrderTotal,
};

export default ordersApi;
