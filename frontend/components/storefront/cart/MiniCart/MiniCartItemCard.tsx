'use client';

import React, { type FC } from 'react';
import Image from 'next/image';
import { cn } from '@/lib/utils';
import { formatCurrency } from '@/lib/store/config';
import type { StoreCartItem } from '@/stores/store/cart';
import MiniCartItemRemove from './MiniCartItemRemove';

interface MiniCartItemCardProps {
  item: StoreCartItem;
  onRemove: (id: string) => void;
  className?: string;
}

const MiniCartItemCard: FC<MiniCartItemCardProps> = ({ item, onRemove, className }) => {
  return (
    <div className={cn('flex gap-3 px-4 py-3', className)}>
      {/* Product image */}
      <div className="relative h-[60px] w-[60px] flex-shrink-0 overflow-hidden rounded-md border border-gray-200 dark:border-gray-700">
        <Image
          src={item.image || '/images/placeholder-product.png'}
          alt={item.name}
          fill
          sizes="60px"
          className="object-cover"
        />
      </div>

      {/* Info */}
      <div className="flex flex-1 flex-col min-w-0">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
          {item.name}
        </p>

        {item.variant && Object.keys(item.variant).length > 0 && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">
            {Object.entries(item.variant)
              .map(([key, value]) => `${key}: ${value}`)
              .join(', ')}
          </p>
        )}

        <div className="flex items-center justify-between mt-auto pt-1">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            {formatCurrency(item.price)} × {item.quantity}
          </p>

          <MiniCartItemRemove itemId={item.id} onRemove={onRemove} />
        </div>
      </div>
    </div>
  );
};

export default MiniCartItemCard;
