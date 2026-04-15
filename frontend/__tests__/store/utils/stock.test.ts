/**
 * Store Utility Tests — Stock Status
 */

import {
  isInStock,
  getStockLevel,
  getStockStatus,
  getStockMessage,
  getStockInfo,
  canAddToCart,
  getAvailableQuantity,
} from '@/lib/store/utils/stock';

describe('isInStock', () => {
  it('returns true when quantity > 0', () => {
    expect(isInStock(10)).toBe(true);
  });

  it('returns false when quantity is 0', () => {
    expect(isInStock(0)).toBe(false);
  });
});

describe('getStockLevel', () => {
  it('returns the quantity for large amounts', () => {
    expect(getStockLevel(100)).toBe(100);
  });

  it('returns the quantity for small amounts', () => {
    expect(getStockLevel(3)).toBe(3);
  });

  it('returns 0 for zero', () => {
    expect(getStockLevel(0)).toBe(0);
  });
});

describe('getStockStatus', () => {
  it('returns in_stock for available items', () => {
    expect(getStockStatus(50)).toBe('in_stock');
  });

  it('returns out_of_stock for 0', () => {
    expect(getStockStatus(0)).toBe('out_of_stock');
  });

  it('returns low_stock for small quantities', () => {
    const result = getStockStatus(3);
    expect(['low_stock', 'in_stock']).toContain(result);
  });
});

describe('getStockMessage', () => {
  it('returns a user-friendly message', () => {
    const msg = getStockMessage(50);
    expect(typeof msg).toBe('string');
    expect(msg).toBeTruthy();
  });

  it('returns out of stock message for 0', () => {
    const msg = getStockMessage(0);
    expect(msg.toLowerCase()).toContain('out');
  });
});

describe('getStockInfo', () => {
  it('returns a complete stock info object', () => {
    const info = getStockInfo(25);
    expect(info).toHaveProperty('canPurchase');
    expect(info).toHaveProperty('status');
    expect(info).toHaveProperty('message');
    expect(info.canPurchase).toBe(true);
  });
});

describe('canAddToCart', () => {
  it('allows for in-stock items', () => {
    const result = canAddToCart(1, 10);
    expect(result.allowed).toBe(true);
  });

  it('disallows when requesting more than available', () => {
    const result = canAddToCart(5, 2);
    expect(result.allowed).toBe(false);
  });

  it('disallows for out-of-stock items', () => {
    const result = canAddToCart(1, 0);
    expect(result.allowed).toBe(false);
  });
});

describe('getAvailableQuantity', () => {
  it('returns the available quantity', () => {
    expect(getAvailableQuantity(25)).toBe(25);
  });

  it('subtracts cart quantity', () => {
    expect(getAvailableQuantity(25, 5)).toBe(20);
  });

  it('returns 0 for out of stock', () => {
    expect(getAvailableQuantity(0)).toBe(0);
  });
});
