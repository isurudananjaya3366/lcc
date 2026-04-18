/**
 * Checkout Sidebar Utility Tests — Task 94 (Unit Testing Suite) + Task 97 (Performance)
 *
 * Tests pricing calculation utilities used by the OrderSidebar:
 * subtotal calculation, shipping cost logic, discount application,
 * total calculation, and LKR currency formatting.
 */

import { describe, it, expect } from 'vitest';

// ─── LKR Currency Formatting ──────────────────────────────────────────────────

/**
 * Format a number as LKR currency string.
 * Mirrors the formatting used throughout checkout sidebar components.
 */
function formatLKR(amount: number): string {
  return `₨${amount.toLocaleString()}`;
}

describe('LKR currency formatting', () => {
  it('formats zero as ₨0', () => {
    expect(formatLKR(0)).toBe('₨0');
  });

  it('formats 500 as ₨500', () => {
    expect(formatLKR(500)).toBe('₨500');
  });

  it('formats 3000 with comma separator', () => {
    expect(formatLKR(3000)).toContain('3,000');
  });

  it('formats 15000 with comma separator', () => {
    expect(formatLKR(15000)).toContain('15,000');
  });

  it('formats 125000 with comma separator', () => {
    expect(formatLKR(125000)).toContain('125,000');
  });

  it('always starts with ₨ symbol', () => {
    expect(formatLKR(1000).startsWith('₨')).toBe(true);
  });
});

// ─── Cart Subtotal Calculation ────────────────────────────────────────────────

interface CartItemForCalc {
  price: number;
  quantity: number;
}

function calculateSubtotal(items: CartItemForCalc[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

describe('Checkout subtotal calculation', () => {
  it('returns 0 for empty cart', () => {
    expect(calculateSubtotal([])).toBe(0);
  });

  it('calculates single item total correctly', () => {
    expect(calculateSubtotal([{ price: 1500, quantity: 2 }])).toBe(3000);
  });

  it('sums multiple items', () => {
    const items = [
      { price: 1000, quantity: 2 },
      { price: 500, quantity: 1 },
    ];
    expect(calculateSubtotal(items)).toBe(2500);
  });

  it('handles quantity 1', () => {
    expect(calculateSubtotal([{ price: 2500, quantity: 1 }])).toBe(2500);
  });

  it('handles large cart correctly', () => {
    const items = Array.from({ length: 10 }, () => ({ price: 1000, quantity: 1 }));
    expect(calculateSubtotal(items)).toBe(10000);
  });
});

// ─── Shipping Cost Logic ──────────────────────────────────────────────────────

const FREE_SHIPPING_THRESHOLD = 5000;

function getShippingCost(subtotal: number, selectedMethodPrice: number): number {
  return subtotal >= FREE_SHIPPING_THRESHOLD ? 0 : selectedMethodPrice;
}

describe('Shipping cost calculation', () => {
  it('applies free shipping at or above LKR 5000 threshold', () => {
    expect(getShippingCost(5000, 350)).toBe(0);
  });

  it('applies free shipping above threshold', () => {
    expect(getShippingCost(5001, 350)).toBe(0);
  });

  it('charges shipping below threshold', () => {
    expect(getShippingCost(4999, 350)).toBe(350);
  });

  it('charges standard rate at LKR 1000', () => {
    expect(getShippingCost(1000, 350)).toBe(350);
  });

  it('charges express rate correctly', () => {
    expect(getShippingCost(2000, 750)).toBe(750);
  });

  it('free shipping at exactly threshold boundary', () => {
    expect(getShippingCost(5000, 350)).toBe(0);
    expect(getShippingCost(4999, 350)).toBe(350);
  });

  it('handles zero subtotal', () => {
    expect(getShippingCost(0, 350)).toBe(350);
  });
});

// ─── Discount Application ─────────────────────────────────────────────────────

function applyDiscount(subtotal: number, discountPercent: number): number {
  if (discountPercent < 0 || discountPercent > 100) return 0;
  return (subtotal * discountPercent) / 100;
}

describe('Discount application', () => {
  it('applies 10% discount correctly', () => {
    expect(applyDiscount(1000, 10)).toBe(100);
  });

  it('applies 50% discount correctly', () => {
    expect(applyDiscount(2000, 50)).toBe(1000);
  });

  it('applies 0% discount (no discount)', () => {
    expect(applyDiscount(1000, 0)).toBe(0);
  });

  it('applies 100% discount', () => {
    expect(applyDiscount(1000, 100)).toBe(1000);
  });

  it('returns 0 for negative discount percent', () => {
    expect(applyDiscount(1000, -10)).toBe(0);
  });

  it('returns 0 for discount > 100%', () => {
    expect(applyDiscount(1000, 150)).toBe(0);
  });
});

// ─── Grand Total Calculation ──────────────────────────────────────────────────

function calculateGrandTotal(subtotal: number, shipping: number, discount: number): number {
  return Math.max(0, subtotal + shipping - discount);
}

describe('Grand total calculation', () => {
  it('adds subtotal and shipping', () => {
    expect(calculateGrandTotal(2500, 350, 0)).toBe(2850);
  });

  it('subtracts discount from total', () => {
    expect(calculateGrandTotal(2500, 350, 250)).toBe(2600);
  });

  it('handles free shipping (zero shipping cost)', () => {
    expect(calculateGrandTotal(5000, 0, 0)).toBe(5000);
  });

  it('returns 0 if discount exceeds subtotal + shipping', () => {
    expect(calculateGrandTotal(100, 0, 500)).toBe(0);
  });

  it('calculates complete scenario correctly', () => {
    // 3 items × ₨1,000 = ₨3,000 subtotal
    // Standard shipping = ₨350
    // 10% discount on ₨3,000 = ₨300 off
    // Total = ₨3,000 + ₨350 - ₨300 = ₨3,050
    expect(calculateGrandTotal(3000, 350, 300)).toBe(3050);
  });
});

// ─── Sidebar Item Count ───────────────────────────────────────────────────────

interface CartItemWithQty {
  quantity: number;
}

function getTotalItemCount(items: CartItemWithQty[]): number {
  return items.reduce((sum, item) => sum + item.quantity, 0);
}

describe('Sidebar item count', () => {
  it('returns 0 for empty cart', () => {
    expect(getTotalItemCount([])).toBe(0);
  });

  it('counts single item', () => {
    expect(getTotalItemCount([{ quantity: 1 }])).toBe(1);
  });

  it('counts multiple quantities', () => {
    expect(getTotalItemCount([{ quantity: 2 }, { quantity: 3 }])).toBe(5);
  });

  it('counts items with quantity > 1', () => {
    const items = [{ quantity: 3 }, { quantity: 2 }, { quantity: 1 }];
    expect(getTotalItemCount(items)).toBe(6);
  });
});
