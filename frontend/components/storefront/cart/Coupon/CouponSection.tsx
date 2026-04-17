'use client';

import React, { useState, type FC } from 'react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { useStoreCartStore } from '@/stores/store/cart';
import { validateCoupon } from '@/services/storefront/couponService';
import CouponInput from './CouponInput';
import AppliedCoupon from './AppliedCoupon';
import CouponValidation from './CouponValidation';

interface CouponSectionProps {
  className?: string;
}

const CouponSection: FC<CouponSectionProps> = ({ className }) => {
  const [expanded, setExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const discount = useStoreCartStore((s) => s.discount);
  const applyCoupon = useStoreCartStore((s) => s.applyCoupon);
  const removeCoupon = useStoreCartStore((s) => s.removeCoupon);

  const handleApply = async (code: string) => {
    setError(null);
    setSuccess(null);
    setIsLoading(true);

    try {
      const result = await validateCoupon(code);

      if (result.valid && result.type && result.value !== undefined) {
        applyCoupon(code, result.type, result.value);
        setSuccess('Coupon applied successfully!');
        toast.success('Coupon applied successfully!');
      } else {
        setError(result.error ?? 'Invalid coupon code');
      }
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemove = () => {
    removeCoupon();
    setSuccess(null);
    setError(null);
    toast.info('Coupon removed');
  };

  return (
    <div className={cn('space-y-2', className)}>
      {discount ? (
        <AppliedCoupon
          code={discount.code}
          type={discount.type}
          value={discount.value}
          onRemove={handleRemove}
        />
      ) : (
        <>
          {!expanded ? (
            <button
              type="button"
              onClick={() => setExpanded(true)}
              className={cn(
                'text-sm font-medium text-green-600 hover:text-green-700 hover:underline',
                'dark:text-green-400 dark:hover:text-green-300'
              )}
            >
              Have a coupon?
            </button>
          ) : (
            <CouponInput onApply={handleApply} isLoading={isLoading} />
          )}
        </>
      )}
      <CouponValidation error={error} success={success} />
    </div>
  );
};

export default CouponSection;
