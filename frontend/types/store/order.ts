/**
 * Storefront Order Types
 */

export interface StoreOrder {
  id: string;
  orderId: string;
  orderNumber: string;
  customerId: string;
  status: StoreOrderStatus;
  items: StoreOrderItem[];
  subtotal: number;
  tax: number;
  shipping: number;
  discount: number;
  total: number;
  currency: string;
  customer: { email: string; phone: string };
  shippingAddress: import('./customer').StoreCustomerAddress;
  billingAddress?: import('./customer').StoreCustomerAddress;
  shippingMethod: import('./cart').StoreShippingMethod;
  paymentMethod: StorePaymentMethod;
  trackingNumber?: string;
  carrier?: string;
  estimatedDelivery?: string;
  orderedAt: string;
  confirmedAt?: string;
  shippedAt?: string;
  deliveredAt?: string;
  cancelledAt?: string;
}

export interface StoreOrderItem {
  id: string;
  productId: string;
  variantId?: string;
  name: string;
  sku: string;
  quantity: number;
  price: number;
  lineTotal: number;
}

export enum StoreOrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  PROCESSING = 'processing',
  SHIPPED = 'shipped',
  DELIVERED = 'delivered',
  CANCELLED = 'cancelled',
}

export interface StorePaymentMethod {
  type: StorePaymentMethodType;
  provider?: string;
  last4?: string;
  metadata?: Record<string, unknown>;
}

export enum StorePaymentMethodType {
  CREDIT_CARD = 'credit_card',
  PAYPAL = 'paypal',
  BANK_TRANSFER = 'bank_transfer',
  CASH_ON_DELIVERY = 'cash_on_delivery',
}

export interface StorePaymentTransaction {
  id: string;
  amount: number;
  status: 'pending' | 'completed' | 'failed';
  timestamp: string;
  metadata?: Record<string, unknown>;
}
