/**
 * POS Total Calculator Utilities
 * Provides helper functions for price, discount, and change calculations.
 */

/** Round to 2 decimal places (currency precision) */
export function roundToCurrency(amount: number): number {
  return Math.round(amount * 100) / 100;
}

/** Format a number as LKR currency string */
export function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/** Calculate subtotal from line items */
export function calculateSubtotal(items: Array<{ unitPrice: number; quantity: number }>): number {
  return roundToCurrency(items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0));
}

/** Calculate discount amount from subtotal and discount config */
export function calculateDiscount(
  subtotal: number,
  discount: { type: 'percentage' | 'fixed'; value: number } | null
): number {
  if (!discount) return 0;
  if (discount.type === 'percentage') {
    return roundToCurrency(subtotal * (discount.value / 100));
  }
  return roundToCurrency(Math.min(discount.value, subtotal));
}

/** Calculate change to return to customer */
export function calculateChange(grandTotal: number, paidAmount: number): number {
  const change = paidAmount - grandTotal;
  return change > 0 ? roundToCurrency(change) : 0;
}

/** Validate that an amount is a positive finite number */
export function isValidAmount(value: unknown): value is number {
  return typeof value === 'number' && isFinite(value) && value >= 0;
}

/** Clamp a number between min and max */
export function clampAmount(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}
