'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import EmptyCartIllustration from './EmptyCartIllustration';

interface EmptyCartPageProps {
  className?: string;
}

const EmptyCartPage: FC<EmptyCartPageProps> = ({ className }) => {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center px-4 py-16 text-center',
        className,
      )}
    >
      <EmptyCartIllustration className="mb-6" />

      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
        Your cart is empty
      </h2>

      <p className="max-w-sm text-sm text-gray-500 dark:text-gray-400 mb-8">
        Looks like you haven&apos;t added anything to your cart yet.
        Browse our products to find something you&apos;ll love.
      </p>

      <Link
        href="/products"
        className="inline-flex items-center gap-2 rounded-lg bg-green-700 px-6 py-3 text-sm font-medium text-white shadow-sm hover:bg-green-800 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
      >
        Browse Products
      </Link>
    </div>
  );
};

export default EmptyCartPage;
