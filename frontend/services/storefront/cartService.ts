// ─── Types ──────────────────────────────────────────────────────────────────

export interface CartSyncItem {
  productId: string;
  quantity: number;
  variant: Record<string, string> | null;
}

export interface ServerCartItem {
  id: string;
  productId: string;
  name: string;
  sku: string;
  price: number;
  quantity: number;
  image: string;
  variant: Record<string, string> | null;
}

export interface StockValidationResult {
  validItems: ServerCartItem[];
  invalidItems: Array<ServerCartItem & { reason: 'out_of_stock' | 'low_stock' }>;
  priceChanges: Array<{ itemId: string; oldPrice: number; newPrice: number }>;
}

// ─── Config ─────────────────────────────────────────────────────────────────

const API_BASE = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`;

// ─── API Functions ──────────────────────────────────────────────────────────

/**
 * Sync local cart items to the server (logged-in users).
 * PLACEHOLDER — backend cart API not yet implemented.
 */
export async function syncCartToServer(items: CartSyncItem[]): Promise<{ success: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/cart/sync/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ items }),
    });
    if (!res.ok) return { success: false };
    return { success: true };
  } catch {
    // Placeholder: silently succeed when backend doesn't exist yet
    return { success: true };
  }
}

/**
 * Fetch the server-side cart for the current user.
 * PLACEHOLDER — returns empty cart until backend implements this endpoint.
 */
export async function fetchServerCart(): Promise<ServerCartItem[]> {
  try {
    const res = await fetch(`${API_BASE}/cart/`, { credentials: 'include' });
    if (!res.ok) return [];
    const data = await res.json();
    return data.items ?? [];
  } catch {
    return [];
  }
}

/**
 * Merge guest cart items with server cart items.
 * For duplicate products, the higher quantity wins.
 */
export function mergeGuestCart(
  guestItems: ServerCartItem[],
  serverItems: ServerCartItem[]
): ServerCartItem[] {
  const merged = new Map<string, ServerCartItem>();

  for (const item of serverItems) {
    merged.set(item.productId, { ...item });
  }

  for (const item of guestItems) {
    const existing = merged.get(item.productId);
    if (existing) {
      existing.quantity = Math.max(existing.quantity, item.quantity);
    } else {
      merged.set(item.productId, { ...item });
    }
  }

  return Array.from(merged.values());
}

/**
 * Validate stock levels and prices for cart items against the API.
 * PLACEHOLDER — attempts real fetch, falls back to all-valid.
 */
export async function validateCartStock(
  items: ServerCartItem[]
): Promise<StockValidationResult> {
  const validItems: ServerCartItem[] = [];
  const invalidItems: StockValidationResult['invalidItems'] = [];
  const priceChanges: StockValidationResult['priceChanges'] = [];

  for (const item of items) {
    try {
      const res = await fetch(`${API_BASE}/products/${item.productId}/`);
      if (!res.ok) {
        invalidItems.push({ ...item, reason: 'out_of_stock' });
        continue;
      }
      const product = await res.json();
      const currentPrice = product.price ?? item.price;
      const stock = product.stock ?? product.quantity_available ?? Infinity;

      if (stock <= 0) {
        invalidItems.push({ ...item, reason: 'out_of_stock' });
      } else if (stock < item.quantity) {
        invalidItems.push({ ...item, reason: 'low_stock' });
      } else {
        validItems.push(item);
      }

      if (currentPrice !== item.price) {
        priceChanges.push({ itemId: item.id, oldPrice: item.price, newPrice: currentPrice });
      }
    } catch {
      // If fetch fails (backend not ready), treat item as valid
      validItems.push(item);
    }
  }

  return { validItems, invalidItems, priceChanges };
}
