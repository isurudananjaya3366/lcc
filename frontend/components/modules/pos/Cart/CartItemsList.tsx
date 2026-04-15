'use client';

import { memo } from 'react';
import { CartItem } from './CartItem';
import type { POSCartItem } from '../types';

interface CartItemsListProps {
  items: POSCartItem[];
}

export const CartItemsList = memo(function CartItemsList({ items }: CartItemsListProps) {
  return (
    <div className="divide-y divide-gray-100 dark:divide-gray-800">
      {items.map((item) => (
        <CartItem key={item.id} item={item} />
      ))}
    </div>
  );
});
