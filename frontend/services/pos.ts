// ================================================================
// POS Service — API communication for POS module
// ================================================================

import { api } from '@/services';
import type {
  ProductSearchResult,
  QuickButtonGroup,
  POSCustomer,
  POSPayment,
  POSReceipt,
  POSShift,
} from '@/components/modules/pos/types';

// ── Search ─────────────────────────────────────────────────────

export async function searchProducts(
  query: string,
  options?: { category?: string; inStock?: boolean; signal?: AbortSignal }
): Promise<ProductSearchResult[]> {
  const params = new URLSearchParams({ q: query });
  if (options?.category) params.set('category', options.category);
  if (options?.inStock !== undefined) params.set('in_stock', String(options.inStock));

  return api.get<ProductSearchResult[]>(`/v1/pos/search/products/?${params}`);
}

export async function scanBarcode(barcode: string): Promise<ProductSearchResult> {
  return api.post<ProductSearchResult>('/v1/pos/search/barcode/', { barcode });
}

// ── Quick Buttons ──────────────────────────────────────────────

export async function fetchQuickButtonGroups(): Promise<QuickButtonGroup[]> {
  return api.get<QuickButtonGroup[]>('/v1/pos/search/quick-buttons/');
}

// ── Cart ───────────────────────────────────────────────────────

export async function createCart(sessionId: string) {
  return api.post('/v1/pos/cart/', { session: sessionId });
}

export async function addCartItem(
  cartId: string,
  data: { product: string; variant?: string; quantity: number }
) {
  return api.post(`/v1/pos/cart/${cartId}/add_item/`, data);
}

export async function updateCartQuantity(cartId: string, itemId: string, quantity: number) {
  return api.post(`/v1/pos/cart/${cartId}/update_quantity/`, { item_id: itemId, quantity });
}

export async function removeCartItem(cartId: string, itemId: string) {
  return api.post(`/v1/pos/cart/${cartId}/remove_item/`, { item_id: itemId });
}

export async function applyCartDiscount(
  cartId: string,
  data: { type: string; value: number; reason?: string; coupon_code?: string }
) {
  return api.post(`/v1/pos/cart/${cartId}/apply_discount/`, data);
}

export async function holdCart(cartId: string, reason?: string) {
  return api.post(`/v1/pos/cart/${cartId}/hold/`, { reason });
}

export async function recallCart(cartId: string) {
  return api.post(`/v1/pos/cart/${cartId}/recall/`);
}

// ── Payment ────────────────────────────────────────────────────

export async function processPayment(data: {
  cart_id: string;
  method: string;
  amount: number;
  reference_number?: string;
  amount_tendered?: number;
}): Promise<POSPayment> {
  return api.post<POSPayment>('/v1/pos/payments/process/', data);
}

export async function processSplitPayment(data: {
  cart_id: string;
  payments: Array<{ method: string; amount: number; reference_number?: string }>;
}) {
  return api.post('/v1/pos/payments/split/', data);
}

export async function completePayment(cartId: string) {
  return api.post('/v1/pos/payments/complete/', { cart_id: cartId });
}

export async function refundPayment(paymentId: string, data: { amount: number; reason: string }) {
  return api.post(`/v1/pos/payments/refund/`, { payment_id: paymentId, ...data });
}

// ── Shift / Session ────────────────────────────────────────────

export async function openSession(terminalId: string, openingCash: number): Promise<POSShift> {
  return api.post<POSShift>(`/v1/pos/sessions/`, {
    terminal: terminalId,
    opening_cash: openingCash,
  });
}

export async function closeSession(
  sessionId: string,
  data: { closing_cash: number; notes?: string }
): Promise<POSShift> {
  return api.post<POSShift>(`/v1/pos/sessions/${sessionId}/close_session/`, data);
}

export async function getCurrentSession(terminalId: string): Promise<POSShift | null> {
  return api.get<POSShift | null>(`/v1/pos/sessions/current/?terminal=${terminalId}`);
}

export async function getSessionSummary(sessionId: string) {
  return api.get(`/v1/pos/sessions/${sessionId}/summary/`);
}

// ── Receipt ────────────────────────────────────────────────────

export async function generateReceipt(cartId: string): Promise<POSReceipt> {
  return api.post<POSReceipt>('/v1/pos/receipts/', { cart: cartId });
}

export async function emailReceipt(receiptId: string, email: string) {
  return api.post(`/v1/pos/receipts/${receiptId}/email/`, { email });
}

// ── Customer Search ────────────────────────────────────────────

export async function searchCustomers(query: string): Promise<POSCustomer[]> {
  return api.get<POSCustomer[]>(`/v1/customers/?search=${encodeURIComponent(query)}`);
}

export const posService = {
  searchProducts,
  scanBarcode,
  fetchQuickButtonGroups,
  createCart,
  addCartItem,
  updateCartQuantity,
  removeCartItem,
  applyCartDiscount,
  holdCart,
  recallCart,
  processPayment,
  processSplitPayment,
  completePayment,
  refundPayment,
  openSession,
  closeSession,
  getCurrentSession,
  getSessionSummary,
  generateReceipt,
  emailReceipt,
  searchCustomers,
};
