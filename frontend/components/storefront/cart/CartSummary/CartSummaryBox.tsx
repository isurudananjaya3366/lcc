'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStoreCartStore } from '@/stores/store/cart';
import { CouponSection } from '../Coupon';
import SummaryRow from './SummaryRow';
import CheckoutButton from './CheckoutButton';
import SecureCheckoutNote from './SecureCheckoutNote';

interface CartSummaryBoxProps {
  className?: string;
}

const CartSummaryBox: FC<CartSummaryBoxProps> = ({ className }) => {
  const getCartSummary = useStoreCartStore((s) => s.getCartSummary);
  const summary = getCartSummary();

  return (
    <div
      className={cn(
        'rounded-lg border border-gray-200 bg-white p-6',
        'dark:border-gray-700 dark:bg-gray-900',
        className
      )}
    >
      <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">
        Order Summary
      </h2>

      {/* Coupon */}
      <CouponSection className="mb-5" />

      {/* Summary rows */}
      <div className="space-y-2.5">
        <SummaryRow label="Subtotal" value={summary.subtotal} />
        {summary.discount > 0 && (
          <SummaryRow label="Discount" value={summary.discount} isDiscount />
        )}
        <SummaryRow label="Shipping" value={0} isEstimate />
        <SummaryRow label="Tax" value={summary.tax} />
      </div>

      {/* Total */}
      <div className="mt-4">
        <SummaryRow label="Total" value={summary.total} isTotal />
      </div>

      {/* Checkout */}
      <div className="mt-6 space-y-3">
        <CheckoutButton itemCount={summary.itemCount} />
        <SecureCheckoutNote />
      </div>
    </div>
  );
};

export default CartSummaryBox;
