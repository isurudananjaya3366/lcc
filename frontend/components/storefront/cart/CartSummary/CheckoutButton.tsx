'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface CheckoutButtonProps {
  disabled?: boolean;
  itemCount: number;
  className?: string;
}

const CheckoutButton: FC<CheckoutButtonProps> = ({ disabled = false, itemCount, className }) => {
  if (disabled || itemCount === 0) {
    return (
      <button
        type="button"
        disabled
        className={cn(
          'w-full rounded-lg bg-green-600 px-6 py-3 text-center text-sm font-semibold text-white',
          'cursor-not-allowed opacity-50',
          className
        )}
      >
        Proceed to Checkout
      </button>
    );
  }

  return (
    <Link
      href="/checkout"
      className={cn(
        'block w-full rounded-lg bg-green-600 px-6 py-3 text-center text-sm font-semibold text-white',
        'hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
        'transition-colors',
        'dark:bg-green-500 dark:hover:bg-green-600 dark:focus:ring-offset-gray-900',
        className
      )}
    >
      Proceed to Checkout
    </Link>
  );
};

export default CheckoutButton;
