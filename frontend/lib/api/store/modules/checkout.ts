import { getStoreClient } from '../client';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ShippingAddress {
  id?: number;
  full_name: string;
  phone: string;
  address_line1: string;
  address_line2?: string;
  city: string;
  district: string;
  province: string;
  postal_code: string;
  country: string;
  is_default?: boolean;
  address_type: 'home' | 'work' | 'other';
}

export interface PaymentMethod {
  id: number;
  type: 'payhere' | 'stripe' | 'bank_transfer' | 'cod';
  card_last4?: string;
  card_brand?: string;
  bank_name?: string;
  account_number_last4?: string;
  is_default: boolean;
  expires_at?: string;
}

export interface ShippingMethod {
  id: number;
  name: string;
  code: string;
  price: number;
  estimated_days: string;
  available_zones: string[];
  description: string;
}

export interface OrderSummary {
  subtotal: number;
  discount: number;
  shipping_cost: number;
  tax: number;
  total: number;
  currency: string;
  item_count: number;
  payment_breakdown: Record<string, number>;
}

export type CheckoutStep = 1 | 2 | 3 | 4 | 5;

export interface Checkout {
  id: number;
  user_id: number;
  cart_id: number;
  current_step: CheckoutStep;
  shipping_address: ShippingAddress | null;
  billing_address: ShippingAddress | null;
  payment_method: PaymentMethod | null;
  shipping_method: ShippingMethod | null;
  order_summary: OrderSummary | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CheckoutProgress {
  current_step: CheckoutStep;
  completed_steps: CheckoutStep[];
  completion_percentage: number;
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function initiateCheckout(cartId: number): Promise<Checkout> {
  const { data } = await getStoreClient().post('/checkout/', { cart_id: cartId });
  return data;
}

export async function updateShippingAddress(
  checkoutId: number,
  address: ShippingAddress | { address_id: number }
): Promise<Checkout> {
  const { data } = await getStoreClient().put(`/checkout/${checkoutId}/shipping-address/`, address);
  return data;
}

export async function updatePaymentMethod(
  checkoutId: number,
  payment:
    | { payment_method_id: number }
    | { type: PaymentMethod['type']; details?: Record<string, unknown> }
): Promise<Checkout> {
  const { data } = await getStoreClient().put(`/checkout/${checkoutId}/payment-method/`, payment);
  return data;
}

export async function getShippingOptions(checkoutId: number): Promise<ShippingMethod[]> {
  const { data } = await getStoreClient().get(`/checkout/${checkoutId}/shipping-options/`);
  return data;
}

export async function applyShippingMethod(
  checkoutId: number,
  shippingMethodId: number
): Promise<Checkout> {
  const { data } = await getStoreClient().put(`/checkout/${checkoutId}/shipping-method/`, {
    shipping_method_id: shippingMethodId,
  });
  return data;
}

export async function getOrderSummary(checkoutId: number): Promise<OrderSummary> {
  const { data } = await getStoreClient().get(`/checkout/${checkoutId}/summary/`);
  return data;
}

export async function validateCheckout(
  checkoutId: number
): Promise<{ valid: boolean; errors: string[] }> {
  const { data } = await getStoreClient().post(`/checkout/${checkoutId}/validate/`);
  return data;
}

export async function updateCheckoutStep(
  checkoutId: number,
  step: CheckoutStep
): Promise<Checkout> {
  const { data } = await getStoreClient().put(`/checkout/${checkoutId}/step/`, { step });
  return data;
}

export function getCheckoutProgress(checkout: Checkout): CheckoutProgress {
  const completedSteps: CheckoutStep[] = [];
  if (checkout.shipping_address) completedSteps.push(1, 2);
  if (checkout.payment_method) completedSteps.push(3);
  if (checkout.order_summary) completedSteps.push(4);

  return {
    current_step: checkout.current_step,
    completed_steps: completedSteps,
    completion_percentage: (completedSteps.length / 5) * 100,
  };
}

export async function submitOrder(
  checkoutId: number,
  idempotencyKey: string
): Promise<{ order_id: number; order_number: string }> {
  const { data } = await getStoreClient().post(
    `/checkout/${checkoutId}/submit/`,
    {},
    { headers: { 'Idempotency-Key': idempotencyKey } }
  );
  return data;
}

export async function initializePayHerePayment(checkoutId: number): Promise<{
  merchant_id: string;
  order_id: string;
  amount: number;
  currency: string;
  hash: string;
  return_url: string;
  cancel_url: string;
  notify_url: string;
}> {
  const { data } = await getStoreClient().post(`/checkout/${checkoutId}/payment/payhere/`);
  return data;
}

export async function initializeStripePayment(checkoutId: number): Promise<{
  client_secret: string;
  publishable_key: string;
}> {
  const { data } = await getStoreClient().post(`/checkout/${checkoutId}/payment/stripe/`);
  return data;
}

export async function handlePaymentCallback(
  provider: 'payhere' | 'stripe',
  result: Record<string, unknown>
): Promise<{ status: string; order_id?: number }> {
  const { data } = await getStoreClient().post(`/checkout/payment/${provider}/callback/`, result);
  return data;
}

export async function verifyPaymentStatus(checkoutId: number): Promise<{
  status: 'pending' | 'authorized' | 'paid' | 'failed';
  message: string;
}> {
  const { data } = await getStoreClient().get(`/checkout/${checkoutId}/payment/status/`);
  return data;
}

export async function resumeCheckout(checkoutId: number): Promise<Checkout> {
  const { data } = await getStoreClient().post(`/checkout/${checkoutId}/resume/`);
  return data;
}

const checkoutApi = {
  initiateCheckout,
  updateShippingAddress,
  updatePaymentMethod,
  getShippingOptions,
  applyShippingMethod,
  getOrderSummary,
  validateCheckout,
  updateCheckoutStep,
  getCheckoutProgress,
  submitOrder,
  initializePayHerePayment,
  initializeStripePayment,
  handlePaymentCallback,
  verifyPaymentStatus,
  resumeCheckout,
};

export default checkoutApi;
