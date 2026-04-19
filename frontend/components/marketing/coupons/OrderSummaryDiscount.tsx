'use client';

import { Tag } from 'lucide-react';
import type { CouponSummary } from '@/types/marketing/coupon.types';

interface OrderSummaryDiscountProps {
  couponSummary: CouponSummary | null;
  className?: string;
}

export function OrderSummaryDiscount({ couponSummary, className = '' }: OrderSummaryDiscountProps) {
  if (!couponSummary) return null;

  const discountLabel =
    couponSummary.discountType === 'percentage'
      ? `${couponSummary.discountValue}% off`
      : couponSummary.discountType === 'free_shipping'
        ? 'Free Shipping'
        : `₨${couponSummary.discountValue.toLocaleString()} off`;

  return (
    <div className={`flex items-center justify-between py-1 text-sm ${className}`}>
      <div className="flex items-center gap-1.5 text-green-600">
        <Tag className="h-3.5 w-3.5" />
        <span>
          Coupon: <span className="font-medium">{couponSummary.code}</span>
        </span>
        <span className="text-xs text-green-500">({discountLabel})</span>
      </div>
      <span className="font-medium text-green-600">-₨{couponSummary.discountAmount.toLocaleString()}</span>
    </div>
  );
}
