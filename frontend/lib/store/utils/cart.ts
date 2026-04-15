/**
 * Cart Calculation Utilities
 *
 * Subtotal, tax, shipping, discount, and total calculations for the storefront cart.
 * Uses Sri Lankan 8% VAT rate and LKR thresholds.
 */

const TAX_RATE = 0.08; // 8% VAT
const FREE_SHIPPING_THRESHOLD = 5000; // ₨5,000
const DEFAULT_SHIPPING_RATE = 350; // ₨350

// ─── Types ───────────────────────────────────────────────────────────────────

export interface CartCalcItem {
  price: number;
  quantity: number;
  maxQuantity?: number;
}

export interface CartSummary {
  subtotal: number;
  discount: number;
  tax: number;
  shipping: number;
  total: number;
  itemCount: number;
  qualifiesForFreeShipping: boolean;
  amountToFreeShipping: number;
}

export interface CartValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

// ─── Line Item ───────────────────────────────────────────────────────────────

/**
 * Calculate total for a single cart item.
 * @example calculateItemTotal(500, 3) → 1500
 */
export function calculateItemTotal(price: number, quantity: number): number {
  return Math.round(price * quantity * 100) / 100;
}

// ─── Subtotal ────────────────────────────────────────────────────────────────

/**
 * Calculate cart subtotal from all items.
 */
export function calculateSubtotal(items: CartCalcItem[]): number {
  return items.reduce((sum, item) => sum + calculateItemTotal(item.price, item.quantity), 0);
}

// ─── Tax ─────────────────────────────────────────────────────────────────────

/**
 * Calculate tax (8% VAT) on a given amount.
 * @example calculateTax(1000) → 80
 */
export function calculateTax(amount: number, rate: number = TAX_RATE): number {
  return Math.round(amount * rate * 100) / 100;
}

// ─── Shipping ────────────────────────────────────────────────────────────────

/**
 * Calculate shipping cost. Free if subtotal >= ₨5,000.
 */
export function calculateShipping(
  subtotal: number,
  shippingRate: number = DEFAULT_SHIPPING_RATE
): number {
  if (subtotal >= FREE_SHIPPING_THRESHOLD) return 0;
  return shippingRate;
}

// ─── Discount ────────────────────────────────────────────────────────────────

/**
 * Calculate discount amount from a coupon.
 */
export function calculateDiscount(
  subtotal: number,
  discountValue: number,
  discountType: 'percentage' | 'fixed'
): number {
  if (discountType === 'percentage') {
    const pct = Math.max(0, Math.min(100, discountValue));
    return Math.round(((subtotal * pct) / 100) * 100) / 100;
  }
  return Math.min(subtotal, Math.max(0, discountValue));
}

// ─── Total ───────────────────────────────────────────────────────────────────

/**
 * Calculate the grand total.
 */
export function calculateTotal(
  subtotal: number,
  discount: number,
  tax: number,
  shipping: number
): number {
  return Math.max(0, subtotal - discount + tax + shipping);
}

// ─── Summary ─────────────────────────────────────────────────────────────────

/**
 * Get a complete cart summary with all computed values.
 */
export function getCartSummary(
  items: CartCalcItem[],
  discountValue: number = 0,
  discountType: 'percentage' | 'fixed' = 'fixed',
  shippingRate: number = DEFAULT_SHIPPING_RATE
): CartSummary {
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
  const subtotal = calculateSubtotal(items);
  const discount = calculateDiscount(subtotal, discountValue, discountType);
  const afterDiscount = subtotal - discount;
  const tax = calculateTax(afterDiscount);
  const shipping = calculateShipping(subtotal, shippingRate);
  const total = calculateTotal(subtotal, discount, tax, shipping);
  const qualifiesForFreeShipping = subtotal >= FREE_SHIPPING_THRESHOLD;
  const amountToFreeShipping = qualifiesForFreeShipping ? 0 : FREE_SHIPPING_THRESHOLD - subtotal;

  return {
    subtotal,
    discount,
    tax,
    shipping,
    total,
    itemCount,
    qualifiesForFreeShipping,
    amountToFreeShipping,
  };
}

// ─── Validation ──────────────────────────────────────────────────────────────

/**
 * Validate that cart prices are reasonable and quantities within bounds.
 */
export function validateCartPrices(items: CartCalcItem[]): CartValidation {
  const errors: string[] = [];
  const warnings: string[] = [];

  for (let i = 0; i < items.length; i++) {
    const item = items[i]!;
    if (item.price < 0) errors.push(`Item ${i + 1}: negative price`);
    if (item.quantity <= 0) errors.push(`Item ${i + 1}: invalid quantity`);
    if (item.maxQuantity && item.quantity > item.maxQuantity) {
      warnings.push(`Item ${i + 1}: quantity (${item.quantity}) exceeds max (${item.maxQuantity})`);
    }
  }

  return { isValid: errors.length === 0, errors, warnings };
}

/**
 * Check if order meets minimum total requirement.
 */
export function checkMinimumOrder(
  total: number,
  minimum: number = 0
): { meetsMinimum: boolean; shortfall: number } {
  return {
    meetsMinimum: total >= minimum,
    shortfall: Math.max(0, minimum - total),
  };
}

/**
 * Detect items that may have changed stock availability.
 */
export function detectStockChanges(
  items: Array<CartCalcItem & { isAvailable?: boolean }>
): string[] {
  const issues: string[] = [];
  for (let i = 0; i < items.length; i++) {
    const item = items[i]!;
    if (item.isAvailable === false) {
      issues.push(`Item ${i + 1} is no longer available`);
    }
    if (item.maxQuantity && item.quantity > item.maxQuantity) {
      issues.push(`Item ${i + 1}: only ${item.maxQuantity} available (requested ${item.quantity})`);
    }
  }
  return issues;
}
