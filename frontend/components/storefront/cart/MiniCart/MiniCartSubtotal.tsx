'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import { formatCurrency } from '@/lib/store/config';

interface MiniCartSubtotalProps {
  subtotal: number;
  className?: string;
}

const MiniCartSubtotal: FC<MiniCartSubtotalProps> = ({ subtotal, className }) => {
  return (
    <div
      className={cn(
        'flex items-center justify-between px-4 py-3 border-t border-gray-200 dark:border-gray-700',
        className
      )}
    >
      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Subtotal</span>
      <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
        {formatCurrency(subtotal)}
      </span>
    </div>
  );
};

export default MiniCartSubtotal;
