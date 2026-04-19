'use client';

/**
 * Coupon Validation & Application Hooks
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback } from 'react';
import * as couponApi from '@/lib/marketing/coupon';
import type {
  ValidateCouponRequest,
  ValidateCouponResponse,
  ApplyCouponResponse,
} from '@/types/marketing/coupon.types';

const COUPON_KEYS = {
  all: ['coupons'] as const,
  validate: (code: string) => ['coupons', 'validate', code] as const,
  available: () => ['coupons', 'available'] as const,
};

/** Hook for debounced coupon validation */
export function useCouponValidation() {
  const [debouncedCode, setDebouncedCode] = useState('');
  const [debounceTimer, setDebounceTimer] = useState<ReturnType<typeof setTimeout> | null>(null);

  const query = useQuery<ValidateCouponResponse>({
    queryKey: COUPON_KEYS.validate(debouncedCode),
    queryFn: () =>
      couponApi.validateCoupon({
        code: debouncedCode,
        cartTotal: 0,
        items: [],
      }),
    enabled: debouncedCode.length >= 3,
    staleTime: 30 * 1000,
    retry: false,
  });

  const validate = useCallback(
    (code: string) => {
      if (debounceTimer) clearTimeout(debounceTimer);
      const timer = setTimeout(() => {
        setDebouncedCode(code.trim().toUpperCase());
      }, 500);
      setDebounceTimer(timer);
    },
    [debounceTimer]
  );

  return { ...query, validate };
}

/** Hook for applying a coupon */
export function useApplyCoupon() {
  const queryClient = useQueryClient();

  return useMutation<ApplyCouponResponse, Error, { code: string; cartId?: string }>({
    mutationFn: (data) => couponApi.applyCoupon(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: COUPON_KEYS.all });
    },
  });
}

/** Hook for removing a coupon */
export function useRemoveCoupon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (code: string) => couponApi.removeCoupon(code),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cart'] });
      queryClient.invalidateQueries({ queryKey: COUPON_KEYS.all });
    },
  });
}

/** Hook for available coupons list */
export function useAvailableCoupons() {
  return useQuery({
    queryKey: COUPON_KEYS.available(),
    queryFn: () => couponApi.getAvailableCoupons(),
    staleTime: 5 * 60 * 1000,
  });
}
