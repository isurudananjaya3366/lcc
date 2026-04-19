'use client';

import { createStore } from '../utils';
import type { Coupon, DiscountType } from '@/types/marketing/coupon.types';

interface CouponState {
  appliedCoupon: Coupon | null;
  discountAmount: number;
  isLoading: boolean;
  error: string | null;

  // Actions
  setAppliedCoupon: (coupon: Coupon, discountAmount: number) => void;
  removeCoupon: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;

  // Selectors
  hasAppliedCoupon: () => boolean;
  getDiscountDisplay: () => string;
}

export const useCouponStore = createStore<CouponState>(
  'coupon-store',
  (set, get) => ({
    appliedCoupon: null,
    discountAmount: 0,
    isLoading: false,
    error: null,

    setAppliedCoupon: (coupon, discountAmount) =>
      set({ appliedCoupon: coupon, discountAmount, error: null }),

    removeCoupon: () =>
      set({ appliedCoupon: null, discountAmount: 0, error: null }),

    setLoading: (isLoading) => set({ isLoading }),

    setError: (error) => set({ error }),

    reset: () =>
      set({ appliedCoupon: null, discountAmount: 0, isLoading: false, error: null }),

    hasAppliedCoupon: () => get().appliedCoupon !== null,

    getDiscountDisplay: () => {
      const { appliedCoupon, discountAmount } = get();
      if (!appliedCoupon) return '';
      if (appliedCoupon.discountType === 'percentage') return `${appliedCoupon.discountValue}% off`;
      if (appliedCoupon.discountType === 'free_shipping') return 'Free Shipping';
      return `₨${discountAmount.toLocaleString()} off`;
    },
  }),
  { persist: true }
);
