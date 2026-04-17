'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface MiniCartItemRemoveProps {
  itemId: string;
  onRemove: (id: string) => void;
  loading?: boolean;
  className?: string;
}

const MiniCartItemRemove: FC<MiniCartItemRemoveProps> = ({
  itemId,
  onRemove,
  loading = false,
  className,
}) => {
  return (
    <button
      type="button"
      onClick={() => onRemove(itemId)}
      disabled={loading}
      aria-label="Remove item from cart"
      className={cn(
        'p-0.5 text-gray-400 transition-colors',
        'hover:text-red-500 dark:hover:text-red-400',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
    >
      {loading ? (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4 animate-spin"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
      ) : (
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
      )}
    </button>
  );
};

export default MiniCartItemRemove;
