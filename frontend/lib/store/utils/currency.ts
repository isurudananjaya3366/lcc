/**
 * Currency Utilities
 *
 * LKR currency formatting, parsing, and conversion for the LankaCommerce storefront.
 * Uses South Asian numbering convention (lakhs/crores) and Intl.NumberFormat.
 */

const LKR_LOCALE = 'en-LK';
const LKR_CODE = 'LKR';
const LKR_SYMBOL = '₨';

// ─── Core Formatting ─────────────────────────────────────────────────────────

/**
 * Format a number as LKR currency.
 * @example formatCurrency(1234.5) → "₨ 1,234.50"
 */
export function formatCurrency(
  amount: number,
  options?: {
    hideSymbol?: boolean;
    decimals?: number;
    useCode?: boolean;
  }
): string {
  const decimals = options?.decimals ?? 2;
  const formatted = new Intl.NumberFormat(LKR_LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(Math.abs(amount));

  const sign = amount < 0 ? '-' : '';

  if (options?.hideSymbol) return `${sign}${formatted}`;
  if (options?.useCode) return `${sign}${LKR_CODE} ${formatted}`;
  return `${sign}${LKR_SYMBOL} ${formatted}`;
}

/**
 * Shorthand for formatCurrency with default options.
 * @example formatLKR(2500) → "₨ 2,500.00"
 */
export function formatLKR(amount: number): string {
  return formatCurrency(amount);
}

/**
 * Format currency with compact notation (K, L, M, Cr).
 * Uses South Asian conventions: L = Lakh (100K), Cr = Crore (10M).
 * @example formatCompactCurrency(150000) → "₨ 1.5L"
 * @example formatCompactCurrency(12500000) → "₨ 1.25Cr"
 */
export function formatCompactCurrency(amount: number): string {
  const abs = Math.abs(amount);
  const sign = amount < 0 ? '-' : '';

  if (abs >= 10_000_000) {
    const crores = abs / 10_000_000;
    return `${sign}${LKR_SYMBOL} ${crores.toFixed(crores % 1 === 0 ? 0 : 2)}Cr`;
  }
  if (abs >= 100_000) {
    const lakhs = abs / 100_000;
    return `${sign}${LKR_SYMBOL} ${lakhs.toFixed(lakhs % 1 === 0 ? 0 : 1)}L`;
  }
  if (abs >= 1_000) {
    const thousands = abs / 1_000;
    return `${sign}${LKR_SYMBOL} ${thousands.toFixed(thousands % 1 === 0 ? 0 : 1)}K`;
  }
  return formatCurrency(amount);
}

// ─── Parsing ─────────────────────────────────────────────────────────────────

/**
 * Parse a currency string back to a number.
 * Handles "₨", "Rs.", "LKR", commas, and whitespace.
 * @example parseCurrency("₨ 1,234.50") → 1234.5
 * @example parseCurrency("LKR 100") → 100
 */
export function parseCurrency(value: string): number {
  const cleaned = value
    .replace(/[₨රු]/g, '')
    .replace(/Rs\.?/gi, '')
    .replace(/LKR/gi, '')
    .replace(/,/g, '')
    .replace(/\s/g, '')
    .trim();

  const result = parseFloat(cleaned);
  return isNaN(result) ? 0 : result;
}

// ─── Range Formatting ────────────────────────────────────────────────────────

/**
 * Format a price range.
 * @example formatCurrencyRange(100, 500) → "₨ 100.00 – ₨ 500.00"
 * @example formatCurrencyRange(100, 100) → "₨ 100.00"
 */
export function formatCurrencyRange(min: number, max: number): string {
  if (min === max) return formatLKR(min);
  return `${formatLKR(min)} – ${formatLKR(max)}`;
}

// ─── Conversion ──────────────────────────────────────────────────────────────

/**
 * Simple currency conversion (for display purposes only).
 * Uses static rates — not suitable for financial calculations.
 */
export function convertCurrency(
  amount: number,
  fromCode: string,
  toCode: string,
  rates: Record<string, number>
): number {
  if (fromCode === toCode) return amount;

  const fromRate = rates[fromCode];
  const toRate = rates[toCode];

  if (!fromRate || !toRate) {
    throw new Error(`Missing exchange rate for ${fromCode} or ${toCode}`);
  }

  // Convert to base (USD assumed) then to target
  return (amount / fromRate) * toRate;
}
