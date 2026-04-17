'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface MiniCartFooterProps {
  className?: string;
}

const MiniCartFooter: FC<MiniCartFooterProps> = ({ className }) => {
  return (
    <div className={cn('flex gap-2 px-4 pb-4 pt-2', className)}>
      <Link
        href="/cart"
        className="flex-1 py-2 px-4 text-sm font-medium text-center text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        View Cart
      </Link>
      <Link
        href="/checkout"
        className="flex-1 py-2 px-4 text-sm font-medium text-center text-white bg-green-700 rounded-lg hover:bg-green-800 transition-colors"
      >
        Checkout
      </Link>
    </div>
  );
};

export default MiniCartFooter;
