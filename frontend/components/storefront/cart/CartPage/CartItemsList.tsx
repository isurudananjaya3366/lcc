'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStoreCartStore } from '@/stores/store/cart';
import CartItemRow from './CartItemRow';

interface CartItemsListProps {
  className?: string;
}

const CartItemsList: FC<CartItemsListProps> = ({ className }) => {
  const items = useStoreCartStore((s) => s.items);

  return (
    <div
      className={cn(
        'rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900',
        className,
      )}
    >
      <div className="divide-y divide-gray-200 px-4 dark:divide-gray-700 sm:px-6">
        {items.map((item) => (
          <CartItemRow key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
};

export default CartItemsList;
