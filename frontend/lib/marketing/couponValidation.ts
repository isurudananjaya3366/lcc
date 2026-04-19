/**
 * Coupon Validation Utilities — client-side validation logic.
 */

import type { DiscountType, CouponRestrictions } from '@/types/marketing/coupon.types';

// ── Task 09: Percentage Discount ────────────────────────────────

export function calculatePercentageDiscount(
  cartTotal: number,
  percentage: number,
  maxDiscount?: number
): number {
  const discount = Math.round((cartTotal * percentage) / 100);
  if (maxDiscount && discount > maxDiscount) return maxDiscount;
  return Math.min(discount, cartTotal);
}

// ── Task 10: Fixed Discount ─────────────────────────────────────

export function calculateFixedDiscount(cartTotal: number, fixedAmount: number): number {
  return Math.min(fixedAmount, cartTotal);
}

// ── Task 11: Free Shipping ──────────────────────────────────────

export function calculateFreeShippingDiscount(shippingCost: number): number {
  return shippingCost;
}

// ── Task 12: Minimum Order Validation ───────────────────────────

export interface MinOrderValidation {
  isValid: boolean;
  message: string;
  shortfall: number;
  percentComplete: number;
}

export function validateMinimumOrder(
  cartTotal: number,
  minimumOrder?: number
): MinOrderValidation {
  if (!minimumOrder || minimumOrder <= 0) {
    return { isValid: true, message: '', shortfall: 0, percentComplete: 100 };
  }

  const shortfall = Math.max(0, minimumOrder - cartTotal);
  const percentComplete = Math.min(100, Math.round((cartTotal / minimumOrder) * 100));

  return {
    isValid: cartTotal >= minimumOrder,
    message: shortfall > 0
      ? `Add ₨${shortfall.toLocaleString()} more to use this coupon (min: ₨${minimumOrder.toLocaleString()})`
      : '',
    shortfall,
    percentComplete,
  };
}

// ── Task 13: Expiry Validation ──────────────────────────────────

export interface ExpiryValidation {
  isValid: boolean;
  isExpired: boolean;
  isNotStarted: boolean;
  message: string;
  timeRemaining: number;
  urgencyLevel: 'high' | 'medium' | 'low' | 'none';
}

export function validateCouponExpiry(startDate: string, endDate: string): ExpiryValidation {
  const now = new Date();
  const start = new Date(startDate);
  const end = new Date(endDate);
  const timeRemaining = end.getTime() - now.getTime();
  const hoursRemaining = timeRemaining / (1000 * 60 * 60);

  if (now < start) {
    return {
      isValid: false, isExpired: false, isNotStarted: true,
      message: `This coupon starts on ${start.toLocaleDateString()}`,
      timeRemaining: 0, urgencyLevel: 'none',
    };
  }

  if (now > end) {
    return {
      isValid: false, isExpired: true, isNotStarted: false,
      message: 'This coupon has expired',
      timeRemaining: 0, urgencyLevel: 'none',
    };
  }

  const urgencyLevel = hoursRemaining < 24 ? 'high' : hoursRemaining < 72 ? 'medium' : 'low';

  return {
    isValid: true, isExpired: false, isNotStarted: false,
    message: urgencyLevel === 'high' ? 'Expires soon!' : '',
    timeRemaining, urgencyLevel,
  };
}

// ── Task 14: Usage Limit Validation ─────────────────────────────

export interface UsageLimitValidation {
  isValid: boolean;
  message: string;
  userUsageRemaining: number;
  totalUsageRemaining: number;
}

export function validateUsageLimits(
  userUsageCount: number,
  usageLimitPerUser: number | undefined,
  totalUsageCount: number,
  totalUsageLimit: number | undefined
): UsageLimitValidation {
  if (usageLimitPerUser && userUsageCount >= usageLimitPerUser) {
    return {
      isValid: false,
      message: 'You have reached the usage limit for this coupon',
      userUsageRemaining: 0,
      totalUsageRemaining: totalUsageLimit ? totalUsageLimit - totalUsageCount : Infinity,
    };
  }

  if (totalUsageLimit && totalUsageCount >= totalUsageLimit) {
    return {
      isValid: false,
      message: 'This coupon has reached its maximum usage',
      userUsageRemaining: usageLimitPerUser ? usageLimitPerUser - userUsageCount : Infinity,
      totalUsageRemaining: 0,
    };
  }

  return {
    isValid: true,
    message: '',
    userUsageRemaining: usageLimitPerUser ? usageLimitPerUser - userUsageCount : Infinity,
    totalUsageRemaining: totalUsageLimit ? totalUsageLimit - totalUsageCount : Infinity,
  };
}

// ── Task 15: Product-Specific Validation ────────────────────────

export interface ProductRestrictionValidation {
  isValid: boolean;
  message: string;
  applicableItems: string[];
  excludedItems: string[];
}

export function validateProductRestriction(
  cartProductIds: string[],
  applicableProductIds?: string[],
  excludedProductIds?: string[]
): ProductRestrictionValidation {
  if (!applicableProductIds?.length && !excludedProductIds?.length) {
    return { isValid: true, message: '', applicableItems: cartProductIds, excludedItems: [] };
  }

  const excluded = excludedProductIds
    ? cartProductIds.filter((id) => excludedProductIds.includes(id))
    : [];

  const applicable = applicableProductIds
    ? cartProductIds.filter((id) => applicableProductIds.includes(id))
    : cartProductIds.filter((id) => !excluded.includes(id));

  return {
    isValid: applicable.length > 0,
    message: applicable.length === 0 ? 'No eligible items in cart for this coupon' : '',
    applicableItems: applicable,
    excludedItems: excluded,
  };
}

// ── Task 16: Category Validation ────────────────────────────────

export function validateCategoryRestriction(
  cartCategoryIds: string[],
  applicableCategoryIds?: string[],
  excludedCategoryIds?: string[]
): ProductRestrictionValidation {
  if (!applicableCategoryIds?.length && !excludedCategoryIds?.length) {
    return { isValid: true, message: '', applicableItems: cartCategoryIds, excludedItems: [] };
  }

  const excluded = excludedCategoryIds
    ? cartCategoryIds.filter((id) => excludedCategoryIds.includes(id))
    : [];

  const applicable = applicableCategoryIds
    ? cartCategoryIds.filter((id) => applicableCategoryIds.includes(id))
    : cartCategoryIds.filter((id) => !excluded.includes(id));

  return {
    isValid: applicable.length > 0,
    message: applicable.length === 0 ? 'No eligible categories in cart for this coupon' : '',
    applicableItems: applicable,
    excludedItems: excluded,
  };
}

// ── Task 17: First Order Validation ─────────────────────────────

export function validateFirstOrderCoupon(
  orderCount: number,
  isFirstOrderOnly?: boolean
): { isValid: boolean; message: string } {
  if (!isFirstOrderOnly) return { isValid: true, message: '' };
  if (orderCount > 0) {
    return { isValid: false, message: 'This coupon is only valid for first-time orders' };
  }
  return { isValid: true, message: '' };
}

// ── Unified Discount Calculator ─────────────────────────────────

export function calculateDiscount(
  discountType: DiscountType,
  discountValue: number,
  cartTotal: number,
  shippingCost: number = 0,
  maxDiscount?: number
): number {
  switch (discountType) {
    case 'percentage':
      return calculatePercentageDiscount(cartTotal, discountValue, maxDiscount);
    case 'fixed_amount':
      return calculateFixedDiscount(cartTotal, discountValue);
    case 'free_shipping':
      return calculateFreeShippingDiscount(shippingCost);
    default:
      return 0;
  }
}
