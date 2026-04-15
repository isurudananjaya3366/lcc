import { getStoreClient } from '../client';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface WishlistItem {
  id: number;
  wishlist_id: number;
  product_id: number;
  product: {
    id: number;
    name: string;
    slug: string;
    price: number;
    sale_price: number | null;
    image_url: string;
    in_stock: boolean;
  };
  variant_id: number | null;
  added_at: string;
  notification_enabled: boolean;
}

export interface Wishlist {
  id: number;
  user_id: number;
  items: WishlistItem[];
  created_at: string;
  updated_at: string;
}

export interface WishlistSummary {
  item_count: number;
  total_value: number;
  available_count: number;
  out_of_stock_count: number;
}

interface LocalWishlist {
  product_ids: number[];
  timestamps: Record<string, string>;
}

// ─── Guest Wishlist (localStorage) ──────────────────────────────────────────

const WISHLIST_KEY = 'store_wishlist';

function getLocalWishlist(): LocalWishlist {
  if (typeof window === 'undefined') return { product_ids: [], timestamps: {} };
  try {
    const raw = localStorage.getItem(WISHLIST_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // Corrupted data
  }
  return { product_ids: [], timestamps: {} };
}

function saveLocalWishlist(wishlist: LocalWishlist): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(WISHLIST_KEY, JSON.stringify(wishlist));
}

function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('store-auth-token');
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function getWishlist(): Promise<Wishlist | LocalWishlist> {
  if (!isAuthenticated()) return getLocalWishlist();

  const { data } = await getStoreClient().get('/customer/wishlist/');
  return data;
}

export async function addToWishlist(productId: number, variantId?: number): Promise<void> {
  if (!isAuthenticated()) {
    const local = getLocalWishlist();
    if (!local.product_ids.includes(productId)) {
      local.product_ids.push(productId);
      local.timestamps[String(productId)] = new Date().toISOString();
      saveLocalWishlist(local);
    }
    return;
  }

  await getStoreClient().post('/customer/wishlist/items/', {
    product_id: productId,
    variant_id: variantId,
  });
}

export async function removeFromWishlist(itemIdOrProductId: number): Promise<void> {
  if (!isAuthenticated()) {
    const local = getLocalWishlist();
    local.product_ids = local.product_ids.filter((id) => id !== itemIdOrProductId);
    delete local.timestamps[String(itemIdOrProductId)];
    saveLocalWishlist(local);
    return;
  }

  await getStoreClient().delete(`/customer/wishlist/items/${itemIdOrProductId}/`);
}

export async function clearWishlist(): Promise<void> {
  if (!isAuthenticated()) {
    saveLocalWishlist({ product_ids: [], timestamps: {} });
    return;
  }

  await getStoreClient().delete('/customer/wishlist/');
}

export async function moveToCart(wishlistItemId: number): Promise<void> {
  await getStoreClient().post(`/customer/wishlist/items/${wishlistItemId}/move-to-cart/`);
}

export function isInWishlist(productId: number): boolean {
  if (!isAuthenticated()) {
    const local = getLocalWishlist();
    return local.product_ids.includes(productId);
  }
  // For authenticated users, this should be checked via the wishlist state
  return false;
}

export function getWishlistCount(): number {
  if (!isAuthenticated()) {
    return getLocalWishlist().product_ids.length;
  }
  return 0;
}

export async function syncWishlist(): Promise<Wishlist> {
  const local = getLocalWishlist();
  if (local.product_ids.length === 0) {
    const { data } = await getStoreClient().get('/customer/wishlist/');
    return data;
  }

  const { data } = await getStoreClient().post('/customer/wishlist/sync/', {
    product_ids: local.product_ids,
  });
  saveLocalWishlist({ product_ids: [], timestamps: {} });
  return data;
}

export async function enableNotifications(wishlistItemId: number): Promise<void> {
  await getStoreClient().put(`/customer/wishlist/items/${wishlistItemId}/notify/`, {
    enabled: true,
  });
}

export async function disableNotifications(wishlistItemId: number): Promise<void> {
  await getStoreClient().put(`/customer/wishlist/items/${wishlistItemId}/notify/`, {
    enabled: false,
  });
}

export function getWishlistValue(items: WishlistItem[]): number {
  return items.reduce((sum, item) => sum + (item.product.sale_price ?? item.product.price), 0);
}

export function getAvailableItems(items: WishlistItem[]): WishlistItem[] {
  return items.filter((item) => item.product.in_stock);
}

const wishlistApi = {
  getWishlist,
  addToWishlist,
  removeFromWishlist,
  clearWishlist,
  moveToCart,
  isInWishlist,
  getWishlistCount,
  syncWishlist,
  enableNotifications,
  disableNotifications,
  getWishlistValue,
  getAvailableItems,
};

export default wishlistApi;
