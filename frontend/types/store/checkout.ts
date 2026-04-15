/**
 * Storefront Checkout Types
 */

export interface StoreCheckoutSession {
  sessionId: string;
  customerId?: string;
  cart: import('./cart').StoreCart;
  customer?: import('./customer').StoreCustomer;
  step: StoreCheckoutStep;
  shippingAddress?: import('./customer').StoreCustomerAddress;
  billingAddress?: import('./customer').StoreCustomerAddress;
  paymentMethod?: import('./order').StorePaymentMethod;
  isProcessing: boolean;
}

export enum StoreCheckoutStep {
  CART = 'cart',
  INFORMATION = 'information',
  SHIPPING = 'shipping',
  PAYMENT = 'payment',
  CONFIRMATION = 'confirmation',
}

export interface StoreCheckoutValidation {
  information: StoreFieldValidation;
  shipping: StoreFieldValidation;
  payment: StoreFieldValidation;
}

export interface StoreFieldValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface StoreCheckoutSummary {
  itemCount: number;
  subtotal: number;
  tax: number;
  shipping: number;
  discount: number;
  total: number;
}

export interface StoreOrderConfirmation {
  orderId: string;
  orderNumber: string;
  confirmationEmail: string;
  estimatedDelivery: string;
}

export interface StoreOrderReceipt {
  orderId: string;
  items: import('./order').StoreOrderItem[];
  subtotal: number;
  tax: number;
  shipping: number;
  total: number;
  shippingAddress: import('./customer').StoreCustomerAddress;
  trackingInfo?: { number: string; carrier: string };
}
