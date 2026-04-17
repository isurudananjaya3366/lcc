'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface EmptyMiniCartProps {
  className?: string;
}

const EmptyMiniCart: FC<EmptyMiniCartProps> = ({ className }) => {
  return (
    <div className={cn('px-4 py-8 text-center', className)}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="mx-auto h-12 w-12 text-gray-300 dark:text-gray-600 mb-3"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"
        />
      </svg>
      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
        Your cart is empty
      </p>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
        Add items to get started
      </p>
      <Link
        href="/products"
        className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-700 rounded-lg hover:bg-green-800 transition-colors"
      >
        Start Shopping
      </Link>
    </div>
  );
};

export default EmptyMiniCart;
