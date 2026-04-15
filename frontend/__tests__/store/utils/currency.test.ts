/**
 * Store Utility Tests — Currency
 */

import {
  formatCurrency,
  formatLKR,
  formatCompactCurrency,
  parseCurrency,
  formatCurrencyRange,
} from '@/lib/store/utils/currency';

describe('formatCurrency', () => {
  it('formats a number with LKR currency', () => {
    const result = formatCurrency(1250);
    expect(result).toContain('1,250');
  });

  it('handles zero', () => {
    const result = formatCurrency(0);
    expect(result).toContain('0');
  });

  it('handles negative numbers', () => {
    const result = formatCurrency(-500);
    expect(result).toContain('500');
  });

  it('formats with 2 decimal places', () => {
    const result = formatCurrency(99.5);
    expect(result).toMatch(/99\.50/);
  });
});

describe('formatLKR', () => {
  it('formats with LKR symbol', () => {
    const result = formatLKR(1250);
    expect(result).toBeTruthy();
    expect(typeof result).toBe('string');
  });

  it('handles large numbers', () => {
    const result = formatLKR(1000000);
    expect(result).toContain('1,000,000');
  });
});

describe('formatCompactCurrency', () => {
  it('formats thousands compactly', () => {
    const result = formatCompactCurrency(5000);
    expect(result).toBeTruthy();
  });

  it('formats lakhs compactly', () => {
    const result = formatCompactCurrency(500000);
    expect(result).toBeTruthy();
  });
});

describe('parseCurrency', () => {
  it('parses a formatted currency string to number', () => {
    const result = parseCurrency('1,250.00');
    expect(result).toBe(1250);
  });

  it('handles strings with currency symbols', () => {
    const result = parseCurrency('Rs. 1,250.00');
    expect(result).toBe(1250);
  });

  it('returns 0 for invalid input', () => {
    const result = parseCurrency('abc');
    expect(result).toBe(0);
  });
});

describe('formatCurrencyRange', () => {
  it('formats a price range', () => {
    const result = formatCurrencyRange(100, 500);
    expect(result).toBeTruthy();
    expect(typeof result).toBe('string');
  });
});
