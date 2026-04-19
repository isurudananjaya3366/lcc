'use client';

import { Percent, Gift, Truck } from 'lucide-react';
import type { DiscountType } from '@/types/marketing/coupon.types';
import { COUPON_TEST_IDS } from '@/lib/marketing/marketingTestIds';

interface DiscountDisplayProps {
  discountType: DiscountType;
  discountValue: number;
  discountAmount: number;
  className?: string;
}

const icons: Record<DiscountType, typeof Percent> = {
  percentage: Percent,
  fixed_amount: Gift,
  free_shipping: Truck,
};

export function DiscountDisplay({ discountType, discountValue, discountAmount, className = '' }: DiscountDisplayProps) {
  const Icon = icons[discountType];

  const label =
    discountType === 'percentage'
      ? `${discountValue}% off`
      : discountType === 'free_shipping'
        ? 'Free Shipping'
        : `₨${discountValue.toLocaleString()} off`;

  return (
    <div data-testid={COUPON_TEST_IDS.discountDisplay} className={`flex items-center justify-between text-green-700 ${className}`}>
      <div className="flex items-center gap-1.5">
        <Icon className="h-4 w-4" />
        <span className="text-sm font-medium">{label}</span>
      </div>
      <span className="text-sm font-semibold">-₨{discountAmount.toLocaleString()}</span>
    </div>
  );
}
