'use client';

import React, { type FC } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { cn } from '@/lib/utils';
import type { MiniCartItemProps } from '@/types/store/header';

const formatPrice = (price: number): string => {
  return `₨ ${price.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
};

const MiniCartItem: FC<MiniCartItemProps> = ({ item, onRemove, className }) => {
  return (
    <div className={cn('flex gap-3 px-4 py-3', className)}>
      {/* Product image */}
      <Link
        href={`/products/${item.slug}`}
        className="relative h-16 w-16 flex-shrink-0 overflow-hidden rounded-md border border-gray-200 dark:border-gray-700"
      >
        <Image src={item.image} alt={item.name} fill sizes="64px" className="object-cover" />
      </Link>

      {/* Info */}
      <div className="flex flex-1 flex-col min-w-0">
        <Link
          href={`/products/${item.slug}`}
          className="text-sm font-medium text-gray-900 dark:text-gray-100 hover:text-green-700 dark:hover:text-green-400 truncate transition-colors"
        >
          {item.name}
        </Link>

        {item.variant && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{item.variant}</p>
        )}

        <div className="flex items-center justify-between mt-auto pt-1">
          <p className="text-sm text-gray-700 dark:text-gray-300">
            {formatPrice(item.price)} × {item.quantity}
          </p>

          <button
            type="button"
            onClick={() => onRemove(item.id)}
            className="text-gray-400 hover:text-red-500 transition-colors p-0.5"
            aria-label={`Remove ${item.name} from cart`}
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
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default MiniCartItem;
