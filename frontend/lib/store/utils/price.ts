/**
 * Price Display Utilities
 *
 * Generates structured price display data with sale indicators,
 * discount badges, strikethrough pricing, and accessibility labels.
 */

import { formatLKR, formatCurrencyRange } from './currency';

// ─── Types ───────────────────────────────────────────────────────────────────

export interface PriceDisplay {
  displayPrice: string;
  originalPrice?: string;
  discountBadge?: string;
  isOnSale: boolean;
  isFree: boolean;
  cssClasses: string;
  ariaLabel: string;
}

// ─── Core ────────────────────────────────────────────────────────────────────

/**
 * Generate a structured price display object.
 * @example displayPrice(1000, 1500) → { displayPrice: "₨ 1,000.00", originalPrice: "₨ 1,500.00", isOnSale: true, ... }
 */
export function displayPrice(price: number, compareAtPrice?: number): PriceDisplay {
  const isFree = price === 0;
  const isOnSale = !!compareAtPrice && compareAtPrice > price && !isFree;

  const cssClasses = ['price', isOnSale ? 'price--sale' : '', isFree ? 'price--free' : '']
    .filter(Boolean)
    .join(' ');

  let ariaLabel: string;
  if (isFree) {
    ariaLabel = 'Free';
  } else if (isOnSale && compareAtPrice) {
    const pct = Math.round(((compareAtPrice - price) / compareAtPrice) * 100);
    ariaLabel = `${formatLKR(price)}, was ${formatLKR(compareAtPrice)}, ${pct}% off`;
  } else {
    ariaLabel = formatLKR(price);
  }

  return {
    displayPrice: isFree ? 'Free' : formatLKR(price),
    originalPrice: isOnSale && compareAtPrice ? formatLKR(compareAtPrice) : undefined,
    discountBadge: isOnSale && compareAtPrice ? getDiscountBadge(price, compareAtPrice) : undefined,
    isOnSale,
    isFree,
    cssClasses,
    ariaLabel,
  };
}

/**
 * Format a price range for products with variants.
 * @example formatPriceRange(800, 2500) → "₨ 800.00 – ₨ 2,500.00"
 */
export function formatPriceRange(minPrice: number, maxPrice: number): string {
  return formatCurrencyRange(minPrice, maxPrice);
}

/**
 * Get a discount badge string.
 * @example getDiscountBadge(800, 1000) → "-20%"
 */
export function getDiscountBadge(salePrice: number, originalPrice: number): string {
  if (originalPrice <= 0 || salePrice >= originalPrice) return '';
  const pct = Math.round(((originalPrice - salePrice) / originalPrice) * 100);
  return `-${pct}%`;
}

/**
 * Format a price with strikethrough for display in HTML.
 * @returns {{ current: string; original?: string }}
 */
export function formatStrikethroughPrice(
  price: number,
  compareAtPrice?: number
): { current: string; original?: string } {
  return {
    current: formatLKR(price),
    original: compareAtPrice && compareAtPrice > price ? formatLKR(compareAtPrice) : undefined,
  };
}

/**
 * Get a summary of cart pricing.
 */
export function getPriceSummary(
  items: Array<{ price: number; quantity: number; compareAtPrice?: number }>
): {
  subtotal: number;
  totalSavings: number;
  itemCount: number;
} {
  let subtotal = 0;
  let totalSavings = 0;
  let itemCount = 0;

  for (const item of items) {
    subtotal += item.price * item.quantity;
    itemCount += item.quantity;
    if (item.compareAtPrice && item.compareAtPrice > item.price) {
      totalSavings += (item.compareAtPrice - item.price) * item.quantity;
    }
  }

  return { subtotal, totalSavings, itemCount };
}
