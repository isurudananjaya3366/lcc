/**
 * Stock Checking Utilities
 *
 * Stock status, availability checks, badge helpers, and backorder support.
 */

// ─── Types ───────────────────────────────────────────────────────────────────

export type StockStatus = 'in_stock' | 'low_stock' | 'out_of_stock' | 'backorder';

export interface StockInfo {
  status: StockStatus;
  quantity: number;
  message: string;
  badgeVariant: 'success' | 'warning' | 'destructive' | 'secondary';
  canPurchase: boolean;
}

const LOW_STOCK_THRESHOLD = 10;

// ─── Core Checks ─────────────────────────────────────────────────────────────

/**
 * Check if a product is currently in stock.
 */
export function isInStock(quantity: number): boolean {
  return quantity > 0;
}

/**
 * Get numeric stock level, clamped to zero.
 */
export function getStockLevel(quantity: number): number {
  return Math.max(0, quantity);
}

/**
 * Get the stock status category.
 */
export function getStockStatus(
  quantity: number,
  allowBackorder: boolean = false,
  threshold: number = LOW_STOCK_THRESHOLD
): StockStatus {
  if (quantity <= 0) return allowBackorder ? 'backorder' : 'out_of_stock';
  if (quantity <= threshold) return 'low_stock';
  return 'in_stock';
}

/**
 * Get a human-readable stock message.
 */
export function getStockMessage(
  quantity: number,
  allowBackorder: boolean = false,
  threshold: number = LOW_STOCK_THRESHOLD
): string {
  const status = getStockStatus(quantity, allowBackorder, threshold);

  switch (status) {
    case 'in_stock':
      return 'In Stock';
    case 'low_stock':
      return `Only ${quantity} left in stock`;
    case 'out_of_stock':
      return 'Out of Stock';
    case 'backorder':
      return 'Available on Backorder';
  }
}

/**
 * Get full stock info including badge variant and purchase eligibility.
 */
export function getStockInfo(
  quantity: number,
  allowBackorder: boolean = false,
  threshold: number = LOW_STOCK_THRESHOLD
): StockInfo {
  const status = getStockStatus(quantity, allowBackorder, threshold);
  const message = getStockMessage(quantity, allowBackorder, threshold);

  const badgeVariant: StockInfo['badgeVariant'] =
    status === 'in_stock'
      ? 'success'
      : status === 'low_stock'
        ? 'warning'
        : status === 'backorder'
          ? 'secondary'
          : 'destructive';

  const canPurchase = status !== 'out_of_stock';

  return {
    status,
    quantity: getStockLevel(quantity),
    message,
    badgeVariant,
    canPurchase,
  };
}

// ─── Cart Integration ────────────────────────────────────────────────────────

/**
 * Check if a given quantity can be added to cart for a product.
 */
export function canAddToCart(
  requestedQuantity: number,
  availableQuantity: number,
  currentCartQuantity: number = 0,
  allowBackorder: boolean = false
): { allowed: boolean; maxAddable: number; reason?: string } {
  if (requestedQuantity <= 0) {
    return { allowed: false, maxAddable: 0, reason: 'Quantity must be at least 1' };
  }

  const totalRequested = currentCartQuantity + requestedQuantity;

  if (allowBackorder) {
    return { allowed: true, maxAddable: requestedQuantity };
  }

  if (availableQuantity <= 0) {
    return { allowed: false, maxAddable: 0, reason: 'Out of stock' };
  }

  if (totalRequested > availableQuantity) {
    const maxAddable = Math.max(0, availableQuantity - currentCartQuantity);
    return {
      allowed: false,
      maxAddable,
      reason:
        maxAddable > 0
          ? `Only ${maxAddable} more can be added`
          : 'Maximum quantity already in cart',
    };
  }

  return { allowed: true, maxAddable: requestedQuantity };
}

/**
 * Get the maximum purchasable quantity for a product.
 */
export function getAvailableQuantity(
  stockQuantity: number,
  cartQuantity: number = 0,
  maxPerOrder?: number
): number {
  const available = Math.max(0, stockQuantity - cartQuantity);
  if (maxPerOrder !== undefined) {
    return Math.min(available, Math.max(0, maxPerOrder - cartQuantity));
  }
  return available;
}
