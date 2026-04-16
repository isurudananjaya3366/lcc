'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import CartBadge from './CartBadge';
import type { CartIconProps } from '@/types/store/header';

const CartIcon: FC<CartIconProps> = ({ itemCount, onClick, className, showBadge = true }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'relative p-2 text-gray-700 dark:text-gray-300 hover:text-green-700 dark:hover:text-green-400 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800',
        className
      )}
      aria-label={`Shopping cart${itemCount > 0 ? `, ${itemCount} item${itemCount === 1 ? '' : 's'}` : ''}`}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"
        />
      </svg>
      {showBadge && itemCount > 0 && <CartBadge count={itemCount} />}
    </button>
  );
};

export default CartIcon;
