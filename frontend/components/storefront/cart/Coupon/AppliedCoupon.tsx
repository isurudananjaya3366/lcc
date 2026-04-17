'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface AppliedCouponProps {
  code: string;
  type: 'percentage' | 'fixed';
  value: number;
  onRemove: () => void;
  className?: string;
}

const AppliedCoupon: FC<AppliedCouponProps> = ({ code, type, value, onRemove, className }) => {
  const description = type === 'percentage' ? `${value}% off` : `₨${value.toLocaleString()} off`;

  return (
    <div
      className={cn(
        'flex items-center justify-between rounded-md border border-green-200 bg-green-50 px-3 py-2',
        'dark:border-green-800 dark:bg-green-950',
        className
      )}
    >
      <div className="flex items-center gap-2">
        {/* Tag icon */}
        <svg
          className="h-4 w-4 text-green-600 dark:text-green-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M7 7h.01M7 3h5a1.97 1.97 0 011.4.58l7.02 7.02a2 2 0 010 2.83l-4.99 4.99a2 2 0 01-2.83 0L5.58 11.4A1.97 1.97 0 015 10V5a2 2 0 012-2z"
          />
        </svg>
        <span className="text-sm font-medium text-green-700 dark:text-green-300">
          {code} — {description}
        </span>
      </div>

      <button
        type="button"
        onClick={onRemove}
        className={cn(
          'rounded p-0.5 text-green-600 hover:bg-green-100 hover:text-green-800',
          'dark:text-green-400 dark:hover:bg-green-900 dark:hover:text-green-200'
        )}
        aria-label="Remove coupon"
      >
        {/* X icon */}
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

export default AppliedCoupon;
