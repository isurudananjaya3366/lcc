/**
 * Store Utility Tests — Cart Calculations
 */

import {
  calculateItemTotal,
  calculateSubtotal,
  calculateTax,
  calculateShipping,
  calculateDiscount,
  calculateTotal,
  getCartSummary,
  checkMinimumOrder,
} from '@/lib/store/utils/cart';

const mockItems = [
  { productId: '1', name: 'Item A', price: 1000, quantity: 2, image: '', slug: 'a' },
  { productId: '2', name: 'Item B', price: 500, quantity: 1, image: '', slug: 'b' },
];

describe('calculateItemTotal', () => {
  it('multiplies price by quantity', () => {
    expect(calculateItemTotal(1000, 2)).toBe(2000);
  });

  it('handles zero quantity', () => {
    expect(calculateItemTotal(1000, 0)).toBe(0);
  });
});

describe('calculateSubtotal', () => {
  it('sums all item totals', () => {
    const result = calculateSubtotal(mockItems);
    expect(result).toBe(2500); // 1000*2 + 500*1
  });

  it('returns 0 for empty array', () => {
    expect(calculateSubtotal([])).toBe(0);
  });
});

describe('calculateTax', () => {
  it('calculates 8% VAT', () => {
    const result = calculateTax(1000);
    expect(result).toBe(80); // 8% of 1000
  });

  it('handles zero', () => {
    expect(calculateTax(0)).toBe(0);
  });
});

describe('calculateShipping', () => {
  it('returns 0 (free) for orders over 5000 LKR', () => {
    const result = calculateShipping(5000);
    expect(result).toBe(0);
  });

  it('charges shipping for orders under 5000 LKR', () => {
    const result = calculateShipping(2000);
    expect(result).toBeGreaterThan(0);
  });
});

describe('calculateDiscount', () => {
  it('calculates discount from a code', () => {
    const result = calculateDiscount(1000, 10, 'percentage');
    expect(result).toBe(100);
  });

  it('returns 0 when no discount applied', () => {
    const result = calculateDiscount(1000, 0, 'fixed');
    expect(result).toBe(0);
  });
});

describe('calculateTotal', () => {
  it('sums subtotal + tax + shipping - discount', () => {
    const result = calculateTotal(2500, 100, 200, 350);
    expect(result).toBe(2950); // 2500 - 100 + 200 + 350
  });
});

describe('getCartSummary', () => {
  it('returns a complete cart summary object', () => {
    const summary = getCartSummary(mockItems);
    expect(summary).toHaveProperty('subtotal');
    expect(summary).toHaveProperty('tax');
    expect(summary).toHaveProperty('shipping');
    expect(summary).toHaveProperty('total');
    expect(summary.subtotal).toBe(2500);
  });
});

describe('checkMinimumOrder', () => {
  it('passes for orders meeting minimum', () => {
    const result = checkMinimumOrder(1000, 500);
    expect(result.meetsMinimum).toBe(true);
  });

  it('fails for orders below minimum', () => {
    const result = checkMinimumOrder(200, 500);
    expect(result.meetsMinimum).toBe(false);
    expect(result.shortfall).toBe(300);
  });
});
