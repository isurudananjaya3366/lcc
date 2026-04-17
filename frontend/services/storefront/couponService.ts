/**
 * Client-side coupon validation service.
 * Hardcoded test coupons until backend API is available.
 */

// ─── Types ──────────────────────────────────────────────────────────────────

export interface CouponValidationResult {
  valid: boolean;
  type?: 'percentage' | 'fixed';
  value?: number;
  error?: string;
}

// ─── Test Coupons ───────────────────────────────────────────────────────────

interface TestCoupon {
  type: 'percentage' | 'fixed';
  value: number;
}

const TEST_COUPONS: Record<string, TestCoupon> = {
  SAVE10: { type: 'percentage', value: 10 },
  SAVE20: { type: 'percentage', value: 20 },
  FLAT500: { type: 'fixed', value: 500 },
  FLAT1000: { type: 'fixed', value: 1000 },
};

// ─── Validation ─────────────────────────────────────────────────────────────

/**
 * Validate a coupon code against hardcoded test coupons.
 * Simulates an API call with a 300ms delay.
 */
export async function validateCoupon(code: string): Promise<CouponValidationResult> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 300));

  const normalised = code.trim().toUpperCase();

  if (!normalised) {
    return { valid: false, error: 'Please enter a coupon code' };
  }

  const coupon = TEST_COUPONS[normalised];

  if (!coupon) {
    return { valid: false, error: 'Invalid coupon code' };
  }

  return { valid: true, type: coupon.type, value: coupon.value };
}
