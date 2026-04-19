'use client';

import { useState } from 'react';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { CouponInput } from './CouponInput';
import { AppliedCouponBadge } from './AppliedCouponBadge';
import { DiscountDisplay } from './DiscountDisplay';
import { useCouponStore } from '@/stores/store/coupon';
import { COUPON_TEST_IDS } from '@/lib/marketing/marketingTestIds';

interface CartCouponSectionProps {
  cartTotal: number;
  className?: string;
}

export function CartCouponSection({ cartTotal, className = '' }: CartCouponSectionProps) {
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const { appliedCoupon, discountAmount } = useCouponStore();

  return (
    <div className={`space-y-3 ${className}`}>
      <h3 className="text-sm font-semibold text-gray-700">Coupon Code</h3>

      {appliedCoupon ? (
        <>
          <AppliedCouponBadge onRemoved={() => setMessage(null)} />
          <DiscountDisplay
            discountType={appliedCoupon.discountType}
            discountValue={appliedCoupon.discountValue}
            discountAmount={discountAmount}
          />
        </>
      ) : (
        <CouponInput
          cartTotal={cartTotal}
          onApplied={(code) => setMessage({ type: 'success', text: `Coupon "${code}" applied!` })}
          onError={(text) => setMessage({ type: 'error', text })}
        />
      )}

      {message && (
        <div
          data-testid={message.type === 'success' ? COUPON_TEST_IDS.couponSuccess : COUPON_TEST_IDS.couponError}
          className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${
            message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle className="h-4 w-4 shrink-0" />
          ) : (
            <AlertCircle className="h-4 w-4 shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}
    </div>
  );
}
