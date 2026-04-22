/**
 * Store Utility Tests — Discount Calculations
 */

import {
  calculatePercentageDiscount,
  calculateFixedDiscount,
  applyDiscount,
  calculateBulkDiscount,
  calculateBuyXGetY,
  calculateStackedDiscounts,
  DiscountType,
} from '@/lib/store/utils/discount';

describe('calculatePercentageDiscount', () => {
  it('calculates 20% off 1000', () => {
    const result = calculatePercentageDiscount(1000, 20);
    expect(result.discountAmount).toBe(200);
    expect(result.finalAmount).toBe(800);
  });

  it('returns 0 for 0%', () => {
    expect(calculatePercentageDiscount(1000, 0).discountAmount).toBe(0);
  });

  it('handles 100%', () => {
    expect(calculatePercentageDiscount(1000, 100).discountAmount).toBe(1000);
  });
});

describe('calculateFixedDiscount', () => {
  it('subtracts a fixed amount', () => {
    const result = calculateFixedDiscount(1000, 200);
    expect(result.discountAmount).toBe(200);
    expect(result.finalAmount).toBe(800);
  });

  it('caps at original price', () => {
    const result = calculateFixedDiscount(100, 200);
    expect(result.discountAmount).toBeLessThanOrEqual(100);
  });
});

describe('applyDiscount', () => {
  it('applies percentage discount', () => {
    const result = applyDiscount(1000, 10, DiscountType.PERCENTAGE);
    expect(result.finalAmount).toBe(900);
  });

  it('applies fixed discount', () => {
    const result = applyDiscount(1000, 150, DiscountType.FIXED);
    expect(result.finalAmount).toBe(850);
  });

  it('never goes below 0', () => {
    const result = applyDiscount(100, 200, DiscountType.FIXED);
    expect(result.finalAmount).toBeGreaterThanOrEqual(0);
  });
});

describe('calculateBulkDiscount', () => {
  it('applies tiered discount for higher quantities', () => {
    const tiers: import('@/lib/store/utils/discount').BulkTier[] = [
      { minQuantity: 5, discountPercentage: 5 },
      { minQuantity: 10, discountPercentage: 10 },
    ];
    const result = calculateBulkDiscount(1000, 10, tiers);
    expect(result.discountAmount).toBe(1000); // 10% of 1000*10
  });

  it('returns 0 when below all tiers', () => {
    const tiers: import('@/lib/store/utils/discount').BulkTier[] = [
      { minQuantity: 5, discountPercentage: 5 },
    ];
    const result = calculateBulkDiscount(1000, 2, tiers);
    expect(result.discountAmount).toBe(0);
  });
});

describe('calculateBuyXGetY', () => {
  it('calculates free items for buy 2 get 1', () => {
    const result = calculateBuyXGetY(500, 3, 2, 1);
    expect(result.discountAmount).toBeGreaterThan(0);
    expect(result.finalAmount).toBeLessThan(result.originalAmount);
  });
});

describe('calculateStackedDiscounts', () => {
  it('applies multiple discounts sequentially', () => {
    const discounts = [
      { type: DiscountType.PERCENTAGE as const, value: 10 },
      { type: DiscountType.FIXED as const, value: 50 },
    ];
    const result = calculateStackedDiscounts(1000, discounts);
    expect(result.finalAmount).toBeLessThan(1000);
    expect(result.finalAmount).toBeGreaterThan(0);
  });
});
