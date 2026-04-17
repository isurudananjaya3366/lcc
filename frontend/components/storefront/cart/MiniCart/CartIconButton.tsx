'use client';

import React, { useState, type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStoreCartStore } from '@/stores/store/cart';
import MiniCartDropdown from './MiniCartDropdown';

interface CartIconButtonProps {
  className?: string;
}

const CartIconButton: FC<CartIconButtonProps> = ({ className }) => {
  const [isOpen, setIsOpen] = useState(false);
  const getItemCount = useStoreCartStore((s) => s.getItemCount);
  const itemCount = getItemCount();

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
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

        {itemCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-green-700 text-[10px] font-bold text-white">
            {itemCount > 99 ? '99+' : itemCount}
          </span>
        )}
      </button>

      <MiniCartDropdown isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </div>
  );
};

export default CartIconButton;
