/**
 * Store Utility Tests — Price Display
 */

import {
  displayPrice,
  formatPriceRange,
  getDiscountBadge,
  formatStrikethroughPrice,
  getPriceSummary,
} from '@/lib/store/utils/price';

describe('displayPrice', () => {
  it('returns a PriceDisplay object', () => {
    const result = displayPrice(1000);
    expect(result).toHaveProperty('displayPrice');
    expect(typeof result.displayPrice).toBe('string');
  });

  it('shows sale price when compareAtPrice is higher', () => {
    const result = displayPrice(800, 1000);
    expect(result.isOnSale).toBe(true);
  });

  it('handles zero price', () => {
    const result = displayPrice(0);
    expect(result.isFree).toBe(true);
  });
});

describe('formatPriceRange', () => {
  it('formats a min-max range', () => {
    const result = formatPriceRange(100, 500);
    expect(typeof result).toBe('string');
    expect(result).toBeTruthy();
  });
});

describe('getDiscountBadge', () => {
  it('calculates discount percentage', () => {
    const result = getDiscountBadge(800, 1000);
    expect(result).toContain('20');
  });

  it('returns empty for no discount', () => {
    const result = getDiscountBadge(1000, 1000);
    expect(result).toBeFalsy();
  });
});

describe('formatStrikethroughPrice', () => {
  it('returns formatted original price', () => {
    const result = formatStrikethroughPrice(1000);
    expect(typeof result).toBe('object');
    expect(typeof result.current).toBe('string');
    expect(result.current).toBeTruthy();
  });
});

describe('getPriceSummary', () => {
  it('returns a complete price summary', () => {
    const items = [{ price: 1000, quantity: 2, compareAtPrice: 1200 }];
    const result = getPriceSummary(items);
    expect(result).toHaveProperty('subtotal');
    expect(result).toHaveProperty('totalSavings');
    expect(result).toHaveProperty('itemCount');
  });
});
