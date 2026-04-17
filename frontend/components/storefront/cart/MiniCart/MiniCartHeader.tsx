'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface MiniCartHeaderProps {
  itemCount: number;
  onClose: () => void;
  className?: string;
}

const MiniCartHeader: FC<MiniCartHeaderProps> = ({ itemCount, onClose, className }) => {
  return (
    <div
      className={cn(
        'flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800',
        className
      )}
    >
      <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
        Your Cart
        {itemCount > 0 && (
          <span className="ml-1.5 inline-flex items-center justify-center rounded-full bg-green-100 dark:bg-green-900 px-2 py-0.5 text-xs font-medium text-green-700 dark:text-green-300">
            {itemCount} {itemCount === 1 ? 'item' : 'items'}
          </span>
        )}
      </h3>
      <button
        type="button"
        onClick={onClose}
        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors rounded p-0.5"
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
  );
};

export default MiniCartHeader;
