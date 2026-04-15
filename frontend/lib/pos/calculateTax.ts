// ── POS Tax Calculation Utilities ─────────────────────────────

export interface TaxConfig {
  enabled: boolean;
  rate: number;
  name: string;
  inclusive: boolean;
}

const DEFAULT_TAX_CONFIG: TaxConfig = {
  enabled: true,
  rate: 15, // Sri Lanka VAT
  name: 'VAT',
  inclusive: false,
};

/**
 * Calculate tax amount from a taxable base.
 * Rounds to 2 decimal places (half-up).
 */
export function calculateTaxAmount(taxableAmount: number, taxRate: number): number {
  if (taxRate <= 0 || taxableAmount <= 0) return 0;
  return Math.round(taxableAmount * (taxRate / 100) * 100) / 100;
}

/**
 * Get the taxable total (subtotal minus discount).
 */
export function calculateTaxableTotal(subtotal: number, discountAmount: number): number {
  return Math.max(0, subtotal - discountAmount);
}

/**
 * Calculate grand total = subtotal - discount + tax.
 */
export function calculateGrandTotal(
  subtotal: number,
  discountAmount: number,
  taxAmount: number
): number {
  return Math.round((subtotal - discountAmount + taxAmount) * 100) / 100;
}

/**
 * Full cart total calculation pipeline.
 */
export function calculateCartTotals(
  subtotal: number,
  discountAmount: number,
  taxConfig: TaxConfig = DEFAULT_TAX_CONFIG
) {
  const taxableTotal = calculateTaxableTotal(subtotal, discountAmount);
  const taxAmount = taxConfig.enabled ? calculateTaxAmount(taxableTotal, taxConfig.rate) : 0;
  const grandTotal = calculateGrandTotal(subtotal, discountAmount, taxAmount);

  return {
    subtotal,
    discountAmount,
    taxableTotal,
    taxRate: taxConfig.rate,
    taxName: taxConfig.name,
    taxAmount,
    grandTotal,
  };
}

export { DEFAULT_TAX_CONFIG };
