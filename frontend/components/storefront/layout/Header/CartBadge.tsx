import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import type { CartBadgeProps } from '@/types/store/header';

const CartBadge: FC<CartBadgeProps> = ({ count, max = 99, className }) => {
  const displayCount = count > max ? `${max}+` : String(count);

  return (
    <span
      className={cn(
        'absolute -top-1 -right-1 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-red-600 rounded-full border-2 border-white dark:border-gray-900',
        className
      )}
      aria-hidden="true"
    >
      {displayCount}
    </span>
  );
};

export default CartBadge;
