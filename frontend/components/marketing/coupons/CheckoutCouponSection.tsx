'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { useCouponStore } from '@/stores/store/coupon';
import { AppliedCouponBadge } from './AppliedCouponBadge';
import { CouponInput } from './CouponInput';
import type { Coupon } from '@/types/marketing/coupon.types';

interface CheckoutCouponSectionProps {
  cartTotal: number;
  onCouponApplied?: (coupon: Coupon) => void;
  onCouponRemoved?: () => void;
  className?: string;
}

export function CheckoutCouponSection({
  cartTotal,
  onCouponApplied,
  onCouponRemoved,
  className = '',
}: CheckoutCouponSectionProps) {
  const { appliedCoupon } = useCouponStore();
  const [expanded, setExpanded] = useState(false);

  const handleApplied = (code: string) => {
    setExpanded(false);
    if (appliedCoupon) {
      onCouponApplied?.(appliedCoupon);
    }
    void code;
  };

  return (
    <div className={`rounded-lg border border-gray-200 ${className}`}>
      {appliedCoupon ? (
        <div className="flex items-center justify-between p-4">
          <AppliedCouponBadge onRemoved={onCouponRemoved} />
        </div>
      ) : (
        <>
          {/* Collapsible toggle */}
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="flex w-full items-center justify-between px-4 py-3 text-left text-sm text-blue-600 hover:underline"
          >
            <span>Have a coupon code? Click here</span>
            <ChevronDown
              className={`h-4 w-4 transition-transform ${expanded ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Expanded input */}
          {expanded && (
            <div className="border-t border-gray-200 px-4 pb-4 pt-3">
              <CouponInput cartTotal={cartTotal} onApplied={handleApplied} />
            </div>
          )}
        </>
      )}
    </div>
  );
}
