'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import type { StoreCartItem } from '@/stores/store/cart';
import MiniCartItemCard from './MiniCartItemCard';

const MAX_DISPLAY_ITEMS = 5;

interface MiniCartItemsListProps {
  items: StoreCartItem[];
  onRemoveItem: (id: string) => void;
  className?: string;
}

const MiniCartItemsList: FC<MiniCartItemsListProps> = ({ items, onRemoveItem, className }) => {
  const displayItems = items.slice(0, MAX_DISPLAY_ITEMS);
  const remainingCount = items.length - MAX_DISPLAY_ITEMS;

  return (
    <div className={cn('flex flex-col', className)}>
      <div className="max-h-72 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-800">
        {displayItems.map((item) => (
          <MiniCartItemCard key={item.id} item={item} onRemove={onRemoveItem} />
        ))}
      </div>

      {remainingCount > 0 && (
        <div className="px-4 py-2 text-center border-t border-gray-100 dark:border-gray-800">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            and {remainingCount} more item{remainingCount === 1 ? '' : 's'} in cart
          </p>
        </div>
      )}
    </div>
  );
};

export default MiniCartItemsList;
