/**
 * Discount Calculation Utilities
 *
 * Supports percentage, fixed, buy-X-get-Y, and bulk discount types
 * with validation and stacking capabilities.
 */

// ─── Types ───────────────────────────────────────────────────────────────────

export enum DiscountType {
  PERCENTAGE = 'percentage',
  FIXED = 'fixed',
  BUY_X_GET_Y = 'buy_x_get_y',
  BULK = 'bulk',
}

export interface DiscountResult {
  originalAmount: number;
  discountAmount: number;
  finalAmount: number;
  discountPercentage: number;
}

export interface BulkTier {
  minQuantity: number;
  discountPercentage: number;
}

// ─── Core Calculations ───────────────────────────────────────────────────────

/**
 * Calculate a percentage discount.
 * @example calculatePercentageDiscount(1000, 20) → { discountAmount: 200, finalAmount: 800, ... }
 */
export function calculatePercentageDiscount(amount: number, percentage: number): DiscountResult {
  const clamped = Math.max(0, Math.min(100, percentage));
  const discountAmount = Math.round(((amount * clamped) / 100) * 100) / 100;
  return {
    originalAmount: amount,
    discountAmount,
    finalAmount: Math.max(0, amount - discountAmount),
    discountPercentage: clamped,
  };
}

/**
 * Calculate a fixed amount discount.
 * @example calculateFixedDiscount(1000, 150) → { discountAmount: 150, finalAmount: 850, ... }
 */
export function calculateFixedDiscount(amount: number, discount: number): DiscountResult {
  const clamped = Math.max(0, Math.min(amount, discount));
  return {
    originalAmount: amount,
    discountAmount: clamped,
    finalAmount: Math.max(0, amount - clamped),
    discountPercentage: amount > 0 ? Math.round((clamped / amount) * 100) : 0,
  };
}

/**
 * Calculate discount percentage from original and sale price.
 * @example calculateDiscountPercentage(1000, 800) → 20
 */
export function calculateDiscountPercentage(originalPrice: number, salePrice: number): number {
  if (originalPrice <= 0 || salePrice >= originalPrice) return 0;
  return Math.round(((originalPrice - salePrice) / originalPrice) * 100);
}

/**
 * Calculate the absolute savings amount.
 * @example calculateSaveAmount(1000, 800) → 200
 */
export function calculateSaveAmount(originalPrice: number, salePrice: number): number {
  return Math.max(0, originalPrice - salePrice);
}

/**
 * Apply a discount of a given type to an amount.
 */
export function applyDiscount(
  amount: number,
  discountValue: number,
  type: DiscountType
): DiscountResult {
  switch (type) {
    case DiscountType.PERCENTAGE:
      return calculatePercentageDiscount(amount, discountValue);
    case DiscountType.FIXED:
      return calculateFixedDiscount(amount, discountValue);
    default:
      return {
        originalAmount: amount,
        discountAmount: 0,
        finalAmount: amount,
        discountPercentage: 0,
      };
  }
}

// ─── Advanced Discounts ──────────────────────────────────────────────────────

/**
 * Calculate bulk/tiered discount based on quantity.
 * Uses the highest qualifying tier.
 * @example calculateBulkDiscount(500, 10, [{ minQuantity: 5, discountPercentage: 10 }]) → 10% off
 */
export function calculateBulkDiscount(
  unitPrice: number,
  quantity: number,
  tiers: BulkTier[]
): DiscountResult {
  const sorted = [...tiers].sort((a, b) => b.minQuantity - a.minQuantity);
  const tier = sorted.find((t) => quantity >= t.minQuantity);

  const amount = unitPrice * quantity;

  if (!tier) {
    return {
      originalAmount: amount,
      discountAmount: 0,
      finalAmount: amount,
      discountPercentage: 0,
    };
  }

  return calculatePercentageDiscount(amount, tier.discountPercentage);
}

/**
 * Calculate buy-X-get-Y discount.
 * @example calculateBuyXGetY(100, 6, 2, 1) → buy 2 get 1 free applied to 6 items
 */
export function calculateBuyXGetY(
  unitPrice: number,
  quantity: number,
  buyQuantity: number,
  freeQuantity: number
): DiscountResult {
  const amount = unitPrice * quantity;
  const groupSize = buyQuantity + freeQuantity;
  const fullGroups = Math.floor(quantity / groupSize);
  const freeItems = fullGroups * freeQuantity;
  const discountAmount = freeItems * unitPrice;

  return {
    originalAmount: amount,
    discountAmount,
    finalAmount: Math.max(0, amount - discountAmount),
    discountPercentage: amount > 0 ? Math.round((discountAmount / amount) * 100) : 0,
  };
}

/**
 * Apply multiple stacked discounts sequentially.
 * Each discount is applied to the running total (not original).
 */
export function calculateStackedDiscounts(
  amount: number,
  discounts: Array<{ value: number; type: DiscountType }>
): DiscountResult {
  let running = amount;
  let totalDiscount = 0;

  for (const d of discounts) {
    const result = applyDiscount(running, d.value, d.type);
    totalDiscount += result.discountAmount;
    running = result.finalAmount;
  }

  return {
    originalAmount: amount,
    discountAmount: totalDiscount,
    finalAmount: running,
    discountPercentage: amount > 0 ? Math.round((totalDiscount / amount) * 100) : 0,
  };
}

// ─── Validation ──────────────────────────────────────────────────────────────

/** Validate that a percentage discount value is within range */
export function isValidPercentage(value: number): boolean {
  return value >= 0 && value <= 100;
}

/** Validate that a discount amount doesn't exceed the original */
export function isValidFixedDiscount(amount: number, discount: number): boolean {
  return discount >= 0 && discount <= amount;
}
