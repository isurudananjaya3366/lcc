'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStoreCartStore } from '@/stores/store/cart';
import type { StoreCartItem } from '@/stores/store/cart';
import CartItemImage from './CartItemImage';
import CartItemDetails from './CartItemDetails';
import CartItemPrice from './CartItemPrice';

interface CartItemRowProps {
  item: StoreCartItem;
  className?: string;
}

const CartItemRow: FC<CartItemRowProps> = ({ item, className }) => {
  const updateCartItem = useStoreCartStore((s) => s.updateCartItem);
  const removeFromCart = useStoreCartStore((s) => s.removeFromCart);

  const handleDecrement = () => {
    if (item.quantity > 1) {
      updateCartItem(item.id, item.quantity - 1);
    }
  };

  const handleIncrement = () => {
    updateCartItem(item.id, item.quantity + 1);
  };

  return (
    <div className={cn('flex gap-4 py-4', className)}>
      <CartItemImage src={item.image} alt={item.name} />

      <div className="flex flex-1 flex-col gap-2 min-w-0 sm:flex-row sm:items-start sm:gap-4">
        <CartItemDetails
          name={item.name}
          sku={item.sku}
          variants={item.variant}
          className="flex-1"
        />

        <div className="flex items-center gap-4 sm:gap-6">
          {/* Quantity selector */}
          <div className="flex items-center rounded-lg border border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={handleDecrement}
              disabled={item.quantity <= 1}
              className="flex h-8 w-8 items-center justify-center text-gray-600 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed dark:text-gray-300 dark:hover:bg-gray-700 rounded-l-lg transition-colors"
              aria-label="Decrease quantity"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </button>
            <span className="flex h-8 w-10 items-center justify-center text-sm font-medium text-gray-900 dark:text-gray-100 border-x border-gray-200 dark:border-gray-700">
              {item.quantity}
            </span>
            <button
              type="button"
              onClick={handleIncrement}
              className="flex h-8 w-8 items-center justify-center text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-r-lg transition-colors"
              aria-label="Increase quantity"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>

          <CartItemPrice
            price={item.price}
            quantity={item.quantity}
            lineSubtotal={item.lineSubtotal}
          />

          {/* Remove button */}
          <button
            type="button"
            onClick={() => removeFromCart(item.id)}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-900/20 dark:hover:text-red-400 transition-colors"
            aria-label={`Remove ${item.name} from cart`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CartItemRow;
