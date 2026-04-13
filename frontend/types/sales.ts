/**
 * Sales Types
 *
 * Comprehensive TypeScript types for sales operations including
 * orders, order items, payment processing, fulfillment, and
 * order status tracking.
 */

// ── Enums ──────────────────────────────────────────────────────

export enum OrderStatus {
  DRAFT = 'DRAFT',
  PENDING = 'PENDING',
  CONFIRMED = 'CONFIRMED',
  PROCESSING = 'PROCESSING',
  SHIPPED = 'SHIPPED',
  DELIVERED = 'DELIVERED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
  REFUNDED = 'REFUNDED',
}

export enum OrderType {
  SALE = 'SALE',
  QUOTE = 'QUOTE',
  RETURN = 'RETURN',
  EXCHANGE = 'EXCHANGE',
}

export enum PaymentStatus {
  UNPAID = 'UNPAID',
  PARTIAL = 'PARTIAL',
  PAID = 'PAID',
  OVERPAID = 'OVERPAID',
  REFUNDED = 'REFUNDED',
}

export enum FulfillmentStatus {
  UNFULFILLED = 'UNFULFILLED',
  PARTIALLY_FULFILLED = 'PARTIALLY_FULFILLED',
  FULFILLED = 'FULFILLED',
  DELIVERED = 'DELIVERED',
  RETURNED = 'RETURNED',
}

export enum ShippingMethod {
  PICKUP = 'PICKUP',
  STANDARD = 'STANDARD',
  EXPRESS = 'EXPRESS',
  OVERNIGHT = 'OVERNIGHT',
  COURIER = 'COURIER',
}

export enum OrderSource {
  POS = 'POS',
  WEBSTORE = 'WEBSTORE',
  PHONE = 'PHONE',
  EMAIL = 'EMAIL',
  WALK_IN = 'WALK_IN',
}

// ── Supporting Interfaces ──────────────────────────────────────

export interface OrderItem {
  id: string;
  orderId: string;
  productId: string;
  variantId?: string;
  sku: string;
  name: string;
  description?: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  discountType: 'FIXED' | 'PERCENTAGE';
  taxRate: number;
  taxAmount: number;
  subtotal: number;
  total: number;
  warehouseId?: string;
  notes?: string;
}

export interface OrderDiscount {
  id: string;
  orderId: string;
  discountCode?: string;
  discountName: string;
  discountType: 'FIXED' | 'PERCENTAGE';
  discountValue: number;
  discountAmount: number;
  appliedBy?: string;
  appliedAt?: string;
}

export interface OrderPayment {
  id: string;
  orderId: string;
  paymentNumber: string;
  paymentDate: string;
  paymentMethod: 'CASH' | 'CARD' | 'BANK_TRANSFER' | 'CREDIT';
  amount: number;
  referenceNumber?: string;
  cardLastFour?: string;
  status: PaymentStatus;
  processedBy?: string;
  notes?: string;
}

export interface OrderShipment {
  id: string;
  orderId: string;
  shipmentNumber: string;
  carrier?: string;
  trackingNumber?: string;
  shippingMethod: ShippingMethod;
  shippedDate?: string;
  estimatedDelivery?: string;
  deliveredDate?: string;
  items: { productId: string; variantId?: string; quantity: number }[];
  weight?: number;
  dimensions?: { length: number; width: number; height: number };
  shippingCost: number;
}

export interface OrderAddress {
  addressType: 'BILLING' | 'SHIPPING';
  firstName: string;
  lastName: string;
  companyName?: string;
  street: string;
  street2?: string;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  phone?: string;
  email?: string;
}

export interface OrderNote {
  id: string;
  orderId: string;
  note: string;
  category?: string;
  isCustomerVisible: boolean;
  createdBy: string;
  createdAt: string;
}

export interface OrderSummary {
  totalOrders: number;
  totalValue: number;
  averageOrderValue: number;
  statusBreakdown: Record<OrderStatus, number>;
  sourceBreakdown: Record<OrderSource, number>;
  period: { startDate: string; endDate: string };
}

// ── Main Entity ────────────────────────────────────────────────

export interface Order {
  id: string;
  tenantId: string;
  orderNumber: string;
  orderType: OrderType;
  orderStatus: OrderStatus;
  orderSource: OrderSource;
  orderDate: string;
  customerId?: string;
  customerName?: string;
  customerEmail?: string;
  customerPhone?: string;
  items: OrderItem[];
  discounts?: OrderDiscount[];
  payments?: OrderPayment[];
  shipments?: OrderShipment[];
  billingAddress?: OrderAddress;
  shippingAddress?: OrderAddress;
  subtotal: number;
  discountTotal: number;
  taxTotal: number;
  shippingCost: number;
  total: number;
  paymentStatus: PaymentStatus;
  fulfillmentStatus: FulfillmentStatus;
  notes?: OrderNote[];
  tags?: string[];
  customFields?: Record<string, unknown>;
  salesPersonId?: string;
  warehouseId?: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

// ── API Request/Response Interfaces ────────────────────────────

export interface OrderCreateRequest {
  orderType?: OrderType;
  orderSource: OrderSource;
  customerId?: string;
  items: Omit<OrderItem, 'id' | 'orderId' | 'taxAmount' | 'subtotal' | 'total'>[];
  billingAddress?: OrderAddress;
  shippingAddress?: OrderAddress;
  shippingMethod?: ShippingMethod;
  discounts?: Omit<OrderDiscount, 'id' | 'orderId' | 'discountAmount'>[];
  payments?: Omit<OrderPayment, 'id' | 'orderId' | 'paymentNumber' | 'status'>[];
  salesPersonId?: string;
  warehouseId?: string;
  notes?: string;
  tags?: string[];
}

export interface OrderUpdateRequest {
  orderStatus?: OrderStatus;
  customerId?: string;
  billingAddress?: OrderAddress;
  shippingAddress?: OrderAddress;
  salesPersonId?: string;
  warehouseId?: string;
  tags?: string[];
  customFields?: Record<string, unknown>;
}

export interface OrderSearchParams {
  query?: string;
  customerId?: string;
  orderStatus?: OrderStatus;
  paymentStatus?: PaymentStatus;
  fulfillmentStatus?: FulfillmentStatus;
  orderSource?: OrderSource;
  startDate?: string;
  endDate?: string;
  salesPersonId?: string;
  tags?: string[];
  sort?: string;
  page?: number;
  pageSize?: number;
}

export interface QuickSaleRequest {
  items: { productId: string; variantId?: string; quantity: number; price: number }[];
  customerId?: string;
  payments: { paymentMethod: 'CASH' | 'CARD' | 'BANK_TRANSFER'; amount: number }[];
  warehouseId?: string;
  notes?: string;
}
