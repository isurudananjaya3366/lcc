'use client';

import { Tag, X, Loader2 } from 'lucide-react';
import { useCouponStore } from '@/stores/store/coupon';
import { useRemoveCoupon } from '@/hooks/marketing/useCoupon';
import { COUPON_TEST_IDS } from '@/lib/marketing/marketingTestIds';

interface AppliedCouponBadgeProps {
  onRemoved?: () => void;
  className?: string;
}

export function AppliedCouponBadge({ onRemoved, className = '' }: AppliedCouponBadgeProps) {
  const { appliedCoupon, getDiscountDisplay, removeCoupon: removeFromStore } = useCouponStore();
  const { mutate: remove, isPending } = useRemoveCoupon();

  if (!appliedCoupon) return null;

  const handleRemove = () => {
    remove(appliedCoupon.code, {
      onSuccess: () => {
        removeFromStore();
        onRemoved?.();
      },
    });
  };

  return (
    <div
      data-testid={COUPON_TEST_IDS.appliedCouponBadge}
      className={`inline-flex items-center gap-2 rounded-full bg-green-50 px-3 py-1.5 text-sm text-green-700 ${className}`}
    >
      <Tag className="h-3.5 w-3.5" />
      <span className="font-medium">{appliedCoupon.code}</span>
      <span className="text-green-600">({getDiscountDisplay()})</span>
      <button
        data-testid={COUPON_TEST_IDS.couponRemoveButton}
        onClick={handleRemove}
        disabled={isPending}
        className="ml-1 rounded-full p-0.5 text-green-600 hover:bg-green-100 hover:text-green-800 disabled:opacity-50"
        type="button"
        aria-label="Remove coupon"
      >
        {isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <X className="h-3.5 w-3.5" />}
      </button>
    </div>
  );
}
