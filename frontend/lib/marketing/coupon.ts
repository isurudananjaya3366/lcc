/**
 * Coupon API Client
 */

import type {
  ValidateCouponRequest,
  ValidateCouponResponse,
  ApplyCouponRequest,
  ApplyCouponResponse,
  RemoveCouponResponse,
  CouponListItem,
} from '@/types/marketing/coupon.types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(error.message || `HTTP ${res.status}`);
  }
  return res.json();
}

/** Validate a coupon code against cart */
export async function validateCoupon(data: ValidateCouponRequest): Promise<ValidateCouponResponse> {
  return fetchJSON<ValidateCouponResponse>('/api/webstore/coupons/validate', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/** Apply a validated coupon to cart */
export async function applyCoupon(data: ApplyCouponRequest): Promise<ApplyCouponResponse> {
  return fetchJSON<ApplyCouponResponse>('/api/webstore/coupons/apply', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/** Remove applied coupon from cart */
export async function removeCoupon(code: string): Promise<RemoveCouponResponse> {
  return fetchJSON<RemoveCouponResponse>('/api/webstore/coupons/remove', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

/** Get available coupons for current user */
export async function getAvailableCoupons(): Promise<CouponListItem[]> {
  return fetchJSON<CouponListItem[]>('/api/webstore/coupons/available');
}

/** Get coupon details by code */
export async function getCouponByCode(code: string): Promise<ValidateCouponResponse> {
  return fetchJSON<ValidateCouponResponse>(`/api/webstore/coupons/${encodeURIComponent(code)}`);
}
