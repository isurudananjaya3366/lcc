'use client';

import React, { useRef, useEffect, type FC } from 'react';
import { cn } from '@/lib/utils';
import type { MiniCartProps } from '@/types/store/header';
import MiniCartItem from './MiniCartItem';
import MiniCartFooter from './MiniCartFooter';

const MAX_DISPLAY_ITEMS = 5;

const MiniCart: FC<MiniCartProps> = ({
  isOpen,
  onClose,
  items,
  subtotal,
  onRemoveItem,
  onViewCart,
  onCheckout,
}) => {
  const cartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (cartRef.current && !cartRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const displayItems = items.slice(0, MAX_DISPLAY_ITEMS);
  const remainingCount = items.length - MAX_DISPLAY_ITEMS;

  return (
    <div
      ref={cartRef}
      className={cn(
        'absolute right-0 top-full mt-2 w-96 bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50',
        'animate-in zoom-in-95 fade-in duration-150'
      )}
      role="dialog"
      aria-label="Shopping cart preview"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          Shopping Cart ({items.length})
        </h3>
        <button
          type="button"
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          aria-label="Close cart preview"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      {/* Items or empty state */}
      {items.length === 0 ? (
        <div className="px-4 py-8 text-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="mx-auto h-10 w-10 text-gray-300 dark:text-gray-600 mb-3"
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
          <p className="text-sm text-gray-500 dark:text-gray-400">Your cart is empty</p>
        </div>
      ) : (
        <>
          <div className="max-h-80 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-800">
            {displayItems.map((item) => (
              <MiniCartItem key={item.id} item={item} onRemove={onRemoveItem} />
            ))}
          </div>

          {remainingCount > 0 && (
            <div className="px-4 py-2 text-center border-t border-gray-100 dark:border-gray-800">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                + {remainingCount} more item{remainingCount === 1 ? '' : 's'} in cart
              </p>
            </div>
          )}

          <MiniCartFooter
            subtotal={subtotal}
            onViewCart={onViewCart}
            onCheckout={onCheckout}
            itemCount={items.length}
          />
        </>
      )}
    </div>
  );
};

export default MiniCart;
