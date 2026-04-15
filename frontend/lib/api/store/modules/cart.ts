import { getStoreClient } from '../client';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface StoreCartItem {
  id: number;
  product_id: number;
  product: { id: number; name: string; slug: string; image_url: string };
  variant_id: number | null;
  variant: { id: number; name: string; sku: string; attributes: Record<string, string> } | null;
  quantity: number;
  unit_price: number;
  line_total: number;
  notes: string | null;
}

export interface StoreCart {
  id: number;
  user_id: number | null;
  items: StoreCartItem[];
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
  currency: string;
  coupon_code: string | null;
  coupon_discount: number;
  created_at: string;
  updated_at: string;
}

export interface AddToCartParams {
  product_id: number;
  variant_id?: number;
  quantity: number;
  notes?: string;
}

export interface UpdateCartItemParams {
  quantity: number;
  notes?: string;
}

export interface ApplyCouponParams {
  coupon_code: string;
}

// ─── Guest Cart (localStorage) ──────────────────────────────────────────────

const GUEST_CART_KEY = 'store_cart';

interface GuestCartItem {
  product_id: number;
  variant_id?: number;
  quantity: number;
  notes?: string;
  added_at: string;
}

interface GuestCart {
  items: GuestCartItem[];
  updated_at: string;
}

function getGuestCart(): GuestCart {
  if (typeof window === 'undefined') return { items: [], updated_at: new Date().toISOString() };
  try {
    const raw = localStorage.getItem(GUEST_CART_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // Corrupted data
  }
  return { items: [], updated_at: new Date().toISOString() };
}

function saveGuestCart(cart: GuestCart): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(GUEST_CART_KEY, JSON.stringify(cart));
}

function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('store-auth-token');
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function getCart(): Promise<StoreCart> {
  if (!isAuthenticated()) {
    const guest = getGuestCart();
    return {
      id: 0,
      user_id: null,
      items: guest.items.map((item, idx) => ({
        id: idx,
        product_id: item.product_id,
        product: { id: item.product_id, name: '', slug: '', image_url: '' },
        variant_id: item.variant_id ?? null,
        variant: null,
        quantity: item.quantity,
        unit_price: 0,
        line_total: 0,
        notes: item.notes ?? null,
      })),
      subtotal: 0,
      discount: 0,
      tax: 0,
      total: 0,
      currency: 'LKR',
      coupon_code: null,
      coupon_discount: 0,
      created_at: guest.updated_at,
      updated_at: guest.updated_at,
    };
  }

  const { data } = await getStoreClient().get('/cart/');
  return data;
}

export async function addToCart(params: AddToCartParams): Promise<StoreCart> {
  if (!isAuthenticated()) {
    const guest = getGuestCart();
    const existing = guest.items.find(
      (i) => i.product_id === params.product_id && i.variant_id === params.variant_id
    );
    if (existing) {
      existing.quantity += params.quantity;
    } else {
      guest.items.push({
        product_id: params.product_id,
        variant_id: params.variant_id,
        quantity: params.quantity,
        notes: params.notes,
        added_at: new Date().toISOString(),
      });
    }
    guest.updated_at = new Date().toISOString();
    saveGuestCart(guest);
    return getCart();
  }

  const { data } = await getStoreClient().post('/cart/items/', params);
  return data;
}

export async function updateCartItem(
  itemId: number,
  params: UpdateCartItemParams
): Promise<StoreCart> {
  if (!isAuthenticated()) {
    const guest = getGuestCart();
    const item = guest.items[itemId];
    if (item) {
      item.quantity = params.quantity;
      if (params.notes !== undefined) item.notes = params.notes;
      guest.updated_at = new Date().toISOString();
      saveGuestCart(guest);
    }
    return getCart();
  }

  const { data } = await getStoreClient().patch(`/cart/items/${itemId}/`, params);
  return data;
}

export async function removeCartItem(itemId: number): Promise<StoreCart> {
  if (!isAuthenticated()) {
    const guest = getGuestCart();
    guest.items.splice(itemId, 1);
    guest.updated_at = new Date().toISOString();
    saveGuestCart(guest);
    return getCart();
  }

  await getStoreClient().delete(`/cart/items/${itemId}/`);
  return getCart();
}

export async function clearCart(): Promise<void> {
  if (!isAuthenticated()) {
    saveGuestCart({ items: [], updated_at: new Date().toISOString() });
    return;
  }

  await getStoreClient().delete('/cart/clear/');
}

export async function applyCoupon(params: ApplyCouponParams): Promise<StoreCart> {
  const { data } = await getStoreClient().post('/cart/apply-coupon/', params);
  return data;
}

export async function removeCoupon(): Promise<StoreCart> {
  const { data } = await getStoreClient().delete('/cart/coupon/');
  return data;
}

export async function syncCart(): Promise<StoreCart> {
  const guestCart = getGuestCart();
  if (guestCart.items.length === 0) return getCart();

  const { data } = await getStoreClient().post('/cart/sync/', { items: guestCart.items });
  // Clear guest cart after sync
  saveGuestCart({ items: [], updated_at: new Date().toISOString() });
  return data;
}

export function getCartSummary(): { itemCount: number; subtotal: number } {
  const guest = getGuestCart();
  return {
    itemCount: guest.items.reduce((sum, item) => sum + item.quantity, 0),
    subtotal: 0, // Price requires API call
  };
}

const cartApi = {
  getCart,
  addToCart,
  updateCartItem,
  removeCartItem,
  clearCart,
  applyCoupon,
  removeCoupon,
  syncCart,
  getCartSummary,
};

export default cartApi;
