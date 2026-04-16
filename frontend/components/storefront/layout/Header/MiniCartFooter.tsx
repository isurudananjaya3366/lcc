'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import type { MiniCartFooterProps } from '@/types/store/header';

const formatPrice = (price: number): string => {
  return `₨ ${price.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
};

const MiniCartFooter: FC<MiniCartFooterProps> = ({
  subtotal,
  onViewCart,
  onCheckout,
  itemCount,
  className,
}) => {
  return (
    <div
      className={cn('border-t border-gray-200 dark:border-gray-700 px-4 py-3 space-y-3', className)}
    >
      {/* Subtotal row */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Subtotal{itemCount ? ` (${itemCount} item${itemCount === 1 ? '' : 's'})` : ''}
        </span>
        <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          {formatPrice(subtotal)}
        </span>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={onViewCart}
          className="flex-1 py-2 px-4 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          View Cart
        </button>
        <button
          type="button"
          onClick={onCheckout}
          className="flex-1 py-2 px-4 text-sm font-medium text-white bg-green-700 rounded-lg hover:bg-green-800 transition-colors"
        >
          Checkout
        </button>
      </div>
    </div>
  );
};

export default MiniCartFooter;
